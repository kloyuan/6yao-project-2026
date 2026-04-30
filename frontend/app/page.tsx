'use client'

import { useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'

export default function HomePage() {
  const canvasRef    = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const exitingRef   = useRef(false)          // guard: prevent double-trigger
  const router       = useRouter()

  // Shared exit: add CSS animation class, then navigate
  function triggerExit() {
    if (exitingRef.current) return
    exitingRef.current = true
    containerRef.current?.classList.add('hero-exiting')
    setTimeout(() => router.push('/question'), 500)
  }

  useEffect(() => {
    const canvas    = canvasRef.current
    const container = containerRef.current
    if (!canvas || !container) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // ── canvas resize ──────────────────────────────────
    function resize() {
      canvas!.width  = window.innerWidth
      canvas!.height = window.innerHeight
    }
    window.addEventListener('resize', resize)
    resize()

    // ── particle mist ──────────────────────────────────
    const w = canvas
    const c = ctx

    class Particle {
      x: number; y: number; size: number
      speedX: number; speedY: number; opacity: number

      constructor() {
        this.x       = Math.random() * w.width
        this.y       = Math.random() * w.height
        this.size    = Math.random() * 150 + 50
        this.speedX  = Math.random() * 0.5 - 0.25
        this.speedY  = Math.random() * 0.2 - 0.1
        this.opacity = Math.random() * 0.15
      }

      update() {
        this.x += this.speedX
        this.y += this.speedY
        if (this.x > w.width  + 100) this.x = -100
        if (this.x < -100)           this.x = w.width + 100
        if (this.y > w.height + 100) this.y = -100
        if (this.y < -100)           this.y = w.height + 100
      }

      draw() {
        const g = c.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.size)
        g.addColorStop(0, `rgba(255,255,255,${this.opacity})`)
        g.addColorStop(1, 'rgba(255,255,255,0)')
        c.beginPath()
        c.fillStyle = g
        c.arc(this.x, this.y, this.size, 0, Math.PI * 2)
        c.fill()
      }
    }

    const particles: Particle[] = []
    for (let i = 0; i < 30; i++) particles.push(new Particle())

    let animId: number
    function animate() {
      c.clearRect(0, 0, w.width, w.height)
      particles.forEach(p => { p.update(); p.draw() })
      animId = requestAnimationFrame(animate)
    }
    animate()

    // ── parallax element refs (live in bg layer, outside containerRef) ──
    const m1 = document.querySelector<HTMLElement>('.hero-mountain-1')
    const m2 = document.querySelector<HTMLElement>('.hero-mountain-2')
    const m3 = document.querySelector<HTMLElement>('.hero-mountain-3')
    const o1 = document.querySelector<HTMLElement>('.hero-orb-1')

    // ── mouse parallax (desktop) ───────────────────────
    function onMouseMove(e: MouseEvent) {
      const x = (window.innerWidth  / 2 - e.pageX) / 50
      const y = (window.innerHeight / 2 - e.pageY) / 50
      if (m1) m1.style.transform = `translateX(${x * 1.5}px) translateY(${y * 0.5}px)`
      if (m2) m2.style.transform = `translateX(${x * 2.5}px) translateY(${y * 1}px)`
      if (m3) m3.style.transform = `translateX(${x * 0.8}px) translateY(${y * 0.2}px)`
      if (o1) o1.style.transform  = `translateX(${-x * 3}px) translateY(${-y * 2}px)`
    }
    document.addEventListener('mousemove', onMouseMove)

    // ── mouse wheel (any direction) → exit (desktop) ─────
    function onWheel(e: WheelEvent) {
      if (e.deltaY !== 0) triggerExit()
    }
    window.addEventListener('wheel', onWheel, { passive: true })

    // ── touch parallax (mobile) ────────────────────────
    function onTouchMove(e: TouchEvent) {
      const t = e.touches[0]
      const x = (window.innerWidth  / 2 - t.pageX) / 30
      const y = (window.innerHeight / 2 - t.pageY) / 30
      if (m2) m2.style.transform = `translate(${x}px, ${y}px)`
    }
    window.addEventListener('touchmove', onTouchMove, { passive: true })

    // ── swipe up → exit (mobile) ───────────────────────
    let touchStartY = 0
    function onTouchStart(e: TouchEvent) {
      touchStartY = e.touches[0].clientY
    }
    function onTouchEnd(e: TouchEvent) {
      if (touchStartY - e.changedTouches[0].clientY > 50) triggerExit()
    }
    window.addEventListener('touchstart', onTouchStart, { passive: true })
    window.addEventListener('touchend',   onTouchEnd)

    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener('resize', resize)
      document.removeEventListener('mousemove', onMouseMove)
      window.removeEventListener('wheel',       onWheel)
      window.removeEventListener('touchmove',   onTouchMove)
      window.removeEventListener('touchstart',  onTouchStart)
      window.removeEventListener('touchend',    onTouchEnd)
    }
  }, [router])  // eslint-disable-line react-hooks/exhaustive-deps

  return (
    /* Static parchment shell — stays fixed, never animates */
    <div className="hero-page">

      {/* ── Background layer: mountains + mist — pinned, never moves ── */}
      <div className="hero-ink-world">
        <div className="hero-orb hero-orb-1" />
        <div className="hero-orb hero-orb-2" />

        <svg className="hero-mountain hero-mountain-1" viewBox="0 0 1000 400" preserveAspectRatio="none">
          <path d="M0,400 Q150,100 300,250 T600,100 T1000,350 L1000,400 L0,400 Z" />
        </svg>
        <svg className="hero-mountain hero-mountain-2" viewBox="0 0 1000 400" preserveAspectRatio="none">
          <path d="M0,400 Q200,150 400,300 T800,50 T1000,400 L0,400 Z" />
        </svg>
        <svg className="hero-mountain hero-mountain-3" viewBox="0 0 1000 400" preserveAspectRatio="none">
          <path d="M0,400 Q250,50 500,200 T1000,100 L1000,400 L0,400 Z" />
        </svg>

        <canvas ref={canvasRef} className="hero-mist-canvas" />
      </div>

      {/* ── Foreground layer: text + logo + CTA — slides up on exit ── */}
      <div className="hero-content" ref={containerRef}>

      {/* ── Corner marks ── */}
      <div className="hero-corner hero-corner-tl" />
      <div className="hero-corner hero-corner-tr" />
      <div className="hero-corner hero-corner-bl" />
      <div className="hero-corner hero-corner-br" />

      {/* ── Stage ── */}
      <main className="hero-stage">
        <div className="hero-metadata">
          <div><p>The Method</p></div>
          <div style={{ textAlign: 'right' }}>
            <p>EN/中文</p>
            <p style={{ marginTop: 4, opacity: 0.6 }}>∞</p>
          </div>
        </div>

        <div className="hero-logo-container">
          <span className="hero-decor-star">
            <svg width="24" height="24" viewBox="0 0 24 24" style={{ display: 'block', margin: '0 auto' }}>
              <circle cx="12" cy="12" r="10" fill="currentColor" />
              <path
                d="M12 5.5 C12.5 9.5 14.5 11.5 18.5 12 C14.5 12.5 12.5 14.5 12 18.5 C11.5 14.5 9.5 12.5 5.5 12 C9.5 11.5 11.5 9.5 12 5.5 Z"
                fill="#F1EFE9"
              />
            </svg>
          </span>
          <h1 className="hero-logo">六爻</h1>
          <p className="hero-logo-sub">
            LIU YAO<br />COIN CASTING
          </p>
        </div>

        {/* Click on the bottom CTA is the desktop fallback */}
        <div className="hero-bottom-action" onClick={triggerExit}>
          <span className="hero-seal">上滑起心动念</span>
          <div className="hero-swipe-line" />
        </div>
      </main>

    </div>
    </div>
  )
}
