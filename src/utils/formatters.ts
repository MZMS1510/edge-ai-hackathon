// String formatters for the speech therapy dashboard

export const formatDuration = (minutes: number): string => {
  if (minutes === 0) return '0min';
  if (minutes < 60) return `${minutes}min`;
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}min` : `${hours}h`;
};

export const formatWordsPerMinute = (wpm: number): string => {
  return `${wpm} palavras/min`;
};

export const formatScore = (score: number): string => {
  return score.toString();
};

export const formatPresentationCount = (count: number): string => {
  return count.toString();
};

export const formatSessionTitle = (title: string): string => {
  return title.trim() || 'Sessão sem título';
};