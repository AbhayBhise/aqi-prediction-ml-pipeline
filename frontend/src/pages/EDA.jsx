import React, { useState, useEffect, useCallback } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import api from '../services/api';

const IMG_BASE = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/images`;
const MONTH_NAMES = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

const METRIC_LABELS = {
  AQI_Score: 'AQI Score (0-5 mapped from category)',
  PM2_5_ugm3: 'PM2.5 (ug/m3)',
  PM10_ugm3: 'PM10 (ug/m3)',
  NO2_ugm3: 'NO2 (ug/m3)',
  SO2_ugm3: 'SO2 (ug/m3)',
  O3_ugm3: 'O3 (ug/m3)',
  CO_ugm3: 'CO (ug/m3)',
};

const formatNum = (value, digits = 2) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return 'N/A';
  return Number(value).toFixed(digits);
};

const ImageCard = ({ name, file, description, loading }) => {
  const [imgError, setImgError] = useState(false);

  useEffect(() => {
    setImgError(false);
  }, [file]);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden flex flex-col">
      <div className="p-4 border-b border-slate-800">
        <h3 className="text-base font-semibold text-white">{name}</h3>
        {description && <p className="text-xs text-slate-500 mt-1">{description}</p>}
      </div>
      <div className="flex-1 bg-slate-950 flex items-center justify-center min-h-[300px] p-3 relative">
        {loading ? (
          <div className="flex flex-col items-center gap-3 text-slate-600">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-xs">Generating plot...</span>
          </div>
        ) : imgError ? (
          <div className="flex flex-col items-center gap-2 text-slate-600 text-sm">
            <span className="text-3xl">Chart unavailable</span>
            <span className="text-xs">{file} not available</span>
          </div>
        ) : (
          <img
            key={file}
            src={`${IMG_BASE}/${file}`}
            alt={name}
            className="max-w-full max-h-[500px] object-contain rounded"
            onError={() => setImgError(true)}
          />
        )}
      </div>
    </div>
  );
};

const EDA = () => {
  const [filters, setFilters] = useState({ cities: [], months: [] });
  const [selectedCity, setSelectedCity] = useState('ALL');
  const [selectedMonth, setSelectedMonth] = useState('ALL');
  const [plots, setPlots] = useState([]);
  const [meta, setMeta] = useState({ filtered: false, city: 'All Cities', month: 'All Months' });
  const [loading, setLoading] = useState(false);
  const [filtersLoading, setFiltersLoading] = useState(true);

  const [rowCount, setRowCount] = useState(0);
  const [citywiseSummary, setCitywiseSummary] = useState([]);
  const [monthwiseSummary, setMonthwiseSummary] = useState([]);
  const [rawTimeSeries, setRawTimeSeries] = useState([]);
  const [seriesMetrics, setSeriesMetrics] = useState([]);
  const [selectedMetric, setSelectedMetric] = useState('AQI_Score');

  useEffect(() => {
    api.get('/eda_filters')
      .then(res => {
        setFilters(res.data);
        setFiltersLoading(false);
      })
      .catch(() => setFiltersLoading(false));
  }, []);

  const fetchPlots = useCallback(() => {
    setLoading(true);
    const params = {};
    if (selectedCity && selectedCity !== 'ALL') params.city = selectedCity;
    if (selectedMonth && selectedMonth !== 'ALL') params.month = selectedMonth;

    api.get('/eda_data', { params })
      .then(res => {
        setPlots(res.data.plots || []);
        setRowCount(res.data.row_count || 0);
        setCitywiseSummary(res.data.citywise_summary || []);
        setMonthwiseSummary(res.data.monthwise_summary || []);
        setRawTimeSeries(res.data.raw_time_series || []);

        const metrics = res.data.raw_time_series_metrics || [];
        setSeriesMetrics(metrics);
        setSelectedMetric(prev => (metrics.includes(prev) ? prev : (metrics[0] || 'AQI_Score')));

        setMeta({
          filtered: res.data.filtered,
          city: res.data.city,
          month: res.data.month,
        });
        setLoading(false);
      })
      .catch(err => {
        console.error('EDA fetch error:', err);
        setPlots([]);
        setRowCount(0);
        setCitywiseSummary([]);
        setMonthwiseSummary([]);
        setRawTimeSeries([]);
        setSeriesMetrics([]);
        setLoading(false);
      });
  }, [selectedCity, selectedMonth]);

  useEffect(() => {
    fetchPlots();
  }, [fetchPlots]);

  const handleReset = () => {
    setSelectedCity('ALL');
    setSelectedMonth('ALL');
  };

  const cityChartData = citywiseSummary.slice(0, 12);
  const monthChartData = monthwiseSummary.map(item => ({
    ...item,
    month_name: MONTH_NAMES[item.Month] || `M${item.Month}`,
  }));

  const monthLabel = meta.month !== 'All Months' ? MONTH_NAMES[parseInt(meta.month, 10)] : 'All Months';

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white">Exploratory Data Analysis</h1>
          <p className="text-slate-400 text-sm mt-1">
            {meta.filtered
              ? `Showing filtered data for ${meta.city} - ${monthLabel} (${rowCount.toLocaleString()} rows)`
              : `Full dataset - ${rowCount ? rowCount.toLocaleString() : '839,644'} rows across 29 Indian cities`}
          </p>
        </div>

        {meta.filtered && (
          <div className="flex items-center gap-2 bg-indigo-900/30 border border-indigo-500/30 rounded-lg px-4 py-2">
            <span className="text-indigo-300 text-sm font-medium">Filtered view active</span>
            <button
              onClick={handleReset}
              className="text-xs text-indigo-400 hover:text-white border border-indigo-700 rounded px-2 py-0.5 transition-colors"
            >
              Reset
            </button>
          </div>
        )}
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 mb-6">
        <h2 className="text-sm font-semibold text-slate-300 mb-4">Filter & Regenerate Plots</h2>
        <div className="flex flex-wrap gap-4 items-end">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-400">City</label>
            <select
              value={selectedCity}
              onChange={e => setSelectedCity(e.target.value)}
              disabled={filtersLoading}
              className="bg-slate-950 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 min-w-[160px] disabled:opacity-60"
            >
              <option value="ALL">All Cities</option>
              {filters.cities.map(c => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-400">Month</label>
            <select
              value={selectedMonth}
              onChange={e => setSelectedMonth(e.target.value)}
              disabled={filtersLoading}
              className="bg-slate-950 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 min-w-[140px] disabled:opacity-60"
            >
              <option value="ALL">All Months</option>
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(m => (
                <option key={m} value={m}>{MONTH_NAMES[m]}</option>
              ))}
            </select>
          </div>

          <div className="flex gap-3">
            <button
              onClick={fetchPlots}
              disabled={loading}
              className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              {loading ? 'Generating...' : 'Apply Filters'}
            </button>
            {meta.filtered && (
              <button
                onClick={handleReset}
                className="border border-slate-700 hover:border-slate-500 text-slate-300 hover:text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {meta.filtered && (
          <p className="text-xs text-slate-500 mt-3">
            Plots are generated on-demand and cached on the backend. Subsequent requests for the same filter combination load instantly.
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h3 className="text-base font-semibold text-white">Citywise AQI Summary</h3>
          <p className="text-xs text-slate-500 mt-1">Average mapped AQI score and record counts by city.</p>
          <div className="w-full h-[280px] mt-3">
            {cityChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={cityChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis dataKey="City" stroke="#94a3b8" interval={0} angle={-20} textAnchor="end" height={55} />
                  <YAxis stroke="#94a3b8" domain={[0, 5]} />
                  <Tooltip
                    cursor={{ fill: '#1e293b' }}
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }}
                    formatter={(value, key) => [
                      key === 'avg_aqi_score' ? formatNum(value, 3) : value,
                      key === 'avg_aqi_score' ? 'Avg AQI Score' : key,
                    ]}
                  />
                  <Bar dataKey="avg_aqi_score" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500 text-sm">No citywise data available.</div>
            )}
          </div>
          <div className="mt-3 max-h-[190px] overflow-auto border border-slate-800 rounded-lg">
            <table className="w-full text-xs">
              <thead className="bg-slate-950 text-slate-400 sticky top-0">
                <tr>
                  <th className="text-left px-3 py-2">City</th>
                  <th className="text-right px-3 py-2">Rows</th>
                  <th className="text-right px-3 py-2">Avg Score</th>
                  <th className="text-left px-3 py-2">Dominant</th>
                </tr>
              </thead>
              <tbody>
                {citywiseSummary.slice(0, 20).map(row => (
                  <tr key={row.City} className="border-t border-slate-800 text-slate-300">
                    <td className="px-3 py-1.5">{row.City}</td>
                    <td className="px-3 py-1.5 text-right">{Number(row.records || 0).toLocaleString()}</td>
                    <td className="px-3 py-1.5 text-right">{formatNum(row.avg_aqi_score, 3)}</td>
                    <td className="px-3 py-1.5">{row.dominant_category || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <h3 className="text-base font-semibold text-white">Monthwise AQI Summary</h3>
          <p className="text-xs text-slate-500 mt-1">Average mapped AQI score by month for the current filter scope.</p>
          <div className="w-full h-[280px] mt-3">
            {monthChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis dataKey="month_name" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" domain={[0, 5]} />
                  <Tooltip
                    cursor={{ fill: '#1e293b' }}
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }}
                    formatter={(value, key) => [
                      key === 'avg_aqi_score' ? formatNum(value, 3) : value,
                      key === 'avg_aqi_score' ? 'Avg AQI Score' : key,
                    ]}
                  />
                  <Bar dataKey="avg_aqi_score" fill="#14b8a6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-500 text-sm">No monthwise data available.</div>
            )}
          </div>
          <div className="grid grid-cols-3 gap-2 mt-3">
            {monthChartData.map(row => (
              <div key={row.Month} className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2">
                <p className="text-xs text-slate-400">{row.month_name}</p>
                <p className="text-sm text-white font-semibold">{formatNum(row.avg_aqi_score, 3)}</p>
                <p className="text-[11px] text-slate-500">{Number(row.records || 0).toLocaleString()} rows</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 mb-6">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h3 className="text-base font-semibold text-white">Raw Data Time Series</h3>
            <p className="text-xs text-slate-500 mt-1">Mean values over chronological timestamps for the selected filter.</p>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-400">Metric</label>
            <select
              value={selectedMetric}
              onChange={e => setSelectedMetric(e.target.value)}
              className="bg-slate-950 border border-slate-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500 min-w-[230px]"
            >
              {seriesMetrics.map(metric => (
                <option key={metric} value={metric}>{METRIC_LABELS[metric] || metric}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="w-full h-[360px] mt-4">
          {rawTimeSeries.length > 0 && seriesMetrics.includes(selectedMetric) ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={rawTimeSeries}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="timestamp" stroke="#94a3b8" minTickGap={35} />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }}
                  formatter={(value) => formatNum(value, 3)}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey={selectedMetric}
                  stroke={selectedMetric === 'AQI_Score' ? '#f59e0b' : '#6366f1'}
                  strokeWidth={2}
                  dot={false}
                  name={METRIC_LABELS[selectedMetric] || selectedMetric}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-500 text-sm">No raw time-series points available for this filter.</div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {plots.length > 0 ? (
          plots.map(plot => (
            <ImageCard
              key={plot.file}
              name={plot.name}
              file={plot.file}
              description={plot.description}
              loading={loading}
            />
          ))
        ) : (
          !loading && (
            <div className="xl:col-span-2 text-center py-16 text-slate-600">
              No plots available. Try applying different filters.
            </div>
          )
        )}

        {loading && plots.length === 0 && [1, 2, 3, 4].map(i => (
          <div key={i} className="bg-slate-900 border border-slate-800 rounded-xl min-h-[350px] flex items-center justify-center">
            <div className="flex flex-col items-center gap-3 text-slate-600">
              <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              <span className="text-xs">Generating plot {i}...</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EDA;

