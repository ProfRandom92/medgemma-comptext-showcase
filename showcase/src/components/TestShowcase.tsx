'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronRight, Check, AlertCircle, Play, Pause } from 'lucide-react';

interface TestCase {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'passed' | 'failed';
  duration?: number;
  category: 'dashboard' | 'demo2' | 'visualizer';
}

const initialTests: TestCase[] = [
  // Dashboard Tests
  {
    id: 'dashboard-1',
    name: 'Should load dashboard with all sections visible',
    description: 'Verify hero section, feature cards, and input area',
    status: 'pending',
    category: 'dashboard',
  },
  {
    id: 'dashboard-2',
    name: 'Should switch between demo and visualizer tabs',
    description: 'Test tab navigation functionality',
    status: 'pending',
    category: 'dashboard',
  },
  {
    id: 'dashboard-3',
    name: 'Should process clinical text and display results',
    description: 'Fill clinical text and verify results appear',
    status: 'pending',
    category: 'dashboard',
  },
  {
    id: 'dashboard-4',
    name: 'Should display pipeline flow animation',
    description: 'Verify Nurse → Triage → Doctor stages visible',
    status: 'pending',
    category: 'dashboard',
  },
  {
    id: 'dashboard-5',
    name: 'Should display token visualization',
    description: 'Verify compression percentage is shown',
    status: 'pending',
    category: 'dashboard',
  },

  // Demo 2 Tests
  {
    id: 'demo2-1',
    name: 'Should load demo2 page with hospital workflow',
    description: 'Verify workflow view is visible',
    status: 'pending',
    category: 'demo2',
  },
  {
    id: 'demo2-2',
    name: 'Should start batch processing and show progress',
    description: 'Process 4 clinical cases',
    status: 'pending',
    category: 'demo2',
  },
  {
    id: 'demo2-3',
    name: 'Should display performance metrics after processing',
    description: 'Show total patients, avg time, success rate',
    status: 'pending',
    category: 'demo2',
  },
  {
    id: 'demo2-4',
    name: 'Should show clinical case details in batch results',
    description: 'Display Maria, James, Patricia, David cases',
    status: 'pending',
    category: 'demo2',
  },
  {
    id: 'demo2-5',
    name: 'Should display clinical domains and priority levels',
    description: 'Show 🫀🫁🧠🚑 and P1/P2/P3 badges',
    status: 'pending',
    category: 'demo2',
  },

  // Visualizer Tests
  {
    id: 'viz-1',
    name: 'Should load visualizer with default timeline view',
    description: 'Timeline mode loads with data',
    status: 'pending',
    category: 'visualizer',
  },
  {
    id: 'viz-2',
    name: 'Should display header statistics',
    description: 'Show Original, Compressed, Reduction, Savings cards',
    status: 'pending',
    category: 'visualizer',
  },
  {
    id: 'viz-3',
    name: 'Should switch between visualization modes',
    description: 'Test Timeline, Comparison, Analysis, Protocol, Savings',
    status: 'pending',
    category: 'visualizer',
  },
  {
    id: 'viz-4',
    name: 'Should display timeline chart with data points',
    description: 'Verify SVG chart renders',
    status: 'pending',
    category: 'visualizer',
  },
  {
    id: 'viz-5',
    name: 'Should display text comparison',
    description: 'Show original vs compressed examples',
    status: 'pending',
    category: 'visualizer',
  },
];

export function TestShowcase() {
  const [tests, setTests] = useState<TestCase[]>(initialTests);
  const [isRunning, setIsRunning] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<
    'all' | 'dashboard' | 'demo2' | 'visualizer'
  >('all');

  const filteredTests =
    selectedCategory === 'all'
      ? tests
      : tests.filter((t) => t.category === selectedCategory);

  const stats = {
    total: filteredTests.length,
    passed: filteredTests.filter((t) => t.status === 'passed').length,
    failed: filteredTests.filter((t) => t.status === 'failed').length,
    running: filteredTests.filter((t) => t.status === 'running').length,
    pending: filteredTests.filter((t) => t.status === 'pending').length,
  };

  const runTests = async () => {
    setIsRunning(true);

    for (let i = 0; i < filteredTests.length; i++) {
      const test = filteredTests[i];

      // Set to running
      setTests((prev) =>
        prev.map((t) => (t.id === test.id ? { ...t, status: 'running' } : t))
      );

      // Simulate test duration
      const duration = Math.random() * 2000 + 500; // 500-2500ms
      await new Promise((resolve) => setTimeout(resolve, duration));

      // Random pass/fail (90% pass rate)
      const passed = Math.random() > 0.1;

      // Set result
      setTests((prev) =>
        prev.map((t) =>
          t.id === test.id
            ? {
                ...t,
                status: passed ? 'passed' : 'failed',
                duration: Math.round(duration),
              }
            : t
        )
      );

      await new Promise((resolve) => setTimeout(resolve, 300));
    }

    setIsRunning(false);
  };

  const resetTests = () => {
    setTests((prev) =>
      prev.map((t) => ({ ...t, status: 'pending', duration: undefined }))
    );
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-bold text-white mb-2">🎭 Test Showcase</h1>
        <p className="text-gray-400">
          Interactive demonstration of Playwright E2E tests
        </p>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8"
      >
        {[
          { label: 'Total', value: stats.total, color: 'text-slate-300' },
          { label: 'Passed', value: stats.passed, color: 'text-green-400' },
          { label: 'Failed', value: stats.failed, color: 'text-red-400' },
          { label: 'Running', value: stats.running, color: 'text-yellow-400' },
          { label: 'Pending', value: stats.pending, color: 'text-gray-400' },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-slate-800/50 border border-slate-600 rounded-lg p-4 text-center"
          >
            <div className={`text-2xl font-bold ${stat.color}`}>
              {stat.value}
            </div>
            <div className="text-sm text-gray-400">{stat.label}</div>
          </div>
        ))}
      </motion.div>

      {/* Controls */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="flex gap-4 mb-8 flex-wrap"
      >
        <button
          onClick={runTests}
          disabled={isRunning}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded-lg transition"
        >
          <Play size={18} />
          {isRunning ? 'Running...' : 'Run Tests'}
        </button>

        <button
          onClick={resetTests}
          disabled={isRunning}
          className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:bg-gray-600 text-white rounded-lg transition"
        >
          <Pause size={18} />
          Reset
        </button>

        <div className="flex gap-2">
          {['all', 'dashboard', 'demo2', 'visualizer'].map((cat) => (
            <button
              key={cat}
              onClick={() =>
                setSelectedCategory(
                  cat as 'all' | 'dashboard' | 'demo2' | 'visualizer'
                )
              }
              className={`px-3 py-2 rounded-lg transition text-sm ${
                selectedCategory === cat
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
              }`}
            >
              {cat === 'all'
                ? 'All'
                : cat === 'dashboard'
                  ? '📋 Dashboard'
                  : cat === 'demo2'
                    ? '🏥 Demo 2'
                    : '📊 Visualizer'}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Progress Bar */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="mb-8"
      >
        <div className="flex justify-between text-sm text-gray-400 mb-2">
          <span>Progress</span>
          <span>
            {stats.passed + stats.failed} / {stats.total}
          </span>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-green-400 to-green-600"
            initial={{ width: 0 }}
            animate={{
              width: `${((stats.passed + stats.failed) / stats.total) * 100}%`,
            }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </motion.div>

      {/* Test Cases */}
      <div className="space-y-3">
        {filteredTests.map((test, index) => (
          <motion.div
            key={test.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 + index * 0.05 }}
            className={`p-4 rounded-lg border transition ${
              test.status === 'passed'
                ? 'bg-green-900/20 border-green-600/30'
                : test.status === 'failed'
                  ? 'bg-red-900/20 border-red-600/30'
                  : test.status === 'running'
                    ? 'bg-yellow-900/20 border-yellow-600/30'
                    : 'bg-slate-800/30 border-slate-600/30'
            }`}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  {test.status === 'passed' && (
                    <Check size={18} className="text-green-400" />
                  )}
                  {test.status === 'failed' && (
                    <AlertCircle size={18} className="text-red-400" />
                  )}
                  {test.status === 'running' && (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity }}
                      className="text-yellow-400"
                    >
                      <Play size={18} />
                    </motion.div>
                  )}
                  {test.status === 'pending' && (
                    <div className="w-4 h-4 rounded-full border-2 border-slate-500" />
                  )}

                  <h3 className="font-semibold text-white">{test.name}</h3>
                </div>
                <p className="text-sm text-gray-400 ml-7">{test.description}</p>
              </div>

              <div className="text-right whitespace-nowrap">
                {test.duration && (
                  <div className="text-sm text-gray-400">{test.duration}ms</div>
                )}
                <div
                  className={`text-xs font-semibold mt-1 ${
                    test.status === 'passed'
                      ? 'text-green-400'
                      : test.status === 'failed'
                        ? 'text-red-400'
                        : test.status === 'running'
                          ? 'text-yellow-400'
                          : 'text-gray-400'
                  }`}
                >
                  {test.status.toUpperCase()}
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Legend */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="mt-12 p-6 bg-slate-800/30 border border-slate-600/30 rounded-lg"
      >
        <h3 className="text-sm font-semibold text-gray-300 mb-3">About</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-400">
          <div>
            <span className="font-semibold text-gray-300">📊 52 Tests:</span>{' '}
            Comprehensive E2E coverage
          </div>
          <div>
            <span className="font-semibold text-gray-300">⚡ Fast:</span> ~85
            seconds total (parallel)
          </div>
          <div>
            <span className="font-semibold text-gray-300">✓ Reliable:</span>{' '}
            No flaky tests with auto-waiting
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-slate-600/30 text-xs text-gray-500">
          <p>
            💡 This is a simulated test runner. For actual tests, run:{' '}
            <code className="bg-slate-900 px-2 py-1 rounded">
              npm run test:e2e
            </code>
          </p>
        </div>
      </motion.div>

      {/* Quick Links */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.9 }}
        className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4"
      >
        {[
          {
            title: '📖 Testing Guide',
            desc: 'Read PLAYWRIGHT_TESTING_GUIDE.md',
          },
          {
            title: '🏗️ Best Practices',
            desc: 'Read E2E_TESTING_BEST_PRACTICES.md',
          },
          {
            title: '🚀 Run Tests',
            desc: 'Read RUN_TESTS.md for execution',
          },
        ].map((link) => (
          <div
            key={link.title}
            className="p-4 bg-slate-800/50 border border-slate-600/30 rounded-lg hover:border-slate-500/50 transition cursor-pointer"
          >
            <h4 className="font-semibold text-white flex items-center gap-2">
              {link.title}
              <ChevronRight size={16} />
            </h4>
            <p className="text-sm text-gray-400 mt-1">{link.desc}</p>
          </div>
        ))}
      </motion.div>
    </div>
  );
}
