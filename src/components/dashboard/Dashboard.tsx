import React from 'react';
import { Box, Typography, Stack } from '@mui/material';
import MetricCard from '../common/MetricCard';
import PerformanceChart from './PerformanceChart';
import ImprovementPointsWidget from './ImprovementPointsWidget';
import RecentSessionsWidget from './RecentSessionsWidget';
import CallToActionSection from './CallToActionSection';
import { DashboardProps } from '../../types/interfaces';
import { formatDuration, formatWordsPerMinute, formatScore, formatPresentationCount } from '../../utils/formatters';

const Dashboard: React.FC<DashboardProps> = ({ metrics, hasData, onStartSession }) => {
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
        Dashboard
      </Typography>

      {/* Metrics Cards */}
      <Stack direction="row" spacing={3} sx={{ mb: 4 }}>
        <Box sx={{ flex: 1 }}>
          <MetricCard
            title="Total de Apresentações"
            value={formatPresentationCount(metrics.totalPresentations)}
          />
        </Box>
        <Box sx={{ flex: 1 }}>
          <MetricCard
            title="Tempo Médio de Apresentação"
            value={formatDuration(metrics.averageTime)}
          />
        </Box>
        <Box sx={{ flex: 1 }}>
          <MetricCard
            title="Última Pontuação de Performance"
            value={formatScore(metrics.lastPerformanceScore)}
          />
        </Box>
        <Box sx={{ flex: 1 }}>
          <MetricCard
            title="Média de Itens de Fala (PPM)"
            value={formatWordsPerMinute(metrics.speechItemsAverage)}
          />
        </Box>
      </Stack>

      {/* Main Content Grid */}
      <Stack direction="row" spacing={3} sx={{ mb: 4 }}>
        {/* Performance Chart */}
        <Box sx={{ flex: 2 }}>
          <PerformanceChart hasData={hasData} />
        </Box>
        
        {/* Improvement Points */}
        <Box sx={{ flex: 1 }}>
          <ImprovementPointsWidget hasData={hasData} />
        </Box>
      </Stack>

      {/* Bottom Section */}
      <Stack direction="row" spacing={3}>
        {/* Recent Sessions */}
        <Box sx={{ flex: 1 }}>
          <RecentSessionsWidget hasData={hasData} />
        </Box>
        
        {/* Call to Action */}
        <Box sx={{ flex: 1 }}>
          <CallToActionSection onStartSession={onStartSession} />
        </Box>
      </Stack>
    </Box>
  );
};

export default Dashboard;