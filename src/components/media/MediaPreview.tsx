import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  IconButton,
  Slider,
  Typography,
  Stack,
  Paper,
  Tooltip
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import VolumeOffIcon from '@mui/icons-material/VolumeOff';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import DownloadIcon from '@mui/icons-material/Download';
import { SessionType } from '../../types/enums';

interface MediaPreviewProps {
  blob: Blob;
  sessionType: SessionType;
  onClose?: () => void;
}

const MediaPreview: React.FC<MediaPreviewProps> = ({
  blob,
  sessionType,
  onClose
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [mediaUrl, setMediaUrl] = useState<string>('');

  useEffect(() => {
    // Criar URL do blob
    const url = URL.createObjectURL(blob);
    setMediaUrl(url);

    // Cleanup
    return () => {
      URL.revokeObjectURL(url);
    };
  }, [blob]);

  const isVideoType = sessionType === SessionType.AUDIO_VIDEO || sessionType === SessionType.SCREEN_RECORDING;
  const mediaElement = isVideoType ? videoRef.current : audioRef.current;

  const handlePlayPause = () => {
    if (mediaElement) {
      if (isPlaying) {
        mediaElement.pause();
      } else {
        mediaElement.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (mediaElement) {
      setCurrentTime(mediaElement.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (mediaElement) {
      setDuration(mediaElement.duration);
    }
  };

  const handleSeek = (event: Event, newValue: number | number[]) => {
    const time = newValue as number;
    if (mediaElement) {
      mediaElement.currentTime = time;
      setCurrentTime(time);
    }
  };

  const handleVolumeChange = (event: Event, newValue: number | number[]) => {
    const vol = newValue as number;
    setVolume(vol);
    if (mediaElement) {
      mediaElement.volume = vol;
    }
    setIsMuted(vol === 0);
  };

  const handleMuteToggle = () => {
    if (mediaElement) {
      if (isMuted) {
        mediaElement.volume = volume;
        setIsMuted(false);
      } else {
        mediaElement.volume = 0;
        setIsMuted(true);
      }
    }
  };

  const handleFullscreen = () => {
    if (videoRef.current && videoRef.current.requestFullscreen) {
      videoRef.current.requestFullscreen();
    }
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = mediaUrl;
    link.download = `recording_${Date.now()}.${isVideoType ? 'webm' : 'wav'}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <Paper
      elevation={10}
      sx={{
        background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        borderRadius: 4,
        p: 3,
        maxWidth: isVideoType ? 800 : 400,
        mx: 'auto',
        boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
      }}
    >
      <Typography
        variant="h6"
        sx={{
          mb: 3,
          textAlign: 'center',
          fontWeight: 600,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}
      >
        Preview da Gravação
      </Typography>

      {/* Media Element */}
      <Box
        sx={{
          mb: 3,
          borderRadius: 3,
          overflow: 'hidden',
          backgroundColor: '#000',
          position: 'relative',
        }}
      >
        {isVideoType ? (
          <video
            ref={videoRef}
            src={mediaUrl}
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
            onEnded={() => setIsPlaying(false)}
            style={{
              width: '100%',
              height: 'auto',
              maxHeight: '400px',
              display: 'block',
            }}
          />
        ) : (
          <Box
            sx={
              {
                height: 120,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
              }
            }
          >
            <audio
              ref={audioRef}
              src={mediaUrl}
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
              onEnded={() => setIsPlaying(false)}
              style={{ display: 'none' }}
            />
            <VolumeUpIcon sx={{ fontSize: 48, color: '#94a3b8' }} />
          </Box>
        )}
      </Box>

      {/* Controls */}
      <Stack spacing={2}>
        {/* Progress Bar */}
        <Box>
          <Slider
            value={currentTime}
            max={duration}
            onChange={handleSeek}
            sx={{
              color: '#667eea',
              '& .MuiSlider-thumb': {
                backgroundColor: '#667eea',
                '&:hover': {
                  boxShadow: '0 0 0 8px rgba(102, 126, 234, 0.16)',
                },
              },
              '& .MuiSlider-track': {
                backgroundColor: '#667eea',
              },
              '& .MuiSlider-rail': {
                backgroundColor: 'rgba(102, 126, 234, 0.2)',
              },
            }}
          />
          <Stack direction="row" justifyContent="space-between">
            <Typography variant="caption" sx={{ color: '#64748b' }}>
              {formatTime(currentTime)}
            </Typography>
            <Typography variant="caption" sx={{ color: '#64748b' }}>
              {formatTime(duration)}
            </Typography>
          </Stack>
        </Box>

        {/* Control Buttons */}
        <Stack direction="row" spacing={1} alignItems="center" justifyContent="center">
          <Tooltip title={isPlaying ? 'Pausar' : 'Reproduzir'}>
            <IconButton
              onClick={handlePlayPause}
              sx={{
                backgroundColor: '#667eea',
                color: 'white',
                '&:hover': {
                  backgroundColor: '#5a67d8',
                  transform: 'scale(1.1)',
                },
                transition: 'all 0.2s ease',
              }}
            >
              {isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
            </IconButton>
          </Tooltip>

          <Tooltip title={isMuted ? 'Ativar som' : 'Silenciar'}>
            <IconButton onClick={handleMuteToggle} sx={{ color: '#64748b' }}>
              {isMuted ? <VolumeOffIcon /> : <VolumeUpIcon />}
            </IconButton>
          </Tooltip>

          <Box sx={{ width: 100, mx: 2 }}>
            <Slider
              value={isMuted ? 0 : volume}
              max={1}
              step={0.1}
              onChange={handleVolumeChange}
              size="small"
              sx={{
                color: '#667eea',
                '& .MuiSlider-thumb': {
                  backgroundColor: '#667eea',
                },
                '& .MuiSlider-track': {
                  backgroundColor: '#667eea',
                },
              }}
            />
          </Box>

          {isVideoType && (
            <Tooltip title="Tela cheia">
              <IconButton onClick={handleFullscreen} sx={{ color: '#64748b' }}>
                <FullscreenIcon />
              </IconButton>
            </Tooltip>
          )}

          <Tooltip title="Download">
            <IconButton onClick={handleDownload} sx={{ color: '#64748b' }}>
              <DownloadIcon />
            </IconButton>
          </Tooltip>
        </Stack>
      </Stack>
    </Paper>
  );
};

export default MediaPreview;