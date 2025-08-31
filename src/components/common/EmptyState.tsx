import React from 'react';
import { Box, Typography, Stack } from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';

interface EmptyStateProps {
  message: string;
  showLockIcon?: boolean;
}

const EmptyState: React.FC<EmptyStateProps> = ({ message, showLockIcon = false }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        minHeight: 200,
        textAlign: 'center',
        p: 3,
      }}
    >
      {showLockIcon && (
        <LockOutlinedIcon
          sx={{
            fontSize: 48,
            color: 'grey.400',
            mb: 2,
          }}
        />
      )}
      <Typography
        variant="body2"
        color="text.secondary"
        sx={{
          maxWidth: 300,
          lineHeight: 1.5,
        }}
      >
        {message}
      </Typography>
    </Box>
  );
};

export default EmptyState;