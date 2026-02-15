'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Heart, TrendingUp, Clock } from 'lucide-react';
import type { PipelineResult } from '@/types';

interface RedAlertDisplayProps {
  result: PipelineResult;
  isRedAlert?: boolean;
}

export default function RedAlertDisplay({ result }: RedAlertDisplayProps) {
  const isRedAlert = result.triage.priority_level === 'P1';
  const isUrgent = result.triage.priority_level === 'P2';

  const priorityColors = {
    P1: { bg: 'red', text: 'text-red-400', border: 'border-red-500/50', bgOpacity: 'bg-red-950/30' },
    P2: { bg: 'yellow', text: 'text-yellow-400', border: 'border-yellow-500/50', bgOpacity: 'bg-yellow-950/30' },
    P3: { bg: 'emerald', text: 'text-emerald-400', border: 'border-emerald-500/50', bgOpacity: 'bg-emerald-950/30' },
  };

  const colors = priorityColors[result.triage.priority_level];

  return (
    <motion.div
      className={`rounded-lg border ${colors.border} ${colors.bgOpacity} p-6 space-y-4`}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
    >
      {/* Alert Header */}
      <div className="flex items-start gap-3">
        <motion.div
          animate={isRedAlert ? { scale: [1, 1.2, 1] } : {}}
          transition={{ repeat: Infinity, duration: 2 }}
        >
          <AlertTriangle className={`w-6 h-6 ${colors.text}`} />
        </motion.div>
        <div className="flex-1">
          <h3 className={`font-bold ${colors.text}`}>
            {isRedAlert && '🚨 CRITICAL - IMMEDIATE ESCALATION'}
            {isUrgent && '⚠️ URGENT - PRIORITY REVIEW'}
            {!isRedAlert && !isUrgent && '✓ STANDARD - ROUTINE'}
          </h3>
          <p className="text-sm text-slate-400 mt-1">{result.triage.reason}</p>
        </div>
      </div>

      {/* Priority Metrics */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-slate-800/50 rounded p-3">
          <p className="text-xs text-slate-400 mb-1">Priority Level</p>
          <p className={`text-lg font-bold ${colors.text}`}>{result.triage.priority_level}</p>
        </div>
        <div className="bg-slate-800/50 rounded p-3">
          <p className="text-xs text-slate-400 mb-1">Response Time</p>
          <p className="text-lg font-bold text-blue-400">{result.total_time_ms}ms</p>
        </div>
      </div>

      {/* Recommendation Summary */}
      {result.doctor.recommendation && (
        <motion.div
          className="bg-slate-800/30 rounded p-4 border border-slate-700/50"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <p className="text-sm font-semibold text-slate-200 mb-2">Medical Recommendation:</p>
          <p className="text-sm text-slate-400 line-clamp-3">
            {result.doctor.recommendation}
          </p>
        </motion.div>
      )}

      {/* Red Alert Escalation Info */}
      {isRedAlert && (
        <motion.div
          className="bg-red-950/50 border border-red-700/50 rounded p-4 space-y-2"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <p className="text-sm font-semibold text-red-300">Escalation Required:</p>
          <ul className="text-sm text-red-400 space-y-1">
            <li>✓ Alert senior physician immediately</li>
            <li>✓ Consider ICU admission</li>
            <li>✓ Continuous vital monitoring mandatory</li>
          </ul>
        </motion.div>
      )}
    </motion.div>
  );
}
