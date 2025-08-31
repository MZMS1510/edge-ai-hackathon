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
    <Card
      sx={{
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        mb: 3,
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Typography
          variant="h6"
          sx={{
            mb: 3,
            fontWeight: 600,
            color: 'text.primary',
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
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'rgba(255, 255, 255, 0.5)',
              },
            }}
          />

          <Box>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mb: 2 }}
            >
              Quer avaliar um evento passado?
            </Typography>
            
            <Button
              variant="contained"
              onClick={onFileUpload}
              startIcon={<IosShareOutlinedIcon />}
              sx={{
                backgroundColor: 'grey.800',
                color: 'white',
                px: 3,
                py: 1,
                fontWeight: 600,
                borderRadius: 2,
                '&:hover': {
                  backgroundColor: 'grey.900',
                },
              }}
            >
              FAÇA UM UPLOAD
            </Button>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
};

export default SessionConfiguration;