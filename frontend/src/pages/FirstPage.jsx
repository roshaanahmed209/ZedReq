import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../css/pages/FirstPage.css';
import { attachFirstPageEffects } from '../utils/firstPageEffects.js';
import { sendReservationEmail } from '../services/emailjs';
import DarkVeil from '../components/DarkVeil';
import GlobeAnimation from '../components/GlobeAnimation';
import lmsHeroImg from '../../static/AI powered LMS.jpg';
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

/* ─── Rotating hero taglines ───────────────────────────── */
const HERO_ROT = [
  'Curated to your skills.',
  'Optimized for hiring managers.',
  'Practice until you ace it.',
  'Private, secure, and bias-aware.',
];

/** Second line of the hero headline rotates (two lines total: “Your Career.” + one swap line). */
const HERO_HL_VARIANTS = [
  {
    ariaLabel: 'Your Career. Less guessing. More gravity.',
    line2: (
      <>
        <em>Less</em> guessing. More gravity.
      </>
    ),
  },
  {
    ariaLabel: 'Your Career. Orchestrated from profile to signature.',
    line2: (
      <>
        <em>Orchestrated</em> from profile to signature.
      </>
    ),
  },
  {
    ariaLabel: 'Your Career. From invisible to undeniable.',
    line2: (
      <>
        From <em>invisible</em> to undeniable.
      </>
    ),
  },
  {
    ariaLabel: 'Your Career. Engineered for the next yes.',
    line2: (
      <>
        <em>Engineered</em> for the next yes.
      </>
    ),
  },
];

/* ─── Features ─────────────────────────────────────────── */
const FEATURES = [
  {
    label: 'Profile Intelligence',
    icon: 'icon-matching.svg',
    title: 'AI-Built Profile',
    desc: 'Your resume is 30 seconds of a recruiter\'s attention. ZedReq surfaces skills, patterns, and signals that static PDFs can\'t — built by AI trained on 2M+ successful applications.',
  },
  {
    label: 'Opportunity Engine',
    icon: 'icon-network.svg',
    title: 'Smart Job Matching',
    desc: 'Skip the keyword-spray. Our engine ranks roles by genuine fit — salary, team structure, growth trajectory, and culture.',
  },
  {
    label: 'Skill Intelligence',
    icon: 'icon-learning.svg',
    title: 'Adaptive Learning',
    desc: 'ZedReq maps your gap to the role you want, then builds a personalized path to close it — courses, projects, mentors.',
  },
  {
    label: 'Career Network',
    icon: 'icon-tracking.svg',
    title: 'Warm Introductions',
    desc: 'Cold applications convert at 2%. Warm introductions convert at 40%. ZedReq routes you through the right second-degree connection.',
  },
  {
    label: 'AI Interview Coach',
    icon: 'icon-interview.svg',
    title: 'Interview Prep',
    desc: 'Realistic mock interviews for your exact target role. Feedback in real-time on delivery, structure, and technical depth.',
  },
  {
    label: 'Application Tracking',
    icon: 'icon-analytics.svg',
    title: 'Pipeline Intelligence',
    desc: 'See every stage of every application in one board. Know exactly when to follow up — and what to say when you do.',
  },
  {
    label: 'AI Assistant',
    icon: 'icon-assistant.svg',
    title: 'Your Career Co-Pilot',
    desc: 'Ask anything. Cover letter in 90 seconds. Salary benchmark by city. Offer negotiation script. ZedReq AI never leaves your side.',
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

function PricingFeatureYes({ text, emph = false }) {
  return (
    <li className={`pricing__feature${emph ? ' pricing__feature--emph' : ''}`}>
      <i className="f-yes" aria-label="Included" />
      {text}
    </li>
  );
}

/* ─── Trust stats ───────────────────────────────────────── */
const TRUST_ITEMS = [
  { num: '01', title: 'Zero Data Brokering', desc: 'We never sell, share, or broker your data. Your career profile stays private until you choose to share it.' },
  { num: '02', title: 'GDPR Article 17 Compliant', desc: 'Delete your account and all data is purged within 30 days — no backups, no traces, by law.' },
  { num: '03', title: 'Monthly Bias Audits', desc: 'Our scoring models are audited for demographic bias every 30 days by an independent panel.' },
  { num: '04', title: 'AES-256 Encryption', desc: 'Every piece of data — at rest and in transit — is encrypted using bank-grade AES-256 protocols.' },
  {
    num: '05',
    title: 'OWASP-informed hardening',
    desc: 'We design against common OWASP-style risks: TLS everywhere, strict auth on APIs, input validation, rate limits on sensitive routes, and dependency updates—so typical web attacks are mitigated by design, not ad hoc patches.',
  },
  {
    num: '06',
    title: 'Sign in the way you already trust',
    desc: 'Sign in with Google—the account you already use every day—so you are not juggling yet another password for ZedReq.',
  },
];

/* ═══════════════════════════════════════════════════════════════
   COMPONENT
════════════════════════════════════════════════════════════════ */
export default function FirstPage() {
  const navigate = useNavigate();
  const rootRef = useRef(null);
  const [menuOpen,       setMenuOpen]       = useState(false);
  const [modalOpen,      setModalOpen]      = useState(false);
  const [reserveDone,    setReserveDone]    = useState(false);
  const [reserveLoading, setReserveLoading] = useState(false);
  const [reserveError,   setReserveError]   = useState('');
  const [faqOpen,        setFaqOpen]        = useState(null);
  const [tIdx,           setTIdx]           = useState(0);
  const [rotIdx,         setRotIdx]         = useState(0);
  const [rotFade,        setRotFade]        = useState(false);
  const [hlIdx,          setHlIdx]          = useState(0);
  const [hlFade,         setHlFade]         = useState(false);

  /* Attach imperative DOM effects once */
  useEffect(() => {
    const cleanup = attachFirstPageEffects(rootRef.current);
    return cleanup;
  }, []);

  const HL_SWAP_MS = 560;
  const ROT_SWAP_MS = 480;

  /* Rotating hero tagline */
  useEffect(() => {
    const id = setInterval(() => {
      setRotFade(true);
      setTimeout(() => {
        setRotIdx((i) => (i + 1) % HERO_ROT.length);
        setRotFade(false);
      }, ROT_SWAP_MS);
    }, 3200);
    return () => clearInterval(id);
  }, []);

  /* Rotating hero headline (lines 2–3 only; “Your Career.” fixed) */
  useEffect(() => {
    const id = setInterval(() => {
      setHlFade(true);
      setTimeout(() => {
        setHlIdx((i) => (i + 1) % HERO_HL_VARIANTS.length);
        setHlFade(false);
      }, HL_SWAP_MS);
    }, 4200);
    return () => clearInterval(id);
  }, []);

  /* Auto-advance testimonials */
  useEffect(() => {
    const id = setInterval(() => setTIdx((i) => (i + 1) % TESTIMONIALS.length), 5500);
    return () => clearInterval(id);
  }, []);

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

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000';
      const res = await fetch(`${apiUrl}/api/reserved-seats`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Failed to reserve seat');
      if (!data.success) throw new Error(data.message || 'Failed to reserve seat');

      const promoCode = data.promo_code || '';
      if (!data.already_reserved && promoCode) {
        await sendReservationEmail(email, promoCode);
      }
      setReserveDone(true);
    } catch (err) {
      setReserveError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setReserveLoading(false);
    }
  }, []);

  /* ─── Render ─────────────────────────────────────────── */
  return (
    <div className="zedreq-root" ref={rootRef}>
      <a href="#main" className="skip-link">Skip to content</a>

      {/* ── Scroll progress ── */}
      <div className="scroll-progress" aria-hidden="true" />

      {/* ════════════ NAV ════════════ */}
      <nav className="nav" aria-label="Primary navigation">
        <a href="/" className="nav__brand" aria-label="ZedReq home">
          <img src={A('logo.svg')} alt="" className="nav__logo" width={28} height={28} />
          <span className="nav__wordmark">ZedReq</span>
        </a>

        <ul className="nav__links" role="list">
          {['Features', 'Product', 'Pricing'].map((item) => (
            <li key={item}>
              <a href={`#${item.toLowerCase()}`} className="nav__link">{item}</a>
            </li>
          ))}
        </ul>

        <button
          className="nav__burger"
          aria-label="Open menu"
          aria-expanded={menuOpen}
          onClick={openMenu}
        >
          <span /><span /><span />
        </button>
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
        <section className="hero" id="hero" aria-label="Hero">
          {/* Background effects */}
          <div style={{ position: 'absolute', inset: 0, zIndex: 0 }} aria-hidden="true">
            <DarkVeil
              hueShift={399}
              noiseIntensity={0.0}
              scanlineIntensity={0.2}
              speed={0.8}
              scanlineFrequency={0.0}
              warpAmount={1.0}
              resolutionScale={1.0}
            />
          </div>
          <div className="hero__texture" aria-hidden="true" />

          {/* Orbit ring decorations */}
          <div className="hero__orbit-ring" style={{ width: 480, height: 480, top: '50%', right: '10%' }} aria-hidden="true" />
          <div className="hero__orbit-ring" style={{ width: 640, height: 640, top: '50%', right: '10%', opacity: 0.4 }} aria-hidden="true" />
          <div className="hero__orbit-ring" style={{ width: 760, height: 760, top: '50%', right: '10%', opacity: 0.2 }} aria-hidden="true" />

          {/* Orbiting feature icons */}
          <div className="hero__orbits" aria-hidden="true">
            {['icon-matching.svg','icon-interview.svg','icon-analytics.svg','icon-learning.svg','icon-network.svg'].map((icon, i) => (
              <div key={icon} className="hero__orbit-icon">
                <img src={A(icon)} alt="" />
              </div>
            ))}
          </div>

          {/* Status badge */}
          <div className="hero__status">
            <span className="hero__status-dot" aria-hidden="true" />
            Now in Early Access — Limited Seats
          </div>

          {/* Monumental headline */}
          <div className="hero__head" style={{ textAlign: 'center', alignItems: 'center' }}>
            <h1
              className="hero__hl"
              aria-label={HERO_HL_VARIANTS[hlIdx].ariaLabel}
            >
              <span className="hero__hl-line">Your Career.</span>
              <span className={`hero__hl-line hero__hl-line--swap${hlFade ? ' fade-out' : ''}`}>
                {HERO_HL_VARIANTS[hlIdx].line2}
              </span>
            </h1>

            {/* Rotating tagline */}
            <div className="hero__rotating" aria-live="polite" aria-atomic="true">
              <span className="hero__rot-sep" aria-hidden="true" />
              <span className={`hero__rot-text${rotFade ? ' fade-out' : ''}`}>
                {HERO_ROT[rotIdx]}
              </span>
            </div>

            {/* Lead */}
            <p className="hero__lead">
              ZedReq is a career operating system in one lane: AI that hardens your profile into proof,
              only surfaces roles that respect your trajectory, and runs interview-grade reps until the room
              feels smaller than your preparation — then keeps score until the offer lands.
            </p>

            {/* CTAs */}
            <div className="hero__actions" style={{ justifyContent: 'center' }}>
              <button className="btn btn--accent" onClick={openModal}>
                Reserve Early Access ↗
              </button>
              <a href="/login" className="btn btn--primary">
                Get Started
              </a>
            </div>
          </div>

          {/* Scroll indicator */}
          <div className="hero__scroll" aria-hidden="true">
            <span className="hero__scroll-line" />
            <span className="hero__scroll-label">Scroll</span>
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
              <article key={f.label} className="feat-card" role="listitem">
                <span className="feat-card__label">{f.label}</span>
                <img src={A(f.icon)} alt="" className="feat-card__icon" />
                <h3 className="feat-card__title">{f.title}</h3>
                <p className="feat-card__desc">{f.desc}</p>
                <span className="feat-card__arrow" aria-hidden="true">Learn more →</span>
              </article>
            ))}
          </div>
        </section>

        {/* ════════════ CHAPTERS (product showcase) ════════════ */}
        <section className="chapters" id="product" aria-label="Product showcase">

          {/* Chapter 1 — AI Profile */}
          <div className="chapter">
            <div className="chapter__img-wrap">
              <img
                src={A('chapter-ai-profile.jpg')}
                alt="AI Career Assistant interface"
                className="chapter__bg-img"
                loading="lazy"
                decoding="async"
              />
              {/* Score mockup overlaid on image */}
              <div className="chapter__mockup">
                <span className="chapter__mock-label">Profile Strength Analysis</span>
                <div className="chapter__bar-wrap">
                  {[
                    { name: 'Technical Skills', pct: '92%' },
                    { name: 'Soft Skills',      pct: '78%' },
                    { name: 'Leadership',        pct: '84%' },
                    { name: 'Domain Expertise', pct: '96%' },
                  ].map((row) => (
                    <div key={row.name} className="chapter__bar-row">
                      <span className="chapter__bar-name">{row.name}</span>
                      <div className="chapter__bar-track">
                        <div
                          className="chapter__bar-fill"
                          data-target={row.pct}
                          style={{ width: 0 }}
                        />
                      </div>
                      <span className="chapter__bar-pct">{row.pct}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="chapter__body reveal-right">
              <span className="chapter__num">01 — AI Profile</span>
              <h2 className="chapter__title">
                A resume that<br /><em>speaks for you</em>
              </h2>
              <p className="chapter__desc">
                Our AI reads your entire work history — every role, project, skill, and result —
                and builds a multi-dimensional profile that surfaces what static PDFs bury. Hiring
                managers see the whole story, not just the keywords.
              </p>

              {/* Score widget */}
              <div className="chapter__score-wrap">
                {[
                  { label: 'Match Score',   val: '94/100', pct: '94%',  delay: '0s'   },
                  { label: 'Visibility',    val: '88/100', pct: '88%',  delay: '0.15s' },
                  { label: 'Completeness',  val: '97/100', pct: '97%',  delay: '0.3s'  },
                ].map((row) => (
                  <div key={row.label} className="chapter__score-row">
                    <span className="chapter__score-label">{row.label}</span>
                    <div className="chapter__score-track">
                      <div
                        className="chapter__score-fill"
                        data-target={row.pct}
                        style={{ '--delay': row.delay, width: 0 }}
                      />
                    </div>
                    <span className="chapter__score-val">{row.val}</span>
                  </div>
                ))}
              </div>

              <a href="/features" className="chapter__link">Explore AI Profile →</a>
            </div>
          </div>

          {/* Chapter 2 — Smart Matching (reversed) */}
          <div className="chapter chapter--rev chapter--rev-globe">
            <div className="chapter__img-wrap" style={{ position: 'relative', overflow: 'hidden' }}>
              <GlobeAnimation />
            </div>

            <div className="chapter__body reveal-left">
              <span className="chapter__num">02 — Smart Matching</span>
              <h2 className="chapter__title">
                Roles that <em>actually fit</em>
              </h2>
              <p className="chapter__desc">
                Stop spray-and-praying. ZedReq&apos;s matching engine weighs 47 dimensions of fit —
                compensation, team structure, growth trajectory, commute, culture signals — and
                returns a ranked shortlist of roles where you&apos;re genuinely competitive.
              </p>
              <a href="/features" className="chapter__link">See how matching works →</a>
            </div>
          </div>

          {/* Chapter 3 — Interview Sim */}
          <div className="chapter">
            <div className="chapter__img-wrap">
              <img
                src={A('chapter-interview.jpg')}
                alt="AI Mock Interview platform"
                className="chapter__bg-img"
                loading="lazy"
                decoding="async"
              />
              <div className="chapter__mockup">
                <span className="chapter__mock-label">Live Interview Session</span>
                <div className="chapter__chat">
                  <div className="chapter__chat-row">
                    <div className="chapter__chat-bubble">
                      Walk me through a time you led a cross-functional project under pressure.
                    </div>
                  </div>
                  <div className="chapter__chat-row chapter__chat-row--user">
                    <div className="chapter__chat-bubble">
                      In Q3 at my previous role, I led a six-person team to ship a payment integration in 8 days...
                    </div>
                  </div>
                  <div className="chapter__chat-row">
                    <div className="chapter__chat-bubble">
                      Good structure. Try adding the specific outcome metric in your close — e.g., "which reduced churn by 12%".
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="chapter__body reveal-right">
              <span className="chapter__num">03 — Interview Simulator</span>
              <h2 className="chapter__title">
                Practice until<br /><em>it&apos;s automatic</em>
              </h2>
              <p className="chapter__desc">
                Realistic mock interviews tailored to your exact target role. Real-time coaching on
                structure, delivery, and technical depth. Twelve sessions and you won&apos;t feel the
                anxiety — just the conversation.
              </p>
              <a href="/login" className="chapter__link">Try a mock interview →</a>
            </div>
          </div>

          {/* Chapter 4 — LMS (reversed) */}
          <div className="chapter chapter--rev">
            <div className="chapter__img-wrap">
              <img
                src={lmsHeroImg}
                alt="ZedReq LMS — courses, modules, and progress"
                className="chapter__bg-img"
                loading="lazy"
                decoding="async"
              />
              <div className="chapter__mockup">
                <span className="chapter__mock-label">Course progress</span>
                <div className="chapter__bar-wrap">
                  {[
                    { name: 'Leadership', pct: '72%' },
                    { name: 'System design', pct: '88%' },
                    { name: 'Negotiation', pct: '54%' },
                    { name: 'Domain depth', pct: '91%' },
                  ].map((row) => (
                    <div key={row.name} className="chapter__bar-row">
                      <span className="chapter__bar-name">{row.name}</span>
                      <div className="chapter__bar-track">
                        <div
                          className="chapter__bar-fill"
                          data-target={row.pct}
                          style={{ width: 0 }}
                        />
                      </div>
                      <span className="chapter__bar-pct">{row.pct}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="chapter__body reveal-left">
              <span className="chapter__num">04 — LMS</span>
              <h2 className="chapter__title">
                Skills that<br /><em>compound</em>
              </h2>
              <p className="chapter__desc">
                Curated learning paths align with your profile gaps and target roles. Complete
                focused modules, earn shareable credentials, and keep your edge sharp — without
                leaving the platform.
              </p>
              <a href="/lms" className="chapter__link">Open the LMS →</a>
            </div>
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
          <div className="trust__head">
            <div>
              <span className="mono-label mono-label--accent reveal" style={{ marginBottom: '1.5rem', display: 'block' }}>
                Privacy &amp; Security
              </span>
              <h2 className="trust__hl reveal" id="trust-hl">
                Your data.<br /><em>Your rules.</em>
              </h2>
            </div>
            <p className="trust__sub reveal" style={{ '--d': 1 }}>
              We built ZedReq on a simple principle: your career data belongs to you, not
              to advertisers, not to recruiters, and not to us. Every feature, every data
              store, and every algorithm is designed around that belief.
            </p>
          </div>

          <div className="trust__grid">
            {TRUST_ITEMS.map((item) => (
              <div key={item.num} className="trust-item">
                <div className="trust-item__num">{item.num}</div>
                <div className="trust-item__title">{item.title}</div>
                <p className="trust-item__desc">{item.desc}</p>
              </div>
            ))}
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
              Start free.<br /><em>Scale when you&apos;re ready.</em>
            </h2>
          </div>

          <div className="pricing__grid pricing__grid--4">
            {/* Explorer — matches Choose Plan Free */}
            <div className="pricing__card reveal">
              <p className="pricing__tier">Explorer</p>
              <p className="pricing__price">Free</p>
              <p className="pricing__period">Forever</p>
              <hr className="pricing__rule" />
              <ul className="pricing__features pricing__teaser">
                {FREE_TEASER_WORDS.map((word) => (
                  <li key={word} className="pricing__feature pricing__teaser-word">
                    <i className="f-yes" aria-label="Included" />
                    {word}
                  </li>
                ))}
              </ul>
              <hr className="pricing__rule" />
              <p className="mono-label pricing__block-label">LIMITED USAGE</p>
              <ul className="pricing__features">
                {FREE_MONTHLY_LIMITS.map((line) => (
                  <PricingFeatureYes key={line} text={line} emph />
                ))}
              </ul>
              <a href="/login" className="btn btn--outline pricing__cta">
                Start Free
              </a>
            </div>

            {/* Professional — matches Choose Plan Pro */}
            <div className="pricing__card pricing__card--feat reveal">
              <span className="pricing__badge">Most Popular</span>
              <p className="pricing__tier">Professional</p>
              <p className="pricing__price">$49.99</p>
              <p className="pricing__period">per month</p>
              <hr className="pricing__rule" />
              <p className="mono-label pricing__block-label">Platform access:</p>
              <ul className="pricing__features">
                {PLATFORM_ACCESS_LINES.map((line) => (
                  <PricingFeatureYes key={line} text={line} />
                ))}
              </ul>
              <p className="mono-label pricing__block-label">Higher monthly limits</p>
              <ul className="pricing__features">
                {PRO_MONTHLY_LIMITS.map((line, i) => (
                  <PricingFeatureYes key={line} text={line} emph={i < 3} />
                ))}
              </ul>
              <a href="/login" className="btn pricing__cta">
                Get Started
              </a>
            </div>

            {/* Elite — matches Choose Plan Premium */}
            <div className="pricing__card reveal">
              <p className="pricing__tier">Elite</p>
              <p className="pricing__price">$89.99</p>
              <p className="pricing__period">per month</p>
              <hr className="pricing__rule" />
              <p className="mono-label pricing__block-label">Platform access:</p>
              <ul className="pricing__features">
                {PLATFORM_ACCESS_LINES.map((line) => (
                  <PricingFeatureYes key={line} text={line} />
                ))}
              </ul>
              <p className="mono-label pricing__block-label">Highest standard monthly limits</p>
              <ul className="pricing__features">
                {PREMIUM_MONTHLY_LIMITS.map((line, i) => (
                  <PricingFeatureYes key={line} text={line} emph={i < 3} />
                ))}
              </ul>
              <a href="/login" className="btn btn--outline pricing__cta">
                Go Elite
              </a>
            </div>

            {/* Enterprise — matches Choose Plan Enterprise */}
            <div className="pricing__card reveal">
              <p className="pricing__tier">Enterprise</p>
              <p className="pricing__card-desc">
                Unlimited usage for AI messages, courses, and interviews — assigned by agreement.
              </p>
              <p className="pricing__price">Custom</p>
              <p className="pricing__period">by arrangement</p>
              <hr className="pricing__rule" />
              <p className="mono-label pricing__block-label">Platform access:</p>
              <ul className="pricing__features">
                {PLATFORM_ACCESS_LINES.map((line) => (
                  <PricingFeatureYes key={line} text={line} />
                ))}
              </ul>
              <p className="mono-label pricing__block-label">Enterprise usage</p>
              <ul className="pricing__features">
                {ENTERPRISE_USAGE_FEATURES.map(({ text, emph }) => (
                  <PricingFeatureYes key={text} text={text} emph={emph} />
                ))}
              </ul>
              <a href="/login" className="btn btn--outline pricing__cta">
                Contact us
              </a>
            </div>
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
            <button className="btn btn--accent" onClick={openModal}>
              Reserve Early Access ↗
            </button>
            <a href="/login" className="btn btn--primary">
              Get Started
            </a>
          </div>
        </section>

        {/* ════════════ FOOTER ════════════ */}
        <footer className="footer">
          <div className="footer__inner">
            <a href="/" aria-label="ZedReq home">
              <img src={A('logo.svg')} alt="ZedReq" className="footer__logo" />
            </a>

            <nav className="footer__nav" aria-label="Footer navigation">
              {[
                { label: 'Features',  href: '/features' },
                { label: 'Product',   href: '#product' },
                { label: 'Pricing',   href: '/pricing' },
                { label: 'About',     href: '/about' },
                { label: 'Blog',      href: '/blog' },
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
                <p className="modal__success-sub">
                  Check your inbox for your reference code and Pro Plan discount details.
                </p>
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
                  <button
                    type="submit"
                    className="btn btn--accent"
                    style={{ justifyContent: 'center' }}
                    disabled={reserveLoading}
                  >
                    {reserveLoading ? 'Reserving…' : 'Reserve Seat'}
                  </button>
                </form>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
