import React, { useState } from 'react';
import { Mic } from 'lucide-react';
import { motion } from 'framer-motion';
import interviewMockImg from '../../static/interviewwww.png';

const InterviewSimulatorDashboard = () => {
  const EASE = [0.22, 1, 0.36, 1];
  const [jobs] = useState([
    {
      id: 1,
      title: 'Senior Frontend Developer',
      company: 'TechCorp Inc.',
      location: 'Remote',
      type: 'Full-time',
      exp: '5+ years',
      tags: ['React', 'AWS', 'Node.js'],
      color: 'border-blue-500',
    },
    {
      id: 2,
      title: 'Full Stack Engineer',
      company: 'StartupHub',
      location: 'San Francisco, CA',
      type: 'Full-time',
      tags: ['React', 'AWS'],
      color: 'border-slate-600',
    },
    {
      id: 3,
      title: 'React Developer',
      company: 'Digital Solutions',
      tags: ['JavaScript', 'AWS', 'Node.js'],
      color: 'border-green-500',
      active: true,
    },
    {
      id: 4,
      title: 'AI Recommendation Engine',
      company: 'Innovatate Labs',
      location: 'Remote',
      type: 'Full-time',
      exp: '2-3 years',
      tags: ['Spring Boot'],
      color: 'border-blue-400',
    },
  ]);

  return (
    <div className="w-full min-h-[560px] bg-[#000000] p-4 sm:p-5 font-sans text-slate-200 relative overflow-hidden">
      <div className="relative z-10 flex justify-between items-center mb-4 sm:mb-5">
        <span className="uppercase text-[0.66rem] sm:text-[0.74rem] font-bold tracking-widest text-slate-500">
          Interview Analytics
        </span>
        <h3 className="text-xl sm:text-2xl font-bold text-slate-100 tracking-tight">ZedReq</h3>
      </div>

      <div className="relative z-10 flex flex-col gap-5 items-stretch">
        <motion.div
          className="w-full bg-[#0f1113] rounded-2xl border border-white/10 overflow-hidden shadow-[0_0_28px_rgba(21,133,161,0.24),0_0_60px_rgba(21,133,161,0.14)]"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.6, delay: 0.2, ease: EASE }}
        >
          <motion.div
            className="p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.8, delay: 2.0, ease: EASE }}
          >
            <div className="flex items-center gap-2 mb-2">
              <Mic className="w-4 h-4 text-[#1585A1]" />
              <h4 className="text-base sm:text-lg font-bold text-slate-100">AI Mock Interview</h4>
            </div>
            <p className="text-sm sm:text-base text-slate-300 leading-relaxed mb-3">
              Role-specific questions and instant coaching to improve your structure, clarity, and confidence.
            </p>

            <motion.div
              className="relative rounded-xl overflow-hidden aspect-[16/8.5] sm:aspect-[16/8] bg-[#0d0d0d] border border-white/10"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1.6, delay: 2.5, ease: EASE }}
            >
              <img
                src={interviewMockImg}
                alt="AI mock interview session"
                className="w-full h-full object-cover"
                loading="lazy"
                decoding="async"
              />
              <div className="absolute left-3 top-3 px-2.5 py-1 rounded-md bg-black/40 text-xs sm:text-sm text-white/90 border border-white/15">
                Live Session
              </div>

            </motion.div>
          </motion.div>
        </motion.div>

        <motion.div
          className="w-full bg-[#0f1113] rounded-2xl border border-white/10 p-4 sm:p-5 shadow-[0_20px_46px_-10px_rgba(0,0,0,0.62)]"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.6, delay: 4.0, ease: EASE }}
        >
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.8, delay: 5.8, ease: EASE }}
          >
            <div className="flex items-center gap-2 mb-2">
              <h4 className="text-base sm:text-lg font-bold text-slate-100">AI Recommended Jobs</h4>
            </div>
            <p className="text-sm sm:text-base text-slate-300 mb-3 font-medium">
              Based on your resume and profile
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {jobs.map((job, idx) => (
                <motion.div
                  key={job.id}
                  className={`p-3 rounded-xl text-white border-l-4 transition-all hover:-translate-y-0.5 cursor-pointer ${
                    job.active
                      ? `bg-[#1e2329] ${job.color} ring-1 ring-[#1585A1]/40`
                      : `bg-[#16181b] ${job.color}`
                  }`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 1.1, delay: 6.2 + idx * 0.35, ease: EASE }}
                >
                  <h5 className="font-bold text-sm sm:text-base mb-1 leading-snug">{job.title}</h5>
                  <p className="text-xs sm:text-sm text-slate-300 mb-2">{job.company}</p>

                  <div className="flex flex-wrap gap-1.5 mb-2">
                    {job.location && (
                      <span className="text-[0.7rem] sm:text-xs text-slate-300">{job.location}</span>
                    )}
                    {job.type && (
                      <span className="text-[0.7rem] sm:text-xs text-slate-300">{job.type}</span>
                    )}
                    {job.exp && (
                      <span className="text-[0.7rem] sm:text-xs text-slate-300">{job.exp}</span>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-1">
                    {job.tags.map((tag) => (
                      <span key={tag} className="px-2 py-0.5 rounded-full bg-white/5 text-[0.68rem] sm:text-[0.75rem] text-[#8dc9d9]">
                        {tag}
                      </span>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>

            <motion.div
              className="mt-3 flex justify-between items-center text-[0.72rem] sm:text-xs font-bold text-slate-400 uppercase tracking-widest"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1.0, delay: 7.8, ease: EASE }}
            >
              <span>Software Engineer</span>
              <span>Recommendation Engine</span>
            </motion.div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
};

export default InterviewSimulatorDashboard;
