// TypeScript schemas for the speech therapy dashboard

import { SessionType } from './enums';

// Props types (data passed to components)
export interface DashboardProps {
  metrics: DashboardMetrics;
  hasData: boolean;
  onStartSession: () => void;
}

export interface NovaSessionProps {
  onStartRecording: (type: SessionType) => void;
  onFileUpload: (file: File) => void;
  onSessionTitleChange: (title: string) => void;
}

export interface SidebarProps {
  currentRoute: string;
  user: UserProfile;
  onNavigate: (route: string) => void;
}

// Store types (global state data)
export interface AppState {
  user: UserProfile;
  dashboard: DashboardState;
  recording: RecordingStateInterface;
}

export interface UserProfile {
  name: string;
  avatar: string;
  isAuthenticated: boolean;
}

export interface DashboardState {
  metrics: DashboardMetrics;
  hasData: boolean;
}

export interface RecordingStateInterface {
  isRecording: boolean;
  recordingType: SessionType | null;
  currentSession: SessionData | null;
}

// Query types (API response data)
export interface DashboardMetrics {
  totalPresentations: number;
  averageTime: number;
  lastPerformanceScore: number;
  speechItemsAverage: number;
}

export interface PerformanceData {
  timestamp: string;
  score: number;
  duration: number;
}

export interface SessionData {
  id: string;
  title: string;
  type: SessionType;
  createdAt: string;
  duration?: number;
  score?: number;
}

export interface ImprovementPoint {
  id: string;
  category: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
}