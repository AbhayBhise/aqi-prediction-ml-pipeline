import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  BarChart3,
  LineChart,
  Brain,
  Network,
  Activity,
  Zap,
  MessageSquare,
  Cpu,
  Bot
} from "lucide-react";
import Dashboard from './pages/Dashboard';
import EDA from './pages/EDA';
import ModelComparison from './pages/ModelComparison';
import LSTMPage from './pages/LSTMPage';
import Clustering from './pages/Clustering';
import FinalInsights from './pages/FinalInsights';
import Prediction from "./pages/Prediction";
import GenerativeAI from './pages/GenerativeAI';
import AgenticAI from './pages/AgenticAI';

const icons = {
  dashboard: LayoutDashboard,
  eda: BarChart3,
  comparison: Activity,
  lstm: Brain,
  clustering: Network,
  prediction: Zap,
  insights: LineChart,
  generative: Cpu,
  agent: Bot,
};

const SidebarItem = ({ to, iconKey, text, onClick }) => {
  const location = useLocation();
  const isActive = location.pathname === to && !onClick;
  const Icon = icons[iconKey] || LayoutDashboard;

  if (onClick) {
    return (
      <button onClick={onClick} className="w-full flex items-center px-4 py-3 mb-2 rounded-lg transition-colors text-slate-400 hover:bg-slate-800 hover:text-white">
        <Icon size={20} className="mr-3" />
        <span className="font-medium">{text}</span>
      </button>
    );
  }

  return (
    <Link to={to} className={`flex items-center px-4 py-3 mb-2 rounded-lg transition-colors ${isActive ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'}`}>
      <Icon size={20} className="mr-3" />
      <span className="font-medium">{text}</span>
    </Link>
  );
};

const Sidebar = () => {
  return (
    <div className="w-64 bg-slate-900 border-r border-slate-800 h-screen overflow-y-auto shrink-0">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">AQI ML Vision</h1>
        <p className="text-slate-500 text-sm mt-1">Analytics Dashboard</p>
      </div>
      <div className="px-4 mt-6">
        <p className="px-4 text-[10px] font-black text-slate-600 uppercase tracking-widest mb-3">Core Modules</p>
        <SidebarItem to="/" iconKey="dashboard" text="Dashboard Overview" />
        <SidebarItem to="/eda" iconKey="eda" text="Dataset EDA" />
        <SidebarItem to="/comparison" iconKey="comparison" text="Model Comparison" />
        <SidebarItem to="/lstm" iconKey="lstm" text="LSTM Analytics" />
        <SidebarItem to="/clustering" iconKey="clustering" text="Clustering Analysis" />
        <SidebarItem to="/prediction" iconKey="prediction" text="AQI Forecast" />
        <SidebarItem to="/insights" iconKey="insights" text="Final Insights" />

        <div className="pt-4 mt-4 border-t border-slate-800">
          <p className="px-4 text-[10px] font-black text-slate-600 uppercase tracking-widest mb-3">Advanced AI</p>
          <SidebarItem to="/generative" iconKey="generative" text="Generative AI (VAE)" />
          <SidebarItem to="/agent" iconKey="agent" text="Agentic AI" />
        </div>
      </div>
    </div>
  );
};

const Layout = ({ children }) => {
  return (
    <div className="flex bg-slate-950 h-screen overflow-hidden">
      <Sidebar />
      <main id="main-content" className="flex-1 overflow-y-auto p-8 relative">
        {children}
      </main>
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
