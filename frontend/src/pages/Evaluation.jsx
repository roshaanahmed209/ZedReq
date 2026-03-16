import React, { useState, useRef, useEffect, useCallback } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { lmsAPI } from '../services/api'
import Navbar from '../components/Navbar'
import '../css/pages/Evaluation.css'

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`

const slideUp = keyframes`
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`

const spin = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`

const LoadingSpinner = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-light);
  
  &::after {
    content: '';
    width: 24px;
    height: 24px;
    border: 3px solid var(--border);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: ${spin} 0.8s linear infinite;
  }
`

const Container = styled.div`
  min-height: 100vh;
  width: 100%;
  background: var(--bg-light);
  animation: ${fadeIn} 0.6s ease-in;
  overflow-x: hidden;
`


const BackButton = styled.button`
  padding: 10px;
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: var(--hover-bg);
    border-color: var(--primary);
  }

  @media (max-width: 600px) {
    padding: 8px;
  }

  @media (max-width: 480px) {
    padding: 8px;
  }
`

const MainContainer = styled.div`
  width: 100%;
  max-width: 100%;
  margin: 0;
  display: grid;
  grid-template-columns: 450px 1fr;
  gap: 25px;
  padding: 30px 20px;
  
  @media (max-width: 1400px) {
    grid-template-columns: 420px 1fr;
    gap: 22px;
    padding: 28px 18px;
  }
  
  @media (max-width: 1200px) {
    grid-template-columns: 400px 1fr;
    gap: 20px;
  }
  
  @media (max-width: 1024px) {
    grid-template-columns: 350px 1fr;
    gap: 20px;
    padding: 25px 15px;
  }
  
  @media (max-width: 900px) {
    grid-template-columns: 320px 1fr;
    gap: 18px;
    padding: 22px 14px;
  }
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 20px;
    padding: 20px 15px;
  }
  
  @media (max-width: 600px) {
    gap: 18px;
    padding: 18px 12px;
  }

  @media (max-width: 480px) {
    padding: 15px 12px;
    gap: 15px;
  }
  
  @media (max-width: 360px) {
    padding: 12px 10px;
    gap: 12px;
  }
`

const SidePanel = styled.aside`
  position: sticky;
  top: 100px;
  height: fit-content;
  max-height: calc(100vh - 120px);
  background: var(--bg-white);
  border-radius: 16px;
  border: 1px solid var(--border);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  overflow: hidden;

  @media (max-width: 768px) {
    position: relative;
    top: 0;
    max-height: none;
  }
`

const PanelHeader = styled.div`
  padding: 28px 28px;
  background: var(--bg-white);
  color: var(--text);
  position: sticky;
  top: 0;
  z-index: 10;
  border-radius: 16px 16px 0 0;
  border-bottom: 1px solid var(--border);
  
  @media (max-width: 1024px) {
    padding: 24px 24px;
  }
  
  @media (max-width: 768px) {
    padding: 20px 20px;
    border-radius: 12px 12px 0 0;
  }
  
  @media (max-width: 480px) {
    padding: 18px 16px;
    border-radius: 10px 10px 0 0;
  }
  
  @media (max-width: 360px) {
    padding: 16px 14px;
  }
`

const PageTitle = styled.h1`
  font-size: 1.5em;
  color: var(--text);
  margin-bottom: 8px;
  font-weight: 300;
  
  @media (max-width: 1024px) {
    font-size: 1.4em;
    margin-bottom: 6px;
  }
  
  @media (max-width: 768px) {
    font-size: 1.3em;
    margin-bottom: 5px;
  }
  
  @media (max-width: 600px) {
    font-size: 1.2em;
  }
  
  @media (max-width: 480px) {
    font-size: 1.1em;
    margin-bottom: 4px;
  }
  
  @media (max-width: 360px) {
    font-size: 1em;
  }
`

const PageSubtitle = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
  
  @media (max-width: 768px) {
    font-size: 0.85em;
  }
  
  @media (max-width: 480px) {
    font-size: 0.8em;
  }
  
  @media (max-width: 360px) {
    font-size: 0.75em;
  }
`

const ScrollableContent = styled.div`
  max-height: calc(100vh - 270px);
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 10px;
  }
  
  &::-webkit-scrollbar-thumb:hover {
    background: var(--text-lighter);
  }
`

const PanelContent = styled.div`
  position: relative;
  padding: 24px 28px;
`

const CourseSelector = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`

const CourseOption = styled.div`
  padding: 14px 18px;
  background: ${props => props.active ? 'rgba(10, 102, 194, 0.1)' : 'transparent'};
  border: 1px solid ${props => props.active ? 'var(--primary)' : 'var(--border)'};
  border-radius: 8px;
  color: ${props => props.active ? 'var(--primary)' : 'var(--text-light)'};
  font-size: 0.9em;
  font-weight: 300;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 12px;
  
  &:hover {
    background: rgba(10, 102, 194, 0.1);
    border-color: var(--primary);
    color: var(--primary);
  }
`

const CourseIcon = styled.div`
  width: 36px;
  height: 36px;
  min-width: 36px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8em;
  font-weight: 500;
  color: white;
`

const CourseTitle = styled.div`
  flex: 1;
  font-size: 0.95em;
`

const MainContent = styled.main`
  min-height: 80vh;
  width: 100%;
`

const EvaluationContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`

const GridContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;

  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
`

const EvaluationCard = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 32px;
  animation: ${slideUp} 0.4s ease-out;
  transition: all 0.3s ease;

  &:hover {
    border-color: rgba(10, 102, 194, 0.3);
  }
`

const CardHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
`

const CardHeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`

const CardIcon = styled.div`
  width: 40px;
  height: 40px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  svg {
    width: 20px;
    height: 20px;
    color: var(--primary);
  }
`

const CardTitle = styled.h2`
  font-size: 1.3em;
  color: var(--text);
  font-weight: 400;
  letter-spacing: -0.3px;
`

const ScoreDisplay = styled.div`
  font-size: 1.8em;
  font-weight: 300;
  color: var(--text);
`

const MetricGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
`

const MetricItem = styled.div`
  padding: 20px;
  background: linear-gradient(135deg, rgba(10, 102, 194, 0.05), rgba(0, 160, 220, 0.05));
  border-radius: 12px;
  border: 1px solid rgba(10, 102, 194, 0.2);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg, var(--primary), var(--secondary));
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(10, 102, 194, 0.2);
    border-color: var(--primary);
  }
`

const MetricLabel = styled.div`
  font-size: 0.8em;
  color: var(--text-light);
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-weight: 500;
`

const MetricValue = styled.div`
  font-size: 1.8em;
  font-weight: 300;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`

const AnalysisList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`

const AnalysisItem = styled.div`
  padding: 20px 24px;
  background: var(--hover-bg);
  border-radius: 8px;
  border: 1px solid var(--border);
  transition: all 0.3s ease;

  &:hover {
    border-color: rgba(10, 102, 194, 0.4);
    background: rgba(10, 102, 194, 0.03);
  }
`

const AnalysisTitle = styled.div`
  font-size: 0.95em;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 12px;
  letter-spacing: 0.3px;
`

const AnalysisText = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
  line-height: 1.7;
  font-weight: 300;
`

const ProgressCircle = styled.div`
  position: relative;
  width: 180px;
  height: 180px;
  margin: 20px auto;
`

const CircleBackground = styled.circle`
  fill: none;
  stroke: var(--border);
  stroke-width: 8;
`

const CircleProgress = styled.circle`
  fill: none;
  stroke: url(#scoreGradient);
  stroke-width: 8;
  stroke-linecap: round;
  transform: rotate(-90deg);
  transform-origin: 50% 50%;
  stroke-dasharray: ${props => props.circumference};
  stroke-dashoffset: ${props => props.offset};
  transition: stroke-dashoffset 1s ease;
`

const CircleText = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
`

const CircleValue = styled.div`
  font-size: 2.5em;
  font-weight: 300;
  color: var(--text);
  margin-bottom: 4px;
`

const CircleLabel = styled.div`
  font-size: 0.85em;
  color: var(--text-light);
  font-weight: 300;
`

const SkillBar = styled.div`
  margin-bottom: 20px;
  
  &:last-child {
    margin-bottom: 0;
  }
`

const SkillHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`

const SkillName = styled.div`
  font-size: 0.9em;
  color: var(--text);
  font-weight: 400;
`

const SkillPercentage = styled.div`
  font-size: 0.85em;
  color: var(--text-light);
  font-weight: 300;
`

const SkillProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: var(--border);
  border-radius: 10px;
  overflow: hidden;
  position: relative;
`

const SkillProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  border-radius: 10px;
  width: ${props => props.width}%;
  transition: width 1s ease;
  position: relative;

  &::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2));
  }
`

const SkillSubStats = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  font-size: 0.75em;
  color: var(--text-light);
`

const TrendChart = styled.div`
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 120px;
  gap: 8px;
  margin-top: 20px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
`

const TrendBar = styled.div`
  flex: 1;
  min-width: 30px;
  background: linear-gradient(180deg, var(--secondary), var(--primary));
  border-radius: 4px 4px 0 0;
  height: ${props => props.height}%;
  position: relative;
  transition: all 0.5s ease;
  
  &:hover {
    opacity: 0.8;
    transform: translateY(-3px);
  }
`

const TrendValue = styled.div`
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.75em;
  color: var(--text);
  font-weight: 400;
  white-space: nowrap;
`

const TrendLabel = styled.div`
  text-align: center;
  font-size: 0.7em;
  color: var(--text-light);
  margin-top: 8px;
`

// My Answers View Styled Components
const ViewToggle = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 16px;
`

const ViewToggleButton = styled.button`
  padding: 10px 20px;
  background: ${props => props.active ? 'var(--primary)' : 'transparent'};
  color: ${props => props.active ? 'white' : 'var(--text-light)'};
  border: 1px solid ${props => props.active ? 'var(--primary)' : 'var(--border)'};
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: ${props => props.active ? '500' : '300'};
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.active ? 'var(--primary)' : 'rgba(10, 102, 194, 0.1)'};
    border-color: var(--primary);
    color: ${props => props.active ? 'white' : 'var(--primary)'};
  }
`

const AnswersHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
`

const FilterSortContainer = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
`

const Select = styled.select`
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg-white);
  color: var(--text);
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary);
  }

  &:focus {
    outline: none;
    border-color: var(--primary);
  }
`

const AnswerCard = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  border: 1px solid var(--border);
  margin-bottom: 16px;
  overflow: hidden;
  transition: all 0.3s ease;

  &:hover {
    border-color: rgba(10, 102, 194, 0.3);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
`

const AnswerCardHeader = styled.div`
  padding: 20px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: ${props => props.expanded ? 'rgba(10, 102, 194, 0.05)' : 'transparent'};
  transition: background 0.2s ease;
`

const AnswerCardLeft = styled.div`
  flex: 1;
  min-width: 0;
`

const AnswerQuestion = styled.div`
  font-size: 1em;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 8px;
  line-height: 1.5;
`

const AnswerMeta = styled.div`
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 0.85em;
  color: var(--text-light);
`

const AnswerMetaItem = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
`

const ScoreBadge = styled.div`
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85em;
  font-weight: 500;
  background: ${props => props.color}20;
  color: ${props => props.color};
  border: 1px solid ${props => props.color}40;
`

const CorrectBadge = styled.div`
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 0.8em;
  font-weight: 500;
  background: ${props => props.correct ? '#10b98120' : '#ef444420'};
  color: ${props => props.correct ? '#10b981' : '#ef4444'};
  border: 1px solid ${props => props.correct ? '#10b98140' : '#ef444440'};
`

const ExpandIcon = styled.div`
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-light);
  transition: transform 0.2s ease;
  transform: ${props => props.expanded ? 'rotate(180deg)' : 'rotate(0deg)'};

  svg {
    width: 20px;
    height: 20px;
  }
`

const AnswerCardContent = styled.div`
  padding: 0 20px;
  max-height: ${props => props.expanded ? '2000px' : '0'};
  overflow: hidden;
  transition: max-height 0.3s ease, padding 0.3s ease;
  padding: ${props => props.expanded ? '0 20px 20px 20px' : '0 20px'};
`

const AnswerSection = styled.div`
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
`

const AnswerSectionTitle = styled.div`
  font-size: 0.9em;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`

const AnswerText = styled.div`
  font-size: 0.9em;
  color: var(--text-light);
  line-height: 1.7;
  padding: 12px;
  background: var(--hover-bg);
  border-radius: 8px;
  white-space: pre-wrap;
  word-wrap: break-word;
`

const FeedbackText = styled.div`
  font-size: 0.9em;
  color: var(--text);
  line-height: 1.7;
  padding: 12px;
  background: rgba(10, 102, 194, 0.05);
  border-radius: 8px;
  white-space: pre-wrap;
  word-wrap: break-word;
`

const SuggestionsList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 12px 0 0 0;
`

const SuggestionItem = styled.li`
  padding: 10px 12px;
  margin-bottom: 8px;
  background: rgba(10, 102, 194, 0.05);
  border-radius: 6px;
  font-size: 0.9em;
  color: var(--text);
  line-height: 1.6;

  &:last-child {
    margin-bottom: 0;
  }
`

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: var(--text-light);
`

const EmptyStateIcon = styled.div`
  font-size: 3em;
  margin-bottom: 16px;
`

const EmptyStateText = styled.div`
  font-size: 1.1em;
  margin-bottom: 8px;
  color: var(--text);
`

const EmptyStateSubtext = styled.div`
  font-size: 0.9em;
  color: var(--text-light);
`

// ---------------------------------------------------------------------------
// Rate-limit constants — module-level so they are never re-declared per render
// ---------------------------------------------------------------------------
const MAX_EVALUATIONS = 3

/**
 * usePersistentCounter
 * A small custom hook that keeps a numeric counter in both React state and
 * localStorage so the value survives page refreshes and logout/login cycles.
 *
 * @param {string}  key  - localStorage key (should be user-scoped by the caller)
 * @param {number}  max  - upper bound; stored value is clamped to [0, max]
 * @returns {[number, (updater: number | ((prev: number) => number)) => void]}
 */
function usePersistentCounter(key, max) {
  const [count, _setCount] = useState(() => {
    const raw = parseInt(localStorage.getItem(key) || '0', 10)
    // Clamp to [0, max] to neutralise any manual localStorage tampering
    return Math.min(Math.max(0, isNaN(raw) ? 0 : raw), max)
  })

  const setCount = useCallback((updater) => {
    _setCount(prev => {
      const next = typeof updater === 'function' ? updater(prev) : updater
      const clamped = Math.min(Math.max(0, next), max)
      localStorage.setItem(key, String(clamped))
      return clamped
    })
  }, [key, max]) // eslint-disable-line react-hooks/exhaustive-deps

  return [count, setCount]
}

const Evaluation = () => {
  const [selectedCourseId, setSelectedCourseId] = useState(null)
  const [courses, setCourses] = useState([])
  const [dashboard, setDashboard] = useState(null)
  const [weeklyPerformance, setWeeklyPerformance] = useState([])
  const [domainPerformance, setDomainPerformance] = useState([])
  const [coursePerformance, setCoursePerformance] = useState(null)
  const [sectionPerformance, setSectionPerformance] = useState([])
  const [courseAnalysis, setCourseAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [performanceLoading, setPerformanceLoading] = useState(false)
  const [evaluating, setEvaluating] = useState(false)
  const [viewMode, setViewMode] = useState('performance') // 'performance' or 'answers'
  const [answers, setAnswers] = useState([])
  const [answersLoading, setAnswersLoading] = useState(false)
  const [expandedAnswers, setExpandedAnswers] = useState(new Set())
  const [sortBy, setSortBy] = useState('date') // 'date', 'score', 'course'
  const [filterCourseId, setFilterCourseId] = useState(null)
  const navigate = useNavigate()
  const location = useLocation()
  const { logout, user: authUser } = useAuth()

  // Persistent rate-limit counter — scoped per user, clamped, tamper-resistant
  const evalKey = React.useMemo(
    () => authUser?.id ? `lms_eval_count_${authUser.id}_${selectedCourseId || 'global'}` : null,
    [authUser?.id, selectedCourseId]
  )
  const [evaluationCount, setEvaluationCount] = usePersistentCounter(evalKey ?? '__noop__', MAX_EVALUATIONS)

  // Fetch courses on mount
  useEffect(() => {
    fetchCourses()
  }, [])

  // If navigated here with a courseId in state (e.g. from "Submit & Evaluate"),
  // auto-select that course once the courses list is loaded.
  useEffect(() => {
    const navCourseId = location.state?.courseId
    if (navCourseId && courses.length > 0) {
      const match = courses.find(c => c.id === navCourseId)
      if (match) {
        setSelectedCourseId(navCourseId)
      }
    }
  }, [courses, location.state])

  // Fetch performance data when course is selected
  useEffect(() => {
    if (selectedCourseId) {
      fetchPerformanceData()
    }
  }, [selectedCourseId])

  // Fetch answers when view mode changes to 'answers'
  useEffect(() => {
    if (viewMode === 'answers') {
      fetchAnswers()
    }
  }, [viewMode, filterCourseId])

  const fetchCourses = async () => {
    try {
      const response = await lmsAPI.getMyCourses({ limit: 100 })
      if (response.data && response.data.courses) {
        const coursesList = response.data.courses.map(course => ({
          id: course.course_id || course.id,
          title: course.course_title || course.title,
          icon: course.course_icon || (course.title ? course.title.substring(0, 2).toUpperCase() : 'CO')
        }))
        setCourses(coursesList)

        // Prefer courseId from navigation state; fallback to first course
        const navCourseId = location.state?.courseId
        if (navCourseId && coursesList.find(c => c.id === navCourseId)) {
          setSelectedCourseId(navCourseId)
        } else if (coursesList.length > 0 && !selectedCourseId) {
          setSelectedCourseId(coursesList[0].id)
        }
      }
    } catch (err) {
      console.error('Error fetching courses:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchPerformanceData = async () => {
    if (!selectedCourseId) return
    
    try {
      setPerformanceLoading(true)
      setLoading(true)
      
      // Fetch all data with individual error handling to prevent one failure from blocking others
      const [dashboardRes, weeklyRes, domainRes, coursePerfRes, sectionPerfRes, analysisRes] = await Promise.allSettled([
        lmsAPI.getDashboard().catch(err => {
          console.warn('Error fetching dashboard:', err)
          return { data: null }
        }),
        lmsAPI.getWeeklyPerformance(7).catch(err => {
          console.warn('Error fetching weekly performance:', err)
          return { data: { performance: [] } }
        }),
        lmsAPI.getDomainPerformance().catch(err => {
          console.warn('Error fetching domain performance:', err)
          return { data: { domains: [] } }
        }),
        lmsAPI.getCoursePerformance(selectedCourseId).catch(err => {
          console.warn('Error fetching course performance:', err)
          return { data: null }
        }),
        lmsAPI.getSectionPerformance(selectedCourseId).catch(err => {
          console.warn('Error fetching section performance:', err)
          return { data: { sections: [] } }
        }),
        lmsAPI.getCourseAnalysis(selectedCourseId).catch(err => {
          console.warn('Error fetching course analysis:', err)
          return { data: null }
        })
      ])

      // Extract data from settled promises
      if (dashboardRes.status === 'fulfilled' && dashboardRes.value?.data) {
        setDashboard(dashboardRes.value.data)
      }
      
      if (weeklyRes.status === 'fulfilled' && weeklyRes.value?.data?.performance) {
        setWeeklyPerformance(weeklyRes.value.data.performance)
      }
      
      if (domainRes.status === 'fulfilled' && domainRes.value?.data?.domains) {
        setDomainPerformance(domainRes.value.data.domains)
      }
      
      if (coursePerfRes.status === 'fulfilled' && coursePerfRes.value?.data) {
        setCoursePerformance(coursePerfRes.value.data)
      }
      

      if (sectionPerfRes.status === 'fulfilled' && sectionPerfRes.value?.data?.sections) {
        setSectionPerformance(sectionPerfRes.value.data.sections)
      }

      if (analysisRes.status === 'fulfilled' && analysisRes.value?.data) {
        setCourseAnalysis(analysisRes.value.data)
      }
    } catch (err) {
      console.error('Error fetching performance data:', err)
    } finally {
      setLoading(false)
      setPerformanceLoading(false)
    }
  }

  const handleRunEvaluation = async () => {
    if (!selectedCourseId) return
    if (evaluationCount >= MAX_EVALUATIONS) {
      console.warn('[Evaluation] handleRunEvaluation: Attempt limit reached')
      return
    }
    
    try {
      setEvaluating(true)
      const response = await lmsAPI.triggerSeezEvaluateCourse(selectedCourseId)
      
      if (response.data) {
        const result = response.data.result || {}
        const message = response.data.message || ''
        
        // Update rate limit counter from server response if available
        if (response.data.rate_limit?.remaining !== undefined) {
          const remaining = response.data.rate_limit.remaining
          setEvaluationCount(() => MAX_EVALUATIONS - remaining)
        } else {
          // Fallback: increment local counter
          setEvaluationCount(prev => prev + 1)
        }
        
        // Check if no answers were found (this is now a success response, not an error)
        if (message.includes('No unevaluated answers found') || 
            (result.error && result.error.includes('No unevaluated answers found'))) {
          alert('All answers for this course have already been evaluated. No new evaluations needed.')
        } else if (result.success) {
          alert(`Evaluation completed! Evaluated ${result.evaluated_count || 0} answer(s).`)
        } else {
          alert('Evaluation completed, but some answers may not have been evaluated.')
        }
        
        // Always refetch performance data to show updated metrics
        await fetchPerformanceData()
        
        // Refresh answers if in answers view
        if (viewMode === 'answers') {
          await fetchAnswers()
        }
      }
    } catch (err) {
      console.error('Error running evaluation:', err)
      
      // Handle rate limit error (429)
      if (err.response?.status === 429) {
        const detail = err.response.data?.detail
        if (detail?.remaining !== undefined) {
          setEvaluationCount(() => MAX_EVALUATIONS - detail.remaining)
        } else {
          setEvaluationCount(MAX_EVALUATIONS) // Assume limit reached
        }
        const errorMsg = detail?.message || detail || 'Evaluation limit reached. Maximum 3 attempts allowed per course.'
        alert(`Error: ${errorMsg}`)
      } else {
        const errorMsg = err.response?.data?.detail || err.message || 'Failed to run evaluation'
        alert(`Error: ${typeof errorMsg === 'string' ? errorMsg : errorMsg.message || 'Failed to run evaluation'}`)
      }
    } finally {
      setEvaluating(false)
    }
  }

  const handleBackToLMS = () => {
    navigate('/lms')
  }

  const handleBackToFeed = () => {
    navigate('/feed')
  }

  // Security: Escape HTML to prevent XSS attacks
  const escapeHtml = (text) => {
    if (!text) return ''
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
  }

  // Fetch user answers with evaluation data
  const fetchAnswers = async () => {
    try {
      setAnswersLoading(true)
      const params = {}
      if (filterCourseId) {
        // We'll filter by course on the frontend since API doesn't support course filter directly
        // For now, fetch all and filter client-side
      }
      const response = await lmsAPI.getMyAnswers(params)
      if (response.data && response.data.answers) {
        let fetchedAnswers = response.data.answers
        
        // Filter by course if selected
        if (filterCourseId) {
          // We need to get course_id from question, but it's not in the answer response
          // For now, we'll show all answers and let user filter visually
          // TODO: Enhance API to include course_id in answer response
        }
        
        setAnswers(fetchedAnswers)
      }
    } catch (err) {
      console.error('Error fetching answers:', err)
    } finally {
      setAnswersLoading(false)
    }
  }

  // Toggle answer expansion
  const toggleAnswer = (answerId) => {
    const newExpanded = new Set(expandedAnswers)
    if (newExpanded.has(answerId)) {
      newExpanded.delete(answerId)
    } else {
      newExpanded.add(answerId)
    }
    setExpandedAnswers(newExpanded)
  }

  // Get score color based on score value
  const getScoreColor = (score) => {
    if (score >= 8) return '#10b981' // green
    if (score >= 6) return '#f59e0b' // yellow
    return '#ef4444' // red
  }

  // Get score badge text
  const getScoreBadgeText = (score) => {
    if (score >= 8) return 'Excellent'
    if (score >= 6) return 'Good'
    if (score >= 4) return 'Fair'
    return 'Needs Improvement'
  }

  // Sort answers
  const getSortedAnswers = () => {
    const sorted = [...answers]
    switch (sortBy) {
      case 'score':
        return sorted.sort((a, b) => {
          // Calculate score from points_earned and question points
          const scoreA = a.points_earned && a.points ? (a.points_earned / a.points) * 10 : 0
          const scoreB = b.points_earned && b.points ? (b.points_earned / b.points) * 10 : 0
          return scoreB - scoreA
        })
      case 'course':
        return sorted.sort((a, b) => {
          const courseA = a.course_title || ''
          const courseB = b.course_title || ''
          return courseA.localeCompare(courseB)
        })
      case 'date':
      default:
        return sorted.sort((a, b) => {
          const dateA = new Date(a.submitted_at || 0)
          const dateB = new Date(b.submitted_at || 0)
          return dateB - dateA
        })
    }
  }

  // Parse improvement suggestions from feedback
  const parseImprovementSuggestions = (feedback) => {
    if (!feedback) return []
    const suggestionsMatch = feedback.match(/Improvement Suggestions:\s*([\s\S]*?)(?:\n\n|$)/i)
    if (suggestionsMatch) {
      const suggestionsText = suggestionsMatch[1]
      // Split by bullet points or new lines
      return suggestionsText
        .split(/\n|•|-\s*/)
        .map(s => s.trim())
        .filter(s => s.length > 0)
    }
    return []
  }

  // Get feedback without improvement suggestions
  const getFeedbackWithoutSuggestions = (feedback) => {
    if (!feedback) return ''
    return feedback.replace(/Improvement Suggestions:[\s\S]*/i, '').trim()
  }

  const selectedCourse = courses.find(c => c.id === selectedCourseId)
  
  // Calculate overall score from course performance or dashboard
  const overallScore = coursePerformance?.accuracy_percentage 
    ? (coursePerformance.accuracy_percentage / 100) * 10 
    : dashboard?.overall_accuracy 
      ? (dashboard.overall_accuracy / 100) * 10 
      : 0
  
  // Calculate metrics - use real data or 0
  const questionsAttempted = coursePerformance?.questions_answered || dashboard?.total_questions || 0
  const correctAnswers = coursePerformance?.correct_answers || dashboard?.correct_answers || 0
  const accuracyRate = coursePerformance?.accuracy_percentage || dashboard?.overall_accuracy || 0
  
  // Calculate weekly trend from real data
  const weeklyTrendData = weeklyPerformance
    .slice(0, 4)
    .reverse()
    .map((week, index) => {
      const accuracy = week.accuracy_percentage || 0
      const score = (accuracy / 100) * 10
      return {
        week: `Week ${index + 1}`,
        score: score,
        height: Math.max(20, Math.min(100, (score / 10) * 100))
      }
    })
  
  // Calculate improvement percentage if we have trend data
  const improvementPercentage = weeklyTrendData.length >= 2
    ? ((weeklyTrendData[weeklyTrendData.length - 1].score - weeklyTrendData[0].score) / weeklyTrendData[0].score * 100).toFixed(1)
    : null

  return (
    <Container>
      <Navbar />

      <MainContainer>
        <SidePanel>
          <PanelHeader>
            <PageTitle>AI Evaluation</PageTitle>
            <PageSubtitle>Select a course</PageSubtitle>
          </PanelHeader>
          
          <PanelContent>
            <ScrollableContent>
              {loading && courses.length === 0 ? (
                <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-light)' }}>
                  Loading courses...
                </div>
              ) : courses.length === 0 ? (
                <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-light)' }}>
                  No courses found. Enroll in a course first.
                </div>
              ) : (
                <>
                  <CourseSelector>
                    {courses.map((course) => (
                      <CourseOption
                        key={course.id}
                        active={selectedCourseId === course.id}
                        onClick={() => setSelectedCourseId(course.id)}
                      >
                        <CourseIcon>{course.icon}</CourseIcon>
                        <CourseTitle>{course.title}</CourseTitle>
                      </CourseOption>
                    ))}
                  </CourseSelector>
                  {selectedCourseId && (
                    <button
                      onClick={handleRunEvaluation}
                      disabled={evaluating || evaluationCount >= MAX_EVALUATIONS}
                      title={
                        evaluationCount >= MAX_EVALUATIONS
                          ? 'Evaluation limit reached (3/3)'
                          : `Run AI evaluation (${MAX_EVALUATIONS - evaluationCount} attempts left)`
                      }
                      style={{
                        marginTop: '20px',
                        width: '100%',
                        padding: '12px',
                        background: evaluationCount >= MAX_EVALUATIONS ? 'var(--border)' : 'var(--primary)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: (evaluating || evaluationCount >= MAX_EVALUATIONS) ? 'not-allowed' : 'pointer',
                        opacity: (evaluating || evaluationCount >= MAX_EVALUATIONS) ? 0.6 : 1
                      }}
                    >
                      {evaluating
                        ? 'Running AI Evaluation...'
                        : evaluationCount >= MAX_EVALUATIONS
                        ? `Limit Reached (${MAX_EVALUATIONS}/${MAX_EVALUATIONS})`
                        : `Run AI Evaluation (${MAX_EVALUATIONS - evaluationCount} left)`
                      }
                    </button>
                  )}
                </>
              )}
            </ScrollableContent>
          </PanelContent>
        </SidePanel>

        <MainContent>
          <EvaluationContainer>
            {/* View Toggle */}
            <ViewToggle>
              <ViewToggleButton
                active={viewMode === 'performance'}
                onClick={() => setViewMode('performance')}
              >
                Performance Overview
              </ViewToggleButton>
              <ViewToggleButton
                active={viewMode === 'answers'}
                onClick={() => setViewMode('answers')}
              >
                My Answers
              </ViewToggleButton>
            </ViewToggle>

            {viewMode === 'answers' ? (
              /* My Answers View */
              <>
                <AnswersHeader>
                  <div style={{ fontSize: '1.2em', fontWeight: '400', color: 'var(--text)' }}>
                    Answer History
                  </div>
                  <FilterSortContainer>
                    <Select
                      value={filterCourseId || ''}
                      onChange={(e) => setFilterCourseId(e.target.value ? parseInt(e.target.value) : null)}
                    >
                      <option value="">All Courses</option>
                      {courses.map(course => (
                        <option key={course.id} value={course.id}>{course.title}</option>
                      ))}
                    </Select>
                    <Select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                    >
                      <option value="date">Sort by Date</option>
                      <option value="score">Sort by Score</option>
                      <option value="course">Sort by Course</option>
                    </Select>
                  </FilterSortContainer>
                </AnswersHeader>

                {answersLoading ? (
                  <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-light)' }}>
                    Loading answers...
                  </div>
                ) : getSortedAnswers().length === 0 ? (
                  <EmptyState>
                    <EmptyStateIcon>📝</EmptyStateIcon>
                    <EmptyStateText>No answers found</EmptyStateText>
                    <EmptyStateSubtext>
                      {filterCourseId 
                        ? 'No evaluated answers for this course yet. Submit answers and run evaluation to see results here.'
                        : 'You haven\'t submitted any answers yet. Go to the LMS page to answer questions and get them evaluated.'}
                    </EmptyStateSubtext>
                  </EmptyState>
                ) : (
                  getSortedAnswers()
                    .filter(answer => {
                      // Filter by course if selected
                      if (filterCourseId && answer.course_id) {
                        return answer.course_id === filterCourseId
                      }
                      return true
                    })
                    .map((answer) => {
                      const isExpanded = expandedAnswers.has(answer.id)
                      const evaluated = answer.evaluated_at !== null
                      // Calculate score from points_earned and question points
                      const score = answer.points_earned && answer.points 
                        ? Math.round((answer.points_earned / answer.points) * 10) 
                        : null
                      const scoreColor = score !== null ? getScoreColor(score) : '#6b7280'
                      const improvementSuggestions = parseImprovementSuggestions(answer.feedback)
                      const feedbackWithoutSuggestions = getFeedbackWithoutSuggestions(answer.feedback)

                      return (
                        <AnswerCard key={answer.id}>
                          <AnswerCardHeader
                            expanded={isExpanded}
                            onClick={() => toggleAnswer(answer.id)}
                          >
                            <AnswerCardLeft>
                              <AnswerQuestion>
                                {escapeHtml(answer.question_text || 'Question not available')}
                              </AnswerQuestion>
                              <AnswerMeta>
                                <AnswerMetaItem>
                                  <span>📅</span>
                                  <span>
                                    {answer.submitted_at 
                                      ? new Date(answer.submitted_at).toLocaleDateString('en-US', {
                                          year: 'numeric',
                                          month: 'short',
                                          day: 'numeric'
                                        })
                                      : 'N/A'}
                                  </span>
                                </AnswerMetaItem>
                                {evaluated && score !== null && (
                                  <>
                                    <AnswerMetaItem>
                                      <ScoreBadge color={scoreColor}>
                                        {score}/10 - {getScoreBadgeText(score)}
                                      </ScoreBadge>
                                    </AnswerMetaItem>
                                    <AnswerMetaItem>
                                      <CorrectBadge correct={answer.is_correct}>
                                        {answer.is_correct ? '✓ Correct' : '✗ Incorrect'}
                                      </CorrectBadge>
                                    </AnswerMetaItem>
                                    <AnswerMetaItem>
                                      <span>Points: {answer.points_earned || 0}/{answer.points || 0}</span>
                                    </AnswerMetaItem>
                                  </>
                                )}
                                {!evaluated && (
                                  <AnswerMetaItem>
                                    <span style={{ color: '#f59e0b' }}>⏳ Not Evaluated</span>
                                  </AnswerMetaItem>
                                )}
                              </AnswerMeta>
                            </AnswerCardLeft>
                            <ExpandIcon expanded={isExpanded}>
                              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <polyline points="6 9 12 15 18 9"></polyline>
                              </svg>
                            </ExpandIcon>
                          </AnswerCardHeader>
                          <AnswerCardContent expanded={isExpanded}>
                            <AnswerSection>
                              <AnswerSectionTitle>Your Answer</AnswerSectionTitle>
                              <AnswerText>
                                {escapeHtml(answer.answer_text || 'No answer provided')}
                              </AnswerText>
                            </AnswerSection>

                            {evaluated && answer.feedback && (
                              <>
                                <AnswerSection>
                                  <AnswerSectionTitle>Feedback</AnswerSectionTitle>
                                  <FeedbackText>
                                    {escapeHtml(feedbackWithoutSuggestions)}
                                  </FeedbackText>
                                </AnswerSection>

                                {improvementSuggestions.length > 0 && (
                                  <AnswerSection>
                                    <AnswerSectionTitle>Improvement Suggestions</AnswerSectionTitle>
                                    <SuggestionsList>
                                      {improvementSuggestions.map((suggestion, idx) => (
                                        <SuggestionItem key={idx}>
                                          {escapeHtml(suggestion)}
                                        </SuggestionItem>
                                      ))}
                                    </SuggestionsList>
                                  </AnswerSection>
                                )}
                              </>
                            )}

                            {evaluated && !answer.feedback && (
                              <AnswerSection>
                                <div style={{ color: 'var(--text-light)', fontStyle: 'italic' }}>
                                  No feedback available for this answer.
                                </div>
                              </AnswerSection>
                            )}
                          </AnswerCardContent>
                        </AnswerCard>
                      )
                    })
                )}
              </>
            ) : (
              /* Performance Overview View */
              <>
            {/* Overall Performance */}
            <GridContainer>
              <EvaluationCard>
                <CardHeader>
                  <CardHeaderLeft>
                    <CardIcon>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                      </svg>
                    </CardIcon>
                    <CardTitle>Overall Score</CardTitle>
                  </CardHeaderLeft>
                </CardHeader>
                
                {performanceLoading ? (
                  <LoadingSpinner />
                ) : (
                  <ProgressCircle>
                    <svg width="180" height="180">
                      <defs>
                        <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="var(--primary)" />
                          <stop offset="100%" stopColor="var(--secondary)" />
                        </linearGradient>
                      </defs>
                      <CircleBackground cx="90" cy="90" r="70" />
                      <CircleProgress 
                        cx="90" 
                        cy="90" 
                        r="70" 
                        circumference={2 * Math.PI * 70}
                        offset={2 * Math.PI * 70 * (1 - Math.max(0, overallScore) / 10)}
                      />
                    </svg>
                    <CircleText>
                      <CircleValue>{overallScore > 0 ? overallScore.toFixed(1) : '0.0'}</CircleValue>
                      <CircleLabel>out of 10</CircleLabel>
                    </CircleText>
                  </ProgressCircle>
                )}
              </EvaluationCard>

              <EvaluationCard>
                <CardHeader>
                  <CardHeaderLeft>
                    <CardIcon>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="18" y1="20" x2="18" y2="10"></line>
                        <line x1="12" y1="20" x2="12" y2="4"></line>
                        <line x1="6" y1="20" x2="6" y2="14"></line>
                      </svg>
                    </CardIcon>
                    <CardTitle>Key Metrics</CardTitle>
                  </CardHeaderLeft>
                </CardHeader>
                
                {performanceLoading ? (
                  <LoadingSpinner />
                ) : (
                  <div>
                    <SkillBar>
                      <SkillHeader>
                        <SkillName>Questions Attempted</SkillName>
                        <SkillPercentage>{questionsAttempted}</SkillPercentage>
                      </SkillHeader>
                      <SkillProgressBar>
                        <SkillProgressFill width={Math.min(100, (questionsAttempted / 150) * 100)} />
                      </SkillProgressBar>
                    </SkillBar>
                    <SkillBar>
                      <SkillHeader>
                        <SkillName>Correct Answers</SkillName>
                        <SkillPercentage>{correctAnswers}</SkillPercentage>
                      </SkillHeader>
                      <SkillProgressBar>
                        <SkillProgressFill width={questionsAttempted > 0 ? Math.min(100, (correctAnswers / questionsAttempted) * 100) : 0} />
                      </SkillProgressBar>
                    </SkillBar>
                    <SkillBar>
                      <SkillHeader>
                        <SkillName>Accuracy Rate</SkillName>
                        <SkillPercentage>{accuracyRate.toFixed(1)}%</SkillPercentage>
                      </SkillHeader>
                      <SkillProgressBar>
                        <SkillProgressFill width={accuracyRate} />
                      </SkillProgressBar>
                    </SkillBar>
                    <SkillBar>
                      <SkillHeader>
                        <SkillName>Total Points</SkillName>
                        <SkillPercentage>{coursePerformance?.total_points_earned || 0}</SkillPercentage>
                      </SkillHeader>
                      <SkillProgressBar>
                        <SkillProgressFill width={Math.min(100, ((coursePerformance?.total_points_earned || 0) / 200) * 100)} />
                      </SkillProgressBar>
                    </SkillBar>
                  </div>
                )}
              </EvaluationCard>
            </GridContainer>

            <GridContainer>
              {/* Strengths */}
              <EvaluationCard>
                <CardHeader>
                  <CardHeaderLeft>
                    <CardIcon>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                      </svg>
                    </CardIcon>
                    <CardTitle>Strengths</CardTitle>
                  </CardHeaderLeft>
                </CardHeader>

                {performanceLoading ? (
                  <LoadingSpinner />
                ) : (
                  <div>
                    {courseAnalysis?.strengths?.length > 0 ? (
                      <AnalysisList>
                        {courseAnalysis.strengths.map((item, index) => (
                          <AnalysisItem key={index}>
                            <AnalysisText style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                              <span style={{ color: '#22c55e', flexShrink: 0 }}>✓</span>
                              {item}
                            </AnalysisText>
                          </AnalysisItem>
                        ))}
                      </AnalysisList>
                    ) : (
                      <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-light)' }}>
                        No strengths data available yet. Complete and evaluate questions to see your strengths.
                      </div>
                    )}
                  </div>
                )}
              </EvaluationCard>

              {/* Areas for Improvement */}
              <EvaluationCard>
                <CardHeader>
                  <CardHeaderLeft>
                    <CardIcon>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                      </svg>
                    </CardIcon>
                    <CardTitle>Areas for Improvement</CardTitle>
                  </CardHeaderLeft>
                </CardHeader>

                {performanceLoading ? (
                  <LoadingSpinner />
                ) : (
                  <div>
                    {courseAnalysis?.areas_for_improvement?.length > 0 ? (
                      <>
                        <AnalysisList>
                          {courseAnalysis.areas_for_improvement.map((item, index) => (
                            <AnalysisItem key={index}>
                              <AnalysisText style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                                <span style={{ color: '#f59e0b', flexShrink: 0 }}>▸</span>
                                {item}
                              </AnalysisText>
                            </AnalysisItem>
                          ))}
                        </AnalysisList>
                        {courseAnalysis.summary && (
                          <div style={{ padding: '12px 20px', fontSize: '0.85em', color: 'var(--text-light)', fontStyle: 'italic', borderTop: '1px solid var(--border)' }}>
                            {courseAnalysis.summary}
                          </div>
                        )}
                      </>
                    ) : (
                      <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-light)' }}>
                        No improvement areas identified yet. Complete and evaluate questions to get personalized feedback.
                      </div>
                    )}
                  </div>
                )}
              </EvaluationCard>
            </GridContainer>

            {/* Performance by Level (Section) */}
            <GridContainer>
              <EvaluationCard>
                <CardHeader>
                  <CardHeaderLeft>
                    <CardIcon>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 20V10"></path>
                        <path d="M18 20V4"></path>
                        <path d="M6 20v-4"></path>
                      </svg>
                    </CardIcon>
                    <CardTitle>Performance by Level</CardTitle>
                  </CardHeaderLeft>
                </CardHeader>

                {performanceLoading ? (
                  <LoadingSpinner />
                ) : (
                  <div>
                    {sectionPerformance.length > 0 ? (
                      sectionPerformance.map((section) => (
                        <SkillBar key={section.section_id}>
                          <SkillHeader>
                            <SkillName>{section.title}</SkillName>
                            <SkillPercentage>
                              {section.questions_answered > 0
                                ? `${(Number(section.accuracy_percentage) || 0).toFixed(1)}%`
                                : '—'}
                            </SkillPercentage>
                          </SkillHeader>
                        <SkillProgressBar>
                          <SkillProgressFill width={Number(section.accuracy_percentage) || 0} />
                        </SkillProgressBar>
                        <SkillSubStats>
                          <span>{section.correct_answers}/{section.questions_answered} correct</span>
                          <span>{section.total_points_earned} pts</span>
                        </SkillSubStats>
                      </SkillBar>
                    ))
                  ) : (
                    <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-light)' }}>
                      No section performance data available yet. Generate and answer questions by level to see results here.
                    </div>
                  )}
                  </div>
                )}
              </EvaluationCard>
            </GridContainer>

            <GridContainer>
              {/* Progress & Trends */}
              <EvaluationCard>
                <CardHeader>
                  <CardHeaderLeft>
                    <CardIcon>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                        <polyline points="17 6 23 6 23 12"></polyline>
                      </svg>
                    </CardIcon>
                    <CardTitle>Performance Trend</CardTitle>
                  </CardHeaderLeft>
                </CardHeader>

                {weeklyTrendData.length > 0 ? (
                  <>
                    <TrendChart>
                      {weeklyTrendData.map((week, index) => (
                        <div key={index} className="trend-bar-wrapper">
                          <TrendBar height={week.height}>
                            <TrendValue>{week.score.toFixed(1)}</TrendValue>
                          </TrendBar>
                          <TrendLabel>{week.week}</TrendLabel>
                        </div>
                      ))}
                    </TrendChart>

                    <AnalysisList className="analysis-list-spaced">
                      <AnalysisItem>
                        <AnalysisTitle>
                          {improvementPercentage && parseFloat(improvementPercentage) > 0 
                            ? 'Performance Improvement' 
                            : improvementPercentage && parseFloat(improvementPercentage) < 0
                            ? 'Performance Review'
                            : 'Performance Tracking'}
                        </AnalysisTitle>
                        <AnalysisText>
                          {improvementPercentage && parseFloat(improvementPercentage) > 0
                            ? `Your performance has improved by ${Math.abs(parseFloat(improvementPercentage)).toFixed(1)}% over the last ${weeklyTrendData.length} week${weeklyTrendData.length > 1 ? 's' : ''}. You're showing steady progress in understanding core concepts.`
                            : improvementPercentage && parseFloat(improvementPercentage) < 0
                            ? `Your performance has decreased by ${Math.abs(parseFloat(improvementPercentage)).toFixed(1)}% over the last ${weeklyTrendData.length} week${weeklyTrendData.length > 1 ? 's' : ''}. Consider reviewing the material and practicing more.`
                            : `Tracking your performance over the last ${weeklyTrendData.length} week${weeklyTrendData.length > 1 ? 's' : ''}. Keep up the consistent effort!`}
                        </AnalysisText>
                      </AnalysisItem>
                    </AnalysisList>
                  </>
                ) : (
                  <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--text-light)' }}>
                    <div style={{ fontSize: '2em', marginBottom: '12px' }}>📊</div>
                    <div>No weekly performance data available yet.</div>
                    <div style={{ fontSize: '0.9em', marginTop: '8px' }}>
                      Complete more questions to see your performance trend.
                    </div>
                  </div>
                )}
              </EvaluationCard>

            </GridContainer>
              </>
            )}

          </EvaluationContainer>
        </MainContent>
      </MainContainer>
    </Container>
  )
}

export default Evaluation

