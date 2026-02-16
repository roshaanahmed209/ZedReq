import React, { useState, useRef, useEffect } from 'react'
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
  
  @media (max-width: 1200px) {
    grid-template-columns: 400px 1fr;
    gap: 20px;
  }
  
  @media (max-width: 1024px) {
    grid-template-columns: 350px 1fr;
    gap: 20px;
    padding: 25px 15px;
  }
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 20px;
    padding: 20px 15px;
  }

  @media (max-width: 480px) {
    padding: 15px 12px;
    gap: 15px;
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
`

const PageTitle = styled.h1`
  font-size: 1.5em;
  color: var(--text);
  margin-bottom: 8px;
  font-weight: 300;
`

const PageSubtitle = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
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

const RecommendationCard = styled.div`
  padding: 16px 20px;
  background: transparent;
  border-left: 2px solid var(--border);
  margin-top: 16px;
  margin-left: 4px;
`

const RecommendationTitle = styled.div`
  font-size: 0.85em;
  font-weight: 400;
  color: var(--text-light);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
`

const RecommendationText = styled.p`
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

const Evaluation = () => {
  const [selectedCourseId, setSelectedCourseId] = useState(null)
  const [courses, setCourses] = useState([])
  const [dashboard, setDashboard] = useState(null)
  const [weeklyPerformance, setWeeklyPerformance] = useState([])
  const [domainPerformance, setDomainPerformance] = useState([])
  const [coursePerformance, setCoursePerformance] = useState(null)
  const [loading, setLoading] = useState(true)
  const [evaluating, setEvaluating] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { logout } = useAuth()

  // Fetch courses on mount
  useEffect(() => {
    fetchCourses()
  }, [])

  // Fetch performance data when course is selected
  useEffect(() => {
    if (selectedCourseId) {
      fetchPerformanceData()
    }
  }, [selectedCourseId])

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
        if (coursesList.length > 0 && !selectedCourseId) {
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
      setLoading(true)
      const [dashboardRes, weeklyRes, domainRes, coursePerfRes] = await Promise.all([
        lmsAPI.getDashboard(),
        lmsAPI.getWeeklyPerformance(7),
        lmsAPI.getDomainPerformance(),
        lmsAPI.getCoursePerformance(selectedCourseId)
      ])

      if (dashboardRes.data) setDashboard(dashboardRes.data)
      if (weeklyRes.data && weeklyRes.data.performance) setWeeklyPerformance(weeklyRes.data.performance)
      if (domainRes.data && domainRes.data.domains) setDomainPerformance(domainRes.data.domains)
      if (coursePerfRes.data) setCoursePerformance(coursePerfRes.data)
    } catch (err) {
      console.error('Error fetching performance data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleRunEvaluation = async () => {
    if (!selectedCourseId) return
    
    try {
      setEvaluating(true)
      const response = await lmsAPI.triggerSeezEvaluateCourse(selectedCourseId)
      
      if (response.data && response.data.result && response.data.result.success) {
        alert(`Evaluation completed! Evaluated ${response.data.result.evaluated_count} answers.`)
        // Refetch performance data to show updated metrics
        await fetchPerformanceData()
      } else {
        alert('Evaluation completed, but some answers may not have been evaluated.')
      }
    } catch (err) {
      console.error('Error running evaluation:', err)
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to run evaluation'
      alert(`Error: ${errorMsg}`)
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

  const selectedCourse = courses.find(c => c.id === selectedCourseId)
  
  // Calculate overall score from course performance or dashboard
  const overallScore = coursePerformance?.accuracy_percentage 
    ? (coursePerformance.accuracy_percentage / 100) * 10 
    : dashboard?.overall_accuracy 
      ? (dashboard.overall_accuracy / 100) * 10 
      : 8.4
  
  // Calculate metrics
  const questionsAttempted = coursePerformance?.questions_answered || dashboard?.total_questions || 127
  const correctAnswers = coursePerformance?.correct_answers || dashboard?.correct_answers || 98
  const accuracyRate = coursePerformance?.accuracy_percentage || dashboard?.overall_accuracy || 77.2

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
                      disabled={evaluating}
                      style={{
                        marginTop: '20px',
                        width: '100%',
                        padding: '12px',
                        background: 'var(--primary)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: evaluating ? 'not-allowed' : 'pointer',
                        opacity: evaluating ? 0.6 : 1
                      }}
                    >
                      {evaluating ? 'Running AI Evaluation...' : 'Run AI Evaluation'}
                    </button>
                  )}
                </>
              )}
            </ScrollableContent>
          </PanelContent>
        </SidePanel>

        <MainContent>
          <EvaluationContainer>
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
                      offset={2 * Math.PI * 70 * (1 - overallScore / 10)}
                    />
                  </svg>
                  <CircleText>
                    <CircleValue>{overallScore.toFixed(1)}</CircleValue>
                    <CircleLabel>out of 10</CircleLabel>
                  </CircleText>
                </ProgressCircle>
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
                      <SkillProgressFill width={Math.min(100, (correctAnswers / questionsAttempted) * 100)} />
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

                <div>
                  {domainPerformance.length > 0 ? (
                    domainPerformance
                      .sort((a, b) => (b.accuracy_percentage || 0) - (a.accuracy_percentage || 0))
                      .slice(0, 3)
                      .map((domain, index) => (
                        <SkillBar key={domain.id || index}>
                          <SkillHeader>
                            <SkillName>{domain.domain_name || 'Domain'}</SkillName>
                            <SkillPercentage>{domain.accuracy_percentage?.toFixed(1) || 0}%</SkillPercentage>
                          </SkillHeader>
                          <SkillProgressBar>
                            <SkillProgressFill width={domain.accuracy_percentage || 0} />
                          </SkillProgressBar>
                        </SkillBar>
                      ))
                  ) : (
                    <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-light)' }}>
                      No domain performance data available
                    </div>
                  )}
                </div>
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

                <div>
                  <SkillBar>
                    <SkillHeader>
                      <SkillName>Advanced Hooks</SkillName>
                      <SkillPercentage>58%</SkillPercentage>
                    </SkillHeader>
                    <SkillProgressBar>
                      <SkillProgressFill width={58} />
                    </SkillProgressBar>
                  </SkillBar>
                  <SkillBar>
                    <SkillHeader>
                      <SkillName>Testing & Debugging</SkillName>
                      <SkillPercentage>45%</SkillPercentage>
                    </SkillHeader>
                    <SkillProgressBar>
                      <SkillProgressFill width={45} />
                    </SkillProgressBar>
                  </SkillBar>
                  
                  <AnalysisList className="analysis-list-spaced">
                    <AnalysisItem>
                      <AnalysisText>
                        Focus on completing the "Advanced Hooks" and "Testing with Jest" modules to improve these areas. Practice exercises are available in the LMS portal.
                      </AnalysisText>
                    </AnalysisItem>
                  </AnalysisList>
                </div>
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

                <TrendChart>
                  <div className="trend-bar-wrapper">
                    <TrendBar height={65}>
                      <TrendValue>6.5</TrendValue>
                    </TrendBar>
                    <TrendLabel>Week 1</TrendLabel>
                  </div>
                  <div className="trend-bar-wrapper">
                    <TrendBar height={72}>
                      <TrendValue>7.2</TrendValue>
                    </TrendBar>
                    <TrendLabel>Week 2</TrendLabel>
                  </div>
                  <div className="trend-bar-wrapper">
                    <TrendBar height={78}>
                      <TrendValue>7.8</TrendValue>
                    </TrendBar>
                    <TrendLabel>Week 3</TrendLabel>
                  </div>
                  <div className="trend-bar-wrapper">
                    <TrendBar height={84}>
                      <TrendValue>8.4</TrendValue>
                    </TrendBar>
                    <TrendLabel>Week 4</TrendLabel>
                  </div>
                </TrendChart>

                <AnalysisList className="analysis-list-spaced">
                  <AnalysisItem>
                    <AnalysisTitle>
                      Consistent Improvement
                    </AnalysisTitle>
                    <AnalysisText>
                      Your performance has improved by 15% over the last 4 weeks. You're showing steady progress in understanding core concepts.
                    </AnalysisText>
                  </AnalysisItem>
                </AnalysisList>
              </EvaluationCard>

              {/* AI Recommendations */}
              <EvaluationCard>
                <CardHeader>
                  <CardHeaderLeft>
                    <CardIcon>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                      </svg>
                    </CardIcon>
                    <CardTitle>Recommendations</CardTitle>
                  </CardHeaderLeft>
                </CardHeader>

                <AnalysisList>
                  <AnalysisItem>
                    <AnalysisTitle>
                      Next Course to Take
                    </AnalysisTitle>
                    <AnalysisText>
                      Based on your current skill level and progress, we recommend taking "Testing with Jest" next to strengthen your weak areas.
                    </AnalysisText>
                  </AnalysisItem>
                  <AnalysisItem>
                    <AnalysisTitle>
                      Practice Focus
                    </AnalysisTitle>
                    <AnalysisText>
                      Complete 5 more practice exercises on advanced hooks this week. Focus on useCallback dependencies and useMemo optimization scenarios.
                    </AnalysisText>
                  </AnalysisItem>
                </AnalysisList>
              </EvaluationCard>
            </GridContainer>

          </EvaluationContainer>
        </MainContent>
      </MainContainer>
    </Container>
  )
}

export default Evaluation

