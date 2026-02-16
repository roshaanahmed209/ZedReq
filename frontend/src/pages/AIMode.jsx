import React, { useState } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { nemzAPI } from '../services/api'
import Navbar from '../components/Navbar'
import '../css/pages/AIMode.css'

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`

const slideUp = keyframes`
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`

const fadeInScale = keyframes`
  from { 
    transform: scale(0.95); 
    opacity: 0; 
  }
  to { 
    transform: scale(1); 
    opacity: 1; 
  }
`

const slideInFromBottom = keyframes`
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
`

const Container = styled.div`
  min-height: 100vh;
  width: 100%;
  background: var(--bg-light);
  animation: ${fadeIn} 0.6s ease-in;
  overflow-x: hidden;
`


const BackButton = styled.button`
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

  @media (max-width: 600px) {
    padding: 8px;
  }

  @media (max-width: 480px) {
    padding: 8px;
  }
`

const MainContainer = styled.div`
  width: 100%;
  max-width: 100%;
  margin: 0;
  display: grid;
  grid-template-columns: 450px 1fr;
  gap: 25px;
  padding: 30px 20px;
  
  @media (max-width: 1200px) {
    grid-template-columns: 400px 1fr;
    gap: 20px;
  }
  
  @media (max-width: 1024px) {
    grid-template-columns: 350px 1fr;
    gap: 20px;
    padding: 25px 15px;
  }
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 20px;
    padding: 20px 15px;
  }

  @media (max-width: 480px) {
    padding: 15px 12px;
    gap: 15px;
  }
`

const SidePanel = styled.aside`
  position: sticky;
  top: 100px;
  height: fit-content;
  max-height: calc(100vh - 120px);
  background: var(--bg-white);
  border-radius: 16px;
  border: 1px solid var(--border);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  overflow: hidden;

  @media (max-width: 768px) {
    position: relative;
    top: 0;
    max-height: none;
  }
`

const PanelHeader = styled.div`
  padding: 28px 28px;
  background: var(--bg-white);
  color: var(--text);
  position: sticky;
  top: 0;
  z-index: 10;
  border-radius: 16px 16px 0 0;
  border-bottom: 1px solid var(--border);
`

const PageTitle = styled.h1`
  font-size: 1.5em;
  color: var(--text);
  margin-bottom: 8px;
  font-weight: 300;
`

const PageSubtitle = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
`

const PanelContent = styled.div`
  position: relative;
  padding: 24px 28px;
`

const PanelSection = styled.div`
  margin-bottom: 28px;

  &:last-child {
    margin-bottom: 0;
  }
`

const SectionTitle = styled.h3`
  font-size: 0.9em;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`

const UploadArea = styled.div`
  border: 2px dashed var(--border);
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    border-color: var(--primary);
    background: rgba(10, 102, 194, 0.03);
    transform: scale(1.02);
  }
`

const UploadIcon = styled.div`
  width: 48px;
  height: 48px;
  margin: 0 auto 12px;
  
  svg {
    width: 100%;
    height: 100%;
    color: var(--text-light);
  }
`

const UploadText = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
  margin-bottom: 8px;
`

const UploadButton = styled.button`
  padding: 10px 20px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  margin-top: 12px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(10, 102, 194, 0.4);
  }

  &:active {
    transform: translateY(0);
  }
`

const JobFilterButton = styled.button`
  width: 100%;
  padding: 12px 16px;
  background: ${props => props.active ? 'rgba(10, 102, 194, 0.1)' : 'transparent'};
  border: 1px solid ${props => props.active ? 'var(--primary)' : 'var(--border)'};
  border-radius: 8px;
  color: ${props => props.active ? 'var(--primary)' : 'var(--text-light)'};
  font-size: 0.9em;
  font-weight: 300;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: left;
  margin-bottom: 8px;
  
  &:hover {
    background: rgba(10, 102, 194, 0.1);
    border-color: var(--primary);
    color: var(--primary);
    transform: translateX(4px);
  }
`

const MainContent = styled.main`
  min-height: 80vh;
  width: 100%;
`

const ContentCard = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 32px;
  animation: ${fadeInScale} 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 24px;
  transition: all 0.3s ease;
`

const CardHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
`

const CardHeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`

const CardIcon = styled.div`
  width: 40px;
  height: 40px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  svg {
    width: 20px;
    height: 20px;
    color: var(--primary);
  }
`

const CardTitle = styled.h2`
  font-size: 1.3em;
  color: var(--text);
  font-weight: 400;
  letter-spacing: -0.3px;
`

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 400px;
`

const MessageBubble = styled.div`
  padding: 16px 20px;
  border-radius: 12px;
  max-width: 80%;
  background: ${props => props.isUser ? 'rgba(10, 102, 194, 0.1)' : 'var(--hover-bg)'};
  border: 1px solid ${props => props.isUser ? 'rgba(10, 102, 194, 0.3)' : 'var(--border)'};
  align-self: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  animation: ${slideUp} 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  transition: all 0.2s ease;
`

const MessageText = styled.p`
  font-size: 0.95em;
  color: var(--text);
  line-height: 1.6;
  font-weight: 300;
`

const MessageTime = styled.div`
  font-size: 0.75em;
  color: var(--text-lighter);
  margin-top: 8px;
`

const InputContainer = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 20px;
`

const ChatInput = styled.input`
  flex: 1;
  padding: 14px 18px;
  background: var(--hover-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  font-size: 0.95em;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:focus {
    outline: none;
    border-color: var(--primary);
    background: var(--bg-white);
    box-shadow: 0 0 0 3px rgba(10, 102, 194, 0.1);
    transform: translateY(-1px);
  }

  &::placeholder {
    color: var(--text-lighter);
  }
`

const SendButton = styled.button`
  padding: 14px 24px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.95em;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(10, 102, 194, 0.4);
  }

  &:active {
    transform: translateY(0);
  }

  svg {
    width: 18px;
    height: 18px;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  &:hover svg {
    transform: translateX(2px);
  }
`

const JobList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`

const JobCard = styled.div`
  padding: 20px;
  background: var(--hover-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  animation: ${slideInFromBottom} 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  animation-delay: ${props => props.delay || '0s'};
  animation-fill-mode: both;

  &:hover {
    border-color: rgba(10, 102, 194, 0.4);
    background: rgba(10, 102, 194, 0.03);
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  }
`

const JobTitle = styled.h3`
  font-size: 1.1em;
  color: var(--text);
  font-weight: 400;
  margin-bottom: 8px;
`

const JobCompany = styled.div`
  font-size: 0.9em;
  color: var(--text-light);
  margin-bottom: 12px;
`

const JobMeta = styled.div`
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 0.85em;
  color: var(--text-lighter);
`

const JobMetaItem = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;

  svg {
    width: 14px;
    height: 14px;
  }
`

const MatchScore = styled.div`
  display: inline-block;
  padding: 4px 12px;
  background: rgba(10, 102, 194, 0.1);
  border: 1px solid rgba(10, 102, 194, 0.3);
  border-radius: 12px;
  font-size: 0.8em;
  color: var(--primary);
  font-weight: 500;
  margin-top: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
`

const ProfileList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`

const ProfileCard = styled.div`
  padding: 20px;
  background: var(--hover-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  animation: ${slideInFromBottom} 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  animation-delay: ${props => props.delay || '0s'};
  animation-fill-mode: both;

  &:hover {
    border-color: rgba(10, 102, 194, 0.4);
    background: rgba(10, 102, 194, 0.03);
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  }
`

const ProfileName = styled.h3`
  font-size: 1.1em;
  color: var(--text);
  font-weight: 400;
  margin-bottom: 8px;
`

const ProfileAbout = styled.div`
  font-size: 0.9em;
  color: var(--text-light);
  margin-bottom: 12px;
  line-height: 1.5;
`

const ProfileSkills = styled.div`
  font-size: 0.85em;
  color: var(--text-lighter);
  margin-bottom: 12px;
`

const PostList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`

const PostCard = styled.div`
  padding: 20px;
  background: var(--hover-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  animation: ${slideInFromBottom} 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  animation-delay: ${props => props.delay || '0s'};
  animation-fill-mode: both;

  &:hover {
    border-color: rgba(10, 102, 194, 0.4);
    background: rgba(10, 102, 194, 0.03);
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  }
`

const PostContent = styled.div`
  font-size: 0.95em;
  color: var(--text);
  line-height: 1.6;
  margin-bottom: 12px;
`

const PostAuthor = styled.div`
  font-size: 0.85em;
  color: var(--text-light);
  margin-bottom: 8px;
`

const PostMeta = styled.div`
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 0.85em;
  color: var(--text-lighter);
`

const bounce = keyframes`
  0%, 80%, 100% { 
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% { 
    transform: scale(1);
    opacity: 1;
  }
`

const ThinkingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  border-radius: 12px;
  max-width: 80px;
  background: var(--hover-bg);
  border: 1px solid var(--border);
  align-self: flex-start;
  animation: ${slideUp} 0.4s cubic-bezier(0.4, 0, 0.2, 1);
`

const ThinkingDot = styled.div`
  width: 8px;
  height: 8px;
  background: var(--primary);
  border-radius: 50%;
  animation: ${bounce} 1.4s infinite ease-in-out;
  animation-delay: ${props => props.delay || '0s'};
`

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 20px;
  animation: ${fadeInScale} 0.4s cubic-bezier(0.4, 0, 0.2, 1);
`

const LoadingSpinner = styled.div`
  width: 50px;
  height: 50px;
  border: 4px solid var(--border);
  border-top: 4px solid var(--primary);
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
`

const LoadingText = styled.p`
  font-size: 0.95em;
  color: var(--text-light);
  font-weight: 300;
`

const FileInput = styled.input`
  display: none;
`

const UploadedFileDisplay = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(10, 102, 194, 0.05);
  border: 1px solid rgba(10, 102, 194, 0.3);
  border-radius: 8px;
  margin-top: 12px;
  animation: ${slideUp} 0.3s cubic-bezier(0.4, 0, 0.2, 1);
`

const FileInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
`

const FileIcon = styled.div`
  width: 32px;
  height: 32px;
  background: var(--primary);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  svg {
    width: 16px;
    height: 16px;
    color: white;
  }
`

const FileDetails = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`

const FileName = styled.div`
  font-size: 0.85em;
  color: var(--text);
  font-weight: 400;
`

const FileSize = styled.div`
  font-size: 0.75em;
  color: var(--text-lighter);
`

const RemoveFileButton = styled.button`
  padding: 6px;
  background: transparent;
  border: none;
  color: var(--text-lighter);
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: rgba(255, 0, 0, 0.1);
    color: #ff4444;
  }
  
  svg {
    width: 16px;
    height: 16px;
  }
`

const AIMode = () => {
  const [activeSection, setActiveSection] = useState('chat')
  const [message, setMessage] = useState('')
  const [jobFilter, setJobFilter] = useState('all')
  const [chatMessages, setChatMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your AI career assistant. I can help you find jobs, optimize your resume, and answer career-related questions. How can I assist you today?",
      isUser: false,
      time: "Just now"
    }
  ])
  const [isThinking, setIsThinking] = useState(false)
  const [showJobs, setShowJobs] = useState(false)
  const [showProfiles, setShowProfiles] = useState(false)
  const [showPosts, setShowPosts] = useState(false)
  const [isLoadingJobs, setIsLoadingJobs] = useState(false)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [jobs, setJobs] = useState([])
  const [profiles, setProfiles] = useState([])
  const [posts, setPosts] = useState([])
  const [searchType, setSearchType] = useState('all') // Track what type of results we have
  const fileInputRef = React.useRef(null)
  const navigate = useNavigate()
  const { logout } = useAuth()

  const handleBackToFeed = () => {
    navigate('/feed')
  }

  const handleFileClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (event) => {
    const file = event.target.files[0]
    if (file) {
      const validTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword'
      ]
      
      if (validTypes.includes(file.type)) {
        setUploadedFile(file)
        console.log('File uploaded:', file.name)
      } else {
        alert('Please upload a PDF or DOCX file only.')
      }
    }
  }

  const handleRemoveFile = () => {
    setUploadedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleSendMessage = async () => {
    if (message.trim()) {
      const userMessageText = message.trim()
      
      // Add user message
      const userMessage = {
        id: Date.now(),
        text: userMessageText,
        isUser: true,
        time: "Just now"
      }
      setChatMessages(prev => [...prev, userMessage])
      setMessage('')
      
      // Show thinking animation
      setIsThinking(true)
      
      try {
        // Call Nemz API to search across all types (jobs, profiles, posts)
        // Let the backend determine intent or search all types
        const response = await nemzAPI.searchAll({
          query: userMessageText,
          searchType: undefined, // Let backend determine intent based on query
          limit: 10
        })
        
        setIsThinking(false)
        
        if (response.data && response.data.success) {
          const results = response.data
          const foundJobs = results.jobs || []
          const foundProfiles = results.profiles || []
          const foundPosts = results.posts || []
          const detectedType = results.search_type || 'all'
          
          setSearchType(detectedType)
          
          // Map Nemz job results to display format
          const mappedJobs = foundJobs.map((job, index) => {
            const jobData = job.payload || job
            const matchScore = Math.round((job.score || 0) * 100)
            
            return {
              id: jobData.job_id || jobData.id || index + 1,
              title: jobData.title || jobData.job_title || 'Job Title',
              company: jobData.company_name || jobData.company || 'Company',
              location: jobData.location || jobData.city || 'Location',
              type: jobData.job_type || jobData.type || 'Full-time',
              matchScore: matchScore
            }
          })
          
          // Map Nemz profile results to display format
          const mappedProfiles = foundProfiles.map((profile, index) => {
            const profileData = profile.payload || profile
            const matchScore = Math.round((profile.score || 0) * 100)
            
            return {
              id: profileData.user_id || profileData.id || index + 1,
              name: profileData.name || profileData.user_name || 'User',
              about: profileData.about || profileData.short_desc || '',
              skills: profileData.skills || '',
              currentStatus: profileData.current_status || '',
              profileLink: profileData.profile_link || '',
              matchScore: matchScore
            }
          })
          
          // Map Nemz post results to display format
          const mappedPosts = foundPosts.map((post, index) => {
            const postData = post.payload || post
            const matchScore = Math.round((post.score || 0) * 100)
            
            return {
              id: postData.post_id || postData.id || index + 1,
              description: postData.post_desc || postData.description || '',
              userName: postData.user_name || postData.name || 'User',
              userId: postData.user_id || null,
              likes: postData.likes || 0,
              comments: postData.comments || 0,
              mediaUrl: postData.media_url || null,
              mediaType: postData.media_type || null,
              createdAt: postData.created_at || null,
              matchScore: matchScore
            }
          })
          
          setJobs(mappedJobs)
          setProfiles(mappedProfiles)
          setPosts(mappedPosts)
          
          // Build bot response based on all result types
          let botResponseText = ''
          const resultCounts = {
            jobs: foundJobs.length,
            profiles: foundProfiles.length,
            posts: foundPosts.length
          }
          const totalResults = resultCounts.jobs + resultCounts.profiles + resultCounts.posts
          
          if (totalResults > 0) {
            const parts = []
            if (resultCounts.jobs > 0) {
              parts.push(`${resultCounts.jobs} job${resultCounts.jobs > 1 ? 's' : ''}`)
            }
            if (resultCounts.profiles > 0) {
              parts.push(`${resultCounts.profiles} profile${resultCounts.profiles > 1 ? 's' : ''}`)
            }
            if (resultCounts.posts > 0) {
              parts.push(`${resultCounts.posts} post${resultCounts.posts > 1 ? 's' : ''}`)
            }
            
            botResponseText = `I found ${parts.join(', ')} matching your query! Here are the results below with match scores to help you identify the best matches.`
          } else {
            botResponseText = "I couldn't find any results matching your query. Try refining your search terms or check back later."
          }
          
          const botResponse = {
            id: Date.now() + 1,
            text: botResponseText,
            isUser: false,
            time: "Just now"
          }
          setChatMessages(prev => [...prev, botResponse])
          
          // Show results sections if we have any results
          if (totalResults > 0) {
            setIsLoadingJobs(true)
            setTimeout(() => {
              setIsLoadingJobs(false)
              setShowJobs(foundJobs.length > 0)
              setShowProfiles(foundProfiles.length > 0)
              setShowPosts(foundPosts.length > 0)
            }, 500)
          }
        } else {
          // Handle error or no results
          const botResponse = {
            id: Date.now() + 1,
            text: "I encountered an issue searching. Please try again or rephrase your query.",
            isUser: false,
            time: "Just now"
          }
          setChatMessages(prev => [...prev, botResponse])
        }
      } catch (err) {
        setIsThinking(false)
        console.error('Error searching jobs:', err)
        const botResponse = {
          id: Date.now() + 1,
          text: "I'm having trouble connecting to the search service. Please try again in a moment.",
          isUser: false,
          time: "Just now"
        }
        setChatMessages(prev => [...prev, botResponse])
      }
    }
  }


  return (
    <Container>
      <Navbar />

      <MainContainer>
        <SidePanel>
          <PanelHeader>
            <PageTitle>AI Assistant</PageTitle>
            <PageSubtitle>Your career companion</PageSubtitle>
          </PanelHeader>
          
          <PanelContent>
            <PanelSection>
              <SectionTitle>Upload Resume</SectionTitle>
              <FileInput
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.doc"
                onChange={handleFileChange}
              />
              {!uploadedFile ? (
                <UploadArea onClick={handleFileClick}>
                  <UploadIcon>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                      <polyline points="17 8 12 3 7 8"></polyline>
                      <line x1="12" y1="3" x2="12" y2="15"></line>
                    </svg>
                  </UploadIcon>
                  <UploadText>Drag & drop your resume here</UploadText>
                  <UploadText className="upload-text-small">or</UploadText>
                  <UploadButton onClick={(e) => { e.stopPropagation(); handleFileClick(); }}>
                    Browse Files
                  </UploadButton>
                  <UploadText className="upload-text-tiny">
                    Supported formats: PDF, DOCX
                  </UploadText>
                </UploadArea>
              ) : (
                <UploadedFileDisplay>
                  <FileInfo>
                    <FileIcon>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                      </svg>
                    </FileIcon>
                    <FileDetails>
                      <FileName>{uploadedFile.name}</FileName>
                      <FileSize>{(uploadedFile.size / 1024).toFixed(2)} KB</FileSize>
                    </FileDetails>
                  </FileInfo>
                  <RemoveFileButton onClick={handleRemoveFile}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </RemoveFileButton>
                </UploadedFileDisplay>
              )}
            </PanelSection>

            <PanelSection>
              <SectionTitle>Find Jobs</SectionTitle>
              <JobFilterButton 
                active={jobFilter === 'all'} 
                onClick={() => setJobFilter('all')}
              >
                All Jobs
              </JobFilterButton>
              <JobFilterButton 
                active={jobFilter === 'recommended'} 
                onClick={() => setJobFilter('recommended')}
              >
                AI Recommended
              </JobFilterButton>
              <JobFilterButton 
                active={jobFilter === 'remote'} 
                onClick={() => setJobFilter('remote')}
              >
                Remote Only
              </JobFilterButton>
              <JobFilterButton 
                active={jobFilter === 'fulltime'} 
                onClick={() => setJobFilter('fulltime')}
              >
                Full-time
              </JobFilterButton>
            </PanelSection>
          </PanelContent>
        </SidePanel>

        <MainContent>
          {activeSection === 'chat' && (
            <ContentCard>
              <CardHeader>
                <CardHeaderLeft>
                  <CardIcon>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                  </CardIcon>
                  <CardTitle>AI Career Assistant</CardTitle>
                </CardHeaderLeft>
              </CardHeader>

              <ChatContainer>
                {chatMessages.map((msg) => (
                  <MessageBubble key={msg.id} isUser={msg.isUser}>
                    <MessageText>{msg.text}</MessageText>
                    <MessageTime>{msg.time}</MessageTime>
                  </MessageBubble>
                ))}
                {isThinking && (
                  <ThinkingIndicator>
                    <ThinkingDot delay="0s" />
                    <ThinkingDot delay="0.2s" />
                    <ThinkingDot delay="0.4s" />
                  </ThinkingIndicator>
                )}
              </ChatContainer>

              <InputContainer>
                <ChatInput 
                  placeholder="Ask me anything about your career..."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                />
                <SendButton onClick={handleSendMessage}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="22" y1="2" x2="11" y2="13"></line>
                    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                  </svg>
                  Send
                </SendButton>
              </InputContainer>
            </ContentCard>
          )}

          {(isLoadingJobs || showJobs || showProfiles || showPosts) && (
            <>
              {showJobs && (
                <ContentCard>
                  <CardHeader>
                    <CardHeaderLeft>
                      <CardIcon>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                          <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                        </svg>
                      </CardIcon>
                      <CardTitle>Matched Jobs</CardTitle>
                    </CardHeaderLeft>
                  </CardHeader>

                  {isLoadingJobs ? (
                    <LoadingContainer>
                      <LoadingSpinner />
                      <LoadingText>Finding the best jobs for you...</LoadingText>
                    </LoadingContainer>
                  ) : (
                    <JobList>
                      {jobs.length > 0 ? jobs.map((job, index) => (
                        <JobCard key={job.id} delay={`${index * 0.1}s`}>
                          <JobTitle>{job.title}</JobTitle>
                          <JobCompany>{job.company}</JobCompany>
                          <JobMeta>
                            <JobMetaItem>
                              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                                <circle cx="12" cy="10" r="3"></circle>
                              </svg>
                              {job.location}
                            </JobMetaItem>
                            <JobMetaItem>
                              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                              </svg>
                              {job.type}
                            </JobMetaItem>
                          </JobMeta>
                          <MatchScore>{job.matchScore}% Match</MatchScore>
                        </JobCard>
                      )) : null}
                    </JobList>
                  )}
                </ContentCard>
              )}

              {showProfiles && (
                <ContentCard>
                  <CardHeader>
                    <CardHeaderLeft>
                      <CardIcon>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                          <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                      </CardIcon>
                      <CardTitle>Matched Profiles</CardTitle>
                    </CardHeaderLeft>
                  </CardHeader>

                  {isLoadingJobs ? (
                    <LoadingContainer>
                      <LoadingSpinner />
                      <LoadingText>Finding matching profiles...</LoadingText>
                    </LoadingContainer>
                  ) : (
                    <ProfileList>
                      {profiles.length > 0 ? profiles.map((profile, index) => (
                        <ProfileCard key={profile.id} delay={`${index * 0.1}s`}>
                          <ProfileName>{profile.name}</ProfileName>
                          {profile.about && <ProfileAbout>{profile.about}</ProfileAbout>}
                          {profile.skills && <ProfileSkills><strong>Skills:</strong> {profile.skills}</ProfileSkills>}
                          {profile.currentStatus && (
                            <ProfileSkills><strong>Status:</strong> {profile.currentStatus}</ProfileSkills>
                          )}
                          <MatchScore>{profile.matchScore}% Match</MatchScore>
                        </ProfileCard>
                      )) : null}
                    </ProfileList>
                  )}
                </ContentCard>
              )}

              {showPosts && (
                <ContentCard>
                  <CardHeader>
                    <CardHeaderLeft>
                      <CardIcon>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                          <polyline points="14 2 14 8 20 8"></polyline>
                          <line x1="16" y1="13" x2="8" y2="13"></line>
                          <line x1="16" y1="17" x2="8" y2="17"></line>
                        </svg>
                      </CardIcon>
                      <CardTitle>Matched Posts</CardTitle>
                    </CardHeaderLeft>
                  </CardHeader>

                  {isLoadingJobs ? (
                    <LoadingContainer>
                      <LoadingSpinner />
                      <LoadingText>Finding relevant posts...</LoadingText>
                    </LoadingContainer>
                  ) : (
                    <PostList>
                      {posts.length > 0 ? posts.map((post, index) => (
                        <PostCard key={post.id} delay={`${index * 0.1}s`}>
                          <PostAuthor><strong>{post.userName}</strong></PostAuthor>
                          <PostContent>{post.description}</PostContent>
                          <PostMeta>
                            <JobMetaItem>
                              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                              </svg>
                              {post.likes} likes
                            </JobMetaItem>
                            <JobMetaItem>
                              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                              </svg>
                              {post.comments} comments
                            </JobMetaItem>
                          </PostMeta>
                          <MatchScore>{post.matchScore}% Match</MatchScore>
                        </PostCard>
                      )) : null}
                    </PostList>
                  )}
                </ContentCard>
              )}
            </>
          )}
        </MainContent>
      </MainContainer>
    </Container>
  )
}

export default AIMode

