import {
  useMotionValueEvent,
  useScroll,
  useTransform,
  motion,
} from "framer-motion";
import React, { useEffect, useRef, useState } from "react";
import "./Timeline.css";

/**
 * @param {{ data: { title: string, content: React.ReactNode }[] }} props
 */
export const Timeline = ({ data }) => {
  const ref = useRef(null);
  const containerRef = useRef(null);
  const [height, setHeight] = useState(0);
  const [activeIndex, setActiveIndex] = useState(null);
  const entryRefs = useRef([]);

  useEffect(() => {
    if (ref.current) {
      const rect = ref.current.getBoundingClientRect();
      setHeight(rect.height);
    }
  }, [ref]);

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

  return (
    <div className="timeline-wrapper" ref={containerRef}>
      <div ref={ref} className="timeline-entries">
        {data.map((item, index) => (
          <div
            key={index}
            className="timeline-entry"
            ref={(el) => { entryRefs.current[index] = el; }}
          >
            <div className="timeline-entry-left">
              <div className="timeline-dot-wrapper">
                <div className="timeline-dot" />
              </div>
              <h3 className={`timeline-entry-title timeline-entry-title-desktop${activeIndex === index ? ' timeline-entry-title--active' : ''}`}>
                {item.title}
              </h3>
            </div>

            <div className="timeline-entry-right">
              <h3 className={`timeline-entry-title timeline-entry-title-mobile${activeIndex === index ? ' timeline-entry-title--active' : ''}`}>
                {item.title}
              </h3>
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
