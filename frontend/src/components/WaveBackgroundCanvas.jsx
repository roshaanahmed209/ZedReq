import React, { useEffect, useRef } from 'react'
import './WaveBackgroundCanvas.css'

/**
 * Lightweight animated wave ribbons. Heavy presets avoided:
 * lower internal resolution, fewer lines, coarser Y step, FPS cap, pause off-screen.
 *
 * @param {{
 *   blurred?: boolean
 *   className?: string
 *   phaseOffset?: number
 * }} props
 * - blurred → "embed" preset (small glass panels)
 * - !blurred → "section" preset (full combined section)
 */
export default function WaveBackgroundCanvas({
  blurred = false,
  className = '',
  phaseOffset = 0,
}) {
  const wrapRef = useRef(null)
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const wrap = wrapRef.current
    if (!canvas || !wrap) return

    const ctx = canvas.getContext('2d', { alpha: false, desynchronized: true })
    if (!ctx) return

    // embed = blurred cards (tiny area, heavy blur — can be very cheap)
    // section = full-bleed behind skill + network blocks
    const preset = blurred
      ? { blue: 12, red: 9, yStep: 10, resScale: 0.28, fps: 18 }
      : { blue: 26, red: 20, yStep: 5, resScale: 0.45, fps: 28 }

    const minFrameMs = 1000 / preset.fps
    let cw = 0
    let ch = 0
    let timer = phaseOffset
    let rafId = 0
    let lastFrameTime = 0
    let visible = true
    let running = false

    class WaveGroup {
      constructor(color, count, offset) {
        this.color = color
        this.count = count
        this.offset = offset
      }

      draw() {
        ctx.save()
        ctx.globalCompositeOperation = 'screen'
        const yStep = preset.yStep
        for (let i = 0; i < this.count; i++) {
          ctx.beginPath()
          ctx.lineWidth = Math.max(0.6, 1.2 / preset.resScale)
          const alpha = 0.1 + Math.sin((i / this.count) * Math.PI) * 0.2
          ctx.strokeStyle = `hsla(${this.color}, 80%, 60%, ${alpha})`

          for (let y = 0; y <= ch; y += yStep) {
            const xMain = Math.sin(y * 0.002 + timer + this.offset) * (cw * 0.15)
            const xSub = Math.sin(y * 0.005 + timer * 0.5 + i * 0.02) * 40
            const xPos = cw / 2 + xMain + xSub
            if (y === 0) ctx.moveTo(xPos, y)
            else ctx.lineTo(xPos, y)
          }
          ctx.stroke()
        }
        ctx.restore()
      }
    }

    const blueRibbon = new WaveGroup(190, preset.blue, 0)
    const redRibbon = new WaveGroup(350, preset.red, 3.5)

    function resize() {
      const w = Math.max(1, Math.floor(wrap.clientWidth))
      const h = Math.max(1, Math.floor(wrap.clientHeight))
      cw = Math.max(1, Math.floor(w * preset.resScale))
      ch = Math.max(1, Math.floor(h * preset.resScale))
      canvas.width = cw
      canvas.height = ch
    }

    function drawStaticFrame() {
      ctx.fillStyle = '#000000'
      ctx.fillRect(0, 0, cw, ch)
      blueRibbon.draw()
      redRibbon.draw()
    }

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)')

    function stopLoop() {
      running = false
      if (rafId) {
        cancelAnimationFrame(rafId)
        rafId = 0
      }
    }

    function tick(now) {
      if (!visible) {
        stopLoop()
        return
      }

      if (now - lastFrameTime < minFrameMs) {
        rafId = requestAnimationFrame(tick)
        return
      }

      const dt = Math.min((now - lastFrameTime) / 1000, 0.05)
      lastFrameTime = now

      ctx.fillStyle = '#000000'
      ctx.fillRect(0, 0, cw, ch)
      blueRibbon.draw()
      redRibbon.draw()

      // Original: +0.005/frame @ ~60fps → ~0.3 radians/sec
      timer += 0.3 * dt

      rafId = requestAnimationFrame(tick)
    }

    function startLoop() {
      if (running || reduceMotion.matches) return
      running = true
      lastFrameTime = performance.now()
      rafId = requestAnimationFrame(tick)
    }

    const ro = new ResizeObserver(() => {
      resize()
      if (reduceMotion.matches) drawStaticFrame()
    })
    ro.observe(wrap)

    const io = new IntersectionObserver(
      ([entry]) => {
        visible = entry?.isIntersecting ?? false
        if (visible) {
          resize()
          if (reduceMotion.matches) {
            drawStaticFrame()
          } else {
            startLoop()
          }
        } else {
          stopLoop()
        }
      },
      { root: null, rootMargin: '120px', threshold: 0 }
    )
    io.observe(wrap)

    resize()

    if (reduceMotion.matches) {
      drawStaticFrame()
    } else {
      startLoop()
    }

    const onReduceChange = () => {
      if (reduceMotion.matches) {
        stopLoop()
        resize()
        drawStaticFrame()
      } else if (visible) {
        startLoop()
      }
    }
    reduceMotion.addEventListener('change', onReduceChange)

    return () => {
      stopLoop()
      ro.disconnect()
      io.disconnect()
      reduceMotion.removeEventListener('change', onReduceChange)
    }
  }, [phaseOffset, blurred])

  return (
    <div
      ref={wrapRef}
      className={`wave-bg-canvas-wrap${blurred ? ' wave-bg-canvas-wrap--blurred' : ''}${className ? ` ${className}` : ''}`}
    >
      <canvas
        ref={canvasRef}
        className="wave-bg-canvas"
        aria-hidden="true"
      />
    </div>
  )
}
