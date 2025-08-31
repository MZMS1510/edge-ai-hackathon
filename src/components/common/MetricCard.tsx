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
        height: 120,
        background: 'linear-gradient(145deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(255,255,255,0.3)',
        boxShadow: '0 8px 32px rgba(0,0,0,0.1), 0 4px 16px rgba(0,0,0,0.05)',
        borderRadius: 3,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          transform: 'translateY(-8px) scale(1.02)',
          boxShadow: '0 20px 40px rgba(0,0,0,0.15), 0 8px 24px rgba(0,0,0,0.1)',
          background: 'linear-gradient(145deg, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.9) 100%)'
        }
      }}
    >
      <CardContent sx={{ p: 2.5, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <Typography
          variant="body2"
          sx={{ 
            mb: 1, 
            fontSize: '0.75rem', 
            fontWeight: 500,
            color: '#64748b',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}
        >
          {title}
        </Typography>
        <Typography
          variant="h3"
          sx={{
            fontWeight: 700,
            color: '#1a202c',
            fontSize: '1.75rem',
            lineHeight: 1.2,
            mb: subtitle ? 0.5 : 0,
          }}
        >
          {value}
        </Typography>
        {subtitle && (
          <Typography
            variant="caption"
            sx={{ 
              fontSize: '0.7rem',
              color: '#64748b'
            }}
          >
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default MetricCard;