import React from 'react';
import { Card, CardContent, Typography, Button, Stack, Box, Paper } from '@mui/material';
import MicOutlinedIcon from '@mui/icons-material/MicOutlined';
import VideocamOutlinedIcon from '@mui/icons-material/VideocamOutlined';
import IosShareOutlinedIcon from '@mui/icons-material/IosShareOutlined';
import { SessionType } from '../../types/enums';

interface RecordingInterfaceProps {
  onStartRecording: (type: SessionType) => void;
  onFileUpload: (file: File) => void;
}

const RecordingInterface: React.FC<RecordingInterfaceProps> = ({
  onStartRecording,
  onFileUpload,
}) => {
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onFileUpload(file);
    }
  };

  return (
    <Card
      sx={{
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
      }}
    >
      <CardContent sx={{ p: 4 }}>
        <Stack direction="row" spacing={4} sx={{ height: '300px' }}>
          {/* Recording Section */}
          <Box sx={{ flex: 1 }}>
            <Typography
              variant="h6"
              sx={{
                mb: 3,
                fontWeight: 600,
                color: 'text.primary',
              }}
            >
              Grave agora mesmo:
            </Typography>

            <Stack direction="row" spacing={3} sx={{ mb: 4 }}>
              <Box sx={{ textAlign: 'center' }}>
                <Box
                  sx={{
                    width: 80,
                    height: 80,
                    borderRadius: '50%',
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mb: 2,
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    '&:hover': {
                      transform: 'scale(1.05)',
                      backgroundColor: 'rgba(255, 255, 255, 1)',
                    },
                  }}
                >
                  <MicOutlinedIcon sx={{ fontSize: 32, color: 'text.primary' }} />
                </Box>
              </Box>

              <Box sx={{ textAlign: 'center' }}>
                <Box
                  sx={{
                    width: 80,
                    height: 80,
                    borderRadius: '50%',
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mb: 2,
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    '&:hover': {
                      transform: 'scale(1.05)',
                      backgroundColor: 'rgba(255, 255, 255, 1)',
                    },
                  }}
                >
                  <VideocamOutlinedIcon sx={{ fontSize: 32, color: 'text.primary' }} />
                </Box>
              </Box>
            </Stack>

            <Stack direction="row" spacing={2}>
              <Button
                variant="contained"
                onClick={() => onStartRecording(SessionType.AUDIO_ONLY)}
                sx={{
                  backgroundColor: 'secondary.main',
                  color: 'white',
                  px: 3,
                  py: 1.5,
                  fontWeight: 600,
                  borderRadius: 2,
                  '&:hover': {
                    backgroundColor: 'secondary.dark',
                  },
                }}
              >
                APENAS ÁUDIO
              </Button>
              
              <Button
                variant="contained"
                onClick={() => onStartRecording(SessionType.AUDIO_VIDEO)}
                sx={{
                  backgroundColor: 'secondary.main',
                  color: 'white',
                  px: 3,
                  py: 1.5,
                  fontWeight: 600,
                  borderRadius: 2,
                  '&:hover': {
                    backgroundColor: 'secondary.dark',
                  },
                }}
              >
                ÁUDIO E VÍDEO
              </Button>
            </Stack>
          </Box>

          {/* Upload Section */}
          <Box sx={{ flex: 1 }}>
            <Typography
              variant="h6"
              sx={{
                mb: 3,
                fontWeight: 600,
                color: 'text.primary',
              }}
            >
              Faça um upload de um arquivo de áudio ou vídeo:
            </Typography>

            <Paper
              component="label"
              sx={{
                height: 200,
                border: '2px dashed',
                borderColor: 'grey.300',
                borderRadius: 2,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                backgroundColor: 'rgba(255, 255, 255, 0.5)',
                transition: 'all 0.2s',
                '&:hover': {
                  borderColor: 'primary.main',
                  backgroundColor: 'rgba(255, 255, 255, 0.8)',
                },
              }}
            >
              <input
                type="file"
                accept="audio/*,video/*"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
              
              <IosShareOutlinedIcon
                sx={{
                  fontSize: 48,
                  color: 'grey.400',
                  mb: 2,
                }}
              />
              
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ textAlign: 'center', maxWidth: 200 }}
              >
                Clique aqui ou arraste um arquivo para fazer upload
              </Typography>
            </Paper>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
};

export default RecordingInterface;