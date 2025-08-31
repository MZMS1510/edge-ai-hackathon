"""
Edge Coach - WebSocket Server

Real-time WebSocket server for live video and audio processing.
Provides low-latency communication for:
- Video frame processing with MediaPipe
- Audio analysis and feature extraction
- Real-time metrics calculation
- Live session statistics
- Multi-client broadcasting

Features:
- Handles multiple concurrent clients
- Base64 encoding/decoding for media data
- Automatic client management and cleanup
- Built-in HTML test client
- Error handling and logging

Usage:
    python websocket_server.py
    
WebSocket URL:
    ws://localhost:8765
    
Test Client:
    Open browser and navigate to the server URL for built-in test interface

Author: Edge AI Hackathon Team
License: MIT
"""

import asyncio
import websockets
import json
import base64
import cv2
import numpy as np
from typing import Dict, Set
import logging
from core_processing import MediaPipeProcessor, AudioProcessor
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EdgeCoachWebSocketServer:
    """Unified WebSocket server for real-time processing"""
    
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.mediapipe_processor = MediaPipeProcessor()
        self.audio_processor = AudioProcessor()
        
        # Session data
        self.session_data = {
            'metrics': [],
            'transcripts': [],
            'start_time': time.time()
        }
    
    async def register_client(self, websocket):
        """Register new client"""
        self.clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        # Send welcome message
        await websocket.send(json.dumps({
            'type': 'connection',
            'status': 'connected',
            'message': 'Connected to Edge Coach server'
        }))
    
    async def unregister_client(self, websocket):
        """Unregister client"""
        self.clients.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
    
    async def broadcast_to_clients(self, message):
        """Broadcast message to all connected clients"""
        if self.clients:
            disconnected = set()
            for client in self.clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            # Remove disconnected clients
            for client in disconnected:
                self.clients.discard(client)
    
    async def process_video_frame(self, frame_data):
        """Process video frame and extract metrics"""
        try:
            # Decode base64 frame
            frame_bytes = base64.b64decode(frame_data)
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return None
            
            # Process with MediaPipe
            results = self.mediapipe_processor.process_frame(frame)
            
            # Store metrics
            metrics = results['metrics']
            self.session_data['metrics'].append(metrics)
            
            # Encode annotated frame
            _, buffer = cv2.imencode('.jpg', results['annotated_frame'])
            annotated_frame_b64 = base64.b64encode(buffer).decode('utf-8')
            
            return {
                'type': 'video_analysis',
                'metrics': metrics,
                'joints': results['joints'],
                'annotated_frame': annotated_frame_b64,
                'timestamp': metrics['timestamp']
            }
            
        except Exception as e:
            logger.error(f"Error processing video frame: {e}")
            return {
                'type': 'error',
                'message': f"Video processing error: {str(e)}"
            }
    
    async def process_audio_data(self, audio_data):
        """Process audio data"""
        try:
            # Convert base64 audio to numpy array
            audio_bytes = base64.b64decode(audio_data)
            audio_array = np.frombuffer(audio_bytes, dtype=np.float32)
            
            # Process audio
            audio_features = self.audio_processor.process_audio_chunk(audio_array)
            
            if audio_features:
                return {
                    'type': 'audio_analysis',
                    'features': audio_features,
                    'timestamp': audio_features['timestamp']
                }
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            return {
                'type': 'error',
                'message': f"Audio processing error: {str(e)}"
            }
    
    async def handle_transcript(self, transcript_data):
        """Handle transcript data"""
        try:
            self.session_data['transcripts'].append({
                'text': transcript_data.get('text', ''),
                'timestamp': time.time(),
                'is_final': transcript_data.get('is_final', False)
            })
            
            return {
                'type': 'transcript_received',
                'text': transcript_data.get('text', ''),
                'is_final': transcript_data.get('is_final', False),
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error handling transcript: {e}")
            return {
                'type': 'error',
                'message': f"Transcript error: {str(e)}"
            }
    
    async def get_session_stats(self):
        """Get current session statistics"""
        metrics = self.session_data['metrics']
        
        if not metrics:
            return {
                'type': 'session_stats',
                'stats': {
                    'session_duration': time.time() - self.session_data['start_time'],
                    'total_frames': 0,
                    'message': 'No data yet'
                }
            }
        
        # Calculate statistics
        recent_metrics = metrics[-30:]  # Last 30 frames
        
        nervousness_scores = [m['nervousness_score'] for m in recent_metrics]
        blink_rates = [m['blink_stats']['blink_rate'] for m in recent_metrics]
        hand_movements = [m['raw_metrics']['avg_hand_movement'] for m in recent_metrics]
        
        stats = {
            'session_duration': time.time() - self.session_data['start_time'],
            'total_frames': len(metrics),
            'current_nervousness': nervousness_scores[-1] if nervousness_scores else 0,
            'avg_nervousness': sum(nervousness_scores) / len(nervousness_scores) if nervousness_scores else 0,
            'avg_blink_rate': sum(blink_rates) / len(blink_rates) if blink_rates else 0,
            'avg_hand_movement': sum(hand_movements) / len(hand_movements) if hand_movements else 0,
            'transcript_count': len(self.session_data['transcripts'])
        }
        
        return {
            'type': 'session_stats',
            'stats': stats,
            'timestamp': time.time()
        }
    
    async def reset_session(self):
        """Reset current session data"""
        self.session_data = {
            'metrics': [],
            'transcripts': [],
            'start_time': time.time()
        }
        
        return {
            'type': 'session_reset',
            'message': 'Session data reset',
            'timestamp': time.time()
        }
    
    async def handle_message(self, websocket, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            response = None
            
            if message_type == 'video_frame':
                response = await self.process_video_frame(data.get('frame'))
            
            elif message_type == 'audio_data':
                response = await self.process_audio_data(data.get('audio'))
            
            elif message_type == 'transcript':
                response = await self.handle_transcript(data.get('data', {}))
            
            elif message_type == 'get_stats':
                response = await self.get_session_stats()
            
            elif message_type == 'reset_session':
                response = await self.reset_session()
            
            elif message_type == 'ping':
                response = {
                    'type': 'pong',
                    'timestamp': time.time()
                }
            
            else:
                response = {
                    'type': 'error',
                    'message': f"Unknown message type: {message_type}"
                }
            
            # Send response
            if response:
                await websocket.send(json.dumps(response))
                
                # Broadcast certain types to all clients
                if message_type in ['video_frame', 'audio_data', 'transcript']:
                    await self.broadcast_to_clients(json.dumps(response))
        
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f"Server error: {str(e)}"
            }))
    
    async def handle_client(self, websocket, path):
        """Handle individual client connection"""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed")
        
        except Exception as e:
            logger.error(f"Error in client handler: {e}")
        
        finally:
            await self.unregister_client(websocket)
    
    def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"Starting Edge Coach WebSocket server on {self.host}:{self.port}")
        
        start_server = websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            max_size=10 * 1024 * 1024,  # 10MB max message size
            ping_interval=20,
            ping_timeout=10
        )
        
        return start_server
    
    def cleanup(self):
        """Cleanup resources"""
        self.mediapipe_processor.cleanup()


# HTML client for testing
HTML_CLIENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Edge Coach WebSocket Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .connected { background-color: #d4edda; color: #155724; }
        .disconnected { background-color: #f8d7da; color: #721c24; }
        video { width: 320px; height: 240px; }
        button { padding: 10px 15px; margin: 5px; cursor: pointer; }
        #messages { height: 200px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Edge Coach WebSocket Test Client</h1>
        
        <div class="section">
            <h3>Connection Status</h3>
            <div id="status" class="status disconnected">Disconnected</div>
            <button onclick="connect()">Connect</button>
            <button onclick="disconnect()">Disconnect</button>
        </div>
        
        <div class="section">
            <h3>Video Stream</h3>
            <video id="video" autoplay muted></video><br>
            <button onclick="startVideo()">Start Video</button>
            <button onclick="stopVideo()">Stop Video</button>
        </div>
        
        <div class="section">
            <h3>Controls</h3>
            <button onclick="getStats()">Get Stats</button>
            <button onclick="resetSession()">Reset Session</button>
            <button onclick="ping()">Ping</button>
        </div>
        
        <div class="section">
            <h3>Messages</h3>
            <div id="messages"></div>
        </div>
    </div>

    <script>
        let ws = null;
        let videoStream = null;
        let isStreaming = false;
        
        function addMessage(message) {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.textContent = new Date().toLocaleTimeString() + ': ' + message;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
        
        function updateStatus(connected) {
            const status = document.getElementById('status');
            if (connected) {
                status.textContent = 'Connected';
                status.className = 'status connected';
            } else {
                status.textContent = 'Disconnected';
                status.className = 'status disconnected';
            }
        }
        
        function connect() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                addMessage('Already connected');
                return;
            }
            
            ws = new WebSocket('ws://localhost:8765');
            
            ws.onopen = function() {
                updateStatus(true);
                addMessage('Connected to server');
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addMessage('Received: ' + data.type);
                console.log('Received:', data);
            };
            
            ws.onclose = function() {
                updateStatus(false);
                addMessage('Connection closed');
            };
            
            ws.onerror = function(error) {
                addMessage('Error: ' + error);
            };
        }
        
        function disconnect() {
            if (ws) {
                ws.close();
                ws = null;
            }
        }
        
        function sendMessage(message) {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify(message));
            } else {
                addMessage('Not connected');
            }
        }
        
        async function startVideo() {
            try {
                videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
                document.getElementById('video').srcObject = videoStream;
                isStreaming = true;
                addMessage('Video started');
                
                // Start sending frames (simplified for demo)
                setTimeout(sendVideoFrame, 1000);
            } catch (error) {
                addMessage('Error starting video: ' + error);
            }
        }
        
        function stopVideo() {
            if (videoStream) {
                videoStream.getTracks().forEach(track => track.stop());
                videoStream = null;
                isStreaming = false;
                addMessage('Video stopped');
            }
        }
        
        function sendVideoFrame() {
            if (!isStreaming || !ws || ws.readyState !== WebSocket.OPEN) {
                return;
            }
            
            // This is a simplified demo - normally you'd capture and encode frames
            sendMessage({
                type: 'video_frame',
                frame: 'dummy_frame_data'
            });
            
            if (isStreaming) {
                setTimeout(sendVideoFrame, 100); // 10 FPS
            }
        }
        
        function getStats() {
            sendMessage({ type: 'get_stats' });
        }
        
        function resetSession() {
            sendMessage({ type: 'reset_session' });
        }
        
        function ping() {
            sendMessage({ type: 'ping' });
        }
    </script>
</body>
</html>
"""

async def main():
    """Main function to run the server"""
    server = EdgeCoachWebSocketServer()
    
    try:
        # Start WebSocket server
        start_server = server.start_server()
        
        logger.info("Server is running...")
        logger.info(f"WebSocket server: ws://{server.host}:{server.port}")
        logger.info("Press Ctrl+C to stop")
        
        await start_server
        await asyncio.Future()  # Run forever
        
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    
    finally:
        server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
