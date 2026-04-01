import React, { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import SiteFooter from '../components/SiteFooter'
import TiltedCard from '../components/TiltedCard'
import { ZEDREQ_EMAIL, zedreqMailto } from '../config/contact'
import roshaanImg from '../../static/roshaan.png'
import '../css/pages/About.css'

const LINKEDIN_URL = 'https://www.linkedin.com/in/roshaan-ahmed'

/* ─── hooks ──────────────────────────────────────────── */
function useInView(threshold = 0.18) {
  const ref = useRef(null)
  const [on, setOn] = useState(false)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const io = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) { setOn(true); io.disconnect() } },
      { threshold }
    )
    io.observe(el)
    return () => io.disconnect()
  }, [threshold])
  return [ref, on]
}

function useCounter(to, active, ms = 1200) {
  const [v, setV] = useState(0)
  useEffect(() => {
    if (!active) return
    let f = 0
    const steps = Math.round(ms / 16)
    const id = setInterval(() => {
      f++
      setV(Math.round((1 - Math.pow(1 - f / steps, 3)) * to))
      if (f >= steps) { setV(to); clearInterval(id) }
    }, 16)
    return () => clearInterval(id)
  }, [active, to, ms])
  return v
}

/* ─── data ───────────────────────────────────────────── */
const STATS = [
  { n: '5+',   lbl: 'AI-powered modules' },
  { n: '4',    lbl: 'subscription tiers' },
  { n: '100%', lbl: 'privacy-first design' },
  { n: '1',    lbl: 'focused mission' },
]

const PILLARS = [
  { n: '01', title: 'Intelligent Matching',   body: 'Profile-driven job alignment and networking — not one-size-fits-all keyword searches. ZedReq surfaces roles that match your actual skills and career direction, not just CV words.' },
  { n: '02', title: 'Preparation That Sticks', body: 'Mock interviews, structured evaluations, and learning paths so your progress is measurable and honest. Specific feedback, not generic tips that apply to everyone.' },
  { n: '03', title: 'AI With Limits',          body: 'Assistants and recommendations that augment your judgement — not replace it. Transparent data practices. Terms that say what we actually do and what we don\'t.' },
  { n: '04', title: 'Trust Built In',          body: 'Continuous integrity work, secure accounts, and product behaviour that stays aligned to user expectations. Privacy-first isn\'t a marketing line; it shapes every feature decision.' },
]

const VALUES = [
  { title: 'Integrity', desc: 'Build without compromise. Honest matching, transparent data use, and decisions that respect users at every layer — not just where it\'s convenient.' },
  { title: 'Precision', desc: 'Quality over volume. One great match beats a hundred mediocre ones. We optimise for fit, not for numbers that look good on a dashboard.' },
  { title: 'Privacy',   desc: 'Data-minimal by design. We collect what\'s needed to deliver the feature. Consent is explicit, not buried in a terms document nobody reads.' },
  { title: 'Velocity',  desc: 'Ship early, listen closely, improve fast. Feedback from real users in production is worth more than months of internal speculation.' },
]

const TIMELINE = [
  { year: '2024', txt: 'Identified the gap: platforms matching CVs instead of people. Built the first prototype.' },
  { year: '2024', txt: 'Core matching engine, AI assistant, and user profiles shipped in a focused MVP.' },
  { year: '2025', txt: 'Expanded with LMS learning paths, mock interviews with AI feedback, feed, and networking.' },
  { year: '2025', txt: 'Launched public pages, four-tier plans, and enterprise inquiry.' },
  { year: '2026', txt: 'Scaling. Refining accuracy. Deepening AI coaching. Growing the community.' },
]

const PROJECTS = [
  {
    name: 'AI Sales Agent',
    stack: 'Google ADK · LangGraph · LangChain · Groq LLaMA-7B · Flask',
    detail: 'Conversational agent with structured lead capture, automated follow-ups, session management, and CSV logging.',
  },
  {
    name: 'Smart Land Encroachment Analysis',
    stack: 'YOLOv8 · Template matching · Roboflow · Python · SQLite',
    detail: '89% mAP, 90% template accuracy. Detects unauthorized land use from satellite imagery vs. official sitemaps.',
  },
]

/* ─── sub-components ─────────────────────────────────── */
function PillarRow({ n, title, body }) {
  const [open, setOpen] = useState(false)
  const [ref, on]       = useInView()
  const toggle = () => setOpen(o => !o)
  return (
    <div
      ref={ref}
      className={`ap-row${on ? ' ap-on' : ''}${open ? ' ap-row-open' : ''}`}
      onClick={toggle}
      role="button"
      tabIndex={0}
      aria-expanded={open}
      onKeyDown={e => (e.key === 'Enter' || e.key === ' ') && toggle()}
    >
      <div className="ap-row-head">
        <span className="ap-row-n">{n}</span>
        <span className="ap-row-title">{title}</span>
        <span className="ap-row-arrow" aria-hidden="true">{open ? '−' : '+'}</span>
      </div>
      {/* fix: open class must be on the body div itself for the CSS transition */}
      <div className={`ap-row-body${open ? ' open' : ''}`} aria-hidden={!open}>
        <p>{body}</p>
      </div>
    </div>
  )
}

function ValCard({ title, desc, delay }) {
  const [ref, on] = useInView()
  return (
    <div ref={ref} className={`ap-val${on ? ' ap-on' : ''}`} style={{ transitionDelay: `${delay}ms` }}>
      <div className="ap-val-top" aria-hidden="true" />
      <h3 className="ap-val-t">{title}</h3>
      <p  className="ap-val-d">{desc}</p>
    </div>
  )
}

function TlItem({ year, txt, delay }) {
  const [ref, on] = useInView()
  return (
    <div ref={ref} className={`ap-tl${on ? ' ap-on' : ''}`} style={{ transitionDelay: `${delay}ms` }}>
      <span className="ap-tl-y">{year}</span>
      <span className="ap-tl-bar" aria-hidden="true" />
      <p    className="ap-tl-txt">{txt}</p>
    </div>
  )
}

function StatCard({ n, lbl, active, to, ms }) {
  const count = useCounter(to, active, ms)
  const display = to ? `${count}${n.replace(/[0-9]/g, '')}` : n
  return (
    <div className="ap-stat-card">
      <span className="ap-stat-n">{display}</span>
      <span className="ap-stat-l">{lbl}</span>
    </div>
  )
}

/* ─── page ───────────────────────────────────────────── */
export default function About() {
  const [statsRef,   statsOn]   = useInView(0.1)
  const [founderRef, founderOn] = useInView(0.1)

  return (
    <div className="ap">

      {/* ── nav ── */}
      <header className="ap-nav">
        <Link to="/"           className="ap-nav-logo">ZedReq</Link>
        <nav className="ap-nav-links" aria-label="Primary">
          <Link to="/">Home</Link>
          <Link to="/features">Features</Link>
          <Link to="/pricing">Pricing</Link>
          <Link to="/get-started" className="ap-nav-cta">Get started</Link>
        </nav>
      </header>

      {/* ── hero ── */}
      <section className="ap-hero" aria-label="Hero">
        <div className="ap-hero-eyebrow">
          <span>About ZedReq</span>
          <span>Est. 2024</span>
        </div>
        <h1 className="ap-hero-h1">
          We&apos;re building<br />
          the platform that<br />
          <em>hiring deserves.</em>
        </h1>
        <div className="ap-hero-split">
          <p className="ap-hero-desc">
            ZedReq connects people to roles using AI matching, structured
            preparation, and honest feedback. No keyword games. No fake
            urgency. No dark patterns.
          </p>
          <p className="ap-hero-aside">
            A focused, founder-led team building the career tools we
            always wished existed.
          </p>
        </div>
        <div className="ap-rule" aria-hidden="true" />
      </section>

      {/* ── quote ── */}
      <section className="ap-quote-sec" aria-label="Manifesto">
        <blockquote className="ap-quote">
          &ldquo;Job boards match CVs.<br />
          We match <mark>potential.</mark>&rdquo;
        </blockquote>
      </section>

      {/* ── stats (luxury cards) ── */}
      <section className="ap-stats-sec" ref={statsRef} aria-label="At a glance">
        <div className="ap-stats-grid">
          <StatCard n="5+"   lbl="AI-powered modules"      active={statsOn} to={5}   ms={700}  />
          <StatCard n="4"    lbl="subscription tiers"      active={statsOn} to={4}   ms={900}  />
          <StatCard n="100%" lbl="privacy-first design"    active={statsOn} to={100} ms={1300} />
          <StatCard n="1"    lbl="focused mission"         active={statsOn} to={1}   ms={500}  />
        </div>
      </section>

      {/* ── pillars ── */}
      <div className="ap-rule ap-rule-full" aria-hidden="true" />
      <section className="ap-section" aria-labelledby="ap-pillars-h">
        <div className="ap-section-lbl">
          <h2 id="ap-pillars-h">What we build</h2>
          <p>Four pillars. One coherent platform.</p>
        </div>
        <div className="ap-rows">
          {PILLARS.map(p => <PillarRow key={p.n} {...p} />)}
        </div>
      </section>

      {/* ── values (luxury cards) ── */}
      <div className="ap-rule ap-rule-full" aria-hidden="true" />
      <section className="ap-section" aria-labelledby="ap-vals-h">
        <div className="ap-section-lbl">
          <h2 id="ap-vals-h">How we work</h2>
          <p>The principles that keep us honest when trade-offs get hard.</p>
        </div>
        <div className="ap-vals-grid">
          {VALUES.map((v, i) => (
            <ValCard key={v.title} title={v.title} desc={v.desc} delay={i * 65} />
          ))}
        </div>
      </section>

      {/* ── timeline ── */}
      <div className="ap-rule ap-rule-full" aria-hidden="true" />
      <section className="ap-section" aria-labelledby="ap-story-h">
        <div className="ap-section-lbl">
          <h2 id="ap-story-h">Our story</h2>
          <p>From a frustrated idea to a working platform.</p>
        </div>
        <div className="ap-tl-list">
          {TIMELINE.map((t, i) => (
            <TlItem key={i} year={t.year} txt={t.txt} delay={i * 80} />
          ))}
        </div>
      </section>

      {/* ── founder ── */}
      <div className="ap-rule ap-rule-full" aria-hidden="true" />
      <section className="ap-founder-sec" aria-labelledby="ap-founder-h">
        <div
          ref={founderRef}
          className={`ap-founder-wrap${founderOn ? ' ap-on' : ''}`}
        >
          <div className="ap-founder-left">
            <TiltedCard
              imageSrc={roshaanImg}
              altText="Roshaan Ahmed — Founder & CEO, ZedReq"
              captionText="Roshaan Ahmed"
              containerWidth="340px"
              containerHeight="440px"
              imageWidth="340px"
              imageHeight="440px"
              spotlightRadius={160}
              rotateAmplitude={12}
              scaleOnHover={1.05}
              showMobileWarning={false}
              showTooltip
              displayOverlayContent
              overlayContent={
                <div className="ap-founder-card-overlay">
                  <span>Roshaan Ahmed</span>
                  <span>Founder &amp; CEO</span>
                </div>
              }
            />
            <ul className="ap-founder-tags" aria-label="Roles">
              <li>Founder.</li>
              <li>Engineer.</li>
              <li>Builder.</li>
            </ul>
          </div>

          <div className="ap-founder-right">
            <div className="ap-founder-id">
              <h2 className="ap-founder-name" id="ap-founder-h">Roshaan Ahmed</h2>
              <p className="ap-founder-role">
                Founder &amp; CEO, ZedReq<br />
                Full Stack AI / LLM Engineer ·{' '}
                <a href="https://disrupt.com" target="_blank" rel="noopener noreferrer">
                  Disrupt.com
                </a>{' '}
                (formerly Gaditek)
              </p>
              <p className="ap-founder-loc">500+ connections</p>
            </div>

            <div className="ap-founder-divider" aria-hidden="true" />

            <p className="ap-founder-bio">
              Passionate technologist with hands-on expertise in AI, machine learning, and
              full-stack engineering — focused on building intelligent solutions and turning
              data into actionable insight. Alumnus of{' '}
              <strong>FAST NUCES</strong>, where he served as{' '}
              <strong>Head of Data Science for PROCOM&apos;25</strong>, organising and running a
              Kaggle-style data science competition attended by problem-solvers across Pakistan.
            </p>

            <p className="ap-founder-bio">
              Runner-up at <strong>IBA HackFest Datathon</strong> (GenAI track, alongside
              Muneer Raza) and recognised by Emergen in a sponsored data challenge at
              IBA. Holds <strong>Microsoft Azure AI Services</strong> certification. Career
              spans data analytics at Beats by Dre (Extern), trainee AI development at
              Z360 / Zikra Infotech, systems work at xSystems, and now full-stack AI
              engineering at Disrupt.com (formerly Gaditek).
            </p>

            <ul className="ap-founder-pills">
              {['AI / ML engineering', 'Full-stack & LLMs', 'Machine learning', 'Android development', 'Data analytics'].map(t => (
                <li key={t}>{t}</li>
              ))}
            </ul>

            {/* project cards */}
            <div className="ap-projects-grid">
              {PROJECTS.map(pr => (
                <div className="ap-proj-card" key={pr.name}>
                  <span className="ap-proj-name">{pr.name}</span>
                  <span className="ap-proj-stack">{pr.stack}</span>
                  <p className="ap-proj-detail">{pr.detail}</p>
                </div>
              ))}
            </div>

            <a href={LINKEDIN_URL} target="_blank" rel="noopener noreferrer" className="ap-linkedin">
              View on LinkedIn ↗
            </a>
          </div>
        </div>
      </section>

      {/* ── cta ── */}
      <section className="ap-cta" aria-labelledby="ap-cta-h">
        <div className="ap-cta-inner">
          <h2 className="ap-cta-h" id="ap-cta-h">
            Build your career<br />on honest ground.
          </h2>
          <div className="ap-cta-actions">
            <Link to="/get-started" className="ap-cta-btn">
              Create free account →
            </Link>
            <a href={zedreqMailto('Partnership enquiry')} className="ap-cta-email">
              {ZEDREQ_EMAIL}
            </a>
          </div>
        </div>
      </section>

      <SiteFooter />
    </div>
  )
}
