import React from 'react';
import { Box, Typography, Grid, Container, Paper } from '@mui/material';
import MetricCard from '../common/MetricCard';
import PerformanceChart from './PerformanceChart';
import ImprovementPointsWidget from './ImprovementPointsWidget';
import RecentSessionsWidget from './RecentSessionsWidget';
import CallToActionSection from './CallToActionSection';
import { mockStore } from '../../data/speechTherapyMockData';
import { formatDuration, formatWordsPerMinute, formatScore, formatPresentationCount } from '../../utils/formatters';

interface DashboardMetrics {
  totalPresentations: number;
  averageTime: number;
  lastPerformanceScore: number;
  speechItemsAverage: number;
}

interface DashboardProps {
  metrics: DashboardMetrics;
  hasData: boolean;
  onStartSession: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ metrics, hasData, onStartSession }) => {
  return (
    <Box 
      sx={{ 
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        py: 4
      }}
    >
      <Container maxWidth="xl">
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography
            variant="h3"
            sx={{
              fontWeight: 800,
              color: 'white',
              textAlign: 'center',
              mb: 1,
              textShadow: '0 2px 4px rgba(0,0,0,0.3)'
            }}
          >
            Dashboard
          </Typography>
          <Typography
            variant="h6"
            sx={{
              color: 'rgba(255,255,255,0.8)',
              textAlign: 'center',
              fontWeight: 300
            }}
          >
            Acompanhe seu progresso em terapia da fala
          </Typography>
        </Box>

        {/* Metrics Cards */}
        <Grid container spacing={{ xs: 2, md: 3 }} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} lg={3}>
            <Paper 
              elevation={20} 
              sx={{ 
                borderRadius: 3,
                overflow: 'hidden',
                background: 'linear-gradient(145deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255,255,255,0.3)',
                boxShadow: '0 8px 32px rgba(0,0,0,0.1), 0 4px 16px rgba(0,0,0,0.05)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-12px) scale(1.02)',
                  boxShadow: '0 20px 40px rgba(0,0,0,0.15), 0 8px 24px rgba(0,0,0,0.1)'
                }
              }}
            >
              <MetricCard
                title="Total de Apresentações"
                value={formatPresentationCount(metrics.totalPresentations)}
              />
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} lg={3}>
            <Paper 
              elevation={20} 
              sx={{ 
                borderRadius: 3,
                overflow: 'hidden',
                background: 'linear-gradient(145deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255,255,255,0.3)',
                boxShadow: '0 8px 32px rgba(0,0,0,0.1), 0 4px 16px rgba(0,0,0,0.05)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-12px) scale(1.02)',
                  boxShadow: '0 20px 40px rgba(0,0,0,0.15), 0 8px 24px rgba(0,0,0,0.1)'
                }
              }}
            >
              <MetricCard
                title="Tempo Médio de Apresentação"
                value={formatDuration(metrics.averageTime)}
              />
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} lg={3}>
            <Paper 
              elevation={20} 
              sx={{ 
                borderRadius: 3,
                overflow: 'hidden',
                background: 'linear-gradient(145deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255,255,255,0.3)',
                boxShadow: '0 8px 32px rgba(0,0,0,0.1), 0 4px 16px rgba(0,0,0,0.05)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-12px) scale(1.02)',
                  boxShadow: '0 20px 40px rgba(0,0,0,0.15), 0 8px 24px rgba(0,0,0,0.1)'
                }
              }}
            >
              <MetricCard
                title="Última Pontuação de Performance"
                value={formatScore(metrics.lastPerformanceScore)}
              />
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} lg={3}>
            <Paper 
              elevation={20} 
              sx={{ 
                borderRadius: 3,
                overflow: 'hidden',
                background: 'linear-gradient(145deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255,255,255,0.3)',
                boxShadow: '0 8px 32px rgba(0,0,0,0.1), 0 4px 16px rgba(0,0,0,0.05)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-12px) scale(1.02)',
                  boxShadow: '0 20px 40px rgba(0,0,0,0.15), 0 8px 24px rgba(0,0,0,0.1)'
                }
              }}
            >
              <MetricCard
                title="Média de Itens de Fala (PPM)"
                value={formatWordsPerMinute(metrics.speechItemsAverage)}
              />
            </Paper>
          </Grid>
        </Grid>

        {/* Main Content Grid */}
        <Grid container spacing={{ xs: 2, md: 3 }} sx={{ mb: 4 }}>
          {/* Performance Chart */}
          <Grid item xs={12} lg={8}>
            <Paper 
              elevation={20} 
              sx={{ 
                borderRadius: 3,
                overflow: 'hidden',
                height: { xs: '300px', md: '400px' },
                background: 'linear-gradient(145deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255,255,255,0.3)',
                boxShadow: '0 8px 32px rgba(0,0,0,0.1), 0 4px 16px rgba(0,0,0,0.05)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: '0 20px 40px rgba(0,0,0,0.15), 0 8px 24px rgba(0,0,0,0.1)'
                }
              }}
            >
              <PerformanceChart hasData={hasData} />
            </Paper>
          </Grid>
          
          {/* Improvement Points */}
          <Grid item xs={12} lg={4}>
            <Paper 
              elevation={20} 
              sx={{ 
                borderRadius: 3,
                overflow: 'hidden',
                height: { xs: '300px', md: '400px' },
                background: 'linear-gradient(145deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255,255,255,0.3)',
                boxShadow: '0 8px 32px rgba(0,0,0,0.1), 0 4px 16px rgba(0,0,0,0.05)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: '0 20px 40px rgba(0,0,0,0.15), 0 8px 24px rgba(0,0,0,0.1)'
                }
              }}
            >
              <ImprovementPointsWidget hasData={hasData} />
            </Paper>
          </Grid>
        </Grid>

        {/* Bottom Section */}
        <Grid container spacing={{ xs: 2, md: 3 }}>
          {/* Recent Sessions */}
          <Grid item xs={12} lg={8}>
            <Paper 
              elevation={20} 
              sx={{ 
                borderRadius: 3,
                overflow: 'hidden',
                height: { xs: '250px', md: '300px' },
                background: 'linear-gradient(145deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255,255,255,0.3)',
                boxShadow: '0 8px 32px rgba(0,0,0,0.1), 0 4px 16px rgba(0,0,0,0.05)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: '0 20px 40px rgba(0,0,0,0.15), 0 8px 24px rgba(0,0,0,0.1)'
                }
              }}
            >
              <RecentSessionsWidget hasData={hasData} />
            </Paper>
          </Grid>
          
          {/* Call to Action */}
          <Grid item xs={12} lg={4}>
            <Paper 
              elevation={20} 
              sx={{ 
                borderRadius: 3,
                overflow: 'hidden',
                height: { xs: '250px', md: '300px' },
                background: 'linear-gradient(145deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255,255,255,0.3)',
                boxShadow: '0 8px 32px rgba(0,0,0,0.1), 0 4px 16px rgba(0,0,0,0.05)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: '0 20px 40px rgba(0,0,0,0.15), 0 8px 24px rgba(0,0,0,0.1)'
                }
              }}
            >
              <CallToActionSection onStartSession={onStartSession} />
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Dashboard;