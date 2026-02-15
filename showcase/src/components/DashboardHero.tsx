'use client';

import { motion } from 'framer-motion';
import { ArrowRight, Trophy, Zap, Sparkles } from 'lucide-react';

export function DashboardHero() {
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30, filter: 'blur(10px)' },
    show: {
      opacity: 1,
      y: 0,
      filter: 'blur(0px)',
      transition: { duration: 0.7, ease: 'easeOut' },
    },
  };

  const floatingVariants = {
    animate: {
      y: [0, -10, 0],
      transition: { duration: 4, repeat: Infinity, ease: 'easeInOut' },
    },
  };

  const features = [
    {
      icon: '🫀',
      title: '92-95% Token Reduction',
      desc: 'Intelligent clinical text compression',
    },
    {
      icon: '⚡',
      title: '<50ms Processing',
      desc: 'Real-time clinical data handling',
    },
    {
      icon: '🔒',
      title: 'HIPAA-Compatible',
      desc: 'Edge-first privacy architecture',
    },
    {
      icon: '♾️',
      title: 'Infinitely Scalable',
      desc: 'Stateless, production-ready design',
    },
  ];

  return (
    <motion.section
      className="relative overflow-hidden py-32 px-4 sm:px-6 lg:px-8"
      initial="hidden"
      animate="show"
      variants={containerVariants}
    >
      {/* Enhanced Background gradients */}
      <div className="absolute inset-0 bg-gradient-to-b from-blue-600/15 via-cyan-600/5 to-slate-950/50 pointer-events-none" />
      <motion.div
        className="absolute top-0 right-0 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl pointer-events-none"
        animate={{ opacity: [0.5, 0.8, 0.5] }}
        transition={{ duration: 8, repeat: Infinity }}
      />
      <motion.div
        className="absolute bottom-0 left-0 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"
        animate={{ opacity: [0.3, 0.6, 0.3] }}
        transition={{ duration: 10, repeat: Infinity, delay: 1 }}
      />
      <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(59,130,246,0.03)_25%,rgba(59,130,246,0.03)_50%,transparent_50%,transparent_75%,rgba(59,130,246,0.03)_75%,rgba(59,130,246,0.03))] bg-[length:40px_40px] pointer-events-none opacity-20" />

      <div className="relative max-w-7xl mx-auto">
        {/* Main Title */}
        <motion.div className="text-center mb-20" variants={itemVariants}>
          <motion.div
            className="inline-block mb-8"
            whileHover={{ scale: 1.08 }}
            transition={{ type: 'spring', stiffness: 300, damping: 8 }}
          >
            <div className="relative">
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-blue-600/50 via-cyan-500/30 to-blue-600/50 rounded-full blur-lg"
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 3, repeat: Infinity }}
              />
              <span className="relative px-6 py-3 rounded-full bg-gradient-to-r from-blue-600/30 to-cyan-600/20 border border-blue-400/50 text-blue-200 text-sm font-bold uppercase tracking-wider backdrop-blur-sm shadow-lg shadow-blue-500/20">
                ✨ Kaggle MedGemma Impact Challenge
              </span>
            </div>
          </motion.div>

          <motion.h1
            className="text-6xl sm:text-7xl font-black text-white mb-8 leading-tight"
            animate={floatingVariants.animate}
          >
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-300 via-cyan-300 to-blue-400 drop-shadow-lg">
              MedGemma × CompText
            </span>
          </motion.h1>

          <motion.p className="text-xl sm:text-2xl text-gray-200 max-w-4xl mx-auto mb-10 leading-relaxed font-light">
            Privacy-first clinical text compression achieving{' '}
            <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent font-bold">
              92-95% token reduction
            </span>
            {' '}for healthcare AI at{' '}
            <span className="text-emerald-400 font-semibold">enterprise scale</span>
          </motion.p>

          <motion.div className="flex flex-col sm:flex-row gap-6 justify-center" variants={itemVariants}>
            <motion.button
              whileHover={{ scale: 1.08, boxShadow: '0 30px 60px rgba(59, 130, 246, 0.4)' }}
              whileTap={{ scale: 0.95 }}
              className="group relative px-10 py-5 bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 text-white rounded-xl font-bold text-lg flex items-center justify-center gap-3 overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300"
            >
              <motion.div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity" />
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}>
                <Sparkles size={22} />
              </motion.div>
              <span className="relative">Try Live Demo</span>
            </motion.button>

            <motion.a
              href="https://www.kaggle.com/competitions/med-gemma-impact-challenge"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.08, boxShadow: '0 20px 40px rgba(31, 41, 55, 0.5)' }}
              whileTap={{ scale: 0.95 }}
              className="group relative px-10 py-5 bg-gradient-to-r from-slate-700 to-slate-800 hover:from-slate-600 hover:to-slate-700 text-white rounded-xl font-bold text-lg flex items-center justify-center gap-3 border border-slate-600 hover:border-blue-500/50 transition-all duration-300 shadow-lg"
            >
              <Trophy size={22} className="group-hover:text-yellow-400 transition-colors" />
              <span className="relative">View on Kaggle</span>
              <motion.div animate={{ x: [0, 4, 0] }} transition={{ duration: 2, repeat: Infinity }}>
                <ArrowRight size={18} />
              </motion.div>
            </motion.a>
          </motion.div>
        </motion.div>

        {/* Feature Grid - Enhanced */}
        <motion.div
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-20"
          variants={containerVariants}
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              className="group relative p-8 rounded-xl bg-gradient-to-br from-slate-800/50 via-slate-800/20 to-slate-900/50 border border-slate-700/50 hover:border-blue-500/80 transition-all duration-300 overflow-hidden"
              variants={itemVariants}
              whileHover={{ y: -8, boxShadow: '0 20px 40px rgba(59, 130, 246, 0.15)' }}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 via-transparent to-cyan-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <motion.div
                className="absolute top-0 right-0 w-20 h-20 bg-blue-500/10 rounded-full blur-2xl group-hover:bg-blue-500/20"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 4, repeat: Infinity }}
              />
              <div className="relative">
                <motion.div className="text-5xl mb-5" animate={{ scale: [1, 1.1, 1] }} transition={{ duration: 3, repeat: Infinity }}>
                  {feature.icon}
                </motion.div>
                <h3 className="text-lg font-bold text-white mb-3 group-hover:text-blue-300 transition duration-300">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-400 group-hover:text-gray-300 transition duration-300">
                  {feature.desc}
                </p>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Stats Row - Premium */}
        <motion.div
          className="grid grid-cols-2 md:grid-cols-4 gap-5 p-8 rounded-2xl bg-gradient-to-r from-slate-800/40 via-slate-800/30 to-slate-800/40 border border-slate-700/50 backdrop-blur-sm shadow-lg"
          variants={containerVariants}
        >
          {[
            { label: 'Token Reduction', value: '92-95%', icon: '📊', color: 'from-cyan-500 to-blue-500' },
            { label: 'Processing Speed', value: '<50ms', icon: '⚡', color: 'from-yellow-500 to-orange-500' },
            { label: 'Scalability', value: 'Infinite', icon: '♾️', color: 'from-emerald-500 to-green-500' },
            { label: 'Privacy Score', value: '100%', icon: '🔒', color: 'from-red-500 to-pink-500' },
          ].map((stat, i) => (
            <motion.div
              key={i}
              className="relative text-center p-4 rounded-xl bg-gradient-to-br from-slate-700/50 to-slate-800/50 border border-slate-600/50 hover:border-slate-500/80 transition-all group"
              whileHover={{ scale: 1.05, y: -4 }}
              variants={itemVariants}
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${stat.color} opacity-0 group-hover:opacity-10 rounded-xl transition-opacity`} />
              <div className="relative">
                <motion.div className="text-4xl mb-3" animate={{ scale: [1, 1.15, 1] }} transition={{ duration: 2.5, repeat: Infinity }}>
                  {stat.icon}
                </motion.div>
                <div className={`text-3xl font-black bg-clip-text text-transparent bg-gradient-to-r ${stat.color} mb-2`}>
                  {stat.value}
                </div>
                <div className="text-xs font-semibold text-gray-400 group-hover:text-gray-300 transition">{stat.label}</div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </motion.section>
  );
}
