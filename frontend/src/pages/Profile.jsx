import React, { useState, useEffect } from 'react'
import styled, { keyframes } from 'styled-components'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { userAPI, connectionAPI, postAPI } from '../services/api'
import { parseProfileUrl, generateProfileUrl } from '../utils/profileUrl'
import '../css/pages/Profile.css'

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`

const slideUp = keyframes`
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`

const Container = styled.div`
  min-height: 100vh;
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
  
  @media (max-width: 768px) {
    padding: 0 15px;
  }
  
  @media (max-width: 480px) {
    padding: 0 12px;
  }
`

const NavContainer = styled.div`
  max-width: 100%;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  gap: 30px;
  
  @media (max-width: 768px) {
    gap: 15px;
    padding: 10px 0;
  }
  
  @media (max-width: 480px) {
    gap: 10px;
    padding: 8px 0;
  }
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
  
  @media (max-width: 768px) {
    font-size: 1.5em;
  }
  
  @media (max-width: 480px) {
    font-size: 1.3em;
  }
`

const NavRight = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
`

const BackButton = styled.button`
  padding: 10px 16px;
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9em;
  
  &:hover {
    background: var(--hover-bg);
    border-color: var(--primary);
  }
`

const ProfileWrapper = styled.div`
  max-width: 1128px;
  margin: 0 auto;
  padding: 0;
`

const CoverPhotoSection = styled.div`
  position: relative;
  width: 100%;
  height: 200px;
  background: ${props => props.coverPic 
    ? `url(${props.coverPic}) center/cover no-repeat`
    : 'linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%)'
  };
  border-radius: 0;
  
  @media (max-width: 768px) {
    height: 150px;
  }
  
  @media (max-width: 480px) {
    height: 120px;
  }
`

const ProfileInfoCard = styled.div`
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 0 0 12px 12px;
  padding: 0;
  margin-bottom: 24px;
  position: relative;
`

const ProfilePictureWrapper = styled.div`
  position: absolute;
  top: -76px;
  left: 24px;
  width: 152px;
  height: 152px;
  border-radius: 50%;
  border: 4px solid var(--bg-white);
  background: var(--bg-white);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  
  @media (max-width: 768px) {
    width: 120px;
    height: 120px;
    top: -60px;
    left: 16px;
  }
  
  @media (max-width: 480px) {
    width: 100px;
    height: 100px;
    top: -50px;
    left: 12px;
  }
`

const ProfilePicture = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
`

const ProfilePicturePlaceholder = styled.div`
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 3em;
  font-weight: 300;
  
  @media (max-width: 768px) {
    font-size: 2.5em;
  }
  
  @media (max-width: 480px) {
    font-size: 2em;
  }
`

const ProfileHeaderContent = styled.div`
  padding: 100px 24px 24px 24px;
  
  @media (max-width: 768px) {
    padding: 80px 20px 20px 20px;
  }
  
  @media (max-width: 480px) {
    padding: 70px 16px 16px 16px;
  }
`

const ProfileName = styled.h1`
  font-size: 2em;
  font-weight: 400;
  color: var(--text);
  margin: 0 0 8px 0;
  
  @media (max-width: 768px) {
    font-size: 1.6em;
  }
  
  @media (max-width: 480px) {
    font-size: 1.4em;
  }
`

const ProfileHeadline = styled.p`
  font-size: 1.1em;
  color: var(--text-light);
  margin: 0 0 8px 0;
  
  @media (max-width: 768px) {
    font-size: 1em;
  }
  
  @media (max-width: 480px) {
    font-size: 0.95em;
  }
`

const ProfileLocation = styled.p`
  font-size: 0.95em;
  color: var(--text-lighter);
  margin: 0 0 16px 0;
  
  @media (max-width: 480px) {
    font-size: 0.9em;
  }
`

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 16px;
  flex-wrap: wrap;
  
  @media (max-width: 480px) {
    flex-direction: column;
  }
`

const ActionButton = styled.button`
  padding: 10px 24px;
  border-radius: 24px;
  border: ${props => props.primary ? 'none' : '1px solid var(--primary)'};
  background: ${props => props.primary ? 'var(--primary)' : 'transparent'};
  color: ${props => props.primary ? 'white' : 'var(--primary)'};
  font-size: 0.95em;
  font-weight: 500;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: ${props => props.disabled ? 0.6 : 1};
  
  &:hover:not(:disabled) {
    background: ${props => props.primary ? 'var(--primary-dark)' : 'rgba(10, 102, 194, 0.1)'};
    transform: translateY(-2px);
  }
  
  &:disabled {
    transform: none;
  }
  
  @media (max-width: 480px) {
    width: 100%;
    justify-content: center;
  }
`

const ContentLayout = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  padding: 0 20px 24px 20px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 20px;
    padding: 0 16px 20px 16px;
  }
  
  @media (max-width: 480px) {
    gap: 16px;
    padding: 0 12px 16px 12px;
  }
`

const MainColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
  
  @media (max-width: 768px) {
    gap: 20px;
  }
  
  @media (max-width: 480px) {
    gap: 16px;
  }
`

const SideColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
  
  @media (max-width: 768px) {
    gap: 20px;
  }
  
  @media (max-width: 480px) {
    gap: 16px;
  }
`

const SectionCard = styled.div`
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  animation: ${slideUp} 0.4s ease-out;
  
  @media (max-width: 768px) {
    padding: 20px;
  }
  
  @media (max-width: 480px) {
    padding: 16px;
    border-radius: 10px;
  }
`

const DescriptionCard = styled(SectionCard)`
  margin: 0 20px 24px 20px;
  
  @media (max-width: 768px) {
    margin: 0 16px 20px 16px;
  }
  
  @media (max-width: 480px) {
    margin: 0 12px 16px 12px;
  }
`

const SectionTitle = styled.h2`
  font-size: 1.3em;
  font-weight: 500;
  color: var(--text);
  margin: 0 0 16px 0;
  
  @media (max-width: 480px) {
    font-size: 1.1em;
    margin-bottom: 12px;
  }
`

const SectionText = styled.div`
  color: var(--text-light);
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
`

const SkillsGrid = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`

const SkillBadge = styled.span`
  padding: 8px 16px;
  background: rgba(10, 102, 194, 0.1);
  color: var(--primary);
  border-radius: 20px;
  font-size: 0.9em;
  font-weight: 500;
  display: inline-block;
`

const CertificatesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`

const CertificateCard = styled.div`
  padding: 16px;
  background: var(--bg-light);
  border-radius: 8px;
  border-left: 3px solid var(--primary);
  
  @media (max-width: 480px) {
    padding: 12px;
  }
`

const CertificateTitle = styled.h3`
  font-size: 1em;
  font-weight: 500;
  color: var(--text);
  margin: 0;
`

const InfoItem = styled.div`
  margin-bottom: 12px;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  strong {
    color: var(--text);
    display: block;
    margin-bottom: 4px;
  }
  
  span {
    color: var(--text-light);
  }
`

const PostsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`

const PostCard = styled.div`
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: var(--primary);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  @media (max-width: 480px) {
    padding: 16px;
    border-radius: 10px;
  }
`

const PostHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
`

const PostAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
  font-size: 1em;
  flex-shrink: 0;
`

const PostInfo = styled.div`
  flex: 1;
  min-width: 0;
`

const PostAuthorName = styled.div`
  font-weight: 500;
  color: var(--text);
  font-size: 0.95em;
  margin-bottom: 2px;
`

const PostTime = styled.div`
  font-size: 0.85em;
  color: var(--text-lighter);
`

const PostContent = styled.div`
  color: var(--text-light);
  line-height: 1.6;
  margin-bottom: 12px;
  word-wrap: break-word;
  white-space: pre-wrap;
`

const PostMedia = styled.div`
  margin: 12px 0;
  border-radius: 8px;
  overflow: hidden;
  
  img, video {
    max-width: 100%;
    max-height: 400px;
    object-fit: contain;
    border-radius: 8px;
  }
`

const PostActions = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
`

const PostAction = styled.button`
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: var(--text-lighter);
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 6px 12px;
  border-radius: 6px;
  
  &:hover {
    background: var(--hover-bg);
    color: var(--primary);
  }
  
  &.liked {
    color: var(--primary);
  }
  
  svg {
    width: 18px;
    height: 18px;
  }
`

const PostCount = styled.span`
  font-size: 0.9em;
  font-weight: 500;
`

const EmptyPosts = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: var(--text-lighter);
`

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 100px 20px;
  
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

const ErrorContainer = styled.div`
  text-align: center;
  padding: 100px 20px;
  color: var(--text-light);
  
  h2 {
    color: var(--text);
    margin-bottom: 12px;
  }
`

function Profile() {
  const params = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const { user: currentUser } = useAuth()
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [connectionStatus, setConnectionStatus] = useState(null)
  const [posts, setPosts] = useState([])
  const [loadingPosts, setLoadingPosts] = useState(false)

  // Parse URL to get user ID (supports both old and new formats)
  const getUserIdFromUrl = () => {
    // Try new format first: username-hashedId
    if (params.username && params.hashedId) {
      const parsed = parseProfileUrl(`profile/${params.username}-${params.hashedId}`)
      if (parsed.userId) {
        return parsed.userId
      }
    }
    
    // Fallback to old format: just userId
    if (params.userId) {
      const userIdNum = parseInt(params.userId)
      if (!isNaN(userIdNum)) {
        return userIdNum
      }
    }
    
    // Try parsing from location pathname
    const parsed = parseProfileUrl(location.pathname)
    return parsed.userId
  }

  const userId = getUserIdFromUrl()

  useEffect(() => {
    if (userId) {
      loadProfile()
      checkConnectionStatus()
      loadUserPosts()
    } else {
      setError('Invalid profile URL')
      setLoading(false)
    }
  }, [userId, location.pathname])

  const loadProfile = async () => {
    if (!userId) {
      setError('Invalid user ID')
      setLoading(false)
      return
    }
    
    try {
      setLoading(true)
      setError(null)
      
      const response = await userAPI.getUserProfile(userId)
      setProfile(response.data)
      
      // If we loaded with old format URL, update to new format for better SEO and UX
      // Only update if we're using the old format (userId param exists but hashedId doesn't)
      if (response.data && response.data.username && params.userId && !params.hashedId) {
        const newUrl = generateProfileUrl(userId, response.data.username)
        if (newUrl !== location.pathname) {
          // Use replace to avoid adding to history stack
          navigate(newUrl, { replace: true })
        }
      }
    } catch (err) {
      console.error('Error loading profile:', err)
      setError(err.response?.data?.detail || 'Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const checkConnectionStatus = async () => {
    if (!currentUser || !userId || userId === currentUser.id) {
      return
    }
    
    try {
      const connections = await connectionAPI.getConnections()
      const isConnected = connections.data?.some(
        conn => conn.user_id === userId || conn.connected_user_id === userId
      )
      
      if (isConnected) {
        setConnectionStatus('connected')
        return
      }
      
      const pending = await connectionAPI.getPendingRequests()
      const sent = await connectionAPI.getSentRequests()
      
      const hasPending = [...(pending.data || []), ...(sent.data || [])].some(
        req => req.sender_id === userId || req.receiver_id === userId
      )
      
      setConnectionStatus(hasPending ? 'pending' : 'none')
    } catch (err) {
      console.error('Error checking connection status:', err)
      setConnectionStatus('none')
    }
  }

  const handleConnect = async () => {
    try {
      await connectionAPI.sendRequest(userId)
      setConnectionStatus('pending')
    } catch (err) {
      console.error('Error sending connection request:', err)
      alert(err.response?.data?.detail || 'Failed to send connection request')
    }
  }

  const parseSkills = (skillsString) => {
    if (!skillsString) return []
    try {
      const parsed = JSON.parse(skillsString)
      return Array.isArray(parsed) ? parsed : []
    } catch {
      return skillsString.split(/[,\n]/).map(s => s.trim()).filter(s => s)
    }
  }

  const parseCertificates = (certificatesString) => {
    if (!certificatesString) return []
    try {
      const parsed = JSON.parse(certificatesString)
      return Array.isArray(parsed) ? parsed : [certificatesString]
    } catch {
      return certificatesString.split('\n').map(c => c.trim()).filter(c => c)
    }
  }

  const loadUserPosts = async () => {
    if (!userId) {
      return
    }
    
    try {
      setLoadingPosts(true)
      const response = await postAPI.getUserPosts(userId, 20, 0)
      setPosts(response.data.posts || [])
    } catch (err) {
      console.error('Error loading user posts:', err)
      setPosts([])
    } finally {
      setLoadingPosts(false)
    }
  }

  const handleLike = async (postId) => {
    try {
      const response = await postAPI.toggleLike(postId)
      setPosts(prevPosts => 
        prevPosts.map(post => 
          post.id === postId || post.post_id === postId
            ? { ...post, is_liked: response.data.is_liked, like_count: response.data.like_count }
            : post
        )
      )
    } catch (err) {
      console.error('Error toggling like:', err)
    }
  }

  const getTimeAgo = (dateString) => {
    if (!dateString) return ''
    const now = new Date()
    const date = new Date(dateString)
    const diffInSeconds = Math.floor((now - date) / 1000)
    
    if (diffInSeconds < 60) return 'just now'
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
    return `${Math.floor(diffInSeconds / 86400)}d ago`
  }

  const escapeHtml = (text) => {
    if (!text) return ''
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
  }

  if (loading) {
    return (
      <Container>
        <Navbar>
          <NavContainer>
            <NavLeft>
              <Logo onClick={() => navigate('/feed')}>ZedReq</Logo>
            </NavLeft>
            <NavRight>
              <BackButton onClick={() => navigate(-1)}>
                ← Back
              </BackButton>
            </NavRight>
          </NavContainer>
        </Navbar>
        <LoadingSpinner />
      </Container>
    )
  }

  if (error || !profile) {
    return (
      <Container>
        <Navbar>
          <NavContainer>
            <NavLeft>
              <Logo onClick={() => navigate('/feed')}>ZedReq</Logo>
            </NavLeft>
            <NavRight>
              <BackButton onClick={() => navigate(-1)}>
                ← Back
              </BackButton>
            </NavRight>
          </NavContainer>
        </Navbar>
        <ErrorContainer>
          <h2>Profile Not Found</h2>
          <p>{error || 'The user profile you are looking for does not exist.'}</p>
        </ErrorContainer>
      </Container>
    )
  }

  const isOwnProfile = currentUser && currentUser.id === userId
  const skills = parseSkills(profile.skills)
  const certificates = parseCertificates(profile.certificates)
  const initials = profile.name 
    ? profile.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) 
    : 'U'

  return (
    <Container>
      <Navbar>
        <NavContainer>
          <NavLeft>
            <Logo onClick={() => navigate('/feed')}>ZedReq</Logo>
          </NavLeft>
          <NavRight>
            <BackButton onClick={() => navigate(-1)}>
              ← Back
            </BackButton>
          </NavRight>
        </NavContainer>
      </Navbar>

      <ProfileWrapper>
        <CoverPhotoSection coverPic={profile.cover_pic} />
        
        <ProfileInfoCard>
          <ProfilePictureWrapper>
            {profile.profile_pic ? (
              <ProfilePicture src={profile.profile_pic} alt={profile.name} />
            ) : (
              <ProfilePicturePlaceholder>{initials}</ProfilePicturePlaceholder>
            )}
          </ProfilePictureWrapper>
          
          <ProfileHeaderContent>
            <ProfileName>{profile.name || 'No Name'}</ProfileName>
            {profile.short_desc && <ProfileHeadline>{profile.short_desc}</ProfileHeadline>}
            {profile.current_status && <ProfileLocation>{profile.current_status}</ProfileLocation>}
            
            {!isOwnProfile && (
              <ActionButtons>
                {connectionStatus === 'none' && (
                  <ActionButton primary onClick={handleConnect}>
                    Connect
                  </ActionButton>
                )}
                {connectionStatus === 'pending' && (
                  <ActionButton disabled>
                    Connection Request Sent
                  </ActionButton>
                )}
                {connectionStatus === 'connected' && (
                  <ActionButton>
                    ✓ Connected
                  </ActionButton>
                )}
                <ActionButton onClick={() => navigate(`/messages`)}>
                  Message
                </ActionButton>
              </ActionButtons>
            )}
          </ProfileHeaderContent>
        </ProfileInfoCard>

        <DescriptionCard>
          <SectionTitle>Description</SectionTitle>
          {profile.about && profile.about.trim() && (
            <SectionText>{profile.about}</SectionText>
          )}
        </DescriptionCard>

        <ContentLayout>
          <MainColumn>
            {skills.length > 0 && (
              <SectionCard>
                <SectionTitle>Skills</SectionTitle>
                <SkillsGrid>
                  {skills.map((skill, index) => (
                    <SkillBadge key={index}>{skill}</SkillBadge>
                  ))}
                </SkillsGrid>
              </SectionCard>
            )}

            {certificates.length > 0 && (
              <SectionCard>
                <SectionTitle>Licenses & Certifications</SectionTitle>
                <CertificatesList>
                  {certificates.map((cert, index) => (
                    <CertificateCard key={index}>
                      <CertificateTitle>{cert}</CertificateTitle>
                    </CertificateCard>
                  ))}
                </CertificatesList>
              </SectionCard>
            )}

            <SectionCard>
              <SectionTitle>Posts</SectionTitle>
              {loadingPosts ? (
                <EmptyPosts>Loading posts...</EmptyPosts>
              ) : posts.length > 0 ? (
                <PostsList>
                  {posts.map(post => (
                    <PostCard key={post.id || post.post_id}>
                      <PostHeader>
                        <PostAvatar>
                          {post.full_name ? post.full_name.charAt(0).toUpperCase() : 'U'}
                        </PostAvatar>
                        <PostInfo>
                          <PostAuthorName>{post.full_name || post.name || post.username}</PostAuthorName>
                          <PostTime>{getTimeAgo(post.created_at)}</PostTime>
                        </PostInfo>
                      </PostHeader>
                      <PostContent dangerouslySetInnerHTML={{ __html: escapeHtml(post.content || post.post_desc) }} />
                      {post.media_url && (
                        <PostMedia>
                          {post.media_type === 'video' ? (
                            <video src={post.media_url} controls preload="metadata" />
                          ) : (
                            <img src={post.media_url} alt="Post media" loading="lazy" />
                          )}
                        </PostMedia>
                      )}
                      <PostActions>
                        <PostAction 
                          className={post.is_liked ? 'liked' : ''}
                          onClick={() => handleLike(post.id || post.post_id)}
                        >
                          <svg viewBox="0 0 24 24" fill={post.is_liked ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                          </svg>
                          <PostCount>{post.like_count || post.likes || 0}</PostCount>
                        </PostAction>
                      </PostActions>
                    </PostCard>
                  ))}
                </PostsList>
              ) : (
                <EmptyPosts>No posts yet</EmptyPosts>
              )}
            </SectionCard>
          </MainColumn>

          <SideColumn>
            <SectionCard>
              <SectionTitle>Profile Information</SectionTitle>
              <InfoItem>
                <strong>Member since</strong>
                <span>{profile.created_at ? new Date(profile.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long' }) : 'N/A'}</span>
              </InfoItem>
              {profile.email && (
                <InfoItem>
                  <strong>Email</strong>
                  <span>{profile.email}</span>
                </InfoItem>
              )}
            </SectionCard>
          </SideColumn>
        </ContentLayout>
      </ProfileWrapper>
    </Container>
  )
}

export default Profile
