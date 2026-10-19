import { ExternalLink, Link2, Lock, Sparkles, X } from 'lucide-react';
import '../css/components/LMSMock.css';
import LMSMockNav from './LMSMockNav';

const LEVELS = [
  { label: 'Basic', selected: true },
  { label: 'Intermediate', locked: true },
  { label: 'Expert', locked: true },
];

const RESOURCES = [
  'Apache Kafka Stream Processing Guide',
  'Learning Apache Kafka — Fundamentals',
  'Event-Driven Architecture Patterns',
  'Kafka Producers & Consumers',
  'Real-Time Data Pipelines',
];

const Q1_OPTIONS = [
  'Storing large files',
  'Real-time stream processing and event streaming',
  'Web development',
  'Machine learning model training',
];

const Q2_OPTIONS = ['True', 'False'];

function OptionRow({ letter, label, chosen }) {
  return (
    <div className={`lms-mock__option${chosen ? ' is-chosen' : ''}`}>
      <span className="lms-mock__option-radio">
        {chosen ? <span className="lms-mock__option-radio-dot" /> : null}
      </span>
      <span>
        <b className="lms-mock__option-letter">{letter}</b>
        {label}
      </span>
    </div>
  );
}

export default function LMSQuizPanel() {
  return (
    <div className="lms-mock">
      <div className="lms-mock__shell">
        <LMSMockNav />

        <div className="lms-mock__layout-row">
          <div className="lms-mock__modal">
            <div className="lms-mock__modal-head">
              <h3 className="lms-mock__modal-title">
                Real-Time Data Processing with Apache Kafka
              </h3>
              <X size={16} className="lms-mock__nav-icon" />
            </div>

            <div className="lms-mock__body">
              <aside className="lms-mock__sidebar">
                <div>
                  <p className="lms-mock__label">Level / Section</p>
                  <div className="lms-mock__stack lms-mock__stack--sm">
                    {LEVELS.map((level) => (
                      <div
                        key={level.label}
                        className={`lms-mock__level${level.selected ? ' is-selected' : ''}`}
                      >
                        <span>{level.label}</span>
                        {level.selected ? (
                          <span className="lms-mock__level-meta">• selected</span>
                        ) : level.locked ? (
                          <Lock size={11} className="lms-mock__warn-icon" />
                        ) : null}
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="lms-mock__label">Resources</p>
                  <ul className="lms-mock__stack lms-mock__stack--sm">
                    {RESOURCES.map((r) => (
                      <li key={r} className="lms-mock__resource">
                        <Link2 size={11} className="lms-mock__nav-icon" />
                        <span className="lms-mock__resource-text">{r}</span>
                        <ExternalLink size={10} className="lms-mock__nav-icon" />
                      </li>
                    ))}
                  </ul>
                </div>

                <button type="button" className="lms-mock__btn">
                  <Sparkles size={13} />
                  Generate Questions
                  <span className="lms-mock__btn-sub">(Basic) · 3 left</span>
                </button>
              </aside>

              <main className="lms-mock__main">
                <div className="lms-mock__section-gap">
                  <div className="lms-mock__progress-head">
                    <span className="lms-mock__progress-label">Overall Progress</span>
                    <span className="lms-mock__progress-meta">2 of 5 answered (40%)</span>
                  </div>
                  <div className="lms-mock__progress-track">
                    <div className="lms-mock__progress-fill" style={{ width: '40%' }} />
                  </div>
                </div>

                <div className="lms-mock__banner lms-mock__section-gap">
                  <p className="lms-mock__banner-title">Basic — Questions &amp; Assessment.</p>
                  <p className="lms-mock__banner-body">
                    Showing questions for the &ldquo;Basic&rdquo; level. Select a different section on the left to switch.
                  </p>
                </div>

                <p className="lms-mock__mono">Page 1 of 1 · Questions 1–5 of 5</p>

                <div className="lms-mock__q-block">
                  <p className="lms-mock__q-label">Question 1</p>
                  <p className="lms-mock__q-text">What is Apache Kafka primarily used for?</p>
                  <div className="lms-mock__stack lms-mock__stack--sm">
                    {Q1_OPTIONS.map((opt, i) => (
                      <OptionRow
                        key={opt}
                        letter={String.fromCharCode(65 + i)}
                        label={opt}
                        chosen={i === 1}
                      />
                    ))}
                  </div>
                </div>

                <div className="lms-mock__q-block">
                  <p className="lms-mock__q-label">Question 2</p>
                  <p className="lms-mock__q-text">
                    True or False: Apache Kafka can only process data in batches, not in real-time.
                  </p>
                  <div className="lms-mock__stack lms-mock__stack--sm">
                    {Q2_OPTIONS.map((opt, i) => (
                      <OptionRow
                        key={opt}
                        letter={String.fromCharCode(65 + i)}
                        label={opt}
                        chosen={i === 1}
                      />
                    ))}
                  </div>
                </div>

                <div className="lms-mock__q-block lms-mock__q-block--fold">
                  <p className="lms-mock__q-label">Question 3</p>
                  <p className="lms-mock__q-text">
                    Explain how Kafka partitions help with scalability in a distributed system.
                  </p>
                  <div className="lms-mock__input">Type your answer here…</div>
                </div>
              </main>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
