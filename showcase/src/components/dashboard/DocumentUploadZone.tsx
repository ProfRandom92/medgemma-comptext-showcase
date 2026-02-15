'use client';

import React, { useCallback } from 'react';
import { motion } from 'framer-motion';
import { Upload, FileText, ImageIcon, Activity } from 'lucide-react';

interface DocumentUploadZoneProps {
  onUpload: (file: File, docType: 'lab_report' | 'imaging_scan' | 'vitals_monitor') => void;
  loading?: boolean;
}

export default function DocumentUploadZone({
  onUpload,
  loading,
}: DocumentUploadZoneProps) {
  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      const file = e.dataTransfer.files?.[0];
      if (file) {
        const docType = inferDocumentType(file.name);
        onUpload(file, docType);
      }
    },
    [onUpload]
  );

  const handleFileSelect = useCallback(
    (docType: 'lab_report' | 'imaging_scan' | 'vitals_monitor') => {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.txt,.pdf,.csv';
      input.onchange = (e) => {
        const file = (e.target as HTMLInputElement).files?.[0];
        if (file) onUpload(file, docType);
      };
      input.click();
    },
    [onUpload]
  );

  const inferDocumentType = (fileName: string): 'lab_report' | 'imaging_scan' | 'vitals_monitor' => {
    const lower = fileName.toLowerCase();
    if (/lab|report|test/.test(lower)) return 'lab_report';
    if (/image|scan|xray|ct|mri/.test(lower)) return 'imaging_scan';
    if (/vital|monitor|ekg|ecg/.test(lower)) return 'vitals_monitor';
    return 'lab_report';
  };

  return (
    <motion.div className="space-y-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      {/* Drag & Drop Zone */}
      <motion.div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        className="relative border-2 border-dashed border-slate-600 rounded-lg p-8 text-center hover:border-red-500/50 transition-all cursor-pointer"
        whileHover={{ borderColor: '#ef4444' }}
      >
        <div className="absolute inset-0 bg-gradient-to-b from-red-600/5 to-transparent rounded-lg pointer-events-none" />
        <div className="relative">
          <Upload className="w-12 h-12 mx-auto mb-3 text-slate-400" />
          <h3 className="text-lg font-semibold text-slate-100 mb-1">Drop documents here</h3>
          <p className="text-sm text-slate-400">or select a document type below</p>
        </div>
      </motion.div>

      {/* Document Type Buttons */}
      <motion.div
        className="grid grid-cols-1 sm:grid-cols-3 gap-3"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        {[
          { type: 'lab_report' as const, icon: FileText, label: 'Lab Report', color: 'blue' },
          { type: 'imaging_scan' as const, icon: ImageIcon, label: 'Imaging Scan', color: 'emerald' },
          { type: 'vitals_monitor' as const, icon: Activity, label: 'Vitals Monitor', color: 'red' },
        ].map((doc, idx) => (
          <motion.button
            key={doc.type}
            onClick={() => handleFileSelect(doc.type)}
            disabled={loading}
            className={`relative overflow-hidden py-4 px-4 rounded-lg border-2 transition-all group disabled:opacity-50`}
            style={{
              borderColor: `var(--color-${doc.color}-600)`,
              backgroundColor: `var(--color-${doc.color}-950)`,
            }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + idx * 0.05 }}
          >
            <div className={`absolute inset-0 bg-${doc.color}-600/10 group-hover:bg-${doc.color}-600/20 transition-all`} />
            <div className="relative flex items-center justify-center gap-2">
              <doc.icon className={`w-5 h-5 text-${doc.color}-400`} />
              <span className={`font-semibold text-${doc.color}-300`}>{doc.label}</span>
            </div>
          </motion.button>
        ))}
      </motion.div>
    </motion.div>
  );
}
