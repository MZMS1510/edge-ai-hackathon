import { useState, useRef, useCallback } from 'react';

interface RecordingOptions {
  includeAudio?: boolean;
  videoQuality?: 'low' | 'medium' | 'high' | 'ultra';
  maxDuration?: number; // em segundos
  audioBitrate?: number;
  videoBitrate?: number;
}

interface RecordingState {
  isRecording: boolean;
  isPaused: boolean;
  duration: number;
  recordedBlob: Blob | null;
  error: string | null;
}

interface UseScreenRecorderReturn {
  state: RecordingState;
  startRecording: (options?: Partial<RecordingOptions>) => Promise<void>;
  stopRecording: () => void;
  pauseRecording: () => void;
  resumeRecording: () => void;
  clearRecording: () => void;
}

const useScreenRecorder = (): UseScreenRecorderReturn => {
  const [state, setState] = useState<RecordingState>({
    isRecording: false,
    isPaused: false,
    duration: 0,
    recordedBlob: null,
    error: null
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number>(0);
  const pausedTimeRef = useRef<number>(0);
  const maxDurationTimerRef = useRef<NodeJS.Timeout | null>(null);

  const getVideoConstraints = (quality: 'low' | 'medium' | 'high' | 'ultra') => {
    switch (quality) {
      case 'low':
        return { width: 640, height: 480, frameRate: 15 };
      case 'medium':
        return { width: 1280, height: 720, frameRate: 24 };
      case 'high':
        return { width: 1920, height: 1080, frameRate: 30 };
      case 'ultra':
        return { width: 2560, height: 1440, frameRate: 60 };
      default:
        return { width: 1280, height: 720, frameRate: 24 };
    }
  };

  const getRecorderOptions = (options: RecordingOptions) => {
    const mimeType = 'video/webm;codecs=vp9,opus';
    const recorderOptions: MediaRecorderOptions = { mimeType };
    
    if (options.videoBitrate || options.audioBitrate) {
      recorderOptions.videoBitsPerSecond = options.videoBitrate || 2500000; // 2.5 Mbps default
      recorderOptions.audioBitsPerSecond = options.audioBitrate || 128000; // 128 kbps default
    }
    
    return recorderOptions;
  };

  const startTimer = useCallback(() => {
    startTimeRef.current = Date.now() - pausedTimeRef.current;
    timerRef.current = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTimeRef.current) / 1000);
      setState(prev => ({ ...prev, duration: elapsed }));
    }, 1000);
  }, []);

  const stopTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const startRecording = useCallback(async (options: Partial<RecordingOptions> = {}) => {
    try {
      setState(prev => ({ ...prev, error: null }));

      const defaultOptions: RecordingOptions = {
        includeAudio: true,
        videoQuality: 'medium',
        maxDuration: 300, // 5 minutos por padrão
        ...options
      };

      // Solicitar permissão para capturar a tela
      const displayStream = await navigator.mediaDevices.getDisplayMedia({
        video: getVideoConstraints(defaultOptions.videoQuality || 'medium'),
        audio: false // Áudio da tela será capturado separadamente se necessário
      });

      let combinedStream = displayStream;

      // Se incluir áudio, capturar áudio do microfone
      if (defaultOptions.includeAudio) {
        try {
          const audioStream = await navigator.mediaDevices.getUserMedia({
            audio: {
              echoCancellation: true,
              noiseSuppression: true,
              autoGainControl: true
            },
            video: false
          });

          // Combinar streams de vídeo e áudio
          const audioTrack = audioStream.getAudioTracks()[0];
          if (audioTrack) {
            combinedStream.addTrack(audioTrack);
          }
        } catch (audioError) {
          console.warn('Não foi possível capturar áudio:', audioError);
          // Continuar apenas com vídeo
        }
      }

      streamRef.current = combinedStream;
      chunksRef.current = [];

      // Configurar MediaRecorder
      const recorderOptions = getRecorderOptions(defaultOptions);
      const mediaRecorder = new MediaRecorder(combinedStream, recorderOptions);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' });
        setState(prev => ({
          ...prev,
          recordedBlob: blob,
          isRecording: false,
          isPaused: false
        }));
        stopTimer();
      };

      mediaRecorder.onerror = (event) => {
        console.error('Erro na gravação:', event);
        setState(prev => ({
          ...prev,
          error: 'Erro durante a gravação',
          isRecording: false,
          isPaused: false
        }));
        stopTimer();
      };

      // Detectar quando o usuário para o compartilhamento de tela
      combinedStream.getVideoTracks()[0].onended = () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          mediaRecorderRef.current.stop();
        }
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(1000); // Capturar dados a cada segundo

      setState(prev => ({
        ...prev,
        isRecording: true,
        isPaused: false,
        duration: 0,
        recordedBlob: null
      }));

      pausedTimeRef.current = 0;
      startTimer();

      // Auto-stop após duração máxima
      if (defaultOptions.maxDuration) {
        setTimeout(() => {
          if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
            stopRecording();
          }
        }, defaultOptions.maxDuration * 1000);
      }

    } catch (error) {
      console.error('Erro ao iniciar gravação:', error);
      setState(prev => ({
        ...prev,
        error: 'Erro ao acessar tela ou microfone. Verifique as permissões.',
        isRecording: false
      }));
    }
  }, [startTimer, stopTimer]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    stopTimer();
  }, [stopTimer]);

  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.pause();
      setState(prev => ({ ...prev, isPaused: true }));
      stopTimer();
      pausedTimeRef.current = Date.now() - startTimeRef.current;
    }
  }, [stopTimer]);

  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
      mediaRecorderRef.current.resume();
      setState(prev => ({ ...prev, isPaused: false }));
      startTimer();
    }
  }, [startTimer]);

  const clearRecording = useCallback(() => {
    setState(prev => ({
      ...prev,
      recordedBlob: null,
      duration: 0,
      error: null
    }));
    chunksRef.current = [];
    pausedTimeRef.current = 0;
  }, []);

  return {
    state,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    clearRecording
  };
};

export default useScreenRecorder;
export type { RecordingOptions, RecordingState, UseScreenRecorderReturn };