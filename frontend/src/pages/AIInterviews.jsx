import React, { useState, useRef, useEffect } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { interviewAPI, jobAPI } from '../services/api'
import Navbar from '../components/Navbar'
import '../css/pages/AIInterviews.css'

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
  background: #0D0D0D;
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
  height: calc(100vh - 80px);
  margin: 0;
  display: grid;
  grid-template-columns: 1fr 450px;
  gap: 0;
  
  @media (max-width: 1400px) {
    grid-template-columns: 1fr 420px;
  }
  
  @media (max-width: 1200px) {
    grid-template-columns: 1fr 400px;
  }
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr 350px;
  }
  
  @media (max-width: 900px) {
    grid-template-columns: 1fr 320px;
  }
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    height: auto;
    min-height: calc(100vh - 80px);
  }
  
  @media (max-width: 600px) {
    height: auto;
    min-height: calc(100vh - 70px);
  }
  
  @media (max-width: 480px) {
    min-height: calc(100vh - 65px);
  }
  
  @media (max-width: 360px) {
    min-height: calc(100vh - 60px);
  }
`

const VideoPanel = styled.div`
  background: #0D0D0D;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 30px;
  position: relative;

  @media (max-width: 1024px) {
    padding: 25px;
  }
  
  @media (max-width: 900px) {
    padding: 22px;
  }

  @media (max-width: 768px) {
    padding: 20px;
    min-height: 60vh;
  }
  
  @media (max-width: 600px) {
    padding: 18px;
    min-height: 55vh;
  }

  @media (max-width: 480px) {
    padding: 15px;
    min-height: 50vh;
  }
  
  @media (max-width: 360px) {
    padding: 12px;
    min-height: 45vh;
  }
`

const DescriptionBanner = styled.div`
  width: 100%;
  max-width: 900px;
  border-radius: 12px;
  padding: 24px 28px;
  margin-bottom: 30px;
  animation: ${slideUp} 0.4s ease-out;

  @media (max-width: 768px) {
    padding: 20px 24px;
    margin-bottom: 24px;
  }

  @media (max-width: 480px) {
    padding: 16px 20px;
    margin-bottom: 20px;
  }
`

const BannerTitle = styled.h2`
  font-size: 1.5em;
  color: white;
  margin-bottom: 12px;
  font-weight: 300;
  display: flex;
  align-items: center;
  gap: 12px;

  svg {
    width: 28px;
    height: 28px;
    color: var(--primary);
  }

  @media (max-width: 768px) {
    font-size: 1.3em;
    gap: 10px;

    svg {
      width: 24px;
      height: 24px;
    }
  }

  @media (max-width: 480px) {
    font-size: 1.2em;
    gap: 8px;

    svg {
      width: 22px;
      height: 22px;
    }
  }
`

const BannerDescription = styled.p`
  font-size: 0.95em;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  font-weight: 300;

  @media (max-width: 768px) {
    font-size: 0.9em;
  }

  @media (max-width: 480px) {
    font-size: 0.85em;
    line-height: 1.5;
  }
`

const VideoContainer = styled.div`
  width: 100%;
  max-width: 900px;
  background: #000;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  position: relative;

  @media (max-width: 768px) {
    border-radius: 12px;
  }
`

const Video = styled.video`
  width: 100%;
  height: auto;
  display: block;
`

const CallControls = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;
  width: 100%;
  max-width: 900px;
  padding: 20px;
  animation: ${slideUp} 0.4s ease-out;

  @media (max-width: 768px) {
    gap: 12px;
    padding: 16px;
  }

  @media (max-width: 480px) {
    gap: 10px;
    padding: 12px;
  }
`

const CallButton = styled.button`
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  background: ${props => props.active ? 'var(--hover-bg)' : 'var(--bg-white)'};
  border: 2px solid ${props => props.active ? 'var(--primary)' : 'var(--border)'};
  color: ${props => props.active ? 'var(--primary)' : 'var(--text-light)'};
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  min-width: 44px; /* Better touch target */
  min-height: 44px;

  svg {
    width: 24px;
    height: 24px;
  }

  &:hover {
    background: var(--hover-bg);
    border-color: var(--primary);
    color: var(--primary);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(10, 102, 194, 0.2);
  }

  &:active {
    transform: translateY(0);
  }

  @media (max-width: 1024px) {
    width: 52px;
    height: 52px;
    
    svg {
      width: 23px;
      height: 23px;
    }
  }

  @media (max-width: 768px) {
    width: 50px;
    height: 50px;

    svg {
      width: 22px;
      height: 22px;
    }
    
    &:hover {
      transform: translateY(-1px);
    }
  }
  
  @media (max-width: 600px) {
    width: 48px;
    height: 48px;
    
    svg {
      width: 21px;
      height: 21px;
    }
  }

  @media (max-width: 480px) {
    width: 46px;
    height: 46px;

    svg {
      width: 20px;
      height: 20px;
    }
    
    &:hover {
      transform: none;
    }
  }
  
  @media (max-width: 360px) {
    width: 44px;
    height: 44px;
    
    svg {
      width: 18px;
      height: 18px;
    }
  }
`

const StartButton = styled(CallButton)`
  background: #2ecc71;
  border-color: #2ecc71;
  color: white;

  &:hover {
    background: #27ae60;
    border-color: #27ae60;
    color: white;
    box-shadow: 0 4px 12px rgba(46, 204, 113, 0.4);
  }
`

const EndCallButton = styled(CallButton)`
  background: #e74c3c;
  border-color: #e74c3c;
  color: white;

  &:hover {
    background: #c0392b;
    border-color: #c0392b;
    color: white;
    box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4);
  }
`

const CallButtonLabel = styled.span`
  font-size: 0.75em;
  color: var(--text-lighter);
  text-align: center;
  margin-top: 6px;
  display: block;

  @media (max-width: 480px) {
    font-size: 0.7em;
    margin-top: 4px;
  }
`

const CallButtonWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
`

const ChatPanel = styled.div`
  background: var(--bg-white);
  margin-top: 20px;
  width: 100%;
  max-width: 900px;
  border-radius: 12px;
  border: 1px solid var(--border);
  animation: ${slideUp} 0.4s ease-out;
  display: flex;
  flex-direction: column;
  height: 400px;

  @media (max-width: 1024px) {
    height: 380px;
    margin-top: 18px;
  }
  
  @media (max-width: 900px) {
    height: 360px;
  }

  @media (max-width: 768px) {
    margin-top: 16px;
    height: 350px;
    border-radius: 10px;
  }
  
  @media (max-width: 600px) {
    height: 320px;
    margin-top: 14px;
  }

  @media (max-width: 480px) {
    margin-top: 12px;
    height: 300px;
    border-radius: 8px;
  }
  
  @media (max-width: 360px) {
    height: 280px;
    margin-top: 10px;
  }
`

const ChatHeader = styled.div`
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--hover-bg);
  border-radius: 12px 12px 0 0;
  display: flex;
  align-items: center;
  gap: 10px;

  svg {
    width: 20px;
    height: 20px;
    color: var(--primary);
  }

  @media (max-width: 480px) {
    padding: 14px 16px;
  }
`

const ChatTitle = styled.h3`
  font-size: 1em;
  color: var(--text);
  font-weight: 400;

  @media (max-width: 480px) {
    font-size: 0.95em;
  }
`

const ChatMessages = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;

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

  @media (max-width: 768px) {
    padding: 16px;
    gap: 12px;
  }

  @media (max-width: 480px) {
    padding: 12px;
    gap: 10px;
  }
`

const Message = styled.div`
  display: flex;
  gap: 12px;
  align-items: flex-start;
  animation: ${slideUp} 0.3s ease-out;

  ${props => props.isUser && `
    flex-direction: row-reverse;
  `}

  @media (max-width: 480px) {
    gap: 8px;
  }
`

const MessageAvatar = styled.div`
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: 50%;
  background: ${props => props.isUser ? 'var(--primary)' : 'linear-gradient(135deg, var(--primary), var(--secondary))'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
  font-size: 0.9em;

  @media (max-width: 480px) {
    width: 32px;
    height: 32px;
    min-width: 32px;
    font-size: 0.85em;
  }
`

const MessageBubble = styled.div`
  background: ${props => props.isUser ? 'var(--primary)' : 'var(--hover-bg)'};
  color: ${props => props.isUser ? 'white' : 'var(--text)'};
  padding: 12px 16px;
  border-radius: ${props => props.isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px'};
  max-width: 70%;
  font-size: 0.9em;
  line-height: 1.5;
  word-wrap: break-word;

  @media (max-width: 768px) {
    max-width: 75%;
    padding: 10px 14px;
    font-size: 0.875em;
  }

  @media (max-width: 480px) {
    max-width: 80%;
    padding: 10px 12px;
    font-size: 0.85em;
  }
`

const ChatInputContainer = styled.div`
  padding: 16px 20px;
  border-top: 1px solid var(--border);
  display: flex;
  gap: 12px;
  background: var(--bg-white);
  border-radius: 0 0 12px 12px;

  @media (max-width: 768px) {
    padding: 14px 16px;
    gap: 10px;
  }

  @media (max-width: 480px) {
    padding: 12px;
    gap: 8px;
  }
`

const ChatInput = styled.input`
  flex: 1;
  padding: 12px 16px;
  background: var(--hover-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  font-size: 0.9em;
  font-family: inherit;
  transition: all 0.2s ease;
  min-height: 44px; /* Better touch target */

  &:focus {
    outline: none;
    border-color: var(--primary);
    background: var(--bg-white);
    box-shadow: 0 0 0 3px rgba(10, 102, 194, 0.1);
  }

  &::placeholder {
    color: var(--text-lighter);
  }

  @media (max-width: 768px) {
    padding: 10px 14px;
    font-size: 0.875em;
    min-height: 42px;
    
    &:focus {
      box-shadow: 0 0 0 2px rgba(10, 102, 194, 0.1);
    }
  }

  @media (max-width: 480px) {
    padding: 10px 12px;
    font-size: 0.85em;
    min-height: 40px;
    border-radius: 6px;
  }
  
  @media (max-width: 360px) {
    padding: 8px 10px;
    font-size: 0.8em;
    min-height: 38px;
  }
`

const SendButton = styled.button`
  padding: 12px 20px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  min-height: 44px; /* Better touch target */
  min-width: 44px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(10, 102, 194, 0.3);
  }

  &:active {
    transform: translateY(0);
  }

  svg {
    width: 18px;
    height: 18px;
  }

  @media (max-width: 768px) {
    padding: 10px 16px;
    font-size: 0.875em;
    min-height: 42px;
    min-width: 42px;
    
    &:hover {
      transform: translateY(-1px);
    }
  }

  @media (max-width: 480px) {
    padding: 10px 14px;
    font-size: 0.85em;
    min-height: 40px;
    min-width: 40px;
    border-radius: 6px;
    
    span {
      display: none;
    }
    
    &:hover {
      transform: none;
    }
  }
  
  @media (max-width: 360px) {
    padding: 8px 12px;
    font-size: 0.8em;
    min-height: 38px;
    min-width: 38px;
    
    svg {
      width: 16px;
      height: 16px;
    }
  }
`

const JobsPanel = styled.div`
  background: var(--bg-white);
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;

  @media (max-width: 768px) {
    border-left: none;
    border-top: 1px solid var(--border);
  }
`

const JobsPanelHeader = styled.div`
  padding: 24px 28px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-white);
  flex-shrink: 0;

  @media (max-width: 768px) {
    padding: 20px 24px;
  }

  @media (max-width: 480px) {
    padding: 16px 20px;
  }
`

const PanelTitle = styled.h2`
  font-size: 1.3em;
  color: var(--text);
  margin-bottom: 8px;
  font-weight: 300;
  display: flex;
  align-items: center;
  gap: 8px;

  svg {
    width: 24px;
    height: 24px;
    color: var(--primary);
  }

  @media (max-width: 480px) {
    font-size: 1.2em;
  }
`

const PanelSubtitle = styled.p`
  font-size: 0.85em;
  color: var(--text-light);

  @media (max-width: 480px) {
    font-size: 0.8em;
  }
`

const JobsList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px 28px;

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

  @media (max-width: 768px) {
    padding: 16px 24px;
    max-height: 400px;
  }

  @media (max-width: 480px) {
    padding: 12px 20px;
  }
`

const JobCard = styled.div`
  background: ${props => props.selected ? 'rgba(10, 102, 194, 0.1)' : 'var(--hover-bg)'};
  border: 1px solid ${props => props.selected ? 'var(--primary)' : 'var(--border)'};
  border-radius: 12px;
  padding: 18px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: ${slideUp} 0.3s ease-out;

  &:hover {
    border-color: var(--primary);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(10, 102, 194, 0.2);
  }

  @media (max-width: 768px) {
    padding: 16px;
    margin-bottom: 12px;
  }

  @media (max-width: 480px) {
    padding: 14px;
  }
`

const JobHeader = styled.div`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12px;
`

const JobTitle = styled.h3`
  font-size: 1em;
  color: var(--text);
  margin-bottom: 4px;
  font-weight: 400;

  @media (max-width: 480px) {
    font-size: 0.95em;
  }
`

const JobCompany = styled.p`
  font-size: 0.85em;
  color: var(--text-light);
  margin-bottom: 8px;

  @media (max-width: 480px) {
    font-size: 0.8em;
  }
`

const JobDetails = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
`

const JobTag = styled.span`
  font-size: 0.75em;
  padding: 4px 10px;
  background: rgba(10, 102, 194, 0.1);
  color: var(--primary);
  border-radius: 12px;
  font-weight: 400;

  @media (max-width: 480px) {
    font-size: 0.7em;
    padding: 3px 8px;
  }
`

const AIBadge = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.7em;
  padding: 4px 8px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border-radius: 10px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;

  svg {
    width: 12px;
    height: 12px;
  }

  @media (max-width: 480px) {
    font-size: 0.65em;
    padding: 3px 6px;
  }
`

const MatchScore = styled.div`
  font-size: 0.85em;
  color: var(--primary);
  font-weight: 500;

  @media (max-width: 480px) {
    font-size: 0.8em;
  }
`

const AIInterviews = () => {
  const [selectedJob, setSelectedJob] = useState(null)
  const [interviews, setInterviews] = useState([])
  const [selectedInterview, setSelectedInterview] = useState(null)
  const [interviewResults, setInterviewResults] = useState(null)
  const [rizFeedback, setRizFeedback] = useState(null)
  const [loadingInterviews, setLoadingInterviews] = useState(true)
  const [recommendedJobs, setRecommendedJobs] = useState([])
  const [loadingJobs, setLoadingJobs] = useState(true)
  const { user } = useAuth()
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [isCameraOff, setIsCameraOff] = useState(false)
  const [isScreenSharing, setIsScreenSharing] = useState(false)
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const videoRef = useRef(null)
  const messagesEndRef = useRef(null)
  const navigate = useNavigate()
  const { logout } = useAuth()

  // Fetch interview history and recommendations on mount
  useEffect(() => {
    fetchInterviews()
    fetchInterviewRecommendations()
  }, [])

  // Fetch interview recommendations (jobs with attempt counts)
  const fetchInterviewRecommendations = async () => {
    if (!user?.id) return
    
    setLoadingJobs(true)
    try {
      const res = await jobAPI.getInterviewRecommendations(user.id, 10)
      setRecommendedJobs(res.data?.recommendations || [])
    } catch (err) {
      console.error('Failed to fetch interview recommendations:', err)
      setRecommendedJobs([])
    } finally {
      setLoadingJobs(false)
    }
  }

  // Fetch interview details and Riz feedback when interview is selected
  useEffect(() => {
    if (selectedInterview) {
      fetchInterviewDetails()
    }
  }, [selectedInterview])

  const fetchInterviews = async () => {
    try {
      setLoadingInterviews(true)
      const response = await interviewAPI.getMyInterviews()
      if (response.data && response.data.interviews) {
        setInterviews(response.data.interviews)
      }
    } catch (err) {
      console.error('Error fetching interviews:', err)
    } finally {
      setLoadingInterviews(false)
    }
  }

  const fetchInterviewDetails = async () => {
    if (!selectedInterview) return
    
    try {
      // Fetch interview details
      const interviewRes = await interviewAPI.getInterview(selectedInterview.interview_id)
      if (interviewRes.data) {
        setInterviewResults(interviewRes.data)
        
        // If interview is completed, fetch Riz feedback
        if (interviewRes.data.status === 'completed') {
          try {
            const rizRes = await interviewAPI.getInterviewRizFeedback(selectedInterview.interview_id)
            if (rizRes.data && rizRes.data.riz_feedback) {
              setRizFeedback(rizRes.data.riz_feedback)
            }
          } catch (err) {
            // Riz feedback might not be available yet
            console.log('Riz feedback not available:', err)
          }
        }
      }
    } catch (err) {
      console.error('Error fetching interview details:', err)
    }
  }

  // Use recommended jobs from API, fallback to empty array
  const jobs = recommendedJobs.length > 0 
    ? recommendedJobs.map(job => ({
        id: job.job_id,
        job_id: job.job_id,
        title: job.title,
        company: job.company_name || 'Company',
        location: job.location || 'Location not specified',
        type: job.job_type || 'Full-time',
        experience: job.experience_level || 'Not specified',
        matchScore: job.composite_score ? Math.round(job.composite_score * 100) : null,
        composite_score: job.composite_score,
        attempt_count: job.attempt_count || 0,
        best_score: job.best_score
      }))
    : []

  const handleJobSelect = (job) => {
    setSelectedJob(job)
    if (videoRef.current) {
      videoRef.current.currentTime = 0
    }
    // Initialize chat with AI greeting
    const companyName = job.company_name || job.company || 'the company'
    setMessages([
      {
        id: 1,
        text: `Hello! Welcome to your AI mock interview for the ${job.title} position at ${companyName}. I'm your AI interviewer today. Are you ready to begin?`,
        isUser: false,
        timestamp: new Date()
      }
    ])
  }

  const handleBackToFeed = () => {
    navigate('/feed')
  }

  const handleStartInterview = () => {
    if (videoRef.current && selectedJob) {
      videoRef.current.play()
      setIsPlaying(true)
    } else if (!selectedJob) {
      alert('Please select a job from the right panel first')
    }
  }

  const toggleMute = () => {
    setIsMuted(!isMuted)
  }

  const toggleCamera = () => {
    setIsCameraOff(!isCameraOff)
  }

  const toggleScreenShare = () => {
    setIsScreenSharing(!isScreenSharing)
  }

  const handleEndCall = () => {
    if (videoRef.current) {
      videoRef.current.pause()
      setIsPlaying(false)
    }
  }

  const handleSendMessage = () => {
    if (!inputMessage.trim() || !selectedJob) return

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      text: inputMessage,
      isUser: true,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')

    // Simulate AI response after a delay
    setTimeout(() => {
      const aiResponse = {
        id: messages.length + 2,
        text: "That's a great question! Let me elaborate on that. In a real interview scenario, the interviewer would provide detailed feedback and follow-up questions based on your response.",
        isUser: false,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiResponse])
      
      // Scroll to bottom
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
      }
    }, 1000)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage()
    }
  }

  return (
    <Container>
      <Navbar />

      <MainContainer>
        <VideoPanel>
          <DescriptionBanner>
            <BannerTitle>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                <line x1="12" y1="19" x2="12" y2="23"></line>
                <line x1="8" y1="23" x2="16" y2="23"></line>
              </svg>
              AI-Powered Mock Interview Platform
            </BannerTitle>
            <BannerDescription>
              <strong className="banner-description-strong">Boost Your Confidence</strong> with our intelligent AI interviewer that adapts to your selected role. 
              Choose a job position from the recommended list on the right, and our AI will conduct a realistic 
              mock interview tailored to that specific role. Engage in real-time conversation through the chat 
              interface, receive personalized questions, and get instant feedback to perfect your responses. 
              Practice until you're ready to ace your next real interview with AI-powered sessions designed to 
              help you succeed.
            </BannerDescription>
          </DescriptionBanner>

          <VideoContainer>
            <Video
              ref={videoRef}
            >
              <source src="/static/video.mp4" type="video/mp4" />
              Your browser does not support the video tag.
            </Video>
          </VideoContainer>

          <CallControls>
            <CallButtonWrapper>
              <StartButton onClick={handleStartInterview}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
              </StartButton>
              <CallButtonLabel>Start</CallButtonLabel>
            </CallButtonWrapper>

            <CallButtonWrapper>
              <CallButton active={isMuted} onClick={toggleMute}>
                {isMuted ? (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="1" y1="1" x2="23" y2="23"></line>
                    <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"></path>
                    <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"></path>
                    <line x1="12" y1="19" x2="12" y2="23"></line>
                    <line x1="8" y1="23" x2="16" y2="23"></line>
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                    <line x1="12" y1="19" x2="12" y2="23"></line>
                    <line x1="8" y1="23" x2="16" y2="23"></line>
                  </svg>
                )}
              </CallButton>
              <CallButtonLabel>{isMuted ? 'Unmute' : 'Mute'}</CallButtonLabel>
            </CallButtonWrapper>

            <CallButtonWrapper>
              <CallButton active={isCameraOff} onClick={toggleCamera}>
                {isCameraOff ? (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="1" y1="1" x2="23" y2="23"></line>
                    <path d="M21 21H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h3m3-3h6l2 3h4a2 2 0 0 1 2 2v9.34m-7.72-2.06a4 4 0 1 1-5.56-5.56"></path>
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
                    <circle cx="12" cy="13" r="4"></circle>
                  </svg>
                )}
              </CallButton>
              <CallButtonLabel>{isCameraOff ? 'Camera Off' : 'Camera On'}</CallButtonLabel>
            </CallButtonWrapper>

            <CallButtonWrapper>
              <CallButton active={isScreenSharing} onClick={toggleScreenShare}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
                  <line x1="8" y1="21" x2="16" y2="21"></line>
                  <line x1="12" y1="17" x2="12" y2="21"></line>
                  {isScreenSharing && (
                    <path d="M7 11l5 5 5-5"></path>
                  )}
                </svg>
              </CallButton>
              <CallButtonLabel>{isScreenSharing ? 'Stop Share' : 'Share'}</CallButtonLabel>
            </CallButtonWrapper>

            <CallButtonWrapper>
              <EndCallButton onClick={handleEndCall}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M10.68 13.31a16 16 0 0 0 3.41 2.6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7 2 2 0 0 1 1.72 2v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.42 19.42 0 0 1-3.33-2.67m-2.67-3.34a19.79 19.79 0 0 1-3.07-8.63A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91"></path>
                  <line x1="23" y1="1" x2="1" y2="23"></line>
                </svg>
              </EndCallButton>
              <CallButtonLabel>End</CallButtonLabel>
            </CallButtonWrapper>
          </CallControls>

          {selectedJob && (
            <ChatPanel>
              <ChatHeader>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <ChatTitle>Interview Chat - {selectedJob.title}</ChatTitle>
              </ChatHeader>
              
              <ChatMessages>
                {messages.map((message) => (
                  <Message key={message.id} isUser={message.isUser}>
                    <MessageAvatar isUser={message.isUser}>
                      {message.isUser ? 'You' : 'AI'}
                    </MessageAvatar>
                    <MessageBubble isUser={message.isUser}>
                      {message.text}
                    </MessageBubble>
                  </Message>
                ))}
                <div ref={messagesEndRef} />
              </ChatMessages>
              
              <ChatInputContainer>
                <ChatInput
                  type="text"
                  placeholder="Type your response..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                />
                <SendButton onClick={handleSendMessage}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13"></line>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                  </svg>
                  <span>Send</span>
                </SendButton>
              </ChatInputContainer>
            </ChatPanel>
          )}
        </VideoPanel>

        <JobsPanel>
          <JobsPanelHeader>
            <PanelTitle>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 3v3"></path>
                <path d="M12 18v3"></path>
                <path d="M5.5 5.5l2.1 2.1"></path>
                <path d="M16.4 16.4l2.1 2.1"></path>
                <path d="M3 12h3"></path>
                <path d="M18 12h3"></path>
                <path d="M5.5 18.5l2.1-2.1"></path>
                <path d="M16.4 7.6l2.1-2.1"></path>
                <circle cx="12" cy="12" r="3"></circle>
              </svg>
              Interview History
            </PanelTitle>
            <PanelSubtitle>Your past interviews and results</PanelSubtitle>
          </JobsPanelHeader>

          {loadingInterviews ? (
            <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-light)' }}>
              Loading interviews...
            </div>
          ) : interviews.length > 0 ? (
            <JobsList>
              {interviews.map((interview) => (
                <JobCard
                  key={interview.interview_id}
                  selected={selectedInterview?.interview_id === interview.interview_id}
                  onClick={() => setSelectedInterview(interview)}
                >
                  <JobHeader>
                    <div style={{ flex: 1 }}>
                      <JobTitle>{interview.job_title || 'Interview'}</JobTitle>
                      <JobCompany>{interview.company_name || 'Company'}</JobCompany>
                    </div>
                    {interview.overall_score !== null && (
                      <AIBadge>
                        {interview.overall_score}/100
                      </AIBadge>
                    )}
                  </JobHeader>
                  <JobDetails>
                    <JobTag>Status: {interview.status}</JobTag>
                    {interview.attempt_number && <JobTag>Attempt #{interview.attempt_number}</JobTag>}
                    {interview.completed_at && (
                      <JobTag>Completed: {new Date(interview.completed_at).toLocaleDateString()}</JobTag>
                    )}
                  </JobDetails>
                  {interview.status === 'completed' && interviewResults && interviewResults.interview_id === interview.interview_id && (
                    <div style={{ marginTop: '12px', padding: '12px', background: 'rgba(10, 102, 194, 0.1)', borderRadius: '8px' }}>
                      {interviewResults.score_breakdown && (
                        <div style={{ fontSize: '0.85em', marginBottom: '8px' }}>
                          <div>Technical: {interviewResults.score_breakdown.technical_score}/100</div>
                          <div>Communication: {interviewResults.score_breakdown.communication_score}/100</div>
                          <div>Problem Solving: {interviewResults.score_breakdown.problem_solving_score}/100</div>
                        </div>
                      )}
                      {rizFeedback && (
                        <div style={{ marginTop: '8px', fontSize: '0.85em' }}>
                          <strong>Riz Feedback:</strong>
                          <div style={{ marginTop: '4px', fontStyle: 'italic' }}>
                            {rizFeedback.summary || 'No summary available'}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </JobCard>
              ))}
            </JobsList>
          ) : (
            <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-light)' }}>
              No interview history. Start a new interview to begin!
            </div>
          )}

          {/* Recommended Jobs for Interviews */}
          <div style={{ marginTop: '30px', paddingTop: '20px', borderTop: '1px solid var(--border)' }}>
            <PanelSubtitle style={{ marginBottom: '12px' }}>
              {loadingJobs ? 'Loading Recommendations...' : 'Recommended Jobs for Practice'}
            </PanelSubtitle>
            <JobsList>
              {loadingJobs ? (
                <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-light)' }}>
                  Loading personalized job recommendations...
                </div>
              ) : jobs.length > 0 ? (
                jobs.map((job) => (
                  <JobCard
                    key={job.job_id || job.id}
                    selected={selectedJob?.job_id === job.job_id || selectedJob?.id === job.id}
                    onClick={() => handleJobSelect(job)}
                  >
                    <JobHeader>
                      <div style={{ flex: 1 }}>
                        <JobTitle>{job.title}</JobTitle>
                        <JobCompany>{job.company_name || job.company || 'Company'}</JobCompany>
                      </div>
                      {job.matchScore && (
                        <AIBadge>
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M12 3v3"></path>
                            <path d="M12 18v3"></path>
                            <path d="M5.5 5.5l2.1 2.1"></path>
                            <path d="M16.4 16.4l2.1 2.1"></path>
                            <path d="M3 12h3"></path>
                            <path d="M18 12h3"></path>
                            <path d="M5.5 18.5l2.1-2.1"></path>
                            <path d="M16.4 7.6l2.1-2.1"></path>
                            <circle cx="12" cy="12" r="3"></circle>
                          </svg>
                          {job.matchScore}%
                        </AIBadge>
                      )}
                    </JobHeader>
                    <JobDetails>
                      <JobTag>📍 {job.location || 'Location not specified'}</JobTag>
                      <JobTag>💼 {job.job_type || job.type || 'Full-time'}</JobTag>
                      {job.experience_level && (
                        <JobTag>⏱️ {job.experience_level}</JobTag>
                      )}
                      {job.attempt_count > 0 && (
                        <JobTag style={{ background: 'rgba(10, 102, 194, 0.1)', color: 'var(--primary)' }}>
                          🔄 Attempt {job.attempt_count + 1}
                        </JobTag>
                      )}
                      {job.best_score && (
                        <JobTag style={{ background: 'rgba(34, 197, 94, 0.1)', color: '#22c55e' }}>
                          ⭐ Best: {job.best_score}%
                        </JobTag>
                      )}
                    </JobDetails>
                  </JobCard>
                ))
              ) : (
                <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-light)' }}>
                  No job recommendations available. Update your profile to get personalized recommendations!
                </div>
              )}
            </JobsList>
          </div>
        </JobsPanel>
      </MainContainer>
    </Container>
  )
}

export default AIInterviews

