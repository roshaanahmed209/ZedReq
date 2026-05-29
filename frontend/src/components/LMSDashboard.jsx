import React, { useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import {
  Home,
  Users,
  Briefcase,
  MessageSquare,
  Bell,
  Search,
  LogOut,
  BarChart3,
  LineChart,
  CheckCircle2,
} from 'lucide-react';

const sidebarItems = ['All Courses', 'In Progress', 'Completed', 'Not Started'];

const courses = [
  {
    id: 'TE',
    title: 'Technical Skills for Mid-Level Roles',
    desc: 'Essential technical tracks for mid-level engineering roles and practical interview readiness.',
    color: 'bg-[#1585A1]',
  },
  {
    id: 'NW',
    title: 'Navigating Workplace Dynamics',
    desc: 'Build communication, collaboration, and leadership habits that accelerate career growth.',
    color: 'bg-[#3b82f6]',
  },
];

const stats = [
  { label: 'TOTAL QUESTIONS', value: 36, active: true },
  { label: 'CORRECT ANSWERS', value: 24, active: false },
  { label: 'WRONG ANSWERS', value: 12, active: false },
];

const navItems = [
  { icon: Home, label: 'Home', active: true },
  { icon: Users, label: 'Network' },
  { icon: Briefcase, label: 'Jobs' },
  { icon: MessageSquare, label: 'Messages' },
  { icon: Bell, label: 'Notifications' },
];

const weeklyData = [38, 52, 44, 61, 73, 66, 79, 70];
const domainData = [22, 36, 41, 33, 58, 64, 57, 71];

const LMSDashboard = () => {
  const rootRef = useRef(null);
  const isInView = useInView(rootRef, { once: true, amount: 0.3 });
  const maxWeekly = Math.max(...weeklyData);
  const maxDomain = Math.max(...domainData);
  const EASE = [0.22, 1, 0.36, 1];

  return (
    <div className="w-full min-h-[560px] bg-[var(--fp-canvas)] p-3 sm:p-4 font-sans text-slate-200 overflow-hidden">
      <motion.div
        ref={rootRef}
        className="w-full bg-[#0f1113] rounded-[22px] border border-white/10 overflow-hidden"
        initial={{ opacity: 0, y: 36, boxShadow: '0 0 0 rgba(21,133,161,0), 0 0 0 rgba(0,0,0,0)' }}
        animate={
          isInView
            ? {
                opacity: 1,
                y: 0,
                boxShadow: '0 0 26px rgba(21,133,161,0.2), 0 22px 52px -12px rgba(0,0,0,0.7)',
              }
            : {
                opacity: 0,
                y: 36,
                boxShadow: '0 0 0 rgba(21,133,161,0), 0 0 0 rgba(0,0,0,0)',
              }
        }
        transition={{
          opacity: { duration: 0.55, delay: 0.05, ease: EASE },
          y: { duration: 0.55, delay: 0.05, ease: EASE },
          boxShadow: { duration: 0.55, delay: 0.5, ease: EASE },
        }}
      >
        <motion.header
          className="px-4 py-3 sm:px-5 flex items-center justify-between border-b border-white/5 bg-[#0f1113]"
          initial={{ opacity: 0, y: 18 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 18 }}
          transition={{ duration: 0.45, delay: 0.12, ease: EASE }}
        >
          <div className="flex items-center gap-3">
            <span className="text-[#1585A1] font-bold text-base sm:text-lg tracking-tight">ZedReq</span>
            <Search size={15} className="text-slate-500" />
          </div>

          <nav className="hidden md:flex items-center gap-5">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.label}
                  className={`flex flex-col items-center gap-1 cursor-pointer transition-colors ${
                    item.active
                      ? 'text-slate-100 border-b-2 border-[#1585A1] pb-1'
                      : 'text-slate-500 hover:text-slate-300'
                  }`}
                >
                  <Icon size={15} />
                  <span className="text-[0.56rem] font-medium">{item.label}</span>
                </div>
              );
            })}
          </nav>

          <button className="px-2.5 py-1 border border-white/20 rounded text-slate-400 text-[0.62rem] flex items-center gap-1.5 hover:bg-white/5">
            Logout <LogOut size={11} />
          </button>
        </motion.header>

        <motion.div
          className="flex flex-col lg:flex-row"
          initial={{ opacity: 0, y: 18 }}
          animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 18 }}
          transition={{ duration: 0.45, delay: 0.22, ease: EASE }}
        >
          <motion.aside
            className="w-full lg:w-64 border-b lg:border-b-0 lg:border-r border-white/5 p-4 flex flex-col gap-4"
            initial={{ opacity: 0, y: 14 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 14 }}
            transition={{ duration: 0.42, delay: 0.32, ease: EASE }}
          >
            <div>
              <h2 className="text-slate-200 font-semibold text-sm mb-1">Learning Management</h2>
              <p className="text-[0.66rem] text-slate-500 mb-4">Explore and learn</p>

              <div className="flex flex-wrap lg:flex-col gap-1.5">
                {sidebarItems.map((item, i) => (
                  <div
                    key={item}
                    className={`px-3 py-2 rounded-lg text-xs cursor-pointer ${
                      i === 0
                        ? 'bg-[#1585A1]/15 text-[#8dc9d9] border border-[#1585A1]/35'
                        : 'text-slate-400 hover:bg-white/5'
                    }`}
                  >
                    {item}
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-2.5">
              {courses.map((course) => (
                <div key={course.id} className="p-3 bg-[#16181b] rounded-xl border border-white/5 hover:border-white/15 transition-all">
                  <div className="flex gap-2.5 items-start">
                    <div
                      className={`w-8 h-8 rounded-lg ${course.color} flex-shrink-0 flex items-center justify-center text-[0.62rem] font-bold text-white`}
                    >
                      {course.id}
                    </div>
                    <div>
                      <h4 className="text-slate-100 text-xs font-bold leading-tight mb-1">{course.title}</h4>
                      <p className="text-[0.66rem] text-slate-400 leading-tight line-clamp-2">{course.desc}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.aside>

          <motion.main
            className="flex-1 p-4 sm:p-5 bg-[#0f1113]"
            initial={{ opacity: 0, y: 14 }}
            animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 14 }}
            transition={{ duration: 0.45, delay: 0.42, ease: EASE }}
          >
            <div className="flex items-center gap-2 mb-2">
              <h3 className="text-base sm:text-lg font-bold text-slate-100">AI-Powered Learning Platform</h3>
              <span className="px-2 py-0.5 bg-[#1585A1] text-[0.56rem] font-black text-white rounded-md">AI</span>
            </div>
            <p className="text-xs text-slate-400 max-w-2xl leading-relaxed mb-4">
              Intelligent recommendations adapt course paths based on your profile, job targets, and performance trends.
            </p>

            <div className="grid grid-cols-2 xl:grid-cols-4 gap-2.5 mb-3">
              {stats.map((stat) => (
                <div
                  key={stat.label}
                  className={`p-3 rounded-xl border h-24 flex flex-col justify-between ${
                    stat.active
                      ? 'bg-[#1e2329] border-[#1585A1]/45 ring-1 ring-[#1585A1]/20'
                      : 'bg-[#16181b] border-white/5'
                  }`}
                >
                  <span className={`text-lg font-bold ${stat.active ? 'text-[#8dc9d9]' : 'text-slate-300'}`}>
                    {stat.value}
                  </span>
                  <span className="text-[0.6rem] font-bold text-slate-500 tracking-wider">{stat.label}</span>
                </div>
              ))}

              <div className="p-3 rounded-xl bg-[#16181b] border border-white/5 flex flex-col items-center justify-center relative">
                <span className="absolute top-2 left-3 text-[0.58rem] font-bold text-slate-500 flex items-center gap-1">
                  <CheckCircle2 size={9} /> Accuracy
                </span>
                <div className="w-14 h-14 rounded-full border-4 border-slate-800 flex items-center justify-center mt-2">
                  <div className="text-center">
                    <div className="text-xs font-bold text-slate-200">66%</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-2.5">
              <div className="bg-[#16181b] border border-white/5 rounded-xl p-3">
                <div className="flex items-center gap-2 mb-3">
                  <BarChart3 size={13} className="text-slate-500" />
                  <span className="text-xs font-bold text-slate-300">Weekly Performance</span>
                </div>
                <div className="h-24 border border-white/10 rounded-md p-2 flex items-end gap-1">
                  {weeklyData.map((value, idx) => (
                    <div key={`w-${idx}`} className="flex-1 flex flex-col justify-end h-full">
                      <div
                        className="w-full rounded-sm bg-[#1585A1]/85"
                        style={{ height: `${Math.max(12, (value / maxWeekly) * 100)}%` }}
                      />
                    </div>
                  ))}
                </div>
                <div className="mt-2 flex justify-between text-[0.58rem] text-slate-500 uppercase">
                  <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span>
                  <span>Fri</span><span>Sat</span><span>Sun</span><span>Mon</span>
                </div>
              </div>

              <div className="bg-[#16181b] border border-white/5 rounded-xl p-3">
                <div className="flex items-center gap-2 mb-3">
                  <LineChart size={13} className="text-slate-500" />
                  <span className="text-xs font-bold text-slate-300">Domain Performance</span>
                </div>
                <div className="h-24 border border-white/10 rounded-md p-2">
                  <svg viewBox="0 0 100 40" className="w-full h-full">
                    {[8, 16, 24, 32].map((y) => (
                      <line
                        key={`h-${y}`}
                        x1="0"
                        y1={y}
                        x2="100"
                        y2={y}
                        stroke="rgba(255,255,255,0.08)"
                        strokeWidth="0.6"
                      />
                    ))}
                    {[12.5, 25, 37.5, 50, 62.5, 75, 87.5].map((x) => (
                      <line
                        key={`v-${x}`}
                        x1={x}
                        y1="0"
                        x2={x}
                        y2="40"
                        stroke="rgba(255,255,255,0.06)"
                        strokeWidth="0.5"
                      />
                    ))}
                    <polyline
                      fill="none"
                      stroke="#1585A1"
                      strokeWidth="1.8"
                      points={domainData
                        .map((value, idx) => `${(idx / (domainData.length - 1)) * 100},${40 - (value / maxDomain) * 34}`)
                        .join(' ')}
                    />
                    {domainData.map((value, idx) => (
                      <circle
                        key={`d-${idx}`}
                        cx={(idx / (domainData.length - 1)) * 100}
                        cy={40 - (value / maxDomain) * 34}
                        r="1.6"
                        fill="#8dc9d9"
                      />
                    ))}
                  </svg>
                </div>
                <div className="mt-2 flex justify-between text-[0.58rem] text-slate-500">
                  <span>0</span><span>250</span><span>500</span><span>750</span><span>1000</span>
                </div>
              </div>
            </div>
          </motion.main>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default LMSDashboard;
