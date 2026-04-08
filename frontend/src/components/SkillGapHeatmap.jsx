import React, { useState, useEffect, useRef, useMemo } from 'react'
import './SkillGapHeatmap.css'

/* ── demo data ─────────────────────────────────────────────── */
const DEFAULT_SKILLS = [
  { name: 'Data Structures', score: 82, threshold: 60, recommended_course_id: 'ds_01' },
  { name: 'Algorithms', score: 55, threshold: 60, recommended_course_id: 'algo_01' },
  { name: 'System Design', score: 48, threshold: 60, recommended_course_id: 'sys_design_01' },
  { name: 'Backend Dev', score: 78, threshold: 60, recommended_course_id: 'backend_01' },
  { name: 'Communication', score: 52, threshold: 60, recommended_course_id: 'comm_01' },
  { name: 'Problem Solving', score: 88, threshold: 60, recommended_course_id: 'ps_01' },
  { name: 'Testing', score: 70, threshold: 60, recommended_course_id: 'test_01' },
  { name: 'API Design', score: 75, threshold: 60, recommended_course_id: 'api_01' },
]

const COURSE_DATA = {
  ds_01: {
    title: 'Advanced Data Structures',
    duration: '3 Weeks',
    difficulty: 'Advanced',
    focus: 'Trees, graphs, hash maps, heaps',
    weeks: [
      { week: 1, title: 'Trees & Graph Traversals', desc: 'Deep-dive into binary trees, BSTs, AVL trees, and common graph traversal patterns used in interviews.' },
      { week: 2, title: 'Hash Maps & Heaps', desc: 'Explore hash-table internals, collision strategies, and priority queue applications.' },
      { week: 3, title: 'Advanced Applications', desc: 'Solve real-world problems combining multiple data structures with timed practice.' },
    ],
  },
  algo_01: {
    title: 'Algorithm Mastery',
    duration: '4 Weeks',
    difficulty: 'Intermediate',
    focus: 'Dynamic programming, greedy, divide & conquer',
    weeks: [
      { week: 1, title: 'Sorting & Searching', desc: 'Master comparison-based and linear-time sorts, binary search variations, and two-pointer techniques.' },
      { week: 2, title: 'Dynamic Programming', desc: 'Build intuition for state transitions, memoization, and tabulation across classic DP families.' },
      { week: 3, title: 'Greedy & Backtracking', desc: 'Learn when greedy works, how to prove optimality, and systematic backtracking frameworks.' },
      { week: 4, title: 'Mock Coding Challenges', desc: 'Timed coding sessions with automated scoring and detailed solution walk-throughs.' },
    ],
  },
  sys_design_01: {
    title: 'Mastering System Design',
    duration: '4 Weeks',
    difficulty: 'Intermediate',
    focus: 'Architecture, scalability, performance',
    weeks: [
      { week: 1, title: 'Fundamentals', desc: 'Client-server model, REST/gRPC, load balancing, caching layers, and CDN basics.' },
      { week: 2, title: 'Scaling Concepts', desc: 'Horizontal vs vertical scaling, sharding, replication, and consistent hashing.' },
      { week: 3, title: 'Distributed Systems', desc: 'CAP theorem, event-driven architecture, message queues, and consensus protocols.' },
      { week: 4, title: 'Mock Design Interviews', desc: 'End-to-end design practice with AI-scored rubrics for communication and completeness.' },
    ],
  },
  backend_01: {
    title: 'Backend Development Deep Dive',
    duration: '5 Weeks',
    difficulty: 'Intermediate',
    focus: 'APIs, databases, microservices',
    weeks: [
      { week: 1, title: 'REST & GraphQL APIs', desc: 'Design clean API contracts, handle versioning, pagination, and error conventions.' },
      { week: 2, title: 'Database Design', desc: 'Normalization, indexing strategies, query optimization, and NoSQL trade-offs.' },
      { week: 3, title: 'Authentication & Security', desc: 'OAuth 2.0, JWTs, RBAC, CORS, rate limiting, and OWASP top-10 mitigations.' },
      { week: 4, title: 'Microservices Architecture', desc: 'Service decomposition, inter-service communication, saga patterns, and observability.' },
      { week: 5, title: 'Deployment & DevOps', desc: 'CI/CD pipelines, containerization, Kubernetes basics, and blue-green deployments.' },
    ],
  },
  comm_01: {
    title: 'Communication for Engineers',
    duration: '3 Weeks',
    difficulty: 'Beginner',
    focus: 'Presentation, documentation, collaboration',
    weeks: [
      { week: 1, title: 'Technical Writing', desc: 'Structure clear design docs, RFCs, and runbooks that drive alignment.' },
      { week: 2, title: 'Presentation Skills', desc: 'Craft compelling demo narratives and handle Q&A with confidence.' },
      { week: 3, title: 'Stakeholder Communication', desc: 'Translate technical trade-offs into business language for cross-functional teams.' },
    ],
  },
  ps_01: {
    title: 'Problem Solving Frameworks',
    duration: '3 Weeks',
    difficulty: 'Advanced',
    focus: 'Analytical thinking, pattern recognition',
    weeks: [
      { week: 1, title: 'Problem Decomposition', desc: 'Break complex challenges into manageable sub-problems using structured frameworks.' },
      { week: 2, title: 'Pattern Recognition', desc: 'Identify recurring problem archetypes to apply proven solution templates faster.' },
      { week: 3, title: 'Optimization Techniques', desc: 'Reduce time & space complexity through amortized analysis and clever re-framing.' },
    ],
  },
  test_01: {
    title: 'Software Testing Mastery',
    duration: '3 Weeks',
    difficulty: 'Intermediate',
    focus: 'Unit, integration, E2E testing',
    weeks: [
      { week: 1, title: 'Unit Testing Fundamentals', desc: 'Isolation strategies, mocking, property-based tests, and coverage analysis.' },
      { week: 2, title: 'Integration & E2E Testing', desc: 'Contract tests, test containers, and reliable browser-level test automation.' },
      { week: 3, title: 'TDD & CI/CD Testing', desc: 'Red-green-refactor workflow, flaky-test triage, and pipeline integration.' },
    ],
  },
  api_01: {
    title: 'API Design Patterns',
    duration: '3 Weeks',
    difficulty: 'Intermediate',
    focus: 'REST, GraphQL, gRPC, versioning',
    weeks: [
      { week: 1, title: 'REST Best Practices', desc: 'Resource naming, HATEOAS, idempotency, and pagination standards.' },
      { week: 2, title: 'GraphQL & gRPC', desc: 'Schema-first development, resolvers, code generation, and performance tuning.' },
      { week: 3, title: 'API Security & Versioning', desc: 'Rate limiting, API keys, OAuth scopes, and backward-compatible evolution.' },
    ],
  },
}

/* ── geometry helpers ──────────────────────────────────────── */
const CX = 200
const CY = 200
const R = 130
const RING_R = 52
const RING_CIRC = 2 * Math.PI * RING_R // ≈ 326.73

const getAngle = (i, total) => -Math.PI / 2 + (2 * Math.PI * i) / total

const getPoint = (i, score, total) => {
  const a = getAngle(i, total)
  return { x: CX + R * (score / 100) * Math.cos(a), y: CY + R * (score / 100) * Math.sin(a) }
}

const getLabelPos = (i, total) => {
  const a = getAngle(i, total)
  const d = R + 28
  return { x: CX + d * Math.cos(a), y: CY + d * Math.sin(a) }
}

const getAnchor = (x) => {
  if (x > CX + 10) return 'start'
  if (x < CX - 10) return 'end'
  return 'middle'
}

/* ── component ─────────────────────────────────────────────── */
const SkillGapHeatmap = ({ skills = DEFAULT_SKILLS }) => {
  const sectionRef = useRef(null)
  const [isVisible, setIsVisible] = useState(false)
  const [animateProgress, setAnimateProgress] = useState(false)
  const [displayScore, setDisplayScore] = useState(0)
  const [tooltipData, setTooltipData] = useState(null)
  const [selectedSkill, setSelectedSkill] = useState(null)
  const [popupOpen, setPopupOpen] = useState(false)
  const [showStrong, setShowStrong] = useState(false)
  const [expandedWeek, setExpandedWeek] = useState(null)

  /* derived */
  const overallScore = useMemo(
    () => Math.round(skills.reduce((s, sk) => s + sk.score, 0) / skills.length),
    [skills],
  )
  const weakSkills = useMemo(() => skills.filter((s) => s.score < s.threshold), [skills])
  const strongSkills = useMemo(() => skills.filter((s) => s.score >= s.threshold), [skills])

  const polygonPts = useMemo(
    () =>
      skills
        .map((s, i) => {
          const p = getPoint(i, s.score, skills.length)
          return `${p.x},${p.y}`
        })
        .join(' '),
    [skills],
  )

  /* ── observers / counters ───────────────────────────────── */
  useEffect(() => {
    const el = sectionRef.current
    if (!el) return undefined
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          setTimeout(() => setAnimateProgress(true), 700)
          obs.unobserve(entry.target)
        }
      },
      { threshold: 0.18 },
    )
    obs.observe(el)
    return () => obs.disconnect()
  }, [])

  useEffect(() => {
    if (!animateProgress) return undefined
    let cur = 0
    const step = Math.max(1, Math.ceil(overallScore / 45))
    const id = setInterval(() => {
      cur += step
      if (cur >= overallScore) {
        cur = overallScore
        clearInterval(id)
      }
      setDisplayScore(cur)
    }, 28)
    return () => clearInterval(id)
  }, [animateProgress, overallScore])

  /* ── handlers ───────────────────────────────────────────── */
  const openCourse = (skill) => {
    setSelectedSkill(skill)
    setPopupOpen(true)
    setExpandedWeek(null)
  }

  const closePopup = () => {
    setPopupOpen(false)
    setTimeout(() => {
      setSelectedSkill(null)
      setExpandedWeek(null)
    }, 320)
  }

  const getCourse = (skill) =>
    COURSE_DATA[skill?.recommended_course_id] || COURSE_DATA.sys_design_01

  /* ── best weak‑skill insight line ───────────────────────── */
  const insightSkill = weakSkills.length > 0 ? weakSkills.reduce((a, b) => (a.score < b.score ? a : b)) : null

  /* ── render ─────────────────────────────────────────────── */
  return (
    <section className="sgh-section" ref={sectionRef}>
      {/* background */}
      <div className="sgh-bg-grid" />
      <div className="sgh-bg-glow" />

      <div className={`sgh-container ${isVisible ? 'sgh-visible' : ''}`}>
        {/* ─── two-column layout: heading | graphics ─────────── */}
        <div className="sgh-layout">
          {/* Column 1: Heading */}
          <header className="sgh-header">
            <h2>Close Your Skill Gaps with AI Precision</h2>
            <p>Our adaptive learning engine analyzes your profile and highlights exactly what you need to improve.</p>
            <div className="sgh-divider" />
          </header>

          {/* Column 2: All graphics (radar + panel) */}
          <div className="sgh-content">
            {/* LEFT — radar */}
          <div className="sgh-radar-area">
            <div className="sgh-radar-wrap">
              <svg viewBox="0 0 400 400" className="sgh-radar-svg" aria-label="Skill radar chart">
                <defs>
                  <radialGradient id="sghFill" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor="#1585A1" stopOpacity="0.45" />
                    <stop offset="100%" stopColor="#1585A1" stopOpacity="0.08" />
                  </radialGradient>
                </defs>

                {/* grid rings */}
                {[0.25, 0.5, 0.75, 1].map((s) => (
                  <circle key={s} cx={CX} cy={CY} r={R * s} className="sgh-grid-ring" />
                ))}

                {/* axes */}
                {skills.map((_, i) => {
                  const a = getAngle(i, skills.length)
                  return (
                    <line
                      key={i}
                      x1={CX}
                      y1={CY}
                      x2={CX + R * Math.cos(a)}
                      y2={CY + R * Math.sin(a)}
                      className="sgh-axis"
                    />
                  )
                })}

                {/* threshold polygon (faint ring) */}
                <polygon
                  points={skills
                    .map((s, i) => {
                      const p = getPoint(i, s.threshold, skills.length)
                      return `${p.x},${p.y}`
                    })
                    .join(' ')}
                  className="sgh-threshold-poly"
                />

                {/* skill polygon */}
                <polygon
                  points={polygonPts}
                  className={`sgh-skill-poly ${isVisible ? 'drawn' : ''}`}
                  fill="url(#sghFill)"
                />

                {/* axis labels */}
                {skills.map((s, i) => {
                  const pos = getLabelPos(i, skills.length)
                  return (
                    <text
                      key={i}
                      x={pos.x}
                      y={pos.y}
                      textAnchor={getAnchor(pos.x)}
                      dominantBaseline="middle"
                      className="sgh-label"
                    >
                      {s.name}
                    </text>
                  )
                })}

                {/* data points + weak pulse */}
                {skills.map((s, i) => {
                  const p = getPoint(i, s.score, skills.length)
                  const weak = s.score < s.threshold
                  return (
                    <g key={i}>
                      {weak && <circle cx={p.x} cy={p.y} r={14} className="sgh-pulse-ring" />}
                      {/* invisible hit target */}
                      <circle
                        cx={p.x}
                        cy={p.y}
                        r={16}
                        fill="transparent"
                        style={{ cursor: weak ? 'pointer' : 'default' }}
                        onMouseEnter={() =>
                          setTooltipData({ skill: s, x: (p.x / 400) * 100, y: (p.y / 400) * 100 })
                        }
                        onMouseLeave={() => setTooltipData(null)}
                        onClick={() => weak && openCourse(s)}
                      />
                      <circle
                        cx={p.x}
                        cy={p.y}
                        r={weak ? 5 : 3.5}
                        className={`sgh-dot ${weak ? 'weak' : 'strong'}`}
                        style={{ pointerEvents: 'none' }}
                      />
                    </g>
                  )
                })}
              </svg>

              {/* tooltip */}
              {tooltipData && (
                <div
                  className="sgh-tooltip"
                  style={{ left: `${tooltipData.x}%`, top: `${tooltipData.y}%` }}
                >
                  <span className="sgh-tooltip-name">{tooltipData.skill.name}</span>
                  <span>Current Level: {tooltipData.skill.score}</span>
                  <span>Target Level: {Math.min(tooltipData.skill.threshold + 15, 100)}</span>
                </div>
              )}
            </div>

            {/* AI Insight badge */}
            {insightSkill && (
              <div className="sgh-insight">
                <div className="sgh-insight-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24">
                    <path d="M12 2a7 7 0 0 1 7 7c0 2.4-1.2 4.5-3 5.7V17a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-2.3A7 7 0 0 1 12 2z" />
                    <path d="M9 21h6" />
                    <path d="M10 17v4" />
                    <path d="M14 17v4" />
                  </svg>
                </div>
                <div className="sgh-insight-text">
                  <span className="sgh-insight-label">AI Insight</span>
                  <p>
                    Improving {insightSkill.name} by {insightSkill.threshold - insightSkill.score + 15}% increases
                    your match rate by 34%.
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* RIGHT — panel */}
          <div className="sgh-panel">
            {/* overall score */}
            <div className="sgh-score-block">
              <div className="sgh-ring-wrap">
                <svg viewBox="0 0 120 120" className="sgh-ring-svg">
                  <circle cx="60" cy="60" r={RING_R} className="sgh-ring-bg" />
                  <circle
                    cx="60"
                    cy="60"
                    r={RING_R}
                    className={`sgh-ring-fill ${animateProgress ? 'animate' : ''}`}
                    strokeDasharray={RING_CIRC}
                    strokeDashoffset={animateProgress ? RING_CIRC - (overallScore / 100) * RING_CIRC : RING_CIRC}
                  />
                </svg>
                <span className="sgh-ring-value">{displayScore}%</span>
              </div>
              <span className="sgh-ring-label">Overall Readiness</span>
            </div>

            {/* weak areas */}
            <div className="sgh-skill-list">
              <h3>Areas to Improve</h3>
              {weakSkills.length === 0 && <p className="sgh-no-weak">All skills above threshold — great job!</p>}
              {weakSkills.map((sk) => {
                const p = getPoint(skills.indexOf(sk), sk.score, skills.length)
                return (
                  <button
                    key={sk.name}
                    className="sgh-skill-row"
                    onClick={() => openCourse(sk)}
                    onMouseEnter={() =>
                      setTooltipData({
                        skill: sk,
                        x: (p.x / 400) * 100,
                        y: (p.y / 400) * 100,
                      })
                    }
                    onMouseLeave={() => setTooltipData(null)}
                  >
                    <div className="sgh-skill-info">
                      <span>{sk.name}</span>
                      <span className="sgh-pct">{sk.score}%</span>
                    </div>
                    <div className="sgh-bar">
                      <div
                        className="sgh-bar-fill weak"
                        style={{ width: animateProgress ? `${sk.score}%` : '0%' }}
                      />
                    </div>
                  </button>
                )
              })}
            </div>

            {/* strong areas toggle */}
            <button className="sgh-strong-toggle" onClick={() => setShowStrong((v) => !v)}>
              <span>Strong Areas</span>
              <svg viewBox="0 0 24 24" className={showStrong ? 'open' : ''}>
                <path d="M6 9l6 6 6-6" />
              </svg>
            </button>

            {showStrong && (
              <div className="sgh-skill-list sgh-strong-list">
                {strongSkills.map((sk) => (
                  <div key={sk.name} className="sgh-skill-row static">
                    <div className="sgh-skill-info">
                      <span>{sk.name}</span>
                      <span className="sgh-pct strong">{sk.score}%</span>
                    </div>
                    <div className="sgh-bar">
                      <div
                        className="sgh-bar-fill strong"
                        style={{ width: animateProgress ? `${sk.score}%` : '0%' }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}

          </div>
        </div>
        </div>
      </div>

      {/* ─── course popup ────────────────────────────────────── */}
      {selectedSkill && (
        <>
          <div
            className={`sgh-overlay ${popupOpen ? 'show' : ''}`}
            onClick={closePopup}
            role="presentation"
          />
          <aside className={`sgh-popup ${popupOpen ? 'show' : ''}`} aria-label="Recommended course">
            <button className="sgh-popup-close" onClick={closePopup} aria-label="Close">
              <svg viewBox="0 0 24 24">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>

            <h3>
              Recommended Course: <span>{getCourse(selectedSkill).title}</span>
            </h3>
            <p className="sgh-popup-sub">Generated based on your skill gap analysis.</p>

            <div className="sgh-popup-meta-list">
              <div className="sgh-popup-meta">
                <svg viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 6v6l4 2" />
                </svg>
                <span>Estimated Duration: {getCourse(selectedSkill).duration}</span>
              </div>
              <div className="sgh-popup-meta">
                <svg viewBox="0 0 24 24">
                  <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z" />
                  <line x1="4" y1="22" x2="4" y2="15" />
                </svg>
                <span>Difficulty: {getCourse(selectedSkill).difficulty}</span>
              </div>
              <div className="sgh-popup-meta">
                <svg viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                </svg>
                <span>Skill Focus: {getCourse(selectedSkill).focus}</span>
              </div>
            </div>

            {/* week accordion */}
            <div className="sgh-popup-outline">
              {getCourse(selectedSkill).weeks.map((w) => (
                <div key={w.week} className={`sgh-week-item ${expandedWeek === w.week ? 'open' : ''}`}>
                  <button
                    className="sgh-week-trigger"
                    onClick={() => setExpandedWeek(expandedWeek === w.week ? null : w.week)}
                    aria-expanded={expandedWeek === w.week}
                  >
                    <span>
                      Week {w.week} — {w.title}
                    </span>
                    <svg viewBox="0 0 24 24" className="sgh-week-chev">
                      <path d="M6 9l6 6 6-6" />
                    </svg>
                  </button>
                  <div className="sgh-week-body">
                    <p>{w.desc}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="sgh-popup-actions">
              <button className="sgh-btn-primary" onClick={closePopup}>
                Start Learning
              </button>
              <button className="sgh-btn-secondary" onClick={closePopup}>
                View Full Curriculum
              </button>
            </div>
          </aside>
        </>
      )}
    </section>
  )
}

export default SkillGapHeatmap
