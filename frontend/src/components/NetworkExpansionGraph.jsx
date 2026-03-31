import React, { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import './NetworkExpansionGraph.css'

/* ═══════════════════════════════════════════════════════════════════════════
   Rotating Globe — canvas-based dot sphere
   ═══════════════════════════════════════════════════════════════════════════ */
/* ── Helpers ─────────────────────────────────────────────────────────────── */
const toVec = (lat, lon) => {
  const φ = (lat * Math.PI) / 180
  const λ = (lon * Math.PI) / 180
  return [Math.cos(φ) * Math.cos(λ), Math.sin(φ), Math.cos(φ) * Math.sin(λ)]
}

const slerp = (a, b, t) => {
  let d = Math.min(1, Math.max(-1, a[0]*b[0] + a[1]*b[1] + a[2]*b[2]))
  const θ = Math.acos(d)
  if (θ < 0.0001) return [a[0], a[1], a[2]]
  const s = Math.sin(θ)
  const wa = Math.sin((1 - t) * θ) / s
  const wb = Math.sin(t * θ) / s
  return [wa*a[0]+wb*b[0], wa*a[1]+wb*b[1], wa*a[2]+wb*b[2]]
}

/* ── Network data ────────────────────────────────────────────────────────── */
const NODE_COORDS = [
  [ 40.7, -74.0], // 0  New York
  [ 51.5,  -0.1], // 1  London
  [ 48.9,   2.3], // 2  Paris
  [ 52.5,  13.4], // 3  Berlin
  [ 55.8,  37.6], // 4  Moscow
  [ 25.2,  55.3], // 5  Dubai
  [ 28.6,  77.2], // 6  Delhi
  [ 22.3, 114.2], // 7  Hong Kong
  [ 35.7, 139.7], // 8  Tokyo
  [  1.3, 103.8], // 9  Singapore
  [-33.9,  18.4], // 10 Cape Town
  [-33.9, 151.2], // 11 Sydney
  [ 37.8,-122.4], // 12 San Francisco
  [ 34.1,-118.2], // 13 Los Angeles
  [ 19.4, -99.1], // 14 Mexico City
  [-23.5, -46.6], // 15 São Paulo
  [  6.5,   3.4], // 16 Lagos
  [ 30.0,  31.2], // 17 Cairo
  [ 43.7, -79.4], // 18 Toronto
  [ 41.0,  28.9], // 19 Istanbul
  [ 59.9,  30.3], // 20 St. Petersburg
  [ 37.6, 127.0], // 21 Seoul
  [  3.1, 101.7], // 22 Kuala Lumpur
  [-34.6, -58.4], // 23 Buenos Aires
]

const EDGE_PAIRS = [
  // Original connections
  [0,1],[0,12],[0,13],[0,18],[0,2],
  [1,2],[1,3],[1,17],[1,19],[1,20],
  [2,3],[3,4],[3,19],
  [4,5],[4,20],[4,17],
  [5,6],[5,17],[5,19],
  [6,7],[6,9],
  [7,8],[7,9],[7,21],
  [8,11],[8,21],
  [9,11],[9,22],
  [10,16],[10,17],
  [11,22],
  [12,13],[12,18],
  [13,14],
  [14,15],[14,23],
  [15,23],
  [16,17],
  [19,20],
  [1,4],[0,15],
  // Additional connections
  [0,3],[0,4],[0,17],[0,19],
  [1,5],[1,6],[1,7],[1,10],[1,16],
  [2,5],[2,17],[2,19],[2,20],
  [3,5],[3,20],[3,17],
  [4,6],[4,19],[4,21],
  [5,7],[5,9],[5,22],
  [6,8],[6,21],[6,22],
  [7,22],[7,11],
  [8,9],[8,22],
  [9,21],[9,6],
  [10,15],[10,23],[10,1],
  [11,21],[11,9],
  [12,0],[12,15],[12,23],
  [13,15],[13,18],[13,23],
  [14,0],[14,18],
  [15,10],[15,16],
  [16,19],[16,5],
  [17,21],[17,7],
  [18,1],[18,2],
  [19,5],[19,6],
  [20,21],[20,4],
  [21,22],[21,11],
  [22,11],[22,6],
  [23,10],[23,16],
]

const RotatingGlobe = () => {
  const canvasRef = useRef(null)
  const rafRef    = useRef(null)
  const angleRef  = useRef(0)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const dpr = window.devicePixelRatio || 1
    const PI2 = Math.PI * 2

    const resize = () => {
      const { offsetWidth: w, offsetHeight: h } = canvas.parentElement
      canvas.width  = w * dpr
      canvas.height = h * dpr
      canvas.style.width  = w + 'px'
      canvas.style.height = h + 'px'
    }
    resize()

    const ctx = canvas.getContext('2d')

    /* ── Sphere dot grid ───────────────────────────────────────────────── */
    const N      = 5500
    const golden = (1 + Math.sqrt(5)) / 2
    const BX = new Float32Array(N)
    const BY = new Float32Array(N)
    const BZ = new Float32Array(N)
    for (let i = 0; i < N; i++) {
      const theta = Math.acos(1 - 2 * (i + 0.5) / N)
      const phi   = 2 * Math.PI * i / golden
      BX[i] = Math.sin(theta) * Math.cos(phi)
      BY[i] = Math.cos(theta)
      BZ[i] = Math.sin(theta) * Math.sin(phi)
    }

    /* ── Lighting ──────────────────────────────────────────────────────── */
    const lx = -0.55, ly = 0.50, lz = 0.67
    const lLen = Math.sqrt(lx*lx + ly*ly + lz*lz)

    /* ── Network nodes ─────────────────────────────────────────────────── */
    const APPEAR_GAP = 0.32   // seconds between each node appearing
    const EDGE_DRAW_DUR = 0.9 // seconds to draw each edge

    const nodes = NODE_COORDS.map((c, i) => ({
      vec:        toVec(c[0], c[1]),
      appearAt:   i * APPEAR_GAP,
      phase:      i * 1.17,   // offset for pulsing ring
      // projected each frame:
      px: 0, py: 0, z: 0, front: false, alpha: 0,
    }))

    const edges = EDGE_PAIRS.map(([a, b]) => ({
      a, b,
      formAt:  Math.max(nodes[a].appearAt, nodes[b].appearAt) + 0.1,
      drawProg: 0,
      // pulse state (2 particles per edge, offset by 0.5)
      speed: 0.18 + Math.random() * 0.10,
      phase: Math.random(),
    }))

    const startTime = Date.now()

    /* ── Draw loop ─────────────────────────────────────────────────────── */
    const draw = () => {
      const W = canvas.width
      const H = canvas.height
      ctx.clearRect(0, 0, W, H)

      const elapsed = (Date.now() - startTime) / 1000

      angleRef.current += 0.0016
      const a    = angleRef.current
      const cosA = Math.cos(a)
      const sinA = Math.sin(a)

      const R  = Math.min(W, H) * 0.58
      const GX = W * 0.62
      const GY = H * 0.84

      /* Project helper */
      const proj = (vec) => {
        const x =  vec[0] * cosA + vec[2] * sinA
        const y =  vec[1]
        const z = -vec[0] * sinA + vec[2] * cosA
        return { x, y, z, px: GX + x*R, py: GY - y*R, front: z > 0 }
      }

      /* ── 1. Sphere dots (dimmed — network is the focus) ─────────────── */
      for (let i = 0; i < N; i++) {
        const x =  BX[i] * cosA + BZ[i] * sinA
        const y =  BY[i]
        const z = -BX[i] * sinA + BZ[i] * cosA

        if (z < 0.02) continue
        const px = GX + x*R, py = GY - y*R
        if (px < -R*0.15 || px > W+R*0.15 || py < -R*0.15 || py > H+R*0.15) continue

        const light = Math.max(0, (x*lx + y*ly + z*lz) / lLen)
        const wh    = Math.pow(light, 2.2) * 0.9
        const rr    = Math.round(wh * 255)
        const gg    = Math.round(((1-wh)*180 + wh*255) * (0.08 + light*0.92))
        const bb    = Math.round(((1-wh)*216 + wh*255) * (0.08 + light*0.92))
        const aa    = Math.min(1, 0.10 + light*0.55)   // dimmer than before

        const dotR = Math.max(0.35*dpr, (0.45 + z*0.7)*dpr)
        ctx.beginPath()
        ctx.arc(px, py, dotR, 0, PI2)
        ctx.fillStyle = `rgba(${rr},${gg},${bb},${aa})`
        ctx.fill()
      }

      /* ── 2. Update node alphas & projected positions ─────────────────── */
      for (const n of nodes) {
        n.alpha = Math.min(1, Math.max(0, (elapsed - n.appearAt) / 0.45))
        const p = proj(n.vec)
        n.px = p.px; n.py = p.py; n.z = p.z; n.front = p.front
      }

      /* ── 3. Edges — draw great-circle arcs progressively ────────────── */
      ctx.lineCap = 'round'

      for (const e of edges) {
        const nA = nodes[e.a], nB = nodes[e.b]
        const edgeAlpha = Math.min(nA.alpha, nB.alpha)
        if (edgeAlpha <= 0) continue

        e.drawProg = Math.min(1, Math.max(0, (elapsed - e.formAt) / EDGE_DRAW_DUR))
        if (e.drawProg <= 0) continue

        /* Walk the great circle from 0 → drawProg */
        const ESTEPS = 36
        ctx.beginPath()
        let started = false

        for (let s = 0; s <= ESTEPS; s++) {
          const t = (s / ESTEPS) * e.drawProg
          const [bx, by, bz] = slerp(nA.vec, nB.vec, t)
          const x =  bx * cosA + bz * sinA
          const y =  by
          const z = -bx * sinA + bz * cosA

          if (z <= 0) { started = false; continue }
          const px = GX + x*R, py = GY - y*R

          if (!started) { ctx.moveTo(px, py); started = true }
          else ctx.lineTo(px, py)
        }

        ctx.strokeStyle = `rgba(0,180,216,${edgeAlpha * 0.42})`
        ctx.lineWidth   = 0.75 * dpr
        ctx.stroke()
      }

      /* ── 4. Pulse particles along completed edges ────────────────────── */
      for (const e of edges) {
        if (e.drawProg < 1) continue
        const nA = nodes[e.a], nB = nodes[e.b]
        const edgeAlpha = Math.min(nA.alpha, nB.alpha)
        if (edgeAlpha <= 0) continue

        for (let p = 0; p < 2; p++) {
          const t = ((elapsed * e.speed + e.phase + p * 0.5) % 1)

          const [bx, by, bz] = slerp(nA.vec, nB.vec, t)
          const x =  bx * cosA + bz * sinA
          const y =  by
          const z = -bx * sinA + bz * cosA
          if (z <= 0) continue

          const px = GX + x*R, py = GY - y*R

          /* Glow halo */
          const g = ctx.createRadialGradient(px, py, 0, px, py, 5*dpr)
          g.addColorStop(0,   `rgba(0,220,255,${edgeAlpha * 0.75})`)
          g.addColorStop(1,   'rgba(0,180,216,0)')
          ctx.beginPath()
          ctx.arc(px, py, 5*dpr, 0, PI2)
          ctx.fillStyle = g
          ctx.fill()

          /* White core */
          ctx.beginPath()
          ctx.arc(px, py, 1.3*dpr, 0, PI2)
          ctx.fillStyle = `rgba(255,255,255,${edgeAlpha * 0.92})`
          ctx.fill()
        }
      }

      /* ── 5. Nodes ────────────────────────────────────────────────────── */
      for (const n of nodes) {
        if (n.alpha <= 0 || !n.front) continue
        const { px, py } = n

        /* Pulsing glow ring */
        const pulse = 0.5 + 0.5 * Math.sin(elapsed * 2.2 + n.phase)
        const glowR = (4 + pulse * 3) * dpr
        const grd = ctx.createRadialGradient(px, py, 0, px, py, glowR)
        grd.addColorStop(0, `rgba(0,200,255,${n.alpha * (0.45 + pulse * 0.25)})`)
        grd.addColorStop(1, 'rgba(0,180,216,0)')
        ctx.beginPath()
        ctx.arc(px, py, glowR, 0, PI2)
        ctx.fillStyle = grd
        ctx.fill()

        /* Outer ring */
        ctx.beginPath()
        ctx.arc(px, py, 3.2*dpr, 0, PI2)
        ctx.strokeStyle = `rgba(0,210,255,${n.alpha * 0.55})`
        ctx.lineWidth   = 0.7 * dpr
        ctx.stroke()

        /* Bright core dot */
        ctx.beginPath()
        ctx.arc(px, py, 1.8*dpr, 0, PI2)
        ctx.fillStyle = `rgba(255,255,255,${n.alpha * 0.95})`
        ctx.fill()
      }

      /* ── 6. Rim-light glow ───────────────────────────────────────────── */
      const rimX = GX - R * 0.40
      const rimY = GY - R * 0.38
      const rim  = ctx.createRadialGradient(rimX, rimY, R*0.01, rimX, rimY, R*0.62)
      rim.addColorStop(0,    'rgba(255,255,255,0.20)')
      rim.addColorStop(0.28, 'rgba(180,230,255,0.08)')
      rim.addColorStop(1,    'rgba(0,0,0,0)')
      ctx.fillStyle = rim
      ctx.fillRect(0, 0, W, H)

      rafRef.current = requestAnimationFrame(draw)
    }

    draw()
    return () => cancelAnimationFrame(rafRef.current)
  }, [])

  return <canvas ref={canvasRef} style={{ position: 'absolute', inset: 0 }} />
}

/* ═══════════════════════════════════════════════════════════════════════════
   Suggested Professionals data
   ═══════════════════════════════════════════════════════════════════════════ */
const SUGGESTED_PROFESSIONALS = [
  { name: 'Emily Zhang',   role: 'ML Engineer',      mutual: 14 },
  { name: 'Raj Malhotra',  role: 'Product Manager',  mutual: 9  },
  { name: 'Sophie Laurent',role: 'Data Analyst',     mutual: 7  },
]

const getInitials = (name) => {
  const p = name.split(' ')
  return p.length >= 2 ? p[0][0] + p[1][0] : p[0][0]
}

/* ═══════════════════════════════════════════════════════════════════════════
   Component
   ═══════════════════════════════════════════════════════════════════════════ */
const NetworkExpansionGraph = () => {
  const sectionRef = useRef(null)

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

        {/* Unified card */}
        <div className="network-unified-card">

          {/* Left — suggested professionals */}
          <div className="network-unified-left">
            <h3 className="insights-card-title">Suggested Professionals</h3>
            <div className="suggested-list">
              {SUGGESTED_PROFESSIONALS.map((prof, i) => (
                <motion.div
                  className="suggested-card"
                  key={prof.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + i * 0.15 }}
                  whileHover={{ y: -3, boxShadow: '0 8px 24px rgba(0,180,216,0.15)' }}
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

          {/* Right — rotating globe */}
          <div className="network-unified-right">
            <RotatingGlobe />
            <div className="globe-text-overlay">
              <span className="globe-text-eyebrow">Live Network</span>
              <h3 className="globe-text-heading">Your connections,<br />mapped globally.</h3>
              <p className="globe-text-sub">
                24 cities · 6 continents · real-time
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  )
}

export default NetworkExpansionGraph
