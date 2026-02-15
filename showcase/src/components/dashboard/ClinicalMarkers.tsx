'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Zap } from 'lucide-react';

interface ClinicalMarkersProps {
  markers: string[];
}

export default function ClinicalMarkers({ markers }: ClinicalMarkersProps) {
  const markerTypes = {
    critical: ['Critical Potassium', 'Critical Fever', 'Troponin Elevation'],
    warning: ['Elevated Glucose', 'Low Hemoglobin', 'Abnormal Findings'],
    vitals: ['Tachycardia', 'Hypertension', 'Consolidation'],
  };

  const getCriticalityLevel = (marker: string) => {
    if (markerTypes.critical.includes(marker)) return 'critical';
    if (markerTypes.warning.includes(marker)) return 'warning';
    return 'info';
  };

  const colorMap = {
    critical: 'red',
    warning: 'yellow',
    info: 'blue',
  };

  return (
    <motion.div
      className="bg-slate-800/50 border border-slate-700 rounded-lg p-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
    >
      <h3 className="text-lg font-semibold text-slate-100 mb-4">Clinical Markers</h3>

      {markers.length === 0 ? (
        <p className="text-sm text-slate-400 text-center py-4">No critical markers detected</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {markers.map((marker, idx) => {
            const level = getCriticalityLevel(marker);
            const color = colorMap[level];

            return (
              <motion.div
                key={idx}
                className={`px-3 py-2 rounded-lg text-xs font-semibold border flex items-center gap-1 bg-${color}-950/30 border-${color}-600/50 text-${color}-400`}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 + idx * 0.05 }}
              >
                {level === 'critical' && <AlertTriangle className="w-3 h-3" />}
                {level === 'warning' && <Zap className="w-3 h-3" />}
                {marker}
              </motion.div>
            );
          })}
        </div>
      )}
    </motion.div>
  );
}
