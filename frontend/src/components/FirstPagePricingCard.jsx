import FirstPageGlowButton from './FirstPageGlowButton';
import '../css/components/FirstPagePricingCard.css';

const logoSrc = `${import.meta.env.BASE_URL}assets/logo.svg`;

/**
 * 3D-style pricing card for First Page only (static — no hover tilt).
 */
export default function FirstPagePricingCard({
  tier,
  price,
  period,
  description,
  badge,
  featured = false,
  ctaHref = '/login',
  ctaLabel,
  sections = [],
  tags = [],
  className = '',
}) {
  const rootClass = ['fp-pricing-card', featured ? 'fp-pricing-card--featured' : '', className]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={rootClass}>
      <div className="fp-pricing-card__card">
        <div className="fp-pricing-card__logo" aria-hidden>
          <span className="fp-pricing-card__circle fp-pricing-card__circle--1" />
          <span className="fp-pricing-card__circle fp-pricing-card__circle--2" />
          <span className="fp-pricing-card__circle fp-pricing-card__circle--3" />
          <span className="fp-pricing-card__circle fp-pricing-card__circle--4" />
          <span className="fp-pricing-card__circle fp-pricing-card__circle--5">
            <img src={logoSrc} alt="" className="fp-pricing-card__logo-img" width={20} height={20} />
          </span>
        </div>

        <div className="fp-pricing-card__glass" aria-hidden />

        <div className="fp-pricing-card__content">
          {badge ? <span className="fp-pricing-card__badge">{badge}</span> : null}
          <span className="fp-pricing-card__title">{tier}</span>
          <span className="fp-pricing-card__price">{price}</span>
          {period ? <span className="fp-pricing-card__period">{period}</span> : null}
          {description ? <p className="fp-pricing-card__desc">{description}</p> : null}

          {tags.length > 0 ? (
            <div className="fp-pricing-card__tags">
              {tags.map((tag) => (
                <span key={tag} className="fp-pricing-card__tag">
                  {tag}
                </span>
              ))}
            </div>
          ) : null}

          {sections.map((section) => (
            <div key={section.label} className="fp-pricing-card__section">
              <p className="fp-pricing-card__section-label">{section.label}</p>
              <ul className="fp-pricing-card__features">
                {section.items.map((item) => {
                  const text = typeof item === 'string' ? item : item.text;
                  const emph = typeof item === 'object' && item.emph;
                  return (
                    <li
                      key={text}
                      className={`fp-pricing-card__feature${emph ? ' fp-pricing-card__feature--emph' : ''}`}
                    >
                      {text}
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>

        <div className="fp-pricing-card__bottom">
          <FirstPageGlowButton href={ctaHref} className="fp-glow-btn--pricing">
            {ctaLabel}
          </FirstPageGlowButton>
        </div>
      </div>
    </div>
  );
}
