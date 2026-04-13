import React, { useState, useEffect, useRef } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'
import { useConfirm } from '../contexts/ConfirmModalContext'
import api, { userAPI } from '../services/api'
import Navbar from '../components/Navbar'
import { ZEDREQ_EMAIL } from '../config/contact'
import { LegalPrivacyBody } from '../content/LegalPrivacyBody'
import { LegalTermsBody } from '../content/LegalTermsBody'
import '../css/pages/GetStarted.css'

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`

const slideIn = keyframes`
  from { transform: translateX(-20px); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
`

const Container = styled.div`
  min-height: 100vh;
  background: var(--bg-light);
  animation: ${fadeIn} 0.6s ease-in;
  padding-top: 80px;
`

const SettingsContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 30px;
  padding: 30px 20px;

  @media (max-width: 1200px) {
    gap: 25px;
    padding: 28px 18px;
  }

  @media (max-width: 1024px) {
    grid-template-columns: 240px 1fr;
    gap: 20px;
    padding: 25px 16px;
  }
  
  @media (max-width: 900px) {
    grid-template-columns: 220px 1fr;
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
    gap: 15px;
    padding: 15px 12px;
  }
  
  @media (max-width: 360px) {
    gap: 12px;
    padding: 12px 10px;
  }
`

const SidePanel = styled.aside`
  background: var(--bg-white);
  border-radius: 16px;
  border: 1px solid var(--border);
  padding: 20px 0;
  height: fit-content;
  position: sticky;
  top: 100px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);

  @media (max-width: 768px) {
    position: static;
    top: auto;
  }
`

const SidePanelSection = styled.div`
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
  color: var(--text-light);
  font-size: 0.9em;
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 44px; /* Better touch target */

  &:hover {
    background: var(--hover-bg);
    color: var(--text);
  }

  &.active {
    background: rgba(21, 133, 161, 0.1);
    color: var(--primary);
    border-left-color: var(--primary);
    font-weight: 500;
  }

  svg {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
  }
  
  @media (max-width: 1024px) {
    padding: 10px 18px;
    font-size: 0.85em;
    gap: 10px;
    min-height: 42px;
    
    svg {
      width: 16px;
      height: 16px;
    }
  }
  
  @media (max-width: 768px) {
    padding: 10px 16px;
    font-size: 0.85em;
    gap: 10px;
  }
  
  @media (max-width: 480px) {
    padding: 8px 14px;
    font-size: 0.8em;
    gap: 8px;
    min-height: 40px;
    
    svg {
      width: 16px;
      height: 16px;
    }
  }
  
  @media (max-width: 360px) {
    padding: 8px 12px;
    font-size: 0.75em;
    gap: 6px;
    min-height: 38px;
    
    svg {
      width: 14px;
      height: 14px;
    }
  }
`

const MainContent = styled.div`
  background: var(--bg-white);
  border-radius: 16px;
  border: 1px solid var(--border);
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  animation: ${slideIn} 0.4s ease-out;

  @media (max-width: 1024px) {
    padding: 35px 25px;
    border-radius: 14px;
  }

  @media (max-width: 768px) {
    padding: 30px 20px;
    border-radius: 12px;
  }
  
  @media (max-width: 600px) {
    padding: 25px 18px;
  }
  
  @media (max-width: 480px) {
    padding: 20px 15px;
    border-radius: 10px;
  }
  
  @media (max-width: 360px) {
    padding: 18px 12px;
    border-radius: 8px;
  }
`

const SectionTitle = styled.h2`
  font-size: 1.8em;
  font-weight: 300;
  color: var(--text);
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid var(--border);
  
  @media (max-width: 1024px) {
    font-size: 1.6em;
    margin-bottom: 25px;
    padding-bottom: 12px;
  }
  
  @media (max-width: 768px) {
    font-size: 1.5em;
    margin-bottom: 24px;
    padding-bottom: 10px;
  }
  
  @media (max-width: 600px) {
    font-size: 1.4em;
    margin-bottom: 20px;
    padding-bottom: 8px;
  }
  
  @media (max-width: 480px) {
    font-size: 1.3em;
    margin-bottom: 18px;
    padding-bottom: 6px;
  }
  
  @media (max-width: 360px) {
    font-size: 1.2em;
    margin-bottom: 16px;
  }
`

const FormGroup = styled.div`
  margin-bottom: 25px;
`

const Label = styled.label`
  display: block;
  font-size: 0.9em;
  color: var(--text-light);
  margin-bottom: 8px;
  font-weight: 500;
`

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-light);
  color: var(--text);
  font-size: 0.95em;
  transition: all 0.2s ease;
  min-height: 44px; /* Better touch target */

  &:focus {
    outline: none;
    border-color: var(--primary);
    background: var(--bg-white);
  }

  &::placeholder {
    color: var(--text-lighter);
  }
  
  @media (max-width: 768px) {
    padding: 10px 14px;
    font-size: 0.9em;
    min-height: 42px;
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

const Textarea = styled.textarea`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-light);
  color: var(--text);
  font-size: 0.95em;
  min-height: 120px;
  resize: vertical;
  transition: all 0.2s ease;
  font-family: inherit;

  &:focus {
    outline: none;
    border-color: var(--primary);
    background: var(--bg-white);
  }

  &::placeholder {
    color: var(--text-lighter);
  }
`

const FileUploadArea = styled.div`
  border: 2px dashed var(--border);
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--bg-light);

  &:hover {
    border-color: var(--primary);
    background: rgba(21, 133, 161, 0.05);
  }

  input[type="file"] {
    display: none;
  }
`

const ImagePreview = styled.div`
  margin-top: 15px;
  position: relative;
  display: inline-block;

  img {
    max-width: 200px;
    max-height: 200px;
    border-radius: 12px;
    border: 2px solid var(--border);
  }
`

const CoverPreview = styled.div`
  margin-top: 15px;
  position: relative;
  display: inline-block;

  img {
    width: 100%;
    max-height: 200px;
    border-radius: 12px;
    border: 2px solid var(--border);
    object-fit: cover;
  }
`

const Button = styled.button`
  padding: 12px 24px;
  background: ${props => props.variant === 'danger' ? '#ef4444' : 'linear-gradient(135deg, var(--primary), var(--secondary))'};
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95em;
  font-weight: 500;
  transition: all 0.3s ease;
  margin-right: 10px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px ${props => props.variant === 'danger' ? 'rgba(239, 68, 68, 0.4)' : 'rgba(21, 133, 161, 0.4)'};
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`

const SecondaryButton = styled.button`
  padding: 12px 24px;
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95em;
  font-weight: 500;
  transition: all 0.3s ease;

  &:hover {
    background: var(--hover-bg);
    border-color: var(--primary);
  }
`

const ToggleSwitch = styled.label`
  position: relative;
  display: inline-block;
  width: 50px;
  height: 26px;

  input {
    opacity: 0;
    width: 0;
    height: 0;
  }

  .slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: 0.3s;
    border-radius: 26px;

    &:before {
      position: absolute;
      content: "";
      height: 20px;
      width: 20px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: 0.3s;
      border-radius: 50%;
    }
  }

  input:checked + .slider {
    background-color: var(--primary);
  }

  input:checked + .slider:before {
    transform: translateX(24px);
  }
`

const Divider = styled.hr`
  border: none;
  border-top: 1px solid var(--border);
  margin: 30px 0;
`

const InfoText = styled.p`
  font-size: 0.85em;
  color: var(--text-lighter);
  margin-top: 8px;
`

const ErrorMessage = styled.div`
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 0.9em;
`

const SuccessMessage = styled.div`
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 0.9em;
`

const LegalDocumentScroll = styled.div`
  max-height: min(70vh, 820px);
  overflow-y: auto;
  padding: 20px;
  background: var(--bg-light);
  border-radius: 8px;
  line-height: 1.6;
  color: var(--text);
`

const ModalOverlay = styled.div`
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
`

const ModalBox = styled.div`
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 32px;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
`

const ModalTitle = styled.h3`
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 6px 0;
`

const ModalSubtitle = styled.p`
  font-size: 0.875rem;
  color: var(--text-light);
  margin: 0 0 22px 0;
`

const ModalLabel = styled.label`
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 6px;
`

const ModalInput = styled.input`
  width: 100%;
  padding: 10px 13px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-light);
  color: var(--text);
  font-size: 0.9rem;
  outline: none;
  box-sizing: border-box;
  &:focus {
    border-color: var(--primary);
  }
`

const ModalSelect = styled.select`
  width: 100%;
  padding: 10px 13px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-light);
  color: var(--text);
  font-size: 0.9rem;
  outline: none;
  box-sizing: border-box;
  &:focus {
    border-color: var(--primary);
  }
`

const ModalTextarea = styled.textarea`
  width: 100%;
  padding: 10px 13px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-light);
  color: var(--text);
  font-size: 0.9rem;
  outline: none;
  resize: vertical;
  min-height: 110px;
  box-sizing: border-box;
  &:focus {
    border-color: var(--primary);
  }
`

const ModalFieldGroup = styled.div`
  margin-bottom: 16px;
`

const ModalActions = styled.div`
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 22px;
`

const ModalSuccessBox = styled.div`
  text-align: center;
  padding: 20px 0 8px;
`

const Settings = () => {
  const navigate = useNavigate()
  const { user, updateUser } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const showConfirm = useConfirm()
  const [activeSection, setActiveSection] = useState('profile')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Contact modals
  const [openModal, setOpenModal] = useState(null) // null | 'help' | 'enterprise'
  const [modalLoading, setModalLoading] = useState(false)
  const [modalError, setModalError] = useState('')
  const [modalSuccess, setModalSuccess] = useState(false)
  const [helpCategory, setHelpCategory] = useState('Technical Issue')
  const [helpSubject, setHelpSubject] = useState('')
  const [helpMessage, setHelpMessage] = useState('')
  const [entCompany, setEntCompany] = useState('')
  const [entRole, setEntRole] = useState('')
  const [entSubject, setEntSubject] = useState('')
  const [entMessage, setEntMessage] = useState('')

  const closeModal = () => {
    setOpenModal(null)
    setModalError('')
    setModalSuccess(false)
    setHelpCategory('Technical Issue')
    setHelpSubject('')
    setHelpMessage('')
    setEntCompany('')
    setEntRole('')
    setEntSubject('')
    setEntMessage('')
  }

  const submitContactForm = async (submissionType, subject, message, extra) => {
    setModalLoading(true)
    setModalError('')
    try {
      await api.post('/api/contact/submit', { submission_type: submissionType, subject, message, extra })
      setModalSuccess(true)
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Something went wrong. Please try again.'
      setModalError(typeof msg === 'string' ? msg : 'Something went wrong. Please try again.')
    } finally {
      setModalLoading(false)
    }
  }

  // Profile settings
  const [name, setName] = useState(user?.name || '')
  const [profilePic, setProfilePic] = useState(null)
  const [profilePicPreview, setProfilePicPreview] = useState(user?.profile_pic || '')
  const [coverPic, setCoverPic] = useState(null)
  const [coverPicPreview, setCoverPicPreview] = useState(user?.cover_pic || '')
  const [resume, setResume] = useState(null)
  const [resumeUploaded, setResumeUploaded] = useState(false) // Track if resume was just uploaded
  const [resumeFileName, setResumeFileName] = useState(null) // Store uploaded file name
  const [interests, setInterests] = useState(user?.interests || '')
  const [location, setLocation] = useState(user?.location || '')

  // Account settings
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [newEmail, setNewEmail] = useState(user?.email || '')

  // Security settings
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false)
  const [twoFactorVerified, setTwoFactorVerified] = useState(false)
  const [loading2FA, setLoading2FA] = useState(false)
  const [twoFactorSetup, setTwoFactorSetup] = useState(null) // { secret, qr_code, manual_entry_key }
  const [twoFactorCode, setTwoFactorCode] = useState('')
  const [backupCodes, setBackupCodes] = useState([])
  const [showBackupCodes, setShowBackupCodes] = useState(false)

  // Subscription & Quota Usage
  const [subscriptionPlan, setSubscriptionPlan] = useState('free')
  const [subscriptionStatus, setSubscriptionStatus] = useState('active')
  const [subscriptionLoading, setSubscriptionLoading] = useState(false)
  const [subscriptionLoaded, setSubscriptionLoaded] = useState(false)
  const [quotaUsage, setQuotaUsage] = useState(null)
  const [paddleSubscriptionId, setPaddleSubscriptionId] = useState(null)
  const [cancelEffectiveFrom, setCancelEffectiveFrom] = useState('next_billing_period')
  const [billingBusy, setBillingBusy] = useState(false)

  // Refs for timeout cleanup
  const timeoutRefs = useRef([])

  // Load user data on mount and when user changes
  useEffect(() => {
    if (user) {
      setName(user.name || '')
      setProfilePicPreview(user.profile_pic || '')
      setCoverPicPreview(user.cover_pic || '')
      setInterests(user.interests || '')
      setLocation(user.location || '')
      setNewEmail(user.email || '')
      
      // Load 2FA status from user profile
      if (user.two_factor_enabled !== undefined) {
        setTwoFactorEnabled(user.two_factor_enabled)
      }
    }
  }, [user])

  // Load subscription and quota usage from server
  useEffect(() => {
    const loadSubscriptionUsage = async () => {
      try {
        setSubscriptionLoading(true)
        const [usageRes, subRes] = await Promise.all([
          userAPI.getSubscriptionUsage(),
          userAPI.getSubscription().catch(() => ({ data: null })),
        ])
        if (usageRes.data) {
          const { plan, usage } = usageRes.data
          setSubscriptionPlan(plan?.plan_name || 'free')
          setSubscriptionStatus(plan?.status || 'active')
          setQuotaUsage(usage)
        }
        if (subRes.data?.paddle_subscription_id) {
          setPaddleSubscriptionId(subRes.data.paddle_subscription_id)
        } else {
          setPaddleSubscriptionId(null)
        }
      } catch (err) {
        console.error('Failed to load subscription usage:', err)
        setSubscriptionPlan('free')
        setSubscriptionStatus('active')
        setPaddleSubscriptionId(null)
      } finally {
        setSubscriptionLoading(false)
        setSubscriptionLoaded(true)
      }
    }
    loadSubscriptionUsage()
  }, [user])

  const refreshSubscriptionData = async () => {
    try {
      const [usageRes, subRes] = await Promise.all([
        userAPI.getSubscriptionUsage(),
        userAPI.getSubscription().catch(() => ({ data: null })),
      ])
      if (usageRes.data) {
        const { plan, usage } = usageRes.data
        setSubscriptionPlan(plan?.plan_name || 'free')
        setSubscriptionStatus(plan?.status || 'active')
        setQuotaUsage(usage)
      }
      if (subRes.data?.paddle_subscription_id) {
        setPaddleSubscriptionId(subRes.data.paddle_subscription_id)
      } else {
        setPaddleSubscriptionId(null)
      }
    } catch (e) {
      console.error(e)
    }
  }

  const handleCancelPaddleSubscription = async () => {
    setBillingBusy(true)
    setError('')
    setSuccess('')
    try {
      await userAPI.cancelSubscription({ effective_from: cancelEffectiveFrom })
      setSuccess(
        cancelEffectiveFrom === 'immediately'
          ? 'Cancellation requested. Access may end shortly once Paddle confirms.'
          : 'Cancellation scheduled for the end of your billing period.'
      )
      await refreshSubscriptionData()
    } catch (err) {
      const d = err.response?.data?.detail
      setError(typeof d === 'string' ? d : err.message || 'Could not cancel subscription')
    } finally {
      setBillingBusy(false)
    }
  }

  const handleChangePaddlePlan = async (targetPlan) => {
    setBillingBusy(true)
    setError('')
    setSuccess('')
    try {
      await userAPI.changeSubscriptionPlan({
        plan: targetPlan,
        proration_billing_mode: 'prorated_immediately',
      })
      setSuccess('Plan change submitted. It may take a moment to appear.')
      await refreshSubscriptionData()
    } catch (err) {
      const d = err.response?.data?.detail
      setError(typeof d === 'string' ? d : err.message || 'Could not change plan')
    } finally {
      setBillingBusy(false)
    }
  }

  // Cleanup timeouts on unmount
  useEffect(() => {
    return () => {
      // Clear any pending timeouts when component unmounts
      timeoutRefs.current.forEach(timeoutId => clearTimeout(timeoutId))
      timeoutRefs.current = []
    }
  }, [])

  const handleProfilePicChange = (e) => {
    const file = e.target.files[0]
    if (!file) return

    if (!file.type.startsWith('image/')) {
      setError('Please select an image file')
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      setError('Image size should be less than 5MB')
      return
    }

    setProfilePic(file)
    const reader = new FileReader()
    reader.onloadend = () => setProfilePicPreview(reader.result)
    reader.readAsDataURL(file)
  }

  const handleCoverPicChange = (e) => {
    const file = e.target.files[0]
    if (!file) return

    if (!file.type.startsWith('image/')) {
      setError('Please select an image file')
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      setError('Image size should be less than 5MB')
      return
    }

    setCoverPic(file)
    const reader = new FileReader()
    reader.onloadend = () => setCoverPicPreview(reader.result)
    reader.readAsDataURL(file)
  }

  const handleResumeChange = (e) => {
    const file = e.target.files[0]
    if (!file) return

    // Validate file type (PDF, Word, or TXT)
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ]
    
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|doc|docx|txt)$/i)) {
      setError('Please select a PDF, Word, or TXT file')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('Resume size should be less than 10MB')
      return
    }

    setResume(file)
    setResumeUploaded(false) // Reset upload status when new file selected
    setError('') // Clear previous errors
  }

  const saveProfileSettings = async () => {
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const trimmedInterests = (interests && interests.trim()) || ''
      if (trimmedInterests.length > 1000) {
        setError('Interests must be less than 1000 characters')
        setLoading(false)
        return
      }

      const trimmedLocation = (location && location.trim()) || ''
      if (trimmedLocation.length > 150) {
        setError('Location must be less than 150 characters')
        setLoading(false)
        return
      }

      const hasFiles = !!(resume || profilePic || coverPic)
      const jsonPayload = {}
      if (trimmedInterests) jsonPayload.interests = trimmedInterests
      if (trimmedLocation) jsonPayload.location = trimmedLocation

      if (!hasFiles && Object.keys(jsonPayload).length === 0) {
        setError('No changes to save')
        setLoading(false)
        return
      }

      const resumeLabel = resume?.name
      let response

      if (hasFiles) {
        const formData = new FormData()
        if (resume) formData.append('resume', resume)
        if (profilePic) formData.append('profile_pic', profilePic)
        if (coverPic) formData.append('cover_pic', coverPic)
        if (trimmedInterests) formData.append('interests', trimmedInterests)
        if (trimmedLocation) formData.append('location', trimmedLocation)
        response = await api.put('/api/user/profile', formData)
      } else {
        response = await api.put('/api/user/profile', jsonPayload)
      }

      if (updateUser && response.data) {
        updateUser({ ...user, ...response.data })
      }

      const vid = response.data?.id ?? response.data?.uid ?? user?.id ?? user?.uid
      if (vid != null) {
        window.dispatchEvent(new CustomEvent('zedreq:profile-updated', { detail: { userId: vid } }))
      }

      if (response.data?.profile_pic) setProfilePicPreview(response.data.profile_pic)
      if (response.data?.cover_pic) setCoverPicPreview(response.data.cover_pic)

      if (resumeLabel) {
        setSuccess(`Resume "${resumeLabel}" uploaded and processed successfully! Your profile has been updated.`)
        setResumeUploaded(true)
      } else {
        setSuccess('Profile updated successfully!')
      }

      setProfilePic(null)
      setCoverPic(null)
      setResume(null)

      const timeoutId = setTimeout(() => {
        setSuccess('')
        setResumeUploaded(false)
      }, 5000)
      timeoutRefs.current.push(timeoutId)
    } catch (error) {
      // Handle rate limiting errors
      if (error.response?.status === 429) {
        const retryAfter = error.response?.headers['retry-after'] || 60
        setError(`Too many requests. Please wait ${retryAfter} seconds before trying again.`)
      } else {
        setError(error.response?.data?.detail || error.message || 'Failed to update profile')
      }
    } finally {
      setLoading(false)
    }
  }

  const saveAccountSettings = async () => {
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const updatedFields = []

      // Validate and update name
      if (name && name.trim() && name.trim() !== user?.name) {
        const trimmedName = name.trim()
        if (trimmedName.length > 100) {
          setError('Name must be less than 100 characters')
          setLoading(false)
          return
        }
        if (trimmedName.length === 0) {
          setError('Name cannot be empty')
          setLoading(false)
          return
        }

        try {
          const response = await api.put('/api/user/profile', { name: trimmedName })
          if (updateUser && response.data) {
            // Use the full response from the API to update user state
            updateUser({ ...user, ...response.data })
          }
          updatedFields.push('name')
        } catch (nameError) {
          if (nameError.response?.status === 429) {
            const retryAfter = nameError.response?.headers['retry-after'] || 60
            setError(`Too many requests. Please wait ${retryAfter} seconds before trying again.`)
          } else {
            setError(nameError.response?.data?.detail || 'Failed to update name')
          }
          setLoading(false)
          return
        }
      }

      // Validate and update password
      if (newPassword) {
        if (!currentPassword) {
          setError('Please enter your current password')
          setLoading(false)
          return
        }

        if (newPassword !== confirmPassword) {
          setError('New passwords do not match')
          setLoading(false)
          return
        }

        if (newPassword.length < 8) {
          setError('Password must be at least 8 characters')
          setLoading(false)
          return
        }

        if (newPassword.length > 25) {
          setError('Password must be less than 25 characters')
          setLoading(false)
          return
        }

        // Check for at least one uppercase letter (client-side validation)
        if (!/[A-Z]/.test(newPassword)) {
          setError('Password must contain at least one uppercase letter')
          setLoading(false)
          return
        }

        try {
          await api.put('/api/user/change-password', {
            current_password: currentPassword,
            new_password: newPassword
          })
          setCurrentPassword('')
          setNewPassword('')
          setConfirmPassword('')
          updatedFields.push('password')
        } catch (passwordError) {
          if (passwordError.response?.status === 429) {
            const retryAfter = passwordError.response?.headers['retry-after'] || 60
            setError(`Too many password change attempts. Please wait ${retryAfter} seconds.`)
          } else {
            setError(passwordError.response?.data?.detail || 'Failed to change password')
          }
          setLoading(false)
          return
        }
      }

      // Validate and update email
      if (newEmail && newEmail !== user?.email) {
        // Basic email validation (client-side)
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(newEmail)) {
          setError('Please enter a valid email address')
          setLoading(false)
          return
        }

        try {
          await api.put('/api/user/email', { email: newEmail })
          if (updateUser) {
            updateUser({ ...user, email: newEmail })
          }
          updatedFields.push('email')
        } catch (emailError) {
          if (emailError.response?.status === 429) {
            const retryAfter = emailError.response?.headers['retry-after'] || 60
            setError(`Too many email update attempts. Please wait ${retryAfter} seconds.`)
          } else {
            setError(emailError.response?.data?.detail || 'Failed to update email')
          }
          setLoading(false)
          return
        }
      }

      // Show success message based on what was updated
      if (updatedFields.length > 0) {
        const fieldNames = updatedFields.map(field => {
          if (field === 'name') return 'Name'
          if (field === 'password') return 'Password'
          if (field === 'email') return 'Email'
          return field
        })
        const message = updatedFields.length === 1
          ? `${fieldNames[0]} updated successfully!`
          : `${fieldNames.join(', ')} updated successfully!`
        setSuccess(message)
        
        // Refresh user data from server to ensure everything is in sync
        try {
          const userResponse = await userAPI.getCurrentUser()
          if (updateUser && userResponse.data) {
            updateUser(userResponse.data)
          }
        } catch (refreshError) {
          // Don't fail the update if refresh fails, just log it
          console.warn('Failed to refresh user data:', refreshError)
        }
      } else {
        setError('No changes to save')
      }

      // Clear success message after 5 seconds
      if (updatedFields.length > 0) {
        setTimeout(() => setSuccess(''), 5000)
      }
    } catch (error) {
      if (error.response?.status === 429) {
        const retryAfter = error.response?.headers['retry-after'] || 60
        setError(`Too many requests. Please wait ${retryAfter} seconds before trying again.`)
      } else {
        setError(error.response?.data?.detail || error.message || 'Failed to update account settings')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteAccount = async () => {
    const isGoogleUser = user?.auth_provider === 'google'

    const firstConfirm = await showConfirm({
      title: 'Delete Account',
      message: 'Are you sure you want to delete your account? This action cannot be undone and all your data will be permanently lost.',
      buttons: [
        { label: 'Cancel', variant: 'secondary', value: false },
        { label: 'Continue', variant: 'danger', value: true },
      ],
    })
    if (!firstConfirm) return

    let password = ''

    if (isGoogleUser) {
      // Google users have no password — just ask for a final confirmation
      const finalConfirm = await showConfirm({
        title: 'Final Confirmation',
        message: 'This will permanently delete your profile, posts, connections, and all associated data. There is no way to recover your account after this.',
        buttons: [
          { label: 'Go Back', variant: 'secondary', value: false },
          { label: 'Yes, Delete My Account', variant: 'danger', value: true },
        ],
      })
      if (!finalConfirm) return
    } else {
      // Email/password users must confirm with their current password
      const enteredPassword = await showConfirm({
        title: 'Confirm Your Password',
        message: 'Enter your current password to permanently delete your account. This will remove your profile, posts, connections, and all associated data.',
        input: {
          type: 'password',
          label: 'Current Password',
          placeholder: 'Enter your password',
        },
        buttons: [
          { label: 'Cancel', variant: 'secondary', value: null },
          { label: 'Delete My Account', variant: 'danger', submitsInput: true },
        ],
      })
      if (!enteredPassword) return
      password = enteredPassword
    }

    setLoading(true)
    setError('')
    try {
      await api.delete('/api/user/account', { data: { password } })
      navigate('/landing')
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to delete account')
      setLoading(false)
    }
  }

  const updateSubscription = async () => {
    setSubscriptionLoading(true)
    setError('')
    setSuccess('')

    try {
      // Validate subscription plan
      if (!['free', 'pro', 'premium'].includes(subscriptionPlan)) {
        setError('Invalid subscription plan selected')
        setSubscriptionLoading(false)
        return
      }

      const response = await api.put('/api/user/subscription', { plan: subscriptionPlan })
      
      if (response.data) {
        setSubscriptionPlan(response.data.plan || subscriptionPlan)
        setSubscriptionStatus(response.data.status || 'active')
        setSuccess(`Subscription updated to ${subscriptionPlan} plan successfully!`)
        
        // Clear success message after 5 seconds
        const timeoutId = setTimeout(() => setSuccess(''), 5000)
        timeoutRefs.current.push(timeoutId)
      }
    } catch (error) {
      if (error.response?.status === 429) {
        const retryAfter = error.response?.headers['retry-after'] || 60
        setError(`Too many requests. Please wait ${retryAfter} seconds before trying again.`)
      } else {
        setError(error.response?.data?.detail || 'Failed to update subscription')
      }
    } finally {
      setSubscriptionLoading(false)
    }
  }

  // Load 2FA status on mount
  useEffect(() => {
    const load2FAStatus = async () => {
      try {
        const response = await api.get('/api/user/2fa/status')
        if (response.data) {
          setTwoFactorEnabled(response.data.enabled || false)
          setTwoFactorVerified(response.data.verified || false)
        }
      } catch (error) {
        console.warn('Failed to load 2FA status:', error)
        // Set defaults if API fails - ensure toggle button is visible
        setTwoFactorEnabled(false)
        setTwoFactorVerified(false)
      }
    }
    if (user) {
      load2FAStatus()
    }
  }, [user])

  const setup2FA = async () => {
    setLoading2FA(true)
    setError('')
    setSuccess('')
    
    try {
      const response = await api.post('/api/user/2fa/setup')
      setTwoFactorSetup(response.data)
      setSuccess('Scan the QR code with your authenticator app')
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to setup 2FA')
    } finally {
      setLoading2FA(false)
    }
  }

  const verify2FASetup = async () => {
    if (!twoFactorCode || twoFactorCode.length !== 6) {
      setError('Please enter a 6-digit code')
      return
    }

    setLoading2FA(true)
    setError('')
    setSuccess('')

    try {
      const response = await api.post('/api/user/2fa/verify-setup', { code: twoFactorCode })
      setTwoFactorEnabled(true)
      setTwoFactorVerified(true)
      setBackupCodes(response.data.backup_codes || [])
      setShowBackupCodes(true)
      setTwoFactorSetup(null)
      setTwoFactorCode('')
      setSuccess('2FA enabled successfully! Please save your backup codes.')
      
      if (updateUser) {
        updateUser({ ...user, two_factor_enabled: true })
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Invalid code. Please try again.')
    } finally {
      setLoading2FA(false)
    }
  }

  const disable2FA = async () => {
    if (!window.confirm('Are you sure you want to disable 2FA? This will make your account less secure.')) {
      return
    }

    setLoading2FA(true)
    setError('')
    setSuccess('')

    try {
      await api.delete('/api/user/2fa')
      setTwoFactorEnabled(false)
      setTwoFactorVerified(false)
      setTwoFactorSetup(null)
      setBackupCodes([])
      setShowBackupCodes(false)
      setSuccess('2FA disabled successfully')
      
      if (updateUser) {
        updateUser({ ...user, two_factor_enabled: false })
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to disable 2FA')
    } finally {
      setLoading2FA(false)
    }
  }

  const getBackupCodes = async () => {
    setLoading2FA(true)
    setError('')
    
    try {
      const response = await api.get('/api/user/2fa/backup-codes')
      setBackupCodes(response.data.backup_codes || [])
      setShowBackupCodes(true)
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to get backup codes')
    } finally {
      setLoading2FA(false)
    }
  }

  const regenerateBackupCodes = async () => {
    if (!window.confirm('Regenerating backup codes will invalidate your existing codes. Continue?')) {
      return
    }

    setLoading2FA(true)
    setError('')
    
    try {
      const response = await api.post('/api/user/2fa/regenerate-backup-codes')
      setBackupCodes(response.data.backup_codes || [])
      setShowBackupCodes(true)
      setSuccess('New backup codes generated. Save them in a safe place.')
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to regenerate backup codes')
    } finally {
      setLoading2FA(false)
    }
  }

  const renderContent = () => {
    switch (activeSection) {
      case 'profile':
        return (
          <>
            <SectionTitle>Profile Settings</SectionTitle>
            
            <FormGroup>
              <Label>Profile Picture</Label>
              <FileUploadArea onClick={() => document.getElementById('profile-pic').click()}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ margin: '0 auto 10px', color: 'var(--text-light)' }}>
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                <p>Click to upload profile picture</p>
                <InfoText>Max size: 5MB (JPG, PNG, GIF)</InfoText>
                <input
                  id="profile-pic"
                  type="file"
                  accept="image/*"
                  onChange={handleProfilePicChange}
                />
              </FileUploadArea>
              {profilePicPreview && (
                <ImagePreview>
                  <img src={profilePicPreview} alt="Profile preview" />
                </ImagePreview>
              )}
            </FormGroup>

            <FormGroup>
              <Label>Cover Picture</Label>
              <FileUploadArea onClick={() => document.getElementById('cover-pic').click()}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ margin: '0 auto 10px', color: 'var(--text-light)' }}>
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <circle cx="8.5" cy="8.5" r="1.5"></circle>
                  <polyline points="21 15 16 10 5 21"></polyline>
                </svg>
                <p>Click to upload cover picture</p>
                <InfoText>Max size: 5MB (JPG, PNG, GIF)</InfoText>
                <input
                  id="cover-pic"
                  type="file"
                  accept="image/*"
                  onChange={handleCoverPicChange}
                />
              </FileUploadArea>
              {coverPicPreview && (
                <CoverPreview>
                  <img src={coverPicPreview} alt="Cover preview" />
                </CoverPreview>
              )}
            </FormGroup>

            <FormGroup>
              <Label>Resume (PDF, DOC, DOCX, TXT)</Label>
              <FileUploadArea onClick={() => document.getElementById('resume').click()}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ margin: '0 auto 10px', color: 'var(--text-light)' }}>
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                <p>Click to upload resume</p>
                <InfoText>Max size: 10MB (PDF, DOC, DOCX, TXT)</InfoText>
                <input
                  id="resume"
                  type="file"
                  accept=".pdf,.doc,.docx,.txt,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
                  onChange={handleResumeChange}
                />
              </FileUploadArea>
              {resume && (
                <InfoText style={{ color: 'var(--primary)', fontWeight: '500' }}>
                  ✓ Selected: {resume.name}
                </InfoText>
              )}
              {resumeUploaded && resumeFileName && (
                <InfoText style={{ color: '#22c55e', fontWeight: '500', marginTop: '8px' }}>
                  ✓ Resume "{resumeFileName}" uploaded and processed successfully!
                </InfoText>
              )}
            </FormGroup>

            <FormGroup>
              <Label>Interests</Label>
              <Textarea
                value={interests}
                onChange={(e) => setInterests(e.target.value)}
                placeholder="Enter your interests (e.g., Technology, Music, Travel, Sports...)"
              />
              <InfoText>Separate multiple interests with commas</InfoText>
            </FormGroup>

            <FormGroup>
              <Label>Location</Label>
              <Input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Enter your location"
              />
            </FormGroup>

            <Button onClick={saveProfileSettings} disabled={loading}>
              {loading ? 'Saving...' : 'Save Changes'}
            </Button>
          </>
        )

      case 'account':
        return (
          <>
            <SectionTitle>Account Settings</SectionTitle>

            <FormGroup>
              <Label>Full Name</Label>
              <Input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your full name"
                maxLength={100}
              />
              <InfoText>This is your display name shown on your profile</InfoText>
            </FormGroup>

            <FormGroup>
              <Label>Email Address</Label>
              <Input
                type="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                placeholder="Enter your email"
              />
            </FormGroup>

            <Divider />

            <FormGroup>
              <Label>Current Password</Label>
              <Input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="Enter current password"
              />
            </FormGroup>

            <FormGroup>
              <Label>New Password</Label>
              <Input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Enter new password"
              />
              <InfoText>Password must be at least 8 characters</InfoText>
            </FormGroup>

            <FormGroup>
              <Label>Confirm New Password</Label>
              <Input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm new password"
              />
            </FormGroup>

            <Button onClick={saveAccountSettings} disabled={loading}>
              {loading ? 'Saving...' : 'Save Changes'}
            </Button>
          </>
        )

      case 'security':
        return (
          <>
            <SectionTitle>Security Settings</SectionTitle>

            <FormGroup>
              <Label>Two-Factor Authentication (2FA)</Label>
              <InfoText>Add an extra layer of security to your account using an authenticator app</InfoText>
              
              {/* Simple toggle button - always visible based on database state */}
              <div style={{ marginTop: '15px' }}>
                <Button 
                  onClick={twoFactorEnabled ? disable2FA : setup2FA} 
                  disabled={loading2FA}
                  style={{
                    background: twoFactorEnabled ? 'var(--success)' : 'var(--primary)',
                    minWidth: '180px',
                    fontSize: '1em',
                    padding: '12px 24px'
                  }}
                >
                  {loading2FA 
                    ? 'Processing...' 
                    : twoFactorEnabled 
                      ? '✓ 2FA Enabled (Click to Disable)' 
                      : 'Enable 2FA'}
                </Button>
              </div>
              
              {/* Status indicator */}
              <div style={{ 
                marginTop: '15px', 
                padding: '12px', 
                background: twoFactorEnabled ? 'rgba(40, 167, 69, 0.1)' : 'rgba(108, 117, 125, 0.1)', 
                borderRadius: '8px',
                border: `1px solid ${twoFactorEnabled ? 'var(--success)' : 'var(--border)'}`,
                color: twoFactorEnabled ? 'var(--success)' : 'var(--text-light)',
                fontWeight: 500
              }}>
                <strong>Status:</strong> {twoFactorEnabled ? 'Enabled' : 'Disabled'}
              </div>

              {twoFactorSetup && (
                <div style={{ marginTop: '20px', padding: '20px', background: 'var(--bg-light)', borderRadius: '8px' }}>
                  <h4 style={{ margin: '0 0 15px 0', color: 'var(--text)' }}>Scan QR Code</h4>
                  <p style={{ margin: '0 0 15px 0', color: 'var(--text-light)', fontSize: '0.9em' }}>
                    Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
                  </p>
                  <div style={{ textAlign: 'center', marginBottom: '20px' }}>
                    <img 
                      src={twoFactorSetup.qr_code} 
                      alt="2FA QR Code" 
                      style={{ maxWidth: '250px', border: '1px solid var(--border)', borderRadius: '8px' }}
                    />
                  </div>
                  <div style={{ marginBottom: '20px' }}>
                    <Label>Manual Entry Key (if QR code doesn't work):</Label>
                    <div style={{ 
                      padding: '10px', 
                      background: 'var(--bg-white)', 
                      borderRadius: '4px',
                      fontFamily: 'monospace',
                      fontSize: '0.9em',
                      wordBreak: 'break-all'
                    }}>
                      {twoFactorSetup.manual_entry_key}
                    </div>
                  </div>
                  <div>
                    <Label>Enter 6-digit code from your app:</Label>
                    <Input
                      type="text"
                      value={twoFactorCode}
                      onChange={(e) => setTwoFactorCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                      placeholder="000000"
                      maxLength={6}
                      style={{ fontFamily: 'monospace', fontSize: '1.2em', letterSpacing: '0.5em', textAlign: 'center' }}
                    />
                    <div style={{ marginTop: '15px', display: 'flex', gap: '10px' }}>
                      <Button onClick={verify2FASetup} disabled={loading2FA || twoFactorCode.length !== 6}>
                        {loading2FA ? 'Verifying...' : 'Verify & Enable'}
                      </Button>
                      <SecondaryButton onClick={() => { setTwoFactorSetup(null); setTwoFactorCode('') }}>
                        Cancel
                      </SecondaryButton>
                    </div>
                  </div>
                </div>
              )}

              {twoFactorEnabled && twoFactorVerified && (
                <div style={{ marginTop: '20px' }}>
                  <div style={{ 
                    padding: '15px', 
                    background: 'var(--success)', 
                    color: 'white', 
                    borderRadius: '8px',
                    marginBottom: '15px'
                  }}>
                    ✓ 2FA is enabled and active
                  </div>
                  
                  <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
                    <SecondaryButton onClick={getBackupCodes} disabled={loading2FA}>
                      View Backup Codes
                    </SecondaryButton>
                    <SecondaryButton onClick={regenerateBackupCodes} disabled={loading2FA}>
                      Regenerate Backup Codes
                    </SecondaryButton>
                  </div>

                  {showBackupCodes && backupCodes.length > 0 && (
                    <div style={{ 
                      marginTop: '15px', 
                      padding: '20px', 
                      background: 'var(--bg-light)', 
                      borderRadius: '8px',
                      border: '2px solid var(--warning)'
                    }}>
                      <h4 style={{ margin: '0 0 10px 0', color: 'var(--warning)' }}>
                        ⚠️ Save These Backup Codes
                      </h4>
                      <p style={{ margin: '0 0 15px 0', color: 'var(--text-light)', fontSize: '0.9em' }}>
                        Store these codes in a safe place. Each code can only be used once if you lose access to your authenticator app.
                      </p>
                      <div style={{ 
                        display: 'grid', 
                        gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))', 
                        gap: '10px',
                        marginBottom: '15px'
                      }}>
                        {backupCodes.map((code, index) => (
                          <div 
                            key={index}
                            style={{
                              padding: '8px',
                              background: 'var(--bg-white)',
                              borderRadius: '4px',
                              fontFamily: 'monospace',
                              textAlign: 'center',
                              fontSize: '0.9em'
                            }}
                          >
                            {code}
                          </div>
                        ))}
                      </div>
                      <Button onClick={() => setShowBackupCodes(false)}>
                        I've Saved These Codes
                      </Button>
                    </div>
                  )}

                  <div style={{ marginTop: '20px' }}>
                    <Button 
                      variant="danger" 
                      onClick={disable2FA} 
                      disabled={loading2FA}
                    >
                      {loading2FA ? 'Disabling...' : 'Disable 2FA'}
                    </Button>
                  </div>
                </div>
              )}
            </FormGroup>

            <Divider />

            <FormGroup>
              <Label>Delete Account</Label>
              <InfoText>Once you delete your account, there is no going back. Please be certain.</InfoText>
              <Button variant="danger" onClick={handleDeleteAccount} disabled={loading} style={{ marginTop: '15px' }}>
                {loading ? 'Deleting...' : 'Delete Account'}
              </Button>
            </FormGroup>
          </>
        )

      case 'subscription':
        return (
          <>
            <SectionTitle>Subscription & Usage</SectionTitle>

            <FormGroup>
              <Label>Current Plan</Label>
              <div style={{ 
                padding: '20px', 
                background: 'var(--bg-light)', 
                borderRadius: '8px',
                border: '2px solid var(--border)'
              }}>
                <h3 style={{ margin: '0 0 10px 0', color: 'var(--primary)', textTransform: 'capitalize' }}>
                  {subscriptionPlan} Plan
                </h3>
                <p style={{ margin: '0 0 10px 0', color: 'var(--text-light)' }}>
                  {subscriptionPlan === 'free' ? 'Basic features included' : 
                   subscriptionPlan === 'pro' ? 'Enhanced features and higher limits' :
                   subscriptionPlan === 'premium' ? 'Advanced features with generous limits' :
                   subscriptionPlan === 'enterprise' ? 'Unlimited access with premium features' : 
                   'Basic features included'}
                </p>
                <p style={{ margin: 0, fontSize: '0.9em', color: subscriptionStatus === 'active' ? 'var(--success)' : 'var(--error)', fontWeight: 500 }}>
                  Status: {subscriptionStatus.charAt(0).toUpperCase() + subscriptionStatus.slice(1)}
                </p>
              </div>
            </FormGroup>

            {/* Monthly Usage Quotas */}
            {quotaUsage && (
              <FormGroup>
                <Label>Monthly Usage</Label>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {/* AI Messages */}
                  {(() => {
                    const ai = quotaUsage.ai_messages
                    const isUnlimited = ai?.limit === -1
                    const pct = isUnlimited ? 0 : (ai?.limit > 0 ? Math.min(100, Math.round((ai?.used / ai?.limit) * 100)) : 0)
                    return (
                      <div style={{ padding: '14px', background: 'var(--bg-light)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                          <span style={{ fontWeight: 500, fontSize: '0.9em' }}>AI Messages (Nemz)</span>
                          <span style={{ fontSize: '0.85em', color: pct >= 90 && !isUnlimited ? '#e74c3c' : 'var(--text-light)' }}>
                            {ai?.used ?? 0} / {isUnlimited ? '∞' : (ai?.limit ?? 0)}
                          </span>
                        </div>
                        {!isUnlimited && (
                          <div style={{ width: '100%', height: '6px', background: 'var(--border)', borderRadius: '3px', overflow: 'hidden' }}>
                            <div style={{ width: `${pct}%`, height: '100%', background: pct >= 90 ? '#e74c3c' : pct >= 70 ? '#f39c12' : 'var(--primary)', borderRadius: '3px', transition: 'width 0.3s ease' }} />
                          </div>
                        )}
                        <p style={{ margin: '4px 0 0', fontSize: '0.8em', color: 'var(--text-light)' }}>
                          {isUnlimited ? 'Unlimited messages' : `${ai?.remaining ?? 0} remaining this month`}
                        </p>
                      </div>
                    )
                  })()}

                  {/* Course Enrollments */}
                  {(() => {
                    const ce = quotaUsage.course_enrollments
                    const isUnlimited = ce?.limit === -1
                    const pct = isUnlimited ? 0 : (ce?.limit > 0 ? Math.min(100, Math.round((ce?.used / ce?.limit) * 100)) : 0)
                    return (
                      <div style={{ padding: '14px', background: 'var(--bg-light)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                          <span style={{ fontWeight: 500, fontSize: '0.9em' }}>Course Enrollments (LMS)</span>
                          <span style={{ fontSize: '0.85em', color: pct >= 90 && !isUnlimited ? '#e74c3c' : 'var(--text-light)' }}>
                            {ce?.used ?? 0} / {isUnlimited ? '∞' : (ce?.limit ?? 0)}
                          </span>
                        </div>
                        {!isUnlimited && (
                          <div style={{ width: '100%', height: '6px', background: 'var(--border)', borderRadius: '3px', overflow: 'hidden' }}>
                            <div style={{ width: `${pct}%`, height: '100%', background: pct >= 90 ? '#e74c3c' : pct >= 70 ? '#f39c12' : 'var(--primary)', borderRadius: '3px', transition: 'width 0.3s ease' }} />
                          </div>
                        )}
                        <p style={{ margin: '4px 0 0', fontSize: '0.8em', color: 'var(--text-light)' }}>
                          {isUnlimited ? 'Unlimited enrollments' : `${ce?.remaining ?? 0} remaining this month`}
                        </p>
                      </div>
                    )
                  })()}

                  {/* Interview Sessions */}
                  {(() => {
                    const iv = quotaUsage.interview_sessions
                    const isUnlimited = iv?.limit === -1
                    const pct = isUnlimited ? 0 : (iv?.limit > 0 ? Math.min(100, Math.round((iv?.used / iv?.limit) * 100)) : 0)
                    return (
                      <div style={{ padding: '14px', background: 'var(--bg-light)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                          <span style={{ fontWeight: 500, fontSize: '0.9em' }}>AI Mock Interviews</span>
                          <span style={{ fontSize: '0.85em', color: pct >= 90 && !isUnlimited ? '#e74c3c' : 'var(--text-light)' }}>
                            {iv?.used ?? 0} / {isUnlimited ? '∞' : (iv?.limit ?? 0)}
                          </span>
                        </div>
                        {!isUnlimited && (
                          <div style={{ width: '100%', height: '6px', background: 'var(--border)', borderRadius: '3px', overflow: 'hidden' }}>
                            <div style={{ width: `${pct}%`, height: '100%', background: pct >= 90 ? '#e74c3c' : pct >= 70 ? '#f39c12' : 'var(--primary)', borderRadius: '3px', transition: 'width 0.3s ease' }} />
                          </div>
                        )}
                        <p style={{ margin: '4px 0 0', fontSize: '0.8em', color: 'var(--text-light)' }}>
                          {isUnlimited ? 'Unlimited sessions (max 10 min each)' : `${iv?.remaining ?? 0} remaining this month (max 1 min each)`}
                        </p>
                      </div>
                    )
                  })()}
                </div>
              </FormGroup>
            )}

            <FormGroup>
              <Label>Plan Options</Label>
              <div style={{ 
                padding: '15px', 
                background: 'rgba(108, 117, 125, 0.1)', 
                borderRadius: '8px',
                border: '1px solid var(--border)',
                color: 'var(--text-light)'
              }}>
                <p style={{ margin: 0, fontSize: '0.9em' }}>
                  <strong>Note:</strong> Enterprise plans are assigned by administrators.
                  Paid self-serve plans use Paddle; use Manage subscription below when linked.
                </p>
              </div>
              <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', marginTop: '15px' }}>
                <SecondaryButton 
                  disabled={true}
                  style={{ 
                    borderColor: subscriptionPlan === 'free' ? 'var(--primary)' : 'var(--border)',
                    background: subscriptionPlan === 'free' ? 'rgba(21, 133, 161, 0.1)' : 'transparent',
                    cursor: 'not-allowed',
                    opacity: subscriptionPlan === 'free' ? 1 : 0.5
                  }}
                >
                  Free Plan {subscriptionPlan === 'free' ? '(Current)' : ''}
                </SecondaryButton>
                <SecondaryButton 
                  disabled={true}
                  style={{ 
                    borderColor: subscriptionPlan === 'pro' ? 'var(--primary)' : 'var(--border)',
                    background: subscriptionPlan === 'pro' ? 'rgba(21, 133, 161, 0.1)' : 'transparent',
                    cursor: 'not-allowed',
                    opacity: subscriptionPlan === 'pro' ? 1 : 0.5
                  }}
                >
                  Pro Plan {subscriptionPlan === 'pro' ? '(Current)' : '- $49.99/month'}
                </SecondaryButton>
                <SecondaryButton 
                  disabled={true}
                  style={{ 
                    borderColor: subscriptionPlan === 'premium' ? '#8e44ad' : 'var(--border)',
                    background: subscriptionPlan === 'premium' ? 'rgba(142, 68, 173, 0.1)' : 'transparent',
                    cursor: 'not-allowed',
                    opacity: subscriptionPlan === 'premium' ? 1 : 0.5
                  }}
                >
                  Premium Plan {subscriptionPlan === 'premium' ? '(Current)' : '- $89.99/month'}
                </SecondaryButton>
                <SecondaryButton 
                  disabled={true}
                  style={{ 
                    borderColor: subscriptionPlan === 'enterprise' ? '#27ae60' : 'var(--border)',
                    background: subscriptionPlan === 'enterprise' ? 'rgba(39, 174, 96, 0.1)' : 'transparent',
                    cursor: 'not-allowed',
                    opacity: subscriptionPlan === 'enterprise' ? 1 : 0.5
                  }}
                >
                  Enterprise {subscriptionPlan === 'enterprise' ? '(Current)' : '- Contact Us'}
                </SecondaryButton>
              </div>
            </FormGroup>

            {(subscriptionPlan === 'free' || subscriptionPlan === 'pro' || subscriptionPlan === 'premium') && (
              <FormGroup>
                <Label>Manage subscription</Label>
                {subscriptionPlan === 'free' && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', alignItems: 'center' }}>
                    <span style={{ color: 'var(--text-light)', fontSize: '0.9em' }}>Upgrade to a paid plan:</span>
                    <Link to="/choose-plan" style={{ color: 'var(--primary)', fontWeight: 600 }}>Choose a plan</Link>
                  </div>
                )}
                {(subscriptionPlan === 'pro' || subscriptionPlan === 'premium') && !paddleSubscriptionId && (
                  <p style={{ color: 'var(--text-light)', fontSize: '0.9em', margin: 0 }}>
                    Billing is still syncing, or this account was not billed through Paddle. If you need to cancel or
                    change plans, contact support.
                  </p>
                )}
                {(subscriptionPlan === 'pro' || subscriptionPlan === 'premium') && paddleSubscriptionId && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                      {subscriptionPlan === 'pro' && (
                        <Button
                          type="button"
                          disabled={billingBusy}
                          onClick={() => handleChangePaddlePlan('premium')}
                        >
                          {billingBusy ? 'Working…' : 'Upgrade to Premium'}
                        </Button>
                      )}
                      {subscriptionPlan === 'premium' && (
                        <SecondaryButton
                          type="button"
                          disabled={billingBusy}
                          onClick={() => handleChangePaddlePlan('pro')}
                        >
                          {billingBusy ? 'Working…' : 'Downgrade to Pro'}
                        </SecondaryButton>
                      )}
                    </div>
                    <div style={{ padding: '14px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg-light)' }}>
                      <p style={{ margin: '0 0 10px', fontSize: '0.9em', fontWeight: 600 }}>Cancel subscription</p>
                      <p style={{ margin: '0 0 10px', fontSize: '0.85em', color: 'var(--text-light)' }}>
                        Stops renewal with Paddle. You can cancel at the end of the current period or immediately.
                      </p>
                      <select
                        value={cancelEffectiveFrom}
                        onChange={(e) => setCancelEffectiveFrom(e.target.value)}
                        disabled={billingBusy}
                        style={{
                          marginBottom: '12px',
                          padding: '8px 12px',
                          borderRadius: '6px',
                          border: '1px solid var(--border)',
                          background: 'var(--bg-white)',
                          color: 'var(--text)',
                        }}
                      >
                        <option value="next_billing_period">End of current billing period</option>
                        <option value="immediately">Immediately</option>
                      </select>
                      <div>
                        <Button
                          type="button"
                          variant="danger"
                          disabled={billingBusy}
                          onClick={handleCancelPaddleSubscription}
                        >
                          {billingBusy ? 'Submitting…' : 'Cancel subscription'}
                        </Button>
                      </div>
                    </div>
                  </div>
                )}
              </FormGroup>
            )}
          </>
        )

      case 'appearance':
        return (
          <>
            <SectionTitle>Appearance Settings</SectionTitle>
            
            <FormGroup>
              <Label>Theme</Label>
              <InfoText>Choose between light and dark theme for the application</InfoText>
              
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '20px', 
                marginTop: '20px',
                padding: '20px',
                background: 'var(--bg-light)',
                borderRadius: '12px',
                border: '1px solid var(--border)'
              }}>
                <div style={{ flex: 1 }}>
                  <div style={{ 
                    fontSize: '1.1em', 
                    fontWeight: 500, 
                    color: 'var(--text)',
                    marginBottom: '8px'
                  }}>
                    {theme === 'light' ? 'Light Mode' : 'Dark Mode'}
                  </div>
                  <div style={{ 
                    fontSize: '0.9em', 
                    color: 'var(--text-light)'
                  }}>
                    {theme === 'light' 
                      ? 'Bright theme with light backgrounds' 
                      : 'Dark theme with dark backgrounds'}
                  </div>
                </div>
                
                <ToggleSwitch>
                  <input
                    type="checkbox"
                    checked={theme === 'dark'}
                    onChange={toggleTheme}
                  />
                  <span className="slider"></span>
                </ToggleSwitch>
              </div>
              
              <div style={{ 
                marginTop: '15px', 
                padding: '12px', 
                background: theme === 'dark' 
                  ? 'rgba(21, 133, 161, 0.1)' 
                  : 'rgba(21, 133, 161, 0.05)', 
                borderRadius: '8px',
                border: `1px solid ${theme === 'dark' ? 'var(--primary)' : 'var(--border)'}`,
                color: 'var(--text-light)',
                fontSize: '0.85em'
              }}>
                <strong>Current theme:</strong> {theme === 'light' ? 'Light' : 'Dark'} mode
              </div>
            </FormGroup>
          </>
        )

      case 'privacy':
        return (
          <>
            <SectionTitle>Privacy Policy</SectionTitle>
            <LegalDocumentScroll className="settings-legal-embed">
              <LegalPrivacyBody />
            </LegalDocumentScroll>
          </>
        )

      case 'terms':
        return (
          <>
            <SectionTitle>Terms of Use</SectionTitle>
            <LegalDocumentScroll className="settings-legal-embed">
              <LegalTermsBody />
            </LegalDocumentScroll>
          </>
        )

      case 'contact':
        return (
          <>
            <SectionTitle>Contact Us</SectionTitle>
            <FormGroup>
              <div style={{ marginBottom: '24px', color: 'var(--text)', lineHeight: '1.6' }}>
                Have a question, feedback, or need help with your account? We'd love to hear from you.
                Our team typically responds within a few business days.
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {/* Email Support — opens Gmail compose */}
                <div style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '14px',
                  padding: '18px 20px',
                  background: theme === 'dark' ? 'rgba(21, 133, 161, 0.08)' : 'rgba(21, 133, 161, 0.05)',
                  border: `1px solid ${theme === 'dark' ? 'var(--primary)' : 'var(--border)'}`,
                  borderRadius: '10px',
                }}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2"
                    style={{ width: '22px', height: '22px', flexShrink: 0, marginTop: '2px' }}>
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                    <polyline points="22,6 12,13 2,6"></polyline>
                  </svg>
                  <div>
                    <div style={{ fontWeight: '600', color: 'var(--text)', marginBottom: '4px' }}>
                      Email Support
                    </div>
                    <div style={{ color: 'var(--text-light)', fontSize: '0.875em', marginBottom: '10px' }}>
                      For account issues, billing questions, and general inquiries.
                    </div>
                    <a
                      href={`https://mail.google.com/mail/?view=cm&fs=1&to=${encodeURIComponent(ZEDREQ_EMAIL)}&su=${encodeURIComponent('Support Request')}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: 'var(--primary)', fontWeight: '500', textDecoration: 'none', fontSize: '0.95em' }}
                    >
                      {ZEDREQ_EMAIL}
                    </a>
                  </div>
                </div>

                {/* Help Center — opens submission modal */}
                <div style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '14px',
                  padding: '18px 20px',
                  background: theme === 'dark' ? 'rgba(21, 133, 161, 0.08)' : 'rgba(21, 133, 161, 0.05)',
                  border: `1px solid ${theme === 'dark' ? 'var(--primary)' : 'var(--border)'}`,
                  borderRadius: '10px',
                }}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2"
                    style={{ width: '22px', height: '22px', flexShrink: 0, marginTop: '2px' }}>
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                  </svg>
                  <div>
                    <div style={{ fontWeight: '600', color: 'var(--text)', marginBottom: '4px' }}>
                      Help Center
                    </div>
                    <div style={{ color: 'var(--text-light)', fontSize: '0.875em', marginBottom: '10px' }}>
                      Submit a support ticket and our team will get back to you.
                    </div>
                    <button
                      onClick={() => setOpenModal('help')}
                      style={{
                        background: 'none',
                        border: 'none',
                        padding: 0,
                        cursor: 'pointer',
                        color: 'var(--primary)',
                        fontWeight: '500',
                        fontSize: '0.95em',
                      }}
                    >
                      Submit a request →
                    </button>
                  </div>
                </div>

                {/* Enterprise & Partnerships — opens submission modal */}
                <div style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '14px',
                  padding: '18px 20px',
                  background: theme === 'dark' ? 'rgba(21, 133, 161, 0.08)' : 'rgba(21, 133, 161, 0.05)',
                  border: `1px solid ${theme === 'dark' ? 'var(--primary)' : 'var(--border)'}`,
                  borderRadius: '10px',
                }}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2"
                    style={{ width: '22px', height: '22px', flexShrink: 0, marginTop: '2px' }}>
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                  </svg>
                  <div>
                    <div style={{ fontWeight: '600', color: 'var(--text)', marginBottom: '4px' }}>
                      Enterprise &amp; Partnerships
                    </div>
                    <div style={{ color: 'var(--text-light)', fontSize: '0.875em', marginBottom: '10px' }}>
                      Interested in a custom plan or partnership opportunity?
                    </div>
                    <button
                      onClick={() => setOpenModal('enterprise')}
                      style={{
                        background: 'none',
                        border: 'none',
                        padding: 0,
                        cursor: 'pointer',
                        color: 'var(--primary)',
                        fontWeight: '500',
                        fontSize: '0.95em',
                      }}
                    >
                      Get in touch →
                    </button>
                  </div>
                </div>
              </div>
            </FormGroup>
          </>
        )

      default:
        return null
    }
  }

  return (
    <Container>
      <Navbar />
      <SettingsContainer>
        <SidePanel>
          <SidePanelSection 
            className={activeSection === 'profile' ? 'active' : ''}
            onClick={() => setActiveSection('profile')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            Profile
          </SidePanelSection>

          <SidePanelSection 
            className={activeSection === 'account' ? 'active' : ''}
            onClick={() => setActiveSection('account')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="8.5" cy="7" r="4"></circle>
              <line x1="20" y1="8" x2="20" y2="14"></line>
            </svg>
            Account
          </SidePanelSection>

          <SidePanelSection 
            className={activeSection === 'security' ? 'active' : ''}
            onClick={() => setActiveSection('security')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            Security
          </SidePanelSection>

          <SidePanelSection 
            className={activeSection === 'subscription' ? 'active' : ''}
            onClick={() => setActiveSection('subscription')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <path d="M16 10a4 4 0 0 1-8 0"></path>
            </svg>
            Subscription
          </SidePanelSection>

          <SidePanelSection 
            className={activeSection === 'appearance' ? 'active' : ''}
            onClick={() => setActiveSection('appearance')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="5"></circle>
              <line x1="12" y1="1" x2="12" y2="3"></line>
              <line x1="12" y1="21" x2="12" y2="23"></line>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
              <line x1="1" y1="12" x2="3" y2="12"></line>
              <line x1="21" y1="12" x2="23" y2="12"></line>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg>
            Appearance
          </SidePanelSection>

          <SidePanelSection 
            className={activeSection === 'privacy' ? 'active' : ''}
            onClick={() => setActiveSection('privacy')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
            Privacy Policy
          </SidePanelSection>

          <SidePanelSection 
            className={activeSection === 'terms' ? 'active' : ''}
            onClick={() => setActiveSection('terms')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
            </svg>
            Terms of Use
          </SidePanelSection>

          <SidePanelSection
            className={activeSection === 'contact' ? 'active' : ''}
            onClick={() => setActiveSection('contact')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
              <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
            Contact Us
          </SidePanelSection>
        </SidePanel>

        <MainContent>
          {error && <ErrorMessage>{error}</ErrorMessage>}
          {success && <SuccessMessage>{success}</SuccessMessage>}
          {renderContent()}
        </MainContent>
      </SettingsContainer>

      {/* Help Center Modal */}
      {openModal === 'help' && (
        <ModalOverlay onClick={(e) => { if (e.target === e.currentTarget) closeModal() }}>
          <ModalBox>
            <ModalTitle>Submit a Support Request</ModalTitle>
            <ModalSubtitle>Describe your issue and we'll get back to you within a few business days.</ModalSubtitle>

            {modalSuccess ? (
              <ModalSuccessBox>
                <svg viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2"
                  style={{ width: '48px', height: '48px', margin: '0 auto 12px', display: 'block' }}>
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <div style={{ fontWeight: '600', color: 'var(--text)', fontSize: '1.05rem', marginBottom: '6px' }}>
                  Request submitted!
                </div>
                <div style={{ color: 'var(--text-light)', fontSize: '0.875rem', marginBottom: '20px' }}>
                  We've received your message and will respond shortly.
                </div>
                <Button type="button" onClick={closeModal}>Close</Button>
              </ModalSuccessBox>
            ) : (
              <form onSubmit={async (e) => {
                e.preventDefault()
                await submitContactForm('help', helpSubject, helpMessage, { category: helpCategory })
              }}>
                <ModalFieldGroup>
                  <ModalLabel>Category</ModalLabel>
                  <ModalSelect value={helpCategory} onChange={(e) => setHelpCategory(e.target.value)}>
                    <option>Technical Issue</option>
                    <option>Account &amp; Billing</option>
                    <option>Feature Request</option>
                    <option>Other</option>
                  </ModalSelect>
                </ModalFieldGroup>

                <ModalFieldGroup>
                  <ModalLabel>Subject</ModalLabel>
                  <ModalInput
                    type="text"
                    placeholder="Brief summary of your issue"
                    value={helpSubject}
                    onChange={(e) => setHelpSubject(e.target.value)}
                    required
                    maxLength={200}
                  />
                </ModalFieldGroup>

                <ModalFieldGroup>
                  <ModalLabel>Message</ModalLabel>
                  <ModalTextarea
                    placeholder="Describe your issue in detail…"
                    value={helpMessage}
                    onChange={(e) => setHelpMessage(e.target.value)}
                    required
                    maxLength={5000}
                  />
                </ModalFieldGroup>

                {modalError && (
                  <ErrorMessage style={{ marginBottom: '12px' }}>{modalError}</ErrorMessage>
                )}

                <ModalActions>
                  <SecondaryButton type="button" onClick={closeModal} disabled={modalLoading}>
                    Cancel
                  </SecondaryButton>
                  <Button type="submit" disabled={modalLoading}>
                    {modalLoading ? 'Sending…' : 'Send Request'}
                  </Button>
                </ModalActions>
              </form>
            )}
          </ModalBox>
        </ModalOverlay>
      )}

      {/* Enterprise & Partnerships Modal */}
      {openModal === 'enterprise' && (
        <ModalOverlay onClick={(e) => { if (e.target === e.currentTarget) closeModal() }}>
          <ModalBox>
            <ModalTitle>Enterprise &amp; Partnerships</ModalTitle>
            <ModalSubtitle>Tell us about your organisation and we'll reach out to discuss the right solution.</ModalSubtitle>

            {modalSuccess ? (
              <ModalSuccessBox>
                <svg viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2"
                  style={{ width: '48px', height: '48px', margin: '0 auto 12px', display: 'block' }}>
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <div style={{ fontWeight: '600', color: 'var(--text)', fontSize: '1.05rem', marginBottom: '6px' }}>
                  Message sent!
                </div>
                <div style={{ color: 'var(--text-light)', fontSize: '0.875rem', marginBottom: '20px' }}>
                  Our team will be in touch with you soon.
                </div>
                <Button type="button" onClick={closeModal}>Close</Button>
              </ModalSuccessBox>
            ) : (
              <form onSubmit={async (e) => {
                e.preventDefault()
                await submitContactForm(
                  'enterprise',
                  entSubject,
                  entMessage,
                  { company: entCompany, role: entRole }
                )
              }}>
                <ModalFieldGroup>
                  <ModalLabel>Company Name</ModalLabel>
                  <ModalInput
                    type="text"
                    placeholder="Your company or organisation"
                    value={entCompany}
                    onChange={(e) => setEntCompany(e.target.value)}
                    required
                    maxLength={200}
                  />
                </ModalFieldGroup>

                <ModalFieldGroup>
                  <ModalLabel>Your Role</ModalLabel>
                  <ModalInput
                    type="text"
                    placeholder="e.g. HR Manager, CTO, Founder"
                    value={entRole}
                    onChange={(e) => setEntRole(e.target.value)}
                    required
                    maxLength={100}
                  />
                </ModalFieldGroup>

                <ModalFieldGroup>
                  <ModalLabel>Subject</ModalLabel>
                  <ModalInput
                    type="text"
                    placeholder="What are you looking for?"
                    value={entSubject}
                    onChange={(e) => setEntSubject(e.target.value)}
                    required
                    maxLength={200}
                  />
                </ModalFieldGroup>

                <ModalFieldGroup>
                  <ModalLabel>Message</ModalLabel>
                  <ModalTextarea
                    placeholder="Tell us more about your needs and goals…"
                    value={entMessage}
                    onChange={(e) => setEntMessage(e.target.value)}
                    required
                    maxLength={5000}
                  />
                </ModalFieldGroup>

                {modalError && (
                  <ErrorMessage style={{ marginBottom: '12px' }}>{modalError}</ErrorMessage>
                )}

                <ModalActions>
                  <SecondaryButton type="button" onClick={closeModal} disabled={modalLoading}>
                    Cancel
                  </SecondaryButton>
                  <Button type="submit" disabled={modalLoading}>
                    {modalLoading ? 'Sending…' : 'Send Message'}
                  </Button>
                </ModalActions>
              </form>
            )}
          </ModalBox>
        </ModalOverlay>
      )}
    </Container>
  )
}

export default Settings
