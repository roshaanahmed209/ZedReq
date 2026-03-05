import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import styled, { keyframes } from 'styled-components'
import { useAuth } from '../contexts/AuthContext'
import { signInWithPopup } from 'firebase/auth'
import { auth, googleProvider } from '../config/firebase'
import api, { tokenService } from '../services/api'

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
  max-width: 400px;
`

const Tabs = styled.div`
  display: flex;
  margin-bottom: 30px;
  border-bottom: 1px solid var(--border);
`

const TabButton = styled.button`
  flex: 1;
  padding: 15px 20px;
  background: none;
  border: none;
  color: var(--text-light);
  font-size: 1em;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 2px solid transparent;
  
  &.active {
    color: var(--primary);
    border-bottom-color: var(--primary);
  }
  
  &:hover {
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
  gap: 20px;
`

const InputWrapper = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`

const Label = styled.label`
  color: var(--text);
  font-weight: 500;
`

const Input = styled.input`
  padding: 15px;
  border: 1px solid ${props => props.$hasError ? '#dc3545' : 'var(--border)'};
  border-radius: 8px;
  background: var(--bg-light);
  color: var(--text);
  font-size: 1em;
  transition: border-color 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: ${props => props.$hasError ? '#dc3545' : 'var(--primary)'};
  }
  
  &::placeholder {
    color: var(--text-lighter);
  }
`

const Button = styled.button`
  padding: 15px 30px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  
  &:hover:not(:disabled) {
    background: var(--primary-dark);
    transform: translateY(-2px);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0) scale(0.98);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`

const LoadingSpinner = styled.span`
  display: inline-block;
  animation: ${pulse} 1s infinite;
`

const Message = styled.div`
  padding: 15px;
  border-radius: 8px;
  margin-top: 20px;
  text-align: center;
  opacity: 0;
  transform: translateY(-10px);
  transition: all 0.3s ease;
  
  &.show {
    opacity: 1;
    transform: translateY(0);
  }
  
  &.success {
    background: rgba(40, 167, 69, 0.1);
    color: #28a745;
    border: 1px solid rgba(40, 167, 69, 0.3);
  }
  
  &.error {
    background: rgba(220, 53, 69, 0.1);
    color: #dc3545;
    border: 1px solid rgba(220, 53, 69, 0.3);
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
  font-size: 0.85em;
  color: var(--text-lighter);
  margin-top: 4px;
`

const Divider = styled.div`
  display: flex;
  align-items: center;
  margin: 20px 0;
  width: 100%;
`

const DividerLine = styled.div`
  flex: 1;
  height: 1px;
  background: var(--border);
`

const DividerText = styled.span`
  padding: 0 15px;
  color: var(--text-light);
  font-size: 0.9em;
`

const GoogleButton = styled.button`
  width: 100%;
  padding: 12px 20px;
  background: #fff;
  color: #333;
  border: 1px solid #dadce0;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.2s ease;
  margin-top: 10px;
  
  &:hover:not(:disabled) {
    background: #f8f9fa;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  &:active:not(:disabled) {
    background: #f1f3f4;
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`

const GoogleIcon = styled.span`
  display: flex;
  align-items: center;
  justify-content: center;
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
  const { login, verify2FA, register, updateUser, checkAuthStatus } = useAuth()
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
      showMessage(result.message || 'Login successful!')
      setTimeout(() => {
        navigate('/feed')
      }, 800)
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
      showMessage('Login successful!')
      setRequires2FA(false)
      setTempToken(null)
      setTwoFactorCode('')
      setTimeout(() => {
        navigate('/feed')
      }, 800)
    } else {
      showMessage(result.message || 'Invalid 2FA code', true)
      setTwoFactorCode('')
    }
    
    setLoading(false)
  }

  const handleGoogleSignIn = async () => {
    setLoading(true)
    setMessage('')
    setErrors([])
    
    try {
      // Sign in with Google using Firebase
      const result = await signInWithPopup(auth, googleProvider)
      const user = result.user
      
      // Get the ID token
      const idToken = await user.getIdToken()
      
      // Send token to backend for verification and user creation/login
      const response = await api.post('/api/auth/google', { id_token: idToken })
      
      if (response.data && response.data.access_token) {
        // Store tokens using tokenService
        const { access_token, refresh_token, user: userData } = response.data
        tokenService.setTokens(access_token, refresh_token)
        
        // Update AuthContext with user data
        if (userData) {
          updateUser(userData)
        } else {
          // If user data not in response, fetch it from backend
          await checkAuthStatus()
        }
        
        showMessage('Login successful!')
        // Wait a bit longer to ensure state is updated before navigation
        setTimeout(() => {
          navigate('/feed')
        }, 1000)
      } else {
        showMessage(response.data?.detail || 'Google sign-in failed', true)
      }
    } catch (error) {
      console.error('Google sign-in error:', error)
      if (error.code === 'auth/popup-closed-by-user') {
        showMessage('Sign-in cancelled', true)
      } else {
        showMessage(error.message || 'Google sign-in failed', true)
      }
    } finally {
      setLoading(false)
    }
  }

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
      showMessage(result.message || 'Account created successfully!')
      setTimeout(() => {
        navigate('/feed')
      }, 800)
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
                <div style={{ marginBottom: '20px', textAlign: 'center' }}>
                  <h3 style={{ margin: '0 0 10px 0', color: 'var(--text)' }}>Two-Factor Authentication</h3>
                  <p style={{ margin: 0, color: 'var(--text-light)', fontSize: '0.9em' }}>
                    Enter the 6-digit code from your authenticator app
                  </p>
                </div>
                <InputWrapper>
                  <Label htmlFor="2fa-code">2FA Code</Label>
                  <Input 
                    id="2fa-code"
                    type="text" 
                    value={twoFactorCode}
                    onChange={(e) => setTwoFactorCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    placeholder="000000"
                    maxLength={6}
                    autoComplete="one-time-code"
                    required
                    style={{ 
                      fontFamily: 'monospace', 
                      fontSize: '1.5em', 
                      letterSpacing: '0.5em', 
                      textAlign: 'center' 
                    }}
                  />
                  <PasswordHint>You can also use a backup code (8 characters)</PasswordHint>
                </InputWrapper>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <Button type="submit" disabled={loading || twoFactorCode.length !== 6}>
                    {loading ? <LoadingSpinner>Verifying...</LoadingSpinner> : 'Verify →'}
                  </Button>
                  <Button 
                    type="button" 
                    onClick={() => {
                      setRequires2FA(false)
                      setTempToken(null)
                      setTwoFactorCode('')
                      setMessage('')
                    }}
                    style={{ background: 'var(--bg-light)', color: 'var(--text)' }}
                  >
                    Back
                  </Button>
                </div>
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
              <Button type="submit" disabled={loading}>
                {loading ? <LoadingSpinner>Creating Account...</LoadingSpinner> : 'Sign Up →'}
              </Button>
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
