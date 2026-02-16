import React, { useState, useEffect } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
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

  @media (max-width: 1024px) {
    grid-template-columns: 240px 1fr;
    gap: 20px;
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 20px;
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
  }
`

const MainContent = styled.div`
  background: var(--bg-white);
  border-radius: 16px;
  border: 1px solid var(--border);
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  animation: ${slideIn} 0.4s ease-out;

  @media (max-width: 768px) {
    padding: 30px 20px;
  }
`

const SectionTitle = styled.h2`
  font-size: 1.8em;
  font-weight: 300;
  color: var(--text);
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid var(--border);
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

  &:focus {
    outline: none;
    border-color: var(--primary);
    background: var(--bg-white);
  }

  &::placeholder {
    color: var(--text-lighter);
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
  const [interests, setInterests] = useState(user?.interests || '')
  const [location, setLocation] = useState(user?.location || '')

  // Account settings
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [newEmail, setNewEmail] = useState(user?.email || '')

  // Security settings
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false)

  // Subscription
  const [subscriptionPlan, setSubscriptionPlan] = useState('free')

  useEffect(() => {
    if (user) {
      setProfilePicPreview(user.profile_pic || '')
      setCoverPicPreview(user.cover_pic || '')
      setInterests(user.interests || '')
      setLocation(user.location || '')
      setNewEmail(user.email || '')
    }
  }, [user])

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

    if (file.type !== 'application/pdf') {
      setError('Please select a PDF file')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('Resume size should be less than 10MB')
      return
    }

    setResume(file)
  }

  const saveProfileSettings = async () => {
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const updateData = {}

      if (profilePic) {
        const url = await uploadToCloudinary(profilePic, 'image')
        updateData.profile_pic = url
      }

      if (coverPic) {
        const url = await uploadToCloudinary(coverPic, 'image')
        updateData.cover_pic = url
      }

      if (resume) {
        const url = await uploadToCloudinary(resume, 'pdf')
        updateData.resume = url
      }

      if (interests) {
        updateData.interests = interests
      }

      if (location) {
        updateData.location = location
      }

      if (Object.keys(updateData).length > 0) {
        const response = await api.put('/api/user/profile', updateData)
        if (updateUser) {
          updateUser({ ...user, ...response.data })
        }
        setSuccess('Profile updated successfully!')
        setProfilePic(null)
        setCoverPic(null)
        setResume(null)
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to update profile')
    } finally {
      setLoading(false)
    }
  }

  const saveAccountSettings = async () => {
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      if (newPassword) {
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

        await api.put('/api/user/change-password', {
          current_password: currentPassword,
          new_password: newPassword
        })
        setSuccess('Password changed successfully!')
        setCurrentPassword('')
        setNewPassword('')
        setConfirmPassword('')
      }

      if (newEmail && newEmail !== user?.email) {
        await api.put('/api/user/email', { email: newEmail })
        setSuccess('Email updated successfully!')
        if (updateUser) {
          updateUser({ ...user, email: newEmail })
        }
      }
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to update account settings')
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

  const toggleTwoFactor = async () => {
    setLoading(true)
    setError('')
    try {
      await api.put('/api/user/2fa', { enabled: !twoFactorEnabled })
      setTwoFactorEnabled(!twoFactorEnabled)
      setSuccess('Two-factor authentication updated!')
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to update 2FA settings')
    } finally {
      setLoading(false)
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
              <Label>Resume (PDF)</Label>
              <FileUploadArea onClick={() => document.getElementById('resume').click()}>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ margin: '0 auto 10px', color: 'var(--text-light)' }}>
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
                <p>Click to upload resume</p>
                <InfoText>Max size: 10MB (PDF only)</InfoText>
                <input
                  id="resume"
                  type="file"
                  accept="application/pdf"
                  onChange={handleResumeChange}
                />
              </FileUploadArea>
              {resume && <InfoText>Selected: {resume.name}</InfoText>}
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
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <Label>Two-Factor Authentication (2FA)</Label>
                  <InfoText>Add an extra layer of security to your account</InfoText>
                </div>
                <ToggleSwitch>
                  <input
                    type="checkbox"
                    checked={twoFactorEnabled}
                    onChange={toggleTwoFactor}
                    disabled={loading}
                  />
                  <span className="slider"></span>
                </ToggleSwitch>
              </div>
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
            <SectionTitle>Subscription</SectionTitle>

            <FormGroup>
              <Label>Current Plan</Label>
              <div style={{ 
                padding: '20px', 
                background: 'var(--bg-light)', 
                borderRadius: '8px',
                border: '2px solid var(--border)'
              }}>
                <h3 style={{ margin: '0 0 10px 0', color: 'var(--primary)' }}>
                  {subscriptionPlan === 'free' ? 'Free Plan' : subscriptionPlan === 'pro' ? 'Pro Plan' : 'Premium Plan'}
                </h3>
                <p style={{ margin: 0, color: 'var(--text-light)' }}>
                  {subscriptionPlan === 'free' 
                    ? 'Basic features included'
                    : subscriptionPlan === 'pro'
                    ? 'Advanced features and priority support'
                    : 'All features and premium support'}
                </p>
              </div>
            </FormGroup>

            <FormGroup>
              <Label>Upgrade Plan</Label>
              <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
                <SecondaryButton 
                  onClick={() => setSubscriptionPlan('pro')}
                  style={subscriptionPlan === 'pro' ? { borderColor: 'var(--primary)', background: 'rgba(10, 102, 194, 0.1)' } : {}}
                >
                  Pro Plan - $9.99/month
                </SecondaryButton>
                <SecondaryButton 
                  onClick={() => setSubscriptionPlan('premium')}
                  style={subscriptionPlan === 'premium' ? { borderColor: 'var(--primary)', background: 'rgba(10, 102, 194, 0.1)' } : {}}
                >
                  Premium Plan - $19.99/month
                </SecondaryButton>
              </div>
            </FormGroup>

            <Button onClick={() => setSuccess('Subscription updated!')} disabled={loading}>
              {loading ? 'Processing...' : 'Update Subscription'}
            </Button>
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
