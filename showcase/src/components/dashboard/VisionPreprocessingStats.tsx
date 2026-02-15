'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { FileText, ImageIcon, Activity, CheckCircle2 } from 'lucide-react';

interface ProcessedDocument {
  id: string;
  type: 'lab_report' | 'imaging_scan' | 'vitals_monitor';
  fileName: string;
  extractedText: string;
  confidence: number;
  markers: string[];
  processedAt: Date;
}

interface VisionPreprocessingStatsProps {
  document: ProcessedDocument;
}

export default function VisionPreprocessingStats({ document }: VisionPreprocessingStatsProps) {
  const typeInfo = {
    lab_report: { icon: FileText, label: 'Lab Report', color: 'blue' },
    imaging_scan: { icon: ImageIcon, label: 'Imaging Scan', color: 'emerald' },
    vitals_monitor: { icon: Activity, label: 'Vitals Monitor', color: 'red' },
  };

  const info = typeInfo[document.type];
  const Icon = info.icon;

  return (
    <motion.div
      className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 space-y-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div>
        <h3 className="text-lg font-semibold text-slate-100 mb-4">Vision Preprocessing</h3>
      </div>

      <div className="space-y-3">
        <div className="flex items-center gap-3 pb-3 border-b border-slate-700">
          <Icon className={`w-5 h-5 text-${info.color}-400`} />
          <div>
            <p className="text-xs text-slate-400">Document Type</p>
            <p className="text-sm font-medium text-slate-200">{info.label}</p>
          </div>
        </div>

        <div className="flex items-center justify-between pb-3 border-b border-slate-700">
          <p className="text-xs text-slate-400">Extraction Confidence</p>
          <div className="flex items-center gap-2">
            <div className="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-blue-500 to-emerald-500"
                initial={{ width: 0 }}
                animate={{ width: `${document.confidence * 100}%` }}
                transition={{ duration: 0.8, delay: 0.2 }}
              />
            </div>
            <span className="text-sm font-bold text-slate-200">
              {(document.confidence * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        <div className="pb-3 border-b border-slate-700">
          <p className="text-xs text-slate-400 mb-2">Extracted Content</p>
          <p className="text-xs text-slate-300 line-clamp-2 bg-slate-700/30 p-2 rounded">
            {document.extractedText.substring(0, 100)}...
          </p>
        </div>

        <div className="flex items-center justify-between">
          <p className="text-xs text-slate-400">Processing Status</p>
          <motion.div className="flex items-center gap-1" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span className="text-sm font-medium text-emerald-400">Ready</span>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
