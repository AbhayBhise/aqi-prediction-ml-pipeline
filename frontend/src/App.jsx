import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Moon, Star } from "lucide-react";
import Dashboard from './pages/Dashboard';
import EDA from './pages/EDA';
import ModelComparison from './pages/ModelComparison';
import LSTMPage from './pages/LSTMPage';
import Clustering from './pages/Clustering';
import FinalInsights from './pages/FinalInsights';
import Prediction from "./pages/Prediction";
import GenerativeAI from './pages/GenerativeAI';
import AgenticAI from './pages/AgenticAI';
import BuyMeACoffeeModal from './components/BuyMeACoffeeModal';
import SidePanel from './components/SidePanel';
import AIChatbot from './components/AIChatbot';

const Layout = ({ children }) => {
  return (
    <div className="app-shell theme-dark flex bg-slate-950 h-screen overflow-hidden relative">
      {/* Global Celestial Background Animations */}
      <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden">
        <motion.div
          key="night-bg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900/90 to-indigo-950"
        >
          {/* Dynamic Moon */}
          <motion.div 
            className="absolute text-slate-200 drop-shadow-[0_0_40px_rgba(203,213,225,0.7)] opacity-90"
            animate={{ 
              y: [0, -20, 0],
              rotate: [0, 5, 0]
            }}
            transition={{ 
              duration: 20,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            style={{ right: '15%', top: '15%' }}
          >
            <Moon size={150} fill="currentColor" />
          </motion.div>
          {/* Blinking Stars */}
          {[...Array(40)].map((_, i) => (
            <motion.div
              key={`star-${i}`}
              animate={{ opacity: [0.1, 0.9, 0.1] }}
              transition={{
                duration: 2 + Math.random() * 4,
                repeat: Infinity,
                delay: Math.random() * 3,
                ease: "easeInOut"
              }}
              className="absolute text-yellow-100"
              style={{
                top: `${Math.random() * 100}%`,
                left: `${Math.random() * 100}%`,
                transform: `scale(${0.2 + Math.random() * 0.6})`
              }}
            >
              <Star size={24} fill="currentColor" />
            </motion.div>
          ))}
        </motion.div>
      </div>

      <SidePanel />
      <main id="main-content" className="flex-1 overflow-y-auto p-8 relative z-10 scrollbar-hide">
        {children}
      </main>
      <BuyMeACoffeeModal />
      <AIChatbot />
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <Layout>
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
      </Layout>
    </BrowserRouter>
  );
}

export default App;
