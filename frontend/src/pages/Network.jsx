import React, { useState, useRef, useEffect } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { motion, useInView } from 'framer-motion'
import { networkAPI, connectionAPI, notificationAPI } from '../services/api'

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
`

const NavLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
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
`

const NavRight = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
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
`

const Header = styled.div`
  margin-bottom: 30px;
  animation: ${slideUp} 0.4s ease-out;
`

const PageTitle = styled.h1`
  font-size: 2em;
  color: var(--text);
  margin-bottom: 8px;
  font-weight: 300;
`

const PageSubtitle = styled.p`
  font-size: 1em;
  color: var(--text-light);
`

const TabContainer = styled.div`
  display: flex;
  gap: 0;
  margin-bottom: 30px;
  border-bottom: 2px solid var(--border);
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

  &:hover {
    color: var(--primary);
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
`

const PersonHeader = styled.div`
  height: 80px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  position: relative;
`

const PersonContent = styled.div`
  padding: 60px 20px 20px;
  position: relative;
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
`

const PersonName = styled.h3`
  font-size: 1.2em;
  color: var(--text);
  margin-bottom: 4px;
  font-weight: 400;
  text-align: center;
`

const PersonTitle = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
  margin-bottom: 8px;
  text-align: center;
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
  background: rgba(10, 102, 194, 0.1);
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
  background: rgba(10, 102, 194, 0.1);
  color: var(--primary);
  border-radius: 12px;
  font-weight: 400;
`

const ButtonGroup = styled.div`
  display: flex;
  gap: 10px;
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
    box-shadow: 0 6px 16px rgba(10, 102, 194, 0.3);
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
const UserCard = ({ user, onConnect, isPending, isConnected, loading }) => {
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
          {user.skills?.length > 0 && (
          <PersonSkills>
              {user.skills.slice(0, 3).map((skill, idx) => (
              <SkillTag key={idx}>{skill}</SkillTag>
            ))}
          </PersonSkills>
          )}
          <ConnectButton 
            onClick={() => onConnect(user.id)}
            pending={isPending}
            connected={isConnected}
            disabled={loading || isPending || isConnected}
          >
            {isConnected ? (
              <>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                Connected
              </>
            ) : isPending ? (
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
          <PeopleGrid>
            {connections.map(user => (
              <UserCard
                key={user.id}
                user={user}
                onConnect={() => {}}
                isPending={false}
                isConnected={true}
                loading={false}
              />
            ))}
          </PeopleGrid>
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
      <Navbar>
        <NavContainer>
          <NavLeft>
            <Logo onClick={handleBackToFeed}>ZedReq</Logo>
          </NavLeft>
          <NavRight>
            <IconButton onClick={() => navigate('/notifications')}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
              </svg>
              {unreadNotifications > 0 && (
                <NotificationBadge>{unreadNotifications}</NotificationBadge>
              )}
            </IconButton>
            <IconButton onClick={handleBackToFeed}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
            </IconButton>
          </NavRight>
        </NavContainer>
      </Navbar>

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
            <TabBadge>{connections.length}</TabBadge>
          </Tab>
          <Tab 
            active={activeTab === 'requests'} 
            onClick={() => setActiveTab('requests')}
          >
            Requests
            {pendingRequests.length > 0 && (
              <TabBadge highlight>{pendingRequests.length}</TabBadge>
            )}
          </Tab>
        </TabContainer>

        {renderContent()}
      </MainContainer>
    </Container>
  )
}

export default Network
