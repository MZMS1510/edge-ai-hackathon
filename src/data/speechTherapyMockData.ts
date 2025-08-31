// Mock data for the speech therapy dashboard

import { SessionType } from '../types/enums';

// Data for global state store
export const mockStore = {
  user: {
    name: "Lavínia Mendonça" as const,
    avatar: "/assets/fotos/lavinia-mendonca.jpg" as const,
    isAuthenticated: true as const
  },
  dashboard: {
    metrics: {
      totalPresentations: 0 as const,
      averageTime: 0 as const,
      lastPerformanceScore: 0 as const,
      speechItemsAverage: 0 as const
    },
    hasData: false as const
  },
  recording: {
    isRecording: false as const,
    recordingType: null,
    currentSession: null
  }
};

// Data returned by API queries
export const mockQuery = {
  dashboardMetrics: {
    totalPresentations: 0 as const,
    averageTime: 0 as const,
    lastPerformanceScore: 0 as const,
    speechItemsAverage: 0 as const,
    performanceData: [] as const,
    recentSessions: [] as const,
    improvementPoints: [] as const
  },
  userProfile: {
    name: "Lavínia Mendonça" as const,
    avatar: "/assets/fotos/lavinia-mendonca.jpg" as const
  }
};

// Data passed as props to the root component
export const mockRootProps = {
  initialRoute: "/dashboard" as const,
  theme: "light" as const
};