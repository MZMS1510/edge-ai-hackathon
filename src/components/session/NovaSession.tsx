import React from 'react';
import { Box, Typography, Container, Grid, Paper, Fade } from '@mui/material';
import SessionConfiguration from './SessionConfiguration';
import RecordingInterface from './RecordingInterface';

interface NovaSessionProps {
  onStartRecording: () => void;
  onFileUpload: (file: File) => void;
  onSessionTitleChange: (title: string) => void;
}

const NovaSession: React.FC<NovaSessionProps> = ({
  onStartRecording,
  onFileUpload,
  onSessionTitleChange,
}) => {
  const handleFileUpload = () => {
    // This would typically open a file dialog
    console.log('File upload clicked');
  };

  return (
    <Box 
      sx={{ 
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        py: 4
      }}
    >
      <Container maxWidth="lg">
        {/* Header */}
        <Fade in timeout={800}>
          <Box sx={{ mb: 5, textAlign: 'center' }}>
            <Typography
              variant="h3"
              sx={{
                fontWeight: 800,
                color: 'white',
                mb: 1,
                textShadow: '0 2px 4px rgba(0,0,0,0.3)'
              }}
            >
              Nova Sessão
            </Typography>
            <Typography
              variant="h6"
              sx={{
                color: 'rgba(255,255,255,0.8)',
                fontWeight: 300
              }}
            >
              Configure e inicie sua sessão de terapia da fala
            </Typography>
          </Box>
        </Fade>

        <Grid container spacing={{ xs: 2, md: 4 }}>
          {/* Session Configuration */}
          <Grid item xs={12} md={6}>
            <Fade in timeout={1000}>
              <Paper 
                elevation={20} 
                sx={{ 
                  borderRadius: 4,
                  overflow: 'hidden',
                  height: '100%',
                  background: 'linear-gradient(145deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%)',
                  backdropFilter: 'blur(20px)',
                  border: '1px solid rgba(255,255,255,0.3)',
                  boxShadow: '0 25px 50px rgba(0,0,0,0.15), 0 0 0 1px rgba(255,255,255,0.1)',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    transform: 'translateY(-12px) scale(1.02)',
                    boxShadow: '0 35px 70px rgba(0,0,0,0.25), 0 0 0 1px rgba(255,255,255,0.2)'
                  }
                }}
              >
                <SessionConfiguration
                  onSessionTitleChange={onSessionTitleChange}
                  onFileUpload={handleFileUpload}
                />
              </Paper>
            </Fade>
          </Grid>
          
          {/* Recording Interface */}
          <Grid item xs={12} md={6}>
            <Fade in timeout={1200}>
              <Paper 
                elevation={20} 
                sx={{ 
                  borderRadius: 4,
                  overflow: 'hidden',
                  height: '100%',
                  background: 'linear-gradient(145deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%)',
                  backdropFilter: 'blur(20px)',
                  border: '1px solid rgba(255,255,255,0.3)',
                  boxShadow: '0 25px 50px rgba(0,0,0,0.15), 0 0 0 1px rgba(255,255,255,0.1)',
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    transform: 'translateY(-12px) scale(1.02)',
                    boxShadow: '0 35px 70px rgba(0,0,0,0.25), 0 0 0 1px rgba(255,255,255,0.2)'
                  }
                }}
              >
                <RecordingInterface
                  onStartRecording={onStartRecording}
                  onFileUpload={onFileUpload}
                />
              </Paper>
            </Fade>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default NovaSession;