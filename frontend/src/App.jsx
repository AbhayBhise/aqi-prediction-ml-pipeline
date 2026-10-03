import React, { useState, useEffect, Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import SidePanel from './components/SidePanel';
import AIChatbot from './components/AIChatbot';
import BuyMeACoffeeModal from './components/BuyMeACoffeeModal';
import CelestialSky from './components/CelestialSky';

// Lazy load pages for performance
const Dashboard = lazy(() => import('./pages/Dashboard'));
const EDA = lazy(() => import('./pages/EDA'));
const ModelComparison = lazy(() => import('./pages/ModelComparison'));
const LSTMPage = lazy(() => import('./pages/LSTMPage'));
const Clustering = lazy(() => import('./pages/Clustering'));
const Prediction = lazy(() => import('./pages/Prediction'));
const FinalInsights = lazy(() => import('./pages/FinalInsights'));
const GenerativeAI = lazy(() => import('./pages/GenerativeAI'));
const AgenticAI = lazy(() => import('./pages/AgenticAI'));

import useCelestialSky from './hooks/useCelestialSky';

const PageLoader = () => (
  <div className="flex items-center justify-center h-full w-full">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
  </div>
);

const Layout = ({ children, theme, onThemeChange }) => {
  return (
    <div className={`app-shell theme-${theme} flex bg-transparent h-screen overflow-hidden relative`}>
      <CelestialSky theme={theme} />
      <SidePanel theme={theme} onThemeChange={onThemeChange} />
      <main id="main-content" className="flex-1 overflow-y-auto p-4 pt-16 md:p-8 md:pt-8 relative z-10 scrollbar-hide">
        {children}
      </main>
      <BuyMeACoffeeModal />
      <AIChatbot />
    </div>
  );
};

const getInitialTheme = () => {
  const saved = localStorage.getItem('theme-preference');
  if (saved) return saved;
  const currentHour = new Date().getHours();
  if (currentHour >= 6 && currentHour < 18) {
    return 'light';
  }
  return 'dark';
};

function App() {
  const [theme, setTheme] = useState(getInitialTheme);
  const { celestial } = useCelestialSky();

  useEffect(() => {
    if (celestial && celestial.sun) {
      // If sun altitude is > 0, it's day (light theme), else night (dark theme)
      // Only set if not explicitly saved by user (we assume they want the sky to match location)
      const isDay = celestial.sun.altitude > 0;
      setTheme(isDay ? 'light' : 'dark');
    }
  }, [celestial]);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    if (theme === 'light') {
      document.documentElement.classList.add('theme-light');
      document.documentElement.classList.remove('theme-dark', 'dark');
    } else {
      document.documentElement.classList.add('theme-dark', 'dark');
      document.documentElement.classList.remove('theme-light');
    }
    localStorage.setItem('theme-preference', theme);
  }, [theme]);

  return (
    <BrowserRouter>
      <Layout theme={theme} onThemeChange={setTheme}>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/eda" element={<EDA />} />
            <Route path="/comparison" element={<ModelComparison />} />
            <Route path="/lstm" element={<LSTMPage />} />
            <Route path="/clustering" element={<Clustering />} />
            <Route path="/prediction" element={<Prediction />} />
            <Route path="/insights" element={<FinalInsights />} />
            <Route path="/generative" element={<GenerativeAI />} />
            <Route path="/agent" element={<AgenticAI />} />
          </Routes>
        </Suspense>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
