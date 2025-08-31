import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';
import EmptyState from '../common/EmptyState';

interface ImprovementPointsWidgetProps {
  hasData: boolean;
}

const ImprovementPointsWidget: React.FC<ImprovementPointsWidgetProps> = ({ hasData }) => {
  return (
    <Card
      sx={{
        height: '100%',
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
      }}
    >
      <CardContent sx={{ p: 3, height: '100%' }}>
        <Typography
          variant="h6"
          sx={{
            mb: 2,
            fontWeight: 600,
            color: 'text.primary',
          }}
        >
          Pontos de Melhoria
        </Typography>
        
        <EmptyState 
          message="Faça seu primeiro pitch para desbloquear essa seção!"
          showLockIcon={true}
        />
      </CardContent>
    </Card>
  );
};

export default ImprovementPointsWidget;