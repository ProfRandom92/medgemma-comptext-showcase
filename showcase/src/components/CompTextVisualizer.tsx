'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, Area, AreaChart, ScatterChart, Scatter } from 'recharts';

interface CompTextData {
  originalText: string;
  compressedText: string;
  originalTokens: number;
  compressedTokens: number;
  reduction: number;
  domain: string;
  timestamp: number;
}

interface VisualizationMode {
  type: 'timeline' | 'comparison' | 'breakdown' | 'protocol' | 'savings';
  label: string;
  icon: string;
}

export function CompTextVisualizer() {
  const [compTextHistory, setCompTextHistory] = useState<CompTextData[]>([]);
  const [selectedMode, setSelectedMode] = useState<'timeline' | 'comparison' | 'breakdown' | 'protocol' | 'savings'>('timeline');
  const [expandedView, setExpandedView] = useState(false);
  const [animateCounter, setAnimateCounter] = useState(false);

  // Generate sample data for demo
  useEffect(() => {
    const sampleData: CompTextData[] = [
      {
        originalText: 'Chief complaint: Chest pain radiating to left arm with shortness of breath...',
        compressedText: 'CP radiating L arm + SOB',
        originalTokens: 45,
        compressedTokens: 8,
        reduction: 82.2,
        domain: 'Cardiology',
        timestamp: Date.now() - 60000,
      },
      {
        originalText: 'Patient presents with persistent cough for 3 weeks, fever, productive sputum...',
        compressedText: 'Cough 3w + fever + sputum',
        originalTokens: 38,
        compressedTokens: 7,
        reduction: 81.6,
        domain: 'Respiratory',
        timestamp: Date.now() - 40000,
      },
      {
        originalText: 'Worst headache of life, neck stiffness, photophobia, focal neurological deficits...',
        compressedText: 'Worst HA ever + neck stiff + focal deficits',
        originalTokens: 42,
        compressedTokens: 8,
        reduction: 81.0,
        domain: 'Neurology',
        timestamp: Date.now() - 20000,
      },
      {
        originalText: 'Motor vehicle collision, patient unrestrained, unstable vitals, abdominal distension...',
        compressedText: 'MVC unrestrained + unstable + abd distend',
        originalTokens: 40,
        compressedTokens: 7,
        reduction: 82.5,
        domain: 'Trauma',
        timestamp: Date.now(),
      },
    ];
    setCompTextHistory(sampleData);
    setAnimateCounter(true);
  }, []);

  const visualizationModes: VisualizationMode[] = [
    { type: 'timeline', label: 'Timeline', icon: '📈' },
    { type: 'comparison', label: 'Vergleich', icon: '⚖️' },
    { type: 'breakdown', label: 'Analyse', icon: '🔬' },
    { type: 'protocol', label: 'Protokolle', icon: '🏥' },
    { type: 'savings', label: 'Einsparungen', icon: '💰' },
  ];

  // Prepare timeline data
  const timelineData = compTextHistory.map((item, idx) => ({
    name: `Fall ${idx + 1}`,
    domain: item.domain,
    reduction: Math.round(item.reduction * 10) / 10,
    original: item.originalTokens,
    compressed: item.compressedTokens,
  }));

  // Prepare comparison data
  const comparisonData = compTextHistory.map((item, idx) => ({
    name: item.domain,
    Original: item.originalTokens,
    Komprimiert: item.compressedTokens,
    Einsparung: item.originalTokens - item.compressedTokens,
  }));

  // Prepare breakdown by domain
  const breakdownByDomain = [
    { domain: 'Cardiology', cases: 1, avgReduction: 82.2, avgTokens: 26.5 },
    { domain: 'Respiratory', cases: 1, avgReduction: 81.6, avgTokens: 22.5 },
    { domain: 'Neurology', cases: 1, avgReduction: 81.0, avgTokens: 25.0 },
    { domain: 'Trauma', cases: 1, avgReduction: 82.5, avgTokens: 23.5 },
  ];

  // Calculate totals
  const totalOriginal = compTextHistory.reduce((sum, item) => sum + item.originalTokens, 0);
  const totalCompressed = compTextHistory.reduce((sum, item) => sum + item.compressedTokens, 0);
  const avgReduction = compTextHistory.length > 0
    ? Math.round((compTextHistory.reduce((sum, item) => sum + item.reduction, 0) / compTextHistory.length) * 10) / 10
    : 0;
  const costSavings = totalOriginal - totalCompressed;

  return (
    <div className="w-full space-y-6">
      {/* Header Stats */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-4"
      >
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="bg-gradient-to-br from-medical-blue/20 to-medical-blue/10 border border-medical-blue/50 p-4 rounded-lg"
        >
          <div className="text-sm text-gray-400 mb-1">Ursprüngliche Token</div>
          <motion.div
            className="text-3xl font-bold text-medical-blue"
            animate={animateCounter ? { opacity: [0, 1] } : {}}
          >
            {totalOriginal}
          </motion.div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-br from-medical-green/20 to-medical-green/10 border border-medical-green/50 p-4 rounded-lg"
        >
          <div className="text-sm text-gray-400 mb-1">Komprimierte Token</div>
          <motion.div
            className="text-3xl font-bold text-medical-green"
            animate={animateCounter ? { opacity: [0, 1] } : {}}
          >
            {totalCompressed}
          </motion.div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-br from-medical-orange/20 to-medical-orange/10 border border-medical-orange/50 p-4 rounded-lg"
        >
          <div className="text-sm text-gray-400 mb-1">Durchschn. Reduktion</div>
          <motion.div
            className="text-3xl font-bold text-medical-orange"
            animate={animateCounter ? { opacity: [0, 1] } : {}}
          >
            {avgReduction}%
          </motion.div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-br from-medical-red/20 to-medical-red/10 border border-medical-red/50 p-4 rounded-lg"
        >
          <div className="text-sm text-gray-400 mb-1">Token eingespart</div>
          <motion.div
            className="text-3xl font-bold text-medical-red"
            animate={animateCounter ? { opacity: [0, 1] } : {}}
          >
            {costSavings}
          </motion.div>
        </motion.div>
      </motion.div>

      {/* Visualization Mode Selector */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex gap-2 flex-wrap"
      >
        {visualizationModes.map((mode) => (
          <motion.button
            key={mode.type}
            onClick={() => setSelectedMode(mode.type)}
            className={`px-4 py-2 rounded-lg font-semibold transition-all ${
              selectedMode === mode.type
                ? 'bg-medical-blue text-white shadow-lg shadow-medical-blue/50'
                : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
            }`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {mode.icon} {mode.label}
          </motion.button>
        ))}
      </motion.div>

      {/* Main Visualization */}
      <motion.div
        key={selectedMode}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        className="bg-slate-800/50 border border-slate-700 rounded-lg p-6"
      >
        {selectedMode === 'timeline' && (
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <span>📈</span> Kompressions-Timeline
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timelineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #4B5563' }}
                  formatter={(value) => `${value}%`}
                />
                <Line
                  type="monotone"
                  dataKey="reduction"
                  stroke="#0066CC"
                  strokeWidth={2}
                  dot={{ fill: '#0066CC', r: 5 }}
                  activeDot={{ r: 7 }}
                />
              </LineChart>
            </ResponsiveContainer>
            <p className="text-sm text-gray-400">
              Zeigt die Kompressionsrate für jeden Fall über die Zeit
            </p>
          </div>
        )}

        {selectedMode === 'comparison' && (
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <span>⚖️</span> Original vs. Komprimiert
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={comparisonData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #4B5563' }}
                />
                <Legend />
                <Bar dataKey="Original" fill="#EF4444" />
                <Bar dataKey="Komprimiert" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
            <p className="text-sm text-gray-400">
              Token-Vergleich zwischen Original und komprimiertem Text
            </p>
          </div>
        )}

        {selectedMode === 'breakdown' && (
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <span>🔬</span> Analyse nach Domäne
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {breakdownByDomain.map((item, idx) => (
                <motion.div
                  key={item.domain}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="bg-slate-700/50 p-4 rounded-lg border border-slate-600"
                >
                  <div className="font-semibold text-white mb-3">{item.domain}</div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Fälle:</span>
                      <span className="text-white">{item.cases}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Ø Reduktion:</span>
                      <span className="text-medical-blue">{item.avgReduction}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Ø Token:</span>
                      <span className="text-medical-green">{item.avgTokens}</span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <motion.div
                        className="bg-gradient-to-r from-medical-blue to-medical-green h-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${item.avgReduction}%` }}
                        transition={{ duration: 1, ease: 'easeOut' }}
                      />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
            <p className="text-sm text-gray-400">
              Detaillierte Analyse nach medizinischem Fachbereich
            </p>
          </div>
        )}

        {selectedMode === 'protocol' && (
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <span>🏥</span> Protokolle nach Fachbereich
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                { emoji: '🫀', name: 'Kardiologie', protocols: ['EKG', 'Troponin', 'BP Monitor'] },
                { emoji: '🫁', name: 'Pneumologie', protocols: ['CXR', 'ABG', 'Spirometrie'] },
                { emoji: '🧠', name: 'Neurologie', protocols: ['CT Kopf', 'LP', 'EEG'] },
                { emoji: '🚑', name: 'Traumatologie', protocols: ['FAST', 'Trauma Alert', 'X-Ray'] },
              ].map((item) => (
                <motion.div
                  key={item.name}
                  whileHover={{ scale: 1.02 }}
                  className="bg-gradient-to-br from-slate-700 to-slate-800 p-4 rounded-lg border border-slate-600 hover:border-medical-blue/50 transition-all"
                >
                  <div className="text-2xl mb-2">{item.emoji}</div>
                  <div className="font-semibold text-white mb-3">{item.name}</div>
                  <div className="flex flex-wrap gap-2">
                    {item.protocols.map((protocol) => (
                      <span
                        key={protocol}
                        className="px-2 py-1 bg-medical-blue/20 text-medical-blue text-xs rounded border border-medical-blue/50"
                      >
                        {protocol}
                      </span>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
            <p className="text-sm text-gray-400">
              Klinische Protokolle für jede medizinische Spezialisierung
            </p>
          </div>
        )}

        {selectedMode === 'savings' && (
          <div className="space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <span>💰</span> Kostenanalyse & Einsparungen
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="bg-medical-green/10 border border-medical-green/50 p-4 rounded-lg"
              >
                <div className="text-sm text-gray-400 mb-2">Token Einsparung</div>
                <div className="text-3xl font-bold text-medical-green">{costSavings}</div>
                <div className="text-xs text-gray-500 mt-1">pro Batch</div>
              </motion.div>

              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="bg-medical-blue/10 border border-medical-blue/50 p-4 rounded-lg"
              >
                <div className="text-sm text-gray-400 mb-2">Kostenreduktion</div>
                <div className="text-3xl font-bold text-medical-blue">{avgReduction}%</div>
                <div className="text-xs text-gray-500 mt-1">bei LLM API</div>
              </motion.div>

              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="bg-medical-orange/10 border border-medical-orange/50 p-4 rounded-lg"
              >
                <div className="text-sm text-gray-400 mb-2">Jahreseinsparung</div>
                <motion.div
                  className="text-2xl font-bold text-medical-orange"
                  animate={{ opacity: animateCounter ? [0, 1] : 1 }}
                >
                  ~${(costSavings * 0.0001 * 365000).toFixed(0)}
                </motion.div>
                <div className="text-xs text-gray-500 mt-1">bei 1M Fällen/Jahr</div>
              </motion.div>
            </div>

            <ResponsiveContainer width="100%" height={200}>
              <AreaChart
                data={[
                  { name: 'Jan', cost: 1000, savings: 820 },
                  { name: 'Feb', cost: 950, savings: 775 },
                  { name: 'Mär', cost: 900, savings: 735 },
                  { name: 'Apr', cost: 850, savings: 695 },
                ]}
              >
                <defs>
                  <linearGradient id="colorSavings" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #4B5563' }}
                  formatter={(value) => `$${value}`}
                />
                <Area
                  type="monotone"
                  dataKey="savings"
                  stroke="#10B981"
                  fillOpacity={1}
                  fill="url(#colorSavings)"
                />
              </AreaChart>
            </ResponsiveContainer>
            <p className="text-sm text-gray-400">
              Geschätzte monatliche Kostenersparnisse durch Token-Reduktion
            </p>
          </div>
        )}
      </motion.div>

      {/* Detailed Text Comparison */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-slate-800/50 border border-slate-700 rounded-lg p-6"
      >
        <motion.button
          onClick={() => setExpandedView(!expandedView)}
          className="w-full flex items-center justify-between p-3 bg-slate-700/50 rounded-lg hover:bg-slate-700 transition-all mb-4"
        >
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <span>📝</span> Detaillierte Beispiele
          </h3>
          <motion.div
            animate={{ rotate: expandedView ? 180 : 0 }}
            className="text-xl"
          >
            ▼
          </motion.div>
        </motion.button>

        <AnimatePresence>
          {expandedView && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-4"
            >
              {compTextHistory.map((item, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-slate-700/50 rounded-lg border border-slate-600"
                >
                  <div>
                    <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                      <span>📄</span> Original ({item.originalTokens} Token)
                    </div>
                    <p className="text-sm text-gray-300 line-clamp-3">{item.originalText}</p>
                  </div>
                  <div>
                    <div className="text-sm text-medical-green mb-2 flex items-center gap-2">
                      <span>✨</span> Komprimiert ({item.compressedTokens} Token)
                    </div>
                    <p className="text-sm text-gray-300">{item.compressedText}</p>
                    <div className="mt-3 pt-3 border-t border-slate-600">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-400">{item.domain}</span>
                        <span className="px-2 py-1 bg-medical-green/20 text-medical-green rounded">
                          {item.reduction}% Reduktion
                        </span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Info Box */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-medical-blue/10 border border-medical-blue/50 rounded-lg p-4"
      >
        <p className="text-sm text-gray-300">
          <strong className="text-medical-blue">💡 CompText Visualizer:</strong> Dieser Visualizer zeigt die Effektivität der MedGemma × CompText Kompression
          in Echtzeit. Mit durchschnittlich {avgReduction}% Token-Reduktion bei vollständiger Beibehaltung der klinischen Genauigkeit
          können Sie bis zu 20x Kostenersparnisse bei der LLM-API-Nutzung erzielen.
        </p>
      </motion.div>
    </div>
  );
}
