import React, { useEffect } from 'react';
import { X, ZoomIn, Info, Map as MapIcon } from 'lucide-react';

const ImageModal = ({ isOpen, onClose, imgSrc, title, details }) => {
  // Must be before any early return — cleanup MUST run when isOpen goes false
  useEffect(() => {
    const mainContent = document.getElementById('main-content');
    if (!mainContent) return;

    if (isOpen) {
      mainContent.style.overflow = 'hidden';
    } else {
      mainContent.style.overflow = 'auto';
    }
    return () => {
      mainContent.style.overflow = 'auto';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-8 bg-slate-950/90 backdrop-blur-md transition-all duration-300">
      {/* Close button on backdrop */}
      <div className="absolute inset-0 cursor-zoom-out" onClick={onClose}></div>
      
      <div className="relative w-full max-w-6xl bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden flex flex-col md:flex-row max-h-[90vh]">
        
        {/* Left Side: The Image */}
        <div className="flex-1 bg-black flex items-center justify-center relative overflow-hidden group">
          <img 
            src={imgSrc} 
            alt={title} 
            className="max-w-full max-h-full object-contain transition-transform duration-500 hover:scale-110 cursor-crosshair"
          />
          <div className="absolute bottom-4 left-4 flex gap-2">
            <div className="bg-slate-900/80 backdrop-blur-md px-3 py-1.5 rounded-full border border-slate-700 flex items-center gap-2">
                <ZoomIn size={14} className="text-indigo-400" />
                <span className="text-[10px] font-bold text-white uppercase tracking-wider">Hover to Zoom</span>
            </div>
          </div>
        </div>

        {/* Right Side: Metadata & Legend */}
        <div className="w-full md:w-80 border-t md:border-t-0 md:border-l border-slate-800 p-6 flex flex-col overflow-y-auto">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-xl font-bold text-white leading-tight">{title}</h2>
              <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-[0.2em]">Analytical Artifact</span>
            </div>
            <button 
              onClick={onClose}
              className="p-2 hover:bg-slate-800 rounded-xl text-slate-400 hover:text-white transition-colors"
            >
              <X size={20} />
            </button>
          </div>

          <div className="space-y-6">
            {/* Axis Definitions */}
            <div>
                <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                    <MapIcon size={12} /> Axis Definitions
                </h3>
                <div className="space-y-3">
                    <div className="bg-slate-950/50 p-3 rounded-xl border border-slate-800/50">
                        <p className="text-[9px] font-black text-indigo-400 uppercase tracking-tighter mb-1">X-Axis (Predicted)</p>
                        <p className="text-xs text-slate-300 leading-relaxed">{details.xAxis}</p>
                    </div>
                    <div className="bg-slate-950/50 p-3 rounded-xl border border-slate-800/50">
                        <p className="text-[9px] font-black text-emerald-400 uppercase tracking-tighter mb-1">Y-Axis (Actual)</p>
                        <p className="text-xs text-slate-300 leading-relaxed">{details.yAxis}</p>
                    </div>
                </div>
            </div>

            {/* Interpretation Legend */}
            <div>
                <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-3 flex items-center gap-2">
                    <Info size={12} /> Scientific Context
                </h3>
                <div className="p-4 bg-indigo-500/5 border border-indigo-500/10 rounded-2xl">
                    <p className="text-xs text-slate-400 leading-relaxed italic">
                        "{details.interpretation}"
                    </p>
                </div>
            </div>

            {/* Technical Stamp */}
            <div className="mt-auto pt-6 border-t border-slate-800">
                <div className="flex items-center justify-between text-[10px] font-mono">
                    <span className="text-slate-600">Verification:</span>
                    <span className="text-emerald-500 font-bold">STABLE_V2.0</span>
                </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageModal;
