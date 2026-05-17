import React, { useState } from 'react';
import { MessageSquare, Send, X, Bot, User, Brain } from 'lucide-react';

const AIChatbot = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([
    { role: 'bot', content: "Hello! I'm your Agentic AQI Assistant. I can use real-time tools to analyze current pollution levels. How can I help you today?", thought_trace: [] }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
      const response = await fetch(`${apiBase}/api/chatbot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input }),
      });
      const data = await response.json();
      
      setMessages(prev => [...prev, { 
        role: 'bot', 
        content: data.response, 
        thought_trace: data.thought_trace 
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'bot', content: "Sorry, I'm having trouble connecting to my reasoning engine." }]);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      {/* Backdrop Close */}
      <div className="absolute inset-0" onClick={onClose}></div>
      
      <div className="relative bg-slate-900 border border-slate-700 w-full max-w-2xl h-[600px] rounded-3xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in duration-300">
        {/* Header */}
        <div className="bg-indigo-600 p-6 flex justify-between items-center">
          <div className="flex items-center gap-3 text-white">
            <div className="bg-white/20 p-2 rounded-xl">
                <Bot size={24} />
            </div>
            <div>
                <span className="font-bold text-lg block">Agentic AI Reasoning Engine</span>
                <span className="text-[10px] text-indigo-200 uppercase font-black tracking-widest">Unit IV: NLP & LLM Traceable</span>
            </div>
          </div>
          <button onClick={onClose} className="bg-white/10 hover:bg-white/20 p-2 rounded-xl text-white transition-all">
            <X size={20} />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-950/30">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] rounded-3xl p-4 shadow-lg ${
                msg.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-slate-800 text-slate-200 rounded-tl-none border border-slate-700'
              }`}>
                <div className="flex items-center gap-2 mb-2 opacity-50">
                    {msg.role === 'user' ? <User size={12}/> : <Bot size={12}/>}
                    <span className="text-[10px] font-bold uppercase tracking-widest">{msg.role}</span>
                </div>
                {msg.role === 'bot' && msg.thought_trace?.length > 0 && (
                  <div className="mb-4 p-3 bg-slate-900/80 rounded-2xl border border-indigo-500/20 text-[11px] text-indigo-300 font-mono leading-relaxed">
                    <div className="flex items-center gap-2 mb-2 border-b border-indigo-500/10 pb-1">
                      <Brain size={12} className="text-indigo-400" /> 
                      <span className="font-black">REASONING CHAIN (ReAct)</span>
                    </div>
                    {msg.thought_trace.map((t, ti) => (
                      <div key={ti} className="mb-1">
                        <span className="text-indigo-500 mr-2">[{ti+1}]</span> {t}
                      </div>
                    ))}
                  </div>
                )}
                <p className="text-sm leading-relaxed">{msg.content}</p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-slate-800 text-slate-400 px-6 py-3 rounded-full text-sm animate-pulse flex items-center gap-2 border border-slate-700">
                <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce"></div>
                Agent reasoning in progress...
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="p-6 bg-slate-900 border-t border-slate-800">
          <div className="flex gap-3 bg-slate-950 p-2 rounded-2xl border border-slate-800 focus-within:border-indigo-500/50 transition-colors">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask for AQI insights or health advice..."
              className="flex-1 bg-transparent px-4 py-2 text-sm text-white focus:outline-none"
            />
            <button
              onClick={handleSend}
              className="bg-indigo-600 hover:bg-indigo-500 text-white p-3 rounded-xl transition-all shadow-lg shadow-indigo-600/20 active:scale-95"
            >
              <Send size={20} />
            </button>
          </div>
          <p className="text-center text-[10px] text-slate-600 mt-4 uppercase font-bold tracking-tighter">
            Powered by Agentic LLM Engine & ReAct Framework
          </p>
        </div>
      </div>
    </div>
  );
};

export default AIChatbot;
