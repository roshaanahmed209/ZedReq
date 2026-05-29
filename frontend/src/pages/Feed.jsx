import React, { useState, useEffect, useRef } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'
import api from '../services/api'
import Messages from './Messages'
import { generateProfileUrl } from '../utils/profileUrl'
import { shouldSkipMediaLoad } from '../utils/mediaUrl'
import Navbar from '../components/Navbar'
import PostComments from '../components/PostComments'
import SharePostButton from '../components/SharePostButton'
import '../css/pages/Feed.css'

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`

const slideUp = keyframes`
  from { transform: translateY(10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`

const Container = styled.div`
  position: relative;
  min-height: 100vh;
  animation: ${fadeIn} 0.6s ease-in;

  /*
   * Beam: radial burst originating from the bottom-right corner using #1585A1,
   * fading to transparent as it travels toward the top-left.
   */
  &::before {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 0;
    background-color: var(--bg-light);
    background-image:
      radial-gradient(ellipse 100% 80% at 100% 0%, rgba(21, 133, 161, 0.14) 0%, transparent 52%),
      radial-gradient(ellipse 70% 60% at 0% 100%, rgba(21, 133, 161, 0.08) 0%, transparent 48%);
    pointer-events: none;
  }
`

const MainContainer = styled.div`
  position: relative;
  z-index: 1;
  max-width: 1880px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 268px 248px minmax(0, 1fr);
  gap: 28px;
  padding: 28px clamp(16px, 2.5vw, 32px);
  background: transparent;
  
  @media (max-width: 1400px) {
    max-width: 100%;
    margin: 0 auto;
    grid-template-columns: 254px 236px minmax(0, 1fr);
    gap: 22px;
    padding: 28px 18px;
  }
  
  @media (max-width: 1200px) {
    max-width: 100%;
    margin: 0 auto;
    grid-template-columns: 298px 1fr;
    gap: 20px;
    padding: 25px 15px;
  }
  
  @media (max-width: 1024px) {
    grid-template-columns: 276px 1fr;
    gap: 18px;
    padding: 20px 15px;
  }
  
  @media (max-width: 900px) {
    grid-template-columns: 256px 1fr;
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
  background: transparent;

  @media (max-width: 768px) {
    position: static;
    top: auto;
  }
`

const ProfileCard = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  padding: 28px 24px;
  border: 1px solid var(--border);
  text-align: center;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04), 0 6px 20px rgba(0, 0, 0, 0.04);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    border-color: rgba(21, 133, 161, 0.35);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06), 0 12px 32px rgba(0, 0, 0, 0.06);
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
  background: linear-gradient(145deg, var(--primary) 0%, #0f6a82 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2em;
  font-weight: 600;
  margin: 0 auto 20px;
  box-shadow: 0 0 0 3px rgba(21, 133, 161, 0.12);
  
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
  font-size: 1.2em;
  font-weight: 600;
  letter-spacing: -0.02em;
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
  font-size: 0.875em;
  line-height: 1.45;
  
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
  background: transparent;

  @media (max-width: 1024px) {
    display: none;
  }
`

const SidePanel = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  border: 1px solid var(--border);
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04), 0 6px 20px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.2s ease;

  &:hover {
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05), 0 10px 28px rgba(0, 0, 0, 0.06);
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
    background: rgba(21, 133, 161, 0.1);
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
  transition: background 0.2s ease, color 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: var(--hover-bg);
    color: var(--text);
  }
  
  svg {
    width: 24px;
    height: 24px;
  }
`

const PanelSection = styled.div`
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
  transition: background 0.15s ease;
  
  &:last-child {
    border-bottom: none;
  }
  
  &:hover {
    background: var(--hover-bg);
    cursor: pointer;
  }
`

const PanelHeader = styled.div`
  padding: 18px 20px;
  background: #0f6a82;
  color: white;
  font-weight: 600;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
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
    font-weight: 600;
    font-size: 1.05em;
    font-variant-numeric: tabular-nums;
    color: var(--primary);
  }
`

const PanelLink = styled.div`
  display: flex;
  align-items: center;
  gap: 14px;
  color: var(--text);
  font-size: 0.9em;
  font-weight: 500;
  transition: color 0.15s ease;
  
  .icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    background: rgba(21, 133, 161, 0.08);
    border-radius: 8px;
    transition: background 0.15s ease, color 0.15s ease;
    
    svg {
      color: var(--text-light);
      transition: color 0.15s ease;
    }
  }
  
  &:hover {
    color: var(--primary);
    
    .icon {
      background: rgba(21, 133, 161, 0.16);
      
      svg {
        color: var(--primary);
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

const FeedContainer = styled.main`
  width: 100%;
  min-width: 0;
  background: transparent;
`

const PostCreator = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  padding: 22px 22px 20px;
  margin-bottom: 24px;
  border: 1px solid var(--border);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04), 0 4px 16px rgba(0, 0, 0, 0.04);
  
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
  padding-bottom: 14px;
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
  font-size: 0.9375rem;
  color: var(--text);
  margin-bottom: 4px;
  font-weight: 600;
  letter-spacing: -0.02em;
  
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
  padding: 14px 16px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--bg-light);
  color: var(--text);
  font-size: 0.9375rem;
  line-height: 1.5;
  resize: vertical;
  min-height: 88px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  
  &:focus {
    outline: none;
    border-color: rgba(21, 133, 161, 0.45);
    box-shadow: 0 0 0 3px rgba(21, 133, 161, 0.1);
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
  padding: 10px 22px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  letter-spacing: 0.02em;
  cursor: pointer;
  transition: background 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
  min-height: 44px; /* Better touch target */
  
  &:hover:not(:disabled) {
    background: var(--primary-dark);
    box-shadow: 0 2px 8px rgba(21, 133, 161, 0.35);
  }
  
  &:active:not(:disabled) {
    opacity: 0.92;
  }

  &:disabled {
    opacity: 0.65;
    cursor: not-allowed;
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
  gap: 16px;
  
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

const DiscoveryBanner = styled.div`
  text-align: center;
  padding: 12px 16px;
  margin: 8px 0 16px;
  font-size: 0.85rem;
  color: var(--text-lighter);
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  background: var(--bg-light);
  border-radius: 8px;
`

const Post = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  padding: 20px 22px;
  border: 1px solid var(--border);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04), 0 4px 14px rgba(0, 0, 0, 0.04);
  animation: ${slideUp} 0.35s ease-out;
  
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
  background: linear-gradient(145deg, var(--primary) 0%, #0f6a82 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 1.05em;
  flex-shrink: 0;
  box-shadow: 0 0 0 2px rgba(21, 133, 161, 0.1);
  
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
  font-size: 0.9375rem;
  font-weight: 600;
  letter-spacing: -0.01em;
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
  line-height: 1.65;
  font-size: 0.9375rem;
  color: var(--text);
  white-space: pre-wrap;
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
  padding: 8px 14px;
  background: var(--hover-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-light);
  font-size: 0.875rem;
  transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
  min-height: 44px; /* Better touch target */
  
  &:hover {
    background: rgba(21, 133, 161, 0.08);
    border-color: rgba(21, 133, 161, 0.25);
    color: var(--primary);
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
  padding: 22px 20px;
  color: var(--text-light);
  font-size: 0.875rem;
  letter-spacing: 0.02em;
`

const PostActions = styled.div`
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  width: 100%;
  gap: 8px;
  padding-top: 14px;
  margin-top: 2px;
  border-top: 1px solid var(--border);

  @media (max-width: 480px) {
    gap: 6px;
  }
`

const PostActionsStart = styled.div`
  justify-self: start;
`

const PostActionsCenter = styled.div`
  justify-self: center;
`

const PostActionsEnd = styled.div`
  justify-self: end;
`

const PostAction = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
  padding: 8px 12px;
  border-radius: 8px;
  
  svg {
    transition: color 0.15s ease;
  }
  
  &:hover {
    background: var(--hover-bg);
    color: var(--text);
  }
  
  &.liked {
    color: var(--primary);

    svg {
      color: var(--primary);
    }
  }

  @media (max-width: 768px) {
    min-height: 44px;
    padding: 10px 14px;
  }

  @media (max-width: 480px) {
    padding: 8px 12px;
    gap: 8px;
    font-size: 0.9em;
    min-height: 44px;

    svg {
      width: 20px;
      height: 20px;
      flex-shrink: 0;
    }
  }
`

const LikeCount = styled.span`
  font-size: 0.8125rem;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  min-width: 1ch;
`

const Loading = styled.div`
  text-align: center;
  padding: 44px 28px;
  color: var(--text-light);
  font-size: 0.9375rem;
  line-height: 1.5;
  letter-spacing: 0.01em;
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
`

const MessagesPanel = styled.aside`
  position: fixed;
  top: 100px;
  right: ${props => props.isOpen ? '20px' : '-400px'};
  width: 380px;
  height: 500px;
  max-height: calc(100vh - 140px);
  background: var(--bg-white);
  border-radius: 12px;
  border: 1px solid var(--border);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12), 0 0 1px rgba(0, 0, 0, 0.08);
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
  font-size: 1.05rem;
  color: var(--text);
  font-weight: 600;
  letter-spacing: -0.02em;
`

const CloseButton = styled.button`
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--text-light);
  cursor: pointer;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s ease, color 0.15s ease;

  &:hover {
    background: var(--hover-bg);
    color: var(--text);
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
  transition: background 0.15s ease;
  margin-bottom: 4px;
  opacity: 1;

  &:hover {
    background: var(--hover-bg);
  }
`

const ContactAvatar = styled.div`
  width: 44px;
  height: 44px;
  min-width: 44px;
  border-radius: 50%;
  background: ${props => props.isBot ? 'linear-gradient(145deg, var(--primary) 0%, #0f6a82 100%)' : 'var(--primary)'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 0.9em;

  svg {
    width: 24px;
    height: 24px;
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
  font-size: 0.875rem;
  line-height: 1.45;
  word-wrap: break-word;
  border: ${props => (!props.isUser ? '1px solid var(--border)' : 'none')};
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
  font-size: 0.875rem;
  font-family: inherit;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;

  &:focus {
    outline: none;
    border-color: rgba(21, 133, 161, 0.45);
    background: var(--bg-white);
    box-shadow: 0 0 0 3px rgba(21, 133, 161, 0.1);
  }

  &::placeholder {
    color: var(--text-lighter);
  }
`

const SendButton = styled.button`
  padding: 10px 14px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s ease, box-shadow 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: var(--primary-dark);
    box-shadow: 0 2px 8px rgba(21, 133, 161, 0.35);
  }

  &:active {
    opacity: 0.92;
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
  transition: background 0.15s ease, box-shadow 0.15s ease;

  &:hover {
    background: var(--primary-dark);
    box-shadow: 0 2px 8px rgba(21, 133, 161, 0.35);
  }

  &:active {
    opacity: 0.9;
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
  const [discoveryStartIndex, setDiscoveryStartIndex] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searchTimeout, setSearchTimeout] = useState(null)
  const [messagesOpen, setMessagesOpen] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [commentsOpenByPost, setCommentsOpenByPost] = useState({})
  const { logout, sessionFeedStats } = useAuth()
  const { theme } = useTheme()
  const navigate = useNavigate()
  const likingPostIdsRef = useRef(new Set())

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
    } catch {
      // error surfaced on backend
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
        const segment = feedData.meta?.feed_segment

        if (loadMore) {
          if (segment === 'discovery' && discoveryStartIndex === null) {
            setPosts((prev) => {
              setDiscoveryStartIndex(prev.length)
              return [...prev, ...newPosts]
            })
          } else {
            setPosts((prev) => [...prev, ...newPosts])
          }
        } else {
          setPosts(newPosts)
          setDiscoveryStartIndex(segment === 'discovery' ? 0 : null)
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
        if (!loadMore) setPosts([])
      }
    } catch {
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
    } catch {
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
        setDiscoveryStartIndex(null)
        loadPosts()
      }
    } catch {
      alert('Failed to create post')
      setUploadingMedia(false)
    }
  }

  const handleLike = async (postId) => {
    if (likingPostIdsRef.current.has(postId)) return
    const target = posts.find(p => p.id === postId)
    if (!target) return

    const prevLiked = !!target.is_liked
    const prevCount = Number(target.like_count) || 0

    likingPostIdsRef.current.add(postId)
    setPosts(prev =>
      prev.map(post =>
        post.id === postId
          ? {
              ...post,
              is_liked: !prevLiked,
              like_count: Math.max(0, prevCount + (prevLiked ? -1 : 1)),
            }
          : post
      )
    )

    try {
      const response = await api.post(`/api/posts/${postId}/like`)
      const data = response.data?.data || response.data
      if (data) {
        setPosts(prev =>
          prev.map(post =>
            post.id === postId
              ? { ...post, like_count: data.like_count, is_liked: data.is_liked }
              : post
          )
        )
      }
    } catch {
      setPosts(prev =>
        prev.map(post =>
          post.id === postId
            ? { ...post, is_liked: prevLiked, like_count: prevCount }
            : post
        )
      )
    } finally {
      likingPostIdsRef.current.delete(postId)
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
    } catch {
      // error surfaced on backend
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
    navigate('/login')
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
    if (text == null) return ''
    const div = document.createElement('div')
    div.textContent = String(text)
    return div.innerHTML.replace(/\n/g, '<br />')
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
                <span className="value">
                  {sessionFeedStats != null
                    ? sessionFeedStats.profileViews.toLocaleString()
                    : '—'}
                </span>
              </PanelItem>
            </PanelSection>
            
            <PanelSection>
              <PanelItem>
                <span className="label">Post impressions</span>
                <span className="value">
                  {sessionFeedStats != null
                    ? sessionFeedStats.postImpressions.toLocaleString()
                    : '—'}
                </span>
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
              posts.map((post, index) => (
                <React.Fragment key={post.id}>
                  {discoveryStartIndex !== null && index === discoveryStartIndex && (
                    <DiscoveryBanner>
                      You&apos;ve seen posts from your network — here are more from across the platform
                    </DiscoveryBanner>
                  )}
                <Post>
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
                  {post.media_url && !shouldSkipMediaLoad(post.media_url) && (
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
                    <PostActionsStart>
                      <PostAction
                        type="button"
                        aria-label={post.is_liked ? 'Unlike' : 'Like'}
                        className={post.is_liked ? 'liked' : ''}
                        onClick={() => handleLike(post.id)}
                      >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill={post.is_liked ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                          <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3" />
                        </svg>
                        <LikeCount>{post.like_count}</LikeCount>
                      </PostAction>
                    </PostActionsStart>
                    <PostActionsCenter>
                      <PostAction
                        type="button"
                        aria-label={
                          commentsOpenByPost[post.id]
                            ? 'Hide comments'
                            : 'Show comments'
                        }
                        aria-expanded={!!commentsOpenByPost[post.id]}
                        onClick={() =>
                          setCommentsOpenByPost(prev => ({
                            ...prev,
                            [post.id]: !prev[post.id],
                          }))
                        }
                      >
                        <svg
                          width="20"
                          height="20"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          aria-hidden
                        >
                          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                        </svg>
                        <LikeCount>
                          {post.comment_count ?? 0}
                        </LikeCount>
                      </PostAction>
                    </PostActionsCenter>
                    <PostActionsEnd>
                      <SharePostButton postId={post.id} />
                    </PostActionsEnd>
                  </PostActions>
                  <PostComments
                    postId={post.id}
                    initialCount={post.comment_count ?? 0}
                    defaultExpanded={false}
                    hideToggle
                    expanded={!!commentsOpenByPost[post.id]}
                    onExpandedChange={v =>
                      setCommentsOpenByPost(prev => ({
                        ...prev,
                        [post.id]: v,
                      }))
                    }
                    flush
                    onCountChange={n => {
                      setPosts(prev =>
                        prev.map(p =>
                          p.id === post.id ? { ...p, comment_count: n } : p
                        )
                      )
                    }}
                  />
                </Post>
                </React.Fragment>
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
