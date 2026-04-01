import { useRef, useState } from 'react';
import { motion, useMotionValue, useSpring, useMotionTemplate } from 'framer-motion';
import './TiltedCard.css';

const springValues = { damping: 30, stiffness: 100, mass: 2 };

export default function TiltedCard({
  imageSrc,
  altText = 'Tilted card image',
  captionText = '',
  containerHeight = '300px',
  containerWidth = '100%',
  imageHeight = '300px',
  imageWidth = '300px',
  scaleOnHover = 1.1,
  rotateAmplitude = 14,
  spotlightRadius = 140,
  showMobileWarning = true,
  showTooltip = true,
  overlayContent = null,
  displayOverlayContent = false,
}) {
  const ref = useRef(null);
  const [hovered, setHovered] = useState(false);

  /* tilt */
  const rotateX = useSpring(useMotionValue(0), springValues);
  const rotateY = useSpring(useMotionValue(0), springValues);
  const scale   = useSpring(1, springValues);

  /* caption */
  const capX = useMotionValue(0);
  const capY = useMotionValue(0);
  const capOpacity = useSpring(0);
  const rotateFigcaption = useSpring(0, { stiffness: 350, damping: 30, mass: 1 });

  /* spotlight mask */
  const maskX = useMotionValue(50);
  const maskY = useMotionValue(50);
  const maskStyle = useMotionTemplate`radial-gradient(circle ${spotlightRadius}px at ${maskX}% ${maskY}%, black 10%, transparent 85%)`;

  const [lastY, setLastY] = useState(0);

  function handleMouse(e) {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();

    const offsetX = e.clientX - rect.left - rect.width  / 2;
    const offsetY = e.clientY - rect.top  - rect.height / 2;

    rotateX.set((offsetY / (rect.height / 2)) * -rotateAmplitude);
    rotateY.set((offsetX / (rect.width  / 2)) *  rotateAmplitude);

    capX.set(e.clientX - rect.left);
    capY.set(e.clientY - rect.top);

    rotateFigcaption.set(-(offsetY - lastY) * 0.6);
    setLastY(offsetY);

    /* spotlight position as % of image */
    maskX.set(((e.clientX - rect.left) / rect.width)  * 100);
    maskY.set(((e.clientY - rect.top)  / rect.height) * 100);
  }

  function handleMouseEnter() {
    setHovered(true);
    scale.set(scaleOnHover);
    capOpacity.set(1);
  }

  function handleMouseLeave() {
    setHovered(false);
    scale.set(1);
    rotateX.set(0);
    rotateY.set(0);
    rotateFigcaption.set(0);
    capOpacity.set(0);
  }

  const imgStyle = { width: imageWidth, height: imageHeight };

  return (
    <figure
      ref={ref}
      className="tilted-card-figure"
      style={{ height: containerHeight, width: containerWidth }}
      onMouseMove={handleMouse}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {showMobileWarning && (
        <div className="tilted-card-mobile-alert">
          This effect is not optimised for mobile. Check on desktop.
        </div>
      )}

      <motion.div
        className="tilted-card-inner"
        style={{ width: imageWidth, height: imageHeight, rotateX, rotateY, scale }}
      >
        {/* Layer 1 — grayscale base (always visible) */}
        <motion.img
          src={imageSrc}
          alt={altText}
          className="tilted-card-img tilted-card-img-gray"
          style={imgStyle}
        />

        {/* Layer 2 — full-colour, revealed only where the cursor is */}
        <motion.img
          src={imageSrc}
          alt=""
          aria-hidden="true"
          className="tilted-card-img tilted-card-img-color"
          style={{
            ...imgStyle,
            WebkitMaskImage: maskStyle,
            maskImage: maskStyle,
            opacity: hovered ? 1 : 0,
            transition: 'opacity 0.2s ease',
          }}
        />

        {displayOverlayContent && overlayContent && (
          <motion.div className="tilted-card-overlay">{overlayContent}</motion.div>
        )}
      </motion.div>

      {showTooltip && (
        <motion.figcaption
          className="tilted-card-caption"
          style={{ x: capX, y: capY, opacity: capOpacity, rotate: rotateFigcaption }}
        >
          {captionText}
        </motion.figcaption>
      )}
    </figure>
  );
}
