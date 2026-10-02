import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const TIPS = [
  "Analyzing temporal sequences for AQI trends...",
  "Calibrating forecasting models...",
  "Synthesizing latent space distributions...",
  "Applying dynamic thresholds based on location...",
  "Loading environmental intelligence modules..."
];

const LoadingOverlay = ({ message = "Loading...", progress: externalProgress }) => {
  const [internalProgress, setInternalProgress] = useState(0);
  const [tipIndex, setTipIndex] = useState(0);

  const isExternal = externalProgress !== undefined;
  const progress = isExternal ? externalProgress : internalProgress;

  useEffect(() => {
    if (isExternal) return;
    const interval = setInterval(() => {
      setInternalProgress((prev) => {
        if (prev >= 98) return prev;
        const jump = Math.random() * 15;
        return Math.min(99, prev + jump);
      });
    }, 400);

    return () => clearInterval(interval);
  }, [isExternal]);

  useEffect(() => {
    const tipInterval = setInterval(() => {
      setTipIndex(prev => (prev + 1) % TIPS.length);
    }, 2500);
    return () => clearInterval(tipInterval);
  }, []);

  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center h-64 space-y-6 w-full">
      <div className="relative flex items-center justify-center">
        <svg className="transform -rotate-90 w-32 h-32">
          <circle
            cx="64"
            cy="64"
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            fill="transparent"
            className="text-slate-200 dark:text-slate-700"
          />
          <motion.circle
            cx="64"
            cy="64"
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            fill="transparent"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="text-indigo-500"
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center">
          <span className="text-xl font-bold text-indigo-500">
            {Math.min(Math.floor(progress), 100)}%
          </span>
        </div>
      </div>
      
      <div className="flex flex-col items-center space-y-2 text-slate-900 dark:text-white font-medium">
        <h3 className="text-lg font-semibold tracking-wide">{message}</h3>
        {!isExternal && (
           <p className="text-xs text-slate-500 dark:text-slate-400 font-mono tracking-wider animate-pulse text-center max-w-sm mt-2">
             {TIPS[tipIndex]}
           </p>
        )}
      </div>
    </div>
  );
};

export default LoadingOverlay;
