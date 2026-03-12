import React, { useState, useEffect } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import { contextAPI } from '../services/api'
import Messages from './Messages'
import { generateProfileUrl } from '../utils/profileUrl'
import Navbar from '../components/Navbar'
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


const MainContainer = styled.div`
  max-width: 1600px;
  margin: 0 auto 0 0;
  display: grid;
  grid-template-columns: 280px 280px 1fr;
  gap: 25px;
  padding: 30px 20px;
  
  @media (max-width: 1400px) {
    max-width: 100%;
    margin: 0 auto;
    grid-template-columns: 260px 260px 1fr;
    gap: 22px;
    padding: 28px 18px;
  }
  
  @media (max-width: 1200px) {
    max-width: 100%;
    margin: 0 auto;
    grid-template-columns: 260px 1fr;
    gap: 20px;
    padding: 25px 15px;
  }
  
  @media (max-width: 1024px) {
    grid-template-columns: 240px 1fr;
    gap: 18px;
    padding: 20px 15px;
  }
  
  @media (max-width: 900px) {
    grid-template-columns: 220px 1fr;
    gap: 16px;
    padding: 18px 12px;
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

const Sidebar = styled.aside`
  position: sticky;
  top: 100px;
  height: fit-content;
  
  @media (max-width: 768px) {
    position: static;
    top: auto;
  }
`

const ProfileCard = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  padding: 30px;
  border: 1px solid var(--border);
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    border-color: var(--primary);
  }
  
  @media (max-width: 768px) {
    padding: 25px 20px;
  }
  
  @media (max-width: 480px) {
    padding: 20px 15px;
    border-radius: 10px;
  }
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
  
  @media (max-width: 768px) {
    width: 70px;
    height: 70px;
    font-size: 1.8em;
    margin-bottom: 16px;
  }
  
  @media (max-width: 480px) {
    width: 60px;
    height: 60px;
    font-size: 1.5em;
    margin-bottom: 12px;
  }
`

const ProfileName = styled.h3`
  font-size: 1.3em;
  margin-bottom: 10px;
  color: var(--text);
  
  @media (max-width: 768px) {
    font-size: 1.2em;
    margin-bottom: 8px;
  }
  
  @media (max-width: 480px) {
    font-size: 1.1em;
    margin-bottom: 6px;
  }
  
  @media (max-width: 360px) {
    font-size: 1em;
  }
`

const ProfileHeadline = styled.p`
  color: var(--text-light);
  margin-bottom: 15px;
  font-size: 0.9em;
  
  @media (max-width: 768px) {
    font-size: 0.85em;
    margin-bottom: 12px;
  }
  
  @media (max-width: 480px) {
    font-size: 0.8em;
    margin-bottom: 10px;
  }
`

const ProfileBio = styled.p`
  color: var(--text-lighter);
  font-size: 0.85em;
  line-height: 1.5;
  
  @media (max-width: 768px) {
    font-size: 0.8em;
    line-height: 1.4;
  }
  
  @media (max-width: 480px) {
    font-size: 0.75em;
    line-height: 1.4;
  }
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

const MobileMenuButton = styled.button`
  display: none;
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.3s ease;
  z-index: 101;
  
  @media (max-width: 1024px) {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  &:hover {
    background: rgba(10, 102, 194, 0.1);
    color: var(--primary);
  }
  
  svg {
    width: 24px;
    height: 24px;
  }
`

const MobileMenuOverlay = styled.div`
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  z-index: 199;
  opacity: ${props => props.isOpen ? 1 : 0};
  pointer-events: ${props => props.isOpen ? 'auto' : 'none'};
  transition: opacity 0.3s ease;
  
  @media (max-width: 1024px) {
    display: block;
  }
`

const MobileSidePanel = styled.aside`
  display: none;
  position: fixed;
  top: 0;
  left: ${props => props.isOpen ? '0' : '-100%'};
  width: 280px;
  max-width: 85vw;
  height: 100vh;
  background: var(--bg-white);
  z-index: 200;
  overflow-y: auto;
  box-shadow: 2px 0 20px rgba(0, 0, 0, 0.3);
  transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  @media (max-width: 1024px) {
    display: block;
  }
  
  @media (max-width: 480px) {
    width: 260px;
    max-width: 90vw;
  }
  
  & ${SidePanel} {
    border-radius: 0;
    border: none;
    box-shadow: none;
    margin: 0;
  }
`

const MobileMenuHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-white);
  position: sticky;
  top: 0;
  z-index: 10;
  
  h2 {
    font-size: 1.2em;
    color: var(--text);
    font-weight: 600;
    margin: 0;
  }
`

const MobileMenuCloseButton = styled.button`
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: var(--hover-bg);
    color: var(--text);
    transform: rotate(90deg);
  }
  
  svg {
    width: 24px;
    height: 24px;
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
  
  @media (max-width: 768px) {
    padding: 18px;
    margin-bottom: 20px;
    border-radius: 10px;
  }
  
  @media (max-width: 480px) {
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 8px;
  }
`

const PostCreatorHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
  
  @media (max-width: 768px) {
    gap: 10px;
    margin-bottom: 14px;
    padding-bottom: 10px;
  }
  
  @media (max-width: 480px) {
    gap: 8px;
    margin-bottom: 12px;
    padding-bottom: 8px;
  }
  
  @media (max-width: 360px) {
    gap: 6px;
    margin-bottom: 10px;
    padding-bottom: 6px;
  }
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
  flex-shrink: 0;
  
  @media (max-width: 768px) {
    width: 44px;
    height: 44px;
    font-size: 1.1em;
  }
  
  @media (max-width: 480px) {
    width: 40px;
    height: 40px;
    font-size: 1em;
  }
  
  @media (max-width: 360px) {
    width: 36px;
    height: 36px;
    font-size: 0.9em;
  }
`

const PostCreatorInfo = styled.div`
  flex: 1;
`

const PostCreatorTitle = styled.h3`
  font-size: 1em;
  color: var(--text);
  margin-bottom: 4px;
  font-weight: 600;
  
  @media (max-width: 768px) {
    font-size: 0.95em;
    margin-bottom: 3px;
  }
  
  @media (max-width: 480px) {
    font-size: 0.9em;
    margin-bottom: 2px;
  }
  
  @media (max-width: 360px) {
    font-size: 0.85em;
  }
`

const PostCreatorSubtitle = styled.p`
  font-size: 0.85em;
  color: var(--text-light);
  
  @media (max-width: 768px) {
    font-size: 0.8em;
  }
  
  @media (max-width: 480px) {
    font-size: 0.75em;
  }
  
  @media (max-width: 360px) {
    font-size: 0.7em;
  }
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
  
  @media (max-width: 768px) {
    padding: 12px;
    font-size: 0.95em;
    min-height: 70px;
  }
  
  @media (max-width: 480px) {
    padding: 10px;
    font-size: 0.9em;
    min-height: 60px;
    border-radius: 6px;
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
  min-height: 44px; /* Better touch target */
  
  &:hover {
    background: var(--primary-dark);
    transform: translateY(-2px);
  }
  
  &:active {
    transform: translateY(0) scale(0.98);
  }
  
  @media (max-width: 768px) {
    padding: 10px 20px;
    font-size: 0.95em;
    align-self: stretch;
    width: 100%;
  }
  
  @media (max-width: 480px) {
    padding: 10px 16px;
    font-size: 0.9em;
    border-radius: 6px;
    min-height: 42px;
  }
  
  @media (max-width: 360px) {
    padding: 8px 14px;
    font-size: 0.85em;
  }
`

const PostsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  
  @media (max-width: 768px) {
    gap: 18px;
  }
  
  @media (max-width: 480px) {
    gap: 15px;
  }
  
  @media (max-width: 360px) {
    gap: 12px;
  }
`

const Post = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border);
  animation: ${slideUp} 0.3s ease-out;
  
  @media (max-width: 768px) {
    padding: 18px;
    border-radius: 10px;
  }
  
  @media (max-width: 480px) {
    padding: 15px;
    border-radius: 8px;
  }
`

const PostHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
  
  @media (max-width: 480px) {
    gap: 12px;
    margin-bottom: 12px;
  }
  
  @media (max-width: 360px) {
    gap: 10px;
    margin-bottom: 10px;
  }
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
  flex-shrink: 0;
  
  @media (max-width: 768px) {
    width: 45px;
    height: 45px;
    font-size: 1.1em;
  }
  
  @media (max-width: 480px) {
    width: 40px;
    height: 40px;
    font-size: 1em;
  }
  
  @media (max-width: 360px) {
    width: 36px;
    height: 36px;
    font-size: 0.9em;
  }
`

const PostInfo = styled.div`
  flex: 1;
`

const PostName = styled.h4`
  font-size: 1em;
  margin-bottom: 2px;
  color: var(--text);
  
  @media (max-width: 768px) {
    font-size: 0.95em;
  }
  
  @media (max-width: 480px) {
    font-size: 0.9em;
    margin-bottom: 1px;
  }
  
  @media (max-width: 360px) {
    font-size: 0.85em;
  }
`

const PostUsername = styled.div`
  font-size: 0.85em;
  color: var(--text-lighter);
  margin-bottom: 2px;
  
  @media (max-width: 768px) {
    font-size: 0.8em;
  }
  
  @media (max-width: 480px) {
    font-size: 0.75em;
    margin-bottom: 1px;
  }
`

const PostTime = styled.div`
  font-size: 0.8em;
  color: var(--text-lighter);
  
  @media (max-width: 768px) {
    font-size: 0.75em;
  }
  
  @media (max-width: 480px) {
    font-size: 0.7em;
  }
`

const PostContent = styled.div`
  margin-bottom: 15px;
  line-height: 1.6;
  color: var(--text);
  word-wrap: break-word;
  overflow-wrap: break-word;
  
  @media (max-width: 768px) {
    margin-bottom: 12px;
    line-height: 1.5;
    font-size: 0.95em;
  }
  
  @media (max-width: 480px) {
    margin-bottom: 10px;
    line-height: 1.5;
    font-size: 0.9em;
  }
  
  @media (max-width: 360px) {
    font-size: 0.85em;
  }
`

const PostMedia = styled.div`
  margin-bottom: 15px;
  border-radius: 12px;
  overflow: hidden;
  
  img, video {
    display: block;
    width: 100%;
    max-height: 500px;
    object-fit: cover;
  }
  
  @media (max-width: 768px) {
    margin-bottom: 12px;
    border-radius: 10px;
    
    img, video {
      max-height: 400px;
    }
  }
  
  @media (max-width: 480px) {
    margin-bottom: 10px;
    border-radius: 8px;
    
    img, video {
      max-height: 300px;
    }
  }
  
  @media (max-width: 360px) {
    border-radius: 6px;
    
    img, video {
      max-height: 250px;
    }
  }
`

const MediaPreviewContainer = styled.div`
  position: relative;
  margin-top: 10px;
  border-radius: 12px;
  overflow: hidden;
  max-width: 300px;
  
  img, video {
    width: 100%;
    max-height: 200px;
    object-fit: cover;
  }
  
  @media (max-width: 768px) {
    max-width: 250px;
    border-radius: 10px;
    
    img, video {
      max-height: 180px;
    }
  }
  
  @media (max-width: 480px) {
    max-width: 100%;
    border-radius: 8px;
    
    img, video {
      max-height: 150px;
    }
  }
  
  @media (max-width: 360px) {
    border-radius: 6px;
    
    img, video {
      max-height: 120px;
    }
  }
`

const MediaRemoveButton = styled.button`
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: all 0.2s ease;
  min-width: 44px; /* Better touch target */
  min-height: 44px;
  
  &:hover {
    background: rgba(0, 0, 0, 0.9);
    transform: scale(1.1);
  }
  
  @media (max-width: 480px) {
    width: 32px;
    height: 32px;
    top: 6px;
    right: 6px;
  }
  
  @media (max-width: 360px) {
    width: 36px;
    height: 36px;
    top: 4px;
    right: 4px;
  }
`

const MediaUploadButton = styled.label`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--hover-bg);
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-lighter);
  transition: all 0.2s ease;
  min-height: 44px; /* Better touch target */
  
  &:hover {
    background: var(--accent);
    color: white;
  }
  
  input {
    display: none;
  }
  
  @media (max-width: 768px) {
    padding: 8px 10px;
    font-size: 0.9em;
    gap: 5px;
  }
  
  @media (max-width: 480px) {
    padding: 6px 8px;
    font-size: 0.85em;
    border-radius: 6px;
    gap: 4px;
    
    svg {
      width: 16px;
      height: 16px;
    }
  }
  
  @media (max-width: 360px) {
    padding: 6px;
    font-size: 0.8em;
  }
`

const LoadMoreSpinner = styled.div`
  display: flex;
  justify-content: center;
  padding: 20px;
  color: var(--text-lighter);
`

const PostActions = styled.div`
  display: flex;
  gap: 20px;
  
  @media (max-width: 768px) {
    gap: 15px;
  }
  
  @media (max-width: 480px) {
    gap: 12px;
    flex-wrap: wrap;
  }
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
  
  @media (max-width: 480px) {
    padding: 6px 10px;
    gap: 6px;
    font-size: 0.85em;
    
    svg {
      width: 18px;
      height: 18px;
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
  const [loadingMore, setLoadingMore] = useState(false)
  const [postContent, setPostContent] = useState('')
  const [mediaFile, setMediaFile] = useState(null)
  const [mediaPreview, setMediaPreview] = useState(null)
  const [uploadingMedia, setUploadingMedia] = useState(false)
  const [cursor, setCursor] = useState(null)
  const [hasMore, setHasMore] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searchTimeout, setSearchTimeout] = useState(null)
  const [messagesOpen, setMessagesOpen] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const { logout } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    loadUser()
    loadPosts()
  }, [])


  const loadUser = async () => {
    try {
      const response = await api.get('/api/user')
      let userData = response.data
      
      // If wrapped in 'data' object, unwrap it
      if (userData && userData.data) {
        userData = userData.data
      }
      
      if (userData && !userData.error) {
        // Normalize field names between Flask and FastAPI formats
        setUser({
          ...userData,
          full_name: userData.full_name || userData.name || userData.username,
          headline: userData.headline || userData.short_desc || '',
          bio: userData.bio || userData.about || '',
          id: userData.id || userData.uid
        })
      }
    } catch (error) {
      console.error('Error loading user:', error)
    }
  }

  const loadPosts = async (loadMore = false) => {
    try {
      if (loadMore) {
        setLoadingMore(true)
      }
      
      const params = new URLSearchParams()
      if (loadMore && cursor) {
        params.append('cursor', cursor)
      }
      params.append('limit', '20')
      
      const response = await api.get(`/api/feed?${params.toString()}`)
      
      // Handle FastAPI response format: {posts: [...], pagination: {...}}
      // Also handle Flask format: {data: {posts: [...], pagination: {...}}}
      let feedData = response.data
      
      // If wrapped in 'data' object (Flask format), unwrap it
      if (feedData && feedData.data) {
        feedData = feedData.data
      }
      
      if (feedData && feedData.posts) {
        const newPosts = feedData.posts || []
        
        if (loadMore) {
          setPosts(prev => [...prev, ...newPosts])
        } else {
          setPosts(newPosts)
        }
        
        // Update pagination state
        if (feedData.pagination) {
          setCursor(feedData.pagination.next_cursor)
          setHasMore(feedData.pagination.has_more)
        }
      } else if (Array.isArray(feedData)) {
        // Direct array response
        setPosts(loadMore ? prev => [...prev, ...feedData] : feedData)
      } else {
        console.log('Unexpected feed response format:', response.data)
        if (!loadMore) setPosts([])
      }
    } catch (error) {
      console.error('Error loading posts:', error)
      if (!loadMore) setPosts([])
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }

  // Infinite scroll handler
  const handleScroll = () => {
    if (loadingMore || !hasMore) return
    
    const scrollTop = window.scrollY
    const scrollHeight = document.documentElement.scrollHeight
    const clientHeight = window.innerHeight
    
    // Load more when user is 200px from bottom
    if (scrollTop + clientHeight >= scrollHeight - 200) {
      loadPosts(true)
    }
  }

  useEffect(() => {
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [cursor, hasMore, loadingMore])

  // Media upload to Cloudinary
  const handleMediaSelect = (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'video/mp4', 'video/webm']
    if (!validTypes.includes(file.type)) {
      alert('Please select a valid image or video file')
      return
    }
    
    // Validate file size (max 50MB for videos, 10MB for images)
    const maxSize = file.type.startsWith('video') ? 50 * 1024 * 1024 : 10 * 1024 * 1024
    if (file.size > maxSize) {
      alert(`File too large. Max size: ${file.type.startsWith('video') ? '50MB' : '10MB'}`)
      return
    }
    
    setMediaFile(file)
    
    // Create preview
    const reader = new FileReader()
    reader.onloadend = () => {
      setMediaPreview({
        url: reader.result,
        type: file.type.startsWith('video') ? 'video' : 'image'
      })
    }
    reader.readAsDataURL(file)
  }

  const clearMedia = () => {
    setMediaFile(null)
    setMediaPreview(null)
  }

  const uploadToCloudinary = async (file) => {
    const cloudName = import.meta.env.VITE_CLOUDINARY_CLOUD_NAME
    const uploadPreset = import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET
    
    if (!cloudName || !uploadPreset) {
      console.error('Cloudinary config missing')
      return null
    }
    
    const formData = new FormData()
    formData.append('file', file)
    formData.append('upload_preset', uploadPreset)
    
    const resourceType = file.type.startsWith('video') ? 'video' : 'image'
    
    try {
      const response = await fetch(
        `https://api.cloudinary.com/v1_1/${cloudName}/${resourceType}/upload`,
        { method: 'POST', body: formData }
      )
      const data = await response.json()
      return {
        url: data.secure_url,
        type: resourceType
      }
    } catch (error) {
      console.error('Cloudinary upload error:', error)
      return null
    }
  }

  const createPost = async () => {
    if (!postContent.trim() && !mediaFile) {
      alert('Please enter some content or add media')
      return
    }
    
    try {
      let mediaData = null
      
      // Upload media to Cloudinary if present
      if (mediaFile) {
        setUploadingMedia(true)
        mediaData = await uploadToCloudinary(mediaFile)
        setUploadingMedia(false)
        
        if (!mediaData) {
          alert('Failed to upload media. Please try again.')
          return
        }
      }
      
      // Create post with optional media
      const postData = {
        content: postContent,
        ...(mediaData && {
          media_url: mediaData.url,
          media_type: mediaData.type
        })
      }
      
      const response = await api.post('/api/posts', postData)
      if (response.data.id) {
        setPostContent('')
        clearMedia()
        // Reset pagination and reload feed
        setCursor(null)
        setHasMore(true)
        loadPosts()
      }
    } catch (error) {
      console.error('Error creating post:', error)
      alert('Failed to create post')
      setUploadingMedia(false)
    }
  }

  const handleLike = async (postId) => {
    try {
      const response = await api.post(`/api/posts/${postId}/like`)
      // Handle FastAPI response (direct) or Flask response (wrapped in data)
      const data = response.data?.data || response.data
      if (data) {
        // Update the specific post's like count
        setPosts(posts.map(post => 
          post.id === postId 
            ? { 
                ...post, 
                like_count: data.like_count,
                is_liked: data.is_liked 
              }
            : post
        ))
        
        // Update context if post was liked
        if (data.is_liked) {
          contextAPI.updateContext('like', 'post', postId).catch(() => {})
        }
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
      const response = await api.get(`/api/user/search?q=${encodeURIComponent(query)}`)
      // Handle new response format with users, jobs, posts
      // Extract users array from response
      let usersData = []
      if (response && response.data) {
        // Check if new format (has users property)
        if (response.data.users && Array.isArray(response.data.users)) {
          usersData = response.data.users
        } else if (Array.isArray(response.data)) {
          // Old format - direct array
          usersData = response.data
        }
      }
      // Normalize user data to have consistent field names
      const users = usersData.map(u => ({
        ...u,
        id: u.id || u.uid,
        full_name: u.full_name || u.name || u.username
      }))
      setSearchResults(users)
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

  const handleLogout = () => {
    logout()
    navigate('/landing')
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
    // Toggle messages overlay panel
    setMessagesOpen(!messagesOpen)
  }


  return (
    <Container>
      <Navbar />

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
            
            <PanelSection onClick={() => navigate('/jobs')}>
              <PanelLink>
                <span className="icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                  </svg>
                </span>
                <span>Jobs</span>
              </PanelLink>
            </PanelSection>
            
            <PanelSection onClick={() => user?.id && user?.username && navigate(generateProfileUrl(user.id, user.username))}>
              <PanelLink>
                <span className="icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                </span>
                <span>Profile</span>
              </PanelLink>
            </PanelSection>
            
            <PanelSection onClick={() => navigate('/settings')}>
              <PanelLink>
                <span className="icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="3"></circle>
                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                  </svg>
                </span>
                <span>Settings</span>
              </PanelLink>
            </PanelSection>
          </SidePanel>
        </LeftSidebar>

        <Sidebar>
          <ProfileCard onClick={() => user?.id && user?.username && navigate(generateProfileUrl(user.id, user.username))}>
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
              {mediaPreview && (
                <MediaPreviewContainer>
                  {mediaPreview.type === 'video' ? (
                    <video src={mediaPreview.url} controls />
                  ) : (
                    <img src={mediaPreview.url} alt="Preview" />
                  )}
                  <MediaRemoveButton onClick={clearMedia}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <line x1="18" y1="6" x2="6" y2="18" />
                      <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                  </MediaRemoveButton>
                </MediaPreviewContainer>
              )}
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginTop: '10px' }}>
                <MediaUploadButton>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" />
                    <polyline points="21,15 16,10 5,21" />
                  </svg>
                  Photo/Video
                  <input 
                    type="file" 
                    accept="image/*,video/*" 
                    onChange={handleMediaSelect}
                  />
                </MediaUploadButton>
                <PostButton onClick={createPost} disabled={uploadingMedia}>
                  {uploadingMedia ? 'Uploading...' : 'Post'}
                </PostButton>
              </div>
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
                  {post.media_url && (
                    <PostMedia>
                      {post.media_type === 'video' ? (
                        <video 
                          src={post.media_url} 
                          controls 
                          preload="metadata"
                          style={{ maxWidth: '100%', maxHeight: '500px', borderRadius: '12px' }}
                        />
                      ) : (
                        <img 
                          src={post.media_url} 
                          alt="Post media" 
                          loading="lazy"
                          style={{ maxWidth: '100%', maxHeight: '500px', borderRadius: '12px', objectFit: 'cover' }}
                        />
                      )}
                    </PostMedia>
                  )}
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
            {loadingMore && (
              <LoadMoreSpinner>Loading more posts...</LoadMoreSpinner>
            )}
            {!hasMore && posts.length > 0 && (
              <LoadMoreSpinner>You've reached the end!</LoadMoreSpinner>
            )}
          </PostsContainer>
        </FeedContainer>

        <MessagesPanel isOpen={messagesOpen}>
          <Messages overlay={true} onClose={() => setMessagesOpen(false)} />
        </MessagesPanel>
      </MainContainer>
    </Container>
  )
}

export default Feed
