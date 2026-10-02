import { create } from 'zustand';

const useDashboardStore = create((set) => ({
  dashboardData: null,
  setDashboardData: (data) => set({ dashboardData: data }),
  weatherData: null,
  setWeatherData: (data) => set({ weatherData: data }),
  location: null,
  setLocation: (location) => set({ location }),
  loading: false,
  setLoading: (loading) => set({ loading }),
  error: null,
  setError: (error) => set({ error }),
}));

export default useDashboardStore;
