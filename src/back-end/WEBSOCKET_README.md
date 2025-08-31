# Edge Coach - WebSocket Video Processing

This module provides real-time video processing using WebSockets and MediaPipe for the Edge Coach application.

## Features

- 🎥 **Real-time video processing** using MediaPipe
- 🔌 **WebSocket communication** for low-latency streaming
- 🧠 **AI-powered analysis** of facial expressions, hand movements, and nervousness detection
- 📊 **Live metrics** including blink detection, hand movement tracking, and nervousness scoring
- 🔄 **Session management** with reset and statistics capabilities
- 🌐 **Web-based test client** for easy testing and demonstration

## Components

### 1. WebSocket Video Server (`websocket_video_server.py`)
Standalone WebSocket server that processes video frames using MediaPipe.

**Features:**
- Face mesh detection and tracking
- Hand landmarks detection
- Nervousness score calculation
- Blink detection and analysis
- Real-time feature extraction

### 2. Combined Server (`combined_server.py`)
Integrated server that combines the existing FastAPI REST API with WebSocket capabilities.

**Features:**
- All REST API endpoints from the original application
- WebSocket endpoint for video processing
- Shared data store between REST and WebSocket
- Built-in test client serving

### 3. Test Client (`test_websocket_client.html`)
Web-based client for testing the WebSocket video processing.

**Features:**
- Camera access and video streaming
- Real-time metrics display
- Interactive controls for starting/stopping processing
- Live feature visualization

## Quick Start

### Option 1: Standalone WebSocket Server

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the WebSocket server:**
   ```bash
   cd edge-coach/src
   python websocket_video_server.py
   ```

3. **Open the test client:**
   - Open `test_websocket_client.html` in your browser
   - Or use the test script: `python test_websocket.py`

### Option 2: Combined Server (Recommended)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the combined server:**
   ```bash
   cd edge-coach/src
   python combined_server.py
   ```

3. **Access the services:**
   - **REST API:** http://localhost:8000/api
   - **WebSocket:** ws://localhost:8000/ws
   - **Test Client:** http://localhost:8000/test
   - **API Docs:** http://localhost:8000/docs

## WebSocket Protocol

### Message Types

#### Client to Server:

1. **video_frame** - Send video frame for processing
   ```json
   {
     "type": "video_frame",
     "frame": "base64_encoded_jpeg_data",
     "timestamp": 1640995200000
   }
   ```

2. **get_stats** - Request session statistics
   ```json
   {
     "type": "get_stats"
   }
   ```

3. **reset_session** - Reset current session
   ```json
   {
     "type": "reset_session"
   }
   ```

4. **ping** - Health check
   ```json
   {
     "type": "ping"
   }
   ```

#### Server to Client:

1. **features** - Video processing results
   ```json
   {
     "type": "features",
     "data": {
       "nervousness_score": 0.234,
       "blink_detected": true,
       "blink_stats": {
         "avg_ear": 0.278,
         "blink_rate": 0.15
       },
       "hand_movement": 0.045,
       "head_movement": 0.012,
       "hands_detected": 2,
       "face_detected": 1,
       "frame_number": 150,
       "timestamp": 1640995200.123
     },
     "timestamp": 1640995200.123
   }
   ```

2. **stats** - Session statistics
   ```json
   {
     "type": "stats",
     "data": {
       "total_frames": 500,
       "session_duration": 25.6,
       "avg_nervousness": 0.156,
       "avg_blink_rate": 0.12,
       "avg_hand_movement": 0.034
     },
     "timestamp": 1640995200.123
   }
   ```

3. **error** - Error message
   ```json
   {
     "type": "error",
     "message": "Invalid frame data"
   }
   ```

## Frontend Integration

### JavaScript Example

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// Handle connection open
ws.onopen = function(event) {
    console.log('Connected to WebSocket server');
};

// Handle incoming messages
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'features') {
        // Update UI with real-time metrics
        updateMetrics(data.data);
    } else if (data.type === 'stats') {
        // Display session statistics
        displayStats(data.data);
    }
};

// Send video frame
function sendFrame(videoElement) {
    // Capture frame from video element
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    ctx.drawImage(videoElement, 0, 0);
    
    // Convert to base64
    const dataURL = canvas.toDataURL('image/jpeg', 0.8);
    const base64Data = dataURL.split(',')[1];
    
    // Send to server
    ws.send(JSON.stringify({
        type: 'video_frame',
        frame: base64Data,
        timestamp: Date.now()
    }));
}
```

### React/Vue.js Integration

The WebSocket can be easily integrated into React or Vue.js applications:

```javascript
// React Hook example
import { useState, useEffect, useRef } from 'react';

function useWebSocketVideoProcessor() {
    const [metrics, setMetrics] = useState(null);
    const [connected, setConnected] = useState(false);
    const ws = useRef(null);
    
    useEffect(() => {
        ws.current = new WebSocket('ws://localhost:8000/ws');
        
        ws.current.onopen = () => setConnected(true);
        ws.current.onclose = () => setConnected(false);
        ws.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'features') {
                setMetrics(data.data);
            }
        };
        
        return () => ws.current.close();
    }, []);
    
    const sendFrame = (frameData) => {
        if (ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({
                type: 'video_frame',
                frame: frameData
            }));
        }
    };
    
    return { metrics, connected, sendFrame };
}
```

## Metrics Explanation

### Nervousness Score (0.0 - 1.0)
- Composite score based on blink rate, hand movement, and head movement
- 0.0 = Very calm, 1.0 = Very nervous
- Calculated using weighted average of normalized metrics

### Blink Detection
- **EAR (Eye Aspect Ratio)**: Measure of eye openness
- **Blink Rate**: Percentage of frames with detected blinks
- **Normal range**: 10-15% blink rate

### Movement Tracking
- **Hand Movement**: Average movement of detected hands between frames
- **Head Movement**: Movement of nose landmark (head position)
- **Normalized values**: 0.0 = No movement, higher values = more movement

## Performance Considerations

- **Frame Rate**: Process at 10-15 FPS for real-time performance
- **Image Quality**: JPEG compression at 80% quality for balance of speed/accuracy
- **Network**: WebSocket provides low-latency communication
- **Memory**: Metrics history limited to 1000 frames to prevent memory issues

## Troubleshooting

### Common Issues

1. **Camera not accessible**
   - Ensure browser permissions are granted
   - Use HTTPS for camera access on remote domains

2. **WebSocket connection fails**
   - Check server is running: `python combined_server.py`
   - Verify port 8000 is not blocked by firewall

3. **Poor detection accuracy**
   - Ensure good lighting conditions
   - Keep face and hands visible in frame
   - Adjust camera angle for optimal view

4. **High CPU usage**
   - Reduce frame processing rate
   - Lower video resolution if needed
   - Consider running on GPU if available

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Dependencies

- **mediapipe**: Face and hand detection
- **opencv-python**: Image processing
- **websockets**: WebSocket server/client
- **fastapi**: REST API framework
- **numpy**: Numerical computations

## License

This project is part of the Edge AI Hackathon submission.
