import asyncio
import websockets
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import cv2
import mediapipe as mp
import numpy as np
import base64
import json
import logging
from typing import Dict, Any, List
import io
from PIL import Image
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MediaPipeProcessor:
    """Enhanced MediaPipe processor for edge AI applications"""
    
    def __init__(self):
        # Initialize MediaPipe solutions
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_holistic = mp.solutions.holistic
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        
        # Initialize processors with optimized settings for edge computing
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.7
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=2,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.holistic = self.mp_holistic.Holistic(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.selfie_segmentation = self.mp_selfie_segmentation.SelfieSegmentation(
            model_selection=0
        )
        
    def extract_face_features(self, landmarks) -> Dict[str, Any]:
        """Extract meaningful features from face landmarks for edge AI"""
        if not landmarks:
            return {}
        
        # Convert landmarks to numpy array for easier processing
        points = np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark])
        
        # Calculate face orientation (basic example)
        nose_tip = points[1]  # Nose tip landmark
        left_eye = points[33]  # Left eye landmark
        right_eye = points[263]  # Right eye landmark
        
        # Calculate head pose angles (simplified)
        eye_center = (left_eye + right_eye) / 2
        face_direction = nose_tip - eye_center
        
        # Calculate face dimensions
        face_width = np.linalg.norm(points[356] - points[127])  # Left to right face
        face_height = np.linalg.norm(points[10] - points[152])  # Top to bottom face
        
        return {
            "face_orientation": {
                "x": float(face_direction[0]),
                "y": float(face_direction[1]),
                "z": float(face_direction[2])
            },
            "face_dimensions": {
                "width": float(face_width),
                "height": float(face_height),
                "aspect_ratio": float(face_width / face_height if face_height > 0 else 0)
            },
            "eye_center": {
                "x": float(eye_center[0]),
                "y": float(eye_center[1])
            }
        }
    
    def extract_hand_features(self, landmarks) -> Dict[str, Any]:
        """Extract hand gesture features for edge AI"""
        if not landmarks:
            return {}
        
        points = np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark])
        
        # Calculate hand openness (distance between fingertips)
        fingertips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips
        fingertip_points = points[fingertips]
        
        # Calculate average distance between fingertips
        distances = []
        for i in range(len(fingertips)):
            for j in range(i+1, len(fingertips)):
                dist = np.linalg.norm(fingertip_points[i] - fingertip_points[j])
                distances.append(dist)
        
        avg_fingertip_distance = np.mean(distances)
        
        # Calculate hand center
        hand_center = np.mean(points, axis=0)
        
        # Simple gesture recognition (very basic)
        wrist = points[0]
        middle_mcp = points[9]
        hand_direction = middle_mcp - wrist
        
        return {
            "hand_openness": float(avg_fingertip_distance),
            "hand_center": {
                "x": float(hand_center[0]),
                "y": float(hand_center[1]),
                "z": float(hand_center[2])
            },
            "hand_direction": {
                "x": float(hand_direction[0]),
                "y": float(hand_direction[1]),
                "z": float(hand_direction[2])
            },
            "fingertip_positions": [
                {"x": float(point[0]), "y": float(point[1]), "z": float(point[2])}
                for point in fingertip_points
            ]
        }
    
    def extract_pose_features(self, landmarks) -> Dict[str, Any]:
        """Extract pose features for edge AI analysis"""
        if not landmarks:
            return {}
        
        points = np.array([[lm.x, lm.y, lm.z, lm.visibility] for lm in landmarks.landmark])
        
        # Calculate body orientation
        left_shoulder = points[11][:3]
        right_shoulder = points[12][:3]
        left_hip = points[23][:3]
        right_hip = points[24][:3]
        
        # Calculate shoulder and hip alignment
        shoulder_center = (left_shoulder + right_shoulder) / 2
        hip_center = (left_hip + right_hip) / 2
        
        # Body posture vector
        posture_vector = shoulder_center - hip_center
        
        # Calculate arm positions
        left_elbow = points[13][:3]
        right_elbow = points[14][:3]
        left_wrist = points[15][:3]
        right_wrist = points[16][:3]
        
        # Simple activity recognition features
        arm_spread = np.linalg.norm(left_wrist - right_wrist)
        body_height = np.linalg.norm(posture_vector)
        
        return {
            "posture": {
                "x": float(posture_vector[0]),
                "y": float(posture_vector[1]),
                "z": float(posture_vector[2])
            },
            "body_center": {
                "x": float(hip_center[0]),
                "y": float(hip_center[1]),
                "z": float(hip_center[2])
            },
            "arm_spread": float(arm_spread),
            "body_height": float(body_height),
            "activity_indicators": {
                "arms_raised": bool(left_wrist[1] < left_shoulder[1] and right_wrist[1] < right_shoulder[1]),
                "arms_crossed": bool(arm_spread < 0.3),
                "standing_upright": bool(abs(posture_vector[0]) < 0.1)
            }
        }
    
    def process_frame(self, frame: np.ndarray, analysis_type: str = "holistic") -> Dict[str, Any]:
        """Process frame with enhanced edge AI features"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = {}
        annotated_frame = frame.copy()
        
        try:
            if analysis_type == "face_detection":
                face_results = self.face_detection.process(rgb_frame)
                results["faces"] = []
                
                if face_results.detections:
                    for detection in face_results.detections:
                        self.mp_drawing.draw_detection(annotated_frame, detection)
                        
                        bbox = detection.location_data.relative_bounding_box
                        results["faces"].append({
                            "confidence": float(detection.score[0]),
                            "bbox": {
                                "x": float(bbox.xmin),
                                "y": float(bbox.ymin),
                                "width": float(bbox.width),
                                "height": float(bbox.height)
                            }
                        })
            
            elif analysis_type == "face_mesh":
                face_results = self.face_mesh.process(rgb_frame)
                results["face_analysis"] = []
                
                if face_results.multi_face_landmarks:
                    for face_landmarks in face_results.multi_face_landmarks:
                        self.mp_drawing.draw_landmarks(
                            annotated_frame,
                            face_landmarks,
                            self.mp_face_mesh.FACEMESH_CONTOURS,
                            landmark_drawing_spec=None,
                            connection_drawing_spec=self.mp_drawing_styles
                            .get_default_face_mesh_contours_style()
                        )
                        
                        # Extract AI features
                        face_features = self.extract_face_features(face_landmarks)
                        results["face_analysis"].append(face_features)
            
            elif analysis_type == "hands":
                hand_results = self.hands.process(rgb_frame)
                results["hand_analysis"] = []
                
                if hand_results.multi_hand_landmarks:
                    for hand_landmarks in hand_results.multi_hand_landmarks:
                        self.mp_drawing.draw_landmarks(
                            annotated_frame,
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing_styles.get_default_hand_landmarks_style(),
                            self.mp_drawing_styles.get_default_hand_connections_style()
                        )
                        
                        # Extract AI features
                        hand_features = self.extract_hand_features(hand_landmarks)
                        results["hand_analysis"].append(hand_features)
            
            elif analysis_type == "pose":
                pose_results = self.pose.process(rgb_frame)
                
                if pose_results.pose_landmarks:
                    self.mp_drawing.draw_landmarks(
                        annotated_frame,
                        pose_results.pose_landmarks,
                        self.mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                    )
                    
                    # Extract AI features
                    pose_features = self.extract_pose_features(pose_results.pose_landmarks)
                    results["pose_analysis"] = pose_features
            
            elif analysis_type == "holistic":
                holistic_results = self.holistic.process(rgb_frame)
                
                # Process all components
                if holistic_results.face_landmarks:
                    self.mp_drawing.draw_landmarks(
                        annotated_frame,
                        holistic_results.face_landmarks,
                        self.mp_holistic.FACEMESH_CONTOURS,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=self.mp_drawing_styles
                        .get_default_face_mesh_contours_style()
                    )
                    results["face_analysis"] = self.extract_face_features(holistic_results.face_landmarks)
                
                if holistic_results.pose_landmarks:
                    self.mp_drawing.draw_landmarks(
                        annotated_frame,
                        holistic_results.pose_landmarks,
                        self.mp_holistic.POSE_CONNECTIONS,
                        landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                    )
                    results["pose_analysis"] = self.extract_pose_features(holistic_results.pose_landmarks)
                
                if holistic_results.left_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        annotated_frame,
                        holistic_results.left_hand_landmarks,
                        self.mp_holistic.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
                    results["left_hand_analysis"] = self.extract_hand_features(holistic_results.left_hand_landmarks)
                
                if holistic_results.right_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        annotated_frame,
                        holistic_results.right_hand_landmarks,
                        self.mp_holistic.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
                    results["right_hand_analysis"] = self.extract_hand_features(holistic_results.right_hand_landmarks)
            
            elif analysis_type == "segmentation":
                seg_results = self.selfie_segmentation.process(rgb_frame)
                
                # Create segmentation mask
                mask = seg_results.segmentation_mask
                condition = np.stack((mask,) * 3, axis=-1) > 0.1
                
                # Apply background replacement (blur effect)
                blurred_frame = cv2.GaussianBlur(annotated_frame, (55, 55), 0)
                annotated_frame = np.where(condition, annotated_frame, blurred_frame)
                
                results["segmentation"] = {
                    "mask_applied": True,
                    "background_effect": "blur"
                }
        
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            results["error"] = str(e)
        
        return {
            "analysis_results": results,
            "annotated_frame": annotated_frame,
            "timestamp": asyncio.get_event_loop().time()
        }

# Initialize FastAPI app
app = FastAPI(title="Edge AI MediaPipe Server", version="1.0.0")

# Initialize MediaPipe processor
processor = MediaPipeProcessor()

# Store active WebSocket connections
connections: List[WebSocket] = []

@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    """Serve the main HTML client"""
    html_file = Path(__file__).parent / "mediapipe_client.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text(), status_code=200)
    else:
        return HTMLResponse(content="""
        <html>
            <head><title>Edge AI MediaPipe Server</title></head>
            <body>
                <h1>Edge AI MediaPipe Server</h1>
                <p>Server is running! The client HTML file is not found.</p>
                <p>WebSocket endpoint available at: ws://localhost:8000/ws</p>
            </body>
        </html>
        """, status_code=200)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "mediapipe_available": True,
        "active_connections": len(connections)
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time video processing"""
    await websocket.accept()
    connections.append(websocket)
    client_id = f"{websocket.client.host}:{websocket.client.port}"
    logger.info(f"Client {client_id} connected")
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to Edge AI MediaPipe server",
            "client_id": client_id,
            "supported_analysis_types": [
                "face_detection", "face_mesh", "hands", "pose", "holistic", "segmentation"
            ]
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data.get("type") == "video_frame":
                await process_video_frame(websocket, data)
            elif data.get("type") == "config":
                await handle_config(websocket, data)
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {data.get('type')}"
                })
    
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"Error handling client {client_id}: {e}")
    finally:
        if websocket in connections:
            connections.remove(websocket)

async def process_video_frame(websocket: WebSocket, data: Dict[str, Any]):
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
        results = processor.process_frame(frame, analysis_type)
        
        # Encode processed frame back to base64
        _, buffer = cv2.imencode('.jpg', results["annotated_frame"], [cv2.IMWRITE_JPEG_QUALITY, 80])
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
        
        await websocket.send_json(response)
        
    except Exception as e:
        logger.error(f"Error processing video frame: {e}")
        await websocket.send_json({
            "type": "error",
            "message": f"Error processing frame: {str(e)}"
        })

async def handle_config(websocket: WebSocket, data: Dict[str, Any]):
    """Handle configuration updates"""
    try:
        config = data.get("config", {})
        logger.info(f"Received config update: {config}")
        
        # Here you could update MediaPipe parameters based on config
        # For example, confidence thresholds, model complexity, etc.
        
        await websocket.send_json({
            "type": "config_updated",
            "message": "Configuration updated successfully",
            "config": config
        })
        
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Error updating config: {str(e)}"
        })

if __name__ == "__main__":
    # Run the FastAPI server with WebSocket support
    uvicorn.run(
        "edge_ai_combined_server:app",
        host="localhost",
        port=8000,
        reload=True,
        log_level="info"
    )
