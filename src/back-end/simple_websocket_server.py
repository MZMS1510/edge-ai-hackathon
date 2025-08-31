import asyncio
import websockets
import cv2
import numpy as np
import json
import base64
import time
from typing import Dict, Any
import logging
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleVideoProcessor:
    """Simplified video processor using OpenCV instead of MediaPipe"""
    
    def __init__(self):
        # Initialize OpenCV face detector
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Metrics storage
        self.metrics_history = deque(maxlen=1000)
        self.frame_count = 0
        self.start_time = time.time()
        self.previous_face_center = None
        
    def process_frame(self, frame_data: bytes) -> Dict[str, Any]:
        """Process a single video frame and extract basic features"""
        try:
            # Decode base64 image
            img_data = base64.b64decode(frame_data)
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                logger.error("Failed to decode frame")
                return {"error": "Failed to decode frame"}
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            face_detected = len(faces)
            
            # Calculate basic metrics
            nervousness_score = self._calculate_simple_nervousness(faces, gray)
            head_movement = self._calculate_head_movement(faces)
            blink_detected = self._detect_simple_blinks(faces, gray)
            
            # Create features dictionary
            features = {
                'timestamp': time.time(),
                'nervousness_score': nervousness_score,
                'blink_detected': blink_detected,
                'blink_stats': {
                    'avg_ear': 0.3,  # Placeholder
                    'blink_rate': 0.15 if blink_detected else 0.1
                },
                'hand_movement': 0.0,  # Not implemented without MediaPipe
                'head_movement': head_movement,
                'hands_detected': 0,  # Not implemented without MediaPipe
                'face_detected': face_detected,
                'frame_number': self.frame_count,
                'processing_time': time.time(),
                'session_duration': time.time() - self.start_time,
                'raw_metrics': {
                    'avg_hand_movement': 0.0,
                    'avg_head_movement': head_movement,
                    'hand_movement_std': 0.0,
                    'head_movement_std': 0.0,
                    'face_area': sum(w * h for x, y, w, h in faces) if faces else 0
                }
            }
            
            # Store metrics
            self.metrics_history.append(features)
            self.frame_count += 1
            
            # Add face rectangles for visualization
            if len(faces) > 0:
                face_rects = []
                for (x, y, w, h) in faces:
                    face_rects.append({
                        'x': float(x / frame.shape[1]),  # Normalize coordinates
                        'y': float(y / frame.shape[0]),
                        'width': float(w / frame.shape[1]),
                        'height': float(h / frame.shape[0])
                    })
                features['face_rectangles'] = face_rects
            
            return features
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return {"error": str(e)}
    
    def _calculate_simple_nervousness(self, faces, gray_frame):
        """Calculate a simple nervousness score based on face area variation"""
        if len(faces) == 0:
            return 0.5  # Medium nervousness when no face detected
        
        # Use face area as a proxy for distance/nervousness
        face_areas = [w * h for x, y, w, h in faces]
        total_area = sum(face_areas)
        
        # Simple heuristic: smaller faces might indicate nervousness (moving away)
        # or very large faces might indicate nervousness (moving too close)
        frame_area = gray_frame.shape[0] * gray_frame.shape[1]
        face_ratio = total_area / frame_area
        
        if face_ratio < 0.05:  # Very small face
            return min(0.8, 0.5 + (0.05 - face_ratio) * 10)
        elif face_ratio > 0.3:  # Very large face
            return min(0.8, 0.5 + (face_ratio - 0.3) * 2)
        else:
            return 0.2  # Normal face size, low nervousness
    
    def _calculate_head_movement(self, faces):
        """Calculate head movement based on face center displacement"""
        if len(faces) == 0:
            return 0.0
        
        # Get center of largest face
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = largest_face
        current_center = np.array([x + w/2, y + h/2])
        
        if self.previous_face_center is not None:
            movement = np.linalg.norm(current_center - self.previous_face_center)
            movement = movement / 100.0  # Normalize
        else:
            movement = 0.0
        
        self.previous_face_center = current_center
        return min(movement, 1.0)
    
    def _detect_simple_blinks(self, faces, gray_frame):
        """Simple blink detection using eye detection"""
        if len(faces) == 0:
            return False
        
        # Look for eyes in detected faces
        for (x, y, w, h) in faces:
            roi_gray = gray_frame[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            
            # If no eyes detected, might be blinking
            if len(eyes) == 0:
                return True
        
        return False
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        recent_metrics = list(self.metrics_history)[-30:]  # Last 30 frames
        
        nervousness_scores = [m['nervousness_score'] for m in recent_metrics if 'nervousness_score' in m]
        head_movements = [m['head_movement'] for m in recent_metrics if 'head_movement' in m]
        
        return {
            "total_frames": self.frame_count,
            "session_duration": time.time() - self.start_time,
            "current_nervousness": nervousness_scores[-1] if nervousness_scores else 0,
            "avg_nervousness": sum(nervousness_scores) / len(nervousness_scores) if nervousness_scores else 0,
            "avg_blink_rate": 0.15,  # Placeholder
            "avg_hand_movement": 0.0,  # Not implemented
            "avg_head_movement": sum(head_movements) / len(head_movements) if head_movements else 0,
            "recent_metrics_count": len(recent_metrics)
        }
    
    def reset_session(self):
        """Reset the current session"""
        self.metrics_history.clear()
        self.frame_count = 0
        self.start_time = time.time()
        self.previous_face_center = None
        logger.info("Session reset")

# Global video processor instance
video_processor = SimpleVideoProcessor()

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
    logger.info("Note: Using OpenCV-based face detection (MediaPipe not available)")
    
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
        import cv2
        import websockets
        logger.info("OpenCV and WebSockets available - using simple face detection")
        logger.info("Note: For advanced features, install MediaPipe if available for your platform")
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Install required packages: pip install websockets opencv-python")
        exit(1)
    
    # Run the server
    run_server()
