import { motion } from 'framer-motion';
import { MessageSquare, Send, User } from 'lucide-react';

export const CAREER_ASSISTANT_COUNTS = {
  messages: 4,
  profiles: 2,
};

const messages = [
  {
    id: 1,
    type: 'bot',
    text: "Hello! I'm your AI career assistant. I can help you find jobs, optimize your resume, and answer career-related questions. How can I assist you today?",
  },
  { id: 2, type: 'user', text: 'show me SWE profiles' },
  { id: 3, type: 'bot', text: "I'll search for profiles matching 'Software Engineer'..." },
  {
    id: 4,
    type: 'bot',
    text: 'I found 10 profiles matching your query! Here are the results below with match scores to help you identify the best matches.',
  },
];

const profiles = [
  {
    id: 'C-1842',
    name: 'Ethan Carter',
    initials: 'EC',
    badge: 'Top Fit',
    match: '50%',
    active: true,
  },
  {
    id: 'C-1927',
    name: 'Olivia Bennett',
    initials: 'OB',
    badge: 'Top Fit',
    match: '49%',
    active: false,
  },
];

const CareerAssistantCards = ({
  isInView,
  aiRef,
  profilesSurface,
  EASE,
  DUR,
  GAP,
  tAi,
  tMsg0,
  tInput,
  tProfileShell,
  tProfileBlocks,
}) => (
  <div className="relative z-[1] w-full flex flex-col lg:flex-row items-start gap-5 lg:gap-0 min-h-0 grow mt-4 lg:mt-8">
    <motion.div
      ref={aiRef}
      className="flex-1 w-full min-w-0 z-10 bg-[#0f1113] rounded-[20px] border border-white/10 flex flex-col overflow-hidden relative shadow-[0_0_28px_rgba(21,133,161,0.24),0_0_60px_rgba(21,133,161,0.14)]"
      style={{ zIndex: 10 }}
      initial={false}
      variants={{
        off: { opacity: 0, y: 20 },
        on: { opacity: 1, y: 0, transition: { duration: DUR, delay: tAi, ease: EASE } },
      }}
      animate={isInView ? 'on' : 'off'}
    >
      <div className="p-5 flex items-center gap-3 border-b border-white/5">
        <div className="p-2 bg-blue-900/30 rounded-lg">
          <MessageSquare size={18} className="text-blue-400" />
        </div>
        <h2 className="text-slate-200 font-semibold text-sm">AI Career Assistant</h2>
      </div>

      <div className="p-4 sm:p-6 flex flex-col gap-3 sm:gap-4 min-h-[220px] min-[900px]:min-h-[320px] flex-1 min-h-0 justify-start overflow-hidden">
        {messages.map((msg, i) => (
          <motion.div
            key={msg.id}
            className={`${
              msg.type === 'user' ? 'self-end bg-[#2d3339] text-blue-200' : 'self-start bg-[#24272c] text-slate-400'
            } max-w-[88%] p-3 sm:p-4 rounded-2xl text-[0.75rem] sm:text-[0.875rem] leading-relaxed border border-white/5 shadow-sm`}
            initial={false}
            variants={{
              off: { opacity: 0, y: 10 },
              on: {
                opacity: 1,
                y: 0,
                transition: { duration: 0.42, delay: tMsg0 + i * GAP, ease: EASE },
              },
            }}
            animate={isInView ? 'on' : 'off'}
          >
            {msg.text}
          </motion.div>
        ))}
      </div>

      <motion.div
        className="p-4 sm:p-6 mt-auto shrink-0"
        initial={false}
        variants={{
          off: { opacity: 0, y: 8 },
          on: { opacity: 1, y: 0, transition: { duration: 0.42, delay: tInput, ease: EASE } },
        }}
        animate={isInView ? 'on' : 'off'}
      >
        <div className="relative flex items-center gap-3">
          <div className="flex-1 bg-[#111315] border border-white/10 rounded-xl px-3 sm:px-4 py-2.5 sm:py-3 text-[0.75rem] sm:text-[0.875rem] text-slate-500 italic">
            Ask me anything about your career...
          </div>
          <button
            type="button"
            className="bg-[#0ea5e9] p-3 rounded-xl text-white hover:bg-blue-500 transition-colors inline-flex"
          >
            <span className="flex items-center gap-2 px-1">
              <span className="text-xs font-bold uppercase">Send</span>
              <Send size={14} />
            </span>
          </button>
        </div>
      </motion.div>
    </motion.div>

    <motion.div
      className="w-full max-w-[20rem] mx-auto lg:mx-0 lg:mt-5 lg:w-[min(20rem,28vw)] shrink-0 aspect-square relative z-20 bg-[#0f1113] rounded-[32px] border border-white/10 flex flex-col overflow-hidden shadow-[0_20px_46px_-10px_rgba(0,0,0,0.62)]"
      style={profilesSurface}
      initial={false}
      variants={{
        off: { opacity: 0, y: 20 },
        on: {
          opacity: 1,
          y: 0,
          transition: { duration: DUR, delay: tProfileShell, ease: EASE },
        },
      }}
      animate={isInView ? 'on' : 'off'}
    >
      <div className="p-5 flex items-center gap-3 border-b border-white/5 shrink-0">
        <div className="p-2 bg-blue-500/10 rounded-lg">
          <User size={18} className="text-blue-400" />
        </div>
        <h2 className="text-slate-200 font-semibold text-sm">Matched Profiles</h2>
      </div>
      <div className="p-3 sm:p-4 grid auto-rows-fr gap-3 sm:gap-3.5 flex-1 min-h-0 overflow-hidden content-start">
        {profiles.map((profile, i) => (
          <motion.div
            key={profile.id}
            className={`p-3 sm:p-4 rounded-2xl border transition-all flex flex-col h-full min-h-0 overflow-hidden ${
              profile.active
                ? 'bg-[#1e2329] border-blue-500/50 ring-1 ring-blue-500/20 shadow-[0_0_20px_rgba(59,130,246,0.1)]'
                : 'bg-[#16181b] border-white/5'
            }`}
            initial={false}
            variants={{
              off: { opacity: 0, y: 6 },
              on: {
                opacity: 1,
                y: 0,
                transition: {
                  duration: 0.45,
                  delay: tProfileBlocks + i * 0.12,
                  ease: EASE,
                },
              },
            }}
            animate={isInView ? 'on' : 'off'}
          >
            <div className="flex justify-between items-start gap-1 mb-2">
              <div
                className={`text-[0.65rem] sm:text-xs font-bold p-2 rounded-lg shrink-0 ${
                  profile.active ? 'bg-blue-500/20 text-blue-400' : 'bg-green-500/20 text-green-400'
                }`}
              >
                {profile.initials}
              </div>
              <h3
                className="text-slate-200 font-bold text-xs sm:text-sm flex-1 min-w-0 text-right leading-snug overflow-hidden"
                style={{
                  display: '-webkit-box',
                  WebkitBoxOrient: 'vertical',
                  WebkitLineClamp: 2,
                  wordBreak: 'break-word',
                }}
              >
                {profile.name}
              </h3>
              <div
                className={`text-[0.6rem] sm:text-[0.7rem] font-bold px-2 py-1 rounded-full shrink-0 ${
                  profile.active ? 'bg-blue-500/20 text-blue-400' : 'bg-green-500/20 text-green-400'
                }`}
              >
                {profile.badge}
              </div>
            </div>
            <div className="flex items-center justify-end gap-2 mt-auto pt-2 text-[0.65rem] sm:text-xs min-w-0">
              <div
                className={`shrink-0 px-2 sm:px-2.5 py-0.5 rounded-full text-[0.62rem] sm:text-[0.75rem] font-bold border ${
                  profile.active
                    ? 'bg-blue-500/10 border-blue-500/30 text-blue-400'
                    : 'bg-green-500/10 border-green-500/30 text-green-400'
                }`}
              >
                {profile.match} Match
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  </div>
);

export default CareerAssistantCards;
