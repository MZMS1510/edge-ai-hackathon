// Enums for the speech therapy dashboard application

export enum SessionType {
  AUDIO_ONLY = 'audio_only',
  AUDIO_VIDEO = 'audio_video',
  FILE_UPLOAD = 'file_upload'
}

export enum RecordingState {
  IDLE = 'idle',
  RECORDING = 'recording',
  PAUSED = 'paused',
  STOPPED = 'stopped'
}

export enum MetricType {
  PRESENTATIONS_TOTAL = 'presentations_total',
  AVERAGE_TIME = 'average_time',
  LAST_PERFORMANCE_SCORE = 'last_performance_score',
  SPEECH_ITEMS_AVERAGE = 'speech_items_average'
}

export enum NavigationItem {
  DASHBOARD = 'dashboard',
  NEW_SESSION = 'new_session',
  SESSIONS = 'sessions',
  ANALYTICS = 'analytics',
  SETTINGS = 'settings'
}