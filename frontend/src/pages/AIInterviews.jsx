import React, { useState, useRef, useEffect, useMemo } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useAccessDeniedModal } from '../contexts/AccessDeniedModalContext'
import { interviewAPI, jobAPI, userAPI } from '../services/api'
import Navbar from '../components/Navbar'
import '../css/pages/AIInterviews.css'

function formatInterviewDuration(seconds) {
  const total = Number(seconds)
  if (!Number.isFinite(total) || total <= 0) return '5 minutes'
  if (total < 60) return `${Math.round(total)} seconds`
  const minutes = Math.round(total / 60)
  return minutes === 1 ? '1 minute' : `${minutes} minutes`
}

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

const SIDE_PANEL_WIDTH_KEY = 'aiInterviewsSidePanelWidth'
const MIN_SIDE_PANEL_WIDTH = 300
const MAX_SIDE_PANEL_WIDTH = 640
const DEFAULT_SIDE_PANEL_WIDTH = 450

const MainContainer = styled.div`
  width: 100%;
  max-width: 100%;
  min-height: calc(100vh - 80px);
  margin: 0;
  display: flex;
  align-items: stretch;
  background: var(--bg-light);

  @media (max-width: 768px) {
    flex-direction: column;
    height: auto;
    min-height: calc(100vh - 80px);
  }
`

const MainContent = styled.div`
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
`

const SidePanelsColumn = styled.aside`
  width: ${props => props.$width}px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background: var(--bg-light);
  border-left: 1px solid var(--border);
  height: calc(100vh - 80px);
  max-height: calc(100vh - 80px);
  overflow: hidden;

  @media (max-width: 768px) {
    width: 100%;
    height: auto;
    max-height: none;
    border-left: none;
    padding: 16px;
    gap: 20px;
  }
`

const VideoPanel = styled.div`
  background: var(--bg-light);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 30px 24px;
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
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 24px 28px;
  margin-bottom: 30px;
  box-shadow: var(--shadow);
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
  color: var(--text);
  margin-bottom: 12px;
  font-weight: 400;
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
  color: var(--text-light);
  line-height: 1.6;
  font-weight: 400;

  @media (max-width: 768px) {
    font-size: 0.9em;
  }

  @media (max-width: 480px) {
    font-size: 0.85em;
    line-height: 1.5;
  }
`

const InterviewRoomCard = styled.div`
  width: 100%;
  max-width: 900px;
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 40px 32px;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 20px;
  min-height: 280px;
  justify-content: center;

  @media (max-width: 768px) {
    border-radius: 12px;
    padding: 32px 24px;
    min-height: 240px;
  }

  @media (max-width: 480px) {
    padding: 24px 18px;
    gap: 16px;
  }
`

const RoomIconWrap = styled.div`
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(21, 133, 161, 0.1);
  border: 1px solid rgba(21, 133, 161, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);

  svg {
    width: 34px;
    height: 34px;
  }
`

const RoomCardTitle = styled.h3`
  font-size: 1.25em;
  font-weight: 500;
  color: var(--text);
  margin: 0;
  line-height: 1.4;

  @media (max-width: 480px) {
    font-size: 1.1em;
  }
`

const RoomCardDescription = styled.p`
  font-size: 0.95em;
  color: var(--text-light);
  line-height: 1.6;
  margin: 0;
  max-width: 560px;
  font-weight: 400;

  @media (max-width: 480px) {
    font-size: 0.88em;
  }
`

const RoomDurationNote = styled.p`
  font-size: 0.88em;
  color: var(--primary);
  line-height: 1.5;
  margin: 10px 0 0;
  max-width: 560px;
  font-weight: 500;

  @media (max-width: 480px) {
    font-size: 0.82em;
  }
`

const JoinInterviewButton = styled.a`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 14px 28px;
  background: var(--primary);
  color: white;
  border-radius: 10px;
  font-size: 1em;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.25s ease;
  margin-top: 4px;

  svg {
    width: 20px;
    height: 20px;
  }

  &:hover {
    background: var(--primary-dark);
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(21, 133, 161, 0.25);
    color: white;
  }

  @media (max-width: 480px) {
    width: 100%;
    padding: 14px 20px;
  }
`

const RoomLinkBox = styled.div`
  width: 100%;
  max-width: 640px;
  display: flex;
  align-items: stretch;
  gap: 8px;
  margin-top: 4px;

  @media (max-width: 600px) {
    flex-direction: column;
  }
`

const RoomLinkInput = styled.input`
  flex: 1;
  min-width: 0;
  padding: 12px 14px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--hover-bg);
  color: var(--text);
  font-size: 0.85em;
  font-family: var(--font-mono);

  &:focus {
    outline: none;
    border-color: var(--primary);
    background: var(--bg-white);
    box-shadow: 0 0 0 3px rgba(21, 133, 161, 0.1);
  }
`

const CopyLinkButton = styled.button`
  padding: 12px 18px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-white);
  color: var(--text);
  font-size: 0.88em;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;

  &:hover {
    background: var(--hover-bg);
    border-color: var(--primary);
    color: var(--primary);
  }
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
    box-shadow: 0 4px 12px rgba(21, 133, 161, 0.2);
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

const TranscriptPanel = styled.div`
  background: var(--bg-white);
  margin-top: 20px;
  width: 100%;
  max-width: 900px;
  border-radius: 16px;
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  height: 420px;

  @media (max-width: 1024px) {
    height: 400px;
    margin-top: 18px;
  }

  @media (max-width: 768px) {
    margin-top: 16px;
    height: 380px;
    border-radius: 12px;
  }

  @media (max-width: 480px) {
    margin-top: 12px;
    height: 340px;
    border-radius: 10px;
  }
`

const TranscriptHeader = styled.div`
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--hover-bg);
  border-radius: 16px 16px 0 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;

  svg {
    width: 20px;
    height: 20px;
    color: var(--primary);
    flex-shrink: 0;
  }

  @media (max-width: 480px) {
    padding: 14px 16px;
    flex-direction: column;
    align-items: flex-start;
  }
`

const TranscriptHeaderMain = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
`

const TranscriptTitle = styled.h3`
  font-size: 1em;
  color: var(--text);
  font-weight: 500;
  margin: 0;

  @media (max-width: 480px) {
    font-size: 0.95em;
  }
`

const TranscriptSubtitle = styled.p`
  font-size: 0.8em;
  color: var(--text-light);
  margin: 0;
`

const TranscriptRefreshButton = styled.button`
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg-white);
  color: var(--text-light);
  font-size: 0.78em;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    border-color: var(--primary);
    color: var(--primary);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`

const TranscriptBody = styled.div`
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
    gap: 14px;
  }

  @media (max-width: 480px) {
    padding: 12px;
    gap: 12px;
  }
`

const TranscriptEmptyState = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 32px 24px;
  color: var(--text-light);
  gap: 8px;

  p {
    margin: 0;
    font-size: 0.9em;
    line-height: 1.6;
    max-width: 420px;
  }
`

const SidePanel = styled.section`
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: var(--shadow);
  overflow: hidden;

  @media (max-width: 768px) {
    flex: none;
    min-height: 380px;
  }

  @media (max-width: 480px) {
    min-height: 340px;
    border-radius: 12px;
  }
`

const SidePanelHeader = styled.div`
  padding: 20px 22px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-white);
  flex-shrink: 0;

  @media (max-width: 480px) {
    padding: 16px 18px;
  }
`

const SidePanelList = styled.div`
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px 20px;

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

  @media (max-width: 480px) {
    padding: 12px 16px;
  }
`

const EmptyState = styled.div`
  padding: 24px 16px;
  text-align: center;
  color: var(--text-light);
  font-size: 0.9em;
  line-height: 1.5;
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

const JobCard = styled.div`
  background: ${props => props.selected ? 'rgba(21, 133, 161, 0.1)' : 'var(--hover-bg)'};
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
    box-shadow: 0 4px 12px rgba(21, 133, 161, 0.2);
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
  background: rgba(21, 133, 161, 0.1);
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

const ResultsContainer = styled.div`
  margin-top: 12px;
  padding: 12px;
  background: rgba(21, 133, 161, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(21, 133, 161, 0.2);
  animation: ${slideUp} 0.3s ease-out;
`

const RizFeedbackContainer = styled.div`
  margin-top: 12px;
  padding: 10px;
  background: rgba(21, 133, 161, 0.05);
  border-radius: 6px;
  border: 1px solid rgba(21, 133, 161, 0.2);
`

const RefreshButton = styled.button`
  font-size: 0.75em;
  padding: 4px 8px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--secondary);
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
`

const AIInterviews = () => {
  const { showAccessDeniedModal } = useAccessDeniedModal()
  const [selectedJob, setSelectedJob] = useState(null)
  const [interviews, setInterviews] = useState([])
  const [selectedInterview, setSelectedInterview] = useState(null)
  const [interviewResults, setInterviewResults] = useState(null)
  const [rizFeedback, setRizFeedback] = useState(null)
  const [loadingInterviews, setLoadingInterviews] = useState(true)
  const [recommendedJobs, setRecommendedJobs] = useState([])
  const [loadingJobs, setLoadingJobs] = useState(true)
  const { user } = useAuth()
  const [transcriptItems, setTranscriptItems] = useState([])
  const [loadingTranscript, setLoadingTranscript] = useState(false)
  const [refreshingTranscript, setRefreshingTranscript] = useState(false)
  const [transcriptSource, setTranscriptSource] = useState(null)
  const [transcriptHint, setTranscriptHint] = useState(null)
  const [transcriptUserTurnCount, setTranscriptUserTurnCount] = useState(0)
  const [interviewMaxDurationSeconds, setInterviewMaxDurationSeconds] = useState(300)
  const [sidePanelWidth, setSidePanelWidth] = useState(() => {
    try {
      const saved = localStorage.getItem(SIDE_PANEL_WIDTH_KEY)
      const parsed = saved ? parseInt(saved, 10) : DEFAULT_SIDE_PANEL_WIDTH
      if (!Number.isFinite(parsed)) return DEFAULT_SIDE_PANEL_WIDTH
      return Math.min(MAX_SIDE_PANEL_WIDTH, Math.max(MIN_SIDE_PANEL_WIDTH, parsed))
    } catch {
      return DEFAULT_SIDE_PANEL_WIDTH
    }
  })
  const [isResizingPanel, setIsResizingPanel] = useState(false)
  const sidePanelWidthRef = useRef(sidePanelWidth)
  const isResizingRef = useRef(false)
  const [currentInterview, setCurrentInterview] = useState(null)
  const [startingInterview, setStartingInterview] = useState(false)
  const [completingInterview, setCompletingInterview] = useState(false)
  const [tavusConversationId, setTavusConversationId] = useState(null)
  const [tavusConversationUrl, setTavusConversationUrl] = useState(null)
  const [tavusMeetingToken, setTavusMeetingToken] = useState(null)
  const [linkCopied, setLinkCopied] = useState(false)
  const transcriptEndRef = useRef(null)
  const copyLinkTimeoutRef = useRef(null)
  const navigate = useNavigate()
  const { logout } = useAuth()

  const tavusEmbedSrc = useMemo(() => {
    if (!tavusConversationUrl) return null
    if (!tavusMeetingToken) return tavusConversationUrl
    const sep = tavusConversationUrl.includes('?') ? '&' : '?'
    return `${tavusConversationUrl}${sep}t=${encodeURIComponent(tavusMeetingToken)}`
  }, [tavusConversationUrl, tavusMeetingToken])

  const interviewDurationLabel = useMemo(
    () => formatInterviewDuration(interviewMaxDurationSeconds),
    [interviewMaxDurationSeconds]
  )

  useEffect(() => {
    return () => {
      if (copyLinkTimeoutRef.current) {
        clearTimeout(copyLinkTimeoutRef.current)
      }
    }
  }, [])

  const handleCopyRoomLink = async () => {
    if (!tavusEmbedSrc) return
    try {
      await navigator.clipboard.writeText(tavusEmbedSrc)
      setLinkCopied(true)
      if (copyLinkTimeoutRef.current) {
        clearTimeout(copyLinkTimeoutRef.current)
      }
      copyLinkTimeoutRef.current = setTimeout(() => setLinkCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy interview link:', err)
    }
  }

  // Fetch interview history and recommendations on mount
  useEffect(() => {
    fetchInterviews()
    fetchInterviewRecommendations()
    fetchInterviewSessionLimits()
  }, [])

  const fetchInterviewSessionLimits = async () => {
    try {
      const res = await userAPI.getSubscriptionUsage()
      const seconds = res.data?.plan?.interview_max_duration_seconds
      if (Number.isFinite(seconds) && seconds > 0) {
        setInterviewMaxDurationSeconds(seconds)
      }
    } catch (err) {
      console.error('Failed to fetch interview session duration:', err)
    }
  }

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

  const fetchTranscript = async (interviewId, { background = false } = {}) => {
    if (!interviewId) return

    try {
      if (background) {
        setRefreshingTranscript(true)
      } else {
        setLoadingTranscript(true)
      }
      const response = await interviewAPI.getInterviewTranscript(interviewId)
      if (response.data) {
        setTranscriptItems(response.data.items || [])
        setTranscriptSource(response.data.source || null)
        setTranscriptHint(response.data.hint || null)
        setTranscriptUserTurnCount(response.data.user_turn_count ?? 0)
      }
    } catch (err) {
      console.error('Error fetching interview transcript:', err)
      setTranscriptItems([])
      setTranscriptSource(null)
      setTranscriptHint(null)
      setTranscriptUserTurnCount(0)
    } finally {
      setLoadingTranscript(false)
      setRefreshingTranscript(false)
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
    setCurrentInterview(null)
    setTavusConversationId(null)
    setTavusConversationUrl(null)
    setTavusMeetingToken(null)
    setInterviewResults(null)
    setRizFeedback(null)
    setLinkCopied(false)
    setTranscriptItems([])
    setTranscriptSource(null)
    setTranscriptHint(null)
    setTranscriptUserTurnCount(0)
  }

  const handleBackToFeed = () => {
    navigate('/feed')
  }

  const handleStartInterview = async () => {
    if (!selectedJob) {
      alert('Please select a job from the right panel first')
      return
    }

    if (currentInterview) {
      alert('An interview is already in progress. Please complete it first.')
      return
    }

    try {
      setStartingInterview(true)
      const response = await interviewAPI.startInterview(selectedJob.job_id || selectedJob.id)
      
      if (response.data) {
        const interview = response.data
        setCurrentInterview(interview)
        setTavusConversationId(interview.tavus_conversation_id)
        setTavusConversationUrl(interview.tavus_conversation_url || null)
        setTavusMeetingToken(interview.tavus_meeting_token || null)
        await fetchTranscript(interview.interview_id)
        
        // Refresh interview list
        await fetchInterviews()
      }
    } catch (err) {
      console.error('Error starting interview:', err)
      const errorDetail = err.response?.data?.detail || err.message || 'Failed to start interview'
      
      // Handle quota exceeded (403) from server-side subscription check
      if (err.response?.status === 403) {
        showAccessDeniedModal(err)
      } else if (err.response?.status === 429) {
        // Handle rate limiting
        const retryAfter = err.response?.headers?.['retry-after'] || 60
        const remaining = err.response?.data?.remaining || 0
        alert(`Rate limit exceeded. Please wait ${retryAfter} seconds before starting another interview.\n\nRemaining requests: ${remaining}`)
      } else {
        const msg = typeof errorDetail === 'string' ? errorDetail : (errorDetail?.message || 'Failed to start interview')
        alert(`Error starting interview: ${msg}`)
      }
    } finally {
      setStartingInterview(false)
    }
  }

  const handleCompleteInterview = async () => {
    if (!currentInterview) {
      alert('No interview in progress. Please start an interview first.')
      return
    }

    if (currentInterview.status === 'completed') {
      alert('This interview has already been completed.')
      return
    }

    const confirmComplete = window.confirm(
      'Are you sure you want to complete this interview? This will analyze your responses and generate feedback.'
    )

    if (!confirmComplete) return

    try {
      setCompletingInterview(true)
      const response = await interviewAPI.completeInterview(currentInterview.interview_id)
      
      if (response.data) {
        const results = response.data
        setInterviewResults(results)
        setCurrentInterview({ ...currentInterview, status: 'completed' })
        
        // Fetch Riz feedback if available
        if (results.riz_feedback) {
          setRizFeedback(results.riz_feedback)
        } else {
          // Try to fetch Riz feedback separately
          try {
            const rizRes = await interviewAPI.getInterviewRizFeedback(currentInterview.interview_id)
            if (rizRes.data?.riz_feedback) {
              setRizFeedback(rizRes.data.riz_feedback)
            }
          } catch (err) {
            console.log('Riz feedback not available yet:', err)
          }
        }
        
        // Show results
        let resultMessage = `Interview completed!\n\n`
        resultMessage += `Overall Score: ${results.overall_score}/100\n\n`
        
        if (results.score_breakdown) {
          resultMessage += `Score Breakdown:\n`
          resultMessage += `- Technical: ${results.score_breakdown.technical_score}/100\n`
          resultMessage += `- Communication: ${results.score_breakdown.communication_score}/100\n`
          resultMessage += `- Problem Solving: ${results.score_breakdown.problem_solving_score}/100\n`
          resultMessage += `- Domain Knowledge: ${results.score_breakdown.domain_knowledge_score}/100\n\n`
        }
        
        if (results.strengths && results.strengths.length > 0) {
          resultMessage += `Strengths:\n${results.strengths.map(s => `- ${s}`).join('\n')}\n\n`
        }
        
        if (results.weaknesses && results.weaknesses.length > 0) {
          resultMessage += `Areas for Improvement:\n${results.weaknesses.map(w => `- ${w}`).join('\n')}\n\n`
        }
        
        if (results.riz_feedback) {
          resultMessage += `\nRiz Coaching Feedback is available below!`
        }
        
        alert(resultMessage)
        
        // Refresh interview list
        await fetchInterviews()
        await fetchTranscript(currentInterview.interview_id)
        setTavusConversationUrl(null)
        setTavusMeetingToken(null)
      }
    } catch (err) {
      console.error('Error completing interview:', err)
      const errorDetail = err.response?.data?.detail || err.message || 'Failed to complete interview'
      
      // Handle rate limiting
      if (err.response?.status === 429) {
        const retryAfter = err.response?.headers?.['retry-after'] || 60
        const remaining = err.response?.data?.remaining || 0
        alert(`Rate limit exceeded. Please wait ${retryAfter} seconds before completing another interview.\n\nRemaining requests: ${remaining}`)
      } else {
        alert(`Error completing interview: ${errorDetail}`)
      }
    } finally {
      setCompletingInterview(false)
    }
  }

  const handleRefreshRizFeedback = async () => {
    if (!currentInterview || currentInterview.status !== 'completed') {
      alert('Interview must be completed before refreshing Riz feedback.')
      return
    }

    try {
      const response = await interviewAPI.refreshRizFeedback(currentInterview.interview_id)
      
      if (response.data?.riz_feedback) {
        setRizFeedback(response.data.riz_feedback)
        alert('Riz feedback refreshed successfully!')
      }
    } catch (err) {
      console.error('Error refreshing Riz feedback:', err)
      const errorDetail = err.response?.data?.detail || err.message || 'Failed to refresh Riz feedback'
      
      // Handle rate limiting
      if (err.response?.status === 429) {
        const retryAfter = err.response?.headers?.['retry-after'] || 60
        alert(`Rate limit exceeded. Please wait ${retryAfter} seconds before refreshing again.`)
      } else {
        alert(`Error refreshing Riz feedback: ${errorDetail}`)
      }
    }
  }

  useEffect(() => {
    sidePanelWidthRef.current = sidePanelWidth
  }, [sidePanelWidth])

  useEffect(() => {
    const handleMouseMove = (event) => {
      if (!isResizingRef.current) return
      const nextWidth = window.innerWidth - event.clientX
      const clamped = Math.min(
        MAX_SIDE_PANEL_WIDTH,
        Math.max(MIN_SIDE_PANEL_WIDTH, nextWidth)
      )
      sidePanelWidthRef.current = clamped
      setSidePanelWidth(clamped)
    }

    const handleMouseUp = () => {
      if (!isResizingRef.current) return
      isResizingRef.current = false
      setIsResizingPanel(false)
      try {
        localStorage.setItem(SIDE_PANEL_WIDTH_KEY, String(sidePanelWidthRef.current))
      } catch {
        /* ignore storage errors */
      }
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseup', handleMouseUp)
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }
  }, [])

  const handleResizeStart = (event) => {
    if (window.innerWidth <= 768) return
    event.preventDefault()
    isResizingRef.current = true
    setIsResizingPanel(true)
  }

  useEffect(() => {
    sidePanelWidthRef.current = sidePanelWidth
  }, [sidePanelWidth])

  useEffect(() => {
    document.body.classList.toggle('ai-interviews-resizing', isResizingPanel)
    return () => {
      document.body.classList.remove('ai-interviews-resizing')
    }
  }, [isResizingPanel])

  useEffect(() => {
    if (!currentInterview?.interview_id) {
      setTranscriptItems([])
      setTranscriptSource(null)
      setTranscriptHint(null)
      setTranscriptUserTurnCount(0)
      return
    }

    fetchTranscript(currentInterview.interview_id)

    if (currentInterview.status === 'in_progress') {
      const intervalId = setInterval(() => {
        fetchTranscript(currentInterview.interview_id, { background: true })
      }, 30000)
      return () => clearInterval(intervalId)
    }
  }, [currentInterview?.interview_id, currentInterview?.status])

  useEffect(() => {
    if (transcriptEndRef.current) {
      transcriptEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [transcriptItems.length, loadingTranscript])

  return (
    <Container>
      <Navbar />

      <MainContainer>
        <MainContent>
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
              mock interview tailored to that specific role. Complete your session in the Tavus room,
              then review your question-wise transcript and feedback here.
              Practice until you're ready to ace your next real interview with AI-powered sessions designed to 
              help you succeed.
            </BannerDescription>
          </DescriptionBanner>

          <InterviewRoomCard>
            {tavusEmbedSrc ? (
              <>
                <RoomIconWrap>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M15 10l4.553-2.276A1 1 0 0 1 21 8.618v6.764a1 1 0 0 1-1.447.894L15 14"></path>
                    <rect x="3" y="6" width="12" height="12" rx="2" ry="2"></rect>
                  </svg>
                </RoomIconWrap>
                <RoomCardTitle>Your interview room is ready</RoomCardTitle>
                <RoomCardDescription>
                  Open the live AI interview in a new browser tab. Allow camera and microphone access when prompted,
                  then return here when you are finished to complete the session and view your feedback.
                </RoomCardDescription>
                <RoomDurationNote>
                  This session automatically ends after {interviewDurationLabel}.
                </RoomDurationNote>
                <JoinInterviewButton href={tavusEmbedSrc} target="_blank" rel="noopener noreferrer">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                    <polyline points="15 3 21 3 21 9"></polyline>
                    <line x1="10" y1="14" x2="21" y2="3"></line>
                  </svg>
                  Join Interview Room
                </JoinInterviewButton>
                <RoomLinkBox>
                  <RoomLinkInput
                    type="text"
                    readOnly
                    value={tavusEmbedSrc}
                    aria-label="Interview room link"
                    onFocus={(e) => e.target.select()}
                  />
                  <CopyLinkButton type="button" onClick={handleCopyRoomLink}>
                    {linkCopied ? 'Copied!' : 'Copy link'}
                  </CopyLinkButton>
                </RoomLinkBox>
              </>
            ) : currentInterview && !tavusConversationUrl ? (
              <>
                <RoomIconWrap>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                  </svg>
                </RoomIconWrap>
                <RoomCardTitle>Interview room link unavailable</RoomCardTitle>
                <RoomCardDescription>
                  The session was created but no Tavus room URL was returned. Check backend logs or Tavus configuration,
                  then try starting a new interview.
                </RoomCardDescription>
              </>
            ) : (
              <>
                <RoomIconWrap>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                  </svg>
                </RoomIconWrap>
                <RoomCardTitle>
                  {selectedJob ? 'Ready to start your mock interview' : 'Select a job to begin'}
                </RoomCardTitle>
                <RoomCardDescription>
                  {selectedJob
                    ? `When you start, a secure interview room link will appear here for ${selectedJob.title}. The live session opens in a new tab — you stay on ZedReq to review questions and complete the interview.`
                    : 'Choose a recommended job from the panel on the right, then click Start Interview to generate your personalized mock interview room.'}
                </RoomCardDescription>
                <RoomDurationNote>
                  Each mock interview session automatically ends after {interviewDurationLabel}.
                </RoomDurationNote>
              </>
            )}
          </InterviewRoomCard>

          <CallControls>
            <CallButtonWrapper>
              <StartButton 
                onClick={handleStartInterview}
                disabled={startingInterview || !selectedJob || !!currentInterview}
                style={{ 
                  opacity: (startingInterview || !selectedJob || !!currentInterview) ? 0.6 : 1,
                  cursor: (startingInterview || !selectedJob || !!currentInterview) ? 'not-allowed' : 'pointer'
                }}
              >
                {startingInterview ? (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="spinning">
                    <circle cx="12" cy="12" r="10" strokeDasharray="32" strokeDashoffset="32">
                      <animate attributeName="stroke-dasharray" dur="2s" values="0 32;16 16;0 32;0 32" repeatCount="indefinite"/>
                      <animate attributeName="stroke-dashoffset" dur="2s" values="0;-16;-32;-32" repeatCount="indefinite"/>
                    </circle>
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                  </svg>
                )}
              </StartButton>
              <CallButtonLabel>
                {startingInterview ? 'Starting...' : currentInterview ? 'In Progress' : 'Start Interview'}
              </CallButtonLabel>
            </CallButtonWrapper>

            {currentInterview && currentInterview.status !== 'completed' && (
              <CallButtonWrapper>
                <StartButton 
                  onClick={handleCompleteInterview}
                  disabled={completingInterview}
                  style={{ 
                    background: '#f59e0b',
                    borderColor: '#f59e0b',
                    opacity: completingInterview ? 0.6 : 1,
                    cursor: completingInterview ? 'not-allowed' : 'pointer'
                  }}
                >
                  {completingInterview ? (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="spinning">
                      <circle cx="12" cy="12" r="10" strokeDasharray="32" strokeDashoffset="32">
                        <animate attributeName="stroke-dasharray" dur="2s" values="0 32;16 16;0 32;0 32" repeatCount="indefinite"/>
                        <animate attributeName="stroke-dashoffset" dur="2s" values="0;-16;-32;-32" repeatCount="indefinite"/>
                      </circle>
                    </svg>
                  ) : (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                      <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                  )}
                </StartButton>
                <CallButtonLabel>
                  {completingInterview ? 'Completing...' : 'Complete Interview'}
                </CallButtonLabel>
              </CallButtonWrapper>
            )}
          </CallControls>

          {selectedJob && (
            <TranscriptPanel>
              <TranscriptHeader>
                <TranscriptHeaderMain>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                  </svg>
                  <div>
                    <TranscriptTitle>Interview Transcript — {selectedJob.title}</TranscriptTitle>
                    {tavusConversationId && (
                      <TranscriptSubtitle>Session ID: {tavusConversationId.substring(0, 8)}...</TranscriptSubtitle>
                    )}
                  </div>
                </TranscriptHeaderMain>
                {currentInterview?.interview_id && (
                  <TranscriptRefreshButton
                    type="button"
                    onClick={() => fetchTranscript(currentInterview.interview_id, { background: true })}
                    disabled={loadingTranscript || refreshingTranscript}
                  >
                    {loadingTranscript || refreshingTranscript ? 'Refreshing...' : 'Refresh transcript'}
                  </TranscriptRefreshButton>
                )}
              </TranscriptHeader>

              <TranscriptBody>
                <div className="ai-interview-transcript">
                {loadingTranscript && transcriptItems.length === 0 ? (
                  <TranscriptEmptyState>
                    <p>Loading transcript from Tavus...</p>
                  </TranscriptEmptyState>
                ) : !currentInterview ? (
                  <TranscriptEmptyState>
                    <p>Start an interview to see your question-wise transcript here after you finish in the Tavus room.</p>
                  </TranscriptEmptyState>
                ) : (
                  <>
                    {transcriptHint && (
                      <div className="transcript-hint-banner" role="status">
                        {transcriptHint}
                      </div>
                    )}
                    {transcriptItems.map((item) => (
                      <div key={item.question_index} className="transcript-item">
                        <div className="transcript-question-block">
                          <div className="transcript-meta-row">
                            <span>Question {item.question_index + 1}</span>
                            {item.question_type && (
                              <span className="transcript-type-badge">
                                {item.question_type.replace(/_/g, ' ')}
                              </span>
                            )}
                          </div>
                          <div className="transcript-q-text">{item.question_text}</div>
                        </div>
                        <div className="transcript-answer-block">
                          <div className="transcript-a-label">Your answer</div>
                          {item.has_response ? (
                            <div className="transcript-a-text">{item.user_response}</div>
                          ) : (
                            <p className="transcript-a-pending">
                              No response recorded for this question yet.
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                    {(transcriptSource || transcriptUserTurnCount > 0) && (
                      <div className="transcript-footer">
                        {transcriptSource && (
                          <span>
                            Source: {transcriptSource === 'database' ? 'Saved evaluation transcript' : transcriptSource === 'tavus' ? 'Live Tavus transcript' : 'Questions only (Tavus transcript pending)'}
                          </span>
                        )}
                        {transcriptUserTurnCount > 0 && (
                          <span>
                            {transcriptSource ? ' · ' : ''}
                            {transcriptUserTurnCount} user response{transcriptUserTurnCount === 1 ? '' : 's'} captured
                          </span>
                        )}
                      </div>
                    )}
                    <div ref={transcriptEndRef} />
                  </>
                )}
                </div>
              </TranscriptBody>
            </TranscriptPanel>
          )}
        </VideoPanel>
        </MainContent>

        <div
          className={`ai-interviews-resize-handle${isResizingPanel ? ' is-dragging' : ''}`}
          onMouseDown={handleResizeStart}
          role="separator"
          aria-orientation="vertical"
          aria-label="Resize side panels"
        />

        <SidePanelsColumn $width={sidePanelWidth}>
          <SidePanel>
            <SidePanelHeader>
              <PanelTitle>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                  <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                </svg>
                Recommended Jobs
              </PanelTitle>
              <PanelSubtitle>Select a role to practice your mock interview</PanelSubtitle>
            </SidePanelHeader>

            <SidePanelList>
              {loadingJobs ? (
                <EmptyState>Loading personalized job recommendations...</EmptyState>
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
                        <JobTag style={{ background: 'rgba(21, 133, 161, 0.1)', color: 'var(--primary)' }}>
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
                <EmptyState>
                  No job recommendations available. Update your profile to get personalized recommendations!
                </EmptyState>
              )}
            </SidePanelList>
          </SidePanel>

          <SidePanel>
            <SidePanelHeader>
              <PanelTitle>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                Interview History
              </PanelTitle>
              <PanelSubtitle>Your past interviews, scores, and coaching feedback</PanelSubtitle>
            </SidePanelHeader>

            <SidePanelList>
              {loadingInterviews ? (
                <EmptyState>Loading interviews...</EmptyState>
              ) : interviews.length > 0 ? (
                interviews.map((interview) => (
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
                      <ResultsContainer>
                        {interviewResults.overall_score !== null && (
                          <div style={{ fontSize: '0.9em', marginBottom: '8px', fontWeight: '500' }}>
                            Overall Score: <span style={{ color: 'var(--primary)', fontSize: '1.1em' }}>{interviewResults.overall_score}/100</span>
                          </div>
                        )}
                        {interviewResults.score_breakdown && (
                          <div style={{ fontSize: '0.85em', marginBottom: '8px' }}>
                            <div style={{ marginBottom: '4px' }}>Technical: {interviewResults.score_breakdown.technical_score}/100</div>
                            <div style={{ marginBottom: '4px' }}>Communication: {interviewResults.score_breakdown.communication_score}/100</div>
                            <div style={{ marginBottom: '4px' }}>Problem Solving: {interviewResults.score_breakdown.problem_solving_score}/100</div>
                            <div>Domain Knowledge: {interviewResults.score_breakdown.domain_knowledge_score}/100</div>
                          </div>
                        )}
                        {rizFeedback && (
                          <RizFeedbackContainer>
                            <div style={{ fontSize: '0.85em', fontWeight: '500', marginBottom: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span>Riz Coaching Feedback</span>
                              <RefreshButton
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleRefreshRizFeedback()
                                }}
                              >
                                Refresh
                              </RefreshButton>
                            </div>
                            {rizFeedback.summary && (
                              <div style={{ fontSize: '0.85em', marginBottom: '8px', fontStyle: 'italic', color: 'var(--text)' }}>
                                {rizFeedback.summary}
                              </div>
                            )}
                            {rizFeedback.strengths && rizFeedback.strengths.length > 0 && (
                              <div style={{ fontSize: '0.8em', marginTop: '6px' }}>
                                <strong style={{ color: '#22c55e' }}>Strengths:</strong>
                                <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                                  {rizFeedback.strengths.map((s, idx) => (
                                    <li key={idx}>{s}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {rizFeedback.weaknesses && rizFeedback.weaknesses.length > 0 && (
                              <div style={{ fontSize: '0.8em', marginTop: '6px' }}>
                                <strong style={{ color: '#f59e0b' }}>Areas for Improvement:</strong>
                                <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                                  {rizFeedback.weaknesses.map((w, idx) => (
                                    <li key={idx}>{w}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {rizFeedback.recommendations && rizFeedback.recommendations.length > 0 && (
                              <div style={{ fontSize: '0.8em', marginTop: '6px' }}>
                                <strong style={{ color: 'var(--primary)' }}>Recommendations:</strong>
                                <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                                  {rizFeedback.recommendations.map((r, idx) => (
                                    <li key={idx}>{r}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {rizFeedback.next_steps && rizFeedback.next_steps.length > 0 && (
                              <div style={{ fontSize: '0.8em', marginTop: '6px' }}>
                                <strong style={{ color: 'var(--primary)' }}>Next Steps:</strong>
                                <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                                  {rizFeedback.next_steps.map((ns, idx) => (
                                    <li key={idx}>{ns}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </RizFeedbackContainer>
                        )}
                        {!rizFeedback && interview.status === 'completed' && (
                          <div style={{ marginTop: '8px', fontSize: '0.8em', color: 'var(--text-light)' }}>
                            Riz feedback not available. Click &quot;Refresh&quot; to generate.
                          </div>
                        )}
                      </ResultsContainer>
                    )}
                  </JobCard>
                ))
              ) : (
                <EmptyState>No interview history yet. Start a mock interview to see results here.</EmptyState>
              )}
            </SidePanelList>
          </SidePanel>
        </SidePanelsColumn>
      </MainContainer>
    </Container>
  )
}

export default AIInterviews

