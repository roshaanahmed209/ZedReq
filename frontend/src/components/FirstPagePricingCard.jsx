import { Link } from 'react-router-dom';
import '../css/components/FirstPagePricingCard.css';

const CheckIcon = () => (
  <svg className="check_svg" fill="currentColor" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" aria-hidden>
    <path
      clipRule="evenodd"
      d="M12.416 3.376a.75.75 0 0 1 .208 1.04l-5 7.5a.75.75 0 0 1-1.154.114l-3-3a.75.75 0 0 1 1.06-1.06l2.353 2.353 4.493-6.74a.75.75 0 0 1 1.04-.207Z"
      fillRule="evenodd"
    />
  </svg>
);

/**
 * Pricing card for First Page — Uiverse iconicchandu (scoped under .fp-pricing-card).
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
  const rootClass = ['fp-pricing-card', 'card', featured ? 'card--featured' : '', className]
    .filter(Boolean)
    .join(' ');

  const listItems = [];

  if (tags.length > 0) {
    listItems.push({ key: 'tags-header', type: 'label', text: 'Platform highlights' });
    tags.forEach((tag) => listItems.push({ key: tag, type: 'item', text: tag }));
  }

  sections.forEach((section) => {
    listItems.push({ key: `${section.label}-label`, type: 'label', text: section.label });
    section.items.forEach((item) => {
      const text = typeof item === 'string' ? item : item.text;
      const emph = typeof item === 'object' && item.emph;
      listItems.push({ key: text, type: 'item', text, emph });
    });
  });

  const CtaTag = ctaHref ? Link : 'button';
  const ctaProps = ctaHref ? { to: ctaHref } : { type: 'button' };

  return (
    <div className={rootClass}>
      <div className="card__border" aria-hidden />

      <div className="card_title__container">
        <div className="card_badge-slot">
          {badge ? <span className="card_badge">{badge}</span> : null}
        </div>
        <span className="card_title">{tier}</span>
        {price || period ? (
          <div className="card_price-row" aria-label={[price, period].filter(Boolean).join(', ')}>
            {price ? <span className="card_price">{price}</span> : null}
            {period ? <span className="card_price-period">{period}</span> : null}
          </div>
        ) : null}
        {description ? <p className="card_paragraph">{description}</p> : null}
      </div>

      <hr className="line" />

      <ul className="card__list">
        {listItems.map((entry) => {
          if (entry.type === 'label') {
            return (
              <li key={entry.key} className="card__list_item card__list_item--label">
                <span className="list_text">{entry.text}</span>
              </li>
            );
          }

          return (
            <li
              key={entry.key}
              className={`card__list_item${entry.emph ? ' card__list_item--emph' : ''}`}
            >
              <span className="check">
                <CheckIcon />
              </span>
              <span className="list_text">{entry.text}</span>
            </li>
          );
        })}
      </ul>

      <CtaTag className="button" {...ctaProps}>
        {ctaLabel}
      </CtaTag>
    </div>
  );
}
