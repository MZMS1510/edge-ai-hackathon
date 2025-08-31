import asyncio
import websockets
import cv2
import numpy as np
import mediapipe as mp
import json
import base64
import time
from typing import Dict, Any
import logging
from features import extract_features
import threading
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize face mesh with detection and tracking confidence
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize hands detection
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Metrics storage
        self.metrics_history = deque(maxlen=1000)
        self.frame_count = 0
        self.start_time = time.time()
        
    def process_frame(self, frame_data: bytes) -> Dict[str, Any]:
        """Process a single video frame and extract features"""
        try:
            # Decode base64 image
            img_data = base64.b64decode(frame_data)
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                logger.error("Failed to decode frame")
                return {"error": "Failed to decode frame"}
            
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            face_results = self.face_mesh.process(rgb_frame)
            hand_results = self.hands.process(rgb_frame)
            
            # Extract features using our existing feature extraction
            features = extract_features(face_results, hand_results, frame)
            
            # Store metrics
            self.metrics_history.append(features)
            self.frame_count += 1
            
            # Add processing metadata
            features["frame_number"] = self.frame_count
            features["processing_time"] = time.time()
            features["session_duration"] = time.time() - self.start_time
            
            # Add face mesh landmarks for visualization (optional)
            if face_results.multi_face_landmarks:
                face_landmarks = []
                for landmark in face_results.multi_face_landmarks[0].landmark:
                    face_landmarks.append({
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z
                    })
                features["face_landmarks"] = face_landmarks[:468]  # Limit to avoid large payloads
            
            # Add hand landmarks for visualization (optional)
            if hand_results.multi_hand_landmarks:
                hands_landmarks = []
                for hand_landmark in hand_results.multi_hand_landmarks:
                    hand_points = []
                    for landmark in hand_landmark.landmark:
                        hand_points.append({
                            "x": landmark.x,
                            "y": landmark.y,
                            "z": landmark.z
                        })
                    hands_landmarks.append(hand_points)
                features["hands_landmarks"] = hands_landmarks
            
            return features
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return {"error": str(e)}
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        recent_metrics = list(self.metrics_history)[-30:]  # Last 30 frames
        
        nervousness_scores = [m['nervousness_score'] for m in recent_metrics if 'nervousness_score' in m]
        blink_rates = [m['blink_stats']['blink_rate'] for m in recent_metrics if 'blink_stats' in m]
        hand_movements = [m['raw_metrics']['avg_hand_movement'] for m in recent_metrics if 'raw_metrics' in m]
        
        return {
            "total_frames": self.frame_count,
            "session_duration": time.time() - self.start_time,
            "current_nervousness": nervousness_scores[-1] if nervousness_scores else 0,
            "avg_nervousness": sum(nervousness_scores) / len(nervousness_scores) if nervousness_scores else 0,
            "avg_blink_rate": sum(blink_rates) / len(blink_rates) if blink_rates else 0,
            "avg_hand_movement": sum(hand_movements) / len(hand_movements) if hand_movements else 0,
            "recent_metrics_count": len(recent_metrics)
        }
    
    def reset_session(self):
        """Reset the current session"""
        self.metrics_history.clear()
        self.frame_count = 0
        self.start_time = time.time()
        logger.info("Session reset")

# Global video processor instance
video_processor = VideoProcessor()

async def handle_client(websocket, path):
    """Handle WebSocket client connections"""
    client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    logger.info(f"New client connected: {client_id}")
    
    try:
        async for message in websocket:
            try:
                # Parse incoming message
                data = json.loads(message)
                message_type = data.get("type")
                
                if message_type == "video_frame":
                    # Process video frame
                    frame_data = data.get("frame")
                    if not frame_data:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": "No frame data provided"
                        }))
                        continue
                    
                    # Process the frame
                    features = video_processor.process_frame(frame_data)
                    
                    # Send back the extracted features
                    response = {
                        "type": "features",
                        "data": features,
                        "timestamp": time.time()
                    }
                    await websocket.send(json.dumps(response))
                
                elif message_type == "get_stats":
                    # Get session statistics
                    stats = video_processor.get_session_stats()
                    response = {
                        "type": "stats",
                        "data": stats,
                        "timestamp": time.time()
                    }
                    await websocket.send(json.dumps(response))
                
                elif message_type == "reset_session":
                    # Reset the session
                    video_processor.reset_session()
                    response = {
                        "type": "session_reset",
                        "message": "Session reset successfully",
                        "timestamp": time.time()
                    }
                    await websocket.send(json.dumps(response))
                
                elif message_type == "ping":
                    # Respond to ping
                    response = {
                        "type": "pong",
                        "timestamp": time.time()
                    }
                    await websocket.send(json.dumps(response))
                
                else:
                    # Unknown message type
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    }))
                    
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                logger.error(f"Error handling message from {client_id}: {e}")
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
                
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"Error with client {client_id}: {e}")
    finally:
        logger.info(f"Cleaning up connection for {client_id}")

async def start_server():
    """Start the WebSocket server"""
    host = "localhost"
    port = 8765
    
    logger.info(f"Starting WebSocket server on {host}:{port}")
    
    # Start the server
    server = await websockets.serve(
        handle_client,
        host,
        port,
        ping_interval=20,
        ping_timeout=10,
        max_size=10 * 1024 * 1024,  # 10MB max message size for video frames
        compression=None  # Disable compression for better performance
    )
    
    logger.info(f"WebSocket server running on ws://{host}:{port}")
    logger.info("Supported message types:")
    logger.info("  - video_frame: Send video frame for processing")
    logger.info("  - get_stats: Get session statistics")
    logger.info("  - reset_session: Reset current session")
    logger.info("  - ping: Health check")
    
    return server

def run_server():
    """Run the WebSocket server"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        server = loop.run_until_complete(start_server())
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    finally:
        logger.info("Cleaning up server...")
        loop.close()

if __name__ == "__main__":
    # Check if dependencies are available
    try:
        import mediapipe
        import cv2
        import websockets
        logger.info("All dependencies available")
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Install required packages: pip install websockets mediapipe opencv-python")
        exit(1)
    
    # Run the server
    run_server()
