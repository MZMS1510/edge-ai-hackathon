import React, { useState } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import createCache from "@emotion/cache";
import { CacheProvider } from "@emotion/react";

import theme from './theme/theme';
import Layout from './components/layout/Layout';
import Dashboard from './components/dashboard/Dashboard';
import NovaSession from './components/session/NovaSession';
import { useMediaRecorder } from './hooks/useMediaRecorder';
import { mockStore } from './data/speechTherapyMockData';
import { SessionType } from './types/enums';

const createEmotionCache = () => {
  return createCache({
    key: "mui",
    prepend: true,
  });
};

const emotionCache = createEmotionCache();

const App: React.FC = () => {
  const [currentRoute, setCurrentRoute] = useState('dashboard');
  const [sessionTitle, setSessionTitle] = useState('');
  
  const { startRecording, stopRecording, isRecording, error } = useMediaRecorder();

  const handleStartRecording = async (type: SessionType) => {
    try {
      await startRecording(type);
      console.log(`Started recording: ${type}`);
    } catch (err) {
      console.error('Failed to start recording:', err);
    }
  };

  const handleFileUpload = (file: File) => {
    console.log('File uploaded:', file.name);
    // Handle file upload logic here
  };

  const handleSessionTitleChange = (title: string) => {
    setSessionTitle(title);
  };

  const handleStartSession = () => {
    setCurrentRoute('new_session');
  };

  const handleNavigate = (route: string) => {
    setCurrentRoute(route);
  };

  const renderCurrentScreen = () => {
    switch (currentRoute) {
      case 'dashboard':
        return (
          <Dashboard
            metrics={mockStore.dashboard.metrics}
            hasData={mockStore.dashboard.hasData}
            onStartSession={handleStartSession}
          />
        );
      case 'new_session':
        return (
          <NovaSession
            onStartRecording={handleStartRecording}
            onFileUpload={handleFileUpload}
            onSessionTitleChange={handleSessionTitleChange}
          />
        );
      default:
        return (
          <Dashboard
            metrics={mockStore.dashboard.metrics}
            hasData={mockStore.dashboard.hasData}
            onStartSession={handleStartSession}
          />
        );
    }
  };

  return (
    <CacheProvider value={emotionCache}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Layout
          currentRoute={currentRoute}
          user={mockStore.user}
          onNavigate={handleNavigate}
        >
          {renderCurrentScreen()}
        </Layout>
      </ThemeProvider>
    </CacheProvider>
  );
};

export default App;