import React, { useState, useEffect } from 'react';
import api from '../services/api';

const IMG_BASE = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/images`;

const LSTMPage = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await api.get('/sequential_comparison');
        setMetrics(response.data);
      } catch (error) {
        console.error('Error fetching sequential metrics:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  return (
    <div className="pb-20">
      <div className="flex justify-between items-center mb-10">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Temporal Sequence Analysis</h1>
          <p className="text-slate-400 mt-2 max-w-2xl">
            Leveraging sequential deep learning architectures to capture the multi-scalar temporal dependencies of urban pollutants.
          </p>
        </div>
        <div className="bg-indigo-500/10 border border-indigo-500/20 px-4 py-2 rounded-xl flex items-center gap-2">
            <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-ping"></span>
            <span className="text-indigo-400 text-xs font-black uppercase tracking-widest">Time-Series Deep Learning</span>
        </div>
      </div>

      {/* Comparison Metrics Cards */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-slate-900/50 border border-slate-800 rounded-3xl p-6 h-32 animate-pulse flex flex-col justify-between">
              <div className="h-4 bg-slate-800 rounded w-1/3"></div>
              <div className="h-8 bg-slate-800 rounded w-1/2"></div>
              <div className="h-2 bg-slate-800 rounded w-full"></div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          {['RNN', 'LSTM', 'BiLSTM'].map((m) => (
            <div key={m} className={`bg-slate-900/50 border ${m === 'BiLSTM' ? 'border-indigo-500/50' : 'border-slate-800'} rounded-3xl p-6 relative overflow-hidden transition-all duration-500 hover:scale-[1.05] hover:bg-slate-900/80 group`}>
               <div className="flex justify-between items-start mb-4">
                  <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{m} Architecture</span>
                  {m === 'BiLSTM' && <span className="bg-indigo-500 text-[8px] font-bold px-2 py-0.5 rounded-full text-white uppercase tracking-tighter shadow-[0_0_10px_rgba(99,102,241,0.5)]">Optimal</span>}
               </div>
               <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-black text-white">
                      {metrics?.[m]?.accuracy ? (metrics[m].accuracy * 100).toFixed(1) : '—'}%
                  </span>
                  <span className="text-slate-500 text-xs font-medium">Accuracy</span>
               </div>
               <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div 
                          className={`h-full transition-all duration-1000 ${m === 'RNN' ? 'bg-rose-500' : m === 'LSTM' ? 'bg-blue-500' : 'bg-emerald-500'}`} 
                          style={{ width: `${(metrics?.[m]?.f1_score || 0) * 100}%` }}
                      ></div>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">
                      F1: {metrics?.[m]?.f1_score ? metrics[m].f1_score.toFixed(3) : '—'}
                  </span>
               </div>
               <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:opacity-10 transition-opacity">
                   <svg className="w-24 h-24 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 14.5c-2.48 0-4.5-2.02-4.5-4.5S9.52 7.5 12 7.5s4.5 2.02 4.5 4.5-2.02 4.5-4.5 4.5z"/></svg>
               </div>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
        {/* Comparative Analysis Plot */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl relative group">
            <div className="p-6 border-b border-slate-800 bg-slate-950/40 flex justify-between items-center">
                <div>
                    <h3 className="text-lg font-bold text-white">Comparative Benchmark</h3>
                    <p className="text-xs text-slate-500 mt-1">Accuracy vs F1 Score across different recurrent architectures.</p>
                </div>
                <div className="text-[10px] font-bold text-indigo-400 bg-indigo-400/10 px-2 py-1 rounded-md">STATIC DATA</div>
            </div>
            <div className="p-6 bg-slate-950 flex items-center justify-center min-h-[400px]">
                <img
                    src={`${IMG_BASE}/sequential_comparison_plot.png`}
                    alt="Sequential Model Comparison"
                    className="max-w-full rounded-xl"
                    onError={(e) => { e.target.src="https://placehold.co/600x400?text=Comparison+Plot+Not+Found&font=roboto"; }}
                />
            </div>
        </div>

        {/* BiLSTM Confusion Matrix */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl relative group">
            <div className="p-6 border-b border-slate-800 bg-slate-950/40 flex justify-between items-center text-right">
                <div className="text-[10px] font-bold text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-md">PRE-TRAINED</div>
                <div>
                    <h3 className="text-lg font-bold text-white">BiLSTM Performance</h3>
                    <p className="text-xs text-slate-500 mt-1">Classification breakdown for the Bi-directional LSTM architecture.</p>
                </div>
            </div>
            <div className="p-6 bg-slate-950 flex items-center justify-center min-h-[400px]">
                <img
                    src={`${IMG_BASE}/bilstm_cm.png`}
                    alt="BiLSTM Confusion Matrix"
                    className="max-w-full rounded-xl"
                    onError={(e) => { e.target.src="https://placehold.co/600x400?text=BiLSTM+CM+Not+Found&font=roboto"; }}
                />
            </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
        <div className="lg:col-span-2 space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 relative overflow-hidden group border-l-4 border-indigo-500 shadow-xl">
                 <h3 className="text-white font-bold text-xl mb-4">Architectural Rationale</h3>
                 <p className="text-slate-400 text-sm leading-relaxed mb-6">
                    While Simple RNNs suffer from vanishing gradients, <span className="text-white font-bold italic">LSTMs</span> and <span className="text-white font-bold italic">BiLSTMs</span> maintain long-term memory. Bi-directional models look at both past and future (within the window) to contextually understand pollutant spikes.
                 </p>
                 <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 bg-slate-950 rounded-2xl border border-slate-800 text-center">
                        <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">Window Size</p>
                        <p className="text-lg font-black text-indigo-400">24 Hours</p>
                    </div>
                    <div className="p-4 bg-slate-950 rounded-2xl border border-slate-800 text-center">
                        <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">Hidden Units</p>
                        <p className="text-lg font-black text-indigo-400">128 (x2 Layers)</p>
                    </div>
                 </div>
            </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl">
            <p className="text-indigo-400 text-[10px] font-black uppercase tracking-[0.2em] mb-6">Comparative Summary</p>
            <h4 className="text-white font-bold mb-4">Key Takeaways</h4>
            <div className="space-y-6">
                <div>
                  <div className="flex items-center gap-3 mb-2 text-rose-400">
                    <span className="text-xs font-bold uppercase tracking-widest">Simple RNN</span>
                  </div>
                  <p className="text-slate-400 text-[10px] leading-relaxed">
                    Fastest to train but struggles with dependencies over 6+ hours due to memory decay.
                  </p>
                </div>
                <div className="h-px bg-slate-800"></div>
                <div>
                  <div className="flex items-center gap-3 mb-2 text-blue-400">
                    <span className="text-xs font-bold uppercase tracking-widest">LSTM</span>
                  </div>
                  <p className="text-slate-400 text-[10px] leading-relaxed">
                    The gold standard for time-series; effectively captures persistent smog patterns.
                  </p>
                </div>
                <div className="h-px bg-slate-800"></div>
                <div>
                  <div className="flex items-center gap-3 mb-2 text-emerald-400">
                    <span className="text-xs font-bold uppercase tracking-widest">BiLSTM</span>
                  </div>
                  <p className="text-slate-400 text-[10px] leading-relaxed">
                    Highest accuracy by processing the sequence in both directions for richer feature extraction.
                  </p>
                </div>
            </div>
        </div>
      </div>

      {/* Original LSTM Visuals (Legacy) */}
      <div className="border-t border-slate-800 pt-12">
        <h2 className="text-xl font-bold text-white mb-8">Base LSTM Optimization</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-4">
                <p className="text-[10px] text-slate-500 mb-4 px-2">Convergence History</p>
                <img src={`${IMG_BASE}/improved_lstm_loss.png`} alt="LSTM Loss" className="w-full rounded-xl" />
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-4">
                <p className="text-[10px] text-slate-500 mb-4 px-2">State Confusion Matrix</p>
                <img src={`${IMG_BASE}/improved_lstm_cm.png`} alt="LSTM CM" className="w-full rounded-xl" />
            </div>
        </div>
      </div>
    </div>
  );
};

export default LSTMPage;
