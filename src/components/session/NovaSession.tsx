import React from 'react';
import { Box, Typography, Stack } from '@mui/material';
import SessionConfiguration from './SessionConfiguration';
import RecordingInterface from './RecordingInterface';
import { NovaSessionProps } from '../../types/interfaces';

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
    <Box sx={{ p: 3 }}>
      <Typography
        variant="h4"
        sx={{
          mb: 4,
          fontWeight: 700,
          color: 'text.primary',
        }}
      >
        Nova Sessão
      </Typography>

      <Stack spacing={3}>
        <SessionConfiguration
          onSessionTitleChange={onSessionTitleChange}
          onFileUpload={handleFileUpload}
        />
        
        <RecordingInterface
          onStartRecording={onStartRecording}
          onFileUpload={onFileUpload}
        />
      </Stack>
    </Box>
  );
};

export default NovaSession;