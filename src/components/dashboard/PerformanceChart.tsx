import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { LineChart } from '@mui/x-charts/LineChart';
import EmptyState from '../common/EmptyState';

interface PerformanceChartProps {
  hasData: boolean;
}

const PerformanceChart: React.FC<PerformanceChartProps> = ({ hasData }) => {
  const mockData = hasData ? [
    { x: 1, y: 75 },
    { x: 2, y: 82 },
    { x: 3, y: 78 },
    { x: 4, y: 85 },
    { x: 5, y: 90 },
  ] : [];

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
          Performance ao Longo do Tempo
        </Typography>
        
        {!hasData ? (
          <EmptyState message="Nenhum dado disponível. Submeta sua primeira pitch" />
        ) : (
          <Box sx={{ height: 200, width: '100%' }}>
            <LineChart
              series={[
                {
                  data: mockData.map(point => point.y),
                  label: 'Resolução',
                  color: '#6366F1',
                },
              ]}
              xAxis={[
                {
                  data: mockData.map(point => point.x),
                  label: 'Tempo',
                  scaleType: 'linear',
                },
              ]}
              yAxis={[
                {
                  label: 'Resolução',
                  min: 0,
                  max: 100,
                },
              ]}
              width={undefined}
              height={200}
              margin={{ left: 60, right: 20, top: 20, bottom: 60 }}
              skipAnimation={false}
            />
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default PerformanceChart;