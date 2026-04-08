import React, { useState, useRef, useEffect } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { motion, useInView } from 'framer-motion'
import { networkAPI, connectionAPI, notificationAPI } from '../services/api'
import Messages from './Messages'
import Navbar from '../components/Navbar'

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`

const slideUp = keyframes`
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`

const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`

const Container = styled.div`
  min-height: 100vh;
  width: 100%;
  background: var(--bg-light);
  animation: ${fadeIn} 0.6s ease-in;
`


const NotificationBadge = styled.span`
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ef4444;
  color: white;
  font-size: 0.7em;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 600;
`

const IconButton = styled.button`
  position: relative;
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
`

const MainContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px 20px;
  
  @media (max-width: 1024px) {
    padding: 25px 18px;
  }
  
  @media (max-width: 768px) {
    padding: 20px 15px;
  }
  
  @media (max-width: 600px) {
    padding: 18px 12px;
  }
  
  @media (max-width: 480px) {
    padding: 15px 12px;
  }
  
  @media (max-width: 360px) {
    padding: 12px 10px;
  }
`

const Header = styled.div`
  margin-bottom: 30px;
  animation: ${slideUp} 0.4s ease-out;
  
  @media (max-width: 768px) {
    margin-bottom: 24px;
  }
  
  @media (max-width: 480px) {
    margin-bottom: 20px;
  }
  
  @media (max-width: 360px) {
    margin-bottom: 18px;
  }
`

const PageTitle = styled.h1`
  font-size: 2em;
  color: var(--text);
  margin-bottom: 8px;
  font-weight: 300;
  
  @media (max-width: 1024px) {
    font-size: 1.8em;
  }
  
  @media (max-width: 768px) {
    font-size: 1.6em;
    margin-bottom: 6px;
  }
  
  @media (max-width: 600px) {
    font-size: 1.4em;
  }
  
  @media (max-width: 480px) {
    font-size: 1.3em;
    margin-bottom: 5px;
  }
  
  @media (max-width: 360px) {
    font-size: 1.2em;
  }
`

const PageSubtitle = styled.p`
  font-size: 1em;
  color: var(--text-light);
  
  @media (max-width: 768px) {
    font-size: 0.95em;
  }
  
  @media (max-width: 480px) {
    font-size: 0.9em;
  }
  
  @media (max-width: 360px) {
    font-size: 0.85em;
  }
`

const TabContainer = styled.div`
  display: flex;
  gap: 0;
  margin-bottom: 30px;
  border-bottom: 2px solid var(--border);
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  -ms-overflow-style: none;
  
  &::-webkit-scrollbar {
    display: none;
  }
  
  @media (max-width: 768px) {
    margin-bottom: 24px;
  }
  
  @media (max-width: 480px) {
    margin-bottom: 20px;
  }
  
  @media (max-width: 360px) {
    margin-bottom: 18px;
  }
`

const Tab = styled.button`
  padding: 14px 24px;
  background: transparent;
  color: ${props => props.active ? 'var(--primary)' : 'var(--text-light)'};
  border: none;
  border-bottom: 2px solid ${props => props.active ? 'var(--primary)' : 'transparent'};
  margin-bottom: -2px;
  cursor: pointer;
  font-size: 1em;
  font-weight: ${props => props.active ? '500' : '400'};
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  min-height: 44px; /* Better touch target */

  &:hover {
    color: var(--primary);
  }
  
  @media (max-width: 768px) {
    padding: 12px 20px;
    font-size: 0.95em;
    min-height: 42px;
  }
  
  @media (max-width: 600px) {
    padding: 10px 16px;
    font-size: 0.9em;
    gap: 6px;
  }
  
  @media (max-width: 480px) {
    padding: 10px 14px;
    font-size: 0.85em;
    min-height: 40px;
    gap: 5px;
  }
  
  @media (max-width: 360px) {
    padding: 8px 12px;
    font-size: 0.8em;
    min-height: 38px;
    gap: 4px;
  }
`

const TabBadge = styled.span`
  background: ${props => props.highlight ? '#ef4444' : 'var(--bg-light)'};
  color: ${props => props.highlight ? 'white' : 'var(--text-light)'};
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.85em;
`

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px;
  
  &::after {
    content: '';
    width: 40px;
    height: 40px;
    border: 3px solid var(--border);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: var(--text-light);
  
  svg {
    width: 64px;
    height: 64px;
    margin-bottom: 16px;
    opacity: 0.5;
  }
  
  h3 {
    font-size: 1.2em;
    margin-bottom: 8px;
    color: var(--text);
  }
`

const PeopleGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  
  @media (max-width: 1024px) {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
  }
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 18px;
  }
  
  @media (max-width: 600px) {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  @media (max-width: 480px) {
    gap: 14px;
  }
  
  @media (max-width: 360px) {
    gap: 12px;
  }
`

const PersonCard = styled.div`
  background: var(--bg-white);
  border-radius: 16px;
  border: 1px solid var(--border);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    border-color: var(--primary);
  }
  
  @media (max-width: 768px) {
    border-radius: 12px;
    
    &:hover {
      transform: translateY(-2px);
    }
  }
  
  @media (max-width: 480px) {
    border-radius: 10px;
    
    &:hover {
      transform: none;
    }
  }
  
  @media (max-width: 360px) {
    border-radius: 8px;
  }
`

const PersonHeader = styled.div`
  height: 80px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  position: relative;
  
  @media (max-width: 768px) {
    height: 70px;
  }
  
  @media (max-width: 480px) {
    height: 60px;
  }
  
  @media (max-width: 360px) {
    height: 55px;
  }
`

const PersonContent = styled.div`
  padding: 60px 20px 20px;
  position: relative;
  
  @media (max-width: 768px) {
    padding: 55px 18px 18px;
  }
  
  @media (max-width: 480px) {
    padding: 50px 16px 16px;
  }
  
  @media (max-width: 360px) {
    padding: 45px 14px 14px;
  }
`

const PersonAvatar = styled.div`
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: ${props => props.src ? `url(${props.src}) center/cover` : 'var(--primary)'};
  border: 4px solid var(--bg-white);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2em;
  font-weight: 500;
  position: absolute;
  top: -50px;
  left: 50%;
  transform: translateX(-50%);
  transition: all 0.3s ease;

  ${PersonCard}:hover & {
    transform: translateX(-50%) scale(1.05);
  }
  
  @media (max-width: 768px) {
    width: 90px;
    height: 90px;
    top: -45px;
    font-size: 1.8em;
    border-width: 3.5px;
  }
  
  @media (max-width: 480px) {
    width: 80px;
    height: 80px;
    top: -40px;
    font-size: 1.6em;
    border-width: 3px;
  }
  
  @media (max-width: 360px) {
    width: 70px;
    height: 70px;
    top: -35px;
    font-size: 1.4em;
    border-width: 2.5px;
  }
`

const PersonName = styled.h3`
  font-size: 1.2em;
  color: var(--text);
  margin-bottom: 4px;
  font-weight: 400;
  text-align: center;
  word-wrap: break-word;
  
  @media (max-width: 768px) {
    font-size: 1.1em;
    margin-bottom: 3px;
  }
  
  @media (max-width: 480px) {
    font-size: 1.05em;
    margin-bottom: 2px;
  }
  
  @media (max-width: 360px) {
    font-size: 1em;
  }
`

const PersonTitle = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
  margin-bottom: 8px;
  text-align: center;
  word-wrap: break-word;
  
  @media (max-width: 768px) {
    font-size: 0.85em;
    margin-bottom: 6px;
  }
  
  @media (max-width: 480px) {
    font-size: 0.8em;
    margin-bottom: 5px;
  }
  
  @media (max-width: 360px) {
    font-size: 0.75em;
    margin-bottom: 4px;
  }
`

const PersonCompany = styled.p`
  font-size: 0.85em;
  color: var(--text-lighter);
  margin-bottom: 16px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
`

const PersonBio = styled.p`
  font-size: 0.85em;
  color: var(--text-light);
  line-height: 1.5;
  margin-bottom: 16px;
  text-align: center;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
`

const MutualConnections = styled.div`
  font-size: 0.85em;
  color: var(--primary);
  text-align: center;
  margin-bottom: 16px;
  padding: 8px;
  background: rgba(21, 133, 161, 0.1);
  border-radius: 8px;
`

const PersonSkills = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
  justify-content: center;
`

const SkillTag = styled.span`
  font-size: 0.75em;
  padding: 4px 10px;
  background: rgba(21, 133, 161, 0.1);
  color: var(--primary);
  border-radius: 12px;
  font-weight: 400;
`

const ButtonGroup = styled.div`
  display: flex;
  gap: 10px;
  
  @media (max-width: 480px) {
    flex-direction: column;
    gap: 8px;
  }
  
  @media (max-width: 360px) {
    gap: 6px;
  }
`

const MessageButton = styled.button`
  padding: 12px 20px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.95em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 44px; /* Better touch target */
  flex: 1;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(21, 133, 161, 0.3);
    background: var(--primary-dark);
  }
  
  @media (max-width: 768px) {
    padding: 10px 18px;
    font-size: 0.9em;
    min-height: 42px;
  }
  
  @media (max-width: 480px) {
    padding: 10px 16px;
    font-size: 0.85em;
    min-height: 40px;
    width: 100%;
    
    &:hover {
      transform: none;
    }
  }
  
  @media (max-width: 360px) {
    padding: 8px 14px;
    font-size: 0.8em;
    min-height: 38px;
  }

  &:active {
    transform: translateY(0);
  }

  svg {
    width: 18px;
    height: 18px;
  }
`

const MessagesPanel = styled.aside`
  position: fixed;
  top: 100px;
  right: ${props => props.isOpen ? '20px' : '-400px'};
  width: 380px;
  height: 500px;
  max-height: calc(100vh - 140px);
  background: var(--bg-white);
  border-radius: 16px;
  border: 1px solid var(--border);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 200;
  opacity: ${props => props.isOpen ? 1 : 0};
  pointer-events: ${props => props.isOpen ? 'auto' : 'none'};
  transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.4s ease;

  @media (max-width: 768px) {
    width: 350px;
    top: 80px;
    height: 480px;
    max-height: calc(100vh - 120px);
    right: ${props => props.isOpen ? '20px' : '-380px'};
  }

  @media (max-width: 480px) {
    width: calc(100vw - 40px);
    height: 450px;
    max-height: calc(100vh - 100px);
    right: ${props => props.isOpen ? '20px' : 'calc(-100vw)'};
  }
`

const ConnectButton = styled.button`
  flex: 1;
  padding: 12px 20px;
  background: ${props => {
    if (props.pending) return 'var(--bg-light)'
    if (props.connected) return 'transparent'
    return 'linear-gradient(135deg, var(--primary), var(--secondary))'
  }};
  color: ${props => {
    if (props.pending) return 'var(--text-light)'
    if (props.connected) return 'var(--primary)'
    return 'white'
  }};
  border: ${props => props.connected ? '2px solid var(--primary)' : 'none'};
  border-radius: 8px;
  font-size: 0.95em;
  font-weight: 500;
  cursor: ${props => props.pending ? 'default' : 'pointer'};
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  &:hover {
    ${props => !props.pending && `
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(21, 133, 161, 0.3);
    `}
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`

const AcceptButton = styled(ConnectButton)`
  background: linear-gradient(135deg, #10b981, #059669);
`

const RejectButton = styled(ConnectButton)`
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-light);
  
  &:hover {
    border-color: #ef4444;
    color: #ef4444;
  }
`

// Request Card Component
const RequestCard = ({ request, onAccept, onReject, loading }) => {
  const user = request.sender || request.receiver
  const isReceived = !!request.sender
  
  return (
    <PersonCard>
      <PersonHeader />
      <PersonContent>
        <PersonAvatar src={user?.profile_pic}>
          {!user?.profile_pic && user?.name?.charAt(0).toUpperCase()}
        </PersonAvatar>
        <PersonName>{user?.name}</PersonName>
        <PersonTitle>@{user?.username}</PersonTitle>
        {request.message && (
          <PersonBio>"{request.message}"</PersonBio>
        )}
        {isReceived ? (
          <ButtonGroup>
            <AcceptButton 
              onClick={() => onAccept(request.id)}
              disabled={loading}
            >
              Accept
            </AcceptButton>
            <RejectButton 
              onClick={() => onReject(request.id)}
              disabled={loading}
            >
              Ignore
            </RejectButton>
          </ButtonGroup>
        ) : (
          <ConnectButton pending disabled>
            Pending...
          </ConnectButton>
        )}
      </PersonContent>
    </PersonCard>
  )
}

// User Card Component
const UserCard = ({ user, onConnect, isPending, isConnected, loading, onMessage }) => {
  const ref = useRef(null)
  const inView = useInView(ref, { amount: 0.3, triggerOnce: true })
  
  return (
    <motion.div
      ref={ref}
      initial={{ scale: 0.9, opacity: 0 }}
      animate={inView ? { scale: 1, opacity: 1 } : { scale: 0.9, opacity: 0 }}
      transition={{ duration: 0.4 }}
    >
      <PersonCard>
        <PersonHeader />
        <PersonContent>
          <PersonAvatar src={user.profile_pic}>
            {!user.profile_pic && user.name?.charAt(0).toUpperCase()}
          </PersonAvatar>
          <PersonName>{user.name}</PersonName>
          <PersonTitle>@{user.username}</PersonTitle>
          {user.job_title && user.company && (
          <PersonCompany>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
            </svg>
              {user.job_title} at {user.company}
          </PersonCompany>
          )}
          {user.bio && <PersonBio>{user.bio}</PersonBio>}
          {user.mutual_connections > 0 && (
            <MutualConnections>
              {user.mutual_connections} mutual connection{user.mutual_connections > 1 ? 's' : ''}
              {user.mutual_connection_names?.length > 0 && (
                <> including {user.mutual_connection_names.join(', ')}</>
              )}
            </MutualConnections>
          )}
          {(() => {
            // Parse skills to ensure it's always an array
            let skillsArray = []
            if (user.skills) {
              if (Array.isArray(user.skills)) {
                skillsArray = user.skills
              } else if (typeof user.skills === 'string') {
                // Try to parse as JSON first, then fall back to comma-separated
                try {
                  const parsed = JSON.parse(user.skills)
                  skillsArray = Array.isArray(parsed) ? parsed : []
                } catch {
                  skillsArray = user.skills.split(',').map(s => s.trim()).filter(Boolean)
                }
              }
            }
            return skillsArray.length > 0 && (
              <PersonSkills>
                {skillsArray.slice(0, 3).map((skill, idx) => (
                  <SkillTag key={idx}>{skill}</SkillTag>
                ))}
              </PersonSkills>
            )
          })()}
          {isConnected ? (
            <ButtonGroup>
              <ConnectButton 
                connected={true}
                disabled={true}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                Connected
              </ConnectButton>
              <MessageButton onClick={() => onMessage && onMessage(user.id)}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                Message
              </MessageButton>
            </ButtonGroup>
          ) : (
            <ConnectButton 
              onClick={() => onConnect(user.id)}
              pending={isPending}
              disabled={loading || isPending}
            >
              {isPending ? (
                'Pending...'
              ) : (
                <>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                    <circle cx="8.5" cy="7" r="4"></circle>
                    <line x1="20" y1="8" x2="20" y2="14"></line>
                    <line x1="23" y1="11" x2="17" y2="11"></line>
                  </svg>
                  Connect
                </>
              )}
            </ConnectButton>
          )}
        </PersonContent>
      </PersonCard>
    </motion.div>
  )
}

const Network = () => {
  const [activeTab, setActiveTab] = useState('discover')
  const [discoverUsers, setDiscoverUsers] = useState([])
  const [suggestions, setSuggestions] = useState([])
  const [connections, setConnections] = useState([])
  const [pendingRequests, setPendingRequests] = useState([])
  const [sentRequests, setSentRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)
  const [pendingUserIds, setPendingUserIds] = useState(new Set())
  const [messagesOpen, setMessagesOpen] = useState(false)
  const [selectedUserId, setSelectedUserId] = useState(null)
  const [selectedUser, setSelectedUser] = useState(null)
  const navigate = useNavigate()
  const { logout, unreadNotifications } = useAuth()

  useEffect(() => {
    loadData()
  }, [activeTab])

  const loadData = async () => {
    setLoading(true)
    try {
      switch (activeTab) {
        case 'discover':
          const discoverRes = await networkAPI.discoverUsers(20)
          setDiscoverUsers(discoverRes.data)
          break
        case 'suggestions':
          const suggestRes = await networkAPI.getSuggestions(20)
          setSuggestions(suggestRes.data)
          break
        case 'connections':
          const connRes = await networkAPI.getConnections()
          setConnections(connRes.data)
          break
        case 'requests':
          const [pendingRes, sentRes] = await Promise.all([
            connectionAPI.getPendingRequests(),
            connectionAPI.getSentRequests()
          ])
          setPendingRequests(pendingRes.data)
          setSentRequests(sentRes.data)
          // Track sent request user IDs
          setPendingUserIds(new Set(sentRes.data.map(r => r.receiver_id)))
          break
      }
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleConnect = async (userId) => {
    setActionLoading(true)
    try {
      await connectionAPI.sendRequest(userId)
      setPendingUserIds(prev => new Set([...prev, userId]))
      // Refresh discover list
      if (activeTab === 'discover') {
        const res = await networkAPI.discoverUsers(20)
        setDiscoverUsers(res.data)
      } else if (activeTab === 'suggestions') {
        const res = await networkAPI.getSuggestions(20)
        setSuggestions(res.data)
      }
    } catch (error) {
      console.error('Error sending connection request:', error)
      alert(error.response?.data?.detail || 'Failed to send connection request')
    } finally {
      setActionLoading(false)
    }
  }

  const handleAccept = async (requestId) => {
    setActionLoading(true)
    try {
      await connectionAPI.acceptRequest(requestId)
      // Refresh requests
      const [pendingRes, sentRes] = await Promise.all([
        connectionAPI.getPendingRequests(),
        connectionAPI.getSentRequests()
      ])
      setPendingRequests(pendingRes.data)
      setSentRequests(sentRes.data)
    } catch (error) {
      console.error('Error accepting request:', error)
      alert(error.response?.data?.detail || 'Failed to accept request')
    } finally {
      setActionLoading(false)
    }
  }

  const handleReject = async (requestId) => {
    setActionLoading(true)
    try {
      await connectionAPI.rejectRequest(requestId)
      // Remove from list
      setPendingRequests(prev => prev.filter(r => r.id !== requestId))
    } catch (error) {
      console.error('Error rejecting request:', error)
      alert(error.response?.data?.detail || 'Failed to reject request')
    } finally {
      setActionLoading(false)
    }
  }

  const handleBackToFeed = () => {
    navigate('/feed')
  }

  const handleMessageClick = (userId, userData = null) => {
    setSelectedUserId(userId)
    setSelectedUser(userData)
    setMessagesOpen(true)
  }

  const handleCloseMessages = () => {
    setMessagesOpen(false)
    setSelectedUserId(null)
    setSelectedUser(null)
  }

  const renderContent = () => {
    if (loading) {
      return <LoadingSpinner />
    }

    switch (activeTab) {
      case 'discover':
        return discoverUsers.length === 0 ? (
          <EmptyState>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <h3>No users to discover</h3>
            <p>You've seen everyone! Check back later for new users.</p>
          </EmptyState>
        ) : (
          <PeopleGrid>
            {discoverUsers.map(user => (
              <UserCard
                key={user.id}
                user={user}
                onConnect={handleConnect}
                isPending={pendingUserIds.has(user.id)}
                isConnected={false}
                loading={actionLoading}
              />
            ))}
          </PeopleGrid>
        )
      
      case 'suggestions':
        return suggestions.length === 0 ? (
          <EmptyState>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
            <h3>No suggestions yet</h3>
            <p>Connect with more people to get friend-of-friend suggestions.</p>
          </EmptyState>
        ) : (
          <PeopleGrid>
            {suggestions.map(user => (
              <UserCard
                key={user.id}
                user={user}
                onConnect={handleConnect}
                isPending={pendingUserIds.has(user.id)}
                isConnected={false}
                loading={actionLoading}
              />
            ))}
          </PeopleGrid>
        )
      
      case 'connections':
        return connections.length === 0 ? (
          <EmptyState>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
            </svg>
            <h3>No connections yet</h3>
            <p>Start connecting with people to grow your network.</p>
          </EmptyState>
        ) : (
          <>
            <PageSubtitle style={{ marginBottom: '16px' }}>
              My Connections ({connections.length})
            </PageSubtitle>
            <PeopleGrid>
              {connections.map(user => (
                <UserCard
                  key={user.id}
                  user={user}
                  onConnect={() => {}}
                  isPending={false}
                  isConnected={true}
                  loading={false}
                  onMessage={(userId) => handleMessageClick(userId, user)}
                />
              ))}
            </PeopleGrid>
          </>
        )
      
      case 'requests':
        const totalRequests = pendingRequests.length + sentRequests.length
        return totalRequests === 0 ? (
          <EmptyState>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="8.5" cy="7" r="4"></circle>
              <polyline points="17 11 19 13 23 9"></polyline>
            </svg>
            <h3>No pending requests</h3>
            <p>When someone wants to connect, you'll see it here.</p>
          </EmptyState>
        ) : (
          <>
            {pendingRequests.length > 0 && (
              <>
                <PageSubtitle style={{ marginBottom: '16px' }}>
                  Received ({pendingRequests.length})
                </PageSubtitle>
                <PeopleGrid style={{ marginBottom: '30px' }}>
                  {pendingRequests.map(request => (
                    <RequestCard
                      key={request.id}
                      request={request}
                      onAccept={handleAccept}
                      onReject={handleReject}
                      loading={actionLoading}
                    />
                  ))}
                </PeopleGrid>
              </>
            )}
            {sentRequests.length > 0 && (
              <>
                <PageSubtitle style={{ marginBottom: '16px' }}>
                  Sent ({sentRequests.length})
                </PageSubtitle>
                <PeopleGrid>
                  {sentRequests.map(request => (
                    <RequestCard
                      key={request.id}
                      request={request}
                      onAccept={() => {}}
                      onReject={() => {}}
                      loading={false}
                    />
                  ))}
                </PeopleGrid>
              </>
            )}
          </>
        )
      
      default:
        return null
    }
  }

  return (
    <Container>
      <Navbar />

      <MainContainer>
        <Header>
          <PageTitle>My Network</PageTitle>
          <PageSubtitle>Grow your professional network and discover new opportunities</PageSubtitle>
        </Header>

        <TabContainer>
          <Tab 
            active={activeTab === 'discover'} 
            onClick={() => setActiveTab('discover')}
          >
            Discover
          </Tab>
          <Tab 
            active={activeTab === 'suggestions'} 
            onClick={() => setActiveTab('suggestions')}
          >
            Suggestions
          </Tab>
          <Tab 
            active={activeTab === 'connections'} 
            onClick={() => setActiveTab('connections')}
          >
            My Connections
          </Tab>
          <Tab 
            active={activeTab === 'requests'} 
            onClick={() => setActiveTab('requests')}
          >
            Requests
          </Tab>
        </TabContainer>

        {renderContent()}
      </MainContainer>

      <MessagesPanel isOpen={messagesOpen}>
        <Messages 
          overlay={true} 
          onClose={handleCloseMessages}
          initialRecipientId={selectedUserId}
          initialRecipient={selectedUser}
        />
      </MessagesPanel>
    </Container>
  )
}

export default Network
