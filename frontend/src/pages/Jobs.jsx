import React, { useState, useEffect } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { jobAPI } from '../services/api'

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

const Navbar = styled.nav`
  background: rgba(13, 13, 13, 0.7);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
  position: sticky;
  top: 0;
  z-index: 100;
  width: 100%;
  padding: 0 20px;
`

const NavContainer = styled.div`
  max-width: 100%;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  gap: 30px;

  @media (max-width: 600px) {
    gap: 15px;
    padding: 10px 0;
  }
`

const NavLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
`

const Logo = styled.h1`
  font-size: 1.8em;
  font-weight: 300;
  color: var(--primary);
  cursor: pointer;
  transition: transform 0.2s ease;
  white-space: nowrap;
  
  &:hover {
    transform: scale(1.05);
  }

  @media (max-width: 600px) {
    font-size: 1.5em;
  }
`

const NavRight = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
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

const MainContainer = styled.div`
  width: 100%;
  max-width: 100%;
  padding: 30px 20px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 25px;
  
  @media (max-width: 1200px) {
    gap: 20px;
  }
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  @media (max-width: 480px) {
    padding: 20px 15px;
  }
`

const JobColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: ${fadeInScale} 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  animation-delay: ${props => props.delay || '0s'};
  animation-fill-mode: both;
`

const ColumnHeader = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 24px;
  position: sticky;
  top: 80px;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`

const ColumnTitle = styled.h2`
  font-size: 1.4em;
  color: var(--text);
  font-weight: 400;
  margin-bottom: 8px;
  letter-spacing: -0.3px;
`

const ColumnSubtitle = styled.p`
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

const Jobs = () => {
  const navigate = useNavigate()
  const { user } = useAuth()

  const [allJobs, setAllJobs] = useState([])
  const [remoteJobs, setRemoteJobs] = useState([])
  const [savedJobs, setSavedJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [applyingTo, setApplyingTo] = useState(null)
  const [savingJob, setSavingJob] = useState(null)
  
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
      const [allJobsRes, remoteJobsRes, savedJobsRes] = await Promise.all([
        jobAPI.getJobs({ limit: 50 }),
        jobAPI.getRemoteJobs(50),
        jobAPI.getSavedJobs(50)
      ])
      
      setAllJobs(allJobsRes.data.jobs || [])
      setRemoteJobs(remoteJobsRes.data.jobs || [])
      setSavedJobs(savedJobsRes.data.jobs || [])
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
      
      // Update saved jobs list
      if (isSaved) {
        const job = allJobs.find(j => j.job_id === jobId) || remoteJobs.find(j => j.job_id === jobId)
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

  const renderJobCard = (job, index) => {
    const salary = formatSalary(job.salary_min, job.salary_max)
    const skills = parseSkills(job.skills_required)
    
    return (
      <JobCard key={job.job_id} delay={`${index * 0.1}s`}>
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
        </JobActions>
      </JobCard>
    )
  }

  return (
    <Container>
      <Navbar>
        <NavContainer>
          <NavLeft>
            <Logo onClick={handleBackToFeed}>ZedReq</Logo>
          </NavLeft>
          <NavRight>
            <PostJobButton onClick={() => setShowPostModal(true)}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              Post a Job
            </PostJobButton>
            <BackButton onClick={handleBackToFeed}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
            </BackButton>
          </NavRight>
        </NavContainer>
      </Navbar>

      {error && <ErrorMessage style={{ margin: '20px' }}>{error}</ErrorMessage>}

      <MainContainer>
        <JobColumn delay="0s">
          <ColumnHeader>
            <ColumnTitle>All Jobs</ColumnTitle>
            <ColumnSubtitle>{allJobs.length} opportunities available</ColumnSubtitle>
          </ColumnHeader>
          <JobsContainer>
            {loading ? (
              <LoadingSpinner />
            ) : allJobs.length === 0 ? (
              <EmptyState>No jobs available at the moment</EmptyState>
            ) : (
              allJobs.map((job, index) => renderJobCard(job, index))
            )}
          </JobsContainer>
        </JobColumn>

        <JobColumn delay="0.1s">
          <ColumnHeader>
            <ColumnTitle>Saved Jobs</ColumnTitle>
            <ColumnSubtitle>{savedJobs.length} jobs bookmarked</ColumnSubtitle>
          </ColumnHeader>
          <JobsContainer>
            {loading ? (
              <LoadingSpinner />
            ) : savedJobs.length === 0 ? (
              <EmptyState>No saved jobs yet. Bookmark jobs to find them here.</EmptyState>
            ) : (
              savedJobs.map((job, index) => renderJobCard(job, index))
            )}
          </JobsContainer>
        </JobColumn>

        <JobColumn delay="0.2s">
          <ColumnHeader>
            <ColumnTitle>Remote Jobs</ColumnTitle>
            <ColumnSubtitle>{remoteJobs.length} remote opportunities</ColumnSubtitle>
          </ColumnHeader>
          <JobsContainer>
            {loading ? (
              <LoadingSpinner />
            ) : remoteJobs.length === 0 ? (
              <EmptyState>No remote jobs available</EmptyState>
            ) : (
              remoteJobs.map((job, index) => renderJobCard(job, index))
            )}
          </JobsContainer>
        </JobColumn>
      </MainContainer>

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
