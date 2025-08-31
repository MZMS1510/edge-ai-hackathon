#!/usr/bin/env python3
"""
Simple test script for the WebSocket video server
"""
import asyncio
import websockets
import json
import base64
import cv2
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_client():
    """Test client for the WebSocket video server"""
    uri = "ws://localhost:8765"
    
    try:
        logger.info(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            logger.info("✅ Connected to WebSocket server")
            
            # Test 1: Ping
            logger.info("🏓 Testing ping...")
            await websocket.send(json.dumps({"type": "ping"}))
            response = await websocket.recv()
            data = json.loads(response)
            logger.info(f"Ping response: {data}")
            
            # Test 2: Get initial stats
            logger.info("📊 Getting initial stats...")
            await websocket.send(json.dumps({"type": "get_stats"}))
            response = await websocket.recv()
            data = json.loads(response)
            logger.info(f"Initial stats: {data}")
            
            # Test 3: Send test video frames
            logger.info("🎬 Sending test video frames...")
            
            # Create a simple test image
            test_image = cv2.imread("test_frame.jpg") if cv2.os.path.exists("test_frame.jpg") else None
            
            if test_image is None:
                # Create a synthetic test image
                import numpy as np
                test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
                # Add some basic shapes to make it more interesting
                cv2.rectangle(test_image, (100, 100), (200, 200), (255, 0, 0), -1)
                cv2.circle(test_image, (400, 300), 50, (0, 255, 0), -1)
                logger.info("Created synthetic test image")
            else:
                logger.info("Using existing test_frame.jpg")
            
            # Send 10 test frames
            for i in range(10):
                # Encode image to base64
                _, buffer = cv2.imencode('.jpg', test_image)
                base64_data = base64.b64encode(buffer).decode('utf-8')
                
                # Send frame
                message = {
                    "type": "video_frame",
                    "frame": base64_data,
                    "timestamp": time.time()
                }
                
                await websocket.send(json.dumps(message))
                logger.info(f"Sent frame {i+1}/10")
                
                # Receive response
                response = await websocket.recv()
                data = json.loads(response)
                
                if data.get("type") == "features":
                    features = data.get("data", {})
                    logger.info(f"Frame {i+1} - Nervousness: {features.get('nervousness_score', 0):.3f}, "
                              f"Hands: {features.get('hands_detected', 0)}, "
                              f"Face: {features.get('face_detected', 0)}")
                else:
                    logger.warning(f"Unexpected response: {data}")
                
                # Small delay between frames
                await asyncio.sleep(0.1)
            
            # Test 4: Get final stats
            logger.info("📊 Getting final stats...")
            await websocket.send(json.dumps({"type": "get_stats"}))
            response = await websocket.recv()
            data = json.loads(response)
            logger.info(f"Final stats: {data}")
            
            # Test 5: Reset session
            logger.info("🔄 Resetting session...")
            await websocket.send(json.dumps({"type": "reset_session"}))
            response = await websocket.recv()
            data = json.loads(response)
            logger.info(f"Reset response: {data}")
            
            logger.info("✅ All tests completed successfully!")
            
    except ConnectionRefusedError:
        logger.error("❌ Connection refused. Make sure the WebSocket server is running on localhost:8765")
        logger.error("Run: python websocket_video_server.py")
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")

def test_combined_server():
    """Test the combined server WebSocket endpoint"""
    
    async def test_combined():
        uri = "ws://localhost:8000/ws"
        
        try:
            logger.info(f"Testing combined server at {uri}...")
            async with websockets.connect(uri) as websocket:
                logger.info("✅ Connected to combined server WebSocket")
                
                # Test ping
                await websocket.send(json.dumps({"type": "ping"}))
                response = await websocket.recv()
                data = json.loads(response)
                logger.info(f"Combined server ping response: {data}")
                
        except Exception as e:
            logger.error(f"❌ Combined server test failed: {e}")
    
    return asyncio.run(test_combined())

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "combined":
        logger.info("Testing combined server...")
        test_combined_server()
    else:
        logger.info("Testing standalone WebSocket server...")
        logger.info("Use 'python test_websocket.py combined' to test the combined server")
        asyncio.run(test_websocket_client())
