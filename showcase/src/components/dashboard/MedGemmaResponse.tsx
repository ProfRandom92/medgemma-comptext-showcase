'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { MessageCircle, Zap } from 'lucide-react';
import type { PipelineResult } from '@/types';

interface MedGemmaResponseProps {
  result: PipelineResult;
}

export default function MedGemmaResponse({ result }: MedGemmaResponseProps) {
  return (
    <motion.div
      className="bg-slate-800/50 border border-slate-700 rounded-lg p-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <div className="flex items-center gap-2 mb-4">
        <MessageCircle className="w-5 h-5 text-blue-400" />
        <h3 className="text-lg font-semibold text-slate-100">MedGemma Diagnosis</h3>
      </div>

      <div className="space-y-4">
        {/* Recommendation Text */}
        <motion.div className="bg-slate-700/30 rounded-lg p-4 border border-slate-600/50" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
          <p className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">
            {result.doctor.recommendation}
          </p>
        </motion.div>

        {/* Processing Info */}
        <motion.div className="grid grid-cols-2 gap-3" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
          <div className="bg-slate-700/20 rounded p-3">
            <p className="text-xs text-slate-400 mb-1">Model</p>
            <p className="text-sm font-medium text-slate-200">MedGemma-4B</p>
          </div>
          <div className="bg-slate-700/20 rounded p-3">
            <p className="text-xs text-slate-400 mb-1">Response Time</p>
            <p className="text-sm font-medium text-blue-400">
              {result.doctor.processing_time_ms}ms
            </p>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
