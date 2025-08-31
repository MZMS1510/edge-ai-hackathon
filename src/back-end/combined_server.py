import asyncio
import websockets
import uvicorn
import threading
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import time
from typing import Dict, Any, List
from websocket_video_server import VideoProcessor, handle_client
from main import app as fastapi_app, data_store

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a combined app
app = FastAPI(title="Edge Coach - Combined API & WebSocket Server", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global video processor instance
video_processor = VideoProcessor()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# Mount the existing FastAPI routes
app.mount("/api", fastapi_app)

# Serve static files (for the test client)
try:
    app.mount("/static", StaticFiles(directory=".", html=True), name="static")
except Exception:
    pass  # Directory might not exist in all setups

@app.get("/")
async def root():
    return {
        "message": "Edge Coach - Combined Server",
        "version": "2.0.0",
        "endpoints": {
            "rest_api": "/api",
            "websocket": "/ws",
            "test_client": "/test",
            "docs": "/docs"
        },
        "status": "running"
    }

@app.get("/test", response_class=HTMLResponse)
async def get_test_client():
    """Serve the test client HTML"""
    try:
        with open("test_websocket_client.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Test client not found</h1><p>Please make sure test_websocket_client.html exists.</p>",
            status_code=404
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for video processing"""
    await manager.connect(websocket)
    client_address = f"{websocket.client.host}:{websocket.client.port}"
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "video_frame":
                    # Process video frame
                    frame_data = message.get("frame")
                    if not frame_data:
                        await manager.send_personal_message(json.dumps({
                            "type": "error",
                            "message": "No frame data provided"
                        }), websocket)
                        continue
                    
                    # Process the frame
                    features = video_processor.process_frame(frame_data)
                    
                    # Also send to the existing data store for REST API compatibility
                    if 'error' not in features:
                        try:
                            from main import MetricsData
                            metrics_data = MetricsData(**features)
                            data_store.add_metrics(metrics_data)
                        except Exception as e:
                            logger.warning(f"Could not add to data store: {e}")
                    
                    # Send back the extracted features
                    response = {
                        "type": "features",
                        "data": features,
                        "timestamp": time.time()
                    }
                    await manager.send_personal_message(json.dumps(response), websocket)
                
                elif message_type == "get_stats":
                    # Get session statistics
                    stats = video_processor.get_session_stats()
                    response = {
                        "type": "stats",
                        "data": stats,
                        "timestamp": time.time()
                    }
                    await manager.send_personal_message(json.dumps(response), websocket)
                
                elif message_type == "reset_session":
                    # Reset the session
                    video_processor.reset_session()
                    data_store.reset_session()  # Also reset the REST API data store
                    response = {
                        "type": "session_reset",
                        "message": "Session reset successfully",
                        "timestamp": time.time()
                    }
                    await manager.send_personal_message(json.dumps(response), websocket)
                
                elif message_type == "ping":
                    # Respond to ping
                    response = {
                        "type": "pong",
                        "timestamp": time.time()
                    }
                    await manager.send_personal_message(json.dumps(response), websocket)
                
                else:
                    # Unknown message type
                    await manager.send_personal_message(json.dumps({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    }), websocket)
                    
            except json.JSONDecodeError:
                await manager.send_personal_message(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }), websocket)
            except Exception as e:
                logger.error(f"Error handling message from {client_address}: {e}")
                await manager.send_personal_message(json.dumps({
                    "type": "error",
                    "message": str(e)
                }), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Client {client_address} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error with client {client_address}: {e}")
        manager.disconnect(websocket)

# Additional REST endpoints for WebSocket integration
@app.get("/api/ws/status")
async def websocket_status():
    """Get WebSocket server status"""
    return {
        "active_connections": len(manager.active_connections),
        "video_processor_stats": video_processor.get_session_stats(),
        "status": "running"
    }

@app.post("/api/ws/broadcast")
async def broadcast_message(message: Dict[str, Any]):
    """Broadcast a message to all connected WebSocket clients"""
    if not manager.active_connections:
        raise HTTPException(status_code=400, detail="No active WebSocket connections")
    
    await manager.broadcast(json.dumps(message))
    return {
        "message": "Broadcast sent",
        "connections": len(manager.active_connections),
        "timestamp": time.time()
    }

@app.get("/api/ws/connections")
async def get_connections():
    """Get information about active WebSocket connections"""
    connections_info = []
    for i, conn in enumerate(manager.active_connections):
        try:
            connections_info.append({
                "id": i,
                "client": f"{conn.client.host}:{conn.client.port}",
                "state": "connected"
            })
        except Exception:
            connections_info.append({
                "id": i,
                "client": "unknown",
                "state": "unknown"
            })
    
    return {
        "total_connections": len(manager.active_connections),
        "connections": connections_info
    }

if __name__ == "__main__":
    import sys
    import os
    
    # Check dependencies
    try:
        import mediapipe
        import cv2
        import websockets
        logger.info("✅ All video processing dependencies available")
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("Install required packages: pip install websockets mediapipe opencv-python")
        sys.exit(1)
    
    # Configuration
    host = "0.0.0.0"
    port = 8000
    
    logger.info("🚀 Starting Edge Coach Combined Server...")
    logger.info(f"📡 REST API: http://{host}:{port}/api")
    logger.info(f"🔌 WebSocket: ws://{host}:{port}/ws")
    logger.info(f"🧪 Test Client: http://{host}:{port}/test")
    logger.info(f"📚 API Docs: http://{host}:{port}/docs")
    logger.info(f"📊 Streamlit Dashboard: http://localhost:8501 (if running separately)")
    
    # Run the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
