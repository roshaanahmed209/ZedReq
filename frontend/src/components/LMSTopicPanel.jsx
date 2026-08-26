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

const SOURCES = [
  { host: 'kafka.apache.org', note: 'Official docs', done: true },
  { host: 'confluent.io', note: 'Stream processing', done: true },
  { host: 'martinfowler.com', note: 'Event streaming', done: true },
  { host: 'redis.io', note: 'Caching patterns', live: true },
  { host: 'highscalability.com', note: 'Case studies', queued: true },
];

export default function LMSTopicPanel() {
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

              <main className="lms-mock__main lms-mock__main--col">
                <div className="lms-mock__tile">
                  <p className="lms-mock__tile-title">Profile gap</p>
                  <p className="lms-mock__tile-heading">
                    Backend Engineer → Senior Platform Engineer
                  </p>
                  <p className="lms-mock__tile-body">
                    Missing: stream processing, event-driven architecture, Kafka internals
                  </p>
                </div>

                <div className="lms-mock__banner">
                  <p className="lms-mock__banner-title">Searching the open web</p>
                  <p className="lms-mock__banner-body">
                    38 sources scanned · 12 questions drafted from current material
                  </p>
                </div>

                <ul className="lms-mock__stack lms-mock__stack--sm">
                  {SOURCES.map((src) => (
                    <li
                      key={src.host}
                      className={`lms-mock__source${src.queued ? ' is-queued' : ''}`}
                    >
                      <span
                        className={`lms-mock__source-dot${
                          src.done ? ' is-done' : src.live ? ' is-live' : ''
                        }`}
                      />
                      <span className="lms-mock__source-host">{src.host}</span>
                      <span className="lms-mock__source-note">{src.note}</span>
                    </li>
                  ))}
                </ul>
              </main>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
