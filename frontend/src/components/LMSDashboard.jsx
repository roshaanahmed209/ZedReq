import { useRef } from 'react';
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
import '../css/components/LMSMock.css';

const sidebarItems = ['All Courses', 'In Progress', 'Completed', 'Not Started'];

const courses = [
  {
    id: 'TE',
    title: 'Technical Skills for Mid-Level Roles',
    desc: 'Essential technical tracks for mid-level engineering roles and practical interview readiness.',
    tone: 'teal',
  },
  {
    id: 'NW',
    title: 'Navigating Workplace Dynamics',
    desc: 'Build communication, collaboration, and leadership habits that accelerate career growth.',
    tone: 'blue',
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

const EASE = [0.22, 1, 0.36, 1];

const LMSDashboard = () => {
  const rootRef = useRef(null);
  const isInView = useInView(rootRef, { once: true, amount: 0.3 });
  const maxWeekly = Math.max(...weeklyData);
  const maxDomain = Math.max(...domainData);

  return (
    <div className="lms-mock">
      <motion.div
        ref={rootRef}
        className="lms-mock__shell"
        initial={{ opacity: 0, y: 36 }}
        animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 36 }}
        transition={{ duration: 0.55, ease: EASE }}
      >
        <header className="lms-mock__nav">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span className="lms-mock__brand">ZedReq</span>
            <Search size={15} className="lms-mock__nav-icon" />
          </div>

          <nav className="lms-mock__nav-links" aria-label="App navigation">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.label}
                  className={`lms-mock__nav-link${item.active ? ' is-active' : ''}`}
                >
                  <Icon size={15} />
                  <span>{item.label}</span>
                </div>
              );
            })}
          </nav>

          <button type="button" className="lms-mock__logout">
            Logout <LogOut size={11} />
          </button>
        </header>

        <div className="lms-mock__body">
          <aside className="lms-mock__sidebar lms-mock__sidebar--wide">
            <div>
              <h2 className="lms-mock__section-title">Learning Management</h2>
              <p className="lms-mock__section-sub">Explore and learn</p>

              <div className="lms-mock__stack lms-mock__stack--sm lms-mock__section-gap">
                {sidebarItems.map((item, i) => (
                  <div
                    key={item}
                    className={`lms-mock__filter${i === 0 ? ' is-active' : ''}`}
                  >
                    {item}
                  </div>
                ))}
              </div>
            </div>

            <div className="lms-mock__courses-grid">
              {courses.map((course) => (
                <div key={course.id} className="lms-mock__course-card">
                  <div className="lms-mock__course-card-inner">
                    <div
                      className={`lms-mock__course-card-chip lms-mock__course-card-chip--${course.tone}`}
                    >
                      {course.id}
                    </div>
                    <div>
                      <h4 className="lms-mock__course-card-title">{course.title}</h4>
                      <p className="lms-mock__course-card-desc">{course.desc}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </aside>

          <main className="lms-mock__main">
            <div className="lms-mock__page-head">
              <h3 className="lms-mock__page-title">AI-Powered Learning Platform</h3>
              <span className="lms-mock__badge-ai">AI</span>
            </div>
            <p className="lms-mock__lead">
              Intelligent recommendations adapt course paths based on your profile, job targets, and performance trends.
            </p>

            <div className="lms-mock__stats-grid">
              {stats.map((stat) => (
                <div
                  key={stat.label}
                  className={`lms-mock__stat${stat.active ? ' is-active' : ''}`}
                >
                  <span className="lms-mock__stat-val">{stat.value}</span>
                  <span className="lms-mock__stat-label">{stat.label}</span>
                </div>
              ))}

              <div className="lms-mock__accuracy-ring">
                <span className="lms-mock__accuracy-label">
                  <CheckCircle2 size={9} /> Accuracy
                </span>
                <div className="lms-mock__accuracy-circle">66%</div>
              </div>
            </div>

            <div className="lms-mock__charts-grid">
              <div className="lms-mock__card">
                <div className="lms-mock__card-head">
                  <BarChart3 size={13} className="lms-mock__nav-icon" />
                  <span className="lms-mock__card-title">Weekly Performance</span>
                </div>
                <div className="lms-mock__chart-box">
                  <div className="lms-mock__chart-bars">
                    {weeklyData.map((value, idx) => (
                      <div
                        key={`w-${idx}`}
                        className="lms-mock__chart-bar"
                        style={{ height: `${Math.max(12, (value / maxWeekly) * 100)}%` }}
                      />
                    ))}
                  </div>
                </div>
                <div className="lms-mock__chart-caption">
                  <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span>
                  <span>Fri</span><span>Sat</span><span>Sun</span><span>Mon</span>
                </div>
              </div>

              <div className="lms-mock__card">
                <div className="lms-mock__card-head">
                  <LineChart size={13} className="lms-mock__nav-icon" />
                  <span className="lms-mock__card-title">Domain Performance</span>
                </div>
                <div className="lms-mock__chart-box">
                  <svg viewBox="0 0 100 40" style={{ width: '100%', height: '100%' }} aria-hidden="true">
                    {[8, 16, 24, 32].map((y) => (
                      <line
                        key={`h-${y}`}
                        x1="0"
                        y1={y}
                        x2="100"
                        y2={y}
                        stroke="var(--v1-chart-grid)"
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
                        stroke="var(--v1-chart-grid-faint)"
                        strokeWidth="0.5"
                      />
                    ))}
                    <polyline
                      fill="none"
                      stroke="var(--accent)"
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
                        fill="var(--v1-badge-text)"
                      />
                    ))}
                  </svg>
                </div>
                <div className="lms-mock__chart-caption" style={{ textTransform: 'none' }}>
                  <span>0</span><span>250</span><span>500</span><span>750</span><span>1000</span>
                </div>
              </div>
            </div>
          </main>
        </div>
      </motion.div>
    </div>
  );
};

export default LMSDashboard;
