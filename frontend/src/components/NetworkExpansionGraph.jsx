import React, { useState, useEffect, useRef, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import './NetworkExpansionGraph.css'

/* ═══════════════════════════════════════════════════════════════════════════
   Radial Graph Configuration
   ═══════════════════════════════════════════════════════════════════════════ */
const CX = 50
const CY = 50
const RING1_R = 22
const RING2_R = 40
const FIRST_COUNT = 7
const BASE_ANGLE = -Math.PI / 2
const SIBLING_SPREAD = 0.22

const NODE_R = { center: 5.5, first: 3.5, second: 2.5 }

// Build-up timing
const NODE_INTERVAL = 350 // ms between each node during initial build

/* ─── Helpers ────────────────────────────────────────────────────────────── */
const polar = (angle, r) => ({
  x: +(CX + r * Math.cos(angle)).toFixed(2),
  y: +(CY + r * Math.sin(angle)).toFixed(2),
})

const getInitials = (name) => {
  if (name === 'You') return 'Y'
  const p = name.split(' ')
  return p.length >= 2 ? p[0][0] + p[1][0] : p[0][0]
}

/* ═══════════════════════════════════════════════════════════════════════════
   Graph Data
   ═══════════════════════════════════════════════════════════════════════════ */
const FIRST_DEGREE_DATA = [
  { name: 'Sarah Chen', role: 'Product Designer', industry: 'Design', mutual: 12 },
  { name: 'James Miller', role: 'Software Engineer', industry: 'Technology', mutual: 8 },
  { name: 'Priya Patel', role: 'Data Scientist', industry: 'Technology', mutual: 15 },
  { name: 'Alex Johnson', role: 'Marketing Lead', industry: 'Marketing', mutual: 6 },
  { name: 'Maria Garcia', role: 'UX Researcher', industry: 'Design', mutual: 9 },
  { name: 'David Kim', role: 'Finance Analyst', industry: 'Finance', mutual: 4 },
  { name: 'Emma Wilson', role: 'Project Manager', industry: 'Technology', mutual: 7 },
]

const SECOND_DEGREE_MAP = {
  0: [
    { name: 'Omar Hassan', role: 'DevOps Engineer', industry: 'Technology', mutual: 3 },
    { name: 'Lisa Park', role: 'Content Strategist', industry: 'Marketing', mutual: 5 },
  ],
  1: [
    { name: 'Ryan Taylor', role: 'Backend Developer', industry: 'Technology', mutual: 2 },
    { name: 'Zara Ahmed', role: 'AI Engineer', industry: 'Technology', mutual: 11 },
  ],
  2: [
    { name: 'Chris Brown', role: 'Graphic Designer', industry: 'Design', mutual: 3 },
  ],
  3: [
    { name: 'Nina Petrov', role: 'Cloud Architect', industry: 'Technology', mutual: 7 },
    { name: 'Aisha Khan', role: 'HR Specialist', industry: 'Human Resources', mutual: 1 },
  ],
  4: [
    { name: 'Emily Zhang', role: 'ML Engineer', industry: 'Technology', mutual: 14 },
  ],
  5: [
    { name: 'Raj Malhotra', role: 'Product Manager', industry: 'Technology', mutual: 9 },
    { name: 'Sophie Laurent', role: 'Data Analyst', industry: 'Finance', mutual: 7 },
  ],
  6: [
    { name: 'Tom Rivera', role: 'QA Engineer', industry: 'Technology', mutual: 5 },
    { name: 'Lily Chen', role: 'Frontend Dev', industry: 'Technology', mutual: 6 },
  ],
}

/* ─── Build complete graph (ordered for progressive reveal) ──────────────── */
const buildCompleteGraph = () => {
  const orderedNodes = []
  const allEdges = []
  const firstAngles = []

  // Center
  orderedNodes.push({
    id: 'center', name: 'You', role: 'Your Profile',
    industry: '', mutual: 0, x: CX, y: CY,
    size: 'center', ring: 0,
  })

  // First-degree ring
  FIRST_DEGREE_DATA.forEach((data, i) => {
    const angle = BASE_ANGLE + (2 * Math.PI * i) / FIRST_COUNT
    firstAngles.push(angle)
    const pos = polar(angle, RING1_R)
    orderedNodes.push({ ...data, id: `f${i}`, ...pos, size: 'first', ring: 1 })
    allEdges.push({ from: 'center', to: `f${i}`, type: 'primary' })
  })

  // Second-degree ring (interleaved for spreading effect)
  const allSecond = []
  let sIdx = 0
  Object.entries(SECOND_DEGREE_MAP).forEach(([pIdx, children]) => {
    const parentAngle = firstAngles[parseInt(pIdx)]
    children.forEach((child, ci) => {
      const angle = parentAngle + (ci - (children.length - 1) / 2) * SIBLING_SPREAD
      const pos = polar(angle, RING2_R)
      allSecond.push({
        ...child, id: `s${sIdx}`, ...pos,
        size: 'second', ring: 2, parent: `f${pIdx}`, _ci: ci,
      })
      allEdges.push({ from: `f${pIdx}`, to: `s${sIdx}`, type: 'secondary' })
      sIdx++
    })
  })
  orderedNodes.push(
    ...allSecond.filter((n) => n._ci === 0),
    ...allSecond.filter((n) => n._ci === 1)
  )

  // Growth nodes
  const g0Angle = BASE_ANGLE + (2 * Math.PI * 2) / FIRST_COUNT + SIBLING_SPREAD
  const g0Pos = polar(g0Angle, RING2_R)
  orderedNodes.push({
    id: 'd0', name: 'Kai Nakamura', role: 'Security Engineer',
    industry: 'Technology', mutual: 4, ...g0Pos,
    size: 'second', ring: 2, parent: 'f2',
  })
  allEdges.push({ from: 'f2', to: 'd0', type: 'secondary' })

  const g1Angle = BASE_ANGLE + (2 * Math.PI * 4) / FIRST_COUNT + SIBLING_SPREAD
  const g1Pos = polar(g1Angle, RING2_R)
  orderedNodes.push({
    id: 'd1', name: 'Ava Williams', role: 'Brand Designer',
    industry: 'Design', mutual: 8, ...g1Pos,
    size: 'second', ring: 2, parent: 'f4',
  })
  allEdges.push({ from: 'f4', to: 'd1', type: 'secondary' })

  // Cross-connections
  allEdges.push({ from: 'f0', to: 'f1', type: 'cross' })
  allEdges.push({ from: 'f2', to: 'f6', type: 'cross' })
  allEdges.push({ from: 'f4', to: 'f5', type: 'cross' })
  allEdges.push({ from: 's3', to: 's4', type: 'cross' })

  return { orderedNodes, allEdges }
}

const GRAPH = buildCompleteGraph()

// Static position map
const POS_MAP = {}
GRAPH.orderedNodes.forEach((n) => {
  POS_MAP[n.id] = { x: n.x, y: n.y }
})

// Pre-compute stagger delays for edge loop animation (deterministic)
const EDGE_LOOP_DELAYS = {}
GRAPH.allEdges.forEach((e, i) => {
  EDGE_LOOP_DELAYS[`${e.from}-${e.to}`] = (i * 1.3) % 7
})

/* ─── Edge visual styles ─────────────────────────────────────────────────── */
const EDGE_STYLE = {
  primary: { strokeWidth: 1.2, opacity: 0.4 },
  secondary: { strokeWidth: 0.8, opacity: 0.28 },
  cross: { strokeWidth: 0.6, opacity: 0.15 },
}

/* ─── Suggested Professionals data ───────────────────────────────────────── */
const SUGGESTED_PROFESSIONALS = [
  { name: 'Emily Zhang', role: 'ML Engineer', mutual: 14 },
  { name: 'Raj Malhotra', role: 'Product Manager', mutual: 9 },
  { name: 'Sophie Laurent', role: 'Data Analyst', mutual: 7 },
]

/* ═══════════════════════════════════════════════════════════════════════════
   Component
   ═══════════════════════════════════════════════════════════════════════════ */
const NetworkExpansionGraph = () => {
  const [visibleCount, setVisibleCount] = useState(0)
  const [buildComplete, setBuildComplete] = useState(false)
  const [hoveredNode, setHoveredNode] = useState(null)
  const [suggestedId, setSuggestedId] = useState(null)
  const sectionRef = useRef(null)
  const visibleCountRef = useRef(0)

  visibleCountRef.current = visibleCount

  /* ─── One-time build-up ───────────────────────────────────────────────── */
  useEffect(() => {
    const totalNodes = GRAPH.orderedNodes.length
    const timeouts = []

    for (let i = 1; i <= totalNodes; i++) {
      timeouts.push(setTimeout(() => setVisibleCount(i), i * NODE_INTERVAL))
    }

    // Mark build as complete shortly after last node
    timeouts.push(
      setTimeout(() => setBuildComplete(true), totalNodes * NODE_INTERVAL + 600)
    )

    return () => timeouts.forEach((t) => clearTimeout(t))
  }, [])

  /* ─── Suggested highlight (second-degree only) ────────────────────────── */
  useEffect(() => {
    const iv = setInterval(() => {
      const count = visibleCountRef.current
      const secondIds = GRAPH.orderedNodes
        .slice(0, count)
        .filter((n) => n.ring === 2)
        .map((n) => n.id)
      if (secondIds.length > 0) {
        setSuggestedId(secondIds[Math.floor(Math.random() * secondIds.length)])
      } else {
        setSuggestedId(null)
      }
    }, 5000)
    return () => clearInterval(iv)
  }, [])

  /* ─── Derived visible data ────────────────────────────────────────────── */
  const visibleNodes = useMemo(
    () => GRAPH.orderedNodes.slice(0, visibleCount),
    [visibleCount]
  )

  const visibleNodeIds = useMemo(
    () => new Set(visibleNodes.map((n) => n.id)),
    [visibleNodes]
  )

  const visibleEdges = useMemo(
    () =>
      GRAPH.allEdges.filter(
        (e) => visibleNodeIds.has(e.from) && visibleNodeIds.has(e.to)
      ),
    [visibleNodeIds]
  )

  /* ─── Edge elements ───────────────────────────────────────────────────── */
  const edgeElements = useMemo(() => {
    return visibleEdges.map((edge) => {
      const from = POS_MAP[edge.from]
      const to = POS_MAP[edge.to]
      if (!from || !to) return null
      const s = EDGE_STYLE[edge.type] || EDGE_STYLE.secondary
      const edgeKey = `${edge.from}-${edge.to}`
      const loopDelay = EDGE_LOOP_DELAYS[edgeKey] || 0

      return (
        <motion.line
          key={edgeKey}
          x1={from.x}
          y1={from.y}
          x2={to.x}
          y2={to.y}
          stroke="#00B4D8"
          strokeWidth={s.strokeWidth}
          strokeLinecap="round"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={
            buildComplete
              ? {
                  pathLength: [0, 1, 1, 0],
                  opacity: [0, s.opacity, s.opacity * 0.8, 0],
                }
              : {
                  pathLength: 1,
                  opacity: s.opacity,
                }
          }
          transition={
            buildComplete
              ? {
                  duration: 5,
                  times: [0, 0.25, 0.7, 1],
                  repeat: Infinity,
                  delay: loopDelay,
                  ease: 'easeInOut',
                }
              : { duration: 0.8 }
          }
        />
      )
    })
  }, [visibleEdges, buildComplete])

  /* ─── Node elements (clean — no glow rings, no floating) ──────────────── */
  const nodeElements = useMemo(() => {
    return visibleNodes.map((node) => {
      const r = NODE_R[node.size] || 2.5
      const isSuggested = suggestedId === node.id && node.id !== 'center'
      const isCenter = node.id === 'center'

      return (
        <motion.g
          key={node.id}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
        >
          {/* Node body */}
          <motion.circle
            cx={node.x}
            cy={node.y}
            r={r}
            fill={isCenter ? '#00B4D8' : 'rgba(4, 12, 24, 0.95)'}
            stroke={isSuggested ? '#00d4ff' : isCenter ? '#00d4ff' : '#00B4D8'}
            strokeWidth={isCenter ? 1.2 : isSuggested ? 1.2 : 0.8}
            style={{
              cursor: 'pointer',
              filter: `drop-shadow(0 0 ${isCenter ? 6 : isSuggested ? 5 : 2}px rgba(0,180,216,${isSuggested ? '0.6' : '0.4'}))`,
            }}
            onMouseEnter={() => setHoveredNode(node)}
            onMouseLeave={() => setHoveredNode(null)}
            whileHover={{ scale: 1.15 }}
          />

          {/* Initials label */}
          <text
            x={node.x}
            y={node.y}
            textAnchor="middle"
            dominantBaseline="central"
            fontSize={r * 0.85}
            fill={isCenter ? '#fff' : isSuggested ? '#00d4ff' : '#00B4D8'}
            fontWeight="600"
            fontFamily="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
            style={{ pointerEvents: 'none', userSelect: 'none' }}
          >
            {getInitials(node.name)}
          </text>

          {/* Suggested match badge */}
          {isSuggested && (
            <motion.g
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
            >
              <rect
                x={node.x - 6.5}
                y={node.y - r - 5}
                width={13}
                height={2.8}
                rx={1.4}
                fill="rgba(0,180,216,0.2)"
                stroke="#00B4D8"
                strokeWidth="0.25"
              />
              <text
                x={node.x}
                y={node.y - r - 3.4}
                textAnchor="middle"
                dominantBaseline="central"
                fill="#00d4ff"
                fontSize="1.6"
                fontWeight="500"
                fontFamily="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
              >
                Suggested Match
              </text>
            </motion.g>
          )}
        </motion.g>
      )
    })
  }, [visibleNodes, suggestedId])

  return (
    <section className="network-expansion-section scroll-reveal" ref={sectionRef}>
      <div className="network-expansion-container">
        {/* Section Header */}
        <div className="network-header">
          <h2 className="network-headline">
            <span className="network-headline-glow">Expand Your Professional Network</span>
          </h2>
          <p className="network-subheading">
            Connect with professionals, collaborate with peers, and unlock
            opportunities through intelligent networking.
          </p>
        </div>

        {/* Main Content */}
        <div className="network-content">
          {/* Left: Radial Network Graph (65%) */}
          <div className="network-graph-wrapper">
            <div className="network-graph-container">
              <svg
                viewBox="0 0 100 100"
                className="network-svg"
                preserveAspectRatio="xMidYMid meet"
              >
                {/* Subtle reference rings */}
                <circle
                  cx={CX} cy={CY} r={RING1_R}
                  fill="none" stroke="rgba(0,180,216,0.05)"
                  strokeWidth="0.25" strokeDasharray="1.5 1.5"
                />
                <circle
                  cx={CX} cy={CY} r={RING2_R}
                  fill="none" stroke="rgba(0,180,216,0.035)"
                  strokeWidth="0.25" strokeDasharray="1.5 1.5"
                />

                {/* Connection edges */}
                {edgeElements}

                {/* Nodes */}
                {nodeElements}
              </svg>

              {/* Hover tooltip */}
              <AnimatePresence>
                {hoveredNode && hoveredNode.id !== 'center' && (
                  <motion.div
                    className="node-tooltip"
                    initial={{ opacity: 0, y: 8, scale: 0.9 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 8, scale: 0.9 }}
                    transition={{ duration: 0.2 }}
                    style={{
                      left: `${hoveredNode.x}%`,
                      top: `${hoveredNode.y - 8}%`,
                    }}
                  >
                    <div className="tooltip-avatar-circle">
                      <span className="tooltip-initials">
                        {getInitials(hoveredNode.name)}
                      </span>
                    </div>
                    <div className="tooltip-info">
                      <span className="tooltip-name">{hoveredNode.name}</span>
                      <span className="tooltip-role">{hoveredNode.role}</span>
                      {hoveredNode.industry && (
                        <span className="tooltip-industry">{hoveredNode.industry}</span>
                      )}
                      <span className="tooltip-mutual">
                        {hoveredNode.mutual} Mutual Connections
                      </span>
                    </div>
                    <button className="tooltip-connect-btn">Connect</button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Right: Suggested Professionals Panel (35%) */}
          <div className="network-insights-panel">
            <div className="insights-card">
              <h3 className="insights-card-title">Suggested Professionals</h3>
              <div className="suggested-list">
                {SUGGESTED_PROFESSIONALS.map((prof, i) => (
                  <motion.div
                    className="suggested-card"
                    key={prof.name}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 + i * 0.15 }}
                    whileHover={{
                      y: -3,
                      boxShadow: '0 8px 24px rgba(0,180,216,0.15)',
                    }}
                  >
                    <span className="suggested-avatar-circle">
                      <span className="suggested-avatar-initials">
                        {getInitials(prof.name)}
                      </span>
                    </span>
                    <div className="suggested-info">
                      <span className="suggested-name">{prof.name}</span>
                      <span className="suggested-role">{prof.role}</span>
                      <span className="suggested-mutual">{prof.mutual} mutual</span>
                    </div>
                    <button className="suggested-connect-btn">Connect</button>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
      
    </section>
  )
}

export default NetworkExpansionGraph
