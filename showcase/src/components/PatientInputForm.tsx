'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader } from 'lucide-react';

interface PatientInputFormProps {
  onSubmit: (text: string) => void;
  loading: boolean;
}

const EXAMPLE_CASES = [
  {
    title: '🫀 Cardiology Case',
    text: 'Chief complaint: chest pain radiating to left arm. HR 110, BP 130/85, Temp 39.2C. Medication: aspirin.',
  },
  {
    title: '🫁 Respiratory Case',
    text: 'Shortness of breath, wheezing, asthma exacerbation. HR 95, BP 118/76, Temp 38.5C. Triggers: allergens.',
  },
  {
    title: '🧠 Neurology Case',
    text: 'Slurred speech, left-side weakness, face drooping. Time last known well: 2 hours ago. HR 88, BP 145/92.',
  },
  {
    title: '🚑 Trauma Case',
    text: 'Fall from height, visible laceration on head, deformity noted. HR 112, BP 125/78, Temp 37.1C.',
  },
];

export function PatientInputForm({ onSubmit, loading }: PatientInputFormProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (text: string) => {
    if (text.trim()) {
      onSubmit(text);
      setInput('');
    }
  };

  return (
    <motion.div
      className="space-y-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Main Input - Enhanced */}
      <div className="space-y-3">
        <label className="block text-sm font-bold text-slate-200 uppercase tracking-wide">
          🏥 Clinical Notes
        </label>
        <div className="relative group">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-cyan-600/20 rounded-xl blur opacity-0 group-focus-within:opacity-100 transition duration-500" />
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.ctrlKey && e.key === 'Enter') {
                handleSubmit(input);
              }
            }}
            placeholder="Enter clinical notes or patient narrative..."
            className="relative w-full h-32 px-5 py-4 bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 group-focus-within:border-blue-500/50 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/30 transition-all duration-300 resize-none backdrop-blur-sm shadow-lg"
            disabled={loading}
          />
        </div>
        <motion.p className="text-xs text-slate-400 font-medium flex items-center gap-2">
          <span className="inline-block">💡</span> Tip: Use <span className="px-2 py-0.5 bg-slate-700/50 rounded text-blue-300 font-mono">Ctrl+Enter</span> to submit
        </motion.p>
      </div>

      {/* Action Button - Enhanced */}
      <motion.div className="relative group">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/40 to-cyan-600/40 rounded-lg blur opacity-75 group-hover:opacity-100 transition duration-500" />
        <motion.button
          onClick={() => handleSubmit(input)}
          disabled={loading || !input.trim()}
          className="relative w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold rounded-lg transition-all flex items-center justify-center gap-2 shadow-lg"
          whileHover={{ scale: loading || !input.trim() ? 1 : 1.05 }}
          whileTap={{ scale: loading || !input.trim() ? 1 : 0.95 }}
        >
          {loading ? (
            <>
              <Loader className="h-5 w-5 animate-spin" />
              <span>Processing...</span>
            </>
          ) : (
            <>
              <Send className="h-5 w-5" />
              <span>Process Clinical Case</span>
            </>
          )}
        </motion.button>
      </motion.div>

      {/* Example Cases - Enhanced */}
      <div className="space-y-3">
        <p className="text-xs font-bold text-slate-300 uppercase tracking-wider">📋 Example Clinical Cases:</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {EXAMPLE_CASES.map((example, idx) => {
            const colors = [
              { gradient: 'from-red-900/30 to-red-800/30', border: 'border-red-700/50', hover: 'hover:border-red-600/80', bg: 'group-hover:from-red-900/50 group-hover:to-red-800/50' },
              { gradient: 'from-emerald-900/30 to-emerald-800/30', border: 'border-emerald-700/50', hover: 'hover:border-emerald-600/80', bg: 'group-hover:from-emerald-900/50 group-hover:to-emerald-800/50' },
              { gradient: 'from-purple-900/30 to-purple-800/30', border: 'border-purple-700/50', hover: 'hover:border-purple-600/80', bg: 'group-hover:from-purple-900/50 group-hover:to-purple-800/50' },
              { gradient: 'from-orange-900/30 to-orange-800/30', border: 'border-orange-700/50', hover: 'hover:border-orange-600/80', bg: 'group-hover:from-orange-900/50 group-hover:to-orange-800/50' },
            ];
            const color = colors[idx % colors.length];
            
            return (
              <motion.div key={idx} className="relative group">
                <div className={`absolute inset-0 bg-gradient-to-br ${color.gradient} rounded-lg blur opacity-0 group-hover:opacity-100 transition duration-500`} />
                <motion.button
                  onClick={() => handleSubmit(example.text)}
                  disabled={loading}
                  className={`relative text-left w-full p-4 bg-gradient-to-br ${color.gradient} border ${color.border} ${color.hover} disabled:opacity-50 rounded-lg transition-all backdrop-blur-sm`}
                  whileHover={{ y: -2, x: 2 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <p className="font-bold text-sm mb-2 text-slate-100">{example.title}</p>
                  <p className="line-clamp-2 text-xs text-slate-300 leading-relaxed">{example.text}</p>
                </motion.button>
              </motion.div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}
