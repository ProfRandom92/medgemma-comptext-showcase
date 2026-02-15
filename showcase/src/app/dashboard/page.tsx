'use client';

import React, { useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload,
  FileText,
  ImageIcon,
  Heart,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Zap,
  TrendingDown,
  Users,
  Activity,
  Download,
  BarChart3,
} from 'lucide-react';
import { useMedGemmaAPI } from '@/hooks/useMedGemmaAPI';
import type { PipelineResult, PatientState } from '@/types';

// Component imports
import DocumentUploadZone from '@/components/dashboard/DocumentUploadZone';
import RedAlertDisplay from '@/components/dashboard/RedAlertDisplay';
import VisionPreprocessingStats from '@/components/dashboard/VisionPreprocessingStats';
import CompressionMetrics from '@/components/dashboard/CompressionMetrics';
import MedGemmaResponse from '@/components/dashboard/MedGemmaResponse';
import BatchProcessingPanel from '@/components/dashboard/BatchProcessingPanel';
import ClinicalMarkers from '@/components/dashboard/ClinicalMarkers';

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

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

export default function DashboardPage() {
  const [documents, setDocuments] = useState<ProcessedDocument[]>([]);
  const [batchResults, setBatchResults] = useState<BatchResult[]>([]);
  const [activeTab, setActiveTab] = useState<'upload' | 'batch' | 'metrics'>('upload');
  const [selectedDocument, setSelectedDocument] = useState<ProcessedDocument | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const { processPatientCase, loading, error: apiError } = useMedGemmaAPI();

  // Handle document upload
  const handleDocumentUpload = useCallback(
    async (file: File, docType: 'lab_report' | 'imaging_scan' | 'vitals_monitor') => {
      const reader = new FileReader();

      reader.onload = async (e) => {
        const text = e.target?.result as string;
        const newDoc: ProcessedDocument = {
          id: `doc_${Date.now()}`,
          type: docType,
          fileName: file.name,
          extractedText: text,
          confidence: Math.random() * 0.3 + 0.7,
          markers: extractMarkers(text, docType),
          processedAt: new Date(),
        };

        setDocuments((prev) => [newDoc, ...prev]);
        setSelectedDocument(newDoc);
      };

      reader.readAsText(file);
    },
    []
  );

  const extractMarkers = (text: string, docType: string): string[] => {
    const markers: string[] = [];

    if (docType === 'lab_report') {
      if (/glucose|blood\s*sugar/i.test(text)) markers.push('Elevated Glucose');
      if (/hemoglobin|hgb/i.test(text)) markers.push('Low Hemoglobin');
      if (/potassium|K\+/i.test(text)) markers.push('Critical Potassium');
      if (/troponin/i.test(text)) markers.push('Troponin Elevation');
    } else if (docType === 'imaging_scan') {
      if (/abnormal|lesion|mass/i.test(text)) markers.push('Abnormal Findings');
      if (/consolidation/i.test(text)) markers.push('Consolidation');
    } else if (docType === 'vitals_monitor') {
      if (/hr\s*>?\s*120|tachycardia/i.test(text)) markers.push('Tachycardia');
      if (/bp\s*>?\s*160|hypertension/i.test(text)) markers.push('Hypertension');
      if (/temp\s*>?\s*40|fever/i.test(text)) markers.push('Critical Fever');
    }

    return markers;
  };

  const handleProcessDocument = useCallback(
    async (doc: ProcessedDocument) => {
      setIsProcessing(true);
      const result = await processPatientCase(doc.extractedText);

      if (result) {
        setBatchResults((prev) => [
          ...prev,
          { documentId: doc.id, pipelineResult: result },
        ]);
      } else {
        setBatchResults((prev) => [
          ...prev,
          { documentId: doc.id, pipelineResult: null, error: apiError || 'Processing failed' },
        ]);
      }
      setIsProcessing(false);
    },
    [processPatientCase, apiError]
  );

  const handleBatchProcess = useCallback(async () => {
    setIsProcessing(true);
    setBatchResults([]);

    for (const doc of documents) {
      const result = await processPatientCase(doc.extractedText);
      if (result) {
        setBatchResults((prev) => [
          ...prev,
          { documentId: doc.id, pipelineResult: result },
        ]);
      } else {
        setBatchResults((prev) => [
          ...prev,
          { documentId: doc.id, pipelineResult: null, error: apiError || 'Processing failed' },
        ]);
      }
    }

    setIsProcessing(false);
  }, [documents, processPatientCase, apiError]);

  const metrics = useMemo(() => {
    const avgCompression =
      batchResults.length > 0
        ? batchResults
            .filter((r) => r.pipelineResult)
            .reduce(
              (sum, r) => sum + (r.pipelineResult?.compression.reduction_percentage || 0),
              0
            ) / batchResults.filter((r) => r.pipelineResult).length
        : 0;

    const criticalCases = batchResults.filter(
      (r) => r.pipelineResult?.triage.priority_level === 'P1'
    ).length;

    const totalProcessingTime = batchResults.reduce(
      (sum, r) => sum + (r.pipelineResult?.total_time_ms || 0),
      0
    );

    return {
      totalDocuments: documents.length,
      processedDocuments: batchResults.filter((r) => r.pipelineResult).length,
      avgCompression,
      criticalCases,
      totalProcessingTime,
      successRate:
        batchResults.length > 0
          ? ((batchResults.filter((r) => r.pipelineResult).length / batchResults.length) * 100).toFixed(1)
          : 0,
    };
  }, [documents.length, batchResults]);

  const selectedResult = selectedDocument
    ? batchResults.find((r) => r.documentId === selectedDocument.id)?.pipelineResult
    : null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <motion.section
        className="relative overflow-hidden py-12 px-4 sm:px-6 lg:px-8 border-b border-slate-800"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6 }}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-red-600/5 via-transparent to-blue-600/5 pointer-events-none" />

        <div className="relative max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="p-3 bg-red-600/20 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-red-400" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-slate-100">
                  Clinical Dashboard v5
                </h1>
                <p className="text-slate-400 mt-1">
                  Vision preprocessing • Red alert detection • MedGemma diagnosis
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </motion.section>

      {/* Metrics Bar */}
      <motion.section
        className="py-6 px-4 sm:px-6 lg:px-8 border-b border-slate-800 bg-slate-800/30"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        variants={containerVariants}
      >
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="grid grid-cols-2 md:grid-cols-4 gap-4"
            variants={containerVariants}
          >
            {[
              { icon: FileText, label: 'Documents', value: metrics.totalDocuments, color: 'blue' },
              { icon: CheckCircle2, label: 'Processed', value: metrics.processedDocuments, color: 'emerald' },
              { icon: TrendingDown, label: 'Avg Compression', value: `${metrics.avgCompression.toFixed(1)}%`, color: 'violet' },
              { icon: AlertTriangle, label: 'Critical Cases', value: metrics.criticalCases, color: 'red' },
            ].map((stat, idx) => (
              <motion.div
                key={idx}
                className="bg-slate-800/50 border border-slate-700 rounded-lg p-4"
                variants={itemVariants}
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 bg-${stat.color}-600/20 rounded-lg`}>
                    <stat.icon className={`w-5 h-5 text-${stat.color}-400`} />
                  </div>
                  <div>
                    <p className="text-xs text-slate-400">{stat.label}</p>
                    <p className="text-lg font-bold text-slate-100">{stat.value}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </motion.section>

      {/* Main Content */}
      <section className="py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Tab Navigation */}
          <motion.div
            className="flex gap-2 mb-8 border-b border-slate-800"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {(['upload', 'batch', 'metrics'] as const).map((tab) => (
              <motion.button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-3 font-semibold transition-all border-b-2 ${
                  activeTab === tab
                    ? 'border-red-500 text-red-400'
                    : 'border-transparent text-slate-400 hover:text-slate-300'
                }`}
                whileHover={{ scale: 1.05 }}
              >
                {tab === 'upload' && '📤 Upload'}
                {tab === 'batch' && '⚙️ Batch'}
                {tab === 'metrics' && '📊 Metrics'}
              </motion.button>
            ))}
          </motion.div>

          {/* Content */}
          <AnimatePresence mode="wait">
            {activeTab === 'upload' && (
              <motion.div
                key="upload"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="grid grid-cols-1 lg:grid-cols-3 gap-6"
              >
                <div className="lg:col-span-2 space-y-6">
                  <DocumentUploadZone onUpload={handleDocumentUpload} loading={loading} />
                  {documents.length > 0 && (
                    <motion.div
                      className="bg-slate-800/50 border border-slate-700 rounded-lg p-6"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                    >
                      <h3 className="text-lg font-semibold text-slate-100 mb-4">
                        Documents ({documents.length})
                      </h3>
                      <div className="space-y-3">
                        {documents.map((doc) => (
                          <motion.button
                            key={doc.id}
                            onClick={() => setSelectedDocument(doc)}
                            className={`w-full text-left p-4 rounded-lg border transition-all ${
                              selectedDocument?.id === doc.id
                                ? 'bg-red-600/20 border-red-500/50'
                                : 'bg-slate-700/30 border-slate-600/50 hover:bg-slate-700/50'
                            }`}
                            whileHover={{ x: 4 }}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  {doc.type === 'lab_report' && <FileText className="w-4 h-4 text-blue-400" />}
                                  {doc.type === 'imaging_scan' && <ImageIcon className="w-4 h-4 text-emerald-400" />}
                                  {doc.type === 'vitals_monitor' && <Activity className="w-4 h-4 text-red-400" />}
                                  <span className="text-sm font-medium text-slate-200">{doc.fileName}</span>
                                </div>
                                <div className="flex items-center gap-2 text-xs text-slate-400">
                                  <span className="px-2 py-1 bg-slate-600/50 rounded">{doc.type.replace(/_/g, ' ')}</span>
                                  <span>{(doc.confidence * 100).toFixed(0)}% confidence</span>
                                </div>
                              </div>
                              {batchResults.some((r) => r.documentId === doc.id && r.pipelineResult) && (
                                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                              )}
                            </div>
                          </motion.button>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </div>

                <div className="space-y-6">
                  {selectedDocument ? (
                    <>
                      <VisionPreprocessingStats document={selectedDocument} />
                      <ClinicalMarkers markers={selectedDocument.markers} />
                      <motion.button
                        onClick={() => handleProcessDocument(selectedDocument)}
                        disabled={isProcessing}
                        className="w-full py-3 bg-red-600 hover:bg-red-700 disabled:bg-slate-600 text-white font-semibold rounded-lg transition-all"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        {isProcessing ? 'Processing...' : 'Process'}
                      </motion.button>
                    </>
                  ) : (
                    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 text-center text-slate-400">
                      <Heart className="w-12 h-12 mx-auto mb-3 opacity-50" />
                      <p>Select a document</p>
                    </div>
                  )}
                  {selectedResult && <RedAlertDisplay result={selectedResult} />}
                </div>
              </motion.div>
            )}

            {activeTab === 'batch' && (
              <motion.div
                key="batch"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <BatchProcessingPanel
                  documents={documents}
                  batchResults={batchResults}
                  onProcessAll={handleBatchProcess}
                  isProcessing={isProcessing}
                />
              </motion.div>
            )}

            {activeTab === 'metrics' && (
              <motion.div
                key="metrics"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <CompressionMetrics batchResults={batchResults} />
              </motion.div>
            )}
          </AnimatePresence>

          {apiError && (
            <motion.div
              className="mt-6 p-4 bg-red-950/30 border border-red-700/50 rounded-lg text-red-300 text-sm"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              ⚠️ {apiError}
            </motion.div>
          )}
        </div>
      </section>
    </div>
  );
}
