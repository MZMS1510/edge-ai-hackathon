import React from 'react';
import { Card, CardContent, Typography, Button, Box } from '@mui/material';

interface CallToActionSectionProps {
  onStartSession: () => void;
}

const CallToActionSection: React.FC<CallToActionSectionProps> = ({ onStartSession }) => {
  return (
    <Card
      sx={{
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
      }}
    >
      <CardContent sx={{ p: 4, textAlign: 'center' }}>
        <Typography
          variant="h5"
          sx={{
            mb: 3,
            fontWeight: 600,
            color: 'text.primary',
          }}
        >
          Melhore a sua comunicação agora mesmo!
        </Typography>
        
        <Button
          variant="contained"
          size="large"
          onClick={onStartSession}
          sx={{
            backgroundColor: 'grey.800',
            color: 'white',
            px: 4,
            py: 1.5,
            fontSize: '1rem',
            fontWeight: 600,
            borderRadius: 2,
            '&:hover': {
              backgroundColor: 'grey.900',
            },
          }}
        >
          INICIAR
        </Button>
      </CardContent>
    </Card>
  );
};

export default CallToActionSection;