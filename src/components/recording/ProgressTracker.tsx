import React from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Paper,
  Stack,
  Chip,
  Divider
} from '@mui/material';
import {
  AccessTime as TimeIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  SignalCellularAlt as QualityIcon
} from '@mui/icons-material';

interface ProgressTrackerProps {
  // Recording progress
  isRecording: boolean;
  isPaused: boolean;
  duration: number;
  maxDuration?: number;
  
  // Upload progress
  isUploading: boolean;
  uploadProgress?: {
    percentage: number;
    loaded: number;
    total: number;
    speed?: number; // bytes per second
  };
  
  // Recording settings
  videoQuality: string;
  includeAudio: boolean;
  estimatedFileSize?: number;
}

const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  isRecording,
  isPaused,
  duration,
  maxDuration,
  isUploading,
  uploadProgress,
  videoQuality,
  includeAudio,
  estimatedFileSize
}) => {
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatSpeed = (bytesPerSecond: number) => {
    return formatFileSize(bytesPerSecond) + '/s';
  };

  const getRecordingProgress = () => {
    if (!maxDuration || maxDuration === 0) return 0;
    return Math.min((duration / maxDuration) * 100, 100);
  };

  const getStatusColor = () => {
    if (isUploading) return '#f59e0b'; // amber
    if (isRecording && !isPaused) return '#ef4444'; // red
    if (isPaused) return '#f59e0b'; // amber
    return '#10b981'; // green
  };

  const getStatusText = () => {
    if (isUploading) return 'Enviando';
    if (isRecording && !isPaused) return 'Gravando';
    if (isPaused) return 'Pausado';
    return 'Pronto';
  };

  return (
    <Paper
      elevation={6}
      sx={{
        p: 3,
        background: 'linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.8) 100%)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255,255,255,0.3)',
        borderRadius: 3,
        boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
      }}
    >
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography
          variant="h6"
          sx={{
            fontWeight: 700,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Status da Sessão
        </Typography>
        
        <Chip
          label={getStatusText()}
          sx={{
            backgroundColor: getStatusColor(),
            color: 'white',
            fontWeight: 600,
            fontSize: '0.75rem',
            '& .MuiChip-label': {
              px: 2,
            },
          }}
        />
      </Stack>

      <Stack spacing={3}>
        {/* Recording Progress */}
        {(isRecording || isPaused || duration > 0) && (
          <Box>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
              <TimeIcon sx={{ color: '#667eea', fontSize: 20 }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#374151' }}>
                Tempo de Gravação: {formatTime(duration)}
                {maxDuration && maxDuration > 0 && ` / ${formatTime(maxDuration)}`}
              </Typography>
            </Stack>
            
            {maxDuration && maxDuration > 0 && (
              <LinearProgress
                variant="determinate"
                value={getRecordingProgress()}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: 'rgba(102, 126, 234, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    background: isRecording && !isPaused 
                      ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'
                      : 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                    borderRadius: 4,
                  },
                }}
              />
            )}
          </Box>
        )}

        {/* Upload Progress */}
        {isUploading && uploadProgress && (
          <Box>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
              <StorageIcon sx={{ color: '#667eea', fontSize: 20 }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#374151' }}>
                Upload: {uploadProgress.percentage}%
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
            
            <Stack direction="row" justifyContent="space-between" sx={{ mt: 1 }}>
              <Typography variant="caption" sx={{ color: '#64748b' }}>
                {formatFileSize(uploadProgress.loaded)} / {formatFileSize(uploadProgress.total)}
              </Typography>
              {uploadProgress.speed && (
                <Typography variant="caption" sx={{ color: '#64748b' }}>
                  {formatSpeed(uploadProgress.speed)}
                </Typography>
              )}
            </Stack>
          </Box>
        )}

        <Divider sx={{ opacity: 0.3 }} />

        {/* Recording Info */}
        <Stack spacing={2}>
          <Stack direction="row" alignItems="center" spacing={1}>
            <QualityIcon sx={{ color: '#667eea', fontSize: 20 }} />
            <Typography variant="body2" sx={{ color: '#374151' }}>
              <strong>Qualidade:</strong> {videoQuality.charAt(0).toUpperCase() + videoQuality.slice(1)}
            </Typography>
          </Stack>
          
          <Stack direction="row" alignItems="center" spacing={1}>
            <SpeedIcon sx={{ color: '#667eea', fontSize: 20 }} />
            <Typography variant="body2" sx={{ color: '#374151' }}>
              <strong>Áudio:</strong> {includeAudio ? 'Incluído' : 'Desabilitado'}
            </Typography>
          </Stack>
          
          {estimatedFileSize && (
            <Stack direction="row" alignItems="center" spacing={1}>
              <StorageIcon sx={{ color: '#667eea', fontSize: 20 }} />
              <Typography variant="body2" sx={{ color: '#374151' }}>
                <strong>Tamanho Estimado:</strong> {formatFileSize(estimatedFileSize)}
              </Typography>
            </Stack>
          )}
        </Stack>
      </Stack>
    </Paper>
  );
};

export default ProgressTracker;