'use client';

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, TrendingDown, Zap, Clock } from 'lucide-react';
import type { PipelineResult } from '@/types';

interface BatchResult {
  documentId: string;
  pipelineResult: PipelineResult | null;
  error?: string;
}

interface CompressionMetricsProps {
  batchResults: BatchResult[];
}

export default function CompressionMetrics({ batchResults }: CompressionMetricsProps) {
  const metrics = useMemo(() => {
    const processed = batchResults.filter((r) => r.pipelineResult);

    if (processed.length === 0) {
      return {
        avgCompression: 0,
        avgProcessingTime: 0,
        totalTokensSaved: 0,
        minCompression: 0,
        maxCompression: 0,
      };
    }

    const compressionRates = processed.map((r) => r.pipelineResult!.compression.reduction_percentage);
    const processingTimes = processed.map((r) => r.pipelineResult!.total_time_ms);
    const tokensSaved = processed.reduce((sum, r) => {
      const diff = r.pipelineResult!.compression.original_token_count -
        r.pipelineResult!.compression.compressed_token_count;
      return sum + Math.max(0, diff);
    }, 0);

    return {
      avgCompression: compressionRates.reduce((a, b) => a + b, 0) / compressionRates.length,
      avgProcessingTime: processingTimes.reduce((a, b) => a + b, 0) / processingTimes.length,
      totalTokensSaved: tokensSaved,
      minCompression: Math.min(...compressionRates),
      maxCompression: Math.max(...compressionRates),
    };
  }, [batchResults]);

  return (
    <motion.div
      className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <h3 className="text-lg font-semibold text-slate-100">Compression Analytics</h3>

      <div className="grid grid-cols-2 gap-4">
        <MetricCard
          icon={TrendingDown}
          label="Avg Compression"
          value={`${metrics.avgCompression.toFixed(1)}%`}
          color="violet"
        />
        <MetricCard
          icon={Clock}
          label="Avg Processing"
          value={`${metrics.avgProcessingTime.toFixed(0)}ms`}
          color="blue"
        />
        <MetricCard
          icon={Zap}
          label="Tokens Saved"
          value={metrics.totalTokensSaved.toLocaleString()}
          color="emerald"
        />
        <MetricCard
          icon={BarChart3}
          label="Compression Range"
          value={`${metrics.minCompression.toFixed(0)}-${metrics.maxCompression.toFixed(0)}%`}
          color="red"
        />
      </div>

      {batchResults.length > 0 && (
        <motion.div className="pt-4 border-t border-slate-700" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <p className="text-sm text-slate-400 mb-3">Processed: {batchResults.filter((r) => r.pipelineResult).length} / {batchResults.length}</p>
          <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-emerald-500 to-blue-500"
              initial={{ width: 0 }}
              animate={{ width: `${(batchResults.filter((r) => r.pipelineResult).length / batchResults.length) * 100}%` }}
              transition={{ duration: 1 }}
            />
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
  color: string;
}) {
  return (
    <motion.div className={`bg-${color}-950/20 border border-${color}-600/30 rounded-lg p-4`} whileHover={{ scale: 1.05 }}>
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`w-4 h-4 text-${color}-400`} />
        <p className="text-xs text-slate-400">{label}</p>
      </div>
      <p className={`text-lg font-bold text-${color}-300`}>{value}</p>
    </motion.div>
  );
}
