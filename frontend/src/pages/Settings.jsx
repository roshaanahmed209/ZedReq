import React, { useState, useEffect, useRef } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'
import api, { userAPI } from '../services/api'
import Navbar from '../components/Navbar'

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
    background: rgba(10, 102, 194, 0.1);
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
    background: rgba(10, 102, 194, 0.05);
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
    box-shadow: 0 4px 12px ${props => props.variant === 'danger' ? 'rgba(239, 68, 68, 0.4)' : 'rgba(10, 102, 194, 0.4)'};
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

const PrivacyPolicyContent = styled.div`
  max-height: 500px;
  overflow-y: auto;
  padding: 20px;
  background: var(--bg-light);
  border-radius: 8px;
  line-height: 1.6;
  color: var(--text);

  h3 {
    margin-top: 20px;
    margin-bottom: 10px;
    color: var(--primary);
  }

  p {
    margin-bottom: 10px;
  }
`

const Settings = () => {
  const navigate = useNavigate()
  const { user, updateUser } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const [activeSection, setActiveSection] = useState('profile')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Profile settings
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

  // Refs for timeout cleanup
  const timeoutRefs = useRef([])

  // Load user data on mount and when user changes
  useEffect(() => {
    if (user) {
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
        const response = await userAPI.getSubscriptionUsage()
        if (response.data) {
          const { plan, usage } = response.data
          setSubscriptionPlan(plan?.plan_name || 'free')
          setSubscriptionStatus(plan?.status || 'active')
          setQuotaUsage(usage)
        }
      } catch (err) {
        console.error('Failed to load subscription usage:', err)
        setSubscriptionPlan('free')
        setSubscriptionStatus('active')
      } finally {
        setSubscriptionLoading(false)
        setSubscriptionLoaded(true)
      }
    }
    loadSubscriptionUsage()
  }, [user])

  // Cleanup timeouts on unmount
  useEffect(() => {
    return () => {
      // Clear any pending timeouts when component unmounts
      timeoutRefs.current.forEach(timeoutId => clearTimeout(timeoutId))
      timeoutRefs.current = []
    }
  }, [])

  const uploadToCloudinary = async (file, type = 'image') => {
    const cloudName = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME
    const uploadPreset = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET

    if (!cloudName || !uploadPreset) {
      throw new Error('Cloudinary configuration missing')
    }

    const formData = new FormData()
    formData.append('file', file)
    formData.append('upload_preset', uploadPreset)

    const resourceType = type === 'pdf' ? 'raw' : 'image'

    try {
      const response = await fetch(
        `https://api.cloudinary.com/v1_1/${cloudName}/${resourceType}/upload`,
        { method: 'POST', body: formData }
      )
      const data = await response.json()
      if (data.error) throw new Error(data.error.message)
      return data.secure_url
    } catch (error) {
      console.error('Cloudinary upload error:', error)
      throw error
    }
  }

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
      const updateData = {}

      // Validate and upload profile picture
      if (profilePic) {
        try {
          const url = await uploadToCloudinary(profilePic, 'image')
          updateData.profile_pic = url
        } catch (uploadError) {
          setError('Failed to upload profile picture. Please try again.')
          setLoading(false)
          return
        }
      }

      // Validate and upload cover picture
      if (coverPic) {
        try {
          const url = await uploadToCloudinary(coverPic, 'image')
          updateData.cover_pic = url
        } catch (uploadError) {
          setError('Failed to upload cover picture. Please try again.')
          setLoading(false)
          return
        }
      }

      // Handle resume upload - send file directly to backend
      if (resume) {
        setResumeFileName(resume.name) // Store file name for display
        // Resume will be sent as multipart/form-data
      }

      // Validate and sanitize interests (client-side validation)
      if (interests && interests.trim()) {
        const trimmedInterests = interests.trim()
        if (trimmedInterests.length > 1000) {
          setError('Interests must be less than 1000 characters')
          setLoading(false)
          return
        }
        updateData.interests = trimmedInterests
      }

      // Validate and sanitize location (client-side validation)
      if (location && location.trim()) {
        const trimmedLocation = location.trim()
        if (trimmedLocation.length > 150) {
          setError('Location must be less than 150 characters')
          setLoading(false)
          return
        }
        updateData.location = trimmedLocation
      }

      // Check if we have resume file to upload (multipart/form-data) or just data (JSON)
      // Note: profile_pic and cover_pic still use frontend Cloudinary upload for now
      const hasResumeFile = resume
      
      if (hasResumeFile || Object.keys(updateData).length > 0) {
        let response
        
        if (hasResumeFile) {
          // Use multipart/form-data for resume file upload
          const formData = new FormData()
          
          // Send resume file directly to backend
          formData.append('resume', resume)
          
          // Include other fields
          if (interests && interests.trim()) {
            formData.append('interests', interests.trim())
          }
          if (location && location.trim()) {
            formData.append('location', location.trim())
          }
          
          // Also include profile_pic and cover_pic URLs if they were uploaded to Cloudinary
          if (updateData.profile_pic) {
            formData.append('profile_pic', updateData.profile_pic)
          }
          if (updateData.cover_pic) {
            formData.append('cover_pic', updateData.cover_pic)
          }
          
          response = await api.put('/api/user/profile', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          })
        } else {
          // Use JSON for non-file updates
          response = await api.put('/api/user/profile', updateData)
        }
        
        if (updateUser && response.data) {
          updateUser({ ...user, ...response.data })
        }
        
        // Show specific success message if resume was uploaded
        if (resume) {
          setSuccess(`Resume "${resumeFileName}" uploaded and processed successfully! Your profile has been updated.`)
          setResumeUploaded(true)
        } else {
          setSuccess('Profile updated successfully!')
        }
        
        setProfilePic(null)
        setCoverPic(null)
        setResume(null) // Clear file input
        
        // Clear success message after 5 seconds
        const timeoutId = setTimeout(() => {
          setSuccess('')
          setResumeUploaded(false)
        }, 5000)
        timeoutRefs.current.push(timeoutId)
      } else {
        setError('No changes to save')
      }
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
      let hasChanges = false

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
          setSuccess('Password changed successfully!')
          setCurrentPassword('')
          setNewPassword('')
          setConfirmPassword('')
          hasChanges = true
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
          setSuccess(hasChanges ? 'Password and email updated successfully!' : 'Email updated successfully!')
          if (updateUser) {
            updateUser({ ...user, email: newEmail })
          }
          hasChanges = true
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

      if (!hasChanges && !newPassword && (!newEmail || newEmail === user?.email)) {
        setError('No changes to save')
      }

      // Clear success message after 5 seconds
      if (hasChanges) {
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
    if (!window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return
    }

    if (!window.confirm('This will permanently delete all your data. Type DELETE to confirm.')) {
      return
    }

    setLoading(true)
    setError('')
    try {
      await api.delete('/api/user/account')
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
                  <strong>Note:</strong> Plan upgrades will be available in the future. 
                  Enterprise plans are assigned by administrators.
                </p>
              </div>
              <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', marginTop: '15px' }}>
                <SecondaryButton 
                  disabled={true}
                  style={{ 
                    borderColor: subscriptionPlan === 'free' ? 'var(--primary)' : 'var(--border)',
                    background: subscriptionPlan === 'free' ? 'rgba(10, 102, 194, 0.1)' : 'transparent',
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
                    background: subscriptionPlan === 'pro' ? 'rgba(10, 102, 194, 0.1)' : 'transparent',
                    cursor: 'not-allowed',
                    opacity: subscriptionPlan === 'pro' ? 1 : 0.5
                  }}
                >
                  Pro Plan {subscriptionPlan === 'pro' ? '(Current)' : '- $9.99/month'}
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
                  ? 'rgba(10, 102, 194, 0.1)' 
                  : 'rgba(10, 102, 194, 0.05)', 
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
            <PrivacyPolicyContent>
              <h3>1. Information We Collect</h3>
              <p>
                ZedReq collects information that you provide directly to us, including your name, email address, 
                profile information, and any content you post on our platform.
              </p>

              <h3>2. How We Use Your Information</h3>
              <p>
                We use the information we collect to provide, maintain, and improve our services, process your 
                requests, send you communications, and personalize your experience.
              </p>

              <h3>3. Information Sharing</h3>
              <p>
                We do not sell, trade, or rent your personal information to third parties. We may share your 
                information only in specific circumstances, such as with your consent or to comply with legal obligations.
              </p>

              <h3>4. Data Security</h3>
              <p>
                We implement appropriate security measures to protect your personal information against unauthorized 
                access, alteration, disclosure, or destruction.
              </p>

              <h3>5. Your Rights</h3>
              <p>
                You have the right to access, update, or delete your personal information at any time through 
                your account settings.
              </p>

              <h3>6. Cookies</h3>
              <p>
                We use cookies and similar tracking technologies to track activity on our platform and hold 
                certain information to improve your experience.
              </p>

              <h3>7. Changes to This Policy</h3>
              <p>
                We may update this Privacy Policy from time to time. We will notify you of any changes by 
                posting the new Privacy Policy on this page.
              </p>

              <h3>8. Contact Us</h3>
              <p>
                If you have any questions about this Privacy Policy, please contact us at privacy@zedreq.com
              </p>

              <p style={{ marginTop: '20px', fontSize: '0.9em', color: 'var(--text-lighter)' }}>
                Last updated: {new Date().toLocaleDateString()}
              </p>
            </PrivacyPolicyContent>
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
        </SidePanel>

        <MainContent>
          {error && <ErrorMessage>{error}</ErrorMessage>}
          {success && <SuccessMessage>{success}</SuccessMessage>}
          {renderContent()}
        </MainContent>
      </SettingsContainer>
    </Container>
  )
}

export default Settings
