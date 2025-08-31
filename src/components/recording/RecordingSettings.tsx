import React from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Slider,
  Typography,
  Paper,
  Divider,
  Stack
} from '@mui/material';
import {
  SettingsOutlined as SettingsIcon,
  HighQuality as QualityIcon,
  Timer as TimerIcon,
  VolumeUp as VolumeIcon
} from '@mui/icons-material';

interface RecordingSettingsProps {
  settings: {
    videoQuality: 'low' | 'medium' | 'high' | 'ultra';
    includeAudio: boolean;
    maxDuration: number;
    videoBitrate: number;
    audioBitrate: number;
  };
  onSettingsChange: (settings: any) => void;
  disabled?: boolean;
}

const RecordingSettings: React.FC<RecordingSettingsProps> = ({
  settings,
  onSettingsChange,
  disabled = false
}) => {
  const handleQualityChange = (quality: string) => {
    onSettingsChange({ ...settings, videoQuality: quality });
  };

  const handleAudioToggle = (includeAudio: boolean) => {
    onSettingsChange({ ...settings, includeAudio });
  };

  const handleMaxDurationChange = (duration: number) => {
    onSettingsChange({ ...settings, maxDuration: duration });
  };

  const handleVideoBitrateChange = (bitrate: number) => {
    onSettingsChange({ ...settings, videoBitrate: bitrate });
  };

  const handleAudioBitrateChange = (bitrate: number) => {
    onSettingsChange({ ...settings, audioBitrate: bitrate });
  };

  const getQualityDescription = (quality: string) => {
    switch (quality) {
      case 'low': return '640x480, 15fps';
      case 'medium': return '1280x720, 24fps';
      case 'high': return '1920x1080, 30fps';
      case 'ultra': return '2560x1440, 60fps';
      default: return '';
    }
  };

  const formatDuration = (seconds: number) => {
    if (seconds === 0) return 'Sem limite';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return minutes > 0 ? `${minutes}m ${remainingSeconds}s` : `${remainingSeconds}s`;
  };

  const formatBitrate = (bitrate: number) => {
    return bitrate >= 1000000 ? `${(bitrate / 1000000).toFixed(1)} Mbps` : `${(bitrate / 1000).toFixed(0)} kbps`;
  };

  return (
    <Paper
      elevation={8}
      sx={{
        p: 3,
        background: 'linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255,255,255,0.3)',
        borderRadius: 4,
        boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
      }}
    >
      <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
        <SettingsIcon sx={{ color: '#667eea', fontSize: 28 }} />
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
          Configurações de Gravação
        </Typography>
      </Stack>

      <Stack spacing={3}>
        {/* Qualidade de Vídeo */}
        <Box>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
            <QualityIcon sx={{ color: '#667eea', fontSize: 20 }} />
            <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#374151' }}>
              Qualidade de Vídeo
            </Typography>
          </Stack>
          <FormControl fullWidth disabled={disabled}>
            <Select
              value={settings.videoQuality}
              onChange={(e) => handleQualityChange(e.target.value)}
              sx={{
                borderRadius: 2,
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(102, 126, 234, 0.3)',
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: 'rgba(102, 126, 234, 0.5)',
                },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#667eea',
                },
              }}
            >
              <MenuItem value="low">Baixa - {getQualityDescription('low')}</MenuItem>
              <MenuItem value="medium">Média - {getQualityDescription('medium')}</MenuItem>
              <MenuItem value="high">Alta - {getQualityDescription('high')}</MenuItem>
              <MenuItem value="ultra">Ultra - {getQualityDescription('ultra')}</MenuItem>
            </Select>
          </FormControl>
        </Box>

        <Divider sx={{ opacity: 0.3 }} />

        {/* Áudio */}
        <Box>
          <FormControlLabel
            control={
              <Switch
                checked={settings.includeAudio}
                onChange={(e) => handleAudioToggle(e.target.checked)}
                disabled={disabled}
                sx={{
                  '& .MuiSwitch-switchBase.Mui-checked': {
                    color: '#667eea',
                  },
                  '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                    backgroundColor: '#667eea',
                  },
                }}
              />
            }
            label={
              <Typography sx={{ fontWeight: 600, color: '#374151' }}>
                Incluir Áudio
              </Typography>
            }
          />
        </Box>

        <Divider sx={{ opacity: 0.3 }} />

        {/* Duração Máxima */}
        <Box>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
            <TimerIcon sx={{ color: '#667eea', fontSize: 20 }} />
            <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#374151' }}>
              Duração Máxima: {formatDuration(settings.maxDuration)}
            </Typography>
          </Stack>
          <Slider
            value={settings.maxDuration}
            onChange={(_, value) => handleMaxDurationChange(value as number)}
            min={0}
            max={1800} // 30 minutos
            step={30}
            disabled={disabled}
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
        </Box>

        <Divider sx={{ opacity: 0.3 }} />

        {/* Bitrate de Vídeo */}
        <Box>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#374151', mb: 2 }}>
            Bitrate de Vídeo: {formatBitrate(settings.videoBitrate)}
          </Typography>
          <Slider
            value={settings.videoBitrate}
            onChange={(_, value) => handleVideoBitrateChange(value as number)}
            min={500000} // 500 kbps
            max={10000000} // 10 Mbps
            step={250000}
            disabled={disabled}
            sx={{
              color: '#667eea',
              '& .MuiSlider-thumb': {
                backgroundColor: '#667eea',
              },
              '& .MuiSlider-track': {
                backgroundColor: '#667eea',
              },
              '& .MuiSlider-rail': {
                backgroundColor: 'rgba(102, 126, 234, 0.2)',
              },
            }}
          />
        </Box>

        {/* Bitrate de Áudio */}
        {settings.includeAudio && (
          <Box>
            <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2 }}>
              <VolumeIcon sx={{ color: '#667eea', fontSize: 20 }} />
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#374151' }}>
                Bitrate de Áudio: {formatBitrate(settings.audioBitrate)}
              </Typography>
            </Stack>
            <Slider
              value={settings.audioBitrate}
              onChange={(_, value) => handleAudioBitrateChange(value as number)}
              min={64000} // 64 kbps
              max={320000} // 320 kbps
              step={32000}
              disabled={disabled}
              sx={{
                color: '#667eea',
                '& .MuiSlider-thumb': {
                  backgroundColor: '#667eea',
                },
                '& .MuiSlider-track': {
                  backgroundColor: '#667eea',
                },
                '& .MuiSlider-rail': {
                  backgroundColor: 'rgba(102, 126, 234, 0.2)',
                },
              }}
            />
          </Box>
        )}
      </Stack>
    </Paper>
  );
};

export default RecordingSettings;