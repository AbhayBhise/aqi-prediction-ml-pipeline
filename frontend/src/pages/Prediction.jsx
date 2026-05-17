import React, { useEffect, useMemo, useState } from 'react';
import api from '../services/api';

const featureList = [
  'PM2_5_ugm3',
  'PM10_ugm3',
  'NO2_ugm3',
  'CO_ugm3',
  'SO2_ugm3',
  'O3_ugm3',
  'Temp_2m_C',
  'Humidity_Percent',
  'Wind_Speed_10m_kmh',
];

const defaultValues = {
  PM2_5_ugm3: 45.2,
  PM10_ugm3: 88.5,
  NO2_ugm3: 20.1,
  CO_ugm3: 0.52,
  SO2_ugm3: 15.4,
  O3_ugm3: 30.2,
  Temp_2m_C: 28.5,
  Humidity_Percent: 62.0,
  Wind_Speed_10m_kmh: 11.8,
};

const horizons = [1, 4, 6, 12, 24];

const modelOptions = [
  { key: 'lstm', label: 'LSTM (Deep Learning)', mode: 'Sequential temporal pattern recognition' },
  { key: 'bilstm', label: 'Bi-LSTM (Deep Learning)', mode: 'Bi-directional long-term dependencies' },
  { key: 'hist_gradient_boosting', label: 'Hist Gradient Boosting', mode: 'Highest short-horizon accuracy' },
  { key: 'xgboost', label: 'XGBoost', mode: 'SOTA performance for tabular data' },
  { key: 'random_forest', label: 'Random Forest', mode: 'Better balanced category recall' },
  { key: 'logistic_regression', label: 'Logistic Regression', mode: 'Fast conservative baseline' },
];

const aqiColors = {
  Good: 'bg-emerald-500',
  Moderate: 'bg-yellow-500',
  Unhealthy_Sensitive: 'bg-orange-500',
  Unhealthy: 'bg-red-500',
  Very_Unhealthy: 'bg-purple-500',
  Hazardous: 'bg-rose-900',
};

const formatMetric = (value) => {
  if (value === undefined || value === null) return 'N/A';
  return `${(value * 100).toFixed(2)}%`;
};

const toLocalDateTimeValue = (date) => {
  const pad = (n) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:00`;
};

const Prediction = () => {
  const [cities, setCities] = useState([]);
  const [city, setCity] = useState('Delhi');
  const [horizon, setHorizon] = useState(1);
  const [model, setModel] = useState('hist_gradient_boosting');
  const [datetime, setDatetime] = useState(toLocalDateTimeValue(new Date()));
  const [formData, setFormData] = useState(defaultValues);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/eda_filters')
      .then((res) => {
        const nextCities = res.data?.cities || [];
        setCities(nextCities);
        if (nextCities.includes('Delhi')) setCity('Delhi');
        else if (nextCities.length) setCity(nextCities[0]);
      })
      .catch((err) => console.error('Failed to load city filters:', err));
  }, []);

  const selectedModel = useMemo(
    () => modelOptions.find((item) => item.key === model),
    [model]
  );

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleForecast = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    const features = featureList.reduce((acc, key) => {
      acc[key] = parseFloat(formData[key]);
      return acc;
    }, {});

    try {
      const res = await api.post('/forecast', {
        city,
        horizon_hours: horizon,
        model,
        datetime,
        features,
      });
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Forecast request failed');
    } finally {
      setLoading(false);
    }
  };

  const handleFetchLive = async () => {
    setFetchLoading(true);
    setError('');
    try {
      const res = await api.get(`/live_data?city=${city}`);
      const live = res.data?.features;
      if (live) {
        setFormData((prev) => ({
          ...prev,
          ...live
        }));
        // Update datetime to current local
        setDatetime(toLocalDateTimeValue(new Date()));
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch live data. Ensure API key is set in .env.');
    } finally {
      setFetchLoading(false);
    }
  };

  return (
    <div className="pb-20">
      <div className="flex justify-between items-start mb-10 gap-8">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Future AQI Forecast</h1>
          <p className="text-slate-400 mt-2">Predict AQI category 1h, 4h, 6h, 12h, or 24h ahead using saved forecast models.</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl px-5 py-3 text-right">
          <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest">Active Mode</p>
          <p className="text-sm text-indigo-300 font-bold">Chronological Forecast</p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-10 items-start">
        <div className="xl:col-span-4 bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl sticky top-8">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-2 h-6 bg-indigo-500 rounded-full"></div>
            <h3 className="text-lg font-bold text-white uppercase tracking-tight">Forecast Controls</h3>
          </div>

          <form onSubmit={handleForecast} className="space-y-6">
            <div>
              <label className="block text-[10px] uppercase font-black text-slate-500 mb-2 tracking-widest">City</label>
              <select
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
              >
                {cities.map((item) => <option key={item} value={item}>{item}</option>)}
              </select>
              <button
                type="button"
                onClick={handleFetchLive}
                disabled={fetchLoading}
                className="mt-3 w-full bg-slate-800 hover:bg-slate-700 text-indigo-300 text-[10px] font-black py-2 rounded-lg transition-all flex items-center justify-center gap-2 uppercase tracking-widest border border-indigo-500/20"
              >
                {fetchLoading ? (
                  <div className="w-3 h-3 border-2 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin"></div>
                ) : (
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                )}
                {fetchLoading ? 'Fetching...' : 'Fetch Live Parameters'}
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] uppercase font-black text-slate-500 mb-2 tracking-widest">Horizon</label>
                <select
                  value={horizon}
                  onChange={(e) => setHorizon(parseInt(e.target.value, 10))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                >
                  {horizons.map((item) => <option key={item} value={item}>{item} hours</option>)}
                </select>
              </div>
              <div>
                <label className="block text-[10px] uppercase font-black text-slate-500 mb-2 tracking-widest">Time</label>
                <input
                  type="datetime-local"
                  value={datetime}
                  onChange={(e) => setDatetime(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] uppercase font-black text-slate-500 mb-2 tracking-widest">Forecast Model</label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
              >
                {modelOptions.map((item) => <option key={item.key} value={item.key}>{item.label}</option>)}
              </select>
              <p className="mt-2 text-[10px] text-slate-500 font-bold uppercase tracking-wider">{selectedModel?.mode}</p>
            </div>

            <div className="grid grid-cols-2 gap-x-6 gap-y-5">
              {featureList.map((key) => (
                <div key={key} className="group">
                  <label className="block text-[10px] uppercase font-black text-slate-500 mb-2 tracking-widest group-focus-within:text-indigo-400 transition-colors">
                    {key.replace(/_/g, ' ').replace('ugm3', '(ug/m3)')}
                  </label>
                  <input
                    type="number"
                    name={key}
                    value={formData[key]}
                    onChange={handleChange}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all font-mono"
                    step="any"
                    required
                  />
                </div>
              ))}
            </div>

            {error && (
              <div className="bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded-2xl px-4 py-3 text-xs font-bold">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-4 bg-indigo-600 hover:bg-indigo-500 text-white font-black py-4 rounded-2xl transition-all shadow-xl shadow-indigo-600/30 active:scale-95 disabled:opacity-50 flex items-center justify-center gap-3 uppercase tracking-widest text-xs"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                  Forecasting...
                </>
              ) : 'Predict Future AQI'}
            </button>
          </form>
        </div>

        <div className="xl:col-span-8 space-y-8">
          {result ? (
            <>
              <div className="bg-slate-900 border border-slate-800 rounded-[2.5rem] p-10 relative overflow-hidden shadow-2xl">
                <div className="relative z-10">
                  <div className="flex flex-wrap items-center gap-4 mb-8">
                    <span className="bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] font-black px-3 py-1.5 rounded-full uppercase tracking-[0.2em]">
                      {result.horizon_hours}h Forecast
                    </span>
                    <span className="text-slate-500 text-[10px] font-mono font-bold">MODEL: {result.model_label}</span>
                    <span className="text-slate-500 text-[10px] font-mono font-bold">CITY: {result.city}</span>
                  </div>

                  <div className="flex flex-col md:flex-row md:items-end gap-8 mb-10">
                    <div>
                      <p className="text-slate-500 text-[10px] font-black uppercase tracking-widest mb-3">Predicted Future Category</p>
                      <h2 className={`text-7xl font-black tracking-tighter ${result.prediction === 'Hazardous' ? 'text-rose-600' : 'text-white'}`}>
                        {result.prediction.replace(/_/g, ' ')}
                      </h2>
                    </div>
                    <div className={`px-6 py-3 rounded-2xl mb-2 flex items-center gap-3 ${aqiColors[result.prediction] || 'bg-slate-700'} shadow-xl`}>
                      <div className="w-2.5 h-2.5 bg-white rounded-full animate-pulse shadow-[0_0_10px_white]"></div>
                      <span className="text-white text-xs font-black uppercase tracking-widest">
                        {result.confidence ? `${(result.confidence * 100).toFixed(1)}% confidence` : 'Forecast'}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-slate-950/50 border border-slate-800 rounded-2xl p-5">
                      <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest mb-2">Input Time</p>
                      <p className="text-sm text-slate-200 font-mono">{new Date(result.input_time).toLocaleString()}</p>
                    </div>
                    <div className="bg-slate-950/50 border border-slate-800 rounded-2xl p-5">
                      <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest mb-2">Forecast For</p>
                      <p className="text-sm text-slate-200 font-mono">{new Date(result.forecast_for).toLocaleString()}</p>
                    </div>
                    <div className="bg-slate-950/50 border border-slate-800 rounded-2xl p-5">
                      <p className="text-[10px] text-slate-500 font-black uppercase tracking-widest mb-2">Test Accuracy</p>
                      <p className="text-sm text-slate-200 font-mono">{formatMetric(result.metrics?.accuracy)}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-xl">
                  <h4 className="text-sm font-black text-white uppercase tracking-widest mb-6">Validation Profile</h4>
                  <div className="space-y-4">
                    {[
                      ['Macro F1', result.metrics?.macro_f1],
                      ['Balanced Accuracy', result.metrics?.balanced_accuracy],
                      ['Severe Recall', result.metrics?.severe_class_recall],
                      ['Weighted F1', result.metrics?.f1_weighted],
                    ].map(([label, value]) => (
                      <div key={label} className="flex justify-between items-center border-b border-slate-800/70 pb-3">
                        <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">{label}</span>
                        <span className="text-sm text-indigo-300 font-mono font-black">{formatMetric(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-xl">
                  <h4 className="text-sm font-black text-white uppercase tracking-widest mb-6">Class Probabilities</h4>
                  <div className="space-y-3">
                    {Object.entries(result.probabilities || {}).map(([label, value]) => (
                      <div key={label}>
                        <div className="flex justify-between mb-1">
                          <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">{label.replace(/_/g, ' ')}</span>
                          <span className="text-[10px] text-slate-500 font-mono">{(value * 100).toFixed(1)}%</span>
                        </div>
                        <div className="h-2 bg-slate-950 rounded-full overflow-hidden">
                          <div className={`${aqiColors[label] || 'bg-indigo-500'} h-full rounded-full`} style={{ width: `${Math.max(value * 100, 1)}%` }}></div>
                        </div>
                      </div>
                    ))}
                    {!result.probabilities && (
                      <p className="text-xs text-slate-500 font-bold">Probability output is not available for this model.</p>
                    )}
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center p-20 border-2 border-dashed border-slate-800 rounded-[3rem] text-slate-700 min-h-[600px]">
              <p className="font-black text-xs tracking-[0.3em] uppercase mb-2">Awaiting Forecast Request</p>
              <p className="text-[10px] text-slate-600 font-bold uppercase tracking-widest">Select horizon, model, city, and current readings</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Prediction;
