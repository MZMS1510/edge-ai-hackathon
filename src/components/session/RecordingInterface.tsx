import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Button, Stack, Box, Paper, LinearProgress, Chip } from '@mui/material';
import MicOutlinedIcon from '@mui/icons-material/MicOutlined';
import VideocamOutlinedIcon from '@mui/icons-material/VideocamOutlined';
import ScreenShareIcon from '@mui/icons-material/ScreenShare';
import StopIcon from '@mui/icons-material/Stop';
import PauseIcon from '@mui/icons-material/Pause';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SettingsIcon from '@mui/icons-material/SettingsOutlined';
import IosShareOutlinedIcon from '@mui/icons-material/IosShareOutlined';
import { SessionType } from '../../types/enums';
import useScreenRecorder from '../../hooks/useScreenRecorder';
import { useUpload } from '../../hooks/useUpload';
import MediaPreview from '../media/MediaPreview';
import RecordingSettings from '../recording/RecordingSettings';
import ProgressTracker from '../recording/ProgressTracker';

interface RecordingInterfaceProps {
  onStartRecording: (type: SessionType) => void;
  onFileUpload: (file: File) => void;
  onRecordingComplete?: (blob: Blob, type: SessionType) => void;
}

const RecordingInterface: React.FC<RecordingInterfaceProps> = ({
  onStartRecording,
  onFileUpload,
  onRecordingComplete,
}) => {
  const {
    isRecording,
    isPaused,
    duration,
    recordedBlob,
    error,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    clearRecording
  } = useScreenRecorder();

  const {
    uploadFile,
    isUploading,
    progress: uploadProgress,
    error: uploadError,
    success: uploadSuccess,
    resetUpload
  } = useUpload();

  const [currentRecordingType, setCurrentRecordingType] = useState<SessionType | null>(null);
  const [showUploadStatus, setShowUploadStatus] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [recordingSettings, setRecordingSettings] = useState({
    videoQuality: 'medium' as 'low' | 'medium' | 'high' | 'ultra',
    includeAudio: true,
    maxDuration: 300, // 5 minutos
    videoBitrate: 2500000, // 2.5 Mbps
    audioBitrate: 128000, // 128 kbps
  });

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onFileUpload(file);
    }
  };

  const handleStartScreenRecording = async () => {
    try {
      setCurrentRecordingType(SessionType.SCREEN_RECORDING);
      await startRecording({
        includeAudio: recordingSettings.includeAudio,
        videoQuality: recordingSettings.videoQuality,
        maxDuration: recordingSettings.maxDuration > 0 ? recordingSettings.maxDuration : undefined,
        videoBitrate: recordingSettings.videoBitrate,
        audioBitrate: recordingSettings.audioBitrate,
      });
      onStartRecording(SessionType.SCREEN_RECORDING);
    } catch (err) {
      console.error('Erro ao iniciar gravação de tela:', err);
      setCurrentRecordingType(null);
    }
  };

  const handleStopRecording = () => {
    stopRecording();
    setCurrentRecordingType(null);
  };

  const handlePauseResume = () => {
    if (isPaused) {
      resumeRecording();
    } else {
      pauseRecording();
    }
  };

  useEffect(() => {
    if (recordedBlob && currentRecordingType) {
      // Chamar callback se fornecido
      if (onRecordingComplete) {
        onRecordingComplete(recordedBlob, currentRecordingType);
      }
      
      // Mostrar preview primeiro
      setShowPreview(true);
    }
  }, [recordedBlob, currentRecordingType, onRecordingComplete]);

  const handleUpload = async (blob: Blob, sessionType: SessionType) => {
    setShowUploadStatus(true);
    try {
      const response = await uploadFile(blob, sessionType);
      if (response.success) {
        console.log('Upload realizado com sucesso:', response);
      } else {
        console.error('Erro no upload:', response.error);
      }
    } catch (error) {
      console.error('Erro durante o upload:', error);
    }
  };

  const handleStartUpload = async () => {
    if (recordedBlob && currentRecordingType) {
      setShowPreview(false);
      await handleUpload(recordedBlob, currentRecordingType);
    }
  };

  const handleClosePreview = () => {
    setShowPreview(false);
    clearRecording();
    setCurrentRecordingType(null);
  };

  const handleCloseUploadStatus = () => {
    setShowUploadStatus(false);
    resetUpload();
    clearRecording();
    setCurrentRecordingType(null);
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Stack spacing={3}>

      {/* Recording Section */}
      <Box
        sx={{
          p: 4,
          height: '100%',
          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
          borderRadius: 2,
        }}
      >
        <Box>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 4 }}>
            <Typography
              variant="h5"
              sx={{
                fontWeight: 700,
                color: '#1a202c',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Grave agora mesmo:
            </Typography>
            
            <Button
              variant="outlined"
              onClick={() => setShowSettings(!showSettings)}
              startIcon={<SettingsIcon />}
              sx={{
                borderColor: '#667eea',
                color: '#667eea',
                px: 3,
                py: 1,
                fontWeight: 600,
                borderRadius: 3,
                fontSize: '0.875rem',
                textTransform: 'none',
                '&:hover': {
                  borderColor: '#5a67d8',
                  backgroundColor: 'rgba(102, 126, 234, 0.05)',
                },
              }}
            >
              {showSettings ? 'Ocultar' : 'Configurações'}
            </Button>
          </Stack>

          {/* Large Recording Area */}
          <Box
            sx={{
              background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
              borderRadius: 4,
              p: 6,
              mb: 4,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: 200,
              border: '2px solid rgba(255,255,255,0.1)',
              boxShadow: 'inset 0 2px 10px rgba(0,0,0,0.2), 0 8px 25px rgba(0,0,0,0.1)',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'scale(1.02)',
                boxShadow: 'inset 0 2px 10px rgba(0,0,0,0.3), 0 12px 35px rgba(0,0,0,0.15)',
              },
            }}
          >
            <VideocamOutlinedIcon 
              sx={{ 
                fontSize: 80, 
                color: '#94a3b8',
                filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.3))',
              }} 
            />
          </Box>

          {/* Status da Gravação */}
          {isRecording && (
            <Box sx={{ mb: 3 }}>
              <Stack direction="row" spacing={2} alignItems="center" justifyContent="center" sx={{ mb: 2 }}>
                <Chip
                  label={isPaused ? 'PAUSADO' : 'GRAVANDO'}
                  color={isPaused ? 'warning' : 'error'}
                  sx={{
                    fontWeight: 600,
                    fontSize: '0.875rem',
                    animation: isPaused ? 'none' : 'pulse 1.5s infinite',
                    '@keyframes pulse': {
                      '0%': { opacity: 1 },
                      '50%': { opacity: 0.7 },
                      '100%': { opacity: 1 },
                    },
                  }}
                />
                <Typography variant="h6" sx={{ color: '#1a202c', fontWeight: 600 }}>
                  {formatDuration(duration)}
                </Typography>
              </Stack>
              <LinearProgress
                variant="indeterminate"
                sx={{
                  height: 6,
                  borderRadius: 3,
                  backgroundColor: 'rgba(102, 126, 234, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  },
                }}
              />
            </Box>
          )}

          {/* Controles de Gravação */}
          {isRecording ? (
            <Stack direction="row" spacing={3} justifyContent="center">
              <Button
                variant="contained"
                onClick={handlePauseResume}
                startIcon={isPaused ? <PlayArrowIcon /> : <PauseIcon />}
                sx={{
                  background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                  color: 'white',
                  px: 4,
                  py: 1.5,
                  fontWeight: 600,
                  borderRadius: 3,
                  fontSize: '0.875rem',
                  textTransform: 'none',
                  boxShadow: '0 4px 15px rgba(245, 158, 11, 0.3)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #d97706 0%, #b45309 100%)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 25px rgba(245, 158, 11, 0.4)',
                  },
                }}
              >
                {isPaused ? 'Continuar' : 'Pausar'}
              </Button>
              <Button
                variant="contained"
                onClick={handleStopRecording}
                startIcon={<StopIcon />}
                sx={{
                  background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                  color: 'white',
                  px: 4,
                  py: 1.5,
                  fontWeight: 600,
                  borderRadius: 3,
                  fontSize: '0.875rem',
                  textTransform: 'none',
                  boxShadow: '0 4px 15px rgba(239, 68, 68, 0.3)',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 25px rgba(239, 68, 68, 0.4)',
                  },
                }}
              >
                Parar Gravação
              </Button>
            </Stack>
          ) : (
            /* Recording Buttons */
            <Stack direction="row" spacing={4} justifyContent="center">
              <Box sx={{ textAlign: 'center' }}>
                <Box
                  onClick={() => onStartRecording(SessionType.AUDIO_ONLY)}
                  sx={{
                    width: 90,
                    height: 90,
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mb: 3,
                    cursor: 'pointer',
                    boxShadow: '0 8px 25px rgba(102, 126, 234, 0.3)',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      transform: 'translateY(-5px) scale(1.05)',
                      boxShadow: '0 15px 40px rgba(102, 126, 234, 0.4)',
                    },
                  }}
                >
                  <MicOutlinedIcon sx={{ fontSize: 36, color: 'white', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))' }} />
                </Box>
                <Button
                  variant="contained"
                  onClick={() => onStartRecording(SessionType.AUDIO_ONLY)}
                  sx={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    px: 4,
                    py: 1.5,
                    fontWeight: 600,
                    borderRadius: 3,
                    fontSize: '0.875rem',
                    textTransform: 'none',
                    boxShadow: '0 4px 15px rgba(102, 126, 234, 0.3)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 25px rgba(102, 126, 234, 0.4)',
                    },
                  }}
                >
                  Iniciar Áudio
                </Button>
              </Box>
                
              <Box sx={{ textAlign: 'center' }}>
                <Box
                  onClick={() => onStartRecording(SessionType.AUDIO_VIDEO)}
                  sx={{
                    width: 90,
                    height: 90,
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mb: 3,
                    cursor: 'pointer',
                    boxShadow: '0 8px 25px rgba(102, 126, 234, 0.3)',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      transform: 'translateY(-5px) scale(1.05)',
                      boxShadow: '0 15px 40px rgba(102, 126, 234, 0.4)',
                    },
                  }}
                >
                  <VideocamOutlinedIcon sx={{ fontSize: 36, color: 'white', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))' }} />
                </Box>
                <Button
                  variant="contained"
                  onClick={() => onStartRecording(SessionType.AUDIO_VIDEO)}
                  sx={{
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    px: 4,
                    py: 1.5,
                    fontWeight: 600,
                    borderRadius: 3,
                    fontSize: '0.875rem',
                    textTransform: 'none',
                    boxShadow: '0 4px 15px rgba(102, 126, 234, 0.3)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 25px rgba(102, 126, 234, 0.4)',
                    },
                  }}
                >
                  Iniciar Vídeo
                </Button>
              </Box>

              <Box sx={{ textAlign: 'center' }}>
                <Box
                  onClick={handleStartScreenRecording}
                  sx={{
                    width: 90,
                    height: 90,
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mb: 3,
                    cursor: 'pointer',
                    boxShadow: '0 8px 25px rgba(16, 185, 129, 0.3)',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    '&:hover': {
                      transform: 'translateY(-5px) scale(1.05)',
                      boxShadow: '0 15px 40px rgba(16, 185, 129, 0.4)',
                    },
                  }}
                >
                  <ScreenShareIcon sx={{ fontSize: 36, color: 'white', filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))' }} />
                </Box>
                <Button
                  variant="contained"
                  onClick={handleStartScreenRecording}
                  sx={{
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    color: 'white',
                    px: 4,
                    py: 1.5,
                    fontWeight: 600,
                    borderRadius: 3,
                    fontSize: '0.875rem',
                    textTransform: 'none',
                    boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 25px rgba(16, 185, 129, 0.4)',
                    },
                  }}
                >
                  Gravar Tela
                </Button>
              </Box>
            </Stack>
          )}

          {/* Preview da Gravação */}
          {showPreview && recordedBlob && currentRecordingType && (
            <Box sx={{ mt: 3 }}>
              <MediaPreview
                blob={recordedBlob}
                sessionType={currentRecordingType}
                onClose={handleClosePreview}
              />
              
              <Stack direction="row" spacing={2} justifyContent="center" sx={{ mt: 3 }}>
                <Button
                  variant="outlined"
                  onClick={handleClosePreview}
                  sx={{
                    borderColor: '#64748b',
                    color: '#64748b',
                    px: 4,
                    py: 1.5,
                    fontWeight: 600,
                    borderRadius: 3,
                    fontSize: '0.875rem',
                    textTransform: 'none',
                    '&:hover': {
                      borderColor: '#475569',
                      backgroundColor: 'rgba(100, 116, 139, 0.05)',
                    },
                  }}
                >
                  Descartar
                </Button>
                <Button
                  variant="contained"
                  onClick={handleStartUpload}
                  sx={{
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    color: 'white',
                    px: 4,
                    py: 1.5,
                    fontWeight: 600,
                    borderRadius: 3,
                    fontSize: '0.875rem',
                    textTransform: 'none',
                    boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                      transform: 'translateY(-2px)',
                      boxShadow: '0 8px 25px rgba(16, 185, 129, 0.4)',
                    },
                  }}
                >
                  Enviar para Análise
                </Button>
              </Stack>
            </Box>
          )}

          {/* Status de Upload */}
          {showUploadStatus && (
            <Box sx={{ mt: 3 }}>
              <Typography
                variant="h6"
                sx={{
                  mb: 2,
                  textAlign: 'center',
                  color: '#1a202c',
                  fontWeight: 600
                }}
              >
                {isUploading ? 'Enviando gravação...' : uploadSuccess ? 'Upload concluído!' : 'Erro no upload'}
              </Typography>
              
              {isUploading && uploadProgress && (
                <Box sx={{ mb: 2 }}>
                  <Stack direction="row" spacing={2} alignItems="center" justifyContent="center" sx={{ mb: 1 }}>
                    <Typography variant="body2" sx={{ color: '#64748b' }}>
                      {uploadProgress.percentage}%
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#64748b' }}>
                      {Math.round(uploadProgress.loaded / 1024)} KB / {Math.round(uploadProgress.total / 1024)} KB
                    </Typography>
                  </Stack>
                  <LinearProgress
                    variant="determinate"
                    value={uploadProgress.percentage}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: 'rgba(102, 126, 234, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                        borderRadius: 4,
                      },
                    }}
                  />
                </Box>
              )}
              
              {uploadSuccess && (
                <Box sx={{ textAlign: 'center', mb: 2 }}>
                  <Typography variant="body2" sx={{ color: '#10b981', fontWeight: 500 }}>
                    ✅ Gravação enviada com sucesso para análise!
                  </Typography>
                </Box>
              )}
              
              {uploadError && (
                <Box sx={{ textAlign: 'center', mb: 2 }}>
                  <Typography variant="body2" sx={{ color: '#ef4444', fontWeight: 500 }}>
                    ❌ {uploadError}
                  </Typography>
                </Box>
              )}
              
              {(uploadSuccess || uploadError) && (
                <Box sx={{ textAlign: 'center' }}>
                  <Button
                    variant="outlined"
                    onClick={handleCloseUploadStatus}
                    sx={{
                      borderColor: '#667eea',
                      color: '#667eea',
                      px: 3,
                      py: 1,
                      fontWeight: 600,
                      borderRadius: 3,
                      fontSize: '0.875rem',
                      textTransform: 'none',
                      '&:hover': {
                        borderColor: '#5a67d8',
                        backgroundColor: 'rgba(102, 126, 234, 0.05)',
                      },
                    }}
                  >
                    Nova Gravação
                  </Button>
                </Box>
              )}
            </Box>
          )}

          {/* Configurações de Gravação */}
            {showSettings && (
              <Box sx={{ mt: 3 }}>
                <RecordingSettings
                  settings={recordingSettings}
                  onSettingsChange={setRecordingSettings}
                  disabled={isRecording || isPaused}
                />
              </Box>
            )}

            {/* Progress Tracker */}
            {(isRecording || isPaused || duration > 0 || isUploading) && (
              <Box sx={{ mt: 3 }}>
                <ProgressTracker
                  isRecording={isRecording}
                  isPaused={isPaused}
                  duration={duration}
                  maxDuration={recordingSettings.maxDuration > 0 ? recordingSettings.maxDuration : undefined}
                  isUploading={isUploading}
                  uploadProgress={uploadProgress}
                  videoQuality={recordingSettings.videoQuality}
                  includeAudio={recordingSettings.includeAudio}
                  estimatedFileSize={recordedBlob ? recordedBlob.size : undefined}
                />
              </Box>
            )}

          {/* Mensagem de Erro */}
          {error && (
            <Box sx={{ mt: 3, textAlign: 'center' }}>
              <Typography variant="body2" sx={{ color: '#ef4444', fontWeight: 500 }}>
                Erro: {error}
              </Typography>
            </Box>
          )}
        </Box>
      </Box>
    </Stack>
  );
};

export default RecordingInterface;