import React, { useState, useEffect } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { jobAPI, contextAPI } from '../services/api'
import Navbar from '../components/Navbar'

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`

const slideUp = keyframes`
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`

const fadeInScale = keyframes`
  from { 
    transform: scale(0.95); 
    opacity: 0; 
  }
  to { 
    transform: scale(1); 
    opacity: 1; 
  }
`

const spin = keyframes`
  to { transform: rotate(360deg); }
`

const Container = styled.div`
  min-height: 100vh;
  width: 100%;
  background: var(--bg-light);
  animation: ${fadeIn} 0.6s ease-in;
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
`

const PostJobButton = styled.button`
  padding: 10px 20px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 400;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(10, 102, 194, 0.4);
  }

  @media (max-width: 600px) {
    padding: 8px 14px;
    font-size: 0.9em;
  }
`

const MainContent = styled.div`
  display: flex;
  width: 100%;
  gap: 24px;
  padding: 30px 20px;
  
  @media (max-width: 768px) {
    padding: 20px 15px;
    gap: 0;
  }
`

const SidePanel = styled.div`
  width: 280px;
  min-width: 280px;
  background: var(--bg-white);
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 24px;
  height: fit-content;
  position: sticky;
  top: 80px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  animation: ${slideUp} 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  
  @media (max-width: 768px) {
    position: fixed;
    top: 0;
    left: ${props => props.isOpen ? '0' : '-100%'};
    height: 100vh;
    width: 280px;
    z-index: 1000;
    border-radius: 0;
    transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow-y: auto;
    padding-top: 60px;
  }
`

const SidePanelHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  
  @media (min-width: 769px) {
    display: none;
  }
`

const SidePanelTitle = styled.h2`
  font-size: 1.3em;
  color: var(--text);
  font-weight: 400;
  margin-bottom: 20px;
  letter-spacing: -0.3px;
  
  @media (max-width: 768px) {
    margin-bottom: 0;
  }
`

const CloseButtonMobile = styled.button`
  background: transparent;
  border: none;
  color: var(--text);
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: var(--hover-bg);
  }
`

const FilterOption = styled.button`
  width: 100%;
  padding: 16px 20px;
  background: ${props => props.active ? 'rgba(10, 102, 194, 0.1)' : 'transparent'};
  border: 1px solid ${props => props.active ? 'var(--primary)' : 'var(--border)'};
  border-radius: 10px;
  color: ${props => props.active ? 'var(--primary)' : 'var(--text)'};
  font-size: 1em;
  font-weight: ${props => props.active ? '500' : '400'};
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: left;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  
  &:hover {
    background: ${props => props.active ? 'rgba(10, 102, 194, 0.15)' : 'var(--hover-bg)'};
    border-color: ${props => props.active ? 'var(--primary)' : 'var(--border)'};
    transform: translateX(4px);
  }
  
  &:last-child {
    margin-bottom: 0;
  }
  
  svg {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
  }
`

const FilterCount = styled.span`
  margin-left: auto;
  padding: 4px 10px;
  background: ${props => props.active ? 'var(--primary)' : 'var(--hover-bg)'};
  color: ${props => props.active ? 'white' : 'var(--text-light)'};
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 500;
`

const MainContainer = styled.div`
  flex: 1;
  min-width: 0;
`

const MobileMenuButton = styled.button`
  display: none;
  padding: 10px;
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  align-items: center;
  justify-content: center;
  
  @media (max-width: 768px) {
    display: flex;
  }
  
  &:hover {
    background: var(--hover-bg);
    border-color: var(--primary);
  }
`

const Overlay = styled.div`
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  z-index: 999;
  animation: ${fadeIn} 0.2s ease;
  
  @media (max-width: 768px) {
    display: ${props => props.isOpen ? 'block' : 'none'};
  }
`

const JobsHeader = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  animation: ${fadeInScale} 0.5s cubic-bezier(0.4, 0, 0.2, 1);
`

const JobsTitle = styled.h2`
  font-size: 1.4em;
  color: var(--text);
  font-weight: 400;
  margin-bottom: 8px;
  letter-spacing: -0.3px;
`

const JobsSubtitle = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
  font-weight: 300;
`

const JobsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`

const JobCard = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 24px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  animation: ${slideUp} 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation-delay: ${props => props.delay || '0s'};
  animation-fill-mode: both;
  position: relative;

  &:hover {
    border-color: rgba(10, 102, 194, 0.4);
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  }
`

const JobHeader = styled.div`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
`

const JobInfo = styled.div`
  flex: 1;
`

const JobTitle = styled.h3`
  font-size: 1.15em;
  color: var(--text);
  font-weight: 400;
  margin-bottom: 8px;
  letter-spacing: -0.2px;
`

const JobCompany = styled.div`
  font-size: 0.95em;
  color: var(--text-light);
  margin-bottom: 4px;
`

const JobLocation = styled.div`
  font-size: 0.85em;
  color: var(--text-lighter);
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;

  svg {
    width: 14px;
    height: 14px;
  }
`

const JobMeta = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
`

const JobTag = styled.span`
  padding: 4px 12px;
  background: ${props => props.primary ? 'rgba(10, 102, 194, 0.1)' : 'var(--hover-bg)'};
  border: 1px solid ${props => props.primary ? 'rgba(10, 102, 194, 0.3)' : 'var(--border)'};
  border-radius: 12px;
  font-size: 0.8em;
  color: ${props => props.primary ? 'var(--primary)' : 'var(--text-light)'};
  font-weight: 400;
`

const MatchScore = styled.div`
  padding: 6px 12px;
  background: rgba(10, 102, 194, 0.1);
  border: 1px solid rgba(10, 102, 194, 0.3);
  border-radius: 8px;
  font-size: 0.85em;
  color: var(--primary);
  font-weight: 500;
  white-space: nowrap;
`

const JobDescription = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
  line-height: 1.6;
  margin-top: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`

const JobActions = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 16px;
`

const ApplyButton = styled.button`
  flex: 1;
  padding: 12px;
  background: ${props => props.applied ? 'var(--hover-bg)' : 'linear-gradient(135deg, var(--primary), var(--secondary))'};
  color: ${props => props.applied ? 'var(--text-light)' : 'white'};
  border: ${props => props.applied ? '1px solid var(--border)' : 'none'};
  border-radius: 8px;
  font-size: 0.95em;
  font-weight: 400;
  cursor: ${props => props.applied ? 'default' : 'pointer'};
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: ${props => props.applied ? 'none' : 'translateY(-2px)'};
    box-shadow: ${props => props.applied ? 'none' : '0 6px 16px rgba(10, 102, 194, 0.4)'};
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`

const SaveButton = styled.button`
  padding: 12px;
  background: ${props => props.saved ? 'rgba(10, 102, 194, 0.1)' : 'transparent'};
  color: ${props => props.saved ? 'var(--primary)' : 'var(--text-light)'};
  border: 1px solid ${props => props.saved ? 'var(--primary)' : 'var(--border)'};
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: rgba(10, 102, 194, 0.1);
    border-color: var(--primary);
    color: var(--primary);
  }
`

const LoadingSpinner = styled.div`
  width: 24px;
  height: 24px;
  border: 2px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: ${spin} 0.8s linear infinite;
  margin: 40px auto;
`

const EmptyState = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: var(--text-light);
  font-size: 0.95em;
`

const ErrorMessage = styled.div`
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 0.9em;
`

// Modal styles
const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: ${fadeIn} 0.2s ease;
`

const ModalContent = styled.div`
  background: var(--bg-white);
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  animation: ${slideUp} 0.3s cubic-bezier(0.4, 0, 0.2, 1);
`

const ModalHeader = styled.div`
  padding: 24px 24px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
`

const ModalTitle = styled.h2`
  font-size: 1.4em;
  font-weight: 400;
  color: var(--text);
`

const CloseButton = styled.button`
  background: transparent;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
  
  &:hover {
    background: var(--hover-bg);
    color: var(--text);
  }
`

const ModalBody = styled.div`
  padding: 24px;
`

const FormGroup = styled.div`
  margin-bottom: 20px;
`

const Label = styled.label`
  display: block;
  font-size: 0.9em;
  color: var(--text);
  margin-bottom: 8px;
  font-weight: 400;
`

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 1em;
  color: var(--text);
  transition: all 0.2s;
  
  &:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(10, 102, 194, 0.1);
  }
  
  &::placeholder {
    color: var(--text-lighter);
  }
`

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 1em;
  color: var(--text);
  resize: vertical;
  min-height: 120px;
  transition: all 0.2s;
  font-family: inherit;
  
  &:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(10, 102, 194, 0.1);
  }
`

const Select = styled.select`
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 1em;
  color: var(--text);
  cursor: pointer;
  
  &:focus {
    outline: none;
    border-color: var(--primary);
  }
`

const Checkbox = styled.label`
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 0.95em;
  color: var(--text);
  
  input {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
`

const FormRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
  }
`

const SubmitButton = styled.button`
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(10, 102, 194, 0.4);
  }
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`

// Applicants Modal Styles
const ApplicantsModalOverlay = styled(ModalOverlay)`
  z-index: 2000;
`

const ApplicantsModalContent = styled(ModalContent)`
  max-width: 800px;
  max-height: 85vh;
`

const ApplicantsHeader = styled.div`
  padding: 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
`

const ApplicantsTitle = styled.h2`
  font-size: 1.5em;
  font-weight: 400;
  color: var(--text);
  margin-bottom: 8px;
`

const JobInfoSection = styled.div`
  flex: 1;
`

const JobTitleText = styled.div`
  font-size: 1.1em;
  color: var(--text-light);
  margin-bottom: 4px;
`

const ApplicantCount = styled.div`
  font-size: 0.9em;
  color: var(--text-lighter);
`

const ApplicantsList = styled.div`
  padding: 24px;
  max-height: calc(85vh - 200px);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
`

const ApplicantCard = styled.div`
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: var(--primary);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`

const ApplicantHeader = styled.div`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
`

const ApplicantInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
`

const ApplicantAvatar = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
  font-size: 1.2em;
  flex-shrink: 0;
`

const ApplicantDetails = styled.div`
  flex: 1;
`

const ApplicantName = styled.div`
  font-size: 1.1em;
  color: var(--text);
  font-weight: 500;
  margin-bottom: 4px;
`

const ApplicantMeta = styled.div`
  font-size: 0.9em;
  color: var(--text-light);
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
`

const StatusBadge = styled.span`
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 500;
  background: ${props => 
    props.status === 'accepted' ? 'rgba(34, 197, 94, 0.1)' :
    props.status === 'rejected' ? 'rgba(239, 68, 68, 0.1)' :
    'rgba(10, 102, 194, 0.1)'
  };
  color: ${props => 
    props.status === 'accepted' ? '#22c55e' :
    props.status === 'rejected' ? '#ef4444' :
    'var(--primary)'
  };
  border: 1px solid ${props => 
    props.status === 'accepted' ? 'rgba(34, 197, 94, 0.3)' :
    props.status === 'rejected' ? 'rgba(239, 68, 68, 0.3)' :
    'rgba(10, 102, 194, 0.3)'
  };
`

const ApplicantActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 16px;
`

const ActionButton = styled.button`
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9em;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid var(--border);
  background: ${props => 
    props.variant === 'accept' ? 'rgba(34, 197, 94, 0.1)' :
    props.variant === 'reject' ? 'rgba(239, 68, 68, 0.1)' :
    'transparent'
  };
  color: ${props => 
    props.variant === 'accept' ? '#22c55e' :
    props.variant === 'reject' ? '#ef4444' :
    'var(--text)'
  };
  
  &:hover:not(:disabled) {
    background: ${props => 
      props.variant === 'accept' ? 'rgba(34, 197, 94, 0.2)' :
      props.variant === 'reject' ? 'rgba(239, 68, 68, 0.2)' :
      'var(--hover-bg)'
    };
    transform: translateY(-2px);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`

const ViewApplicantsButton = styled.button`
  flex: 1;
  padding: 12px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.95em;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(10, 102, 194, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
`

const ApplicantCountBadge = styled.span`
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-size: 0.85em;
  margin-left: 8px;
`

const Jobs = () => {
  const navigate = useNavigate()
  const { user } = useAuth()

  const [allJobs, setAllJobs] = useState([])
  const [remoteJobs, setRemoteJobs] = useState([])
  const [savedJobs, setSavedJobs] = useState([])
  const [postedJobs, setPostedJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [applyingTo, setApplyingTo] = useState(null)
  const [savingJob, setSavingJob] = useState(null)
  const [activeFilter, setActiveFilter] = useState('all')
  const [sidePanelOpen, setSidePanelOpen] = useState(false)
  
  // Applicants modal state
  const [selectedJob, setSelectedJob] = useState(null)
  const [applicants, setApplicants] = useState([])
  const [loadingApplicants, setLoadingApplicants] = useState(false)
  const [showApplicantsModal, setShowApplicantsModal] = useState(false)
  const [updatingStatus, setUpdatingStatus] = useState(null)
  
  // Post job modal state
  const [showPostModal, setShowPostModal] = useState(false)
  const [posting, setPosting] = useState(false)
  const [postError, setPostError] = useState(null)
  const [jobForm, setJobForm] = useState({
    title: '',
    description: '',
    company_name: '',
    location: '',
    job_type: 'full-time',
    is_remote: false,
    experience_level: '',
    skills_required: '',
    salary_min: '',
    salary_max: ''
  })

  const handleBackToFeed = () => {
    navigate('/feed')
  }

  // Fetch jobs
  const fetchJobs = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const [allJobsRes, remoteJobsRes, savedJobsRes, postedJobsRes] = await Promise.all([
        jobAPI.getJobs({ limit: 50 }),
        jobAPI.getRemoteJobs(50),
        jobAPI.getSavedJobs(50),
        jobAPI.getMyPostedJobs(50)
      ])
      
      setAllJobs(allJobsRes.data.jobs || [])
      setRemoteJobs(remoteJobsRes.data.jobs || [])
      setSavedJobs(savedJobsRes.data.jobs || [])
      setPostedJobs(postedJobsRes.data.jobs || [])
    } catch (err) {
      console.error('Failed to fetch jobs:', err)
      setError('Failed to load jobs. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchJobs()
  }, [])

  // Handle apply to job
  const handleApply = async (jobId, e) => {
    e.stopPropagation()
    if (applyingTo) return
    
    setApplyingTo(jobId)
    try {
      await jobAPI.applyToJob(jobId)
      // Update local state
      const updateJobs = (jobs) => 
        jobs.map(job => 
          job.job_id === jobId ? { ...job, has_applied: true } : job
        )
      setAllJobs(updateJobs)
      setRemoteJobs(updateJobs)
      setSavedJobs(updateJobs)
      setPostedJobs(updateJobs)
      
      // Update context for job application
      contextAPI.updateContext('apply', 'job', jobId).catch(() => {})
    } catch (err) {
      console.error('Failed to apply:', err)
      alert(err.response?.data?.detail || 'Failed to apply')
    } finally {
      setApplyingTo(null)
    }
  }

  // Handle save/unsave job
  const handleSave = async (jobId, e) => {
    e.stopPropagation()
    if (savingJob) return
    
    setSavingJob(jobId)
    try {
      const res = await jobAPI.toggleSaveJob(jobId)
      const isSaved = res.data.is_saved
      
      // Update local state
      const updateJobs = (jobs) => 
        jobs.map(job => 
          job.job_id === jobId ? { ...job, is_saved: isSaved } : job
        )
      setAllJobs(updateJobs)
      setRemoteJobs(updateJobs)
      setPostedJobs(updateJobs)
      
      // Update saved jobs list
      if (isSaved) {
        const job = allJobs.find(j => j.job_id === jobId) || remoteJobs.find(j => j.job_id === jobId) || postedJobs.find(j => j.job_id === jobId)
        if (job) {
          setSavedJobs(prev => [{ ...job, is_saved: true }, ...prev])
        }
      } else {
        setSavedJobs(prev => prev.filter(j => j.job_id !== jobId))
      }
    } catch (err) {
      console.error('Failed to save job:', err)
    } finally {
      setSavingJob(null)
    }
  }

  // Handle post job
  const handlePostJob = async (e) => {
    e.preventDefault()
    setPosting(true)
    setPostError(null)
    
    try {
      const jobData = {
        ...jobForm,
        salary_min: jobForm.salary_min ? parseInt(jobForm.salary_min) : null,
        salary_max: jobForm.salary_max ? parseInt(jobForm.salary_max) : null,
        experience_level: jobForm.experience_level || null
      }
      
      await jobAPI.createJob(jobData)
      setShowPostModal(false)
      setJobForm({
        title: '',
        description: '',
        company_name: '',
        location: '',
        job_type: 'full-time',
        is_remote: false,
        experience_level: '',
        skills_required: '',
        salary_min: '',
        salary_max: ''
      })
      fetchJobs() // Refresh jobs
    } catch (err) {
      console.error('Failed to post job:', err)
      setPostError(err.response?.data?.detail || 'Failed to post job')
    } finally {
      setPosting(false)
    }
  }

  // Format salary
  const formatSalary = (min, max) => {
    if (!min && !max) return null
    const format = (n) => `$${(n / 1000).toFixed(0)}k`
    if (min && max) return `${format(min)} - ${format(max)}`
    if (min) return `From ${format(min)}`
    if (max) return `Up to ${format(max)}`
    return null
  }

  // Parse skills string to array
  const parseSkills = (skills) => {
    if (!skills) return []
    return skills.split(',').map(s => s.trim()).filter(Boolean)
  }

  // Get current jobs based on active filter
  const getCurrentJobs = () => {
    switch (activeFilter) {
      case 'saved':
        return savedJobs
      case 'remote':
        return remoteJobs
      case 'posted':
        return postedJobs
      default:
        return allJobs
    }
  }

  // Get current filter title and subtitle
  const getFilterInfo = () => {
    switch (activeFilter) {
      case 'saved':
        return {
          title: 'Saved Jobs',
          subtitle: `${savedJobs.length} jobs bookmarked`
        }
      case 'remote':
        return {
          title: 'Remote Jobs',
          subtitle: `${remoteJobs.length} remote opportunities`
        }
      case 'posted':
        return {
          title: 'Posted Jobs',
          subtitle: `${postedJobs.length} jobs posted by you`
        }
      default:
        return {
          title: 'All Jobs',
          subtitle: `${allJobs.length} opportunities available`
        }
    }
  }

  const handleFilterChange = (filter) => {
    setActiveFilter(filter)
    setSidePanelOpen(false) // Close side panel on mobile when filter is selected
  }

  // Handle view applicants
  const handleViewApplicants = async (jobId) => {
    const job = postedJobs.find(j => j.job_id === jobId)
    setSelectedJob(job)
    setShowApplicantsModal(true)
    setLoadingApplicants(true)
    setApplicants([])
    
    try {
      const res = await jobAPI.getJobApplicants(jobId)
      setApplicants(res.data.applicants || res.data || [])
    } catch (err) {
      console.error('Failed to fetch applicants:', err)
      setError('Failed to load applicants. Please try again.')
    } finally {
      setLoadingApplicants(false)
    }
  }

  // Handle update application status
  const handleUpdateApplicationStatus = async (applicationId, status) => {
    if (updatingStatus === applicationId) return
    
    setUpdatingStatus(applicationId)
    try {
      await jobAPI.updateApplicationStatus(applicationId, status)
      // Update local state
      setApplicants(prev => 
        prev.map(app => 
          app.application_id === applicationId 
            ? { ...app, status } 
            : app
        )
      )
    } catch (err) {
      console.error('Failed to update status:', err)
      alert(err.response?.data?.detail || 'Failed to update application status')
    } finally {
      setUpdatingStatus(null)
    }
  }

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown'
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now - date)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays} days ago`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
    return date.toLocaleDateString()
  }

  // Track job view when job card is clicked
  const handleJobCardClick = (jobId, e) => {
    // Only track if click is not on a button or interactive element
    if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
      return
    }
    // Track job view
    contextAPI.updateContext('view', 'job', jobId).catch(() => {})
  }

  const renderJobCard = (job, index) => {
    const salary = formatSalary(job.salary_min, job.salary_max)
    const skills = parseSkills(job.skills_required)
    
    return (
      <JobCard key={job.job_id} delay={`${index * 0.1}s`} onClick={(e) => handleJobCardClick(job.job_id, e)}>
        <JobHeader>
          <JobInfo>
            <JobTitle>{job.title}</JobTitle>
            <JobCompany>{job.company_name || job.poster_name || 'Unknown Company'}</JobCompany>
            <JobLocation>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                <circle cx="12" cy="10" r="3"></circle>
              </svg>
              {job.location || 'Location not specified'}
            </JobLocation>
          </JobInfo>
          {job.match_score && <MatchScore>{job.match_score}% Match</MatchScore>}
        </JobHeader>
        
        <JobDescription>{job.description}</JobDescription>
        
        <JobMeta>
          <JobTag primary>{job.job_type || 'full-time'}</JobTag>
          {salary && <JobTag>{salary}</JobTag>}
          {job.is_remote && <JobTag primary>Remote</JobTag>}
          {skills.slice(0, 3).map((skill, idx) => (
            <JobTag key={idx}>{skill}</JobTag>
          ))}
          {skills.length > 3 && <JobTag>+{skills.length - 3}</JobTag>}
        </JobMeta>
        
        <JobActions>
          {activeFilter === 'posted' ? (
            // For posted jobs, show View Applicants button
            <ViewApplicantsButton onClick={() => handleViewApplicants(job.job_id)}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
              View Applicants
              {job.application_count > 0 && (
                <ApplicantCountBadge>{job.application_count}</ApplicantCountBadge>
              )}
            </ViewApplicantsButton>
          ) : (
            // For other jobs, show Apply and Save buttons
            <>
              <ApplyButton 
                applied={job.has_applied}
                disabled={applyingTo === job.job_id || job.has_applied}
                onClick={(e) => !job.has_applied && handleApply(job.job_id, e)}
              >
                {applyingTo === job.job_id ? 'Applying...' : job.has_applied ? 'Applied' : 'Apply Now'}
              </ApplyButton>
              <SaveButton 
                saved={job.is_saved}
                disabled={savingJob === job.job_id}
                onClick={(e) => handleSave(job.job_id, e)}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill={job.is_saved ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2">
                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                </svg>
              </SaveButton>
            </>
          )}
        </JobActions>
      </JobCard>
    )
  }

  return (
    <Container>
      <Navbar />

      {error && <ErrorMessage style={{ margin: '20px' }}>{error}</ErrorMessage>}

      <Overlay isOpen={sidePanelOpen} onClick={() => setSidePanelOpen(false)} />

      <MainContent>
        <SidePanel isOpen={sidePanelOpen}>
          <SidePanelHeader>
            <SidePanelTitle>Filter Jobs</SidePanelTitle>
            <CloseButtonMobile onClick={() => setSidePanelOpen(false)}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </CloseButtonMobile>
          </SidePanelHeader>
          
          <FilterOption
            active={activeFilter === 'all'}
            onClick={() => handleFilterChange('all')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            All Jobs
            <FilterCount active={activeFilter === 'all'}>{allJobs.length}</FilterCount>
          </FilterOption>

          <FilterOption
            active={activeFilter === 'saved'}
            onClick={() => handleFilterChange('saved')}
          >
            <svg viewBox="0 0 24 24" fill={activeFilter === 'saved' ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
            </svg>
            Saved Jobs
            <FilterCount active={activeFilter === 'saved'}>{savedJobs.length}</FilterCount>
          </FilterOption>

          <FilterOption
            active={activeFilter === 'remote'}
            onClick={() => handleFilterChange('remote')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
              <line x1="12" y1="22.08" x2="12" y2="12"></line>
            </svg>
            Remote Jobs
            <FilterCount active={activeFilter === 'remote'}>{remoteJobs.length}</FilterCount>
          </FilterOption>

          <FilterOption
            active={activeFilter === 'posted'}
            onClick={() => handleFilterChange('posted')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            Posted Jobs
            <FilterCount active={activeFilter === 'posted'}>{postedJobs.length}</FilterCount>
          </FilterOption>
        </SidePanel>

        <MainContainer>
          <JobsHeader>
            <JobsTitle>{getFilterInfo().title}</JobsTitle>
            <JobsSubtitle>{getFilterInfo().subtitle}</JobsSubtitle>
          </JobsHeader>
          <JobsContainer>
            {loading ? (
              <LoadingSpinner />
            ) : getCurrentJobs().length === 0 ? (
              <EmptyState>
                {activeFilter === 'saved' 
                  ? 'No saved jobs yet. Bookmark jobs to find them here.'
                  : activeFilter === 'remote'
                  ? 'No remote jobs available'
                  : activeFilter === 'posted'
                  ? 'You haven\'t posted any jobs yet. Click "Post a Job" to get started.'
                  : 'No jobs available at the moment'}
              </EmptyState>
            ) : (
              getCurrentJobs().map((job, index) => renderJobCard(job, index))
            )}
          </JobsContainer>
        </MainContainer>
      </MainContent>

      {/* Applicants Modal */}
      {showApplicantsModal && selectedJob && (
        <ApplicantsModalOverlay onClick={() => setShowApplicantsModal(false)}>
          <ApplicantsModalContent onClick={e => e.stopPropagation()}>
            <ApplicantsHeader>
              <JobInfoSection>
                <ApplicantsTitle>Applicants</ApplicantsTitle>
                <JobTitleText>{selectedJob.title}</JobTitleText>
                <ApplicantCount>
                  {applicants.length} {applicants.length === 1 ? 'applicant' : 'applicants'}
                </ApplicantCount>
              </JobInfoSection>
              <CloseButton onClick={() => setShowApplicantsModal(false)}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </CloseButton>
            </ApplicantsHeader>
            
            <ApplicantsList>
              {loadingApplicants ? (
                <LoadingSpinner />
              ) : applicants.length === 0 ? (
                <EmptyState>No applicants yet for this job posting.</EmptyState>
              ) : (
                applicants.map((applicant) => {
                  const initials = applicant.applicant_name 
                    ? applicant.applicant_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
                    : applicant.username
                    ? applicant.username.substring(0, 2).toUpperCase()
                    : 'U'
                  
                  return (
                    <ApplicantCard key={applicant.application_id || applicant.user_id || applicant.applicant_id}>
                      <ApplicantHeader>
                        <ApplicantInfo>
                          <ApplicantAvatar>{initials}</ApplicantAvatar>
                          <ApplicantDetails>
                            <ApplicantName>
                              {applicant.applicant_name || applicant.username || applicant.name || 'Unknown User'}
                            </ApplicantName>
                            <ApplicantMeta>
                              <span>
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ display: 'inline', marginRight: '4px' }}>
                                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                                  <line x1="16" y1="2" x2="16" y2="6"></line>
                                  <line x1="8" y1="2" x2="8" y2="6"></line>
                                  <line x1="3" y1="10" x2="21" y2="10"></line>
                                </svg>
                                Applied {formatDate(applicant.applied_at || applicant.created_at || applicant.application_date)}
                              </span>
                              {applicant.status && (
                                <StatusBadge status={applicant.status}>
                                  {applicant.status.charAt(0).toUpperCase() + applicant.status.slice(1)}
                                </StatusBadge>
                              )}
                            </ApplicantMeta>
                          </ApplicantDetails>
                        </ApplicantInfo>
                      </ApplicantHeader>
                      
                      {applicant.cover_letter && (
                        <div style={{ marginTop: '12px', padding: '12px', background: 'var(--bg-white)', borderRadius: '8px', fontSize: '0.9em', color: 'var(--text-light)', lineHeight: '1.6' }}>
                          {applicant.cover_letter}
                        </div>
                      )}
                      
                      {applicant.status !== 'accepted' && applicant.status !== 'rejected' && (
                        <ApplicantActions>
                          <ActionButton
                            variant="accept"
                            onClick={() => handleUpdateApplicationStatus(applicant.application_id || applicant.id, 'accepted')}
                            disabled={updatingStatus === (applicant.application_id || applicant.id)}
                          >
                            {updatingStatus === (applicant.application_id || applicant.id) ? 'Updating...' : 'Accept'}
                          </ActionButton>
                          <ActionButton
                            variant="reject"
                            onClick={() => handleUpdateApplicationStatus(applicant.application_id || applicant.id, 'rejected')}
                            disabled={updatingStatus === (applicant.application_id || applicant.id)}
                          >
                            {updatingStatus === (applicant.application_id || applicant.id) ? 'Updating...' : 'Reject'}
                          </ActionButton>
                        </ApplicantActions>
                      )}
                    </ApplicantCard>
                  )
                })
              )}
            </ApplicantsList>
          </ApplicantsModalContent>
        </ApplicantsModalOverlay>
      )}

      {/* Post Job Modal */}
      {showPostModal && (
        <ModalOverlay onClick={() => setShowPostModal(false)}>
          <ModalContent onClick={e => e.stopPropagation()}>
            <ModalHeader>
              <ModalTitle>Post a New Job</ModalTitle>
              <CloseButton onClick={() => setShowPostModal(false)}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </CloseButton>
            </ModalHeader>
            <ModalBody>
              {postError && <ErrorMessage>{postError}</ErrorMessage>}
              <form onSubmit={handlePostJob}>
                <FormGroup>
                  <Label>Job Title *</Label>
                  <Input
                    type="text"
                    value={jobForm.title}
                    onChange={e => setJobForm({...jobForm, title: e.target.value})}
                    placeholder="e.g. Senior Software Engineer"
                    required
                  />
                </FormGroup>
                
                <FormGroup>
                  <Label>Description *</Label>
                  <TextArea
                    value={jobForm.description}
                    onChange={e => setJobForm({...jobForm, description: e.target.value})}
                    placeholder="Describe the role, responsibilities, and requirements..."
                    required
                  />
                </FormGroup>
                
                <FormRow>
                  <FormGroup>
                    <Label>Company Name</Label>
                    <Input
                      type="text"
                      value={jobForm.company_name}
                      onChange={e => setJobForm({...jobForm, company_name: e.target.value})}
                      placeholder="Your company name"
                    />
                  </FormGroup>
                  
                  <FormGroup>
                    <Label>Location</Label>
                    <Input
                      type="text"
                      value={jobForm.location}
                      onChange={e => setJobForm({...jobForm, location: e.target.value})}
                      placeholder="e.g. San Francisco, CA"
                    />
                  </FormGroup>
                </FormRow>
                
                <FormRow>
                  <FormGroup>
                    <Label>Job Type</Label>
                    <Select
                      value={jobForm.job_type}
                      onChange={e => setJobForm({...jobForm, job_type: e.target.value})}
                    >
                      <option value="full-time">Full-time</option>
                      <option value="part-time">Part-time</option>
                      <option value="contract">Contract</option>
                      <option value="internship">Internship</option>
                    </Select>
                  </FormGroup>
                  
                  <FormGroup>
                    <Label>Experience Level</Label>
                    <Select
                      value={jobForm.experience_level}
                      onChange={e => setJobForm({...jobForm, experience_level: e.target.value})}
                    >
                      <option value="">Any</option>
                      <option value="entry">Entry Level</option>
                      <option value="mid">Mid Level</option>
                      <option value="senior">Senior Level</option>
                      <option value="lead">Lead</option>
                      <option value="executive">Executive</option>
                    </Select>
                  </FormGroup>
                </FormRow>
                
                <FormRow>
                  <FormGroup>
                    <Label>Salary Min ($)</Label>
                    <Input
                      type="number"
                      value={jobForm.salary_min}
                      onChange={e => setJobForm({...jobForm, salary_min: e.target.value})}
                      placeholder="e.g. 100000"
                    />
                  </FormGroup>
                  
                  <FormGroup>
                    <Label>Salary Max ($)</Label>
                    <Input
                      type="number"
                      value={jobForm.salary_max}
                      onChange={e => setJobForm({...jobForm, salary_max: e.target.value})}
                      placeholder="e.g. 150000"
                    />
                  </FormGroup>
                </FormRow>
                
                <FormGroup>
                  <Label>Skills Required</Label>
                  <Input
                    type="text"
                    value={jobForm.skills_required}
                    onChange={e => setJobForm({...jobForm, skills_required: e.target.value})}
                    placeholder="e.g. JavaScript, React, Node.js (comma-separated)"
                  />
                </FormGroup>
                
                <FormGroup>
                  <Checkbox>
                    <input
                      type="checkbox"
                      checked={jobForm.is_remote}
                      onChange={e => setJobForm({...jobForm, is_remote: e.target.checked})}
                    />
                    This is a remote position
                  </Checkbox>
                </FormGroup>
                
                <SubmitButton type="submit" disabled={posting}>
                  {posting ? 'Posting...' : 'Post Job'}
                </SubmitButton>
              </form>
            </ModalBody>
          </ModalContent>
        </ModalOverlay>
      )}
    </Container>
  )
}

export default Jobs
