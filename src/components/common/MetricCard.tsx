import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, subtitle }) => {
  return (
    <Card
      sx={{
        height: '100%',
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
      }}
    >
      <CardContent sx={{ p: 3 }}>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mb: 1, fontSize: '0.75rem', fontWeight: 500 }}
        >
          {title}
        </Typography>
        <Typography
          variant="h4"
          sx={{
            fontWeight: 700,
            color: 'text.primary',
            mb: subtitle ? 0.5 : 0,
          }}
        >
          {value}
        </Typography>
        {subtitle && (
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ fontSize: '0.7rem' }}
          >
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default MetricCard;