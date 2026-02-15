'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Play, CheckCircle2, AlertCircle, FileText, ImageIcon, Activity } from 'lucide-react';
import type { PipelineResult } from '@/types';

interface ProcessedDocument {
  id: string;
  type: 'lab_report' | 'imaging_scan' | 'vitals_monitor';
  fileName: string;
  extractedText: string;
  confidence: number;
  markers: string[];
  processedAt: Date;
}

interface BatchResult {
  documentId: string;
  pipelineResult: PipelineResult | null;
  error?: string;
}

interface BatchProcessingPanelProps {
  documents: ProcessedDocument[];
  batchResults: BatchResult[];
  onProcessAll: () => void;
  isProcessing: boolean;
}

export default function BatchProcessingPanel({
  documents,
  batchResults,
  onProcessAll,
  isProcessing,
}: BatchProcessingPanelProps) {
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'lab_report':
        return <FileText className="w-4 h-4 text-blue-400" />;
      case 'imaging_scan':
        return <ImageIcon className="w-4 h-4 text-emerald-400" />;
      case 'vitals_monitor':
        return <Activity className="w-4 h-4 text-red-400" />;
      default:
        return null;
    }
  };

  return (
    <motion.div className="space-y-6" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      {/* Action Bar */}
      <motion.div
        className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 flex items-center justify-between"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div>
          <h3 className="text-lg font-semibold text-slate-100 mb-1">Batch Processing</h3>
          <p className="text-sm text-slate-400">
            {documents.length} document{documents.length !== 1 ? 's' : ''} ready to process
          </p>
        </div>
        <motion.button
          onClick={onProcessAll}
          disabled={isProcessing || documents.length === 0}
          className="flex items-center gap-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 text-white font-semibold rounded-lg transition-all"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Play className="w-4 h-4" />
          {isProcessing ? 'Processing...' : 'Process All'}
        </motion.button>
      </motion.div>

      {/* Documents Queue */}
      {documents.length > 0 && (
        <motion.div
          className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 space-y-3"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <h3 className="text-lg font-semibold text-slate-100 mb-4">Queue ({documents.length})</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {documents.map((doc, idx) => {
              const result = batchResults.find((r) => r.documentId === doc.id);
              const isProcessed = result?.pipelineResult;
              const hasError = result?.error;

              return (
                <motion.div
                  key={doc.id}
                  className={`flex items-center justify-between p-3 rounded-lg border transition-all ${
                    isProcessed
                      ? 'bg-emerald-950/20 border-emerald-600/30'
                      : hasError
                      ? 'bg-red-950/20 border-red-600/30'
                      : 'bg-slate-700/30 border-slate-600/30'
                  }`}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                >
                  <div className="flex items-center gap-3 flex-1">
                    {getTypeIcon(doc.type)}
                    <div className="flex-1">
                      <p className="text-sm font-medium text-slate-200">{doc.fileName}</p>
                      <p className="text-xs text-slate-400">
                        {doc.type.replace(/_/g, ' ')} • {doc.confidence * 100 | 0}% confidence
                      </p>
                    </div>
                  </div>
                  <div>
                    {isProcessed && (
                      <div className="flex items-center gap-1 text-emerald-400">
                        <CheckCircle2 className="w-5 h-5" />
                        <span className="text-xs font-medium">
                          {result.pipelineResult?.total_time_ms}ms
                        </span>
                      </div>
                    )}
                    {hasError && (
                      <div className="flex items-center gap-1 text-red-400">
                        <AlertCircle className="w-5 h-5" />
                        <span className="text-xs font-medium">Error</span>
                      </div>
                    )}
                    {!isProcessed && !hasError && (
                      <span className="text-xs text-slate-400">Pending</span>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </motion.div>
      )}

      {/* Empty State */}
      {documents.length === 0 && (
        <motion.div
          className="bg-slate-800/50 border border-dashed border-slate-600 rounded-lg p-12 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <p className="text-slate-400">No documents to process. Upload some documents first!</p>
        </motion.div>
      )}
    </motion.div>
  );
}
