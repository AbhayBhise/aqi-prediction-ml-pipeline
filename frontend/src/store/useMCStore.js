import { create } from 'zustand';

const useMCStore = create((set) => ({
  metrics: [],
  forecastMetrics: [],
  loading: true,
  hasLoaded: false,
  setAll: (data) => set(data)
}));

export default useMCStore;
