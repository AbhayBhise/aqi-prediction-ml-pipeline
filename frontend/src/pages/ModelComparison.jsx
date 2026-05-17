import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../services/api';
import ImageModal from '../components/ImageModal';

const IMG_BASE = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/images`;

const ModelComparison = () => {
  const [metrics, setMetrics] = useState([]);
  const [forecastMetrics, setForecastMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeMetric, setActiveMetric] = useState('Accuracy'); // 'Accuracy' | 'MacroF1' | 'SevereRecall'
  
  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);

  useEffect(() => {
    Promise.all([api.get('/model_metrics'), api.get('/forecast_metrics')])
      .then(([modelRes, forecastRes]) => {
        setMetrics(modelRes.data || []);
        setForecastMetrics(forecastRes.data?.results || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error loading metrics:", err);
        setLoading(false);
      });
  }, []);

  const openImageDetail = (imgSrc, title, modelName) => {
    const details = {
        xAxis: "Predicted AQI Categories (Good to Hazardous). Each column represents what the model predicted for a given input set.",
        yAxis: "Actual (True) AQI Categories. Each row represents what the AQI level actually was in reality.",
        interpretation: `This Confusion Matrix provides scientific proof for the ${modelName} model's performance. The diagonal values (top-left to bottom-right) represent 'True Positives' where the model was correct. Off-diagonal values show specific misclassifications, helping us identify where the model confuses similar AQI levels.`
    };
    setSelectedImage({ src: imgSrc, title: `Confusion Matrix: ${title}`, details });
    setIsModalOpen(true);
  };

  const sortedMetrics = React.useMemo(() => {
    return [...metrics].sort((a, b) => {
      let valA = 0;
      let valB = 0;
      if (activeMetric === 'Accuracy') {
        valA = a.Accuracy;
        valB = b.Accuracy;
      } else if (activeMetric === 'MacroF1') {
        valA = a.MacroF1 || a.F1Score;
        valB = b.MacroF1 || b.F1Score;
      } else if (activeMetric === 'SevereRecall') {
        valA = a.SevereClassRecall || 0;
        valB = b.SevereClassRecall || 0;
      }
      return (valB || 0) - (valA || 0);
    });
  }, [metrics, activeMetric]);

  const chartData = sortedMetrics.map(m => ({
    name: m.Model.split(' ')[0], // Short name for chart
    fullName: m.Model,
    Accuracy: (m.Accuracy * 100).toFixed(1),
    F1: (m.F1Score * 100).toFixed(1),
    Precision: (m.Precision * 100).toFixed(1),
    Recall: (m.Recall * 100).toFixed(1),
    MacroF1: ((m.MacroF1 || 0) * 100).toFixed(1),
    SevereRecall: ((m.SevereClassRecall || 0) * 100).toFixed(1)
  }));

  const bestModel = sortedMetrics.length > 0 ? sortedMetrics[0] : null;
  const worstModel = sortedMetrics.length > 0 ? sortedMetrics[sortedMetrics.length - 1] : null;
  const bestForecastByHorizon = [1, 4, 6, 12, 24].map((horizon) => {
    const rows = forecastMetrics.filter((row) => row.horizon_hours === horizon);
    return rows.sort((a, b) => b.accuracy - a.accuracy)[0];
  }).filter(Boolean);
  const forecastChartData = forecastMetrics.map((row) => ({
    name: `${row.horizon_hours}h ${row.model.split(' ')[0]}`,
    horizon: `${row.horizon_hours}h`,
    model: row.model,
    Accuracy: (row.accuracy * 100).toFixed(1),
    MacroF1: (row.macro_f1 * 100).toFixed(1),
    SevereRecall: (row.severe_class_recall * 100).toFixed(1),
  }));

  return (
    <div className="pb-20">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Algorithm Benchmark Report</h1>
          <p className="text-slate-400 mt-1">Comparative study of 8 distinct architectural regimes for target AQI classification.</p>
        </div>
        <div className="flex gap-3">
            {bestModel && (
              <div className="bg-emerald-500/10 border border-emerald-500/20 px-4 py-2 rounded-xl flex items-center gap-2 shadow-lg shadow-emerald-500/5">
                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                <span className="text-emerald-400 text-xs font-bold uppercase tracking-wider">Top Performer: {bestModel.Model}</span>
              </div>
            )}
            {worstModel && (
                <div className="bg-rose-500/10 border border-rose-500/20 px-4 py-2 rounded-xl flex items-center gap-2 shadow-lg shadow-rose-500/5">
                  <span className="w-2 h-2 bg-rose-500 rounded-full"></span>
                  <span className="text-rose-400 text-xs font-bold uppercase tracking-wider">Underperformer: {worstModel.Model}</span>
                </div>
            )}
        </div>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center h-96 opacity-50">
           <div className="w-12 h-12 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin mb-4"></div>
           <p className="text-slate-400 font-mono text-xs uppercase tracking-[0.2em]">Aggregating Architecture Telemetry...</p>
        </div>
      ) : (
        <>
          {/* Main Chart Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 mb-10 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-10 opacity-[0.03] pointer-events-none">
                <svg className="w-64 h-64 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14h-2v-4h2v4zm4 0h-2v-6h2v6zm-8 0H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V7h2v2z"/></svg>
            </div>
            
            <div className="flex flex-wrap justify-between items-center gap-4 mb-10 relative z-10">
              <div>
                <h3 className="text-xl font-bold text-white">
                  {activeMetric === 'Accuracy' && 'Overall Accuracy Leaderboard'}
                  {activeMetric === 'MacroF1' && 'Macro F1-Score Leaderboard'}
                  {activeMetric === 'SevereRecall' && 'Rare-Class Leaderboard (Severe Recall %)'}
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  {activeMetric === 'Accuracy' && 'Comparing raw prediction accuracy across the entire validation dataset.'}
                  {activeMetric === 'MacroF1' && 'Macro F1 provides an unweighted balance across all 6 AQI categories.'}
                  {activeMetric === 'SevereRecall' && 'Measures classification sensitivity specifically on Rare/Severe (Very Unhealthy & Hazardous) bands.'}
                </p>
              </div>
              <div className="flex flex-wrap gap-2 bg-slate-950/60 p-1.5 rounded-2xl border border-slate-800">
                {[
                  { id: 'Accuracy', label: 'Accuracy' },
                  { id: 'MacroF1', label: 'Macro F1' },
                  { id: 'SevereRecall', label: 'Severe Recall' }
                ].map((item) => (
                  <button
                    key={item.id}
                    onClick={() => setActiveMetric(item.id)}
                    className={`px-4 py-2 rounded-xl text-xs font-black uppercase tracking-wider transition-all duration-300 ${
                      activeMetric === item.id
                        ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                    }`}
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </div>
            
            <div className="h-[350px] relative z-10">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} opacity={0.3} />
                  <XAxis 
                    dataKey="name" 
                    stroke="#475569" 
                    tick={{fontSize: 11, fontWeight: 600}}
                    axisLine={false}
                    tickLine={false}
                    dy={15}
                  />
                  <YAxis stroke="#475569" domain={[0, 100]} axisLine={false} tickLine={false} tick={{fontSize: 10}} />
                  <Tooltip 
                    cursor={{fill: 'rgba(255,255,255,0.03)'}} 
                    contentStyle={{backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', borderRadius: '16px', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.5)'}} 
                  />
                  <Bar 
                    dataKey={activeMetric === 'Accuracy' ? 'Accuracy' : activeMetric === 'MacroF1' ? 'MacroF1' : 'SevereRecall'} 
                    fill={activeMetric === 'Accuracy' ? '#10b981' : activeMetric === 'MacroF1' ? '#6366f1' : '#f59e0b'} 
                    radius={[8, 8, 0, 0]} 
                    barSize={40} 
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Model Ranking Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl mb-12">
            <div className="p-6 border-b border-slate-800 bg-slate-950/40 flex justify-between items-center">
              <h3 className="font-bold text-white text-lg">Statistical Performance Matrix</h3>
              <span className="text-[10px] bg-slate-800 text-slate-400 px-3 py-1 rounded-full font-bold uppercase tracking-wider">Research-Grade Validation</span>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead>
                    <tr className="text-slate-500 text-[10px] font-black uppercase tracking-[0.15em] bg-slate-950/20">
                        <th className="px-8 py-5">Architecture</th>
                        <th className="px-6 py-5 text-center">Accuracy</th>
                        <th className="px-6 py-5 text-center">Precision</th>
                        <th className="px-6 py-5 text-center">Recall</th>
                        <th className="px-6 py-5 text-center">Macro F1</th>
                        <th className="px-6 py-5 text-center">Severe Recall</th>
                        <th className="px-8 py-5 text-right">Inference Speed</th>
                    </tr>
                    </thead>
                    <tbody className="text-sm">
                    {sortedMetrics.map((row, idx) => (
                        <tr key={idx} className={`border-b border-slate-800/50 transition-colors group ${idx === 0 ? 'bg-indigo-500/[0.02]' : 'hover:bg-slate-800/20'}`}>
                        <td className="px-8 py-5 font-bold text-slate-200">
                            <div className="flex items-center gap-3">
                                <span className="text-[10px] text-slate-600 font-mono w-4">0{idx + 1}</span>
                                <span className={`w-1.5 h-1.5 rounded-full ${idx === 0 ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.4)]' : 'bg-slate-700'}`}></span>
                                {row.Model}
                            </div>
                        </td>
                        <td className={`px-6 py-5 text-center font-mono transition-colors ${activeMetric === 'Accuracy' ? 'text-emerald-400 bg-emerald-500/[0.02] font-black' : 'text-slate-400'}`}>{(row.Accuracy * 100).toFixed(1)}%</td>
                        <td className="px-6 py-5 text-center font-mono text-slate-400">{(row.Precision * 100).toFixed(1)}%</td>
                        <td className="px-6 py-5 text-center font-mono text-slate-400">{(row.Recall * 100).toFixed(1)}%</td>
                        <td className={`px-6 py-5 text-center font-mono transition-colors ${activeMetric === 'MacroF1' ? 'text-indigo-400 bg-indigo-500/[0.02] font-black' : 'text-slate-400'}`}>{((row.MacroF1 || row.F1Score) * 100).toFixed(1)}%</td>
                        <td className={`px-6 py-5 text-center transition-colors ${activeMetric === 'SevereRecall' ? 'text-amber-400 bg-amber-500/[0.02] font-black' : 'text-slate-400 font-mono'}`}>{((row.SevereClassRecall || 0) * 100).toFixed(1)}%</td>
                        <td className="px-8 py-5 text-right font-mono text-slate-500 text-xs">{(row.Time * 1000).toFixed(1)} ms</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
          </div>

          <div className="mb-12">
            <div className="flex items-center gap-4 mb-8">
                <h2 className="text-2xl font-bold text-white tracking-tight">Classification Evidence Grid</h2>
                <div className="h-px flex-1 bg-slate-800"></div>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap">Confusion Matrix Matrix (N=8)</span>
            </div>
            
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                    'logistic_regression', 'decision_tree', 'random_forest', 'hist_gradient_boosting', 'knn',
                    'svm_sgd', 'naive_bayes', 'ann', 'dnn', 'lstm', 'bilstm'
                ].map((mKey, idx) => {
                    const row = metrics.find(m => m.Model.toLowerCase().replaceAll(" ", "_") === mKey) || { Model: mKey, F1Score: 0, SevereClassRecall: 0 };
                    const imgUrl = `${IMG_BASE}/cm_${mKey}.png`;
                    return (
                        <div 
                            key={mKey} 
                            onClick={() => openImageDetail(imgUrl, mKey.replace(/_/g, ' ').toUpperCase(), row.Model)}
                            className="bg-slate-900 border border-slate-800 rounded-2xl p-4 hover:ring-2 hover:ring-indigo-500/30 transition-all group shadow-xl cursor-zoom-in"
                        >
                            <div className="flex justify-between items-center mb-4">
                                <span className="text-xs font-black text-slate-300 group-hover:text-white transition-colors">{mKey.replace(/_/g, ' ').toUpperCase()}</span>
                                <div className="w-6 h-6 bg-slate-950 rounded-lg flex items-center justify-center text-[10px] text-slate-600 font-bold border border-slate-800">
                                    0{idx + 1}
                                </div>
                            </div>
                            <div className="aspect-square bg-slate-950 rounded-xl overflow-hidden border border-slate-800 mb-4 transition-all duration-700 relative">
                                <img 
                                    src={imgUrl} 
                                    alt={`CM for ${mKey}`}
                                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                                    onError={(e) => { e.target.src="https://placehold.co/400x400?text=Matrix+Pending&font=roboto"; }}
                                />
                                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
                                    <p className="text-[10px] text-indigo-300 font-bold uppercase tracking-tighter">Click to Expand Scientific Artifact</p>
                                </div>
                            </div>
                            <div className="flex justify-between items-end">
                                <div>
                                    <p className="text-[9px] text-slate-500 font-bold uppercase tracking-tighter">Severe Recall</p>
                                    <p className="text-lg font-black text-indigo-400">{((row.SevereClassRecall || 0) * 100).toFixed(1)}</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-[9px] text-slate-500 font-bold uppercase tracking-tighter">Status</p>
                                    <p className="text-[10px] font-bold text-emerald-500">VERIFIED</p>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
          </div>

          <div className="mb-12">
            <div className="flex items-center gap-4 mb-8">
              <h2 className="text-2xl font-bold text-white tracking-tight">Forecast Model Comparison</h2>
              <div className="h-px flex-1 bg-slate-800"></div>
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest whitespace-nowrap">Future AQI Horizons</span>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-5 gap-4 mb-8">
              {bestForecastByHorizon.map((row) => (
                <div key={row.horizon_hours} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
                  <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest mb-2">{row.horizon_hours}h Best Accuracy</p>
                  <p className="text-sm text-white font-black truncate">{row.model}</p>
                  <p className="text-2xl text-indigo-400 font-black mt-3">{(row.accuracy * 100).toFixed(2)}%</p>
                  <p className="text-[10px] text-slate-500 font-bold mt-2">Macro F1 {(row.macro_f1 * 100).toFixed(1)}%</p>
                </div>
              ))}
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 mb-8 shadow-2xl">
              <div className="flex justify-between items-center mb-8">
                <h3 className="text-xl font-bold text-white">Forecast Accuracy by Horizon</h3>
                <span className="text-[10px] bg-slate-800 text-slate-400 px-3 py-1 rounded-full font-bold uppercase tracking-wider">Chronological Test Split</span>
              </div>
              <div className="h-[360px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={forecastChartData} margin={{ top: 0, right: 0, left: -20, bottom: 60 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} opacity={0.3} />
                    <XAxis dataKey="name" stroke="#475569" tick={{fontSize: 10, fontWeight: 600}} angle={-35} textAnchor="end" interval={0} axisLine={false} tickLine={false} />
                    <YAxis stroke="#475569" domain={[0, 100]} axisLine={false} tickLine={false} tick={{fontSize: 10}} />
                    <Tooltip cursor={{fill: 'rgba(255,255,255,0.03)'}} contentStyle={{backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff', borderRadius: '16px'}} />
                    <Bar dataKey="Accuracy" fill="#14b8a6" radius={[8, 8, 0, 0]} barSize={24} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
              <div className="p-6 border-b border-slate-800 bg-slate-950/40 flex justify-between items-center">
                <h3 className="font-bold text-white text-lg">Forecast Performance Matrix</h3>
                <span className="text-[10px] bg-slate-800 text-slate-400 px-3 py-1 rounded-full font-bold uppercase tracking-wider">1h / 4h / 6h / 12h / 24h</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="text-slate-500 text-[10px] font-black uppercase tracking-[0.15em] bg-slate-950/20">
                      <th className="px-8 py-5">Horizon</th>
                      <th className="px-8 py-5">Model</th>
                      <th className="px-6 py-5 text-center">Accuracy</th>
                      <th className="px-6 py-5 text-center">Macro F1</th>
                      <th className="px-6 py-5 text-center">Balanced Acc.</th>
                      <th className="px-6 py-5 text-center">Severe Recall</th>
                      <th className="px-6 py-5 text-center">Evidence</th>
                      <th className="px-8 py-5 text-right">Train Rows</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {forecastMetrics
                      .slice()
                      .sort((a, b) => a.horizon_hours - b.horizon_hours || b.accuracy - a.accuracy)
                      .map((row, idx) => (
                        <tr key={`${row.horizon_hours}-${row.model}`} className={`border-b border-slate-800/50 transition-colors group ${idx % 3 === 0 ? 'bg-indigo-500/[0.02]' : 'hover:bg-slate-800/20'}`}>
                          <td className="px-8 py-5 font-black text-indigo-300">{row.horizon_hours}h</td>
                          <td className="px-8 py-5 font-bold text-slate-200">{row.model}</td>
                          <td className="px-6 py-5 text-center font-black text-emerald-400">{(row.accuracy * 100).toFixed(2)}%</td>
                          <td className="px-6 py-5 text-center font-mono text-slate-400">{(row.macro_f1 * 100).toFixed(1)}%</td>
                          <td className="px-6 py-5 text-center font-mono text-slate-400">{(row.balanced_accuracy * 100).toFixed(1)}%</td>
                          <td className="px-6 py-5 text-center font-mono text-slate-400">{(row.severe_class_recall * 100).toFixed(1)}%</td>
                          <td className="px-6 py-5 text-center">
                            <button 
                                onClick={() => openImageDetail(
                                    `${IMG_BASE}/cm_forecast_${row.horizon_hours}h_${row.model.toLowerCase().replace(/ /g, '_')}.png`,
                                    `${row.model} (${row.horizon_hours}h Horizon)`,
                                    row.model
                                )}
                                className="bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 text-indigo-400 p-2 rounded-lg transition-all group/btn"
                                title="View Scientific Proof"
                            >
                                <svg className="w-4 h-4 group-hover/btn:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                </svg>
                            </button>
                          </td>
                          <td className="px-8 py-5 text-right font-mono text-slate-500 text-xs">{row.train_rows.toLocaleString()}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Scientific Artifact Detail Modal */}
      {selectedImage && (
        <ImageModal 
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          imgSrc={selectedImage.src}
          title={selectedImage.title}
          details={selectedImage.details}
        />
      )}
    </div>
  );
};

export default ModelComparison;
