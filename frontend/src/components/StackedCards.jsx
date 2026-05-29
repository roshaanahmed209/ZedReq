import { useRef } from 'react';
import { motion, useReducedMotion, useScroll, useTransform } from 'framer-motion';
import '../css/components/StackedCards.css';

function StickyTrustCard({ item, index, total, progress }) {
  const step = 1 / Math.max(total - 1, 1);
  const rangeStart = index * step;
  const targetScale = Math.max(0.82, 1 - (total - index - 1) * 0.04);
  const scale = useTransform(progress, [rangeStart, 1], [1, targetScale]);
  const topOffset = index * 16 + 72;

  return (
    <div className="stacked-cards__sticky-slot">
      <motion.article
        className="stacked-cards__card"
        style={{
          scale,
          top: `calc(-4vh + ${topOffset}px)`,
          zIndex: index + 1,
        }}
      >
        <div className="stacked-cards__num">{item.num}</div>
        <h3 className="stacked-cards__title">{item.title}</h3>
        <p className="stacked-cards__desc">{item.desc}</p>
      </motion.article>
    </div>
  );
}

export default function StackedCards({ items }) {
  const containerRef = useRef(null);
  const reduceMotion = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ['start start', 'end end'],
  });

  if (reduceMotion) {
    return (
      <div className="stacked-cards stacked-cards--static">
        {items.map((item) => (
          <article key={item.num} className="stacked-cards__card stacked-cards__card--static">
            <div className="stacked-cards__num">{item.num}</div>
            <h3 className="stacked-cards__title">{item.title}</h3>
            <p className="stacked-cards__desc">{item.desc}</p>
          </article>
        ))}
      </div>
    );
  }

  return (
    <div
      className="stacked-cards"
      ref={containerRef}
      aria-label="Privacy and security highlights"
    >
      <div className="stacked-cards__scroll-room">
        {items.map((item, index) => (
          <StickyTrustCard
            key={item.num}
            item={item}
            index={index}
            total={items.length}
            progress={scrollYProgress}
          />
        ))}
      </div>
    </div>
  );
}
