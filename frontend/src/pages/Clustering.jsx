import React, { useState, useEffect } from 'react';
import api from '../services/api';

const IMG_BASE = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/images`;

const Clustering = () => {
  const [data, setData] = useState(null);
  const [loadingDend, setLoadingDend] = useState(false);
  const [dendUrl, setDendUrl] = useState(null);

  useEffect(() => {
    api.get('/clustering_data').then(res => {
      setData(res.data);
    }).catch(err => console.error(err));
  }, []);

  const generateDendrogram = () => {
    setLoadingDend(true);
    api.get('/generate_dendrogram').then(res => {
      setDendUrl(`${IMG_BASE}/${res.data.file}?t=${new Date().getTime()}`);
      setLoadingDend(false);
    }).catch(err => {
      console.error(err);
      setLoadingDend(false);
    });
  };

  const scores = data?.silhouette_scores || {};

  return (
    <div className="pb-20">
      <div className="flex justify-between items-center mb-10">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Unsupervised Pattern Recognition</h1>
          <p className="text-slate-400 mt-2 max-w-2xl">
            Identifying underlying pollutant regimes through latent space analysis. We utilize dimensionality reduction (PCA) and hierarchical clustering to segment city profiles.
          </p>
        </div>
        <button 
          onClick={generateDendrogram}
          disabled={loadingDend}
          className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-xl font-bold transition-all shadow-lg shadow-indigo-600/20 active:scale-95 disabled:opacity-50"
        >
          {loadingDend ? 'Generating Dendrogram...' : 'Compute Hierarchical Tree'}
        </button>
      </div>

      {/* Silhouette Scores Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        {[
          ['KMeans', '#6366f1', 'Centroid-based partitioning for circular clusters.'], 
          ['Hierarchical', '#14b8a6', 'Tree-based mapping of nested pollutant relationships.'], 
          ['DBSCAN', '#f59e0b', 'Density-based noise filtering for irregular shapes.']
        ].map(([algo, color, desc]) => (
          <div key={algo} className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-xl">
            <p className="text-slate-500 text-[10px] uppercase font-black tracking-widest">{algo} Efficiency</p>
            <h2 className="text-4xl font-black mt-2 mb-4" style={{ color }}>{scores[algo] ?? '...'}</h2>
            <p className="text-slate-400 text-xs leading-relaxed">{desc}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        {/* PCA Plot */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
            <div className="p-6 border-b border-slate-800 bg-slate-950/40">
                <h3 className="text-lg font-bold text-white">PCA Latent Space Projection</h3>
                <p className="text-xs text-slate-500 mt-1">High-dimensional chemistry (12 features) reduced to 2 principal components.</p>
            </div>
            <div className="p-6 bg-slate-950 flex items-center justify-center min-h-[450px]">
                <img
                    src={`${IMG_BASE}/pca_clusters.png`}
                    alt="PCA Cluster Plot"
                    className="max-w-full rounded-xl hover:scale-105 transition-transform duration-700 pointer-events-none"
                    onError={(e) => { e.target.src="https://placehold.co/600x400?text=PCA+Plot+Pending&font=roboto"; }}
                />
            </div>
            <div className="p-6 bg-slate-900/50">
                <h4 className="text-white font-bold text-sm mb-2">Cluster Interpretations</h4>
                <div className="space-y-3">
                    <div className="flex gap-4">
                        <div className="w-1 h-8 bg-indigo-500 rounded-full shrink-0"></div>
                        <p className="text-xs text-slate-400 leading-relaxed">
                            <span className="text-white font-bold">Regime A (Urban Primary):</span> Characterized by high NO2 and PM2.5, typically peaking during commute hours in metropolitan zones.
                        </p>
                    </div>
                    <div className="flex gap-4">
                        <div className="w-1 h-8 bg-teal-500 rounded-full shrink-0"></div>
                        <p className="text-xs text-slate-400 leading-relaxed">
                            <span className="text-white font-bold">Regime B (Industrial Secondary):</span> High SO2 and CO concentrations from non-mobile point sources, showing less diurnal variance.
                        </p>
                    </div>
                </div>
            </div>
        </div>

        {/* Dendrogram Plot */}
        <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
            <div className="p-6 border-b border-slate-800 bg-slate-950/40">
                <h3 className="text-lg font-bold text-white">Hierarchical Dendrogram</h3>
                <p className="text-xs text-slate-500 mt-1">Agglomerative linkage evidence showing how pollutant groups merge scientifically.</p>
            </div>
            <div className="p-6 bg-slate-950 flex items-center justify-center min-h-[450px]">
                {dendUrl ? (
                    <img
                        src={dendUrl}
                        alt="Dendrogram"
                        className="max-w-full rounded-xl animate-in fade-in duration-700"
                    />
                ) : (
                    <div className="text-center p-12 border-2 border-dashed border-slate-800 rounded-3xl w-full">
                        <div className="w-12 h-12 bg-slate-900 rounded-full flex items-center justify-center mx-auto mb-4 border border-slate-800 text-slate-700">
                            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z"></path></svg>
                        </div>
                        <p className="text-xs text-slate-700 font-bold uppercase tracking-widest mb-4">Hierarchical Matrix Not Computed</p>
                        <button 
                            onClick={generateDendrogram}
                            className="text-xs text-indigo-400 hover:text-indigo-300 font-bold underline underline-offset-4"
                        >
                            Authorize Computation
                        </button>
                    </div>
                )}
            </div>
            <div className="p-6">
                 <h4 className="text-white font-bold text-sm mb-4">Methodology Note</h4>
                 <p className="text-xs text-slate-400 leading-relaxed bg-slate-950/50 p-4 rounded-xl border border-slate-800">
                    The dendrogram is computed using <span className="text-indigo-400 font-mono">Ward's method</span> on a normalized subset of the research dataset. It identifies at what distance threshold individual city AQI profiles become statistically indistinguishable.
                 </p>
            </div>
        </div>
      </div>
    </div>
  );
};

export default Clustering;
