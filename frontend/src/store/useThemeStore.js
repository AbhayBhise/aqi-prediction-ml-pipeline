import { create } from 'zustand';

const useThemeStore = create((set) => ({
  theme: localStorage.getItem('aqi-ui-theme') || 'light',
  setTheme: (theme) => set({ theme }),
}));

export default useThemeStore;
