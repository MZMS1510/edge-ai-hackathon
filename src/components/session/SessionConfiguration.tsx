import React, { useState } from 'react';
import { Card, CardContent, Typography, TextField, Button, Stack, Box } from '@mui/material';
import IosShareOutlinedIcon from '@mui/icons-material/IosShareOutlined';

interface SessionConfigurationProps {
  onSessionTitleChange: (title: string) => void;
  onFileUpload: () => void;
}

const SessionConfiguration: React.FC<SessionConfigurationProps> = ({
  onSessionTitleChange,
  onFileUpload,
}) => {
  const [sessionTitle, setSessionTitle] = useState('');

  const handleTitleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setSessionTitle(value);
    onSessionTitleChange(value);
  };

  return (
    <Box
      sx={{
        p: 4,
        height: '100%',
        background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
        borderRadius: 2,
      }}
    >
      <Box>
        <Typography
          variant="h5"
          sx={{
            mb: 4,
            fontWeight: 700,
            color: '#1a202c',
            textAlign: 'center',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Configurações da Sessão
        </Typography>

        <Stack spacing={3}>
          <TextField
            fullWidth
            label="Título da Sessão"
            value={sessionTitle}
            onChange={handleTitleChange}
            variant="outlined"
            sx={{
              mb: 2,
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                borderRadius: 3,
                transition: 'all 0.3s ease',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 1)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 8px 25px rgba(0,0,0,0.1)',
                },
                '&.Mui-focused': {
                  backgroundColor: 'rgba(255, 255, 255, 1)',
                  boxShadow: '0 0 0 3px rgba(102, 126, 234, 0.2)',
                },
              },
              '& .MuiInputLabel-root': {
                color: '#64748b',
                fontWeight: 500,
              },
            }}
          />

          <Box>
            <Typography
              variant="body1"
              sx={{ 
                mb: 3, 
                color: '#475569',
                fontWeight: 500,
                textAlign: 'center'
              }}
            >
              Quer avaliar um evento passado?
            </Typography>
            
            <Button
              variant="contained"
              onClick={onFileUpload}
              startIcon={<IosShareOutlinedIcon />}
              fullWidth
              sx={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                px: 4,
                py: 2,
                fontWeight: 600,
                borderRadius: 3,
                fontSize: '1rem',
                textTransform: 'none',
                boxShadow: '0 8px 25px rgba(102, 126, 234, 0.3)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%)',
                  transform: 'translateY(-3px)',
                  boxShadow: '0 12px 35px rgba(102, 126, 234, 0.4)',
                },
              }}
            >
              FAÇA UM UPLOAD
            </Button>
          </Box>
        </Stack>
      </Box>
    </Box>
  );
};

export default SessionConfiguration;