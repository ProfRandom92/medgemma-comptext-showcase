'use client';

import React from 'react';
import { motion } from 'framer-motion';
import type { CompressionResult } from '@/types';

interface TokenVisualizationProps {
  result: CompressionResult;
}

export function TokenVisualization({ result }: TokenVisualizationProps) {
  const ratio = result.compressed_token_count / result.original_token_count;
  const barWidth = Math.max(5, ratio * 100);

  return (
    <div className="space-y-8">
      {/* Token Count Comparison - Enhanced */}
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <label className="text-sm font-bold text-slate-200 uppercase tracking-wider">📄 Original Text</label>
          <motion.span
            className="text-lg font-bold text-red-400 px-3 py-1 bg-red-950/30 border border-red-700/50 rounded-lg"
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            {result.original_token_count} tokens
          </motion.span>
        </div>
        <motion.div
          className="relative h-4 bg-gradient-to-r from-slate-800 to-slate-700 rounded-full overflow-hidden border border-slate-700/50 shadow-lg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div
            className="h-full bg-gradient-to-r from-red-600 via-red-500 to-red-400 shadow-lg shadow-red-500/50"
            initial={{ width: 0 }}
            animate={{ width: '100%' }}
            transition={{ duration: 1, ease: 'easeOut', delay: 0.2 }}
          />
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-red-400/0 via-red-200/30 to-red-400/0"
            animate={{ x: ['-100%', '100%'] }}
            transition={{ duration: 2, repeat: Infinity, repeatDelay: 0.5 }}
          />
        </motion.div>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <label className="text-sm font-bold text-slate-200 uppercase tracking-wider">✨ Compressed</label>
          <motion.span
            className="text-lg font-bold text-emerald-400 px-3 py-1 bg-emerald-950/30 border border-emerald-700/50 rounded-lg"
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity, delay: 0.1 }}
          >
            {result.compressed_token_count} tokens
          </motion.span>
        </div>
        <motion.div
          className="relative h-4 bg-gradient-to-r from-slate-800 to-slate-700 rounded-full overflow-hidden border border-slate-700/50 shadow-lg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <motion.div
            className="h-full bg-gradient-to-r from-emerald-600 via-emerald-500 to-emerald-400 shadow-lg shadow-emerald-500/50"
            style={{ width: `${barWidth}%` }}
            initial={{ width: 0 }}
            animate={{ width: `${barWidth}%` }}
            transition={{ duration: 1, ease: 'easeOut', delay: 0.3 }}
          />
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-emerald-400/0 via-emerald-200/30 to-emerald-400/0"
            animate={{ x: ['-100%', '100%'] }}
            transition={{ duration: 2, repeat: Infinity, repeatDelay: 0.5, delay: 0.3 }}
          />
        </motion.div>
      </div>

      {/* Reduction Stats - Enhanced */}
      <motion.div
        className="grid grid-cols-2 gap-4 pt-6 border-t border-slate-700/50"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.5, staggerChildren: 0.1 }}
      >
        {/* Token Reduction Card */}
        <motion.div
          className="relative group"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-600/20 to-emerald-700/20 rounded-lg blur opacity-0 group-hover:opacity-100 transition duration-500" />
          <div className="relative bg-gradient-to-br from-emerald-950/50 to-emerald-900/30 border border-emerald-700/50 group-hover:border-emerald-600/80 rounded-lg p-4 transition-all">
            <p className="text-xs font-semibold text-emerald-300 uppercase tracking-wider mb-2">🎯 Reduction</p>
            <motion.p
              className="text-3xl font-bold text-emerald-400"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              {result.reduction_percentage}%
            </motion.p>
          </div>
        </motion.div>

        {/* Compression Time Card */}
        <motion.div
          className="relative group"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 to-cyan-700/20 rounded-lg blur opacity-0 group-hover:opacity-100 transition duration-500" />
          <div className="relative bg-gradient-to-br from-blue-950/50 to-cyan-900/30 border border-blue-700/50 group-hover:border-blue-600/80 rounded-lg p-4 transition-all">
            <p className="text-xs font-semibold text-blue-300 uppercase tracking-wider mb-2">⚡ Speed</p>
            <motion.p
              className="text-3xl font-bold text-blue-400"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.2 }}
            >
              {result.compression_time_ms}ms
            </motion.p>
          </div>
        </motion.div>

        {/* Tokens Saved Card */}
        <motion.div
          className="relative group"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.7 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-purple-600/20 to-pink-700/20 rounded-lg blur opacity-0 group-hover:opacity-100 transition duration-500" />
          <div className="relative bg-gradient-to-br from-purple-950/50 to-pink-900/30 border border-purple-700/50 group-hover:border-purple-600/80 rounded-lg p-4 transition-all">
            <p className="text-xs font-semibold text-purple-300 uppercase tracking-wider mb-2">💾 Saved</p>
            <motion.p
              className="text-3xl font-bold text-purple-400"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.4 }}
            >
              {result.original_token_count - result.compressed_token_count}
            </motion.p>
          </div>
        </motion.div>

        {/* Cost Savings Card */}
        <motion.div
          className="relative group"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.8 }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-orange-600/20 to-red-700/20 rounded-lg blur opacity-0 group-hover:opacity-100 transition duration-500" />
          <div className="relative bg-gradient-to-br from-orange-950/50 to-red-900/30 border border-orange-700/50 group-hover:border-orange-600/80 rounded-lg p-4 transition-all">
            <p className="text-xs font-semibold text-orange-300 uppercase tracking-wider mb-2">💰 Savings</p>
            <motion.p
              className="text-3xl font-bold text-orange-400"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.6 }}
            >
              ~${(0.06 * (result.original_token_count - result.compressed_token_count) / 1000).toFixed(3)}
            </motion.p>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
