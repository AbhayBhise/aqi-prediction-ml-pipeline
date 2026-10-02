import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  BarChart3,
  LineChart,
  Brain,
  Network,
  Activity,
  Zap,
  Cpu,
  Bot,
  Coffee,
  Star,
  Moon
} from "lucide-react";
import { motion } from 'framer-motion';

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
      <button onClick={onClick} className="w-full flex items-center px-4 py-3 mb-2 rounded-xl transition-all duration-300 text-slate-400 hover:bg-slate-800/50 hover:text-white hover:scale-[1.02] active:scale-95">
        <Icon size={20} className="mr-3" />
        <span className="font-medium text-sm tracking-wide">{text}</span>
      </button>
    );
  }

  return (
    <Link to={to} className={`flex items-center px-4 py-3 mb-2 rounded-xl transition-all duration-300 ${isActive ? 'bg-indigo-600/80 text-white shadow-[0_0_15px_rgba(79,70,229,0.3)] border border-indigo-500/50' : 'text-slate-400 hover:bg-slate-800/50 hover:text-white hover:scale-[1.02] border border-transparent'}`}>
      <Icon size={20} className="mr-3" />
      <span className="font-medium text-sm tracking-wide">{text}</span>
    </Link>
  );
};

const SidePanel = () => {
  return (
    <nav className="w-64 border-r bg-slate-900/40 backdrop-blur-xl border-slate-800/60 shadow-[2px_0_20px_rgba(0,0,0,0.4)] flex flex-col transition-colors duration-500 z-20 overflow-hidden relative group">
      
      {/* Animated Celestial Background inside SidePanel */}
      <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden opacity-30 mix-blend-screen">
        <div className="absolute inset-0 bg-gradient-to-b from-indigo-900/20 via-slate-900/10 to-transparent"></div>
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={`star-sp-${i}`}
            animate={{ opacity: [0.1, 0.7, 0.1] }}
            transition={{
              duration: 2 + Math.random() * 3,
              repeat: Infinity,
              delay: Math.random() * 2,
              ease: "easeInOut"
            }}
            className="absolute text-indigo-200"
            style={{
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              transform: `scale(${0.2 + Math.random() * 0.4})`
            }}
          >
            <Star size={16} fill="currentColor" />
          </motion.div>
        ))}
      </div>
      
      <div className="p-6 relative z-30">
        <h1 className="text-2xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 drop-shadow-[0_0_10px_rgba(99,102,241,0.2)]">AQI ML Vision</h1>
        <p className="text-slate-500 text-xs mt-1 tracking-wider uppercase font-bold">Analytics Dashboard</p>
      </div>
      
      <div className="px-4 mt-2 relative z-30 flex-1 overflow-y-auto overflow-x-hidden scrollbar-hide">
        <p className="px-4 text-[10px] font-black text-indigo-400/70 uppercase tracking-widest mb-3 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse"></span>
          Core Modules
        </p>
        <SidebarItem to="/" iconKey="dashboard" text="Dashboard" />
        <SidebarItem to="/eda" iconKey="eda" text="Dataset EDA" />
        <SidebarItem to="/comparison" iconKey="comparison" text="Model Comparison" />
        <SidebarItem to="/lstm" iconKey="lstm" text="LSTM Analytics" />
        <SidebarItem to="/clustering" iconKey="clustering" text="Clustering Analysis" />
        <SidebarItem to="/prediction" iconKey="prediction" text="AQI Forecast" />
        <SidebarItem to="/insights" iconKey="insights" text="Final Insights" />

        <div className="pt-4 mt-4 border-t border-slate-800/50">
          <p className="px-4 text-[10px] font-black text-cyan-400/70 uppercase tracking-widest mb-3 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse"></span>
            Advanced AI
          </p>
          <SidebarItem to="/generative" iconKey="generative" text="Generative AI (VAE)" />
          <SidebarItem to="/agent" iconKey="agent" text="Agentic AI" />
        </div>

        <div className="pt-4 mt-4 border-t border-slate-800/50 mb-6">
          <p className="px-4 text-[10px] font-black text-amber-400/70 uppercase tracking-widest mb-3">Support</p>
          <a 
            href="https://buymeacoffee.com/bhiseabhayq" 
            target="_blank" 
            rel="noopener noreferrer"
            className="flex items-center justify-center px-4 py-3 rounded-xl transition-all duration-300 text-[#FFDD00] bg-[#FFDD00]/10 hover:bg-[#FFDD00]/20 border border-[#FFDD00]/30 hover:scale-[1.02] shadow-[0_0_15px_rgba(255,221,0,0.1)] hover:shadow-[0_0_20px_rgba(255,221,0,0.2)]"
          >
            <Coffee size={18} className="mr-2" />
            <span className="font-bold text-sm tracking-wide">Buy me a coffee</span>
          </a>
        </div>
      </div>
    </nav>
  );
};

export default SidePanel;
