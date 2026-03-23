import React, { useState, useEffect } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { jobAPI, contextAPI } from '../services/api'
import Navbar from '../components/Navbar'

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

const spin = keyframes`
  to { transform: rotate(360deg); }
`

const Container = styled.div`
  min-height: 100vh;
  width: 100%;
  background: var(--bg-light);
  animation: ${fadeIn} 0.6s ease-in;
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
`

const PostJobButton = styled.button`
  padding: 10px 20px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 400;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(10, 102, 194, 0.4);
  }

  @media (max-width: 600px) {
    padding: 8px 14px;
    font-size: 0.9em;
  }
`

const MainContent = styled.div`
  display: flex;
  width: 100%;
  gap: 24px;
  padding: 30px 20px;
  
  @media (max-width: 1024px) {
    gap: 20px;
    padding: 25px 18px;
  }
  
  @media (max-width: 900px) {
    gap: 18px;
    padding: 22px 16px;
  }
  
  @media (max-width: 768px) {
    padding: 20px 15px;
    gap: 0;
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

const SidePanel = styled.div`
  width: 280px;
  min-width: 280px;
  background: var(--bg-white);
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 24px;
  height: fit-content;
  position: sticky;
  top: 80px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  animation: ${slideUp} 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  
  @media (max-width: 1024px) {
    width: 260px;
    min-width: 260px;
    padding: 22px;
  }
  
  @media (max-width: 900px) {
    width: 240px;
    min-width: 240px;
    padding: 20px;
  }
  
  @media (max-width: 768px) {
    position: fixed;
    top: 0;
    left: ${props => props.isOpen ? '0' : '-100%'};
    height: 100vh;
    width: 280px;
    max-width: 85vw;
    z-index: 1000;
    border-radius: 0;
    transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow-y: auto;
    padding-top: 60px;
    min-width: auto;
  }
  
  @media (max-width: 480px) {
    width: 260px;
    max-width: 90vw;
    padding: 18px;
    padding-top: 55px;
  }
  
  @media (max-width: 360px) {
    width: 240px;
    max-width: 95vw;
    padding: 16px;
    padding-top: 50px;
  }
`

const SidePanelHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  
  @media (min-width: 769px) {
    display: none;
  }
`

const SidePanelTitle = styled.h2`
  font-size: 1.3em;
  color: var(--text);
  font-weight: 400;
  margin-bottom: 20px;
  letter-spacing: -0.3px;
  
  @media (max-width: 768px) {
    margin-bottom: 0;
  }
`

const CloseButtonMobile = styled.button`
  background: transparent;
  border: none;
  color: var(--text);
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: var(--hover-bg);
  }
`

const FilterOption = styled.button`
  width: 100%;
  padding: 16px 20px;
  background: ${props => props.active ? 'rgba(10, 102, 194, 0.1)' : 'transparent'};
  border: 1px solid ${props => props.active ? 'var(--primary)' : 'var(--border)'};
  border-radius: 10px;
  color: ${props => props.active ? 'var(--primary)' : 'var(--text)'};
  font-size: 1em;
  font-weight: ${props => props.active ? '500' : '400'};
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: left;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  min-height: 44px; /* Better touch target */
  
  &:hover {
    background: ${props => props.active ? 'rgba(10, 102, 194, 0.15)' : 'var(--hover-bg)'};
    border-color: ${props => props.active ? 'var(--primary)' : 'var(--border)'};
    transform: translateX(4px);
  }
  
  &:last-child {
    margin-bottom: 0;
  }
  
  svg {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
  }
  
  @media (max-width: 1024px) {
    padding: 14px 18px;
    font-size: 0.95em;
    gap: 10px;
  }
  
  @media (max-width: 768px) {
    padding: 12px 16px;
    font-size: 0.9em;
    gap: 10px;
    min-height: 42px;
    
    svg {
      width: 18px;
      height: 18px;
    }
  }
  
  @media (max-width: 480px) {
    padding: 10px 14px;
    font-size: 0.85em;
    gap: 8px;
    min-height: 40px;
    border-radius: 8px;
    
    svg {
      width: 16px;
      height: 16px;
    }
  }
  
  @media (max-width: 360px) {
    padding: 8px 12px;
    font-size: 0.8em;
    gap: 6px;
    min-height: 38px;
  }
`

const FilterCount = styled.span`
  margin-left: auto;
  padding: 4px 10px;
  background: ${props => props.active ? 'var(--primary)' : 'var(--hover-bg)'};
  color: ${props => props.active ? 'white' : 'var(--text-light)'};
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 500;
`

const MainContainer = styled.div`
  flex: 1;
  min-width: 0;
`

const MobileMenuButton = styled.button`
  display: none;
  padding: 10px;
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  align-items: center;
  justify-content: center;
  
  @media (max-width: 768px) {
    display: flex;
  }
  
  &:hover {
    background: var(--hover-bg);
    border-color: var(--primary);
  }
`

const Overlay = styled.div`
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  z-index: 999;
  animation: ${fadeIn} 0.2s ease;
  
  @media (max-width: 768px) {
    display: ${props => props.isOpen ? 'block' : 'none'};
  }
`

const JobsHeader = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  animation: ${fadeInScale} 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  
  @media (max-width: 768px) {
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 10px;
  }
  
  @media (max-width: 480px) {
    padding: 16px;
    margin-bottom: 16px;
    border-radius: 8px;
  }
  
  @media (max-width: 360px) {
    padding: 14px;
    margin-bottom: 14px;
  }
`

const JobsTitle = styled.h2`
  font-size: 1.4em;
  color: var(--text);
  font-weight: 400;
  margin-bottom: 8px;
  letter-spacing: -0.3px;
  
  @media (max-width: 768px) {
    font-size: 1.3em;
    margin-bottom: 6px;
  }
  
  @media (max-width: 480px) {
    font-size: 1.2em;
    margin-bottom: 5px;
  }
  
  @media (max-width: 360px) {
    font-size: 1.1em;
  }
`

const JobsSubtitle = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
  font-weight: 300;
  
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

const JobSearchForm = styled.form`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 16px 0 12px;
  align-items: stretch;

  @media (max-width: 480px) {
    flex-direction: column;
    margin: 14px 0 10px;
  }
`

const JobSearchInput = styled.input`
  flex: 1;
  min-width: 200px;
  padding: 12px 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 0.95em;
  color: var(--text);
  background: var(--bg-light);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;

  &::placeholder {
    color: var(--text-lighter);
  }

  &:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 2px rgba(10, 102, 194, 0.15);
  }

  @media (max-width: 480px) {
    min-width: 0;
    width: 100%;
  }
`

const JobSearchSubmit = styled.button`
  padding: 12px 22px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.95em;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(10, 102, 194, 0.35);
  }

  &:disabled {
    opacity: 0.65;
    cursor: not-allowed;
  }
`

const JobSearchClear = styled.button`
  padding: 12px 16px;
  background: transparent;
  color: var(--text-light);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: var(--primary);
    color: var(--primary);
    background: rgba(10, 102, 194, 0.04);
  }
`

const JobsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  
  @media (max-width: 768px) {
    gap: 14px;
  }
  
  @media (max-width: 480px) {
    gap: 12px;
  }
  
  @media (max-width: 360px) {
    gap: 10px;
  }
`

const JobCard = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 24px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  animation: ${slideUp} 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation-delay: ${props => props.delay || '0s'};
  animation-fill-mode: both;
  position: relative;

  &:hover {
    border-color: rgba(10, 102, 194, 0.4);
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  }
  
  @media (max-width: 768px) {
    padding: 20px;
    border-radius: 10px;
    
    &:hover {
      transform: translateY(-2px);
    }
  }
  
  @media (max-width: 480px) {
    padding: 16px;
    border-radius: 8px;
    
    &:hover {
      transform: none;
    }
  }
  
  @media (max-width: 360px) {
    padding: 14px;
    border-radius: 6px;
  }
`

const JobHeader = styled.div`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
  
  @media (max-width: 768px) {
    margin-bottom: 14px;
  }
  
  @media (max-width: 480px) {
    margin-bottom: 12px;
    flex-direction: column;
    gap: 10px;
  }
  
  @media (max-width: 360px) {
    margin-bottom: 10px;
    gap: 8px;
  }
`

const JobInfo = styled.div`
  flex: 1;
  min-width: 0;
`

const JobTitle = styled.h3`
  font-size: 1.15em;
  color: var(--text);
  font-weight: 400;
  margin-bottom: 8px;
  letter-spacing: -0.2px;
  word-wrap: break-word;
  
  @media (max-width: 768px) {
    font-size: 1.1em;
    margin-bottom: 6px;
  }
  
  @media (max-width: 480px) {
    font-size: 1.05em;
    margin-bottom: 5px;
  }
  
  @media (max-width: 360px) {
    font-size: 1em;
    margin-bottom: 4px;
  }
`

const JobCompany = styled.div`
  font-size: 0.95em;
  color: var(--text-light);
  margin-bottom: 4px;
  word-wrap: break-word;
  
  @media (max-width: 768px) {
    font-size: 0.9em;
    margin-bottom: 3px;
  }
  
  @media (max-width: 480px) {
    font-size: 0.85em;
    margin-bottom: 2px;
  }
  
  @media (max-width: 360px) {
    font-size: 0.8em;
  }
`

const JobLocation = styled.div`
  font-size: 0.85em;
  color: var(--text-lighter);
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  flex-wrap: wrap;

  svg {
    width: 14px;
    height: 14px;
    flex-shrink: 0;
  }
  
  @media (max-width: 768px) {
    font-size: 0.8em;
    margin-top: 6px;
    gap: 5px;
    
    svg {
      width: 13px;
      height: 13px;
    }
  }
  
  @media (max-width: 480px) {
    font-size: 0.75em;
    margin-top: 5px;
    gap: 4px;
    
    svg {
      width: 12px;
      height: 12px;
    }
  }
  
  @media (max-width: 360px) {
    font-size: 0.7em;
    margin-top: 4px;
  }
`

const JobMeta = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
`

const JobTag = styled.span`
  padding: 4px 12px;
  background: ${props => props.primary ? 'rgba(10, 102, 194, 0.1)' : 'var(--hover-bg)'};
  border: 1px solid ${props => props.primary ? 'rgba(10, 102, 194, 0.3)' : 'var(--border)'};
  border-radius: 12px;
  font-size: 0.8em;
  color: ${props => props.primary ? 'var(--primary)' : 'var(--text-light)'};
  font-weight: 400;
`

const MatchScore = styled.div`
  padding: 6px 12px;
  background: rgba(10, 102, 194, 0.1);
  border: 1px solid rgba(10, 102, 194, 0.3);
  border-radius: 8px;
  font-size: 0.85em;
  color: var(--primary);
  font-weight: 500;
  white-space: nowrap;
`

const LocationPriorityBadge = styled.span`
  padding: 4px 10px;
  background: ${props => {
    if (props.priority === 1) return 'rgba(34, 197, 94, 0.15)'; // City - Green
    if (props.priority === 2) return 'rgba(59, 130, 246, 0.15)'; // Country - Blue
    return 'rgba(168, 85, 247, 0.15)'; // Remote - Purple
  }};
  border: 1px solid ${props => {
    if (props.priority === 1) return 'rgba(34, 197, 94, 0.4)';
    if (props.priority === 2) return 'rgba(59, 130, 246, 0.4)';
    return 'rgba(168, 85, 247, 0.4)';
  }};
  border-radius: 6px;
  font-size: 0.75em;
  color: ${props => {
    if (props.priority === 1) return '#22c55e';
    if (props.priority === 2) return '#3b82f6';
    return '#a855f7';
  }};
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
`

const RecommendationScores = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
  font-size: 0.75em;
`

const ScoreBadge = styled.span`
  padding: 3px 8px;
  background: rgba(10, 102, 194, 0.08);
  border: 1px solid rgba(10, 102, 194, 0.2);
  border-radius: 4px;
  color: var(--text-light);
  font-weight: 400;
`

const JobDescription = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
  line-height: 1.6;
  margin-top: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`

const JobActions = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 16px;
`

const ApplyButton = styled.button`
  flex: 1;
  padding: 12px;
  background: ${props => props.applied ? 'var(--hover-bg)' : 'linear-gradient(135deg, var(--primary), var(--secondary))'};
  color: ${props => props.applied ? 'var(--text-light)' : 'white'};
  border: ${props => props.applied ? '1px solid var(--border)' : 'none'};
  border-radius: 8px;
  font-size: 0.95em;
  font-weight: 400;
  cursor: ${props => props.applied ? 'default' : 'pointer'};
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: ${props => props.applied ? 'none' : 'translateY(-2px)'};
    box-shadow: ${props => props.applied ? 'none' : '0 6px 16px rgba(10, 102, 194, 0.4)'};
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`

const SaveButton = styled.button`
  padding: 12px;
  background: ${props => props.saved ? 'rgba(10, 102, 194, 0.1)' : 'transparent'};
  color: ${props => props.saved ? 'var(--primary)' : 'var(--text-light)'};
  border: 1px solid ${props => props.saved ? 'var(--primary)' : 'var(--border)'};
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: rgba(10, 102, 194, 0.1);
    border-color: var(--primary);
    color: var(--primary);
  }
`

const LoadingSpinner = styled.div`
  width: 24px;
  height: 24px;
  border: 2px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: ${spin} 0.8s linear infinite;
  margin: 40px auto;
`

const EmptyState = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: var(--text-light);
  font-size: 0.95em;
`

const ErrorMessage = styled.div`
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 0.9em;
`

// Modal styles
const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: ${fadeIn} 0.2s ease;
`

const ModalContent = styled.div`
  background: var(--bg-white);
  border-radius: 16px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  animation: ${slideUp} 0.3s cubic-bezier(0.4, 0, 0.2, 1);
`

const ModalHeader = styled.div`
  padding: 24px 24px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
`

const ModalTitle = styled.h2`
  font-size: 1.4em;
  font-weight: 400;
  color: var(--text);
`

const CloseButton = styled.button`
  background: transparent;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
  
  &:hover {
    background: var(--hover-bg);
    color: var(--text);
  }
`

const ModalBody = styled.div`
  padding: 24px;
`

const FormGroup = styled.div`
  margin-bottom: 20px;
`

const Label = styled.label`
  display: block;
  font-size: 0.9em;
  color: var(--text);
  margin-bottom: 8px;
  font-weight: 400;
`

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 1em;
  color: var(--text);
  transition: all 0.2s;
  
  &:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(10, 102, 194, 0.1);
  }
  
  &::placeholder {
    color: var(--text-lighter);
  }
`

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 1em;
  color: var(--text);
  resize: vertical;
  min-height: 120px;
  transition: all 0.2s;
  font-family: inherit;
  
  &:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(10, 102, 194, 0.1);
  }
`

const Select = styled.select`
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 1em;
  color: var(--text);
  cursor: pointer;
  
  &:focus {
    outline: none;
    border-color: var(--primary);
  }
`

const Checkbox = styled.label`
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 0.95em;
  color: var(--text);
  
  input {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
`

const FormRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
  }
`

const SubmitButton = styled.button`
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(10, 102, 194, 0.4);
  }
  
  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
`

// Applicants Modal Styles
const ApplicantsModalOverlay = styled(ModalOverlay)`
  z-index: 2000;
`

const ApplicantsModalContent = styled(ModalContent)`
  max-width: 1400px;
  width: 95vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
  
  @media (max-width: 768px) {
    width: 100vw;
    max-height: 100vh;
  }
`

const ApplicantsHeader = styled.div`
  padding: 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  background: var(--bg-white);
  position: sticky;
  top: 0;
  z-index: 10;
`

const ApplicantsLayout = styled.div`
  display: flex;
  flex-direction: row;
  flex: 1;
  overflow: hidden;
  min-height: 0;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`

const ApplicantsLeftPanel = styled.div`
  width: 360px;
  min-width: 360px;
  border-right: 1px solid var(--border);
  background: var(--bg-light);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
  
  @media (max-width: 768px) {
    width: 100%;
    min-width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--border);
    max-height: 300px;
  }
`

const ApplicantsRightPanel = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
  background: var(--bg-white);
  min-width: 0;
`

const ApplicantsTitle = styled.h2`
  font-size: 1.5em;
  font-weight: 400;
  color: var(--text);
  margin-bottom: 8px;
`

const JobInfoSection = styled.div`
  flex: 1;
`

const JobTitleText = styled.div`
  font-size: 1.1em;
  color: var(--text-light);
  margin-bottom: 4px;
`

const ApplicantCount = styled.div`
  font-size: 0.9em;
  color: var(--text-lighter);
`

const ApplicantsList = styled.div`
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
`

const ApplicantListItem = styled.div`
  padding: 16px;
  background: ${props => props.selected ? 'var(--bg-white)' : 'transparent'};
  border: 1px solid ${props => props.selected ? 'var(--primary)' : 'var(--border)'};
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 12px;
  
  &:hover {
    background: var(--bg-white);
    border-color: ${props => props.selected ? 'var(--primary)' : 'rgba(10, 102, 194, 0.3)'};
    transform: translateX(2px);
  }
`

const ApplicantListAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
  font-size: 0.9em;
  flex-shrink: 0;
`

const ApplicantListInfo = styled.div`
  flex: 1;
  min-width: 0;
`

const ApplicantListName = styled.div`
  font-size: 0.95em;
  font-weight: ${props => props.selected ? '500' : '400'};
  color: var(--text);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`

const ApplicantListMeta = styled.div`
  font-size: 0.8em;
  color: var(--text-light);
  display: flex;
  align-items: center;
  gap: 8px;
`

const ApplicantDetailContent = styled.div`
  padding: 32px;
  flex: 1;
  max-width: 100%;
  overflow-x: hidden;
  
  @media (max-width: 768px) {
    padding: 20px;
  }
`

const ApplicantDetailSection = styled.div`
  margin-bottom: 32px;
  
  &:last-child {
    margin-bottom: 0;
  }
`

const ApplicantDetailTitle = styled.h3`
  font-size: 1.2em;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--border);
`

const ApplicantDetailInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`

const ApplicantDetailRow = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;
  
  svg {
    width: 18px;
    height: 18px;
    color: var(--text-light);
    flex-shrink: 0;
    margin-top: 2px;
  }
`

const ApplicantDetailLabel = styled.span`
  font-size: 0.9em;
  color: var(--text-light);
  font-weight: 500;
  min-width: 120px;
`

const ApplicantDetailValue = styled.div`
  font-size: 0.95em;
  color: var(--text);
  flex: 1;
  word-break: break-word;
  line-height: 1.6;
`

const ApplicantResume = styled.div`
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 24px;
  font-size: 0.95em;
  color: var(--text);
  line-height: 1.8;
  white-space: pre-wrap;
  max-height: 500px;
  overflow-y: auto;
  word-wrap: break-word;
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: var(--bg-white);
    border-radius: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 4px;
    
    &:hover {
      background: var(--text-lighter);
    }
  }
  
  &:empty::before {
    content: 'No resume available';
    color: var(--text-lighter);
    font-style: italic;
  }
`

const ProfileLinkButton = styled.button`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 8px;
  text-decoration: none;
  font-size: 0.9em;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(10, 102, 194, 0.4);
  }
  
  svg {
    width: 16px;
    height: 16px;
  }
`

const ApplicantCard = styled.div`
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: var(--primary);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
`

const ApplicantHeader = styled.div`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
`

const ApplicantInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
`

const ApplicantAvatar = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
  font-size: 1.2em;
  flex-shrink: 0;
`

const ApplicantDetails = styled.div`
  flex: 1;
`

const ApplicantName = styled.div`
  font-size: 1.1em;
  color: var(--text);
  font-weight: 500;
  margin-bottom: 4px;
`

const ApplicantMeta = styled.div`
  font-size: 0.9em;
  color: var(--text-light);
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
`

const StatusBadge = styled.span`
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 500;
  background: ${props => 
    props.status === 'accepted' ? 'rgba(34, 197, 94, 0.1)' :
    props.status === 'rejected' ? 'rgba(239, 68, 68, 0.1)' :
    'rgba(10, 102, 194, 0.1)'
  };
  color: ${props => 
    props.status === 'accepted' ? '#22c55e' :
    props.status === 'rejected' ? '#ef4444' :
    'var(--primary)'
  };
  border: 1px solid ${props => 
    props.status === 'accepted' ? 'rgba(34, 197, 94, 0.3)' :
    props.status === 'rejected' ? 'rgba(239, 68, 68, 0.3)' :
    'rgba(10, 102, 194, 0.3)'
  };
`

const ApplicantActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 16px;
`

const ActionButton = styled.button`
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9em;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid var(--border);
  background: ${props => 
    props.variant === 'accept' ? 'rgba(34, 197, 94, 0.1)' :
    props.variant === 'reject' ? 'rgba(239, 68, 68, 0.1)' :
    'transparent'
  };
  color: ${props => 
    props.variant === 'accept' ? '#22c55e' :
    props.variant === 'reject' ? '#ef4444' :
    'var(--text)'
  };
  
  &:hover:not(:disabled) {
    background: ${props => 
      props.variant === 'accept' ? 'rgba(34, 197, 94, 0.2)' :
      props.variant === 'reject' ? 'rgba(239, 68, 68, 0.2)' :
      'var(--hover-bg)'
    };
    transform: translateY(-2px);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`

const ViewApplicantsButton = styled.button`
  flex: 1;
  padding: 12px;
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
  justify-content: center;
  gap: 8px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(10, 102, 194, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
`

const ApplicantCountBadge = styled.span`
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-size: 0.85em;
  margin-left: 8px;
`

// Job Detail Side Panel Styles
const JobDetailOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1500;
  display: ${props => props.isOpen ? 'block' : 'none'};
  animation: ${fadeIn} 0.2s ease;
`

const JobDetailPanel = styled.div`
  position: fixed;
  top: 0;
  right: ${props => props.isOpen ? '0' : '-100%'};
  width: 100%;
  max-width: 600px;
  height: 100vh;
  background: var(--bg-white);
  z-index: 1501;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
  transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  
  @media (max-width: 768px) {
    max-width: 100%;
  }
`

const JobDetailHeader = styled.div`
  padding: 24px;
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  background: var(--bg-white);
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
`

const JobDetailTitle = styled.h2`
  font-size: 1.5em;
  font-weight: 400;
  color: var(--text);
  margin: 0;
  flex: 1;
`

const JobDetailCloseButton = styled.button`
  background: transparent;
  border: none;
  color: var(--text-light);
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  
  &:hover {
    background: var(--hover-bg);
    color: var(--text);
  }
  
  svg {
    width: 24px;
    height: 24px;
  }
`

const JobDetailContent = styled.div`
  padding: 24px;
  flex: 1;
`

const JobDetailSection = styled.div`
  margin-bottom: 32px;
  
  &:last-child {
    margin-bottom: 0;
  }
`

const JobDetailSectionTitle = styled.h3`
  font-size: 1.1em;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
`

const JobDetailInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`

const JobDetailInfoRow = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;
  
  svg {
    width: 18px;
    height: 18px;
    color: var(--text-light);
    flex-shrink: 0;
    margin-top: 2px;
  }
`

const JobDetailInfoLabel = styled.span`
  font-size: 0.9em;
  color: var(--text-light);
  font-weight: 500;
  min-width: 100px;
`

const JobDetailInfoValue = styled.span`
  font-size: 0.95em;
  color: var(--text);
  flex: 1;
`

const JobDetailDescription = styled.div`
  font-size: 0.95em;
  color: var(--text);
  line-height: 1.7;
  white-space: pre-wrap;
`

const JobDetailSkills = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`

const JobDetailSkillTag = styled.span`
  padding: 6px 14px;
  background: rgba(10, 102, 194, 0.1);
  border: 1px solid rgba(10, 102, 194, 0.3);
  border-radius: 12px;
  font-size: 0.85em;
  color: var(--primary);
  font-weight: 400;
`

const JobDetailActions = styled.div`
  padding: 24px;
  border-top: 1px solid var(--border);
  display: flex;
  gap: 12px;
  position: sticky;
  bottom: 0;
  background: var(--bg-white);
  z-index: 10;
`

const Jobs = () => {
  const navigate = useNavigate()
  const { user } = useAuth()

  const [allJobs, setAllJobs] = useState([])
  const [remoteJobs, setRemoteJobs] = useState([])
  const [savedJobs, setSavedJobs] = useState([])
  const [postedJobs, setPostedJobs] = useState([])
  const [recommendedJobs, setRecommendedJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [loadingRecommendations, setLoadingRecommendations] = useState(false)
  const [applyingTo, setApplyingTo] = useState(null)
  const [savingJob, setSavingJob] = useState(null)
  const [activeFilter, setActiveFilter] = useState('all')
  const [sidePanelOpen, setSidePanelOpen] = useState(false)
  
  // Job detail side panel state
  const [selectedJobDetail, setSelectedJobDetail] = useState(null)
  const [jobDetailPanelOpen, setJobDetailPanelOpen] = useState(false)
  
  // Applicants modal state
  const [selectedJob, setSelectedJob] = useState(null)
  const [applicants, setApplicants] = useState([])
  const [loadingApplicants, setLoadingApplicants] = useState(false)
  const [showApplicantsModal, setShowApplicantsModal] = useState(false)
  const [updatingStatus, setUpdatingStatus] = useState(null)
  const [selectedApplicant, setSelectedApplicant] = useState(null)
  
  // Post job modal state
  const [showPostModal, setShowPostModal] = useState(false)
  const [posting, setPosting] = useState(false)
  const [postError, setPostError] = useState(null)
  const [jobSearchInput, setJobSearchInput] = useState('')
  const [appliedJobSearch, setAppliedJobSearch] = useState('')
  const [searchJobsList, setSearchJobsList] = useState([])
  const [searchJobsLoading, setSearchJobsLoading] = useState(false)
  const [jobForm, setJobForm] = useState({
    title: '',
    description: '',
    company_name: '',
    location: '',
    job_type: 'full-time',
    is_remote: false,
    experience_level: '',
    skills_required: '',
    salary_min: '',
    salary_max: ''
  })

  const handleBackToFeed = () => {
    navigate('/feed')
  }

  // Fetch jobs
  const fetchJobs = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const [allJobsRes, remoteJobsRes, savedJobsRes, postedJobsRes] = await Promise.all([
        jobAPI.getJobs({ limit: 50 }),
        jobAPI.getRemoteJobs(50),
        jobAPI.getSavedJobs(50),
        jobAPI.getMyPostedJobs(50)
      ])
      
      setAllJobs(allJobsRes.data.jobs || [])
      setRemoteJobs(remoteJobsRes.data.jobs || [])
      setSavedJobs(savedJobsRes.data.jobs || [])
      setPostedJobs(postedJobsRes.data.jobs || [])
    } catch (err) {
      console.error('Failed to fetch jobs:', err)
      setError('Failed to load jobs. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  // Fetch job recommendations
  const fetchRecommendations = async () => {
    if (!user?.id) return
    
    setLoadingRecommendations(true)
    try {
      const res = await jobAPI.getJobRecommendations(user.id, 20)
      setRecommendedJobs(res.data?.recommendations || [])
    } catch (err) {
      console.error('Failed to fetch recommendations:', err)
      setRecommendedJobs([])
    } finally {
      setLoadingRecommendations(false)
    }
  }

  const fetchJobSearch = async (rawQuery) => {
    const q = (rawQuery || '').trim()
    if (!q) {
      setAppliedJobSearch('')
      setSearchJobsList([])
      return
    }
    setSearchJobsLoading(true)
    setError(null)
    try {
      const res = await jobAPI.getJobs({ query: q, limit: 50 })
      setSearchJobsList(res.data.jobs || [])
      setAppliedJobSearch(q)
    } catch (err) {
      console.error('Job search failed:', err)
      setError('Job search failed. Please try again.')
      setSearchJobsList([])
    } finally {
      setSearchJobsLoading(false)
    }
  }

  const handleJobSearchSubmit = e => {
    e.preventDefault()
    fetchJobSearch(jobSearchInput)
  }

  const handleClearJobSearch = () => {
    setJobSearchInput('')
    setAppliedJobSearch('')
    setSearchJobsList([])
  }

  useEffect(() => {
    fetchJobs()
  }, [])

  // Fetch recommendations when user is available and recommended filter is active
  useEffect(() => {
    if (user?.id && activeFilter === 'recommended') {
      fetchRecommendations()
    }
  }, [user?.id, activeFilter])

  // Handle apply to job
  const handleApply = async (jobId, e) => {
    e.stopPropagation()
    if (applyingTo) return
    
    setApplyingTo(jobId)
    try {
      await jobAPI.applyToJob(jobId)
      // Update local state
      const updateJobs = (jobs) => 
        jobs.map(job => 
          job.job_id === jobId ? { ...job, has_applied: true } : job
        )
      setAllJobs(updateJobs)
      setRemoteJobs(updateJobs)
      setSavedJobs(updateJobs)
      setPostedJobs(updateJobs)
      setSearchJobsList(updateJobs)
      
      // Update context for job application
      contextAPI.updateContext('apply', 'job', jobId).catch(() => {})
    } catch (err) {
      console.error('Failed to apply:', err)
      alert(err.response?.data?.detail || 'Failed to apply')
    } finally {
      setApplyingTo(null)
    }
  }

  // Handle save/unsave job
  const handleSave = async (jobId, e) => {
    e.stopPropagation()
    if (savingJob) return
    
    setSavingJob(jobId)
    try {
      const res = await jobAPI.toggleSaveJob(jobId)
      const isSaved = res.data.is_saved
      
      // Update local state
      const updateJobs = (jobs) => 
        jobs.map(job => 
          job.job_id === jobId ? { ...job, is_saved: isSaved } : job
        )
      setAllJobs(updateJobs)
      setRemoteJobs(updateJobs)
      setPostedJobs(updateJobs)
      setSearchJobsList(updateJobs)
      
      // Update saved jobs list
      if (isSaved) {
        const job = allJobs.find(j => j.job_id === jobId) || remoteJobs.find(j => j.job_id === jobId) || postedJobs.find(j => j.job_id === jobId)
        if (job) {
          setSavedJobs(prev => [{ ...job, is_saved: true }, ...prev])
        }
      } else {
        setSavedJobs(prev => prev.filter(j => j.job_id !== jobId))
      }
    } catch (err) {
      console.error('Failed to save job:', err)
    } finally {
      setSavingJob(null)
    }
  }

  // Handle post job
  const handlePostJob = async (e) => {
    e.preventDefault()
    setPosting(true)
    setPostError(null)
    
    try {
      const jobData = {
        ...jobForm,
        salary_min: jobForm.salary_min ? parseInt(jobForm.salary_min) : null,
        salary_max: jobForm.salary_max ? parseInt(jobForm.salary_max) : null,
        experience_level: jobForm.experience_level || null
      }
      
      await jobAPI.createJob(jobData)
      setShowPostModal(false)
      setJobForm({
        title: '',
        description: '',
        company_name: '',
        location: '',
        job_type: 'full-time',
        is_remote: false,
        experience_level: '',
        skills_required: '',
        salary_min: '',
        salary_max: ''
      })
      fetchJobs() // Refresh jobs
    } catch (err) {
      console.error('Failed to post job:', err)
      setPostError(err.response?.data?.detail || 'Failed to post job')
    } finally {
      setPosting(false)
    }
  }

  // Format salary
  const formatSalary = (min, max) => {
    if (!min && !max) return null
    const format = (n) => `$${(n / 1000).toFixed(0)}k`
    if (min && max) return `${format(min)} - ${format(max)}`
    if (min) return `From ${format(min)}`
    if (max) return `Up to ${format(max)}`
    return null
  }

  // Parse skills string to array
  const parseSkills = (skills) => {
    // Always return an array, even if input is invalid
    if (!skills) return []
    
    // If already an array, return it (filtered and trimmed)
    if (Array.isArray(skills)) {
      return skills.map(s => String(s).trim()).filter(Boolean)
    }
    
    // If it's a string, split by comma
    if (typeof skills === 'string') {
      const result = skills.split(',').map(s => s.trim()).filter(Boolean)
      return Array.isArray(result) ? result : []
    }
    
    // For any other type, try to convert to string first
    try {
      const result = String(skills).split(',').map(s => s.trim()).filter(Boolean)
      return Array.isArray(result) ? result : []
    } catch (e) {
      // If anything goes wrong, return empty array
      console.warn('Error parsing skills:', e, skills)
      return []
    }
  }

  // Get current jobs based on active filter
  const getCurrentJobs = () => {
    switch (activeFilter) {
      case 'saved':
        return savedJobs
      case 'remote':
        return remoteJobs
      case 'posted':
        return postedJobs
      case 'recommended':
        return recommendedJobs
      default:
        return allJobs
    }
  }

  // Get current filter title and subtitle
  const getFilterInfo = () => {
    switch (activeFilter) {
      case 'saved':
        return {
          title: 'Saved Jobs',
          subtitle: `${savedJobs.length} jobs bookmarked`
        }
      case 'remote':
        return {
          title: 'Remote Jobs',
          subtitle: `${remoteJobs.length} remote opportunities`
        }
      case 'posted':
        return {
          title: 'Posted Jobs',
          subtitle: `${postedJobs.length} jobs posted by you`
        }
      case 'recommended':
        return {
          title: 'Recommended for You',
          subtitle: loadingRecommendations 
            ? 'Loading personalized recommendations...' 
            : `${recommendedJobs.length} jobs matched to your profile`
        }
      default:
        return {
          title: 'All Jobs',
          subtitle: `${allJobs.length} opportunities available`
        }
    }
  }

  const handleFilterChange = (filter) => {
    setActiveFilter(filter)
    setSidePanelOpen(false) // Close side panel on mobile when filter is selected
  }

  // Handle view applicants
  const handleViewApplicants = async (jobId) => {
    const job = postedJobs.find(j => j.job_id === jobId)
    setSelectedJob(job)
    setShowApplicantsModal(true)
    setLoadingApplicants(true)
    setApplicants([])
    setSelectedApplicant(null)
    
    try {
      const res = await jobAPI.getJobApplicants(jobId)
      const applicantsList = res.data.applicants || res.data || []
      setApplicants(applicantsList)
      // Auto-select first applicant if available
      if (applicantsList.length > 0) {
        setSelectedApplicant(applicantsList[0])
      }
    } catch (err) {
      console.error('Failed to fetch applicants:', err)
      setError('Failed to load applicants. Please try again.')
    } finally {
      setLoadingApplicants(false)
    }
  }

  // Handle update application status
  const handleUpdateApplicationStatus = async (applicationId, status) => {
    if (updatingStatus === applicationId) return
    
    setUpdatingStatus(applicationId)
    try {
      await jobAPI.updateApplicationStatus(applicationId, status)
      // Update local state
      setApplicants(prev => 
        prev.map(app => 
          app.application_id === applicationId 
            ? { ...app, status } 
            : app
        )
      )
    } catch (err) {
      console.error('Failed to update status:', err)
      alert(err.response?.data?.detail || 'Failed to update application status')
    } finally {
      setUpdatingStatus(null)
    }
  }

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown'
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now - date)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays} days ago`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
    return date.toLocaleDateString()
  }

  // Handle job card click - open detail panel
  const handleJobCardClick = (job, e) => {
    // Only track if click is not on a button or interactive element
    if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
      return
    }
    // Set selected job and open panel
    setSelectedJobDetail(job)
    setJobDetailPanelOpen(true)
    // Track job view
    contextAPI.updateContext('view', 'job', job.job_id).catch(() => {})
  }

  // Close job detail panel
  const handleCloseJobDetailPanel = () => {
    setJobDetailPanelOpen(false)
    setSelectedJobDetail(null)
  }

  const renderJobCard = (job, index) => {
    const salary = formatSalary(job.salary_min, job.salary_max)
    const skills = parseSkills(job.skills_required)
    // Ensure skills is always an array - double check for safety
    let skillsArray = []
    if (Array.isArray(skills)) {
      skillsArray = skills
    } else if (skills) {
      // If parseSkills returned something unexpected, try to convert it
      try {
        skillsArray = Array.from(skills) || []
      } catch (e) {
        skillsArray = []
      }
    }
    
    return (
      <JobCard key={job.job_id} delay={`${index * 0.1}s`} onClick={(e) => handleJobCardClick(job, e)}>
        <JobHeader>
          <JobInfo>
            <JobTitle>{job.title}</JobTitle>
            <JobCompany>{job.company_name || job.poster_name || 'Unknown Company'}</JobCompany>
            <JobLocation>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                <circle cx="12" cy="10" r="3"></circle>
              </svg>
              {job.location || 'Location not specified'}
            </JobLocation>
          </JobInfo>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
            {job.composite_score && (
              <MatchScore>
                {Math.round(job.composite_score * 100)}% Match
              </MatchScore>
            )}
            {job.location_priority && (
              <LocationPriorityBadge priority={job.location_priority}>
                {job.location_priority === 1 ? '📍 City Match' : 
                 job.location_priority === 2 ? '🌍 Country Match' : 
                 '🌐 Remote'}
              </LocationPriorityBadge>
            )}
          </div>
        </JobHeader>
        
        <JobDescription>{job.description}</JobDescription>
        
        {/* Show recommendation scores for recommended jobs */}
        {activeFilter === 'recommended' && job.composite_score && (
          <RecommendationScores>
            <ScoreBadge>Similarity: {Math.round(job.similarity_score * 100)}%</ScoreBadge>
            <ScoreBadge>Skills: {Math.round(job.skill_match_score * 100)}%</ScoreBadge>
            <ScoreBadge>Salary: {Math.round(job.salary_match_score * 100)}%</ScoreBadge>
            <ScoreBadge>Recency: {Math.round(job.recency_score * 100)}%</ScoreBadge>
          </RecommendationScores>
        )}
        
        <JobMeta>
          <JobTag primary>{job.job_type || 'full-time'}</JobTag>
          {salary && <JobTag>{salary}</JobTag>}
          {job.is_remote && <JobTag primary>Remote</JobTag>}
          {skillsArray.length > 0 && skillsArray.slice(0, 3).map((skill, idx) => (
            <JobTag key={idx}>{skill}</JobTag>
          ))}
          {skillsArray.length > 3 && <JobTag>+{skillsArray.length - 3}</JobTag>}
        </JobMeta>
        
        <JobActions>
          {activeFilter === 'posted' ? (
            // For posted jobs, show View Applicants button
            <ViewApplicantsButton onClick={() => handleViewApplicants(job.job_id)}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
              View Applicants
              {job.application_count > 0 && (
                <ApplicantCountBadge>{job.application_count}</ApplicantCountBadge>
              )}
            </ViewApplicantsButton>
          ) : (
            // For other jobs, show Apply and Save buttons
            <>
              <ApplyButton 
                applied={job.has_applied}
                disabled={applyingTo === job.job_id || job.has_applied}
                onClick={(e) => !job.has_applied && handleApply(job.job_id, e)}
              >
                {applyingTo === job.job_id ? 'Applying...' : job.has_applied ? 'Applied' : 'Apply Now'}
              </ApplyButton>
              <SaveButton 
                saved={job.is_saved}
                disabled={savingJob === job.job_id}
                onClick={(e) => handleSave(job.job_id, e)}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill={job.is_saved ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2">
                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                </svg>
              </SaveButton>
            </>
          )}
        </JobActions>
      </JobCard>
    )
  }

  return (
    <Container>
      <Navbar />

      {error && <ErrorMessage style={{ margin: '20px' }}>{error}</ErrorMessage>}

      <Overlay isOpen={sidePanelOpen} onClick={() => setSidePanelOpen(false)} />
      <JobDetailOverlay isOpen={jobDetailPanelOpen} onClick={handleCloseJobDetailPanel} />

      <MainContent>
        <SidePanel isOpen={sidePanelOpen}>
          <SidePanelHeader>
            <SidePanelTitle>Filter Jobs</SidePanelTitle>
            <CloseButtonMobile onClick={() => setSidePanelOpen(false)}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </CloseButtonMobile>
          </SidePanelHeader>
          
          <FilterOption
            active={activeFilter === 'all'}
            onClick={() => handleFilterChange('all')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
            All Jobs
            <FilterCount active={activeFilter === 'all'}>{allJobs.length}</FilterCount>
          </FilterOption>

          <FilterOption
            active={activeFilter === 'saved'}
            onClick={() => handleFilterChange('saved')}
          >
            <svg viewBox="0 0 24 24" fill={activeFilter === 'saved' ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
            </svg>
            Saved Jobs
            <FilterCount active={activeFilter === 'saved'}>{savedJobs.length}</FilterCount>
          </FilterOption>

          <FilterOption
            active={activeFilter === 'remote'}
            onClick={() => handleFilterChange('remote')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
              <line x1="12" y1="22.08" x2="12" y2="12"></line>
            </svg>
            Remote Jobs
            <FilterCount active={activeFilter === 'remote'}>{remoteJobs.length}</FilterCount>
          </FilterOption>

          <FilterOption
            active={activeFilter === 'posted'}
            onClick={() => handleFilterChange('posted')}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            Posted Jobs
            <FilterCount active={activeFilter === 'posted'}>{postedJobs.length}</FilterCount>
          </FilterOption>

          <FilterOption
            active={activeFilter === 'recommended'}
            onClick={() => handleFilterChange('recommended')}
          >
            <svg viewBox="0 0 24 24" fill={activeFilter === 'recommended' ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
            </svg>
            Recommended
            <FilterCount active={activeFilter === 'recommended'}>
              {loadingRecommendations ? '...' : recommendedJobs.length}
            </FilterCount>
          </FilterOption>
        </SidePanel>

        <MainContainer>
          <JobsHeader>
            <JobsTitle>
              {appliedJobSearch ? 'Search results' : getFilterInfo().title}
            </JobsTitle>
            <JobSearchForm onSubmit={handleJobSearchSubmit}>
              <JobSearchInput
                type="search"
                value={jobSearchInput}
                onChange={e => setJobSearchInput(e.target.value)}
                placeholder="Search jobs — e.g. AI engineer, React developer, remote data science…"
                aria-label="Search jobs by title, skills, or description"
                autoComplete="off"
              />
              <JobSearchSubmit type="submit" disabled={searchJobsLoading}>
                {searchJobsLoading ? 'Searching…' : 'Search'}
              </JobSearchSubmit>
              {appliedJobSearch ? (
                <JobSearchClear type="button" onClick={handleClearJobSearch}>
                  Clear
                </JobSearchClear>
              ) : null}
            </JobSearchForm>
            <JobsSubtitle>
              {appliedJobSearch
                ? `${searchJobsList.length} job${searchJobsList.length !== 1 ? 's' : ''} matching “${appliedJobSearch}”`
                : getFilterInfo().subtitle}
            </JobsSubtitle>
          </JobsHeader>
          <JobsContainer>
            {appliedJobSearch
              ? searchJobsLoading
                ? <LoadingSpinner />
                : searchJobsList.length === 0
                  ? (
                    <EmptyState>
                      No jobs found for “{appliedJobSearch}”. Try different keywords or clear search to browse by category.
                    </EmptyState>
                  )
                  : searchJobsList.map((job, index) => renderJobCard(job, index))
              : loading || (activeFilter === 'recommended' && loadingRecommendations) ? (
              <LoadingSpinner />
            ) : getCurrentJobs().length === 0 ? (
              <EmptyState>
                {activeFilter === 'saved' 
                  ? 'No saved jobs yet. Bookmark jobs to find them here.'
                  : activeFilter === 'remote'
                  ? 'No remote jobs available'
                  : activeFilter === 'posted'
                  ? 'You haven\'t posted any jobs yet. Click "Post a Job" to get started.'
                  : activeFilter === 'recommended'
                  ? 'No personalized recommendations available. Update your profile and preferences to get better matches!'
                  : 'No jobs available at the moment'}
              </EmptyState>
            ) : (
              getCurrentJobs().map((job, index) => renderJobCard(job, index))
            )}
          </JobsContainer>
        </MainContainer>
      </MainContent>

      {/* Applicants Modal */}
      {showApplicantsModal && selectedJob && (
        <ApplicantsModalOverlay onClick={() => setShowApplicantsModal(false)}>
          <ApplicantsModalContent onClick={e => e.stopPropagation()}>
            <ApplicantsHeader>
              <JobInfoSection>
                <ApplicantsTitle>Applicants</ApplicantsTitle>
                <JobTitleText>{selectedJob.title}</JobTitleText>
                <ApplicantCount>
                  {applicants.length} {applicants.length === 1 ? 'applicant' : 'applicants'}
                </ApplicantCount>
              </JobInfoSection>
              <CloseButton onClick={() => setShowApplicantsModal(false)}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </CloseButton>
            </ApplicantsHeader>
            
            <ApplicantsLayout>
              {/* Left Panel - Applicant List */}
              <ApplicantsLeftPanel>
                <ApplicantsList>
                  {loadingApplicants ? (
                    <LoadingSpinner />
                  ) : applicants.length === 0 ? (
                    <EmptyState style={{ padding: '20px', textAlign: 'center' }}>
                      No applicants yet for this job posting.
                    </EmptyState>
                  ) : (
                    applicants.map((applicant) => {
                      const initials = applicant.applicant_name 
                        ? applicant.applicant_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
                        : applicant.applicant_username
                        ? applicant.applicant_username.substring(0, 2).toUpperCase()
                        : 'U'
                      
                      const isSelected = selectedApplicant && (
                        (selectedApplicant.application_id && applicant.application_id && 
                         selectedApplicant.application_id === applicant.application_id) ||
                        (selectedApplicant.applicant_id && applicant.applicant_id && 
                         selectedApplicant.applicant_id === applicant.applicant_id)
                      )
                      
                      return (
                        <ApplicantListItem
                          key={applicant.application_id || applicant.applicant_id}
                          selected={isSelected}
                          onClick={() => setSelectedApplicant(applicant)}
                        >
                          <ApplicantListAvatar>{initials}</ApplicantListAvatar>
                          <ApplicantListInfo>
                            <ApplicantListName selected={isSelected}>
                              {applicant.applicant_name || applicant.applicant_username || 'Unknown User'}
                            </ApplicantListName>
                            <ApplicantListMeta>
                              <span>{formatDate(applicant.applied_at || applicant.created_at || applicant.application_date)}</span>
                              {applicant.status && (
                                <StatusBadge status={applicant.status} style={{ fontSize: '0.75em', padding: '2px 8px' }}>
                                  {applicant.status.charAt(0).toUpperCase() + applicant.status.slice(1)}
                                </StatusBadge>
                              )}
                            </ApplicantListMeta>
                          </ApplicantListInfo>
                        </ApplicantListItem>
                      )
                    })
                  )}
                </ApplicantsList>
              </ApplicantsLeftPanel>
              
              {/* Right Panel - Applicant Details */}
              <ApplicantsRightPanel>
                {selectedApplicant ? (
                  <ApplicantDetailContent>
                    <ApplicantDetailSection>
                      <ApplicantDetailInfo>
                        <ApplicantDetailRow>
                          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                          </svg>
                          <ApplicantDetailLabel>Name:</ApplicantDetailLabel>
                          <ApplicantDetailValue>
                            {selectedApplicant.applicant_name || selectedApplicant.applicant_username || 'Unknown User'}
                          </ApplicantDetailValue>
                        </ApplicantDetailRow>
                        
                        {selectedApplicant.applicant_email && (
                          <ApplicantDetailRow>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                              <polyline points="22,6 12,13 2,6"></polyline>
                            </svg>
                            <ApplicantDetailLabel>Email:</ApplicantDetailLabel>
                            <ApplicantDetailValue>{selectedApplicant.applicant_email}</ApplicantDetailValue>
                          </ApplicantDetailRow>
                        )}
                        
                        {selectedApplicant.short_desc && (
                          <ApplicantDetailRow>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                              <polyline points="14 2 14 8 20 8"></polyline>
                              <line x1="16" y1="13" x2="8" y2="13"></line>
                              <line x1="16" y1="17" x2="8" y2="17"></line>
                            </svg>
                            <ApplicantDetailLabel>Bio:</ApplicantDetailLabel>
                            <ApplicantDetailValue>{selectedApplicant.short_desc}</ApplicantDetailValue>
                          </ApplicantDetailRow>
                        )}
                        
                        {selectedApplicant.current_status && (
                          <ApplicantDetailRow>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <circle cx="12" cy="12" r="10"></circle>
                              <polyline points="12 6 12 12 16 14"></polyline>
                            </svg>
                            <ApplicantDetailLabel>Status:</ApplicantDetailLabel>
                            <ApplicantDetailValue>{selectedApplicant.current_status}</ApplicantDetailValue>
                          </ApplicantDetailRow>
                        )}
                        
                        {selectedApplicant.role && (
                          <ApplicantDetailRow>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                              <circle cx="12" cy="7" r="4"></circle>
                            </svg>
                            <ApplicantDetailLabel>Role:</ApplicantDetailLabel>
                            <ApplicantDetailValue>{selectedApplicant.role}</ApplicantDetailValue>
                          </ApplicantDetailRow>
                        )}
                        
                        {selectedApplicant.company && (
                          <ApplicantDetailRow>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                              <circle cx="12" cy="10" r="3"></circle>
                            </svg>
                            <ApplicantDetailLabel>Company:</ApplicantDetailLabel>
                            <ApplicantDetailValue>{selectedApplicant.company}</ApplicantDetailValue>
                          </ApplicantDetailRow>
                        )}
                        
                        {selectedApplicant.location && (
                          <ApplicantDetailRow>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                              <circle cx="12" cy="10" r="3"></circle>
                            </svg>
                            <ApplicantDetailLabel>Location:</ApplicantDetailLabel>
                            <ApplicantDetailValue>{selectedApplicant.location}</ApplicantDetailValue>
                          </ApplicantDetailRow>
                        )}
                        
                        {selectedApplicant.industry && (
                          <ApplicantDetailRow>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                              <line x1="3" y1="9" x2="21" y2="9"></line>
                              <line x1="9" y1="21" x2="9" y2="9"></line>
                            </svg>
                            <ApplicantDetailLabel>Industry:</ApplicantDetailLabel>
                            <ApplicantDetailValue>{selectedApplicant.industry}</ApplicantDetailValue>
                          </ApplicantDetailRow>
                        )}
                        
                        {selectedApplicant.skills && (() => {
                          // Parse skills to ensure it's always an array
                          let applicantSkills = []
                          if (Array.isArray(selectedApplicant.skills)) {
                            applicantSkills = selectedApplicant.skills
                          } else if (typeof selectedApplicant.skills === 'string') {
                            // Try to parse as JSON first, then fall back to comma-separated
                            try {
                              const parsed = JSON.parse(selectedApplicant.skills)
                              applicantSkills = Array.isArray(parsed) ? parsed : []
                            } catch {
                              applicantSkills = selectedApplicant.skills.split(',').map(s => s.trim()).filter(Boolean)
                            }
                          }
                          return applicantSkills.length > 0 && (
                            <ApplicantDetailRow>
                              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                                <path d="M2 17l10 5 10-5"></path>
                                <path d="M2 12l10 5 10-5"></path>
                              </svg>
                              <ApplicantDetailLabel>Skills:</ApplicantDetailLabel>
                              <ApplicantDetailValue>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                  {applicantSkills.map((skill, idx) => (
                                    <JobTag key={idx}>{skill}</JobTag>
                                  ))}
                                </div>
                              </ApplicantDetailValue>
                            </ApplicantDetailRow>
                          )
                        })()}
                        
                        {selectedApplicant.profile_url && (
                          <ApplicantDetailRow>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                              <polyline points="15 3 21 3 21 9"></polyline>
                              <line x1="10" y1="14" x2="21" y2="3"></line>
                            </svg>
                            <ApplicantDetailLabel>Profile:</ApplicantDetailLabel>
                            <ApplicantDetailValue>
                              <ProfileLinkButton 
                                onClick={() => {
                                  // Extract path from full URL if needed
                                  let profilePath = selectedApplicant.profile_url
                                  if (profilePath.startsWith('http://') || profilePath.startsWith('https://')) {
                                    // Extract path from full URL
                                    try {
                                      const url = new URL(profilePath)
                                      profilePath = url.pathname
                                    } catch (e) {
                                      // If URL parsing fails, try to extract /profile/... part
                                      const match = profilePath.match(/\/profile\/[^\/]+/)
                                      if (match) {
                                        profilePath = match[0]
                                      }
                                    }
                                  }
                                  // Navigate using React Router (will use localStorage token automatically)
                                  navigate(profilePath)
                                  // Close the modal
                                  setShowApplicantsModal(false)
                                }}
                              >
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                                  <polyline points="15 3 21 3 21 9"></polyline>
                                  <line x1="10" y1="14" x2="21" y2="3"></line>
                                </svg>
                                View Profile
                              </ProfileLinkButton>
                            </ApplicantDetailValue>
                          </ApplicantDetailRow>
                        )}
                      </ApplicantDetailInfo>
                    </ApplicantDetailSection>
                    
                    {selectedApplicant.about && (
                      <ApplicantDetailSection>
                        <ApplicantDetailTitle>About</ApplicantDetailTitle>
                        <div style={{ 
                          lineHeight: '1.8', 
                          whiteSpace: 'pre-wrap', 
                          padding: '20px', 
                          background: 'var(--bg-light)', 
                          borderRadius: '8px',
                          fontSize: '0.95em',
                          color: 'var(--text)'
                        }}>
                          {selectedApplicant.about}
                        </div>
                      </ApplicantDetailSection>
                    )}
                    
                    <ApplicantDetailSection>
                      <ApplicantDetailTitle>Resume</ApplicantDetailTitle>
                      <ApplicantResume>
                        {selectedApplicant.resume || 'No resume available'}
                      </ApplicantResume>
                    </ApplicantDetailSection>
                    
                    {selectedApplicant.cover_letter && (
                      <ApplicantDetailSection>
                        <ApplicantDetailTitle>Cover Letter</ApplicantDetailTitle>
                        <div style={{ 
                          lineHeight: '1.8', 
                          whiteSpace: 'pre-wrap', 
                          padding: '20px', 
                          background: 'var(--bg-light)', 
                          borderRadius: '8px',
                          fontSize: '0.95em',
                          color: 'var(--text)'
                        }}>
                          {selectedApplicant.cover_letter}
                        </div>
                      </ApplicantDetailSection>
                    )}
                    
                    {selectedApplicant.status !== 'accepted' && selectedApplicant.status !== 'rejected' && (
                      <ApplicantDetailSection>
                        <ApplicantActions>
                          <ActionButton
                            variant="accept"
                            onClick={() => handleUpdateApplicationStatus(selectedApplicant.application_id || selectedApplicant.id, 'accepted')}
                            disabled={updatingStatus === (selectedApplicant.application_id || selectedApplicant.id)}
                          >
                            {updatingStatus === (selectedApplicant.application_id || selectedApplicant.id) ? 'Updating...' : 'Accept'}
                          </ActionButton>
                          <ActionButton
                            variant="reject"
                            onClick={() => handleUpdateApplicationStatus(selectedApplicant.application_id || selectedApplicant.id, 'rejected')}
                            disabled={updatingStatus === (selectedApplicant.application_id || selectedApplicant.id)}
                          >
                            {updatingStatus === (selectedApplicant.application_id || selectedApplicant.id) ? 'Updating...' : 'Reject'}
                          </ActionButton>
                        </ApplicantActions>
                      </ApplicantDetailSection>
                    )}
                  </ApplicantDetailContent>
                ) : (
                  <ApplicantDetailContent>
                    <EmptyState style={{ textAlign: 'center', padding: '40px' }}>
                      Select an applicant from the list to view their details
                    </EmptyState>
                  </ApplicantDetailContent>
                )}
              </ApplicantsRightPanel>
            </ApplicantsLayout>
          </ApplicantsModalContent>
        </ApplicantsModalOverlay>
      )}

      {/* Post Job Modal */}
      {showPostModal && (
        <ModalOverlay onClick={() => setShowPostModal(false)}>
          <ModalContent onClick={e => e.stopPropagation()}>
            <ModalHeader>
              <ModalTitle>Post a New Job</ModalTitle>
              <CloseButton onClick={() => setShowPostModal(false)}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </CloseButton>
            </ModalHeader>
            <ModalBody>
              {postError && <ErrorMessage>{postError}</ErrorMessage>}
              <form onSubmit={handlePostJob}>
                <FormGroup>
                  <Label>Job Title *</Label>
                  <Input
                    type="text"
                    value={jobForm.title}
                    onChange={e => setJobForm({...jobForm, title: e.target.value})}
                    placeholder="e.g. Senior Software Engineer"
                    required
                  />
                </FormGroup>
                
                <FormGroup>
                  <Label>Description *</Label>
                  <TextArea
                    value={jobForm.description}
                    onChange={e => setJobForm({...jobForm, description: e.target.value})}
                    placeholder="Describe the role, responsibilities, and requirements..."
                    required
                  />
                </FormGroup>
                
                <FormRow>
                  <FormGroup>
                    <Label>Company Name</Label>
                    <Input
                      type="text"
                      value={jobForm.company_name}
                      onChange={e => setJobForm({...jobForm, company_name: e.target.value})}
                      placeholder="Your company name"
                    />
                  </FormGroup>
                  
                  <FormGroup>
                    <Label>Location</Label>
                    <Input
                      type="text"
                      value={jobForm.location}
                      onChange={e => setJobForm({...jobForm, location: e.target.value})}
                      placeholder="e.g. San Francisco, CA or London, UK"
                    />
                    <small style={{ fontSize: '0.8em', color: 'var(--text-light)', marginTop: '4px', display: 'block' }}>
                      Format: City, State/Country (e.g., "New York, NY" or "Toronto, Canada")
                    </small>
                  </FormGroup>
                </FormRow>
                
                <FormRow>
                  <FormGroup>
                    <Label>Job Type</Label>
                    <Select
                      value={jobForm.job_type}
                      onChange={e => setJobForm({...jobForm, job_type: e.target.value})}
                    >
                      <option value="full-time">Full-time</option>
                      <option value="part-time">Part-time</option>
                      <option value="contract">Contract</option>
                      <option value="internship">Internship</option>
                    </Select>
                  </FormGroup>
                  
                  <FormGroup>
                    <Label>Experience Level</Label>
                    <Select
                      value={jobForm.experience_level}
                      onChange={e => setJobForm({...jobForm, experience_level: e.target.value})}
                    >
                      <option value="">Any</option>
                      <option value="entry">Entry Level</option>
                      <option value="mid">Mid Level</option>
                      <option value="senior">Senior Level</option>
                      <option value="lead">Lead</option>
                      <option value="executive">Executive</option>
                    </Select>
                  </FormGroup>
                </FormRow>
                
                <FormRow>
                  <FormGroup>
                    <Label>Salary Min ($)</Label>
                    <Input
                      type="number"
                      value={jobForm.salary_min}
                      onChange={e => setJobForm({...jobForm, salary_min: e.target.value})}
                      placeholder="e.g. 100000"
                    />
                  </FormGroup>
                  
                  <FormGroup>
                    <Label>Salary Max ($)</Label>
                    <Input
                      type="number"
                      value={jobForm.salary_max}
                      onChange={e => setJobForm({...jobForm, salary_max: e.target.value})}
                      placeholder="e.g. 150000"
                    />
                  </FormGroup>
                </FormRow>
                
                <FormGroup>
                  <Label>Skills Required</Label>
                  <Input
                    type="text"
                    value={jobForm.skills_required}
                    onChange={e => setJobForm({...jobForm, skills_required: e.target.value})}
                    placeholder="e.g. JavaScript, React, Node.js (comma-separated)"
                  />
                </FormGroup>
                
                <FormGroup>
                  <Checkbox>
                    <input
                      type="checkbox"
                      checked={jobForm.is_remote}
                      onChange={e => setJobForm({...jobForm, is_remote: e.target.checked})}
                    />
                    This is a remote position
                  </Checkbox>
                </FormGroup>
                
                <SubmitButton type="submit" disabled={posting}>
                  {posting ? 'Posting...' : 'Post Job'}
                </SubmitButton>
              </form>
            </ModalBody>
          </ModalContent>
        </ModalOverlay>
      )}

      {/* Job Detail Side Panel */}
      <JobDetailPanel isOpen={jobDetailPanelOpen}>
        {selectedJobDetail && (() => {
          const detailSkills = parseSkills(selectedJobDetail.skills_required)
          const detailSkillsArray = Array.isArray(detailSkills) ? detailSkills : []
          
          return (
            <>
              <JobDetailHeader>
                <JobDetailTitle>{selectedJobDetail.title}</JobDetailTitle>
                <JobDetailCloseButton onClick={handleCloseJobDetailPanel}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </JobDetailCloseButton>
              </JobDetailHeader>
              
              <JobDetailContent>
              <JobDetailSection>
                <JobDetailInfo>
                  <JobDetailInfoRow>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                      <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                    <JobDetailInfoLabel>Company:</JobDetailInfoLabel>
                    <JobDetailInfoValue>
                      {selectedJobDetail.company_name || selectedJobDetail.poster_name || 'Unknown Company'}
                    </JobDetailInfoValue>
                  </JobDetailInfoRow>
                  
                  <JobDetailInfoRow>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                      <circle cx="12" cy="10" r="3"></circle>
                    </svg>
                    <JobDetailInfoLabel>Location:</JobDetailInfoLabel>
                    <JobDetailInfoValue>
                      {selectedJobDetail.location || 'Location not specified'}
                    </JobDetailInfoValue>
                  </JobDetailInfoRow>
                  
                  <JobDetailInfoRow>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                      <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                    </svg>
                    <JobDetailInfoLabel>Job Type:</JobDetailInfoLabel>
                    <JobDetailInfoValue>
                      {selectedJobDetail.job_type ? selectedJobDetail.job_type.charAt(0).toUpperCase() + selectedJobDetail.job_type.slice(1).replace('-', ' ') : 'Full-time'}
                    </JobDetailInfoValue>
                  </JobDetailInfoRow>
                  
                  {selectedJobDetail.is_remote && (
                    <JobDetailInfoRow>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                        <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                        <line x1="12" y1="22.08" x2="12" y2="12"></line>
                      </svg>
                      <JobDetailInfoLabel>Remote:</JobDetailInfoLabel>
                      <JobDetailInfoValue>Yes</JobDetailInfoValue>
                    </JobDetailInfoRow>
                  )}
                  
                  {formatSalary(selectedJobDetail.salary_min, selectedJobDetail.salary_max) && (
                    <JobDetailInfoRow>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="12" y1="1" x2="12" y2="23"></line>
                        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                      </svg>
                      <JobDetailInfoLabel>Salary:</JobDetailInfoLabel>
                      <JobDetailInfoValue>
                        {formatSalary(selectedJobDetail.salary_min, selectedJobDetail.salary_max)}
                      </JobDetailInfoValue>
                    </JobDetailInfoRow>
                  )}
                  
                  {selectedJobDetail.experience_level && (
                    <JobDetailInfoRow>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                      </svg>
                      <JobDetailInfoLabel>Experience:</JobDetailInfoLabel>
                      <JobDetailInfoValue>
                        {selectedJobDetail.experience_level.charAt(0).toUpperCase() + selectedJobDetail.experience_level.slice(1).replace('_', ' ')}
                      </JobDetailInfoValue>
                    </JobDetailInfoRow>
                  )}
                  
                  {(selectedJobDetail.match_score || selectedJobDetail.composite_score) && (
                    <JobDetailInfoRow>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                        <path d="M2 17l10 5 10-5"></path>
                        <path d="M2 12l10 5 10-5"></path>
                      </svg>
                      <JobDetailInfoLabel>Match Score:</JobDetailInfoLabel>
                      <JobDetailInfoValue>
                        <MatchScore>
                          {selectedJobDetail.composite_score 
                            ? `${Math.round(selectedJobDetail.composite_score * 100)}% Match`
                            : `${selectedJobDetail.match_score}% Match`}
                        </MatchScore>
                      </JobDetailInfoValue>
                    </JobDetailInfoRow>
                  )}
                  
                  {/* Detailed Recommendation Scores */}
                  {selectedJobDetail.composite_score && (
                    <JobDetailInfoRow style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '12px' }}>
                      <JobDetailInfoLabel style={{ marginBottom: '8px' }}>Recommendation Breakdown:</JobDetailInfoLabel>
                      <div style={{ 
                        display: 'flex', 
                        flexDirection: 'column', 
                        gap: '8px', 
                        width: '100%',
                        padding: '12px',
                        background: 'var(--bg-light)',
                        borderRadius: '8px'
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.9em', color: 'var(--text-light)' }}>Overall Match:</span>
                          <span style={{ fontSize: '0.95em', fontWeight: '600', color: 'var(--primary)' }}>
                            {Math.round(selectedJobDetail.composite_score * 100)}%
                          </span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.9em', color: 'var(--text-light)' }}>Semantic Similarity:</span>
                          <span style={{ fontSize: '0.9em', color: 'var(--text)' }}>
                            {Math.round(selectedJobDetail.similarity_score * 100)}%
                          </span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.9em', color: 'var(--text-light)' }}>Skill Match:</span>
                          <span style={{ fontSize: '0.9em', color: 'var(--text)' }}>
                            {Math.round(selectedJobDetail.skill_match_score * 100)}%
                          </span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.9em', color: 'var(--text-light)' }}>Salary Match:</span>
                          <span style={{ fontSize: '0.9em', color: 'var(--text)' }}>
                            {Math.round(selectedJobDetail.salary_match_score * 100)}%
                          </span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.9em', color: 'var(--text-light)' }}>Recency:</span>
                          <span style={{ fontSize: '0.9em', color: 'var(--text)' }}>
                            {Math.round(selectedJobDetail.recency_score * 100)}%
                          </span>
                        </div>
                        {selectedJobDetail.location_priority && (
                          <div style={{ 
                            marginTop: '8px', 
                            paddingTop: '8px', 
                            borderTop: '1px solid var(--border)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                          }}>
                            <span style={{ fontSize: '0.9em', color: 'var(--text-light)' }}>Location Priority:</span>
                            <LocationPriorityBadge priority={selectedJobDetail.location_priority}>
                              {selectedJobDetail.location_priority === 1 ? '📍 City Match' : 
                               selectedJobDetail.location_priority === 2 ? '🌍 Country Match' : 
                               '🌐 Remote'}
                            </LocationPriorityBadge>
                          </div>
                        )}
                      </div>
                    </JobDetailInfoRow>
                  )}
                </JobDetailInfo>
              </JobDetailSection>
              
              <JobDetailSection>
                <JobDetailSectionTitle>Description</JobDetailSectionTitle>
                <JobDetailDescription>
                  {selectedJobDetail.description || 'No description provided.'}
                </JobDetailDescription>
              </JobDetailSection>
              
              {detailSkillsArray.length > 0 && (
                <JobDetailSection>
                  <JobDetailSectionTitle>Required Skills</JobDetailSectionTitle>
                  <JobDetailSkills>
                    {detailSkillsArray.map((skill, idx) => (
                      <JobDetailSkillTag key={idx}>{skill}</JobDetailSkillTag>
                    ))}
                  </JobDetailSkills>
                </JobDetailSection>
              )}
            </JobDetailContent>
            
            <JobDetailActions>
              {activeFilter === 'posted' ? (
                <ViewApplicantsButton 
                  onClick={() => {
                    handleViewApplicants(selectedJobDetail.job_id)
                    handleCloseJobDetailPanel()
                  }}
                  style={{ flex: 1 }}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                    <circle cx="9" cy="7" r="4"></circle>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                  </svg>
                  View Applicants
                  {selectedJobDetail.application_count > 0 && (
                    <ApplicantCountBadge>{selectedJobDetail.application_count}</ApplicantCountBadge>
                  )}
                </ViewApplicantsButton>
              ) : (
                <>
                  <ApplyButton 
                    applied={selectedJobDetail.has_applied}
                    disabled={applyingTo === selectedJobDetail.job_id || selectedJobDetail.has_applied}
                    onClick={(e) => {
                      e.stopPropagation()
                      if (!selectedJobDetail.has_applied) {
                        handleApply(selectedJobDetail.job_id, e)
                      }
                    }}
                    style={{ flex: 1 }}
                  >
                    {applyingTo === selectedJobDetail.job_id ? 'Applying...' : selectedJobDetail.has_applied ? 'Applied' : 'Apply Now'}
                  </ApplyButton>
                  <SaveButton 
                    saved={selectedJobDetail.is_saved}
                    disabled={savingJob === selectedJobDetail.job_id}
                    onClick={(e) => {
                      e.stopPropagation()
                      handleSave(selectedJobDetail.job_id, e)
                    }}
                  >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill={selectedJobDetail.is_saved ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2">
                      <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                    </svg>
                  </SaveButton>
                </>
              )}
            </JobDetailActions>
            </>
          )
        })()}
      </JobDetailPanel>
    </Container>
  )
}

export default Jobs
