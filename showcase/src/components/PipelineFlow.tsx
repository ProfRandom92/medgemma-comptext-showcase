'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, AlertCircle, Stethoscope } from 'lucide-react';
import type { PipelineResult } from '@/types';

interface PipelineFlowProps {
  result: PipelineResult;
}

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.3,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, x: -20 },
  show: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.5 },
  },
};

export function PipelineFlow({ result }: PipelineFlowProps) {
  const [animateFlow, setAnimateFlow] = useState(false);

  useEffect(() => {
    setAnimateFlow(true);
  }, [result]);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'P1':
        return 'from-red-600 to-red-400';
      case 'P2':
        return 'from-orange-600 to-orange-400';
      case 'P3':
        return 'from-green-600 to-green-400';
      default:
        return 'from-gray-600 to-gray-400';
    }
  };

  return (
    <motion.div
      className="space-y-6"
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      {/* Step 1: Nurse Agent - Enhanced */}
      <motion.div variants={itemVariants} className="flex gap-4 relative">
        <div className="flex-shrink-0 relative">
          <motion.div
            className="absolute inset-0 bg-blue-600/30 rounded-full blur"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          <div className="relative flex items-center justify-center h-12 w-12 rounded-full bg-gradient-to-br from-blue-600/40 to-cyan-600/40 border-2 border-blue-500 shadow-lg shadow-blue-500/50">
            <Activity className="h-6 w-6 text-blue-300 animate-pulse" />
          </div>
        </div>
        <div className="flex-1">
          <h4 className="font-bold text-lg text-slate-100 uppercase tracking-wide">🩺 Nurse Agent</h4>
          <p className="text-xs text-blue-300 font-semibold mb-2">CompText Compression Protocol</p>
          <motion.div
            className="mt-2 text-xs text-slate-200 bg-gradient-to-br from-blue-950/50 to-cyan-950/30 border border-blue-700/50 rounded-lg p-3 backdrop-blur-sm"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <p className="font-semibold text-blue-300 mb-1">✓ Extraction Complete</p>
            <p className="text-slate-300">• Fields: {Object.keys(result.compression.compressed_state).length}</p>
            <p className="text-slate-300">• Reduction: {result.compression.reduction_percentage}%</p>
            <p className="text-cyan-400 font-semibold">⏱ {result.compression.compression_time_ms}ms</p>
          </motion.div>
        </div>
      </motion.div>

      {/* Arrow - Enhanced */}
      <motion.div className="flex justify-center py-2">
        <motion.div
          className="text-2xl text-slate-500"
          animate={animateFlow ? { y: [0, 6, 0], opacity: [0.5, 1, 0.5] } : { opacity: 0.3 }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          ↓
        </motion.div>
      </motion.div>

      {/* Step 2: Triage Agent - Enhanced */}
      <motion.div variants={itemVariants} className="flex gap-4 relative">
        <div className="flex-shrink-0 relative">
          <motion.div
            className={`absolute inset-0 bg-gradient-to-r ${getPriorityColor(result.triage.priority_level)} rounded-full blur opacity-40`}
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 2, repeat: Infinity, delay: 0.3 }}
          />
          <div className="relative flex items-center justify-center h-12 w-12 rounded-full bg-gradient-to-br from-orange-600/40 to-red-600/40 border-2 border-orange-500 shadow-lg shadow-orange-500/50">
            <AlertCircle className="h-6 w-6 text-orange-300 animate-pulse" />
          </div>
        </div>
        <div className="flex-1">
          <h4 className="font-bold text-lg text-slate-100 uppercase tracking-wide">🚨 Triage Agent</h4>
          <p className="text-xs text-orange-300 font-semibold mb-2">Priority Assessment</p>
          <motion.div
            className={`mt-2 text-xs text-white bg-gradient-to-r ${getPriorityColor(result.triage.priority_level)} bg-opacity-30 border border-current rounded-lg p-3 backdrop-blur-sm shadow-lg`}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.7 }}
          >
            <p className="font-bold text-lg mb-1">{result.triage.priority_level} — {result.triage.priority_name}</p>
            <p className="text-slate-100">{result.triage.reason}</p>
          </motion.div>
        </div>
      </motion.div>

      {/* Arrow - Enhanced */}
      <motion.div className="flex justify-center py-2">
        <motion.div
          className="text-2xl text-slate-500"
          animate={animateFlow ? { y: [0, 6, 0], opacity: [0.5, 1, 0.5] } : { opacity: 0.3 }}
          transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
        >
          ↓
        </motion.div>
      </motion.div>

      {/* Step 3: Doctor Agent - Enhanced */}
      <motion.div variants={itemVariants} className="flex gap-4 relative">
        <div className="flex-shrink-0 relative">
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-green-600/30 to-emerald-600/30 rounded-full blur opacity-40"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 2, repeat: Infinity, delay: 0.6 }}
          />
          <div className="relative flex items-center justify-center h-12 w-12 rounded-full bg-gradient-to-br from-green-600/40 to-emerald-600/40 border-2 border-green-500 shadow-lg shadow-green-500/50">
            <Stethoscope className="h-6 w-6 text-green-300 animate-pulse" />
          </div>
        </div>
        <div className="flex-1">
          <h4 className="font-bold text-lg text-slate-100 uppercase tracking-wide">👨‍⚕️ Doctor Agent</h4>
          <p className="text-xs text-green-300 font-semibold mb-2">Clinical Recommendation</p>
          <motion.div
            className="mt-2 text-sm text-slate-200 bg-gradient-to-br from-green-950/50 to-emerald-950/30 border border-green-700/50 rounded-lg p-4 italic backdrop-blur-sm shadow-lg"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
          >
            <p className="not-italic font-semibold text-green-300 mb-2">💊 Recommendation:</p>
            <p className="text-slate-100">"{result.doctor.recommendation}"</p>
            <p className="text-xs text-green-400 not-italic mt-2 font-mono">
              ⏱ Processing: {result.doctor.processing_time_ms}ms
            </p>
          </motion.div>
        </div>
      </motion.div>

      {/* Total Pipeline Time - Enhanced */}
      <motion.div
        className="pt-6 border-t border-slate-700/50 relative"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.1 }}
      >
        <motion.div className="absolute inset-0 bg-gradient-to-r from-cyan-600/10 via-blue-600/10 to-cyan-600/10 blur rounded opacity-50" />
        <div className="relative text-center">
          <p className="text-xs font-bold text-cyan-300 uppercase tracking-widest mb-2">⏱ Total Pipeline Duration</p>
          <motion.p
            className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent"
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            {result.total_time_ms}ms
          </motion.p>
          <p className="text-xs text-slate-400 mt-2">Multi-agent processing complete ✓</p>
        </div>
      </motion.div>
    </motion.div>
  );
}
