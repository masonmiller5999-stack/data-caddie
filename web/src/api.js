import axios from 'axios';

const API_BASE = import.meta.env.PROD
  ? 'https://data-caddie-production.up.railway.app/api'
  : '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Tournament endpoints
export const getCurrentTournament = () => api.get('/tournaments/current');
export const getUpcomingTournaments = () => api.get('/tournaments/upcoming');

// Recommendations
export const calculateRecommendations = (weights, usedGolfers) =>
  api.post('/recommendations/calculate', {
    weights,
    used_golfers: usedGolfers,
  });

export const calculateAdvancedRecommendations = (weights, usedGolfers) =>
  api.post('/recommendations/calculate-advanced', {
    weights,
    used_golfers: usedGolfers,
  });

// Golfers
export const getUsedGolfers = () => api.get('/golfers/used');
export const addUsedGolfer = (name, tournament = null) =>
  api.post('/golfers/used', { name, tournament });
export const removeUsedGolfer = (name) =>
  api.delete(`/golfers/used/${encodeURIComponent(name)}`);
export const searchGolfers = (query) =>
  api.get('/golfers/search', { params: { q: query } });
export const getSeasonSummary = () => api.get('/golfers/season/summary');

// Config
export const getDefaultWeights = () => api.get('/config/weights');
export const getAdvancedDefaultWeights = () => api.get('/config/advanced-weights');

export default api;
