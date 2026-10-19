import { useCallback, useEffect, useRef, useState } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import '../css/pages/FirstPage.css';
import '../css/pages/LandingV1.css';
import '../css/pages/LandingV1Action.css';
import '../css/pages/LandingV1Tabs.css';
import '../css/pages/LandingV1Lms.css';
import { attachFirstPageEffects } from '../utils/firstPageEffects.js';
import { isStartupMode } from '../utils/startupMode';
import { sendReservationEmail } from '../services/emailjs';
import { getApiBaseUrl } from '../config/apiBase';
import DarkVeil from '../components/DarkVeil';
import interviewMockImg from '../../static/interviewwww.png';
import { Target, Mic, ClipboardCheck, TrendingUp } from 'lucide-react';
import { useScroll, useMotionValueEvent, useReducedMotion } from 'framer-motion';
import FirstPageGlowButton from '../components/FirstPageGlowButton';
import FirstPagePricingCard from '../components/FirstPagePricingCard';
import StackedCards from '../components/StackedCards';
import LMSDashboard from '../components/LMSDashboard';
import LMSTopicPanel from '../components/LMSTopicPanel';
import LMSQuizPanel from '../components/LMSQuizPanel';
import LMSEvaluationPanel from '../components/LMSEvaluationPanel';
import {
  PLATFORM_ACCESS_LINES,
  FREE_TEASER_WORDS,
  FREE_MONTHLY_LIMITS,
  PRO_MONTHLY_LIMITS,
  PREMIUM_MONTHLY_LIMITS,
  ENTERPRISE_USAGE_FEATURES,
} from '../constants/platformPricing';

/** Resolve a public asset URL (works in both Vite dev and production build). */
const A = (file) => `${import.meta.env.BASE_URL}assets/${file}`;

/* ─── Hero V1 — proof chips under the CTA row ──────────── */
const HERO_CHIPS = [
  { label: 'AI Mock Interviews',  icon: 'icon-interview.svg' },
  { label: 'Interview Feedback',  icon: 'icon-analytics.svg' },
  { label: 'Career Preparation',  icon: 'icon-learning.svg'  },
];

/** Hero headline + lead rotate together — all variants stay on AI mock interviews. */
const HERO_COPY_VARIANTS = [
  {
    ariaLabel:
      'Your next interview should not be your first practice interview. Practice real interview scenarios with AI.',
    line2: 'shouldn\u2019t be your first',
    line3: 'practice interview.',
    lead:
      'Practice real interview scenarios with AI, get detailed feedback, and build the skills you need to land your next role.',
  },
  {
    ariaLabel:
      'Your next interview deserves a real AI mock session. Run role-specific mocks scored in real time.',
    line2: 'deserves a real',
    line3: 'AI mock session.',
    lead:
      'Run role-specific mock interviews with an AI panel — scored on structure, clarity, and depth while you answer out loud.',
  },
  {
    ariaLabel:
      'Your next interview needs rehearsal with instant feedback. Know what to fix before the real panel.',
    line2: 'needs rehearsal',
    line3: 'with instant feedback.',
    lead:
      'Rehearse behavioral and technical questions, then get a breakdown of what landed and what to sharpen next.',
  },
  {
    ariaLabel:
      'Your next interview is not the place to wing answers. Build confidence with AI practice rounds.',
    line2: 'isn\u2019t the place',
    line3: 'to wing answers.',
    lead:
      'Turn interview nerves into a repeatable prep routine — AI sessions that feel like the real thing, without the stakes.',
  },
  {
    ariaLabel:
      'Your next interview starts with AI mock interviews. Walk in having already heard the hard questions.',
    line2: 'starts with AI',
    line3: 'mock interviews.',
    lead:
      'Practice the questions hiring managers actually ask, get scored after every round, and walk in already having answered them.',
  },
];

const HERO_SWAP_MS = 5000;
const HERO_FADE_MS = 480;
const HERO_ENTER_MS = 680;

/* ─── Hero V1 — live-session panel (right column) ──────── */
const HERO_PANEL_QUESTION =
  'Tell me about a time you shipped something under a hard deadline. What did you cut, and why?';

const HERO_PANEL_SIGNALS = [
  { label: 'Structure', pct: 82 },
  { label: 'Clarity',   pct: 74 },
  { label: 'Depth',     pct: 79 },
];

/** Overall score shown in the panel gauge. */
const HERO_PANEL_SCORE = 78;

/* ═══════════════════════════════════════════════════════════════
   SEE IT IN ACTION — section directly below the hero
════════════════════════════════════════════════════════════════ */

/** The four-step rail. `Icon` is rendered, not a string, so tree-shaking keeps only these. */
const ACTION_STEPS = [
  { Icon: Target,         title: 'Choose Role',      desc: 'Select your target job or industry.' },
  { Icon: Mic,            title: 'Get Interviewed',  desc: 'Answer real questions from our AI interviewer.' },
  { Icon: ClipboardCheck, title: 'Receive Feedback', desc: 'Get detailed insights and a score.' },
  { Icon: TrendingUp,     title: 'Improve',          desc: 'Practice again and track your progress.' },
];

/** Waveform bar heights (%) for the recording mock — fixed so the render is deterministic. */
const WAVE_BARS = [
  22, 40, 68, 92, 60, 34, 78, 100, 54, 30,
  46, 84, 66, 38, 90, 58, 26, 72, 44, 20,
];

const ACTION_STRENGTHS = [
  'Clear communication',
  'Good problem solving',
  'Relevant experience',
];

const ACTION_IMPROVEMENTS = [
  'More specific examples',
  'Stronger technical depth',
  'Better STAR structure',
];

/** Step 1 panel — role picker. */
const ROLE_OPTIONS = [
  { label: 'Frontend Engineer', meta: 'React · TypeScript', active: true },
  { label: 'Product Manager',   meta: 'B2B SaaS' },
  { label: 'Data Analyst',      meta: 'SQL · Python' },
  { label: 'Backend Engineer',  meta: 'Go · Postgres' },
  { label: 'UX Designer',       meta: 'Product design' },
];

const SENIORITY_LEVELS = ['Junior', 'Mid', 'Senior', 'Staff'];
const SENIORITY_ACTIVE = 'Senior';

/** Footer summary for the role panel — what the picked set actually produces. */
const ROLE_SUMMARY = [
  { k: 'Questions', v: '8' },
  { k: 'Length',    v: '~15 min' },
  { k: 'Mix',       v: 'Behavioural + technical' },
];

/** Step 2 panel — session chrome around the question. */
const INTERVIEW_META = { position: 'Question 2 of 8', elapsed: '01:12' };
const INTERVIEW_HINT = 'Aim for 60–90 seconds. Structure beats detail.';

/** Step 3 panel — the per-dimension marks behind the overall score. */
const FEEDBACK_BREAKDOWN = [
  { label: 'Structure', val: 82 },
  { label: 'Clarity',   val: 74 },
  { label: 'Depth',     val: 79 },
];

/** Step 4 panel — what the next session should target. */
const PROGRESS_FOCUS = ['Quantify your impact', 'Tighten the opening line'];

/** Step 4 panel — session history. Scores climb so the trend reads at a glance. */
const PROGRESS_SESSIONS = [
  { label: 'Session 1', date: 'Mon', score: 62 },
  { label: 'Session 2', date: 'Wed', score: 71 },
  { label: 'Session 3', date: 'Fri', score: 78, active: true },
];

/** How long each tab holds before auto-advancing, in ms. */
const ACTION_TAB_MS = 5200;

/**
 * True when focus arrived by keyboard rather than a click.
 *
 * Clicking a button focuses it, so a plain `onFocus` would pause the carousel on every
 * click — exactly the behaviour the tabs are meant not to have. `:focus-visible` is the
 * browser's own answer to that distinction. Guarded because older engines throw on an
 * unrecognised pseudo-class in `matches()`; treating that as "not keyboard" simply leaves
 * the carousel running, which is the safe default here.
 */
function isKeyboardFocus(el) {
  try {
    return el.matches(':focus-visible');
  } catch {
    return false;
  }
}

/* ═══════════════════════════════════════════════════════════════
   LMS — scroll-driven walkthrough (replaces the old dashboard mock)
   Three views, advanced by scroll position while the section is pinned.
════════════════════════════════════════════════════════════════ */

const LMS_STEPS = [
  {
    n: '01',
    title: 'Pick your topic',
    desc: 'ZedReq reads the gap between your profile and your target role, then searches the open web for current, credible material on it.',
  },
  {
    n: '02',
    title: 'Answer the set',
    desc: 'Work through questions written from those sources. Every answer is timed, scored, and kept against the topic.',
  },
  {
    n: '03',
    title: 'Read the evaluation',
    desc: 'Accuracy by domain, the questions you lost, and the one thing worth studying before the next set.',
  },
  {
    n: '04',
    title: 'Track it in one place',
    desc: 'Every set, score and course lands in one dashboard — progress by week, strength by domain, and what to take next.',
  },
];

/* ─── Step panels ──────────────────────────────────────── */

const MockChrome = ({ name, children }) => (
  <article className="v1-mock">
    <div className="v1-mock__bar">
      <span className="v1-mock__name">{name}</span>
      <span className="v1-mock__close" aria-hidden="true" />
    </div>
    <div className="v1-mock__body">{children}</div>
  </article>
);

/** Plain progress ring — no glyph inside; the figure beside it carries the number. */
const ScoreRing = ({ score, size = 'md' }) => (
  <span className={`v1-fb__ring v1-fb__ring--${size}`} aria-hidden="true">
    <svg viewBox="0 0 100 100" focusable="false">
      <circle className="v1-fb__ring-track" cx="50" cy="50" r="42" />
      <circle
        className="v1-fb__ring-fill"
        cx="50"
        cy="50"
        r="42"
        style={{ strokeDashoffset: 264 - (264 * score) / 100 }}
      />
    </svg>
  </span>
);

/** 1 — Choose Role */
const RolePanel = () => (
  <MockChrome name="Choose your role">
    <ul className="v1-role__list" role="list">
      {ROLE_OPTIONS.map((role) => (
        <li key={role.label} className={`v1-role${role.active ? ' is-active' : ''}`}>
          <span className="v1-role__text">
            <span className="v1-role__label">{role.label}</span>
            <span className="v1-role__meta">{role.meta}</span>
          </span>
          {role.active ? <span className="v1-role__check" aria-hidden="true" /> : null}
        </li>
      ))}
    </ul>

    <p className="v1-fb__label v1-role__seniority-label">Seniority</p>
    <div className="v1-role__seniority">
      {SENIORITY_LEVELS.map((level) => (
        <span
          key={level}
          className={`v1-role__pill${level === SENIORITY_ACTIVE ? ' is-active' : ''}`}
        >
          {level}
        </span>
      ))}
    </div>

    <dl className="v1-role__summary">
      {ROLE_SUMMARY.map((row) => (
        <div key={row.k} className="v1-role__summary-row">
          <dt>{row.k}</dt>
          <dd>{row.v}</dd>
        </div>
      ))}
    </dl>
  </MockChrome>
);

/** 2 — Get Interviewed */
const InterviewPanel = () => (
  <MockChrome name="AI Interviewer">
    <p className="v1-mock__meta">
      <span>{INTERVIEW_META.position}</span>
      <span>{INTERVIEW_META.elapsed}</span>
    </p>

    <p className="v1-mock__bubble">Tell me about yourself.</p>

    {/* Recorder is its own framed surface, as in the reference */}
    <div className="v1-mock__recorder">
      <div className="v1-wave" aria-hidden="true">
        {WAVE_BARS.map((h, i) => (
          <span key={i} className="v1-wave__bar" style={{ '--h': `${h}%`, '--i': i }} />
        ))}
      </div>

      <p className="v1-mock__rec">
        <span className="v1-mock__rec-dots" aria-hidden="true">
          <i /><i /><i />
        </span>
        Recording…
      </p>

      <span className="v1-mock__stop" />
    </div>

    <p className="v1-mock__hint">{INTERVIEW_HINT}</p>
  </MockChrome>
);

/** 3 — Receive Feedback */
const FeedbackPanel = () => (
  <MockChrome name="Interview Feedback">
    <div className="v1-fb__score">
      <ScoreRing score={HERO_PANEL_SCORE} />
      <span className="v1-fb__score-text">
        <span className="v1-fb__score-label">Your Score</span>
        <span className="v1-fb__score-val">
          {HERO_PANEL_SCORE}
          <span>/100</span>
        </span>
      </span>
    </div>

    <ul className="v1-fb__breakdown" role="list">
      {FEEDBACK_BREAKDOWN.map((d) => (
        <li key={d.label}>
          <span className="v1-fb__breakdown-val">{d.val}</span>
          <span className="v1-fb__breakdown-label">{d.label}</span>
        </li>
      ))}
    </ul>

    <p className="v1-fb__label">Key Strengths</p>
    <ul className="v1-fb__list v1-fb__list--good" role="list">
      {ACTION_STRENGTHS.map((item) => <li key={item}>{item}</li>)}
    </ul>

    <p className="v1-fb__label v1-fb__label--work">Areas to Improve</p>
    <ul className="v1-fb__list v1-fb__list--work" role="list">
      {ACTION_IMPROVEMENTS.map((item) => <li key={item}>{item}</li>)}
    </ul>
  </MockChrome>
);

/** 4 — Improve */
const ProgressPanel = () => {
  const first = PROGRESS_SESSIONS[0].score;
  const last = PROGRESS_SESSIONS[PROGRESS_SESSIONS.length - 1].score;

  return (
    <MockChrome name="Your progress">
      <div className="v1-prog__head">
        <ScoreRing score={last} />
        <span className="v1-fb__score-text">
          <span className="v1-fb__score-label">Latest score</span>
          <span className="v1-fb__score-val">
            {last}
            <span>/100</span>
          </span>
        </span>
        <span className="v1-prog__delta">+{last - first}</span>
      </div>

      <p className="v1-fb__label">Session history</p>
      <ul className="v1-prog__list" role="list">
        {PROGRESS_SESSIONS.map((s) => (
          <li key={s.label} className={`v1-prog__row${s.active ? ' is-active' : ''}`}>
            <span className="v1-prog__row-label">
              {s.label}
              <span className="v1-prog__row-date">{s.date}</span>
            </span>
            <span className="v1-prog__track">
              <span className="v1-prog__fill" style={{ width: `${s.score}%` }} />
            </span>
            <span className="v1-prog__val">{s.score}</span>
          </li>
        ))}
      </ul>

      <p className="v1-fb__label v1-prog__focus-label">Next focus</p>
      <ul className="v1-fb__list v1-fb__list--work" role="list">
        {PROGRESS_FOCUS.map((item) => <li key={item}>{item}</li>)}
      </ul>
    </MockChrome>
  );
};

/* ─── LMS views ────────────────────────────────────────── */
/* Each step shows a full product mock — same dash scale treatment as step 4 so
   the walkthrough reads as one surface, not four different designs. */

const LmsDashWrap = ({ children }) => (
  <div className="v1-lms__dash">
    <div className="v1-lms__dash-inner">{children}</div>
  </div>
);

const LmsTopicView = () => (
  <LmsDashWrap>
    <LMSTopicPanel />
  </LmsDashWrap>
);

const LmsQuizView = () => (
  <LmsDashWrap>
    <LMSQuizPanel />
  </LmsDashWrap>
);

const LmsEvaluationView = () => (
  <LmsDashWrap>
    <LMSEvaluationPanel />
  </LmsDashWrap>
);

const LmsDashboardView = () => (
  <LmsDashWrap>
    <LMSDashboard />
  </LmsDashWrap>
);

/** View per LMS step index — order matches LMS_STEPS. */
const LMS_VIEWS = [LmsTopicView, LmsQuizView, LmsEvaluationView, LmsDashboardView];

/** Panel per step index — order matches ACTION_STEPS. */
const ACTION_PANELS = [RolePanel, InterviewPanel, FeedbackPanel, ProgressPanel];

/* ─── Features ─────────────────────────────────────────── */
const FEATURES = [
  {
    label: 'Profile Intelligence',
    icon: 'icon-matching.svg',
    title: 'AI-Built Profile',
    desc: 'Your resume is 30 seconds of a recruiter\'s attention. ZedReq surfaces skills, patterns, and signals that static PDFs can\'t — built by AI trained on 2M+ successful applications.',
    href: '/features',
  },
  {
    label: 'Opportunity Engine',
    icon: 'icon-network.svg',
    title: 'Smart Job Matching',
    desc: 'Skip the keyword-spray. Our engine ranks roles by genuine fit — salary, team structure, growth trajectory, and culture.',
    href: '/features',
  },
  {
    label: 'Skill Intelligence',
    icon: 'icon-learning.svg',
    title: 'Adaptive Learning',
    desc: 'ZedReq maps your gap to the role you want, then builds a personalized path to close it — courses, projects, mentors.',
    href: '/lms',
  },
  {
    label: 'Career Network',
    icon: 'icon-tracking.svg',
    title: 'Warm Introductions',
    desc: 'Cold applications convert at 2%. Warm introductions convert at 40%. ZedReq routes you through the right second-degree connection.',
    href: '/features',
  },
  {
    label: 'AI Interview Coach',
    icon: 'icon-interview.svg',
    title: 'Interview Prep',
    desc: 'Realistic mock interviews for your exact target role. Feedback in real-time on delivery, structure, and technical depth.',
    href: '/login',
  },
  {
    label: 'Application Tracking',
    icon: 'icon-analytics.svg',
    title: 'Pipeline Intelligence',
    desc: 'See every stage of every application in one board. Know exactly when to follow up — and what to say when you do.',
    href: '/features',
  },
  {
    label: 'AI Assistant',
    icon: 'icon-assistant.svg',
    title: 'Your Career Co-Pilot',
    desc: 'Ask anything. Cover letter in 90 seconds. Salary benchmark by city. Offer negotiation script. ZedReq AI never leaves your side.',
    href: '/login',
  },
];

/* ─── FAQ items ─────────────────────────────────────────── */
const FAQ = [
  {
    q: 'Where is my data stored?',
    a: 'All data is stored on encrypted servers in GDPR-compliant regions. You can export or delete your data at any time from your Settings panel.',
  },
  {
    q: 'Is my data ever sold?',
    a: 'Never. Your data powers your personal career experience exclusively. We do not sell, share, or broker user data to any third party — ever.',
  },
  {
    q: 'How does bias detection work?',
    a: 'Our models are audited monthly for demographic bias across gender, ethnicity, age, and geography. Scoring is based solely on skills and verified experience signals.',
  },
  {
    q: 'Can I delete my account?',
    a: 'Yes, immediately. Go to Settings → Account → Delete Account. All data is purged from our systems within 30 days per GDPR Article 17.',
  },
  {
    q: 'Who can see my profile?',
    a: "Only connections you approve and companies you've applied to. Profiles are private by default with granular privacy controls in Settings.",
  },
];

/* ─── Testimonials ──────────────────────────────────────── */
const TESTIMONIALS = [
  {
    quote: (
      <>
        ZedReq found me a senior engineering role in three weeks. The AI profile builder surfaced
        skills I didn&apos;t even think to list. The match was <em>exact.</em>
      </>
    ),
    name: 'Ayesha K.',
    role: 'Senior Software Engineer — Berlin',
  },
  {
    quote: (
      <>
        I applied to 200 jobs on LinkedIn. Then I joined ZedReq. Six targeted applications. Two
        final rounds. One offer — <em>above my ask.</em>
      </>
    ),
    name: 'Marcus T.',
    role: 'Product Manager — São Paulo',
  },
  {
    quote: (
      <>
        The interview simulator felt eerily real. After twelve practice sessions I walked into my
        panel completely calm. I got the role. ZedReq is the <em>unfair advantage</em> I needed.
      </>
    ),
    name: 'Priya S.',
    role: 'UX Research Lead — Singapore',
  },
];

/* ─── Marquee segments ──────────────────────────────────── */
const MARQUEE_SEGS = [
  'AI Profile Builder',
  'Smart Matching',
  'Interview Simulator',
  'Pipeline Tracker',
  'Bias Detection',
  'Salary Intelligence',
  'Warm Intros',
  'LMS Courses',
  'Career Co-Pilot',
  'GDPR Compliant',
];

/* ─── Trust stats ───────────────────────────────────────── */
const TRUST_ITEMS = [
  { num: '01', title: 'Zero Data Brokering', desc: 'We never sell or share your data. You control what\'s visible.' },
  { num: '02', title: 'GDPR Article 17', desc: 'Delete your account — all data purged within 30 days.' },
  { num: '03', title: 'Monthly Bias Audits', desc: 'Scoring models checked for demographic bias every 30 days.' },
  { num: '04', title: 'AES-256 Encryption', desc: 'Bank-grade encryption at rest and in transit.' },
  { num: '05', title: 'OWASP-informed hardening', desc: 'TLS, strict auth, validation, and rate limits by design.' },
  { num: '06', title: 'Sign in with Google', desc: 'Use the account you already trust — no extra password.' },
];

/* ═══════════════════════════════════════════════════════════════
   COMPONENT
════════════════════════════════════════════════════════════════ */
export default function FirstPage() {
  const startupMode = isStartupMode();
  const { theme, setTheme } = useTheme();
  const rootRef = useRef(null);
  const [menuOpen,       setMenuOpen]       = useState(false);
  const [modalOpen,      setModalOpen]      = useState(false);
  const [reserveDone,    setReserveDone]    = useState(false);
  const [reserveLoading, setReserveLoading] = useState(false);
  const [reserveError,   setReserveError]   = useState('');
  const [reservePromoCode, setReservePromoCode] = useState('');
  const [reserveAlreadyReserved, setReserveAlreadyReserved] = useState(false);
  const [reserveEmailFailed, setReserveEmailFailed] = useState(false);
  const [faqOpen,        setFaqOpen]        = useState(null);
  const [tIdx,           setTIdx]           = useState(0);
  /* Hero copy rotation */
  const [heroIdx,        setHeroIdx]        = useState(0);
  const [heroFade,       setHeroFade]       = useState(false);
  const [heroEnter,      setHeroEnter]      = useState(false);
  /* "See it in action" tabs */
  const [actionTab,      setActionTab]      = useState(0);
  /* Bumped on every manual pick so the dwell timer restarts from that tab */
  const [actionCycle,    setActionCycle]    = useState(0);
  /* Hovering the tabs does nothing — they are click-only. The carousel is held
     solely while a tab has *keyboard* focus, so arrowing through the strip is not
     fighting an auto-advance. A click focuses the button too, which is why the
     handler screens for :focus-visible rather than plain focus. */
  const [actionFocus,    setActionFocus]    = useState(false);
  const actionTabRefs = useRef([]);
  const actionHeld = actionFocus;
  /* Dwell balance for the current tab, and when the running stretch started */
  const dwellLeftRef  = useRef(ACTION_TAB_MS);
  const dwellStartRef = useRef(0);

  /* ── LMS walkthrough ── */
  const lmsRef = useRef(null);
  const [lmsStep, setLmsStep] = useState(0);
  const [lmsNarrow, setLmsNarrow] = useState(false);
  const prefersReducedMotion = useReducedMotion();
  /* Pinning is dropped on small screens and for reduced motion; the three views
     then stack in the normal flow, each under its own step. */
  const lmsStatic = lmsNarrow || !!prefersReducedMotion;

  const { scrollYProgress: lmsProgress } = useScroll({
    target: lmsRef,
    offset: ['start start', 'end end'],
  });

  useMotionValueEvent(lmsProgress, 'change', (v) => {
    if (lmsStatic) return;
    const i = Math.min(LMS_STEPS.length - 1, Math.max(0, Math.floor(v * LMS_STEPS.length)));
    setLmsStep((cur) => (cur === i ? cur : i));
  });

  useEffect(() => {
    const mq = window.matchMedia('(max-width: 1024px)');
    const sync = () => setLmsNarrow(mq.matches);
    sync();
    mq.addEventListener('change', sync);
    return () => mq.removeEventListener('change', sync);
  }, []);

  /* Attach imperative DOM effects once */
  useEffect(() => {
    const cleanup = attachFirstPageEffects(rootRef.current);
    return cleanup;
  }, []);

  /* Scroll to hash targets (e.g. /#pricing from the pricing stub page). */
  useEffect(() => {
    const hash = window.location.hash.replace(/^#/, '');
    if (!hash) return undefined;
    const id = requestAnimationFrame(() => {
      document.getElementById(hash)?.scrollIntoView({ behavior: 'smooth' });
    });
    return () => cancelAnimationFrame(id);
  }, []);

  /* ── "See it in action" tabs ───────────────────────────── */

  /**
   * Picking a tab does not retire the carousel — it keeps cycling so the four
   * steps still play on their own. Bumping the cycle counter restarts the dwell,
   * so a deliberate pick gets a full window before anything moves on.
   */
  const selectActionTab = useCallback((i) => {
    setActionTab(i);
    setActionCycle((c) => c + 1);
    /* A deliberate pick earns a full window, not whatever was left of the last one */
    dwellLeftRef.current = ACTION_TAB_MS;
    dwellStartRef.current = 0;
  }, []);

  /*
   * Auto-advance the step tabs.
   *
   * A plain interval cannot express "pause on hover": clearing and recreating it hands
   * back a full window every time, which would drift out of sync with the timer bar —
   * that resumes from where it froze. So the dwell is tracked as remaining milliseconds,
   * banked on hold and re-armed with only the balance.
   */
  useEffect(() => {
    if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) return;

    if (actionHeld) {
      if (dwellStartRef.current) {
        dwellLeftRef.current = Math.max(
          0,
          dwellLeftRef.current - (Date.now() - dwellStartRef.current)
        );
        dwellStartRef.current = 0;
      }
      return;
    }

    dwellStartRef.current = Date.now();
    const id = setTimeout(() => {
      dwellLeftRef.current = ACTION_TAB_MS;
      dwellStartRef.current = 0;
      setActionTab((i) => (i + 1) % ACTION_STEPS.length);
    }, dwellLeftRef.current);
    return () => clearTimeout(id);
    // `actionTab`/`actionCycle` re-arm the dwell after an advance or a manual pick.
  }, [actionHeld, actionTab, actionCycle]);

  /** Roving focus across the tablist, per the ARIA tabs pattern. */
  const onActionTabKeyDown = useCallback((e) => {
    const last = ACTION_STEPS.length - 1;
    let next = null;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') next = actionTab === last ? 0 : actionTab + 1;
    else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') next = actionTab === 0 ? last : actionTab - 1;
    else if (e.key === 'Home') next = 0;
    else if (e.key === 'End') next = last;
    if (next == null) return;
    e.preventDefault();
    selectActionTab(next);
    actionTabRefs.current[next]?.focus();
  }, [actionTab, selectActionTab]);

  /* Auto-advance testimonials */
  useEffect(() => {
    const id = setInterval(() => setTIdx((i) => (i + 1) % TESTIMONIALS.length), 5500);
    return () => clearInterval(id);
  }, []);

  /* Rotating hero headline + lead (AI mock interview variants) */
  useEffect(() => {
    if (prefersReducedMotion) return undefined;
    let enterTimer;
    let fadeTimer;
    const id = setInterval(() => {
      setHeroFade(true);
      fadeTimer = setTimeout(() => {
        setHeroIdx((i) => (i + 1) % HERO_COPY_VARIANTS.length);
        setHeroFade(false);
        setHeroEnter(true);
        enterTimer = setTimeout(() => setHeroEnter(false), HERO_ENTER_MS);
      }, HERO_FADE_MS);
    }, HERO_SWAP_MS);
    return () => {
      clearInterval(id);
      clearTimeout(fadeTimer);
      clearTimeout(enterTimer);
    };
  }, [prefersReducedMotion]);

  /* Body overflow lock when modal / menu open */
  useEffect(() => {
    document.body.style.overflow = menuOpen || modalOpen ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [menuOpen, modalOpen]);

  /* Reset reserve form on modal close */
  useEffect(() => {
    if (!modalOpen) {
      setReserveDone(false);
      setReserveError('');
      setReserveLoading(false);
      setReservePromoCode('');
      setReserveAlreadyReserved(false);
      setReserveEmailFailed(false);
    }
  }, [modalOpen]);

  /* Escape key */
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === 'Escape') {
        setMenuOpen(false);
        setModalOpen(false);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const openModal  = useCallback(() => setModalOpen(true), []);
  const closeModal = useCallback(() => setModalOpen(false), []);
  const openMenu   = useCallback(() => setMenuOpen(true), []);
  const closeMenu  = useCallback(() => setMenuOpen(false), []);
  const toggleFaq  = useCallback((i) => setFaqOpen((cur) => (cur === i ? null : i)), []);

  /* Reserve seat — calls real backend + sends EmailJS confirmation */
  const onReserve = useCallback(async (e) => {
    e.preventDefault();
    const emailInput = e.target.querySelector('[type="email"]');
    const email = emailInput ? emailInput.value : '';
    if (!email) return;

    setReserveLoading(true);
    setReserveError('');
    setReserveEmailFailed(false);

    try {
      const apiUrl = getApiBaseUrl();
      const res = await fetch(`${apiUrl}/api/reserved-seats`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Failed to reserve seat');
      if (!data.success) throw new Error(data.message || 'Failed to reserve seat');

      const promoCode = data.promo_code || '';
      setReservePromoCode(promoCode);
      setReserveAlreadyReserved(!!data.already_reserved);

      if (!data.already_reserved && promoCode) {
        const emailResult = await sendReservationEmail(email, promoCode);
        if (!emailResult.ok) {
          setReserveEmailFailed(true);
          void fetch(`${apiUrl}/api/reserved-seats/email-delivery-failed`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ promo_code: promoCode, reason: emailResult.reason || 'emailjs_failed' }),
          }).catch(() => {});
        }
      }
      setReserveDone(true);
    } catch (err) {
      setReserveError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setReserveLoading(false);
    }
  }, []);

  /* ─── Render ─────────────────────────────────────────── */
  const heroCopy = HERO_COPY_VARIANTS[heroIdx];

  return (
    <div className="zedreq-root" ref={rootRef}>
      <a href="#main" className="skip-link">Skip to content</a>

      {/* ── Scroll progress ── */}
      <div className="scroll-progress" aria-hidden="true" />

      {/* ════════════ NAV ════════════ */}
      <nav className="nav" aria-label="Primary navigation">
        <a href="/" className="nav__brand" aria-label="ZedReq home">
          <img src={A('logo_tr1.svg')} alt="" className="nav__logo" />
          <span className="nav__wordmark">ZedReq</span>
        </a>

        <ul className="nav__links" role="list">
          {['Features', 'Product', 'Pricing'].map((item) => (
            <li key={item}>
              <a href={`#${item.toLowerCase()}`} className="nav__link">{item}</a>
            </li>
          ))}
        </ul>

        <div className="nav__actions">
          <button
            type="button"
            className={`nav__theme-btn nav__theme-btn--square${theme === 'dark' ? ' nav__theme-btn--to-light' : ' nav__theme-btn--to-dark'}`}
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
            aria-pressed={theme === 'light'}
          >
            {theme === 'dark' ? (
              <svg className="nav__theme-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                <circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" strokeWidth="1.6" />
                <path
                  d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.6"
                  strokeLinecap="round"
                />
              </svg>
            ) : (
              <svg className="nav__theme-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                <path
                  fill="currentColor"
                  d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"
                />
              </svg>
            )}
          </button>
          <button
            className="nav__burger"
            aria-label="Open menu"
            aria-expanded={menuOpen}
            onClick={openMenu}
          >
            <span /><span /><span />
          </button>
          <FirstPageGlowButton href="/login" className="fp-glow-btn--nav" ctaId="navbar_get_started" ctaLocation="navbar">
            Get Started
          </FirstPageGlowButton>
        </div>
      </nav>

      {/* ── Mobile overlay ── */}
      <div
        className={`nav-overlay${menuOpen ? ' open' : ''}`}
        aria-hidden={!menuOpen}
        role="dialog"
        aria-modal="true"
        aria-label="Site navigation"
      >
        <button className="nav-overlay__close btn btn--sm" onClick={closeMenu} aria-label="Close menu">
          CLOSE ✕
        </button>
        {['Features', 'Product', 'Pricing'].map((item) => (
          <a
            key={item}
            href={`#${item.toLowerCase()}`}
            className="nav-overlay__link"
            onClick={closeMenu}
          >
            {item}
          </a>
        ))}
      </div>

      {/* ════════════ HERO ════════════ */}
      <main id="main">
        <section className="hero herov1" id="hero" aria-label="Hero">
          {/* Background effects — DarkVeil carried over unchanged */}
          <div style={{ position: 'absolute', inset: 0, zIndex: 0 }} aria-hidden="true">
            <DarkVeil
              hueShift={399}
              noiseIntensity={0.0}
              scanlineIntensity={0.2}
              speed={0.8}
              scanlineFrequency={0.0}
              warpAmount={1.0}
              resolutionScale={1.0}
              forLightBackground={theme === 'light'}
            />
          </div>
          <div className="hero__texture" aria-hidden="true" />

          <div className="herov1__grid">
            {/* ── Left column: copy ── */}
            <div className="herov1__copy">
              <h1 className="herov1__hl" aria-label={heroCopy.ariaLabel}>
                <span className="herov1__hl-line">Your next interview</span>
                <span
                  className={`herov1__hl-swapped${heroFade ? ' is-fading' : ''}${heroEnter ? ' is-entering' : ''}`}
                  aria-hidden={heroFade}
                >
                  <span className="herov1__hl-line">{heroCopy.line2}</span>
                  <span className="herov1__hl-line herov1__hl-line--accent">{heroCopy.line3}</span>
                </span>
              </h1>

              <p className={`herov1__lead${heroFade ? ' is-fading' : ''}`}>{heroCopy.lead}</p>

              <div className="herov1__actions">
                <FirstPageGlowButton
                  showIcon
                  href="/login"
                  ctaId="hero_start_free_interview"
                  ctaLocation="hero"
                >
                  Start Free Interview →
                </FirstPageGlowButton>
                <button type="button" className="herov1__ghost-btn" onClick={openModal}>
                  Reserve Early Access ↗
                </button>
              </div>

              <ul className="herov1__chips" role="list">
                {HERO_CHIPS.map((chip) => (
                  <li key={chip.label} className="herov1__chip">
                    <img src={A(chip.icon)} alt="" className="herov1__chip-icon" />
                    {chip.label}
                  </li>
                ))}
              </ul>
            </div>

            {/* ── Right column: live mock-interview panel ── */}
            <div className="herov1__panel" role="img" aria-label="Preview of an AI mock interview session scoring 78 out of 100">
              <div className="herov1__panel-bar">
                <span className="herov1__panel-live">
                  <span className="herov1__panel-dot" aria-hidden="true" />
                  Live Session
                </span>
                <span className="herov1__panel-meta">Question 3 of 8 · 12:04</span>
              </div>

              <div className="herov1__panel-body">
                <figure className="herov1__panel-video">
                  <img src={interviewMockImg} alt="" loading="lazy" decoding="async" />
                  <figcaption className="herov1__panel-videotag">Interview in progress</figcaption>
                </figure>

                <div className="herov1__panel-side">
                  <span className="herov1__panel-label">Current question</span>
                  <p className="herov1__panel-question">{HERO_PANEL_QUESTION}</p>

                  <span className="herov1__panel-label">Live signals</span>
                  <ul className="herov1__panel-signals" role="list">
                    {HERO_PANEL_SIGNALS.map((sig) => (
                      <li key={sig.label} className="herov1__panel-signal">
                        <span className="herov1__panel-signal-name">{sig.label}</span>
                        <span className="herov1__panel-signal-track">
                          <span
                            className="herov1__panel-signal-fill"
                            style={{ width: `${sig.pct}%` }}
                          />
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="herov1__panel-score">
                <svg className="herov1__gauge" viewBox="0 0 100 100" aria-hidden="true" focusable="false">
                  <circle className="herov1__gauge-track" cx="50" cy="50" r="42" />
                  <circle
                    className="herov1__gauge-fill"
                    cx="50"
                    cy="50"
                    r="42"
                    style={{ strokeDashoffset: 264 - (264 * HERO_PANEL_SCORE) / 100 }}
                  />
                </svg>
                <div className="herov1__panel-score-text">
                  <span className="herov1__panel-score-val">
                    {HERO_PANEL_SCORE}
                    <span>/100</span>
                  </span>
                  <span className="herov1__panel-score-label">Overall score</span>
                </div>
              </div>
            </div>
          </div>

          {/* Scroll indicator */}
          <div className="hero__scroll" aria-hidden="true">
            <span className="hero__scroll-line" />
          </div>
        </section>

        {/* ════════════ SEE IT IN ACTION ════════════ */}
        <section className="v1-action" id="how-it-works" aria-labelledby="v1-action-hl">
          <div className="v1-action__inner">
            <header className="v1-action__head">
              <h2 className="v1-action__hl reveal" id="v1-action-hl">See it in action</h2>
              <p className="v1-action__sub reveal" style={{ '--d': 1 }}>
                Go from interview to improvement in just a few minutes.
              </p>
            </header>

            {/* ── Four-step tablist ── */}
            {/* `reveal` sits on the tablist, never on the buttons: `is-visible` is added
                imperatively by firstPageEffects, and React rewrites a button's className
                every time the active tab moves — which would strip it and leave the
                button stuck at opacity 0. This container's className never changes. */}
            <div
              className="v1-action__tablist reveal"
              role="tablist"
              aria-label="How ZedReq works"
              onKeyDown={onActionTabKeyDown}
            >
              {ACTION_STEPS.map(({ Icon, title, desc }, i) => {
                const active = actionTab === i;
                return (
                  <button
                    key={title}
                    type="button"
                    role="tab"
                    id={`v1-tab-${i}`}
                    aria-selected={active}
                    aria-controls={`v1-panel-${i}`}
                    tabIndex={active ? 0 : -1}
                    ref={(el) => { actionTabRefs.current[i] = el; }}
                    className={`v1-step${active ? ' is-active' : ''}`}
                    style={{ '--d': i + 1 }}
                    onClick={() => selectActionTab(i)}
                    onFocus={(e) => setActionFocus(isKeyboardFocus(e.target))}
                    onBlur={() => setActionFocus(false)}
                  >
                    <span className="v1-step__icon" aria-hidden="true">
                      <Icon size={20} strokeWidth={1.9} />
                    </span>
                    <span className="v1-step__title">
                      <span className="v1-step__num">{i + 1}.</span> {title}
                    </span>
                    <span className="v1-step__desc">{desc}</span>
                  </button>
                );
              })}
            </div>

            {/* ── Showcase: paired mocks + copy ── */}
            <div className="v1-action__showcase">
              <div className="v1-action__stage reveal-left">
                {ACTION_PANELS.map((Panel, i) => (
                  <div
                    key={ACTION_STEPS[i].title}
                    role="tabpanel"
                    id={`v1-panel-${i}`}
                    aria-labelledby={`v1-tab-${i}`}
                    hidden={actionTab !== i}
                    tabIndex={0}
                    className="v1-action__panel"
                  >
                    {/* Keyed on the tab so the panel's entry animation replays on each swap */}
                    <Panel key={actionTab} />
                  </div>
                ))}
              </div>

              <div className="v1-action__copy reveal-right">
                <h3 className="v1-action__copy-hl">
                  Getting the interview<br />is only half the battle.
                </h3>
                {/* Each quoted question sits on its own line, as in the reference —
                    the break is what gives them their weight, not extra styling. */}
                <p className="v1-action__copy-p">
                  You might have a good resume and the right skills, but when the interviewer
                  asks:
                  <br />&ldquo;Tell me about yourself&rdquo;,
                  <br />&ldquo;Why should we hire you?&rdquo;
                  <br />you need to actually perform.
                </p>
                <p className="v1-action__copy-p v1-action__copy-p--close">
                  ZedReq lets you practice that,
                  <br />before the real interview.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ════════════ MARQUEE ════════════ */}
        <div className="marquee" aria-hidden="true">
          <div className="marquee__inner">
            {[...MARQUEE_SEGS, ...MARQUEE_SEGS].map((seg, i) => (
              <span key={`${seg}-${i}`} className="marquee__seg">
                <span className="marquee__sep" />
                {seg}
              </span>
            ))}
          </div>
        </div>

        {/* ════════════ LMS WALKTHROUGH ════════════ */}
        <section
          className={`v1-lms${lmsStatic ? ' v1-lms--static' : ''}`}
          id="product"
          ref={lmsRef}
          aria-labelledby="v1-lms-hl"
        >
          <div className="v1-lms__sticky">
            <div className="v1-lms__inner">
              <header className="v1-lms__head">
                <span className="v1-lms__eyebrow">04 — LMS</span>
                <h2 className="v1-lms__title" id="v1-lms-hl">
                  Skills that <em>compound</em>
                </h2>
                <p className="v1-lms__desc">
                  Curated learning paths align with your profile gaps and target roles —
                  built from what the web says today, not a static syllabus.
                </p>
              </header>

              <div className="v1-lms__layout">
                {/* Left: the steps */}
                <ol className="v1-lms__list">
                  {LMS_STEPS.map((step, i) => (
                    <li
                      key={step.n}
                      className={`v1-lms__step${!lmsStatic && lmsStep === i ? ' is-active' : ''}`}
                      aria-current={!lmsStatic && lmsStep === i ? 'step' : undefined}
                    >
                      <span className="v1-lms__step-n">{step.n}</span>
                      <h3 className="v1-lms__step-title">{step.title}</h3>
                      <p className="v1-lms__step-desc">{step.desc}</p>

                      {/* Stacked fallback: each view sits under its own step */}
                      {lmsStatic ? (
                        <div className="v1-lms__stacked-view">
                          {(() => {
                            const View = LMS_VIEWS[i];
                            return <View />;
                          })()}
                        </div>
                      ) : null}
                    </li>
                  ))}

                  <FirstPageGlowButton
                    href="/lms"
                    ctaId="feature_open_lms"
                    ctaLocation="features"
                    className="v1-lms__cta"
                  >
                    Open the LMS →
                  </FirstPageGlowButton>
                </ol>

                {/* Right: the pinned stage */}
                {!lmsStatic ? (
                  <div className="v1-lms__stage">
                    {LMS_VIEWS.map((View, i) => (
                      <div
                        key={LMS_STEPS[i].n}
                        className="v1-lms__view"
                        hidden={lmsStep !== i}
                        aria-hidden={lmsStep !== i}
                      >
                        {/* Keyed on the step so the entry animation replays per swap */}
                        <View key={lmsStep} />
                      </div>
                    ))}
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        </section>

        {/* ════════════ FEATURES ════════════ */}
        <section className="features" id="features" aria-labelledby="feat-hl">
          <div className="features__head">
            <h2 className="features__hl reveal" id="feat-hl">
              Everything you need to<br /><em>get hired.</em>
            </h2>
            <p className="features__sub reveal" style={{ '--d': 1 }}>
              Seven intelligent modules. One unified platform. Built for professionals
              who take their careers seriously.
            </p>
          </div>

          <div className="features__grid" role="list">
            {FEATURES.map((f) => (
              <a key={f.label} href={f.href} className="feat-card" role="listitem">
                <span className="feat-card__label">{f.label}</span>
                <img src={A(f.icon)} alt="" className="feat-card__icon" />
                <h3 className="feat-card__title">{f.title}</h3>
                <p className="feat-card__desc">{f.desc}</p>
                <span className="feat-card__arrow" aria-hidden="true">Learn more →</span>
              </a>
            ))}
          </div>
        </section>

        {/* ════════════ STATS ════════════ */}
        <section className="stats" id="stats" aria-labelledby="stats-hl">
          <div className="stats__head reveal">
            <p className="stats__eyebrow">By the numbers</p>
            <h2 className="stats__hl" id="stats-hl">
              Results that<br /><em>speak for themselves.</em>
            </h2>
          </div>

          <div className="stats__grid">
            {[
              { val: '94',   unit: '%', label: 'of users receive an interview within 45 days',     target: '94%' },
              { val: '3.2',  unit: 'x', label: 'more responses than traditional applications',     target: '3.2x' },
              { val: '120',  unit: 'K+', label: 'professionals placed since launch',              target: '120K+' },
              { val: '4.9',  unit: '/5', label: 'average user satisfaction across all platforms', target: '4.9/5' },
            ].map((s) => (
              <div key={s.label} className="stat-item reveal">
                <div className="stat-item__val" data-target={s.target}>
                  {s.val}<span className="stat-item__unit">{s.unit}</span>
                </div>
                <p className="stat-item__label">{s.label}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ════════════ TRUST ════════════ */}
        <section className="trust" id="about" aria-labelledby="trust-hl">
          <div className="trust__layout">
            <header className="trust__head">
              <span className="mono-label mono-label--accent" style={{ marginBottom: '1rem', display: 'block' }}>
                Privacy &amp; Security
              </span>
              <h2 className="trust__hl" id="trust-hl">
                Your data.<br /><em>Your rules.</em>
              </h2>
              <p className="trust__sub">
                Your career data belongs to you — not advertisers, recruiters, or us.
              </p>
            </header>

            <StackedCards items={TRUST_ITEMS} />
          </div>
        </section>

        {/* ════════════ TESTIMONIALS ════════════ */}
        <section className="testimonials" aria-labelledby="t-hl">
          <p className="testimonials__eyebrow reveal" id="t-hl">What our users say</p>

          <div className="t-stage" aria-live="polite" aria-atomic="true">
            {TESTIMONIALS.map((t, i) => (
              <div
                key={i}
                className={`t-item${i === tIdx ? ' active' : ''}`}
                aria-hidden={i !== tIdx}
              >
                <blockquote className="t-quote">{t.quote}</blockquote>
                <div className="t-byline">
                  <span className="t-byline__rule" aria-hidden="true" />
                  <span className="t-byline__name">{t.name}</span>
                  <span className="t-byline__role">{t.role}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="t-dots" role="tablist" aria-label="Testimonials">
            {TESTIMONIALS.map((_, i) => (
              <button
                key={i}
                role="tab"
                aria-selected={i === tIdx}
                aria-label={`Testimonial ${i + 1}`}
                className={`t-dot${i === tIdx ? ' active' : ''}`}
                onClick={() => setTIdx(i)}
              />
            ))}
          </div>
        </section>

        {/* ════════════ PRICING ════════════ */}
        <section className="pricing" id="pricing" aria-labelledby="pricing-hl">
          <div className="pricing__head">
            <p className="pricing__eyebrow reveal">Simple Pricing</p>
            <h2 className="pricing__hl reveal" id="pricing-hl" style={{ '--d': 1 }}>
              {startupMode ? (
                <>Start free.</>
              ) : (
                <>Start free.<br /><em>Scale when you&apos;re ready.</em></>
              )}
            </h2>
          </div>

          <div className={`pricing__grid ${startupMode ? 'pricing__grid--1' : 'pricing__grid--4'}`}>
            <div className="reveal">
              <FirstPagePricingCard
                tier="Explorer"
                price="Free"
                period="Forever"
                description="Full platform access with starter monthly limits on AI coaching, LMS courses, and mock interviews."
                tags={FREE_TEASER_WORDS}
                sections={[{ label: 'Limited usage', items: FREE_MONTHLY_LIMITS }]}
                ctaLabel="Start Free"
              />
            </div>

            {!startupMode && (
              <>
            <div className="reveal">
              <FirstPagePricingCard
                tier="Professional"
                price="$49.99"
                period="per month"
                badge="Most Popular"
                featured
                description="Higher monthly limits for professionals actively interviewing and upskilling."
                sections={[
                  { label: 'Platform access', items: PLATFORM_ACCESS_LINES },
                  { label: 'Monthly limits', items: PRO_MONTHLY_LIMITS.map((line, i) => ({ text: line, emph: i < 3 })) },
                ]}
                ctaLabel="Get Started"
              />
            </div>

            <div className="reveal">
              <FirstPagePricingCard
                tier="Elite"
                price="$89.99"
                period="per month"
                description="Maximum standard limits for power users who want every edge in their search."
                sections={[
                  { label: 'Platform access', items: PLATFORM_ACCESS_LINES },
                  { label: 'Monthly limits', items: PREMIUM_MONTHLY_LIMITS.map((line, i) => ({ text: line, emph: i < 3 })) },
                ]}
                ctaLabel="Go Elite"
              />
            </div>

            <div className="reveal">
              <FirstPagePricingCard
                tier="Enterprise"
                price="Custom"
                period="by arrangement"
                description="Unlimited usage for AI messages, courses, and interviews — assigned by agreement."
                sections={[
                  { label: 'Platform access', items: PLATFORM_ACCESS_LINES },
                  { label: 'Enterprise usage', items: ENTERPRISE_USAGE_FEATURES },
                ]}
                ctaLabel="Contact us"
              />
            </div>
              </>
            )}
          </div>
        </section>

        {/* ════════════ FAQ ════════════ */}
        <section className="faq" aria-labelledby="faq-hl">
          <h2 className="faq__aside-hl reveal" id="faq-hl">
            Questions,<br /><em>answered.</em>
          </h2>

          <div className="faq__list" role="list">
            {FAQ.map((item, i) => (
              <div
                key={i}
                className={`faq__item${faqOpen === i ? ' open' : ''}`}
                role="listitem"
              >
                <button
                  className="faq__q"
                  aria-expanded={faqOpen === i}
                  onClick={() => toggleFaq(i)}
                >
                  {item.q}
                  <span className="faq__icon" aria-hidden="true" />
                </button>
                <p className="faq__a">{item.a}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ════════════ CTA BAND ════════════ */}
        <section className="cta-band" aria-labelledby="cta-hl">
          <p className="cta-band__eyebrow reveal">Get started today</p>
          <h2 className="cta-band__hl reveal" id="cta-hl" style={{ '--d': 1 }}>
            Your next role<br />is <em>already waiting.</em>
          </h2>
          <div className="cta-band__actions reveal" style={{ '--d': 2 }}>
            <FirstPageGlowButton showIcon onClick={openModal} ctaId="footer_reserve_seat" ctaLocation="footer_cta">
              Reserve Early Access ↗
            </FirstPageGlowButton>
            <FirstPageGlowButton href="/login" ctaId="footer_get_started" ctaLocation="footer_cta">Get Started</FirstPageGlowButton>
          </div>
        </section>

        {/* ════════════ FOOTER ════════════ */}
        <footer className="footer">
          <div className="footer__inner">
            <a href="/" aria-label="ZedReq home">
              <img src={A('logo_tr1.svg')} alt="ZedReq" className="footer__logo" />
            </a>

            <nav className="footer__nav" aria-label="Footer navigation">
              {[
                { label: 'Features',  href: '/features' },
                { label: 'Product',   href: '#product' },
                { label: 'Pricing',   href: '/pricing' },
                { label: 'About',     href: '/about' },
                { label: 'Blog',      href: '/blogs' },
                { label: 'Careers',   href: '/careers' },
                { label: 'Privacy',   href: '/privacy' },
                { label: 'Terms',     href: '/terms' },
              ].map((l) => (
                <a key={l.label} href={l.href} className="footer__link">{l.label}</a>
              ))}
            </nav>

            <div className="footer__legal">
              <p>© {new Date().getFullYear()} ZedReq Ltd. All rights reserved.</p>
              <p>
                <a href="/privacy" className="footer__link">Privacy Policy</a>
                {' · '}
                <a href="/terms" className="footer__link">Terms of Service</a>
              </p>
            </div>
          </div>
        </footer>
      </main>

      {/* ════════════ MODAL ════════════ */}
      {modalOpen && (
        <div
          className="modal"
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
        >
          <div
            className="modal__overlay"
            role="presentation"
            onClick={closeModal}
          />
          <div className="modal__box">
            <button className="modal__close btn btn--sm" onClick={closeModal} aria-label="Close modal">
              Close ✕
            </button>

            {reserveDone ? (
              <div className="modal__success">
                <div className="modal__success-icon">✓</div>
                <h2 className="modal__success-hl">You&apos;re reserved.</h2>
                {reserveAlreadyReserved ? (
                  <p className="modal__success-sub">
                    You already had a seat on file. Check your email for your reference code, or contact support if you
                    need it resent.
                  </p>
                ) : reserveEmailFailed ? (
                  <>
                    <p className="modal__success-sub modal__success-sub--warn" role="status">
                      Your seat is saved, but the confirmation email could not be sent automatically. Use your reference
                      code below and keep it somewhere safe.
                    </p>
                    {reservePromoCode && (
                      <p className="modal__success-promo" aria-label="Your reference code">
                        <span className="modal__success-promo-label">Reference code</span>
                        <span className="modal__success-promo-value">{reservePromoCode}</span>
                      </p>
                    )}
                  </>
                ) : (
                  <p className="modal__success-sub">
                    Check your inbox for your reference code and Pro Plan discount details.
                  </p>
                )}
                {!reserveAlreadyReserved && !reserveEmailFailed && reservePromoCode ? (
                  <p className="modal__success-promo" aria-label="Your reference code">
                    <span className="modal__success-promo-label">Reference code</span>
                    <span className="modal__success-promo-value">{reservePromoCode}</span>
                  </p>
                ) : null}
              </div>
            ) : (
              <>
                <h2 className="modal__title" id="modal-title">Reserve Your Seat for Pro Plan</h2>
                <div className="modal__text">
                  <p>
                    Enter your email to reserve your spot and get early access to ZedReq Pro Plan.
                  </p>
                  <p>
                    <strong>Important:</strong>{' '}
                    Please enter your correct email address. A reference code will be generated when
                    you reserve your seat, offering both you and any person you refer a discount on the
                    Pro Plan.
                  </p>
                </div>
                <form className="modal__form" onSubmit={onReserve} noValidate>
                  <input
                    type="email"
                    className="modal__input"
                    placeholder="Enter your email address"
                    autoComplete="email"
                    required
                    disabled={reserveLoading}
                  />
                  {reserveError && (
                    <p className="modal__error" role="alert">{reserveError}</p>
                  )}
                  <FirstPageGlowButton
                    type="submit"
                    showIcon
                    className="fp-glow-btn--full"
                    disabled={reserveLoading}
                  >
                    {reserveLoading ? 'Reserving…' : 'Reserve Seat'}
                  </FirstPageGlowButton>
                </form>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
