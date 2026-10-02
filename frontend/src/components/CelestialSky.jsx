import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Moon, Sun, Cloud, Star } from "lucide-react";

const CelestialSky = ({ theme }) => {
  return (
    <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden">
      <AnimatePresence mode="wait">
        {theme === 'light' ? (
          <motion.div
            key="day-bg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1 }}
            className="absolute inset-0 bg-gradient-to-br from-sky-300 via-blue-200 to-amber-100"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
              className="absolute top-[10%] right-[10%] text-amber-500 opacity-90 drop-shadow-[0_0_30px_rgba(245,158,11,0.5)]"
            >
              <Sun size={120} />
            </motion.div>
            <motion.div
              animate={{ x: [0, 40, 0], y: [0, -10, 0] }}
              transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
              className="absolute top-[20%] left-[20%] text-white/80"
            >
              <Cloud size={80} fill="currentColor" />
            </motion.div>
            <motion.div
              animate={{ x: [0, -30, 0], y: [0, 15, 0] }}
              transition={{ duration: 25, repeat: Infinity, ease: "easeInOut", delay: 2 }}
              className="absolute top-[40%] right-[30%] text-white/60"
            >
              <Cloud size={100} fill="currentColor" />
            </motion.div>
          </motion.div>
        ) : (
          <motion.div
            key="night-bg"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1 }}
            className="absolute inset-0 bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950"
          >
            <motion.div
              animate={{ y: [0, -10, 0], rotate: [0, 5, 0] }}
              transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
              className="absolute top-[15%] right-[15%] text-white drop-shadow-[0_0_60px_rgba(255,255,255,0.9)]"
            >
              <Moon size={100} fill="#ffffff" stroke="#ffffff" className="opacity-100" />
            </motion.div>
            {[...Array(20)].map((_, i) => (
              <motion.div
                key={`star-${i}`}
                animate={{ opacity: [0.2, 0.8, 0.2] }}
                transition={{
                  duration: 2 + Math.random() * 2,
                  repeat: Infinity,
                  delay: Math.random() * 2,
                  ease: "easeInOut"
                }}
                className="absolute text-yellow-100"
                style={{
                  top: `${Math.random() * 80}%`,
                  left: `${Math.random() * 100}%`,
                  transform: `scale(${0.3 + Math.random() * 0.5})`
                }}
              >
                <Star size={24} fill="currentColor" />
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default CelestialSky;
