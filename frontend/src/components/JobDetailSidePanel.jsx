import React, { useEffect, useState } from 'react'
import styled, { keyframes } from 'styled-components'
import { jobAPI } from '../services/api'
import { JobCompanyOrPoster } from './UserProfileLink'

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`

const JobDetailOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1500;
  display: ${props => (props.$isOpen ? 'block' : 'none')};
  animation: ${fadeIn} 0.2s ease;
`

const JobDetailPanel = styled.div`
  position: fixed;
  top: 0;
  right: ${props => (props.$isOpen ? '0' : '-100%')};
  width: 100%;
  max-width: 600px;
  height: 100vh;
  background: var(--bg-white);
  z-index: 1501;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
  transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow-y: auto;
  display: flex;
  flex-direction: column;

  @media (max-width: 768px) {
    max-width: 100%;
  }
`

const JobDetailHeader = styled.div`
  padding: 24px;
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  background: var(--bg-white);
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
`

const JobDetailTitle = styled.h2`
  font-size: 1.5em;
  font-weight: 400;
  color: var(--text);
  margin: 0;
  flex: 1;
`

const JobDetailCloseButton = styled.button`
  background: transparent;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 36px;
  height: 36px;

  &:hover {
    background: var(--hover-bg);
    color: var(--text);
  }

  svg {
    width: 24px;
    height: 24px;
  }
`

const JobDetailContent = styled.div`
  padding: 24px;
  flex: 1;
`

const JobDetailSection = styled.div`
  margin-bottom: 32px;

  &:last-child {
    margin-bottom: 0;
  }
`

const JobDetailSectionTitle = styled.h3`
  font-size: 1.1em;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
`

const JobDetailInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`

const JobDetailInfoRow = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;

  svg {
    width: 18px;
    height: 18px;
    color: var(--text-light);
    flex-shrink: 0;
    margin-top: 2px;
  }
`

const JobDetailInfoLabel = styled.span`
  font-size: 0.9em;
  color: var(--text-light);
  font-weight: 500;
  min-width: 100px;
`

const JobDetailInfoValue = styled.span`
  font-size: 0.95em;
  color: var(--text);
  flex: 1;
`

const JobDetailDescription = styled.div`
  font-size: 0.95em;
  color: var(--text);
  line-height: 1.7;
  white-space: pre-wrap;
`

const JobDetailSkills = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`

const JobDetailSkillTag = styled.span`
  padding: 6px 14px;
  background: rgba(21, 133, 161, 0.1);
  border: 1px solid rgba(21, 133, 161, 0.3);
  border-radius: 12px;
  font-size: 0.85em;
  color: var(--primary);
  font-weight: 400;
`

const JobDetailActions = styled.div`
  padding: 24px;
  border-top: 1px solid var(--border);
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  position: sticky;
  bottom: 0;
  background: var(--bg-white);
  z-index: 10;
`

const ApplyButton = styled.button`
  flex: 1;
  min-width: 140px;
  padding: 12px;
  background: ${props =>
    props.$applied ? 'var(--hover-bg)' : 'linear-gradient(135deg, var(--primary), var(--secondary))'};
  color: ${props => (props.$applied ? 'var(--text-light)' : 'white')};
  border: ${props => (props.$applied ? '1px solid var(--border)' : 'none')};
  border-radius: 8px;
  font-size: 0.95em;
  font-weight: 400;
  cursor: ${props => (props.$applied ? 'default' : 'pointer')};
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: ${props => (props.$applied ? 'none' : 'translateY(-2px)')};
    box-shadow: ${props => (props.$applied ? 'none' : '0 6px 16px rgba(21, 133, 161, 0.4)')};
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`

const SaveButton = styled.button`
  padding: 12px;
  background: ${props => (props.$saved ? 'rgba(21, 133, 161, 0.1)' : 'transparent')};
  color: ${props => (props.$saved ? 'var(--primary)' : 'var(--text-light)')};
  border: 1px solid ${props => (props.$saved ? 'var(--primary)' : 'var(--border)')};
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: rgba(21, 133, 161, 0.1);
    border-color: var(--primary);
    color: var(--primary);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`

const ExternalLinkButton = styled.a`
  flex: 1 1 100%;
  text-align: center;
  padding: 10px 16px;
  font-size: 0.9em;
  color: var(--primary);
  border: 1px solid rgba(21, 133, 161, 0.35);
  border-radius: 8px;
  text-decoration: none;
  transition: background 0.2s ease;

  &:hover {
    background: rgba(21, 133, 161, 0.06);
  }
`

const PanelLoading = styled.div`
  padding: 48px 24px;
  text-align: center;
  color: var(--text-light);
  font-size: 0.95em;
`

const PanelError = styled.div`
  padding: 24px;
  color: #b91c1c;
  font-size: 0.9em;
`

const SearchMatchBadge = styled.span`
  display: inline-block;
  margin-left: 8px;
  padding: 4px 10px;
  background: rgba(21, 133, 161, 0.1);
  border: 1px solid rgba(21, 133, 161, 0.3);
  border-radius: 8px;
  font-size: 0.65em;
  font-weight: 500;
  color: var(--primary);
  vertical-align: middle;
`

function parseSkills(skills) {
  if (!skills) return []
  if (Array.isArray(skills)) {
    return skills.map(s => String(s).trim()).filter(Boolean)
  }
  if (typeof skills === 'string') {
    return skills.split(',').map(s => s.trim()).filter(Boolean)
  }
  try {
    return String(skills)
      .split(',')
      .map(s => s.trim())
      .filter(Boolean)
  } catch {
    return []
  }
}

function formatSalary(min, max) {
  if (!min && !max) return null
  const format = n => `$${(n / 1000).toFixed(0)}k`
  if (min && max) return `${format(min)} - ${format(max)}`
  if (min) return `From ${format(min)}`
  if (max) return `Up to ${format(max)}`
  return null
}

/**
 * Slide-over job detail (description, apply, save) — same UX as Jobs page.
 */
export default function JobDetailSidePanel({
  isOpen,
  jobId,
  onClose,
  matchScoreFromSearch,
  onJobStateChange,
}) {
  const [job, setJob] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [applyingTo, setApplyingTo] = useState(null)
  const [savingJob, setSavingJob] = useState(null)

  useEffect(() => {
    if (!isOpen || !jobId) {
      setJob(null)
      setError(null)
      return
    }

    let cancelled = false
    setLoading(true)
    setError(null)

    jobAPI
      .getJob(jobId)
      .then(res => {
        if (!cancelled) {
          setJob(res.data)
        }
      })
      .catch(err => {
        if (!cancelled) {
          setError(err.response?.data?.detail || err.message || 'Failed to load job')
          setJob(null)
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [isOpen, jobId])

  const handleApply = async e => {
    e.preventDefault()
    e.stopPropagation()
    if (!job?.job_id || applyingTo || job.has_applied) return

    setApplyingTo(job.job_id)
    try {
      await jobAPI.applyToJob(job.job_id)
      setJob(j => ({ ...j, has_applied: true }))
      onJobStateChange?.({ jobId: job.job_id, patch: { has_applied: true } })
    } catch (err) {
      console.error('Apply failed:', err)
      alert(err.response?.data?.detail || 'Failed to apply')
    } finally {
      setApplyingTo(null)
    }
  }

  const handleSave = async e => {
    e.preventDefault()
    e.stopPropagation()
    if (!job?.job_id || savingJob) return

    setSavingJob(job.job_id)
    try {
      const res = await jobAPI.toggleSaveJob(job.job_id)
      const isSaved = res.data?.is_saved
      setJob(j => ({ ...j, is_saved: isSaved }))
      onJobStateChange?.({ jobId: job.job_id, patch: { is_saved: isSaved } })
    } catch (err) {
      console.error('Save failed:', err)
    } finally {
      setSavingJob(null)
    }
  }

  const detailSkills = job ? parseSkills(job.skills_required) : []
  const detailSkillsArray = Array.isArray(detailSkills) ? detailSkills : []

  return (
    <>
      <JobDetailOverlay $isOpen={isOpen} onClick={onClose} role="presentation" />
      <JobDetailPanel $isOpen={isOpen} role="dialog" aria-modal="true" aria-labelledby="ai-job-detail-title">
        {!isOpen || !jobId ? null : loading ? (
          <PanelLoading>Loading job details…</PanelLoading>
        ) : error ? (
          <>
            <JobDetailHeader>
              <JobDetailTitle id="ai-job-detail-title">Job</JobDetailTitle>
              <JobDetailCloseButton type="button" onClick={onClose} aria-label="Close">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </JobDetailCloseButton>
            </JobDetailHeader>
            <PanelError>{error}</PanelError>
          </>
        ) : job ? (
          <>
            <JobDetailHeader>
              <JobDetailTitle id="ai-job-detail-title">
                {job.title}
                {matchScoreFromSearch != null && (
                  <SearchMatchBadge>{matchScoreFromSearch}% match</SearchMatchBadge>
                )}
              </JobDetailTitle>
              <JobDetailCloseButton type="button" onClick={onClose} aria-label="Close">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </JobDetailCloseButton>
            </JobDetailHeader>

            <JobDetailContent>
              <JobDetailSection>
                <JobDetailInfo>
                  <JobDetailInfoRow>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                      <circle cx="12" cy="7" r="4" />
                    </svg>
                    <JobDetailInfoLabel>Company:</JobDetailInfoLabel>
                    <JobDetailInfoValue>
                      <JobCompanyOrPoster job={job} />
                    </JobDetailInfoValue>
                  </JobDetailInfoRow>

                  <JobDetailInfoRow>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                      <circle cx="12" cy="10" r="3" />
                    </svg>
                    <JobDetailInfoLabel>Location:</JobDetailInfoLabel>
                    <JobDetailInfoValue>{job.location || 'Location not specified'}</JobDetailInfoValue>
                  </JobDetailInfoRow>

                  <JobDetailInfoRow>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
                      <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
                    </svg>
                    <JobDetailInfoLabel>Job Type:</JobDetailInfoLabel>
                    <JobDetailInfoValue>
                      {job.job_type
                        ? job.job_type.charAt(0).toUpperCase() + job.job_type.slice(1).replace('-', ' ')
                        : 'Full-time'}
                    </JobDetailInfoValue>
                  </JobDetailInfoRow>

                  {job.is_remote && (
                    <JobDetailInfoRow>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                      </svg>
                      <JobDetailInfoLabel>Remote:</JobDetailInfoLabel>
                      <JobDetailInfoValue>Yes</JobDetailInfoValue>
                    </JobDetailInfoRow>
                  )}

                  {formatSalary(job.salary_min, job.salary_max) && (
                    <JobDetailInfoRow>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <line x1="12" y1="1" x2="12" y2="23" />
                        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                      </svg>
                      <JobDetailInfoLabel>Salary:</JobDetailInfoLabel>
                      <JobDetailInfoValue>{formatSalary(job.salary_min, job.salary_max)}</JobDetailInfoValue>
                    </JobDetailInfoRow>
                  )}

                  {job.experience_level && (
                    <JobDetailInfoRow>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                        <polyline points="22 4 12 14.01 9 11.01" />
                      </svg>
                      <JobDetailInfoLabel>Experience:</JobDetailInfoLabel>
                      <JobDetailInfoValue>
                        {job.experience_level.charAt(0).toUpperCase() +
                          job.experience_level.slice(1).replace('_', ' ')}
                      </JobDetailInfoValue>
                    </JobDetailInfoRow>
                  )}
                </JobDetailInfo>
              </JobDetailSection>

              <JobDetailSection>
                <JobDetailSectionTitle>Description</JobDetailSectionTitle>
                <JobDetailDescription>{job.description || 'No description provided.'}</JobDetailDescription>
              </JobDetailSection>

              {detailSkillsArray.length > 0 && (
                <JobDetailSection>
                  <JobDetailSectionTitle>Required Skills</JobDetailSectionTitle>
                  <JobDetailSkills>
                    {detailSkillsArray.map((skill, idx) => (
                      <JobDetailSkillTag key={idx}>{skill}</JobDetailSkillTag>
                    ))}
                  </JobDetailSkills>
                </JobDetailSection>
              )}
            </JobDetailContent>

            <JobDetailActions>
              <ApplyButton
                type="button"
                $applied={job.has_applied}
                disabled={applyingTo === job.job_id || job.has_applied}
                onClick={handleApply}
              >
                {applyingTo === job.job_id ? 'Applying…' : job.has_applied ? 'Applied' : 'Apply Now'}
              </ApplyButton>
              <SaveButton
                type="button"
                $saved={job.is_saved}
                disabled={savingJob === job.job_id}
                onClick={handleSave}
                aria-label={job.is_saved ? 'Unsave job' : 'Save job'}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill={job.is_saved ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2">
                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
                </svg>
              </SaveButton>
              {job.job_link ? (
                <ExternalLinkButton href={job.job_link} target="_blank" rel="noopener noreferrer">
                  Open external posting
                </ExternalLinkButton>
              ) : null}
            </JobDetailActions>
          </>
        ) : null}
      </JobDetailPanel>
    </>
  )
}
