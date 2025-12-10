import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import styled, { keyframes } from 'styled-components'
import { useAuth } from '../contexts/AuthContext'

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`

const slideIn = keyframes`
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`

const Container = styled.div`
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  min-height: 100vh;
  width: 100%;
  animation: ${fadeIn} 0.6s ease-in;
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
  display: ${props => props.active ? 'block' : 'none'};
  animation: ${props => props.active ? slideIn : 'none'} 0.3s ease-out;
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
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-light);
  color: var(--text);
  font-size: 1em;
  transition: border-color 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: var(--primary);
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
  
  &:hover {
    background: var(--primary-dark);
    transform: translateY(-2px);
  }
  
  &:active {
    transform: translateY(0) scale(0.98);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
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

const RightPanel = styled.div`
  background: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  position: relative;
  overflow: hidden;
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

const Landing = () => {
  const [activeTab, setActiveTab] = useState('login')
  const [message, setMessage] = useState('')
  const [isError, setIsError] = useState(false)
  const [loading, setLoading] = useState(false)
  const { login, register } = useAuth()
  const navigate = useNavigate()

  const showMessage = (text, error = false) => {
    setMessage('')
    setIsError(false)
    
    setTimeout(() => {
      setMessage(text)
      setIsError(error)
    }, 300)
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    const formData = new FormData(e.target)
    const username = formData.get('username')
    const password = formData.get('password')
    
    const result = await login(username, password)
    
    if (result.success) {
      showMessage(result.message)
      setTimeout(() => {
        navigate('/feed')
      }, 1000)
    } else {
      showMessage(result.message, true)
    }
    
    setLoading(false)
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setLoading(true)
    
    const formData = new FormData(e.target)
    const userData = {
      full_name: formData.get('full_name'),
      username: formData.get('username'),
      email: formData.get('email'),
      password: formData.get('password')
    }
    
    const result = await register(userData)
    
    if (result.success) {
      showMessage(result.message)
      setTimeout(() => {
        navigate('/feed')
      }, 1000)
    } else {
      showMessage(result.message, true)
    }
    
    setLoading(false)
  }

  return (
    <Container>
      <LeftPanel>
        <BackArrow to="/">←</BackArrow>
        <Logo>ZedReq</Logo>
        <PageTitle>Sign In</PageTitle>
        
        <AuthContainer>
          <Tabs>
            <TabButton 
              className={activeTab === 'login' ? 'active' : ''}
              onClick={() => setActiveTab('login')}
            >
              Sign In
            </TabButton>
            <TabButton 
              className={activeTab === 'register' ? 'active' : ''}
              onClick={() => setActiveTab('register')}
            >
              Sign Up
            </TabButton>
          </Tabs>
          
          <TabContent active={activeTab === 'login'}>
            <Form onSubmit={handleLogin}>
              <InputWrapper>
                <Label>Username or Email</Label>
                <Input 
                  type="text" 
                  name="username" 
                  placeholder="Username or Email" 
                  required 
                />
              </InputWrapper>
              <InputWrapper>
                <Label>Password</Label>
                <Input 
                  type="password" 
                  name="password" 
                  placeholder="Password" 
                  required 
                />
              </InputWrapper>
              <Button type="submit" disabled={loading}>
                {loading ? 'Signing In...' : 'Sign In →'}
              </Button>
            </Form>
          </TabContent>
          
          <TabContent active={activeTab === 'register'}>
            <Form onSubmit={handleRegister}>
              <InputWrapper>
                <Label>Full Name</Label>
                <Input 
                  type="text" 
                  name="full_name" 
                  placeholder="Full Name" 
                  required 
                />
              </InputWrapper>
              <InputWrapper>
                <Label>Username</Label>
                <Input 
                  type="text" 
                  name="username" 
                  placeholder="Username" 
                  required 
                />
              </InputWrapper>
              <InputWrapper>
                <Label>Email</Label>
                <Input 
                  type="email" 
                  name="email" 
                  placeholder="Email" 
                  required 
                />
              </InputWrapper>
              <InputWrapper>
                <Label>Password</Label>
                <Input 
                  type="password" 
                  name="password" 
                  placeholder="Password" 
                  required 
                />
              </InputWrapper>
              <Button type="submit" disabled={loading}>
                {loading ? 'Creating Account...' : 'Sign Up →'}
              </Button>
            </Form>
          </TabContent>
          
          <Message className={`${message ? 'show' : ''} ${isError ? 'error' : 'success'}`}>
            {message}
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
