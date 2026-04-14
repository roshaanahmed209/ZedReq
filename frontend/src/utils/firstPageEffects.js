/**
 * firstPageEffects.js
 * All imperative DOM effects for the ZedReq FirstPage React component.
 * Called from a useEffect on mount; returns a cleanup function.
 */

const prefersReduced = () =>
  typeof window !== 'undefined' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

export function attachFirstPageEffects(root) {
  if (!root || typeof window === 'undefined') return () => {};

  const cleanups = [];

  /* ─── Scroll progress bar ─────────────────────────────── */
  const progressEl = document.querySelector('.scroll-progress');
  if (progressEl) {
    const onProgress = () => {
      const pct =
        (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
      progressEl.style.width = `${pct}%`;
    };
    window.addEventListener('scroll', onProgress, { passive: true });
    cleanups.push(() => window.removeEventListener('scroll', onProgress));
  }

  /* ─── Nav background on scroll ────────────────────────── */
  const nav = root.querySelector('.nav');
  if (nav) {
    const onNavScroll = () => {
      nav.classList.toggle('nav--scrolled', window.scrollY > 60);
    };
    window.addEventListener('scroll', onNavScroll, { passive: true });
    onNavScroll(); // run once on mount
    cleanups.push(() => window.removeEventListener('scroll', onNavScroll));
  }

  /* ─── Smooth anchor scrolling ─────────────────────────── */
  root.querySelectorAll('a[href^="#"]').forEach((a) => {
    const onClick = (e) => {
      const id = a.getAttribute('href').slice(1);
      const target = document.getElementById(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    };
    a.addEventListener('click', onClick);
    cleanups.push(() => a.removeEventListener('click', onClick));
  });

  /* ─── Generic scroll reveal ───────────────────────────── */
  const revealEls = root.querySelectorAll('.reveal, .reveal-left, .reveal-right, .section-rule');
  if (revealEls.length) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    revealEls.forEach((el) => io.observe(el));
    cleanups.push(() => io.disconnect());
  }

  /* ─── Chapter image Ken Burns trigger ─────────────────── */
  const chapterImgs = root.querySelectorAll('.chapter__img-wrap');
  if (chapterImgs.length) {
    const imgObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            imgObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1 }
    );
    chapterImgs.forEach((el) => imgObserver.observe(el));
    cleanups.push(() => imgObserver.disconnect());
  }

  /* ─── Score / progress bars ───────────────────────────── */
  const bars = root.querySelectorAll('.chapter__score-fill, .chapter__bar-fill');
  if (bars.length) {
    const barObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const el = entry.target;
            const target = el.dataset.target || '80%';
            // small delay to let the section paint first
            setTimeout(() => {
              el.style.width = target;
            }, 200);
            barObserver.unobserve(el);
          }
        });
      },
      { threshold: 0.3 }
    );
    bars.forEach((el) => barObserver.observe(el));
    cleanups.push(() => barObserver.disconnect());
  }

  /* ─── Stats counter animation ─────────────────────────── */
  const statVals = root.querySelectorAll('.stat-item__val[data-target]');
  if (statVals.length) {
    const statObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const el = entry.target;
          const rawTarget = el.dataset.target || '0';
          const numTarget = parseFloat(rawTarget.replace(/[^0-9.]/g, ''));
          const suffix = rawTarget.replace(/[0-9.]/g, '');
          const duration = 1800;
          const start = performance.now();
          const isFloat = rawTarget.includes('.');
          const decimals = isFloat ? (rawTarget.split('.')[1] || '').length : 0;

          const tick = (now) => {
            const elapsed = Math.min(now - start, duration);
            const progress = 1 - Math.pow(1 - elapsed / duration, 4); // ease-out-quartic
            const val = numTarget * progress;
            el.textContent = isFloat ? val.toFixed(decimals) + suffix : Math.floor(val) + suffix;
            if (elapsed < duration) requestAnimationFrame(tick);
            else el.textContent = rawTarget; // snap to exact
          };
          requestAnimationFrame(tick);
          statObserver.unobserve(el);
        });
      },
      { threshold: 0.4 }
    );
    statVals.forEach((el) => statObserver.observe(el));
    cleanups.push(() => statObserver.disconnect());
  }

  /* ─── Hero stage tilt (mouse parallax) ────────────────── */
  const heroStage = root.querySelector('.hero');
  if (heroStage && !prefersReduced()) {
    const onMove = (e) => {
      const { clientX, clientY } = e;
      const { innerWidth, innerHeight } = window;
      const dx = (clientX / innerWidth - 0.5) * 8;
      const dy = (clientY / innerHeight - 0.5) * 4;
      const orbits = heroStage.querySelector('.hero__orbits');
      if (orbits) {
        orbits.style.transform = `translate(${dx * 0.8}px, ${dy * 0.8}px)`;
      }
    };
    heroStage.addEventListener('mousemove', onMove, { passive: true });
    cleanups.push(() => heroStage.removeEventListener('mousemove', onMove));
  }

  /* ─── Feature card stagger fade-in ───────────────────── */
  const featCards = root.querySelectorAll('.feat-card');
  if (featCards.length) {
    featCards.forEach((card, i) => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(1.5rem)';
      card.style.transition = `opacity 0.7s ease ${i * 0.07}s, transform 0.7s ease ${i * 0.07}s`;
    });
    const featObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'none';
            featObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1 }
    );
    featCards.forEach((el) => featObserver.observe(el));
    cleanups.push(() => featObserver.disconnect());
  }

  /* ─── Trust item stagger ─────────────────────────────── */
  const trustItems = root.querySelectorAll('.trust-item');
  if (trustItems.length) {
    trustItems.forEach((item, i) => {
      item.style.opacity = '0';
      item.style.transform = 'translateY(2rem)';
      item.style.transition = `opacity 0.8s ease ${i * 0.1}s, transform 0.8s ease ${i * 0.1}s`;
    });
    const trustObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'none';
            trustObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08 }
    );
    trustItems.forEach((el) => trustObserver.observe(el));
    cleanups.push(() => trustObserver.disconnect());
  }

  /* ─── Escape to close (handled in component but also here) */
  const onKeydown = (e) => {
    if (e.key === 'Escape') {
      const overlay = root.querySelector('.nav-overlay.open');
      if (overlay) overlay.classList.remove('open');
    }
  };
  window.addEventListener('keydown', onKeydown);
  cleanups.push(() => window.removeEventListener('keydown', onKeydown));

  /* ─── Hamburger burger bar animation on menu open ─────── */
  const burger = root.querySelector('.nav__burger');
  const navOverlay = root.querySelector('.nav-overlay');
  if (burger && navOverlay) {
    const bars = burger.querySelectorAll('span');
    const updateBurger = () => {
      const isOpen = navOverlay.classList.contains('open');
      if (bars[0]) bars[0].style.transform = isOpen ? 'translateY(6px) rotate(45deg)' : '';
      if (bars[1]) bars[1].style.opacity  = isOpen ? '0' : '1';
      if (bars[2]) bars[2].style.transform = isOpen ? 'translateY(-6px) rotate(-45deg)' : '';
    };
    const mo = new MutationObserver(updateBurger);
    mo.observe(navOverlay, { attributes: true, attributeFilter: ['class'] });
    cleanups.push(() => mo.disconnect());
  }

  return () => {
    cleanups.forEach((fn) => fn());
  };
}
