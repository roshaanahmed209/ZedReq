import {
  useMotionValueEvent,
  useScroll,
  useTransform,
  motion,
} from "framer-motion";
import React, { useEffect, useRef, useState } from "react";
import "./Timeline.css";

/**
 * @param {{
 *   data: { title: string, content: React.ReactNode, stickyLabel?: string }[],
 *   className?: string,
 * }} props
 */
export const Timeline = ({ data, className = '' }) => {
  const ref = useRef(null);
  const containerRef = useRef(null);
  const [height, setHeight] = useState(0);
  const [activeIndex, setActiveIndex] = useState(null);
  const entryRefs = useRef([]);

  useEffect(() => {
    const el = ref.current;
    if (!el) return undefined;

    const measure = () => setHeight(el.getBoundingClientRect().height);
    measure();

    const ro = new ResizeObserver(measure);
    ro.observe(el);
    return () => ro.disconnect();
  }, [data.length]);

  useEffect(() => {
    const observers = [];
    const visibleRatios = new Array(data.length).fill(0);

    entryRefs.current.forEach((el, i) => {
      if (!el) return;
      const obs = new IntersectionObserver(
        ([entry]) => {
          visibleRatios[i] = entry.intersectionRatio;
          const best = visibleRatios.indexOf(Math.max(...visibleRatios));
          setActiveIndex(visibleRatios[best] > 0 ? best : null);
        },
        { threshold: Array.from({ length: 21 }, (_, k) => k / 20) }
      );
      obs.observe(el);
      observers.push(obs);
    });

    return () => observers.forEach((obs) => obs.disconnect());
  }, [data.length]);

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start 10%", "end 50%"],
  });

  const heightTransform = useTransform(scrollYProgress, [0, 1], [0, height]);
  const opacityTransform = useTransform(scrollYProgress, [0, 0.1], [0, 1]);

  const stickyClass = (index, base) =>
    `${base}${activeIndex === index ? ` ${base}--active` : ''}`;

  return (
    <div className={`timeline-wrapper${className ? ` ${className}` : ''}`} ref={containerRef}>
      <div ref={ref} className="timeline-entries">
        {data.map((item, index) => (
          <div
            key={item.stickyLabel ?? item.title ?? index}
            className="timeline-entry"
            ref={(el) => { entryRefs.current[index] = el; }}
          >
            <div className="timeline-entry-left">
              <div className="timeline-dot-wrapper">
                <div className="timeline-dot" />
              </div>
              {item.stickyLabel != null ? (
                <span className={stickyClass(index, 'timeline-entry-num timeline-entry-num-desktop')}>
                  {item.stickyLabel}
                </span>
              ) : (
                <h3 className={stickyClass(index, 'timeline-entry-title timeline-entry-title-desktop')}>
                  {item.title}
                </h3>
              )}
            </div>

            <div className="timeline-entry-right">
              {item.stickyLabel != null ? (
                <span className={stickyClass(index, 'timeline-entry-num timeline-entry-num-mobile')}>
                  {item.stickyLabel}
                </span>
              ) : (
                <h3 className={stickyClass(index, 'timeline-entry-title timeline-entry-title-mobile')}>
                  {item.title}
                </h3>
              )}
              {item.content}
            </div>
          </div>
        ))}

        {/* The track line */}
        <div
          style={{ height: height + "px" }}
          className="timeline-track"
        >
          <motion.div
            style={{
              height: heightTransform,
              opacity: opacityTransform,
            }}
            className="timeline-track-progress"
          />
        </div>
      </div>
    </div>
  );
};

export default Timeline;
