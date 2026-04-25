import { useRef, useLayoutEffect, useEffect, useState } from 'react';
import { useInView } from 'framer-motion';
import CareerAssistantCards, { CAREER_ASSISTANT_COUNTS } from './CareerAssistantCards';

const GLOW = 'none';
const EASE = [0.22, 1, 0.36, 1];
const DUR = 0.62;
const GAP = 0.12;

const CareerAssistant = () => {
  const rootRef = useRef(null);
  const aiRef = useRef(null);
  const isInView = useInView(rootRef, { once: true, amount: 0.2 });
  const [overlapPx, setOverlapPx] = useState(0);
  const [glowOn, setGlowOn] = useState(false);
  const [isWide, setIsWide] = useState(false);

  useLayoutEffect(() => {
    const mq = window.matchMedia('(min-width: 1024px)');
    const onMq = () => setIsWide(mq.matches);
    onMq();
    mq.addEventListener('change', onMq);
    return () => mq.removeEventListener('change', onMq);
  }, []);

  useLayoutEffect(() => {
    const el = aiRef.current;
    if (!el) return;
    const update = () => {
      const w = el.getBoundingClientRect().width;
      if (w > 0) setOverlapPx(Math.round(w * 0.1));
    };
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, [isInView, isWide]);

  const t0 = 0.1;
  const tAi = t0;
  const tMsg0 = tAi + 0.28;
  const tAfterBubbles = tMsg0 + (CAREER_ASSISTANT_COUNTS.messages - 1) * GAP + 0.46;
  const tInput = tAfterBubbles + 0.16;
  const tProfileShell = tInput + 0.24;
  const tProfileBlocks = tProfileShell + DUR + 0.08;
  const tGlow = tProfileBlocks + 0.4 * (CAREER_ASSISTANT_COUNTS.profiles - 1) + 0.55;

  useEffect(() => {
    if (!isInView) return;
    const id = window.setTimeout(() => setGlowOn(true), tGlow * 1000);
    return () => window.clearTimeout(id);
  }, [isInView, tGlow]);

  const profilesSurface =
    isWide && overlapPx > 0
      ? { marginLeft: -overlapPx }
      : undefined;

  return (
    <div
      ref={rootRef}
      className="w-full min-h-[420px] bg-transparent py-4 px-3 sm:py-6 sm:px-5 font-sans text-left relative flex flex-col items-stretch overflow-visible"
    >
      <div className="w-full max-w-6xl mx-auto flex flex-col grow min-h-0 relative z-[1]">
        <div className="relative isolate w-full min-h-0 grow flex flex-col">
          <div
            className="pointer-events-none absolute left-1/2 top-1/2 w-[90%] max-w-4xl h-[min(80%,22rem)] -translate-x-1/2 -translate-y-1/2 rounded-[2.5rem] transition-[opacity,box-shadow] duration-1000 ease-out"
            style={{
              zIndex: 0,
              opacity: glowOn ? 1 : 0,
              boxShadow: glowOn ? GLOW : '0 0 0 transparent',
            }}
            aria-hidden
          />

          <CareerAssistantCards
            isInView={isInView}
            aiRef={aiRef}
            profilesSurface={profilesSurface}
            EASE={EASE}
            DUR={DUR}
            GAP={GAP}
            tAi={tAi}
            tMsg0={tMsg0}
            tInput={tInput}
            tProfileShell={tProfileShell}
            tProfileBlocks={tProfileBlocks}
          />
        </div>
      </div>
    </div>
  );
};

export default CareerAssistant;
