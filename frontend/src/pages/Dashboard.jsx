import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../services/api';

const Dashboard = () => {
  const [data, setData] = useState([]);

  useEffect(() => {
    api.get('/eda_data').then(res => {
      setData(res.data || []);
    }).catch(err => {
      console.error(err);
      setData([]);
    });
  }, []);

  const chartData = (data && data.aqi_distribution) ? Object.keys(data.aqi_distribution).map(key => ({
    name: key,
    count: data.aqi_distribution[key]
  })) : [];

  return (
    <div>
      <h1 className="text-3xl font-bold text-white mb-8">Dashboard Overview</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <p className="text-slate-400 text-sm font-medium">Dataset Rows</p>
          <h2 className="text-3xl font-bold text-white mt-2">842,160</h2>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <p className="text-slate-400 text-sm font-medium">Features</p>
          <h2 className="text-3xl font-bold text-white mt-2">71</h2>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <p className="text-slate-400 text-sm font-medium">ML Models Trained</p>
          <h2 className="text-3xl font-bold text-indigo-400 mt-2">10</h2>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-6">Aggregate AQI Category Distribution</h3>
        <div className="w-full h-[300px]">
          {chartData && chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip cursor={{fill: '#1e293b'}} contentStyle={{backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff'}} />
                <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-500">
              Loading distribution data...
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
