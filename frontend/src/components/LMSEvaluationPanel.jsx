import { BarChart3, CheckCircle2, Clock } from 'lucide-react';
import '../css/components/LMSMock.css';
import LMSMockNav from './LMSMockNav';

const COURSES = [
  { id: 'RE', title: 'Real-Time Data Processing with Apache Kafka' },
  { id: 'NA', title: 'Natural Language Processing with PyTorch', active: true },
  { id: 'AI', title: 'AI Model Optimization Techniques' },
];

const METRICS = [
  { label: 'Questions Attempted', value: '8', pct: 13 },
  { label: 'Correct Answers', value: '8', pct: 100 },
  { label: 'Accuracy Rate', value: '100.0%', pct: 100 },
  { label: 'Total Points', value: '6', pct: 10 },
];

const STRENGTHS = [
  'Consistently selects correct answers for questions related to PyTorch and deep learning fundamentals.',
  'Effectively articulates complex ideas, such as the purpose of word embeddings and the definition of NLP.',
  'Shows familiarity with PyTorch functions and their applications in creating tensors.',
];

const IMPROVEMENTS = [
  'Needs to ensure accuracy in answer selection, particularly on tensor creation syntax.',
  'Should work on providing concise answers to avoid redundancy in definitions.',
  'Could benefit from reviewing specific PyTorch functions to enhance practical application skills.',
];

function ScoreRing({ score = 10 }) {
  const offset = 264 - (264 * score) / 10;

  return (
    <div className="lms-mock__score-ring">
      <svg viewBox="0 0 100 100" aria-hidden="true">
        <circle className="lms-mock__score-ring-track" cx="50" cy="50" r="42" />
        <circle
          className="lms-mock__score-ring-fill"
          cx="50"
          cy="50"
          r="42"
          strokeDasharray="264"
          strokeDashoffset={offset}
        />
      </svg>
      <div className="lms-mock__score-ring-text">
        <span className="lms-mock__score-val">{score.toFixed(1)}</span>
        <span className="lms-mock__score-sub">out of 10</span>
      </div>
    </div>
  );
}

export default function LMSEvaluationPanel() {
  return (
    <div className="lms-mock">
      <div className="lms-mock__shell">
        <LMSMockNav />

        <div className="lms-mock__body">
          <aside className="lms-mock__sidebar lms-mock__sidebar--wide">
            <div>
              <h2 className="lms-mock__section-title">AI Evaluation</h2>
              <p className="lms-mock__section-sub">Select a course</p>
            </div>

            <div className="lms-mock__stack lms-mock__stack--sm">
              {COURSES.map((course) => (
                <div
                  key={course.id}
                  className={`lms-mock__course${course.active ? ' is-active' : ''}`}
                >
                  <div className="lms-mock__course-chip">{course.id}</div>
                  <span className="lms-mock__course-title">{course.title}</span>
                </div>
              ))}
            </div>

            <button type="button" className="lms-mock__btn" style={{ marginTop: '0.5rem' }}>
              Run AI Evaluation (3 left)
            </button>
          </aside>

          <main className="lms-mock__main">
            <div className="lms-mock__tabs">
              <span className="lms-mock__tab is-active">Performance Overview</span>
              <span className="lms-mock__tab">My Answers</span>
            </div>

            <div className="lms-mock__grid">
              <div className="lms-mock__card">
                <div className="lms-mock__card-head">
                  <BarChart3 size={13} className="lms-mock__list-icon--accent" />
                  <span className="lms-mock__card-title">Overall Score</span>
                </div>
                <div className="lms-mock__card-center">
                  <ScoreRing score={10} />
                </div>
              </div>

              <div className="lms-mock__card">
                <div className="lms-mock__card-head">
                  <BarChart3 size={13} className="lms-mock__nav-icon" />
                  <span className="lms-mock__card-title">Key Metrics</span>
                </div>
                {METRICS.map((m) => (
                  <div key={m.label} className="lms-mock__metric-row">
                    <div className="lms-mock__metric-head">
                      <span className="lms-mock__metric-label">{m.label}</span>
                      <span className="lms-mock__metric-val">{m.value}</span>
                    </div>
                    <div className="lms-mock__metric-track">
                      <div className="lms-mock__metric-fill" style={{ width: `${m.pct}%` }} />
                    </div>
                  </div>
                ))}
              </div>

              <div className="lms-mock__card">
                <div className="lms-mock__card-head">
                  <CheckCircle2 size={13} className="lms-mock__list-icon" />
                  <span className="lms-mock__card-title">Strengths</span>
                </div>
                <ul className="lms-mock__stack lms-mock__stack--sm">
                  {STRENGTHS.map((s) => (
                    <li key={s} className="lms-mock__list-row">
                      <CheckCircle2 size={12} className="lms-mock__list-icon" />
                      <span className="lms-mock__list-text">{s}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="lms-mock__card">
                <div className="lms-mock__card-head">
                  <Clock size={13} className="lms-mock__list-icon--accent" />
                  <span className="lms-mock__card-title">Areas for Improvement</span>
                </div>
                <ul className="lms-mock__stack lms-mock__stack--sm">
                  {IMPROVEMENTS.map((s) => (
                    <li key={s} className="lms-mock__list-row">
                      <span className="lms-mock__list-icon--accent">▸</span>
                      <span className="lms-mock__list-text">{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
