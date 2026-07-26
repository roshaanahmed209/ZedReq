import React, { useState, useEffect } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useAccessDeniedModal } from '../contexts/AccessDeniedModalContext'
import { nemzAPI, vecAPI } from '../services/api'
import Navbar from '../components/Navbar'
import SharePostButton from '../components/SharePostButton'
import JobDetailSidePanel from '../components/JobDetailSidePanel'
import { AiFormattedChatContent } from '../utils/aiChatFormat'
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
  
  @media (max-width: 1400px) {
    grid-template-columns: 420px 1fr;
    gap: 22px;
    padding: 28px 18px;
  }
  
  @media (max-width: 1200px) {
    grid-template-columns: 400px 1fr;
    gap: 20px;
  }
  
  @media (max-width: 1024px) {
    grid-template-columns: 350px 1fr;
    gap: 20px;
    padding: 25px 15px;
  }
  
  @media (max-width: 900px) {
    grid-template-columns: 320px 1fr;
    gap: 18px;
    padding: 22px 14px;
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
    padding: 15px 12px;
    gap: 15px;
  }
  
  @media (max-width: 360px) {
    padding: 12px 10px;
    gap: 12px;
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
  
  @media (max-width: 1024px) {
    padding: 24px 24px;
  }
  
  @media (max-width: 768px) {
    padding: 20px 20px;
    border-radius: 12px 12px 0 0;
  }
  
  @media (max-width: 480px) {
    padding: 18px 16px;
    border-radius: 10px 10px 0 0;
  }
  
  @media (max-width: 360px) {
    padding: 16px 14px;
  }
`

const PageTitle = styled.h1`
  font-size: 1.5em;
  color: var(--text);
  margin-bottom: 8px;
  font-weight: 300;
  
  @media (max-width: 1024px) {
    font-size: 1.4em;
    margin-bottom: 6px;
  }
  
  @media (max-width: 768px) {
    font-size: 1.3em;
    margin-bottom: 5px;
  }
  
  @media (max-width: 600px) {
    font-size: 1.2em;
  }
  
  @media (max-width: 480px) {
    font-size: 1.1em;
    margin-bottom: 4px;
  }
  
  @media (max-width: 360px) {
    font-size: 1em;
  }
`

const PageSubtitle = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
  
  @media (max-width: 768px) {
    font-size: 0.85em;
  }
  
  @media (max-width: 480px) {
    font-size: 0.8em;
  }
  
  @media (max-width: 360px) {
    font-size: 0.75em;
  }
`

const PanelContent = styled.div`
  position: relative;
  padding: 24px 28px;
  
  @media (max-width: 1024px) {
    padding: 20px 24px;
  }
  
  @media (max-width: 768px) {
    padding: 18px 20px;
  }
  
  @media (max-width: 480px) {
    padding: 16px 18px;
  }
  
  @media (max-width: 360px) {
    padding: 14px 16px;
  }
`

const PanelSection = styled.div`
  margin-bottom: 28px;

  &:last-child {
    margin-bottom: 0;
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

const SectionTitle = styled.h3`
  font-size: 0.9em;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  
  @media (max-width: 768px) {
    font-size: 0.85em;
    margin-bottom: 14px;
  }
  
  @media (max-width: 480px) {
    font-size: 0.8em;
    margin-bottom: 12px;
  }
  
  @media (max-width: 360px) {
    font-size: 0.75em;
    margin-bottom: 10px;
  }
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
    background: rgba(21, 133, 161, 0.03);
    transform: scale(1.02);
  }
  
  @media (max-width: 768px) {
    padding: 20px;
    border-radius: 6px;
    
    &:hover {
      transform: scale(1.01);
    }
  }
  
  @media (max-width: 480px) {
    padding: 16px;
    border-radius: 6px;
    
    &:hover {
      transform: none;
    }
  }
  
  @media (max-width: 360px) {
    padding: 14px;
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
  
  @media (max-width: 768px) {
    width: 44px;
    height: 44px;
    margin-bottom: 10px;
  }
  
  @media (max-width: 480px) {
    width: 40px;
    height: 40px;
    margin-bottom: 8px;
  }
  
  @media (max-width: 360px) {
    width: 36px;
    height: 36px;
  }
`

const UploadText = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
  margin-bottom: 8px;
  
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
  }
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
  min-height: 44px; /* Better touch target */

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(21, 133, 161, 0.4);
  }

  &:active {
    transform: translateY(0);
  }
  
  @media (max-width: 768px) {
    padding: 9px 18px;
    font-size: 0.85em;
    min-height: 42px;
    margin-top: 10px;
    
    &:hover {
      transform: translateY(-1px);
    }
  }
  
  @media (max-width: 480px) {
    padding: 8px 16px;
    font-size: 0.8em;
    min-height: 40px;
    margin-top: 8px;
    border-radius: 5px;
    
    &:hover {
      transform: none;
    }
  }
  
  @media (max-width: 360px) {
    padding: 8px 14px;
    font-size: 0.75em;
    min-height: 38px;
  }
`

const JobFilterButton = styled.button`
  width: 100%;
  padding: 12px 16px;
  background: ${props => props.active ? 'rgba(21, 133, 161, 0.1)' : 'transparent'};
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
    background: rgba(21, 133, 161, 0.1);
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
  max-height: 600px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 8px;
  
  /* Custom scrollbar styling */
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: var(--bg-light);
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 3px;
    
    &:hover {
      background: var(--text-lighter);
    }
  }
  
  /* Smooth scrolling */
  scroll-behavior: smooth;
`

const MessageBubble = styled.div`
  padding: 16px 20px;
  border-radius: 12px;
  max-width: 80%;
  background: ${props => props.isUser ? 'rgba(21, 133, 161, 0.1)' : 'var(--hover-bg)'};
  border: 1px solid ${props => props.isUser ? 'rgba(21, 133, 161, 0.3)' : 'var(--border)'};
  align-self: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  animation: ${slideUp} 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  transition: all 0.2s ease;
`

const MessageText = styled.p`
  font-size: 0.95em;
  color: var(--text);
  line-height: 1.6;
  font-weight: 300;
  margin: 0;
`

const BotMessageBody = styled.div`
  font-size: 0.95em;
  color: var(--text);
  line-height: 1.65;
  font-weight: 400;

  p {
    margin: 0 0 0.85em;
    &:last-child {
      margin-bottom: 0;
    }
  }

  ol {
    margin: 0.35em 0 0.85em;
    padding-left: 1.35em;
    list-style-type: decimal;
  }

  li {
    margin-bottom: 0.55em;
    padding-left: 0.2em;
    white-space: pre-line;

    &:last-child {
      margin-bottom: 0;
    }
  }

  strong {
    font-weight: 600;
    color: var(--text);
  }
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
    box-shadow: 0 0 0 3px rgba(21, 133, 161, 0.1);
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
    box-shadow: 0 8px 20px rgba(21, 133, 161, 0.4);
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
  display: block;
  padding: 20px;
  background: var(--hover-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  animation: ${slideInFromBottom} 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  animation-delay: ${props => props.delay || '0s'};
  animation-fill-mode: both;
  color: inherit;
  outline: none;

  &:hover {
    border-color: rgba(21, 133, 161, 0.4);
    background: rgba(21, 133, 161, 0.03);
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  }

  &:focus-visible {
    box-shadow: 0 0 0 2px var(--bg-white), 0 0 0 4px rgba(21, 133, 161, 0.5);
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
  background: rgba(21, 133, 161, 0.1);
  border: 1px solid rgba(21, 133, 161, 0.3);
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

const ProfileCard = styled.a`
  display: block;
  padding: 20px;
  background: var(--hover-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  animation: ${slideInFromBottom} 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  animation-delay: ${props => props.delay || '0s'};
  animation-fill-mode: both;
  text-decoration: none;
  color: inherit;

  &:hover {
    border-color: rgba(21, 133, 161, 0.4);
    background: rgba(21, 133, 161, 0.03);
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  }
  
  &:visited {
    color: inherit;
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

const PostCardExternal = styled.a`
  display: block;
  padding: 20px;
  background: var(--hover-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  animation: ${slideInFromBottom} 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  animation-delay: ${props => props.$delay || '0s'};
  animation-fill-mode: both;
  text-decoration: none;
  color: inherit;

  &:hover {
    border-color: rgba(21, 133, 161, 0.4);
    background: rgba(21, 133, 161, 0.03);
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  }
`

const PostCard = styled(Link)`
  display: block;
  padding: 20px;
  background: var(--hover-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  animation: ${slideInFromBottom} 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  animation-delay: ${props => props.$delay || '0s'};
  animation-fill-mode: both;
  text-decoration: none;
  color: inherit;

  &:hover {
    border-color: rgba(21, 133, 161, 0.4);
    background: rgba(21, 133, 161, 0.03);
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  }

  &:visited {
    color: inherit;
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

const PrebuiltTextContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
`

const PrebuiltTextButton = styled.button`
  padding: 14px 18px;
  background: var(--bg-white);
  border: 1.5px solid var(--border);
  border-radius: 8px;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.9em;
  color: var(--text);
  font-weight: 400;
  line-height: 1.5;
  position: relative;
  overflow: hidden;

  &:hover {
    border-color: var(--primary);
    background: rgba(21, 133, 161, 0.05);
    transform: translateX(4px);
    box-shadow: 0 2px 8px rgba(21, 133, 161, 0.15);
  }

  &:active {
    transform: translateX(2px);
  }

  @media (max-width: 768px) {
    padding: 12px 16px;
    font-size: 0.85em;
  }

  @media (max-width: 480px) {
    padding: 10px 14px;
    font-size: 0.8em;
  }
`

const PrebuiltTextIcon = styled.span`
  display: inline-block;
  margin-right: 8px;
  color: var(--primary);
  font-weight: 500;
`

const UploadedFileDisplay = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(21, 133, 161, 0.05);
  border: 1px solid rgba(21, 133, 161, 0.3);
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
  const { showAccessDeniedModal } = useAccessDeniedModal()
  const [activeSection, setActiveSection] = useState('chat')
  const [message, setMessage] = useState('')
  const [jobFilter, setJobFilter] = useState('all')
  const [sessionId, setSessionId] = useState(null) // Session management
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
  const [aiJobPanelOpen, setAiJobPanelOpen] = useState(false)
  const [aiJobPanelJobId, setAiJobPanelJobId] = useState(null)
  const [aiJobPanelMatchScore, setAiJobPanelMatchScore] = useState(null)
  const [searchType, setSearchType] = useState('all') // Track what type of results we have
  const fileInputRef = React.useRef(null)
  const chatContainerRef = React.useRef(null)
  const navigate = useNavigate()
  const { logout } = useAuth()
  const [isCheckingData, setIsCheckingData] = useState(false)

  // Auto-scroll chat to bottom when new messages arrive
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }, [chatMessages, isThinking])

  // Check Qdrant collections on page load — AI Mode searches ALL jobs via vectors,
  // so empty/underfilled collections must get a FULL reindex (force=true), not last-24h.
  useEffect(() => {
    const checkAndPopulateData = async () => {
      try {
        setIsCheckingData(true)
        
        const statusResponse = await vecAPI.getStatus()
        
        if (statusResponse.data && statusResponse.data.success) {
          const totalPoints = statusResponse.data.total_points || 0
          const pointCounts = statusResponse.data.point_counts || {}
          const jobsKey = Object.keys(pointCounts).find((k) => k.includes('job')) 
            || 'nemz_jobs'
          const jobsPoints = pointCounts[jobsKey] ?? pointCounts['nemz_jobs'] ?? 0
          
          const allEmpty = Object.values(pointCounts).every((count) => count === 0) && totalPoints === 0
          const jobsEmpty = jobsPoints === 0
          
          if (allEmpty || jobsEmpty) {
            console.log(
              '[AIMode] Qdrant needs full index (allEmpty=%s, jobsPoints=%s). Triggering force sync…',
              allEmpty,
              jobsPoints
            )
            try {
              // force=true indexes ALL active jobs/users/posts — not just last 24h
              await vecAPI.syncBackground(true)
              console.log('[AIMode] Full data population triggered successfully')
            } catch (syncError) {
              console.error('[AIMode] Failed to trigger data population:', syncError)
            }
          } else {
            console.log('[AIMode] Qdrant collections have data. Point counts:', pointCounts)
            console.log('[AIMode] Total points:', totalPoints)
          }
        }
      } catch (error) {
        console.error('[AIMode] Error checking Vec agent status:', error)
      } finally {
        setIsCheckingData(false)
      }
    }
    
    checkAndPopulateData()
  }, []) // Run only on mount

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

  const handleSendMessage = async (customMessage = null) => {
    const messageToSend = customMessage || message.trim()
    if (!messageToSend) return
    
    const userMessageText = messageToSend.trim()
    
    // Add user message
    const userMessage = {
      id: Date.now(),
      text: userMessageText,
      isUser: true,
      time: "Just now"
    }
    setChatMessages(prev => [...prev, userMessage])
    if (!customMessage) {
      setMessage('')
    }
      
      // Show thinking animation
      setIsThinking(true)
      
      try {
        // Call conversational chat endpoint with session management
        // Backend handles conversation history via session (no context leakage)
        const chatResponse = await nemzAPI.chat({
          message: userMessageText,
          sessionId: sessionId // Will be null on first call, backend creates session
        })
        
        setIsThinking(false)
        
        if (chatResponse.data && chatResponse.data.success) {
          const { response, should_search, search_type, search_query, session_id } = chatResponse.data
          
          // Store session ID if provided (first message or new session)
          // This ensures conversation context is maintained per session
          if (session_id && session_id !== sessionId) {
            setSessionId(session_id)
          }
          
          // Add AI conversational response
          const botResponse = {
            id: Date.now() + 1,
            text: response,
            isUser: false,
            time: "Just now"
          }
          setChatMessages(prev => [...prev, botResponse])
          
          // If LLM decided to search, perform the search
          if (should_search && search_query) {
            setIsThinking(true)
            
            try {
              // Call Nemz API to search based on LLM's decision
              const searchResponse = await nemzAPI.searchAll({
                query: search_query,
                searchType: search_type || undefined, // Use LLM's determined search type
                limit: 10
              })
            
            setIsThinking(false)
            
            if (searchResponse.data && searchResponse.data.success) {
              const results = searchResponse.data
              const foundJobs = results.jobs || []
              const foundProfiles = results.profiles || []
              const foundPosts = results.posts || []
              const detectedType = results.search_type || 'all'
              
              setSearchType(detectedType)
              
              // Map Nemz job results to display format
              const mappedJobs = foundJobs.map((job, index) => {
                const matchScore = Math.round((job.match_score || job.score || 0) * 100)
                const jobData = job.payload || job
                const jobId = jobData.job_id ?? job.job_id ?? null

                return {
                  job_id: jobId,
                  id: jobId != null ? jobId : index + 1,
                  title: jobData.title || job.title || jobData.job_title || 'Job Title',
                  company: jobData.company_name || job.company_name || jobData.company || 'Company',
                  location: jobData.location || job.location || jobData.city || 'Location',
                  type: jobData.job_type || job.job_type || jobData.type || 'Full-time',
                  jobLink: jobData.job_link || job.job_link || '',
                  matchScore
                }
              })
              
              // Map Nemz profile results to display format
              const mappedProfiles = foundProfiles.map((profile, index) => {
                const matchScore = Math.round((profile.match_score || profile.score || 0) * 100)
                const profileData = profile.payload || profile
                
                return {
                  id: profileData.user_id || profile.user_id || profileData.id || index + 1,
                  name: profileData.name || profile.name || profileData.user_name || 'User',
                  about: profileData.about || profile.about || profileData.short_desc || '',
                  skills: profileData.skills || profile.skills || '',
                  currentStatus: profileData.current_status || profile.current_status || '',
                  profileLink: profileData.profile_link || profile.profile_link || '',
                  matchScore: matchScore
                }
              })
              
              // Map Nemz post results to display format
              const mappedPosts = foundPosts.map((post, index) => {
                const matchScore = Math.round((post.match_score || post.score || 0) * 100)
                const postData = post.payload || post
                const postId = postData.post_id ?? post.post_id ?? null
                const rawLink = postData.post_link || post.post_link || ''
                const postLink =
                  rawLink && /^https?:\/\//i.test(rawLink)
                    ? rawLink
                    : rawLink || (postId != null ? `/post/${postId}` : '')

                return {
                  post_id: postId,
                  id: postId != null ? postId : `post-${index}`,
                  description: postData.post_desc || post.post_desc || postData.description || '',
                  userName: postData.user_name || post.user_name || postData.name || 'User',
                  userId: postData.user_id || post.user_id || null,
                  postLink,
                  likes: postData.likes || post.likes || 0,
                  comments: postData.comments || post.comments || 0,
                  mediaUrl: postData.media_url || post.media_url || null,
                  mediaType: postData.media_type || post.media_type || null,
                  createdAt: postData.created_at || post.created_at || null,
                  matchScore
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
              
              const searchResultResponse = {
                id: Date.now() + 2,
                text: botResponseText,
                isUser: false,
                time: "Just now"
              }
              setChatMessages(prev => [...prev, searchResultResponse])
              
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
              const errorResponse = {
                id: Date.now() + 2,
                text: "I encountered an issue searching. Please try again or rephrase your query.",
                isUser: false,
                time: "Just now"
              }
              setChatMessages(prev => [...prev, errorResponse])
            }
          } catch (searchErr) {
            setIsThinking(false)
            console.error('Error performing search:', searchErr)
            const errorResponse = {
              id: Date.now() + 2,
              text: "I'm having trouble connecting to the search service. Please try again in a moment.",
              isUser: false,
              time: "Just now"
            }
            setChatMessages(prev => [...prev, errorResponse])
          }
        }
      }
      } catch (err) {
        setIsThinking(false)
        console.error('Error in chat:', err)
        
        let errorText = "I'm having trouble processing your message. Please try again in a moment."
        
        // Handle quota exceeded (403)
        if (err.response?.status === 403) {
          showAccessDeniedModal(err)
          return
        } else if (err.response?.status === 429) {
          errorText = "You're sending messages too quickly. Please wait a moment before trying again."
        }
        
        const errorResponse = {
          id: Date.now() + 1,
          text: errorText,
          isUser: false,
          time: "Just now"
        }
        setChatMessages(prev => [...prev, errorResponse])
    }
  }

  const handleNemzJobCardActivate = job => {
    const id = job.job_id
    if (id == null || Number.isNaN(Number(id))) {
      return
    }
    setAiJobPanelMatchScore(job.matchScore ?? null)
    setAiJobPanelJobId(Number(id))
    setAiJobPanelOpen(true)
  }

  const handleNemzJobCardKeyDown = (e, job) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleNemzJobCardActivate(job)
    }
  }

  const handleAiJobPanelJobStateChange = ({ jobId, patch }) => {
    if (!jobId || !patch) return
    setJobs(prev => prev.map(j => (j.job_id === jobId ? { ...j, ...patch } : j)))
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
              <SectionTitle>Quick Actions</SectionTitle>
              <PrebuiltTextContainer>
                <PrebuiltTextButton onClick={() => handleSendMessage("Find me jobs that match my skills and experience")}>
                  Find me jobs that match my skills and experience
                </PrebuiltTextButton>
                
                <PrebuiltTextButton onClick={() => handleSendMessage("Show me remote software engineering positions")}>
                  Show me remote software engineering positions
                </PrebuiltTextButton>
                
                <PrebuiltTextButton onClick={() => handleSendMessage("What are the best jobs for someone with my background?")}>
                  What are the best jobs for someone with my background?
                </PrebuiltTextButton>
                
                <PrebuiltTextButton onClick={() => handleSendMessage("Help me improve my resume for better job matches")}>
                  Help me improve my resume for better job matches
                </PrebuiltTextButton>
                
                <PrebuiltTextButton onClick={() => handleSendMessage("Find companies hiring in my location")}>
                  Find companies hiring in my location
                </PrebuiltTextButton>
                
                <PrebuiltTextButton onClick={() => handleSendMessage("What skills should I learn to advance my career?")}>
                  What skills should I learn to advance my career?
                </PrebuiltTextButton>
              </PrebuiltTextContainer>
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

              <ChatContainer ref={chatContainerRef}>
                {chatMessages.map((msg) => (
                  <MessageBubble key={msg.id} isUser={msg.isUser}>
                    {msg.isUser ? (
                      <MessageText>{msg.text}</MessageText>
                    ) : (
                      <BotMessageBody>
                        <AiFormattedChatContent text={msg.text} />
                      </BotMessageBody>
                    )}
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
                        <JobCard
                          key={job.id}
                          delay={`${index * 0.1}s`}
                          role="button"
                          tabIndex={0}
                          aria-label={`${job.title} at ${job.company}, ${job.matchScore}% match. Open details.`}
                          onClick={() => handleNemzJobCardActivate(job)}
                          onKeyDown={e => handleNemzJobCardKeyDown(e, job)}
                        >
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
                        <ProfileCard 
                          key={profile.id} 
                          delay={`${index * 0.1}s`}
                          href={profile.profileLink || `#`}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => {
                            if (!profile.profileLink) {
                              e.preventDefault()
                            }
                          }}
                        >
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
                      {posts.length > 0 ? posts.map((post, index) => {
                        const to = post.postLink || (post.post_id != null ? `/post/${post.post_id}` : '/feed')
                        const isExternal = /^https?:\/\//i.test(to)
                        if (isExternal) {
                          return (
                            <PostCardExternal
                              key={post.id}
                              href={to}
                              target="_blank"
                              rel="noopener noreferrer"
                              $delay={`${index * 0.1}s`}
                            >
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
                            </PostCardExternal>
                          )
                        }
                        return (
                          <PostCard key={post.id} to={to} $delay={`${index * 0.1}s`}>
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
                            {post.post_id != null && (
                              <div
                                style={{
                                  display: 'flex',
                                  justifyContent: 'flex-end',
                                  marginTop: 10,
                                }}
                                onClick={e => e.stopPropagation()}
                                onKeyDown={e => e.stopPropagation()}
                                role="presentation"
                              >
                                <SharePostButton
                                  postId={post.post_id}
                                  variant="iconOnly"
                                />
                              </div>
                            )}
                            <MatchScore>{post.matchScore}% Match</MatchScore>
                          </PostCard>
                        )
                      }) : null}
                    </PostList>
                  )}
                </ContentCard>
              )}
            </>
          )}
        </MainContent>
      </MainContainer>

      <JobDetailSidePanel
        isOpen={aiJobPanelOpen}
        jobId={aiJobPanelJobId}
        matchScoreFromSearch={aiJobPanelMatchScore}
        onClose={() => {
          setAiJobPanelOpen(false)
          setAiJobPanelJobId(null)
          setAiJobPanelMatchScore(null)
        }}
        onJobStateChange={handleAiJobPanelJobStateChange}
      />
    </Container>
  )
}

export default AIMode

