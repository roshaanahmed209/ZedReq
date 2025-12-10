import React, { useState, useEffect } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import '../css/pages/Feed.css'

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
  position: relative;
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
  gap: 30px;
`

const NavMenu = styled.div`
  display: flex;
  align-items: center;
  gap: 30px;
  
  @media (max-width: 768px) {
    display: none;
  }
`

const NavMenuItem = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  color: var(--text-light);
  font-size: 0.85em;
  transition: color 0.2s ease;
  padding: 8px 12px;
  border-radius: 8px;
  min-width: 80px;
  text-align: center;
  
  svg {
    width: 22px;
    height: 22px;
  }
  
  span {
    white-space: nowrap;
  }
  
  &:hover {
    color: var(--primary);
    background: rgba(10, 102, 194, 0.1);
  }
  
  &.active {
    color: var(--primary);
  }
`

const SearchInput = styled.input`
  padding: 10px 16px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text);
  font-size: 0.9em;
  transition: all 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: var(--primary);
    background: rgba(255, 255, 255, 0.08);
  }
  
  &::placeholder {
    color: var(--text-lighter);
  }
`

const SearchResults = styled.div`
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 280px;
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 12px;
  margin-top: 8px;
  z-index: 1000;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  display: none;
  max-height: 400px;
  overflow-y: auto;
`

const SearchResultItem = styled.div`
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  
  &:hover {
    background: var(--hover-bg);
  }
  
  &:first-child {
    border-radius: 8px 8px 0 0;
  }
  
  &:last-child {
    border-radius: 0 0 8px 8px;
  }
`

const SearchAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
`

const LogoutButton = styled.button`
  padding: 8px 16px;
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: var(--hover-bg);
    border-color: var(--primary);
  }
`

const MainContainer = styled.div`
  max-width: 1600px;
  margin: 0 auto 0 0;
  display: grid;
  grid-template-columns: 280px 280px 1fr;
  gap: 25px;
  padding: 30px 20px;
  
  @media (max-width: 1024px) {
    grid-template-columns: 280px 1fr;
  }
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 20px;
  }
`

const Sidebar = styled.aside`
  position: sticky;
  top: 100px;
  height: fit-content;
`

const ProfileCard = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  padding: 30px;
  border: 1px solid var(--border);
  text-align: center;
`

const ProfileAvatar = styled.div`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2em;
  font-weight: 500;
  margin: 0 auto 20px;
`

const ProfileName = styled.h3`
  font-size: 1.3em;
  margin-bottom: 10px;
  color: var(--text);
`

const ProfileHeadline = styled.p`
  color: var(--text-light);
  margin-bottom: 15px;
  font-size: 0.9em;
`

const ProfileBio = styled.p`
  color: var(--text-lighter);
  font-size: 0.85em;
  line-height: 1.5;
`

const LeftSidebar = styled.aside`
  position: sticky;
  top: 100px;
  height: fit-content;
  
  @media (max-width: 1024px) {
    display: none;
  }
`

const SidePanel = styled.div`
  background: var(--bg-white);
  border-radius: 16px;
  border: 1px solid var(--border);
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  transition: box-shadow 0.3s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
`

const PanelSection = styled.div`
  padding: 14px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.2s ease;
  
  &:last-child {
    border-bottom: none;
  }
  
  &:hover {
    background: var(--hover-bg);
    cursor: pointer;
    padding-left: 24px;
  }
`

const PanelHeader = styled.div`
  padding: 24px 20px;
  background: linear-gradient(135deg, #0a66c2 0%, #004182 100%);
  color: white;
  font-weight: 600;
  font-size: 1em;
  letter-spacing: 0.3px;
  text-transform: uppercase;
  border-bottom: 3px solid var(--primary-dark);
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -3px;
    left: 0;
    width: 60px;
    height: 3px;
    background: var(--secondary);
  }
`

const PanelItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--text);
  
  .label {
    font-size: 0.875em;
    color: var(--text-light);
    font-weight: 400;
    letter-spacing: 0.2px;
  }
  
  .value {
    font-weight: 700;
    font-size: 1.1em;
    color: var(--primary);
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
`

const PanelLink = styled.div`
  display: flex;
  align-items: center;
  gap: 14px;
  color: var(--text);
  font-size: 0.9em;
  font-weight: 500;
  transition: all 0.2s ease;
  
  .icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: rgba(10, 102, 194, 0.1);
    border-radius: 8px;
    transition: all 0.2s ease;
    
    svg {
      color: var(--text-light);
      transition: all 0.2s ease;
    }
  }
  
  &:hover {
    color: var(--primary);
    transform: translateX(2px);
    
    .icon {
      background: var(--primary);
      transform: scale(1.05);
      
      svg {
        color: white;
      }
    }
  }
`

const PanelDivider = styled.div`
  height: 1px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    var(--border) 20%, 
    var(--border) 80%, 
    transparent 100%
  );
  margin: 8px 0;
`

const FeedContainer = styled.main``

const PostCreator = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  border: 1px solid var(--border);
`

const PostCreatorHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
`

const PostCreatorAvatar = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
  font-size: 1.2em;
`

const PostCreatorInfo = styled.div`
  flex: 1;
`

const PostCreatorTitle = styled.h3`
  font-size: 1em;
  color: var(--text);
  margin-bottom: 4px;
  font-weight: 600;
`

const PostCreatorSubtitle = styled.p`
  font-size: 0.85em;
  color: var(--text-light);
`

const PostInputContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 15px;
`

const PostTextarea = styled.textarea`
  width: 100%;
  padding: 15px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg-light);
  color: var(--text);
  font-size: 1em;
  resize: vertical;
  min-height: 80px;
  
  &:focus {
    outline: none;
    border-color: var(--primary);
  }
  
  &::placeholder {
    color: var(--text-lighter);
  }
`

const PostButton = styled.button`
  align-self: flex-end;
  padding: 12px 24px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 8px;
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
`

const PostsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`

const Post = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border);
  animation: ${slideUp} 0.3s ease-out;
`

const PostHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
`

const PostAvatar = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
  font-size: 1.2em;
`

const PostInfo = styled.div`
  flex: 1;
`

const PostName = styled.h4`
  font-size: 1em;
  margin-bottom: 2px;
  color: var(--text);
`

const PostUsername = styled.div`
  font-size: 0.85em;
  color: var(--text-lighter);
  margin-bottom: 2px;
`

const PostTime = styled.div`
  font-size: 0.8em;
  color: var(--text-lighter);
`

const PostContent = styled.div`
  margin-bottom: 15px;
  line-height: 1.6;
  color: var(--text);
`

const PostActions = styled.div`
  display: flex;
  gap: 20px;
`

const PostAction = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  color: var(--text-lighter);
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 8px 12px;
  border-radius: 6px;
  
  svg {
    transition: all 0.3s ease;
  }
  
  &:hover {
    background: var(--hover-bg);
    color: var(--text);
  }
  
  &.liked {
    color: #e74c3c;
    
    svg {
      color: #e74c3c;
    }
  }
`

const LikeCount = styled.span`
  font-size: 0.9em;
`

const Loading = styled.div`
  text-align: center;
  padding: 40px;
  color: var(--text-light);
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

const MessagesPanelHeader = styled.div`
  padding: 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-white);
  flex-shrink: 0;
`

const MessagesPanelTitle = styled.h3`
  font-size: 1.2em;
  color: var(--text);
  font-weight: 300;
`

const CloseButton = styled.button`
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--text-light);
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;

  &:hover {
    background: var(--hover-bg);
    color: var(--text);
    transform: rotate(90deg);
  }

  svg {
    width: 20px;
    height: 20px;
  }
`

const ContactsList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  animation: ${fadeIn} 0.3s ease-in;

  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 10px;
  }
`

const ContactItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 4px;
  opacity: 1;
  transform: translateX(0);

  &:hover {
    background: var(--hover-bg);
    transform: translateX(4px);
  }
`

const ContactAvatar = styled.div`
  width: 44px;
  height: 44px;
  min-width: 44px;
  border-radius: 50%;
  background: ${props => props.isBot ? 'linear-gradient(135deg, var(--primary), var(--secondary))' : 'var(--primary)'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
  font-size: 0.9em;
  transition: all 0.3s ease;

  svg {
    width: 24px;
    height: 24px;
    transition: transform 0.3s ease;
  }

  &:hover svg {
    transform: rotate(15deg) scale(1.1);
  }
`

const ContactInfo = styled.div`
  flex: 1;
  min-width: 0;
`

const ContactName = styled.div`
  font-size: 0.95em;
  color: var(--text);
  font-weight: 400;
  margin-bottom: 2px;
`

const ContactStatus = styled.div`
  font-size: 0.8em;
  color: var(--text-lighter);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`

const ChatView = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: ${fadeIn} 0.3s ease-in;
`

const ChatHeader = styled.div`
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--hover-bg);
  flex-shrink: 0;
`

const ChatHeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
`

const ChatHeaderName = styled.div`
  font-size: 1em;
  color: var(--text);
  font-weight: 400;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`

const ChatMessages = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;

  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 10px;
  }
`

const ChatMessage = styled.div`
  display: flex;
  gap: 8px;
  align-items: flex-start;
  animation: ${fadeIn} 0.4s ease-in, ${slideUp} 0.4s ease-out;
  opacity: 1;
  transform: translateY(0);

  ${props => props.isUser && `
    flex-direction: row-reverse;
  `}
`

const MessageBubble = styled.div`
  background: ${props => props.isUser ? 'var(--primary)' : 'var(--hover-bg)'};
  color: ${props => props.isUser ? 'white' : 'var(--text)'};
  padding: 10px 14px;
  border-radius: ${props => props.isUser ? '12px 12px 4px 12px' : '12px 12px 12px 4px'};
  max-width: 75%;
  font-size: 0.9em;
  line-height: 1.4;
  word-wrap: break-word;
  transition: all 0.3s ease;
  opacity: 1;

  &:hover {
    opacity: 0.95;
    transform: scale(1.02);
  }
`

const ChatInputContainer = styled.div`
  padding: 16px;
  border-top: 1px solid var(--border);
  display: flex;
  gap: 10px;
  background: var(--bg-white);
  flex-shrink: 0;
`

const ChatInput = styled.input`
  flex: 1;
  padding: 10px 14px;
  background: var(--hover-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  font-size: 0.9em;
  font-family: inherit;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: var(--primary);
    background: var(--bg-white);
    box-shadow: 0 0 0 3px rgba(10, 102, 194, 0.1);
    transform: scale(1.01);
  }

  &::placeholder {
    color: var(--text-lighter);
  }
`

const SendButton = styled.button`
  padding: 10px 14px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 1;

  &:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 4px 12px rgba(10, 102, 194, 0.3);
    opacity: 0.9;
  }

  &:active {
    transform: translateY(0) scale(0.98);
  }

  svg {
    width: 18px;
    height: 18px;
  }
`

const BackIconButton = styled.button`
  width: 32px;
  height: 32px;
  min-width: 32px;
  border: none;
  background: var(--primary);
  color: white;
  cursor: pointer;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 1;

  &:hover {
    transform: scale(1.15);
    box-shadow: 0 4px 12px rgba(10, 102, 194, 0.4);
    opacity: 0.9;
  }

  &:active {
    transform: scale(0.95);
  }

  svg {
    width: 16px;
    height: 16px;
  }
`

const Feed = () => {
  const [user, setUser] = useState(null)
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [postContent, setPostContent] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searchTimeout, setSearchTimeout] = useState(null)
  const [messagesOpen, setMessagesOpen] = useState(false)
  const [selectedContact, setSelectedContact] = useState(null)
  const [chatMessages, setChatMessages] = useState({})
  const [messageInput, setMessageInput] = useState('')
  const { logout } = useAuth()
  const navigate = useNavigate()

  const contacts = [
    {
      id: 0,
      name: 'AI Assistant',
      status: 'Always available',
      isBot: true,
      avatar: 'AI'
    },
    {
      id: 1,
      name: 'Sarah Johnson',
      status: 'Active now',
      isBot: false,
      avatar: 'SJ'
    },
    {
      id: 2,
      name: 'Mike Chen',
      status: 'Active 2h ago',
      isBot: false,
      avatar: 'MC'
    },
    {
      id: 3,
      name: 'Emma Davis',
      status: 'Active now',
      isBot: false,
      avatar: 'ED'
    },
    {
      id: 4,
      name: 'Alex Rodriguez',
      status: 'Active 1d ago',
      isBot: false,
      avatar: 'AR'
    },
    {
      id: 5,
      name: 'Lisa Wang',
      status: 'Active now',
      isBot: false,
      avatar: 'LW'
    }
  ]

  useEffect(() => {
    loadUser()
    loadPosts()
  }, [])

  const loadUser = async () => {
    try {
      const response = await api.get('/api/user')
      if (response.data && !response.data.error) {
        setUser(response.data)
      }
    } catch (error) {
      console.error('Error loading user:', error)
    }
  }

  const loadPosts = async () => {
    try {
      const response = await api.get('/api/posts')
      if (response.data) {
        setPosts(response.data)
      }
    } catch (error) {
      console.error('Error loading posts:', error)
    } finally {
      setLoading(false)
    }
  }

  const createPost = async () => {
    if (!postContent.trim()) {
      alert('Please enter some content')
      return
    }
    
    try {
      const response = await api.post('/api/posts', { content: postContent })
      if (response.data.success) {
        setPostContent('')
        loadPosts()
      }
    } catch (error) {
      console.error('Error creating post:', error)
      alert('Failed to create post')
    }
  }

  const handleLike = async (postId) => {
    try {
      const response = await api.post(`/api/posts/${postId}/like`)
      if (response.data) {
        // Update the specific post's like count
        setPosts(posts.map(post => 
          post.id === postId 
            ? { 
                ...post, 
                like_count: response.data.like_count,
                is_liked: !post.is_liked 
              }
            : post
        ))
      }
    } catch (error) {
      console.error('Error toggling like:', error)
    }
  }

  const searchUsers = async (query) => {
    if (!query.trim()) {
      setSearchResults([])
      return
    }
    
    try {
      const response = await api.get(`/api/users/search?q=${encodeURIComponent(query)}`)
      setSearchResults(response.data)
    } catch (error) {
      console.error('Error searching users:', error)
    }
  }

  const handleSearchChange = (e) => {
    const query = e.target.value
    setSearchQuery(query)
    
    if (searchTimeout) {
      clearTimeout(searchTimeout)
    }
    
    const timeout = setTimeout(() => {
      searchUsers(query)
    }, 300)
    
    setSearchTimeout(timeout)
  }

  const handleLogout = async () => {
    try {
      await logout()
      navigate('/landing')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  const getTimeAgo = (dateString) => {
    const now = new Date()
    const date = new Date(dateString)
    const diffInSeconds = Math.floor((now - date) / 1000)
    
    if (diffInSeconds < 60) return 'just now'
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
    return `${Math.floor(diffInSeconds / 86400)}d ago`
  }

  const escapeHtml = (text) => {
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
  }

  const handleMessagesClick = () => {
    setMessagesOpen(!messagesOpen)
    setSelectedContact(null)
  }

  const handleContactSelect = (contact) => {
    setSelectedContact(contact)
    // Initialize chat if it doesn't exist
    if (!chatMessages[contact.id]) {
      setChatMessages(prev => ({
        ...prev,
        [contact.id]: contact.isBot ? [
          {
            id: 1,
            text: "Hello! I'm your AI assistant. How can I help you today?",
            isUser: false,
            timestamp: new Date()
          }
        ] : []
      }))
    }
  }

  const handleSendMessage = () => {
    if (!messageInput.trim() || !selectedContact) return

    const newMessage = {
      id: Date.now(),
      text: messageInput,
      isUser: true,
      timestamp: new Date()
    }

    setChatMessages(prev => ({
      ...prev,
      [selectedContact.id]: [...(prev[selectedContact.id] || []), newMessage]
    }))

    setMessageInput('')

    // Simulate AI response for bot
    if (selectedContact.isBot) {
      setTimeout(() => {
        const aiResponse = {
          id: Date.now() + 1,
          text: "I understand. Let me help you with that. This is a prototype, so I'll provide a generic response. In a real implementation, I would analyze your message and provide relevant assistance.",
          isUser: false,
          timestamp: new Date()
        }
        setChatMessages(prev => ({
          ...prev,
          [selectedContact.id]: [...(prev[selectedContact.id] || []), aiResponse]
        }))
      }, 1000)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage()
    }
  }

  const handleBackToContacts = () => {
    setSelectedContact(null)
  }

  return (
    <Container>
      <Navbar>
        <NavContainer>
          <NavLeft>
            <Logo>ZedReq</Logo>
            <SearchInput 
              type="text" 
              placeholder="Search..." 
              value={searchQuery}
              onChange={handleSearchChange}
              className="search-input-wide"
            />
            {searchResults.length > 0 && (
              <SearchResults className="search-results-positioned">
                {searchResults.map(user => (
                  <SearchResultItem key={user.id}>
                    <SearchAvatar>
                      {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
                    </SearchAvatar>
                    <div>
                      <div><strong>{user.full_name || user.username}</strong></div>
                      <div className="search-username">@{user.username}</div>
                    </div>
                  </SearchResultItem>
                ))}
              </SearchResults>
            )}
          </NavLeft>
          
          <NavRight>
            <NavMenu>
              <NavMenuItem className="active">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                  <polyline points="9 22 9 12 15 12 15 22"></polyline>
                </svg>
                <span>Home</span>
              </NavMenuItem>
              
              <NavMenuItem onClick={() => navigate('/network')}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="9" cy="7" r="4"></circle>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
                <span>Network</span>
              </NavMenuItem>
              
              <NavMenuItem onClick={() => navigate('/jobs')}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                  <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                </svg>
                <span>Jobs</span>
              </NavMenuItem>
              
              <NavMenuItem onClick={handleMessagesClick}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <span>Messages</span>
              </NavMenuItem>
              
              <NavMenuItem>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                  <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                </svg>
                <span>Notifications</span>
              </NavMenuItem>
            </NavMenu>
            
            <LogoutButton onClick={handleLogout}>Logout</LogoutButton>
          </NavRight>
        </NavContainer>
      </Navbar>

      <MainContainer>
        <LeftSidebar>
          <SidePanel>
            <PanelSection>
              <PanelItem>
                <span className="label">Profile views</span>
                <span className="value">142</span>
              </PanelItem>
            </PanelSection>
            
            <PanelSection>
              <PanelItem>
                <span className="label">Post impressions</span>
                <span className="value">1,234</span>
              </PanelItem>
            </PanelSection>
            
            <PanelDivider />
            
            <PanelSection onClick={() => navigate('/lms')}>
              <PanelLink>
                <span className="icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                    <path d="M12 6h4"></path>
                    <path d="M12 10h4"></path>
                    <path d="M12 14h4"></path>
                  </svg>
                </span>
                <span>LMS</span>
              </PanelLink>
            </PanelSection>
            
            <PanelSection onClick={() => navigate('/evaluation')}>
              <PanelLink>
                <span className="icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M9 11l3 3L22 4"></path>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                  </svg>
                </span>
                <span>Evaluation</span>
              </PanelLink>
            </PanelSection>

              <PanelSection onClick={() => navigate('/ai-mode')}>
                <PanelLink>
                  <span className="icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 3v3"></path>
                      <path d="M12 18v3"></path>
                      <path d="M5.5 5.5l2.1 2.1"></path>
                      <path d="M16.4 16.4l2.1 2.1"></path>
                      <path d="M3 12h3"></path>
                      <path d="M18 12h3"></path>
                      <path d="M5.5 18.5l2.1-2.1"></path>
                      <path d="M16.4 7.6l2.1-2.1"></path>
                      <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                  </span>
                  <span>AI Mode</span>
                </PanelLink>
              </PanelSection>
            
            <PanelSection onClick={() => navigate('/ai-interviews')}>
              <PanelLink>
                <span className="icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                    <line x1="12" y1="19" x2="12" y2="23"></line>
                    <line x1="8" y1="23" x2="16" y2="23"></line>
                  </svg>
                </span>
                <span>AI Mock Interviews</span>
              </PanelLink>
            </PanelSection>
            
            
            <PanelSection>
              <PanelLink onClick={() => navigate('/jobs')}>
                <span className="icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                  </svg>
                </span>
                <span>Jobs</span>
              </PanelLink>
            </PanelSection>
            
            <PanelDivider />
            
            <PanelSection>
              <PanelLink>
                <span className="icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="4" y1="9" x2="20" y2="9"></line>
                    <line x1="4" y1="15" x2="20" y2="15"></line>
                    <line x1="10" y1="3" x2="8" y2="21"></line>
                    <line x1="16" y1="3" x2="14" y2="21"></line>
                  </svg>
                </span>
                <span>Followed Hashtags</span>
              </PanelLink>
            </PanelSection>
            
            <PanelSection>
              <PanelLink>
                <span className="icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="3"></circle>
                    <path d="M12 1v6m0 6v6m5.656-14.657l-4.242 4.243m0 4.242l-4.243 4.243m12.728 0l-4.243-4.243m0-4.242l-4.242-4.243"></path>
                  </svg>
                </span>
                <span>Settings</span>
              </PanelLink>
            </PanelSection>
          </SidePanel>
        </LeftSidebar>

        <Sidebar>
          <ProfileCard>
            <ProfileAvatar>
              {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
            </ProfileAvatar>
            <ProfileName>{user?.full_name || user?.username || 'Loading...'}</ProfileName>
            <ProfileHeadline>{user?.headline || 'No headline yet'}</ProfileHeadline>
            <ProfileBio>{user?.bio || 'No bio yet'}</ProfileBio>
          </ProfileCard>
        </Sidebar>

        <FeedContainer>
          <PostCreator>
            <PostCreatorHeader>
              <PostCreatorAvatar>
                {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
              </PostCreatorAvatar>
              <PostCreatorInfo>
                <PostCreatorTitle>Create a Post</PostCreatorTitle>
                <PostCreatorSubtitle>Share your thoughts, ideas, or updates with your network</PostCreatorSubtitle>
              </PostCreatorInfo>
            </PostCreatorHeader>
            <PostInputContainer>
              <PostTextarea 
                value={postContent}
                onChange={(e) => setPostContent(e.target.value)}
                placeholder="What's on your mind? Share something with your network..."
                rows="3"
              />
              <PostButton onClick={createPost}>Post</PostButton>
            </PostInputContainer>
          </PostCreator>

          <PostsContainer>
            {loading ? (
              <Loading>Loading posts...</Loading>
            ) : posts.length === 0 ? (
              <Loading>No posts yet. Be the first to share!</Loading>
            ) : (
              posts.map(post => (
                <Post key={post.id}>
                  <PostHeader>
                    <PostAvatar>
                      {post.full_name ? post.full_name.charAt(0).toUpperCase() : 'U'}
                    </PostAvatar>
                    <PostInfo>
                      <PostName>{post.full_name || post.username}</PostName>
                      <PostUsername>@{post.username}</PostUsername>
                      <PostTime>{getTimeAgo(post.created_at)}</PostTime>
                    </PostInfo>
                  </PostHeader>
                  <PostContent dangerouslySetInnerHTML={{ __html: escapeHtml(post.content) }} />
                  <PostActions>
                    <PostAction 
                      className={post.is_liked ? 'liked' : ''}
                      onClick={() => handleLike(post.id)}
                    >
                      <svg width="18" height="18" viewBox="0 0 24 24" fill={post.is_liked ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                      </svg>
                      <LikeCount>{post.like_count}</LikeCount>
                    </PostAction>
                  </PostActions>
                </Post>
              ))
            )}
          </PostsContainer>
        </FeedContainer>

        <MessagesPanel isOpen={messagesOpen}>
            <MessagesPanelHeader>
              <MessagesPanelTitle>Messages</MessagesPanelTitle>
              <CloseButton onClick={() => setMessagesOpen(false)}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </CloseButton>
            </MessagesPanelHeader>

            {!selectedContact ? (
              <ContactsList>
                {contacts.map(contact => (
                  <ContactItem key={contact.id} onClick={() => handleContactSelect(contact)}>
                    <ContactAvatar isBot={contact.isBot}>
                      {contact.isBot ? (
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M12 3v3"></path>
                          <path d="M12 18v3"></path>
                          <path d="M5.5 5.5l2.1 2.1"></path>
                          <path d="M16.4 16.4l2.1 2.1"></path>
                          <path d="M3 12h3"></path>
                          <path d="M18 12h3"></path>
                          <path d="M5.5 18.5l2.1-2.1"></path>
                          <path d="M16.4 7.6l2.1-2.1"></path>
                          <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                      ) : (
                        contact.avatar
                      )}
                    </ContactAvatar>
                    <ContactInfo>
                      <ContactName>{contact.name}</ContactName>
                      <ContactStatus>{contact.status}</ContactStatus>
                    </ContactInfo>
                  </ContactItem>
                ))}
              </ContactsList>
            ) : (
              <ChatView>
                <ChatHeader>
                  <ChatHeaderLeft>
                    <ContactAvatar isBot={selectedContact.isBot}>
                      {selectedContact.isBot ? (
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M12 3v3"></path>
                          <path d="M12 18v3"></path>
                          <path d="M5.5 5.5l2.1 2.1"></path>
                          <path d="M16.4 16.4l2.1 2.1"></path>
                          <path d="M3 12h3"></path>
                          <path d="M18 12h3"></path>
                          <path d="M5.5 18.5l2.1-2.1"></path>
                          <path d="M16.4 7.6l2.1-2.1"></path>
                          <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                      ) : (
                        selectedContact.avatar
                      )}
                    </ContactAvatar>
                    <ChatHeaderName>{selectedContact.name}</ChatHeaderName>
                  </ChatHeaderLeft>
                  <BackIconButton onClick={handleBackToContacts}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="19" y1="12" x2="5" y2="12"></line>
                      <polyline points="12 19 5 12 12 5"></polyline>
                    </svg>
                  </BackIconButton>
                </ChatHeader>

                <ChatMessages>
                  {(chatMessages[selectedContact.id] || []).map(msg => (
                    <ChatMessage key={msg.id} isUser={msg.isUser}>
                      <MessageBubble isUser={msg.isUser}>
                        {msg.text}
                      </MessageBubble>
                    </ChatMessage>
                  ))}
                </ChatMessages>

                <ChatInputContainer>
                  <ChatInput
                    type="text"
                    placeholder="Type a message..."
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                  />
                  <SendButton onClick={handleSendMessage}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="22" y1="2" x2="11" y2="13"></line>
                      <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                    </svg>
                  </SendButton>
                </ChatInputContainer>
              </ChatView>
            )}
        </MessagesPanel>
      </MainContainer>
    </Container>
  )
}

export default Feed
