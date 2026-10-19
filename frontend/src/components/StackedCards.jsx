import '../css/components/StackedCards.css';

export default function StackedCards({ items }) {
  return (
    <div className="stacked-cards stacked-cards--static" aria-label="Privacy and security highlights">
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
