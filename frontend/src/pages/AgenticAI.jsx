import React, { useState } from 'react';
import { Bot, Brain, Zap, Database, ArrowRight, MessageSquare, Send, User, Cpu, Shield, Activity } from 'lucide-react';

const TOOLS = [
  { name: 'get_current_aqi()', desc: 'Fetches live AQI from OpenWeatherMap API for any city', color: 'cyan', icon: Activity },
  { name: 'query_dataset()', desc: 'Queries the 842,160-row India AQI dataset in memory', color: 'indigo', icon: Database },
  { name: 'forecast_model()', desc: 'Runs LSTM/XGBoost forecast for 1h–24h horizons', color: 'emerald', icon: Brain },
  { name: 'cpcb_health_advice()', desc: 'Maps AQI category to CPCB health recommendations', color: 'amber', icon: Shield },
];

const REACT_STEPS = [
  { step: 'Thought', desc: 'What is the user asking? Which tool is needed?', color: 'indigo' },
  { step: 'Action', desc: 'Call the relevant tool with appropriate parameters', color: 'cyan' },
  { step: 'Observation', desc: 'Receive and interpret the tool result', color: 'amber' },
  { step: 'Output', desc: 'Formulate a grounded, factual response', color: 'emerald' },
];

const SUGGESTED = [
  "What is the current AQI in Delhi?",
  "Which model has the best accuracy?",
  "How many rows are in the dataset?",
  "Should I go outside today?",
  "Explain the Unit IV deep learning models",
  "What is PM2.5 and why is it dangerous?",
];

const AgenticAI = () => {
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      content: "Hello! I'm your custom AQI Project Data Agent. I use a ReAct reasoning loop with access to real-time AQI data, our 842k-row dataset, and all trained forecast models. What would you like to know?",
      thought_trace: ['Initialized with project context.', 'Connected to OpenWeatherMap and dataset tools.', 'Ready to assist.']
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (query = input) => {
    if (!query.trim()) return;
    const userMsg = { role: 'user', content: query };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
      const response = await fetch(`${apiBase}/api/chatbot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'bot', content: data.response, thought_trace: data.thought_trace }]);
    } catch {
      setMessages(prev => [...prev, { role: 'bot', content: "Connection error. Is the Flask backend running?" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pb-20">
      {/* Header */}
      <div className="mb-10">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-indigo-500/10 rounded-xl flex items-center justify-center border border-indigo-500/20">
            <Bot size={20} className="text-indigo-400" />
          </div>
          <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest bg-indigo-500/10 border border-indigo-500/20 px-3 py-1 rounded-full">
            Unit VI — Agentic AI &amp; ReAct Framework
          </span>
        </div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Agentic AI Reasoning Engine</h1>
        <p className="text-slate-400 mt-1">
          An autonomous custom AI agent, implementing the ReAct (Reasoning + Acting) protocol for grounded, tool-augmented AQI analysis.
        </p>
      </div>

      {/* ReAct Loop Architecture */}
      <div className="mb-12">
        <div className="flex items-center gap-4 mb-8">
          <h2 className="text-2xl font-bold text-white tracking-tight">ReAct Loop Architecture</h2>
          <div className="h-px flex-1 bg-slate-800" />
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Reason → Act → Observe</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {REACT_STEPS.map((s, i) => {
            const colors = {
              indigo: 'border-indigo-500/30 bg-indigo-500/5 text-indigo-400',
              cyan: 'border-cyan-500/30 bg-cyan-500/5 text-cyan-400',
              amber: 'border-amber-500/30 bg-amber-500/5 text-amber-400',
              emerald: 'border-emerald-500/30 bg-emerald-500/5 text-emerald-400',
            }[s.color];
            return (
              <div key={i} className={`border rounded-2xl p-5 ${colors} relative`}>
                {i < REACT_STEPS.length - 1 && (
                  <ArrowRight size={14} className="absolute -right-3 top-1/2 -translate-y-1/2 text-slate-600 z-10 hidden md:block" />
                )}
                <div className="text-2xl font-black mb-1">{i + 1}</div>
                <p className="text-sm font-black mb-1">{s.step}</p>
                <p className="text-xs text-slate-400 leading-relaxed">{s.desc}</p>
              </div>
            );
          })}
        </div>

        {/* Tools */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {TOOLS.map((t, i) => {
            const Icon = t.icon;
            const color = {
              cyan: 'border-cyan-500/20 bg-cyan-500/5 text-cyan-400',
              indigo: 'border-indigo-500/20 bg-indigo-500/5 text-indigo-400',
              emerald: 'border-emerald-500/20 bg-emerald-500/5 text-emerald-400',
              amber: 'border-amber-500/20 bg-amber-500/5 text-amber-400',
            }[t.color];
            return (
              <div key={i} className={`border rounded-xl p-4 flex items-start gap-4 ${color}`}>
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 bg-slate-900`}>
                  <Icon size={16} className={color.split(' ')[2]} />
                </div>
                <div>
                  <p className={`text-xs font-black font-mono mb-0.5 ${color.split(' ')[2]}`}>{t.name}</p>
                  <p className="text-xs text-slate-400">{t.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Chat Interface — Full Page */}
      <div className="mb-12">
        <div className="flex items-center gap-4 mb-8">
          <h2 className="text-2xl font-bold text-white tracking-tight">Live Agent Interface</h2>
          <div className="h-px flex-1 bg-slate-800" />
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest">Custom ReAct Engine · Live</span>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
          {/* Chat Header */}
          <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 p-5 flex items-center gap-4">
            <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
              <Bot size={22} className="text-white" />
            </div>
            <div>
              <p className="font-bold text-white text-base">AQI Project Data Agent</p>
              <p className="text-[10px] text-indigo-200 uppercase font-black tracking-widest">ReAct Framework · Unit VI · Syllabus Traceable</p>
            </div>
            <div className="ml-auto flex items-center gap-2 bg-white/10 px-3 py-1.5 rounded-full">
              <Cpu size={12} className="text-white" />
              <span className="text-[10px] text-white font-bold">Internal Agent SDK</span>
            </div>
          </div>

          {/* Messages */}
          <div className="h-[420px] overflow-y-auto p-6 space-y-6 bg-slate-950/30">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-3xl p-4 shadow-lg ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white rounded-tr-none'
                    : 'bg-slate-800 text-slate-200 rounded-tl-none border border-slate-700'
                }`}>
                  <div className="flex items-center gap-2 mb-2 opacity-50">
                    {msg.role === 'user' ? <User size={12} /> : <Bot size={12} />}
                    <span className="text-[10px] font-bold uppercase tracking-widest">{msg.role}</span>
                  </div>
                  {/* ReAct Trace */}
                  {msg.role === 'bot' && msg.thought_trace?.length > 0 && (
                    <div className="mb-3 p-3 bg-slate-900/80 rounded-2xl border border-indigo-500/20 text-[11px] text-indigo-300 font-mono leading-relaxed">
                      <div className="flex items-center gap-2 mb-2 border-b border-indigo-500/10 pb-1">
                        <Brain size={12} className="text-indigo-400" />
                        <span className="font-black">REASONING CHAIN (ReAct)</span>
                      </div>
                      {Array.isArray(msg.thought_trace) ? msg.thought_trace.map((t, ti) => (
                        <div key={ti} className="mb-1">
                          <span className="text-indigo-500 mr-2">[{ti + 1}]</span> {t}
                        </div>
                      )) : (
                        <div className="text-indigo-400/60 italic">Processing natural language trace...</div>
                      )}
                    </div>
                  )}
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-slate-800 text-slate-400 px-6 py-3 rounded-full text-sm flex items-center gap-3 border border-slate-700">
                  <div className="flex gap-1">
                    {[0, 1, 2].map(d => (
                      <div key={d} className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: `${d * 0.15}s` }} />
                    ))}
                  </div>
                  Agent reasoning in progress...
                </div>
              </div>
            )}
          </div>

          {/* Suggested Queries */}
          <div className="px-6 py-3 border-t border-slate-800 flex gap-2 overflow-x-auto">
            {SUGGESTED.map((q, i) => (
              <button
                key={i}
                onClick={() => handleSend(q)}
                className="text-[10px] font-bold text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-3 py-1.5 rounded-full whitespace-nowrap hover:bg-indigo-500/20 transition-colors uppercase tracking-wide"
              >
                {q}
              </button>
            ))}
          </div>

          {/* Input */}
          <div className="p-5 bg-slate-900 border-t border-slate-800">
            <div className="flex gap-3 bg-slate-950 p-2 rounded-2xl border border-slate-800 focus-within:border-indigo-500/50 transition-colors">
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                placeholder="Ask about AQI, models, health advice, or the dataset..."
                className="flex-1 bg-transparent px-4 py-2 text-sm text-white focus:outline-none"
              />
              <button
                onClick={() => handleSend()}
                className="bg-indigo-600 hover:bg-indigo-500 text-white p-3 rounded-xl transition-all shadow-lg shadow-indigo-600/20 active:scale-95 disabled:opacity-50"
                disabled={loading || !input.trim()}
              >
                <Send size={18} />
              </button>
            </div>
            <p className="text-center text-[10px] text-slate-600 mt-3 uppercase font-bold tracking-tighter">
              Powered by Custom AQI Engine · Secured & Rate Limited
            </p>
          </div>
        </div>
      </div>

      {/* Technical Summary */}
      <div className="bg-gradient-to-r from-indigo-500/5 to-purple-500/5 border border-indigo-500/20 rounded-3xl p-8">
        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <MessageSquare size={18} className="text-indigo-400" /> Technical Implementation
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
          <div>
            <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-2">LLM Backend</p>
            <ul className="space-y-1 text-slate-400 text-xs">
              <li>• Custom AI Reasoning Engine</li>
              <li>• Custom Python SDK integration</li>
              <li>• Structured JSON output (thought_trace + response)</li>
              <li>• Rate limiting: 4 req/min (free tier)</li>
            </ul>
          </div>
          <div>
            <p className="text-[10px] font-black text-emerald-400 uppercase tracking-widest mb-2">Agent Tools</p>
            <ul className="space-y-1 text-slate-400 text-xs">
              <li>• Live AQI via OpenWeatherMap API</li>
              <li>• In-memory 842k-row dataset access</li>
              <li>• CPCB breakpoint health mapping</li>
              <li>• Project metrics &amp; syllabus grounding</li>
            </ul>
          </div>
          <div>
            <p className="text-[10px] font-black text-amber-400 uppercase tracking-widest mb-2">ReAct Protocol</p>
            <ul className="space-y-1 text-slate-400 text-xs">
              <li>• Thought → Action → Observation loop</li>
              <li>• Thought trace visible in UI (transparency)</li>
              <li>• Graceful fallback on quota exhaustion</li>
              <li>• Safety filter integration</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgenticAI;
