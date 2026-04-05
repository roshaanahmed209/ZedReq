import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import styled, { keyframes } from 'styled-components'
import { useAuth } from '../contexts/AuthContext'
import { signInWithPopup, signOut } from 'firebase/auth'
import { auth, googleProvider } from '../config/firebase'
import api, { tokenService } from '../services/api'
import { extractApiErrorMessage } from '../utils/apiError'
import { markPrelaunchNoticePending } from '../utils/prelaunchNotice'

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`

const slideIn = keyframes`
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
`

const Container = styled.div`
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  min-height: 100vh;
  width: 100%;
  animation: ${fadeIn} 0.6s ease-in;
  
  @media (max-width: 968px) {
    grid-template-columns: 1fr;
  }
`

const LeftPanel = styled.div`
  background: #1a1a1a;
  color: var(--text);
  padding: 60px 50px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-right: 1px solid var(--border);
  position: relative;
  
  @media (max-width: 968px) {
    padding: 40px 30px;
    min-height: 100vh;
  }
`

const BackArrow = styled(Link)`
  position: absolute;
  top: 30px;
  left: 30px;
  color: #999;
  text-decoration: none;
  font-size: 2em;
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  
  &:hover {
    color: var(--primary);
    transform: translateX(-3px);
  }
`

const Logo = styled.h1`
  font-size: 3em;
  font-weight: 300;
  color: var(--primary);
  margin-bottom: 40px;
`

const PageTitle = styled.h2`
  font-size: 2em;
  font-weight: 400;
  margin-bottom: 40px;
`

const AuthContainer = styled.div`
  width: 100%;
  max-width: 420px;
  padding: 28px 28px 32px;
  border-radius: 16px;
  border: 1px solid color-mix(in srgb, var(--primary) 48%, var(--border));
  background: color-mix(in srgb, var(--bg-white) 94%, transparent);
  box-shadow:
    0 0 0 1px color-mix(in srgb, var(--primary) 14%, transparent),
    0 8px 32px color-mix(in srgb, var(--primary) 16%, transparent),
    var(--shadow-lg);
`

const Tabs = styled.div`
  display: flex;
  gap: 4px;
  padding: 4px;
  margin-bottom: 26px;
  border-radius: 12px;
  background: var(--hover-bg);
  border: 1px solid color-mix(in srgb, var(--border) 70%, transparent);
`

const TabButton = styled.button`
  flex: 1;
  padding: 11px 16px;
  background: transparent;
  border: none;
  border-radius: 10px;
  color: var(--text-light);
  font-size: 0.9375rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  cursor: pointer;
  transition: color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
  
  &.active {
    color: var(--primary);
    background: var(--bg-white);
    box-shadow: var(--shadow);
  }
  
  &:hover:not(.active) {
    color: var(--text);
  }
`

const TabContent = styled.div`
  display: ${props => props.$active ? 'block' : 'none'};
  animation: ${props => props.$active ? slideIn : 'none'} 0.3s ease-out;
`

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 18px;
`

const InputWrapper = styled.div`
  display: flex;
  flex-direction: column;
  gap: 6px;
`

const Label = styled.label`
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-light);
`

const Input = styled.input`
  width: 100%;
  min-height: 48px;
  padding: 13px 16px;
  border: 1px solid ${props => props.$hasError ? '#dc3545' : 'var(--border)'};
  border-radius: 10px;
  background: var(--hover-bg);
  color: var(--text);
  font-size: 0.9375rem;
  line-height: 1.4;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  
  &:hover:not(:focus) {
    border-color: color-mix(in srgb, var(--border) 65%, var(--text-light));
  }
  
  &:focus {
    outline: none;
    border-color: ${props => props.$hasError ? '#dc3545' : 'var(--primary)'};
    background: var(--bg-white);
    box-shadow: 0 0 0 3px
      ${props =>
        props.$hasError
          ? 'color-mix(in srgb, #dc3545 22%, transparent)'
          : 'color-mix(in srgb, var(--primary) 28%, transparent)'};
  }
  
  &::placeholder {
    color: var(--text-lighter);
  }
`

const Button = styled.button`
  min-height: 48px;
  padding: 14px 24px;
  margin-top: 2px;
  background: var(--primary);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 0.9375rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 2px 12px color-mix(in srgb, var(--primary) 38%, transparent);
  
  &:hover:not(:disabled) {
    background: var(--primary-dark);
    transform: translateY(-1px);
    box-shadow: 0 4px 16px color-mix(in srgb, var(--primary) 45%, transparent);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.55;
    cursor: not-allowed;
    box-shadow: none;
  }
`

const SecondaryButton = styled(Button)`
  flex: 1;
  margin-top: 0;
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
  box-shadow: none;
  
  &:hover:not(:disabled) {
    background: var(--hover-bg);
    border-color: color-mix(in srgb, var(--border) 40%, var(--text-light));
    box-shadow: none;
    transform: none;
  }
`

const FormActionsRow = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 4px;
  align-self: stretch;

  & > button {
    margin-top: 0;
  }

  & > button:first-of-type {
    flex: 1.35;
  }

  & > button:last-of-type {
    flex: 1;
  }
`

const LoadingSpinner = styled.span`
  display: inline-block;
  animation: ${pulse} 1s infinite;
`

const Message = styled.div`
  padding: 14px 16px;
  border-radius: 10px;
  margin-top: 22px;
  text-align: center;
  font-size: 0.875rem;
  line-height: 1.45;
  opacity: 0;
  transform: translateY(-6px);
  transition: opacity 0.25s ease, transform 0.25s ease;

  &.show {
    opacity: 1;
    transform: translateY(0);
  }

  &.success {
    background: color-mix(in srgb, #22c55e 12%, transparent);
    color: #86efac;
    border: 1px solid color-mix(in srgb, #22c55e 35%, transparent);
  }

  &.error {
    background: color-mix(in srgb, #dc3545 12%, transparent);
    color: #fca5a5;
    border: 1px solid color-mix(in srgb, #dc3545 35%, transparent);
  }

  [data-theme='light'] & {
    &.success {
      color: #166534;
    }
    &.error {
      color: #991b1b;
    }
  }
`

const ErrorList = styled.ul`
  margin-top: 10px;
  padding-left: 20px;
  text-align: left;
  font-size: 0.9em;
`

const RightPanel = styled.div`
  background: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  position: relative;
  overflow: hidden;
  
  @media (max-width: 968px) {
    display: none;
  }
`

const VideoBackground = styled.video`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
  opacity: 0.4;
  filter: brightness(0.6);
`

const VideoOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(13, 13, 13, 0.75) 0%, rgba(0, 180, 216, 0.15) 100%);
  z-index: 1;
  pointer-events: none;
`

const RightContent = styled.div`
  text-align: center;
  max-width: 500px;
  position: relative;
  z-index: 2;
`

const WelcomeTitle = styled.h2`
  font-size: 2.5em;
  font-weight: 300;
  margin-bottom: 20px;
  color: var(--text);
`

const WelcomeMessage = styled.p`
  font-size: 1.2em;
  color: var(--text-light);
  line-height: 1.6;
`

const PasswordHint = styled.p`
  font-size: 0.8125rem;
  color: var(--text-lighter);
  margin-top: 2px;
  line-height: 1.4;
`

const Divider = styled.div`
  display: flex;
  align-items: center;
  margin: 6px 0 2px;
  width: 100%;
`

const DividerLine = styled.div`
  flex: 1;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    color-mix(in srgb, var(--border) 90%, var(--text-light)) 20%,
    color-mix(in srgb, var(--border) 90%, var(--text-light)) 80%,
    transparent
  );
`

const DividerText = styled.span`
  padding: 0 14px;
  color: var(--text-lighter);
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
`

const GoogleButton = styled.button`
  width: 100%;
  min-height: 48px;
  padding: 12px 20px;
  background: var(--bg-white);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 10px;
  font-size: 0.9375rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
  margin-top: 4px;

  &:hover:not(:disabled) {
    background: var(--hover-bg);
    border-color: color-mix(in srgb, var(--border) 50%, var(--primary));
    box-shadow: var(--shadow);
  }

  &:active:not(:disabled) {
    transform: scale(0.99);
  }

  &:disabled {
    opacity: 0.55;
    cursor: not-allowed;
  }
`

const GoogleIcon = styled.span`
  display: flex;
  align-items: center;
  justify-content: center;
`

const AgreementNote = styled.p`
  font-size: 0.8125rem;
  color: var(--text-light);
  line-height: 1.55;
  margin: -4px 0 2px;

  a {
    color: var(--primary);
    text-decoration: none;
    font-weight: 500;
  }
  a:hover {
    text-decoration: underline;
  }
`

const TwoFactorIntro = styled.div`
  text-align: center;
  margin-bottom: 8px;
`

const TwoFactorTitle = styled.h3`
  margin: 0 0 8px;
  font-size: 1.125rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--text);
`

const TwoFactorSubtitle = styled.p`
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-light);
  line-height: 1.5;
`

const OTPInput = styled(Input)`
  font-family: ui-monospace, 'Cascadia Code', 'Segoe UI Mono', monospace;
  font-size: 1.375rem;
  font-weight: 600;
  letter-spacing: 0.45em;
  text-align: center;
  padding-left: calc(16px + 0.2em);
`

const Landing = () => {
  const [activeTab, setActiveTab] = useState('login')
  const [message, setMessage] = useState('')
  const [errors, setErrors] = useState([])
  const [isError, setIsError] = useState(false)
  const [loading, setLoading] = useState(false)
  const [requires2FA, setRequires2FA] = useState(false)
  const [tempToken, setTempToken] = useState(null)
  const [twoFactorCode, setTwoFactorCode] = useState('')
  const { login, verify2FA, register, updateUser, checkAuthStatus, refreshSessionFeedStats } = useAuth()
  const navigate = useNavigate()

  const showMessage = (text, error = false, errorList = []) => {
    setMessage('')
    setErrors([])
    setIsError(false)

    setTimeout(() => {
      setMessage(text)
      setIsError(error)
      setErrors(errorList)
    }, 100)
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')
    setErrors([])
    
    const formData = new FormData(e.target)
    const username = formData.get('username')?.trim()
    const password = formData.get('password')
    
    if (!username || !password) {
      showMessage('Please enter both username/email and password', true)
      setLoading(false)
      return
    }
    
    const result = await login(username, password)
    
    if (result.requires2FA) {
      setRequires2FA(true)
      setTempToken(result.tempToken)
      showMessage(result.message || 'Please enter your 2FA code')
      setLoading(false)
      return
    }
    
    if (result.success) {
      markPrelaunchNoticePending()
      navigate('/feed')
    } else {
      showMessage(result.message || 'Login failed', true)
    }
    
    setLoading(false)
  }

  const handle2FAVerification = async (e) => {
    e.preventDefault()
    if (!twoFactorCode || twoFactorCode.length !== 6) {
      showMessage('Please enter a 6-digit code', true)
      return
    }

    setLoading(true)
    setMessage('')
    
    const result = await verify2FA(tempToken, twoFactorCode)
    
    if (result.success) {
      setRequires2FA(false)
      setTempToken(null)
      setTwoFactorCode('')
      markPrelaunchNoticePending()
      navigate('/feed')
    } else {
      showMessage(result.message || 'Invalid 2FA code', true)
      setTwoFactorCode('')
    }
    
    setLoading(false)
  }

  const runGoogleAuth = async (intent) => {
    setLoading(true)
    setMessage('')
    setErrors([])

    try {
      const result = await signInWithPopup(auth, googleProvider)
      const firebaseUser = result.user
      const idToken = await firebaseUser.getIdToken()

      const response = await api.post('/api/auth/google', {
        id_token: idToken,
        intent,
      })

      if (response.data && response.data.access_token) {
        const { access_token, refresh_token, user: userData } = response.data
        tokenService.setTokens(access_token, refresh_token)

        if (userData) {
          updateUser(userData)
          refreshSessionFeedStats(userData.id ?? userData.uid)
        } else {
          await checkAuthStatus()
        }

        markPrelaunchNoticePending()
        navigate('/feed')
      } else {
        showMessage(
          extractApiErrorMessage(response.data) || 'Google sign-in failed',
          true
        )
        if (intent === 'login') {
          await signOut(auth)
        }
      }
    } catch (error) {
      console.error('Google auth error:', error)
      if (error.code === 'auth/popup-closed-by-user') {
        showMessage('Sign-in cancelled', true)
      } else if (error.response) {
        const apiMsg = extractApiErrorMessage(error.response.data)
        const fallback =
          intent === 'login' && error.response.status === 404
            ? 'No ZedReq account is registered for this Google email. Please create an account first (use Sign up).'
            : 'Google sign-in failed'
        showMessage(apiMsg || fallback, true)
        if (intent === 'login') {
          await signOut(auth)
        }
      } else {
        showMessage(error.message || 'Google sign-in failed', true)
        if (intent === 'login') {
          await signOut(auth)
        }
      }
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSignIn = () => runGoogleAuth('login')

  const handleGoogleSignUp = () => runGoogleAuth('signup')

  const handleRegister = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')
    setErrors([])
    
    const formData = new FormData(e.target)
    const userData = {
      full_name: formData.get('full_name')?.trim(),
      username: formData.get('username')?.trim(),
      email: formData.get('email')?.trim(),
      password: formData.get('password')
    }
    
    // Basic client-side validation
    if (!userData.full_name || !userData.username || !userData.email || !userData.password) {
      showMessage('Please fill in all fields', true)
      setLoading(false)
      return
    }
    
    // Password requirements (must match backend)
    if (userData.password.length < 8) {
      showMessage('Password must be at least 8 characters long', true)
      setLoading(false)
      return
    }
    
    if (userData.password.length > 25) {
      showMessage('Password must not exceed 25 characters', true)
      setLoading(false)
      return
    }
    
    if (!/[A-Z]/.test(userData.password)) {
      showMessage('Password must contain at least one uppercase letter', true)
      setLoading(false)
      return
    }
    
    const result = await register(userData)
    
    if (result.success) {
      markPrelaunchNoticePending()
      navigate('/feed')
    } else {
      showMessage(result.message || 'Registration failed', true, result.errors || [])
    }
    
    setLoading(false)
  }

  return (
    <Container>
      <LeftPanel>
        <BackArrow to="/">←</BackArrow>
        <Logo>ZedReq</Logo>
        <PageTitle>{activeTab === 'login' ? 'Welcome Back' : 'Join Us'}</PageTitle>
        
        <AuthContainer>
          <Tabs>
            <TabButton 
              className={activeTab === 'login' ? 'active' : ''}
              onClick={() => {
                setActiveTab('login')
                setMessage('')
                setErrors([])
              }}
            >
              Sign In
            </TabButton>
            <TabButton 
              className={activeTab === 'register' ? 'active' : ''}
              onClick={() => {
                setActiveTab('register')
                setMessage('')
                setErrors([])
              }}
            >
              Sign Up
            </TabButton>
          </Tabs>
          
          <TabContent $active={activeTab === 'login'}>
            {!requires2FA ? (
              <Form onSubmit={handleLogin}>
                <InputWrapper>
                  <Label htmlFor="login-username">Username or Email</Label>
                  <Input 
                    id="login-username"
                    type="text" 
                    name="username" 
                    placeholder="Enter your username or email" 
                    autoComplete="username"
                    required 
                  />
                </InputWrapper>
                <InputWrapper>
                  <Label htmlFor="login-password">Password</Label>
                  <Input 
                    id="login-password"
                    type="password" 
                    name="password" 
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    required 
                  />
                </InputWrapper>
                <Button type="submit" disabled={loading}>
                  {loading ? <LoadingSpinner>Signing In...</LoadingSpinner> : 'Sign In →'}
                </Button>
                
                <Divider>
                  <DividerLine />
                  <DividerText>OR</DividerText>
                  <DividerLine />
                </Divider>
                
                <GoogleButton 
                  type="button" 
                  onClick={handleGoogleSignIn} 
                  disabled={loading}
                >
                  <GoogleIcon>
                    <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                      <path d="M17.64 9.20454C17.64 8.56636 17.5827 7.95272 17.4764 7.36363H9V10.845H13.8436C13.635 11.97 13.0009 12.9232 12.0477 13.5614V15.8195H15.9564C17.1582 14.7227 17.64 12.9455 17.64 9.20454Z" fill="#4285F4"/>
                      <path d="M9 18C11.43 18 13.467 17.1941 14.9564 15.8195L12.0477 13.5614C11.2418 14.1014 10.2109 14.4204 9 14.4204C6.65455 14.4204 4.67182 12.8373 3.96409 10.71H0.957275V13.0418C2.43818 15.9832 5.48182 18 9 18Z" fill="#34A853"/>
                      <path d="M3.96409 10.71C3.78409 10.17 3.68182 9.59318 3.68182 9C3.68182 8.40682 3.78409 7.83 3.96409 7.29V4.95818H0.957273C0.347727 6.17318 0 7.54773 0 9C0 10.4523 0.347727 11.8268 0.957273 13.0418L3.96409 10.71Z" fill="#FBBC05"/>
                      <path d="M9 3.57955C10.3214 3.57955 11.5077 4.03364 12.4405 4.92545L15.0218 2.34409C13.4632 0.891818 11.4259 0 9 0C5.48182 0 2.43818 2.01682 0.957275 4.95818L3.96409 7.29C4.67182 5.16273 6.65455 3.57955 9 3.57955Z" fill="#EA4335"/>
                    </svg>
                  </GoogleIcon>
                  {loading ? 'Signing in...' : 'Continue with Google'}
                </GoogleButton>
              </Form>
            ) : (
              <Form onSubmit={handle2FAVerification}>
                <TwoFactorIntro>
                  <TwoFactorTitle>Two-Factor Authentication</TwoFactorTitle>
                  <TwoFactorSubtitle>
                    Enter the 6-digit code from your authenticator app
                  </TwoFactorSubtitle>
                </TwoFactorIntro>
                <InputWrapper>
                  <Label htmlFor="2fa-code">2FA Code</Label>
                  <OTPInput
                    id="2fa-code"
                    type="text"
                    value={twoFactorCode}
                    onChange={(e) => setTwoFactorCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    placeholder="000000"
                    maxLength={6}
                    autoComplete="one-time-code"
                    inputMode="numeric"
                    required
                  />
                  <PasswordHint>You can also use a backup code (8 characters)</PasswordHint>
                </InputWrapper>
                <FormActionsRow>
                  <Button type="submit" disabled={loading || twoFactorCode.length !== 6}>
                    {loading ? <LoadingSpinner>Verifying...</LoadingSpinner> : 'Verify →'}
                  </Button>
                  <SecondaryButton
                    type="button"
                    onClick={() => {
                      setRequires2FA(false)
                      setTempToken(null)
                      setTwoFactorCode('')
                      setMessage('')
                    }}
                  >
                    Back
                  </SecondaryButton>
                </FormActionsRow>
              </Form>
            )}
          </TabContent>
          
          <TabContent $active={activeTab === 'register'}>
            <Form onSubmit={handleRegister}>
              <InputWrapper>
                <Label htmlFor="register-fullname">Full Name</Label>
                <Input 
                  id="register-fullname"
                  type="text" 
                  name="full_name" 
                  placeholder="Enter your full name"
                  autoComplete="name"
                  required 
                />
              </InputWrapper>
              <InputWrapper>
                <Label htmlFor="register-username">Username</Label>
                <Input 
                  id="register-username"
                  type="text" 
                  name="username" 
                  placeholder="Choose a username"
                  autoComplete="username"
                  required 
                />
              </InputWrapper>
              <InputWrapper>
                <Label htmlFor="register-email">Email</Label>
                <Input 
                  id="register-email"
                  type="email" 
                  name="email" 
                  placeholder="Enter your email"
                  autoComplete="email"
                  required 
                />
              </InputWrapper>
              <InputWrapper>
                <Label htmlFor="register-password">Password</Label>
                <Input 
                  id="register-password"
                  type="password" 
                  name="password" 
                  placeholder="Create a password"
                  autoComplete="new-password"
                  required 
                />
                <PasswordHint>8-25 characters, at least one uppercase</PasswordHint>
              </InputWrapper>
              <AgreementNote>
                By creating an account, you agree to our{' '}
                <Link to="/terms">Terms of Service</Link>
                {' '}and{' '}
                <Link to="/privacy">Privacy Policy</Link>.
              </AgreementNote>
              <Button type="submit" disabled={loading}>
                {loading ? <LoadingSpinner>Creating Account...</LoadingSpinner> : 'Sign Up →'}
              </Button>
              <Divider>
                <DividerLine />
                <DividerText>OR</DividerText>
                <DividerLine />
              </Divider>
              <GoogleButton
                type="button"
                onClick={handleGoogleSignUp}
                disabled={loading}
              >
                <GoogleIcon>
                  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                    <path d="M17.64 9.20454C17.64 8.56636 17.5827 7.95272 17.4764 7.36363H9V10.845H13.8436C13.635 11.97 13.0009 12.9232 12.0477 13.5614V15.8195H15.9564C17.1582 14.7227 17.64 12.9455 17.64 9.20454Z" fill="#4285F4"/>
                    <path d="M9 18C11.43 18 13.467 17.1941 14.9564 15.8195L12.0477 13.5614C11.2418 14.1014 10.2109 14.4204 9 14.4204C6.65455 14.4204 4.67182 12.8373 3.96409 10.71H0.957275V13.0418C2.43818 15.9832 5.48182 18 9 18Z" fill="#34A853"/>
                    <path d="M3.96409 10.71C3.78409 10.17 3.68182 9.59318 3.68182 9C3.68182 8.40682 3.78409 7.83 3.96409 7.29V4.95818H0.957273C0.347727 6.17318 0 7.54773 0 9C0 10.4523 0.347727 11.8268 0.957273 13.0418L3.96409 10.71Z" fill="#FBBC05"/>
                    <path d="M9 3.57955C10.3214 3.57955 11.5077 4.03364 12.4405 4.92545L15.0218 2.34409C13.4632 0.891818 11.4259 0 9 0C5.48182 0 2.43818 2.01682 0.957275 4.95818L3.96409 7.29C4.67182 5.16273 6.65455 3.57955 9 3.57955Z" fill="#EA4335"/>
                  </svg>
                </GoogleIcon>
                {loading ? 'Please wait...' : 'Sign up with Google'}
              </GoogleButton>
            </Form>
          </TabContent>
          
          <Message className={`${message ? 'show' : ''} ${isError ? 'error' : 'success'}`}>
            {message}
            {errors.length > 0 && (
              <ErrorList>
                {errors.map((err, idx) => (
                  <li key={idx}>{err}</li>
                ))}
              </ErrorList>
            )}
          </Message>
        </AuthContainer>
      </LeftPanel>
      
      <RightPanel>
        <VideoBackground autoPlay loop muted playsInline>
          <source src="/static/66423-517408349.mp4" type="video/mp4" />
        </VideoBackground>
        <VideoOverlay />
        <RightContent>
          <WelcomeTitle>Welcome to ZedReq</WelcomeTitle>
          <WelcomeMessage>
            Build your professional network, share insights, and grow your career together.
          </WelcomeMessage>
        </RightContent>
      </RightPanel>
    </Container>
  )
}

export default Landing
