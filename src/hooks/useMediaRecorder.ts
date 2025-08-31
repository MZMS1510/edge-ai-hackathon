import { useState, useCallback } from 'react';
import { SessionType } from '../types/enums';

export const useMediaRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);

  const startRecording = useCallback(async (type: SessionType) => {
    try {
      setError(null);
      
      let stream: MediaStream;
      
      if (type === SessionType.AUDIO_ONLY) {
        // Request audio only
        stream = await navigator.mediaDevices.getUserMedia({ 
          audio: true 
        });
      } else if (type === SessionType.AUDIO_VIDEO) {
        // Request both audio and video (screen capture)
        const screenStream = await navigator.mediaDevices.getDisplayMedia({
          video: true,
          audio: true
        });
        
        // Also get microphone audio
        const audioStream = await navigator.mediaDevices.getUserMedia({
          audio: true
        });
        
        // Combine streams
        const combinedStream = new MediaStream([
          ...screenStream.getVideoTracks(),
          ...screenStream.getAudioTracks(),
          ...audioStream.getAudioTracks()
        ]);
        
        stream = combinedStream;
      } else {
        throw new Error('Invalid session type');
      }

      const recorder = new MediaRecorder(stream);
      setMediaRecorder(recorder);
      setIsRecording(true);
      
      recorder.start();
      
      console.log(`Started ${type} recording`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start recording';
      setError(errorMessage);
      console.error('Recording error:', err);
    }
  }, []);

  const stopRecording = useCallback((): Promise<Blob> => {
    return new Promise((resolve, reject) => {
      if (!mediaRecorder) {
        reject(new Error('No active recording'));
        return;
      }

      const chunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { 
          type: mediaRecorder.mimeType || 'video/webm' 
        });
        resolve(blob);
        setIsRecording(false);
        setMediaRecorder(null);
        
        // Stop all tracks
        if (mediaRecorder.stream) {
          mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
      };

      mediaRecorder.stop();
    });
  }, [mediaRecorder]);

  return {
    startRecording,
    stopRecording,
    isRecording,
    error,
  };
};