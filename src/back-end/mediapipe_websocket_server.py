import asyncio
import websockets
import cv2
import mediapipe as mp
import numpy as np
import base64
import json
import logging
from typing import Dict, Any
import io
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MediaPipeVideoProcessor:
    """
    Edge AI video processor using MediaPipe for real-time analysis
    """
    
    def __init__(self):
        # Initialize MediaPipe solutions
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_holistic = mp.solutions.holistic
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize processors
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.holistic = self.mp_holistic.Holistic(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
    def process_frame(self, frame: np.ndarray, analysis_type: str = "holistic") -> Dict[str, Any]:
        """
        Process a single frame using MediaPipe
        
        Args:
            frame: Input frame as numpy array
            analysis_type: Type of analysis to perform
                          ("face_detection", "face_mesh", "hands", "pose", "holistic")
        
        Returns:
            Dictionary containing analysis results and processed frame
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = {}
        annotated_frame = frame.copy()
        
        try:
            if analysis_type == "face_detection":
                face_results = self.face_detection.process(rgb_frame)
                results["faces"] = []
                
                if face_results.detections:
                    for detection in face_results.detections:
                        # Draw face detection
                        self.mp_drawing.draw_detection(annotated_frame, detection)
                        
                        # Extract face data
                        bbox = detection.location_data.relative_bounding_box
                        results["faces"].append({
                            "confidence": detection.score[0],
                            "bbox": {
                                "x": bbox.xmin,
                                "y": bbox.ymin,
                                "width": bbox.width,
                                "height": bbox.height
                            }
                        })
            
            elif analysis_type == "face_mesh":
                face_results = self.face_mesh.process(rgb_frame)
                results["face_landmarks"] = []
                
                if face_results.multi_face_landmarks:
                    for face_landmarks in face_results.multi_face_landmarks:
                        # Draw face mesh
                        self.mp_drawing.draw_landmarks(
                            annotated_frame,
                            face_landmarks,
                            self.mp_face_mesh.FACEMESH_CONTOURS,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=self.mp_drawing_styles
                            .get_default_face_mesh_contours_style()
                        )
                        
                        # Extract landmarks
                        landmarks = []
                        for landmark in face_landmarks.landmark:
                            landmarks.append({
                                "x": landmark.x,
                                "y": landmark.y,
                                "z": landmark.z
                            })
                        results["face_landmarks"].append(landmarks)
            
            elif analysis_type == "hands":
                hand_results = self.hands.process(rgb_frame)
                results["hands"] = []
                
                if hand_results.multi_hand_landmarks:
                    for hand_landmarks in hand_results.multi_hand_landmarks:
                        # Draw hand landmarks
                        self.mp_drawing.draw_landmarks(
                            annotated_frame,
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing_styles.get_default_hand_landmarks_style(),
                            self.mp_drawing_styles.get_default_hand_connections_style()
                        )
                        
                        # Extract hand landmarks
                        landmarks = []
                        for landmark in hand_landmarks.landmark:
                            landmarks.append({
                                "x": landmark.x,
                                "y": landmark.y,
                                "z": landmark.z
                            })
                        results["hands"].append(landmarks)
            
            elif analysis_type == "pose":
                pose_results = self.pose.process(rgb_frame)
                results["pose"] = []
                
                if pose_results.pose_landmarks:
                    # Draw pose landmarks
                    self.mp_drawing.draw_landmarks(
                        annotated_frame,
                        pose_results.pose_landmarks,
                        self.mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                    )
                    
                    # Extract pose landmarks
                    landmarks = []
                    for landmark in pose_results.pose_landmarks.landmark:
                        landmarks.append({
                            "x": landmark.x,
                            "y": landmark.y,
                            "z": landmark.z,
                            "visibility": landmark.visibility
                        })
                    results["pose"] = landmarks
            
            elif analysis_type == "holistic":
                holistic_results = self.holistic.process(rgb_frame)
                
                # Process face landmarks
                if holistic_results.face_landmarks:
                    self.mp_drawing.draw_landmarks(
                        annotated_frame,
                        holistic_results.face_landmarks,
                        self.mp_holistic.FACEMESH_CONTOURS,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=self.mp_drawing_styles
                        .get_default_face_mesh_contours_style()
                    )
                    
                    face_landmarks = []
                    for landmark in holistic_results.face_landmarks.landmark:
                        face_landmarks.append({
                            "x": landmark.x,
                            "y": landmark.y,
                            "z": landmark.z
                        })
                    results["face_landmarks"] = face_landmarks
                
                # Process pose landmarks
                if holistic_results.pose_landmarks:
                    self.mp_drawing.draw_landmarks(
                        annotated_frame,
                        holistic_results.pose_landmarks,
                        self.mp_holistic.POSE_CONNECTIONS,
                        landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                    )
                    
                    pose_landmarks = []
                    for landmark in holistic_results.pose_landmarks.landmark:
                        pose_landmarks.append({
                            "x": landmark.x,
                            "y": landmark.y,
                            "z": landmark.z,
                            "visibility": landmark.visibility
                        })
                    results["pose_landmarks"] = pose_landmarks
                
                # Process hand landmarks
                if holistic_results.left_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        annotated_frame,
                        holistic_results.left_hand_landmarks,
                        self.mp_holistic.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
                    
                    left_hand_landmarks = []
                    for landmark in holistic_results.left_hand_landmarks.landmark:
                        left_hand_landmarks.append({
                            "x": landmark.x,
                            "y": landmark.y,
                            "z": landmark.z
                        })
                    results["left_hand_landmarks"] = left_hand_landmarks
                
                if holistic_results.right_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        annotated_frame,
                        holistic_results.right_hand_landmarks,
                        self.mp_holistic.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
                    
                    right_hand_landmarks = []
                    for landmark in holistic_results.right_hand_landmarks.landmark:
                        right_hand_landmarks.append({
                            "x": landmark.x,
                            "y": landmark.y,
                            "z": landmark.z
                        })
                    results["right_hand_landmarks"] = right_hand_landmarks
        
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            results["error"] = str(e)
        
        return {
            "analysis_results": results,
            "annotated_frame": annotated_frame,
            "timestamp": asyncio.get_event_loop().time()
        }

class EdgeAIWebSocketServer:
    """
    WebSocket server for edge AI video processing with MediaPipe
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.processor = MediaPipeVideoProcessor()
        self.clients = set()
        
    async def handle_client(self, websocket, path):
        """Handle individual client connections"""
        self.clients.add(websocket)
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"Client {client_id} connected")
        
        try:
            await websocket.send(json.dumps({
                "type": "connection_established",
                "message": "Connected to Edge AI MediaPipe server",
                "client_id": client_id,
                "supported_analysis_types": [
                    "face_detection", "face_mesh", "hands", "pose", "holistic"
                ]
            }))
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.process_message(websocket, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON format"
                    }))
                except Exception as e:
                    logger.error(f"Error processing message from {client_id}: {e}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            self.clients.discard(websocket)
    
    async def process_message(self, websocket, data: Dict[str, Any]):
        """Process incoming messages from clients"""
        message_type = data.get("type")
        
        if message_type == "video_frame":
            await self.process_video_frame(websocket, data)
        elif message_type == "config":
            await self.handle_config(websocket, data)
        elif message_type == "ping":
            await websocket.send(json.dumps({"type": "pong"}))
        else:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }))
    
    async def process_video_frame(self, websocket, data: Dict[str, Any]):
        """Process video frame with MediaPipe"""
        try:
            # Decode base64 image
            image_data = data.get("image_data")
            analysis_type = data.get("analysis_type", "holistic")
            
            if not image_data:
                raise ValueError("No image data provided")
            
            # Remove data URL prefix if present
            if "," in image_data:
                image_data = image_data.split(",")[1]
            
            # Decode base64 to bytes
            image_bytes = base64.b64decode(image_data)
            
            # Convert to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                raise ValueError("Could not decode image")
            
            # Process frame with MediaPipe
            results = self.processor.process_frame(frame, analysis_type)
            
            # Encode processed frame back to base64
            _, buffer = cv2.imencode('.jpg', results["annotated_frame"])
            processed_image_b64 = base64.b64encode(buffer).decode('utf-8')
            
            # Send results back to client
            response = {
                "type": "analysis_results",
                "analysis_type": analysis_type,
                "results": results["analysis_results"],
                "processed_image": f"data:image/jpeg;base64,{processed_image_b64}",
                "timestamp": results["timestamp"],
                "frame_id": data.get("frame_id")
            }
            
            await websocket.send(json.dumps(response))
            
        except Exception as e:
            logger.error(f"Error processing video frame: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Error processing frame: {str(e)}"
            }))
    
    async def handle_config(self, websocket, data: Dict[str, Any]):
        """Handle configuration updates"""
        try:
            config = data.get("config", {})
            logger.info(f"Received config update: {config}")
            
            # Here you could update MediaPipe parameters based on config
            # For example, confidence thresholds, model complexity, etc.
            
            await websocket.send(json.dumps({
                "type": "config_updated",
                "message": "Configuration updated successfully",
                "config": config
            }))
            
        except Exception as e:
            await websocket.send(json.dumps({
                "type": "error",
                "message": f"Error updating config: {str(e)}"
            }))
    
    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"Starting Edge AI MediaPipe WebSocket server on {self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info("Server is running... Press Ctrl+C to stop")
            await asyncio.Future()  # Run forever

def main():
    """Main function to start the server"""
    server = EdgeAIWebSocketServer(host="localhost", port=8765)
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    main()
