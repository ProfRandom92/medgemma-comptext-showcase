'use client';

import React from 'react';
import { motion } from 'framer-motion';
import type { PatientState } from '@/types';

interface CompressedStateViewProps {
  state: PatientState;
}

export function CompressedStateView({ state }: CompressedStateViewProps) {
  const json = JSON.stringify(state, null, 2);

  return (
    <motion.div
      className="space-y-3"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-center gap-2 mb-2">
        <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />
        <h3 className="font-semibold text-slate-200">Compressed Patient State</h3>
      </div>

      <pre className="bg-slate-900 border border-slate-700 rounded-lg p-4 overflow-x-auto text-xs text-slate-300 font-mono">
        <code>{json}</code>
      </pre>

      {/* Key Indicators */}
      <motion.div
        className="grid grid-cols-2 gap-2 text-xs"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        {state.meta?.active_protocol && (
          <div className="bg-purple-950/40 border border-purple-700/50 rounded px-3 py-2">
            <p className="text-purple-300 font-semibold">{state.meta.active_protocol}</p>
          </div>
        )}

        {state.chief_complaint && (
          <div className="bg-blue-950/40 border border-blue-700/50 rounded px-3 py-2">
            <p className="text-blue-300 text-xs">Chief: {state.chief_complaint.substring(0, 30)}...</p>
          </div>
        )}

        {state.vitals && (
          <div className="bg-orange-950/40 border border-orange-700/50 rounded px-3 py-2">
            <p className="text-orange-300 font-semibold">
              HR: {state.vitals.hr} | BP: {state.vitals.bp}
            </p>
          </div>
        )}

        {state.specialist_data && Object.keys(state.specialist_data).length > 0 && (
          <div className="bg-cyan-950/40 border border-cyan-700/50 rounded px-3 py-2">
            <p className="text-cyan-300 text-xs">
              Specialist fields: {Object.keys(state.specialist_data).length}
            </p>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}
