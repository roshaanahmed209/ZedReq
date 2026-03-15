import React, { useState, useEffect, useRef } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { motion, useInView } from 'framer-motion'
import { lmsAPI } from '../services/api'
import Navbar from '../components/Navbar'
import '../css/pages/LMS.css'

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`

const slideUp = keyframes`
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`

const spin = keyframes`
  from { transform: rotate(0deg); }
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
    order: -1; /* Show sidebar first on mobile */
    margin-bottom: 20px;
    border-radius: 12px;
  }
  
  @media (max-width: 600px) {
    margin-bottom: 18px;
    border-radius: 10px;
  }
  
  @media (max-width: 480px) {
    margin-bottom: 16px;
    border-radius: 10px;
  }
  
  @media (max-width: 360px) {
    margin-bottom: 14px;
    border-radius: 8px;
  }
`

const ScrollableContent = styled.div`
  max-height: calc(100vh - 270px);
  overflow-y: auto;
  
  /* Custom scrollbar */
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
  
  &::-webkit-scrollbar-thumb:hover {
    background: var(--text-lighter);
  }
`

const PanelTitle = styled.h3`
  font-size: 1.2em;
  color: var(--text);
  margin-bottom: 8px;
  font-weight: 400;
`

const PanelSubtitle = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
  margin: 0;
`

const EnrollButton = styled.button`
  padding: 8px 16px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 500;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--primary-dark);
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
`

const EnrollOverlay = styled.div`
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.78);
  backdrop-filter: blur(8px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
`

const EnrollOverlayRow = styled.div`
  display: flex;
  align-items: center;
  gap: 14px;
  overflow: hidden;
`

const EnrollOverlayText = styled.div`
  font-size: 1.25em;
  font-weight: 500;
  color: #ffffff;
  overflow: hidden;
  height: 1.6em;
  display: flex;
  align-items: center;

  span.msg {
    display: inline-block;
    animation: diceRoll 0.65s cubic-bezier(0.22, 1, 0.36, 1) both;
  }

  @keyframes diceRoll {
    0%   { transform: rotateX(90deg) translateY(-14px); opacity: 0; }
    100% { transform: rotateX(0deg)  translateY(0);     opacity: 1; }
  }
`

const EnrollDots = styled.div`
  display: flex;
  align-items: center;
  gap: 7px;
  padding-bottom: 2px;

  span {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--primary);
    animation: dotBounce 1.6s ease-in-out infinite;
  }

  span:nth-child(1) { animation-delay: 0s; }
  span:nth-child(2) { animation-delay: 0.3s; }
  span:nth-child(3) { animation-delay: 0.6s; }

  @keyframes dotBounce {
    0%, 70%, 100% { transform: translateY(0);    opacity: 0.35; }
    35%           { transform: translateY(-9px); opacity: 1;    }
  }
`

const RefreshRecsButton = styled.button`
  margin-left: auto;
  padding: 4px 10px;
  font-size: 0.78em;
  font-weight: 500;
  color: var(--primary);
  background: transparent;
  border: 1px solid var(--primary);
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 5px;

  &:hover:not(:disabled) {
    background: var(--primary);
    color: white;
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  svg.spinning {
    animation: spin 1s linear infinite;
  }
`

const EmptySubtext = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
  margin-top: 8px;
  text-align: center;
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

const ScrollGradientTop = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 50px;
  background: linear-gradient(to bottom, var(--bg-white), transparent);
  pointer-events: none;
  transition: opacity 0.3s ease;
  opacity: ${props => props.opacity || 0};
  z-index: 5;
`

const ScrollGradientBottom = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100px;
  background: linear-gradient(to top, var(--bg-white), transparent);
  pointer-events: none;
  transition: opacity 0.3s ease;
  opacity: ${props => props.opacity || 0};
  z-index: 5;
`

const MainContent = styled.main`
  min-height: 80vh;
  width: 100%;
  
  @media (max-width: 768px) {
    order: 1; /* Show main content after sidebar on mobile */
    min-height: auto;
  }
`

const TopBanner = styled.div`
  width: 100%;
  grid-column: 1 / -1;
  padding: 24px 32px;
  display: flex;
  align-items: center;
  gap: 16px;
  background: transparent;
  border: none;
  margin-bottom: 20px;

  @media (max-width: 1024px) {
    padding: 22px 28px;
    gap: 14px;
    border-radius: 14px;
  }

  @media (max-width: 768px) {
    padding: 20px 24px;
    gap: 12px;
    border-radius: 12px;
    margin-bottom: 18px;
  }

  @media (max-width: 600px) {
    padding: 18px 20px;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
  }

  @media (max-width: 480px) {
    padding: 16px;
    gap: 10px;
    border-radius: 10px;
    margin-bottom: 14px;
  }
  
  @media (max-width: 360px) {
    padding: 14px;
    gap: 8px;
    margin-bottom: 12px;
  }
`

const BannerIcon = styled.div`
  width: 56px;
  height: 56px;
  min-width: 56px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  
  svg {
    width: 32px;
    height: 32px;
    color: white;
  }
  
  @media (max-width: 768px) {
    width: 50px;
    height: 50px;
    min-width: 50px;
    border-radius: 10px;
    
    svg {
      width: 28px;
      height: 28px;
    }
  }
  
  @media (max-width: 600px) {
    width: 48px;
    height: 48px;
    min-width: 48px;
    border-radius: 10px;
    
    svg {
      width: 26px;
      height: 26px;
    }
  }
  
  @media (max-width: 480px) {
    width: 44px;
    height: 44px;
    min-width: 44px;
    border-radius: 8px;
    
    svg {
      width: 24px;
      height: 24px;
    }
  }
  
  @media (max-width: 360px) {
    width: 40px;
    height: 40px;
    min-width: 40px;
    
    svg {
      width: 22px;
      height: 22px;
    }
  }
`

const BannerContent = styled.div`
  flex: 1;
`

const BannerTitle = styled.h2`
  font-size: 1.8em;
  font-weight: 300;
  color: var(--text);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  word-wrap: break-word;

  @media (max-width: 1024px) {
    font-size: 1.6em;
    gap: 10px;
    margin-bottom: 6px;
  }

  @media (max-width: 768px) {
    font-size: 1.4em;
    gap: 8px;
    margin-bottom: 5px;
  }

  @media (max-width: 600px) {
    font-size: 1.3em;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 4px;
  }

  @media (max-width: 480px) {
    font-size: 1.2em;
    gap: 6px;
    line-height: 1.3;
  }
  
  @media (max-width: 360px) {
    font-size: 1.1em;
    gap: 5px;
  }
`

const AIBadge = styled.span`
  font-size: 0.5em;
  padding: 6px 12px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border-radius: 14px;
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`

const BannerDescription = styled.p`
  font-size: 1.1em;
  color: var(--text-light);
  line-height: 1.6;
  font-weight: 300;
  word-wrap: break-word;
  margin: 0;

  @media (max-width: 1024px) {
    font-size: 1.05em;
    line-height: 1.55;
  }

  @media (max-width: 768px) {
    font-size: 1em;
    line-height: 1.5;
  }

  @media (max-width: 600px) {
    font-size: 0.95em;
    line-height: 1.5;
  }

  @media (max-width: 480px) {
    font-size: 0.9em;
    line-height: 1.45;
  }
  
  @media (max-width: 360px) {
    font-size: 0.85em;
    line-height: 1.4;
  }
`

const DashboardContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  width: 100%;

  @media (max-width: 1024px) {
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 18px;
  }

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  @media (max-width: 600px) {
    grid-template-columns: 1fr;
    gap: 14px;
  }
  
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  @media (max-width: 360px) {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  /* Ensure all direct children (cards) are in separate rows on mobile */
  & > * {
    @media (max-width: 900px) {
      grid-column: 1 / -1;
      width: 100%;
    }
  }
`

const DashboardCard = styled.div`
  background: var(--bg-white);
  border-radius: 16px;
  border: 1px solid var(--border);
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  animation: ${slideUp} 0.4s ease-out;
  
  @media (max-width: 1024px) {
    padding: 22px;
    border-radius: 14px;
  }
  
  @media (max-width: 768px) {
    padding: 20px;
    border-radius: 12px;
  }
  
  @media (max-width: 600px) {
    padding: 18px;
    border-radius: 10px;
  }
  
  @media (max-width: 480px) {
    padding: 16px;
    border-radius: 10px;
  }
  
  @media (max-width: 360px) {
    padding: 14px;
    border-radius: 8px;
  }

  &.dashboard-card-span-2 {
    grid-column: 1 / -1;
  }
`

const CardTitle = styled.h3`
  font-size: 1.1em;
  color: var(--text);
  margin-bottom: 20px;
  font-weight: 300;
  display: flex;
  align-items: center;
  gap: 8px;
  word-wrap: break-word;
  
  @media (max-width: 1024px) {
    font-size: 1.05em;
    margin-bottom: 18px;
    gap: 7px;
  }
  
  @media (max-width: 768px) {
    font-size: 1em;
    margin-bottom: 16px;
    gap: 6px;
  }
  
  @media (max-width: 600px) {
    font-size: 0.95em;
    margin-bottom: 14px;
    gap: 6px;
  }
  
  @media (max-width: 480px) {
    font-size: 0.9em;
    margin-bottom: 12px;
    gap: 5px;
    
    svg {
      width: 18px;
      height: 18px;
    }
  }
  
  @media (max-width: 360px) {
    font-size: 0.85em;
    margin-bottom: 10px;
    
    svg {
      width: 16px;
      height: 16px;
    }
  }
`

const StatCard = styled(DashboardCard)`
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  
  @media (max-width: 480px) {
    min-height: 120px;
  }
`

const StatValue = styled.div`
  font-size: 2.5em;
  font-weight: 300;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
  line-height: 1.2;
  word-wrap: break-word;

  @media (max-width: 1024px) {
    font-size: 2.3em;
    margin-bottom: 7px;
  }
  
  @media (max-width: 768px) {
    font-size: 2.1em;
    margin-bottom: 6px;
  }

  @media (max-width: 600px) {
    font-size: 2em;
    margin-bottom: 5px;
  }

  @media (max-width: 480px) {
    font-size: 1.8em;
    margin-bottom: 4px;
  }
  
  @media (max-width: 360px) {
    font-size: 1.6em;
  }
`

const StatLabel = styled.div`
  font-size: 0.9em;
  color: var(--text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  word-wrap: break-word;
  
  @media (max-width: 768px) {
    font-size: 0.85em;
    letter-spacing: 0.4px;
  }
  
  @media (max-width: 600px) {
    font-size: 0.8em;
    letter-spacing: 0.3px;
  }
  
  @media (max-width: 480px) {
    font-size: 0.75em;
    letter-spacing: 0.3px;
  }
  
  @media (max-width: 360px) {
    font-size: 0.7em;
  }
`

const StatChange = styled.div`
  font-size: 0.85em;
  color: ${props => props.positive ? '#2ecc71' : '#e74c3c'};
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  word-wrap: break-word;
  
  @media (max-width: 768px) {
    font-size: 0.8em;
    margin-top: 6px;
    gap: 3px;
  }
  
  @media (max-width: 600px) {
    font-size: 0.75em;
    margin-top: 5px;
  }
  
  @media (max-width: 480px) {
    font-size: 0.7em;
    margin-top: 4px;
    
    svg {
      width: 14px;
      height: 14px;
    }
  }
  
  @media (max-width: 360px) {
    font-size: 0.65em;
    
    svg {
      width: 12px;
      height: 12px;
    }
  }
`

const ProgressCircle = styled.div`
  position: relative;
  width: 150px;
  height: 150px;
  margin: 20px auto;

  @media (max-width: 1024px) {
    width: 140px;
    height: 140px;
    margin: 18px auto;
  }
  
  @media (max-width: 768px) {
    width: 130px;
    height: 130px;
    margin: 16px auto;
  }

  @media (max-width: 600px) {
    width: 120px;
    height: 120px;
    margin: 14px auto;
  }

  @media (max-width: 480px) {
    width: 110px;
    height: 110px;
    margin: 12px auto;
  }
  
  @media (max-width: 360px) {
    width: 100px;
    height: 100px;
    margin: 10px auto;
  }
  
  svg {
    width: 100%;
    height: 100%;
  }
`

const CircleBackground = styled.circle`
  fill: none;
  stroke: var(--border);
  stroke-width: 10;
`

const CircleProgress = styled.circle`
  fill: none;
  stroke: url(#gradient);
  stroke-width: 10;
  stroke-linecap: round;
  transform: rotate(-90deg);
  transform-origin: 50% 50%;
  stroke-dasharray: ${props => props.circumference};
  stroke-dashoffset: ${props => props.offset};
  transition: stroke-dashoffset 1s ease;
`

const CircleText = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
`

const CircleValue = styled.div`
  font-size: 2em;
  font-weight: 300;
  color: var(--text);
  
  @media (max-width: 768px) {
    font-size: 1.8em;
  }
  
  @media (max-width: 600px) {
    font-size: 1.6em;
  }
  
  @media (max-width: 480px) {
    font-size: 1.4em;
  }
  
  @media (max-width: 360px) {
    font-size: 1.2em;
  }
`

const CircleLabel = styled.div`
  font-size: 0.8em;
  color: var(--text-light);
  
  @media (max-width: 768px) {
    font-size: 0.75em;
  }
  
  @media (max-width: 480px) {
    font-size: 0.7em;
  }
  
  @media (max-width: 360px) {
    font-size: 0.65em;
  }
`

const BarChart = styled.div`
  display: flex;
  align-items: flex-end;
  gap: 16px;
  height: 200px;
  margin-top: 20px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
`

const Bar = styled.div`
  width: 100%;
  max-width: 60px;
  min-width: 35px;
  background: linear-gradient(180deg, #00d4ff 0%, var(--primary) 50%, #004182 100%);
  border-radius: 8px 8px 0 0;
  height: ${props => props.height}%;
  transition: all 0.5s ease;
  position: relative;
  min-height: 30px;
  display: flex;
  flex-shrink: 0;
  
  @media (max-width: 768px) {
    max-width: 50px;
    min-width: 30px;
    min-height: 25px;
  }
  
  @media (max-width: 600px) {
    max-width: 45px;
    min-width: 28px;
    min-height: 20px;
  }
  
  @media (max-width: 480px) {
    max-width: 40px;
    min-width: 25px;
    min-height: 18px;
    border-radius: 6px 6px 0 0;
  }
  
  @media (max-width: 360px) {
    max-width: 35px;
    min-width: 22px;
    min-height: 15px;
  }
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  box-shadow: 0 -2px 8px rgba(10, 102, 194, 0.3), inset 0 -2px 4px rgba(255, 255, 255, 0.1);
  
  &:hover {
    opacity: 0.9;
    transform: translateY(-2px);
    box-shadow: 0 -4px 12px rgba(10, 102, 194, 0.5), inset 0 -2px 4px rgba(255, 255, 255, 0.2);
  }
`

const BarValue = styled.div`
  position: absolute;
  top: -30px;
  font-size: 0.95em;
  font-weight: 500;
  color: #ffffff;
  background: rgba(10, 102, 194, 0.8);
  padding: 4px 8px;
  border-radius: 4px;
  white-space: nowrap;
  
  @media (max-width: 768px) {
    top: -28px;
    font-size: 0.85em;
    padding: 3px 6px;
  }
  
  @media (max-width: 600px) {
    top: -26px;
    font-size: 0.8em;
    padding: 3px 5px;
  }
  
  @media (max-width: 480px) {
    top: -24px;
    font-size: 0.75em;
    padding: 2px 4px;
    border-radius: 3px;
  }
  
  @media (max-width: 360px) {
    top: -22px;
    font-size: 0.7em;
    padding: 2px 3px;
  }
`

const BarLabel = styled.div`
  font-size: 0.85em;
  color: var(--text);
  text-align: center;
  margin-top: 10px;
  font-weight: 400;
  word-wrap: break-word;
  
  @media (max-width: 768px) {
    font-size: 0.8em;
    margin-top: 8px;
  }
  
  @media (max-width: 600px) {
    font-size: 0.75em;
    margin-top: 6px;
  }
  
  @media (max-width: 480px) {
    font-size: 0.7em;
    margin-top: 5px;
  }
  
  @media (max-width: 360px) {
    font-size: 0.65em;
    margin-top: 4px;
  }
`

const WeeklyPerfHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0;
  flex-wrap: wrap;
  gap: 8px;
`

const WeeklyPerfFilters = styled.div`
  display: flex;
  gap: 6px;
`

const WeeklyPerfFilterBtn = styled.button`
  font-size: 0.78em;
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid ${props => props.active ? 'var(--primary)' : 'var(--border)'};
  background: ${props => props.active ? 'var(--primary)' : 'transparent'};
  color: ${props => props.active ? '#fff' : 'var(--text-light)'};
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 400;

  &:hover {
    border-color: var(--primary);
    color: ${props => props.active ? '#fff' : 'var(--primary)'};
  }
`

const BarChartScrollWrapper = styled.div`
  overflow-x: auto;
  width: 100%;

  /* Custom scrollbar matching theme */
  &::-webkit-scrollbar {
    height: 4px;
  }
  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.03);
    border-radius: 4px;
  }
  &::-webkit-scrollbar-thumb {
    background: var(--primary);
    border-radius: 4px;
    opacity: 0.6;
  }
  scrollbar-width: thin;
  scrollbar-color: var(--primary) transparent;
`

const DomainList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
`

const DomainItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`

const DomainHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`

const DomainName = styled.span`
  font-size: 0.9em;
  color: var(--text);
  font-weight: 300;
`

const DomainPercentage = styled.span`
  font-size: 0.85em;
  color: var(--primary);
  font-weight: 300;
`

const DomainProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: var(--border);
  border-radius: 10px;
  overflow: hidden;
`

const DomainProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  border-radius: 10px;
  width: ${props => props.width}%;
  transition: width 0.8s ease;
`

const ActivityItem = styled.div`
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: var(--hover-bg);
  margin-bottom: 12px;
  align-items: center;
  
  &:last-child {
    margin-bottom: 0;
  }
`

const ActivityIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 300;
  flex-shrink: 0;
`

const ActivityContent = styled.div`
  flex: 1;
`

const ActivityTitle = styled.div`
  font-size: 0.9em;
  color: var(--text);
  font-weight: 300;
  margin-bottom: 4px;
`

const ActivityTime = styled.div`
  font-size: 0.8em;
  color: var(--text-lighter);
`

const ActivityScrollContainer = styled.div`
  max-height: 350px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 4px;
  margin-top: 8px;
  
  /* Custom scrollbar styling */
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: var(--hover-bg);
    border-radius: 10px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--text-lighter);
    border-radius: 10px;
    
    &:hover {
      background: var(--text-light);
    }
  }
  
  @media (max-width: 768px) {
    max-height: 280px;
  }
`

const RecommendationsScrollContainer = styled.div`
  max-height: 350px;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 4px;
  margin-top: 8px;
  
  /* Custom scrollbar styling */
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: var(--hover-bg);
    border-radius: 10px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--text-lighter);
    border-radius: 10px;
    
    &:hover {
      background: var(--text-light);
    }
  }
  
  @media (max-width: 768px) {
    max-height: 280px;
  }
  
  @media (max-width: 480px) {
    max-height: 220px;
  }
`

const CoursesGrid = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`

const CourseCard = styled.div`
  background: var(--hover-bg);
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 18px;
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  gap: 14px;
  align-items: start;
  min-height: 80px; /* Better touch target */
  
  @media (max-width: 1024px) {
    padding: 16px;
    gap: 12px;
    border-radius: 10px;
  }
  
  @media (max-width: 768px) {
    padding: 14px;
    gap: 10px;
    border-radius: 8px;
  }
  
  @media (max-width: 480px) {
    padding: 12px;
    gap: 8px;
    min-height: 70px;
  }
  
  @media (max-width: 360px) {
    padding: 10px;
    gap: 6px;
    min-height: 65px;
  }
  
  &:hover {
    background: rgba(10, 102, 194, 0.1);
    border-color: var(--primary);
  }
`

const CourseIcon = styled.div`
  width: 48px;
  height: 48px;
  min-width: 48px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1em;
  font-weight: 300;
  color: white;
  letter-spacing: -0.5px;
  flex-shrink: 0;
  
  @media (max-width: 768px) {
    width: 44px;
    height: 44px;
    min-width: 44px;
    border-radius: 8px;
    font-size: 0.95em;
  }
  
  @media (max-width: 480px) {
    width: 40px;
    height: 40px;
    min-width: 40px;
    border-radius: 8px;
    font-size: 0.9em;
  }
  
  @media (max-width: 360px) {
    width: 36px;
    height: 36px;
    min-width: 36px;
    border-radius: 6px;
    font-size: 0.85em;
  }
`

const CourseContent = styled.div`
  flex: 1;
  min-width: 0;
`

const CourseTitle = styled.h3`
  font-size: 0.95em;
  color: var(--text);
  margin-bottom: 6px;
  font-weight: 300;
  word-wrap: break-word;
  line-height: 1.3;
  
  @media (max-width: 768px) {
    font-size: 0.9em;
    margin-bottom: 5px;
    line-height: 1.3;
  }
  
  @media (max-width: 480px) {
    font-size: 0.85em;
    margin-bottom: 4px;
    line-height: 1.25;
  }
  
  @media (max-width: 360px) {
    font-size: 0.8em;
    margin-bottom: 3px;
  }
`

const CourseDescription = styled.p`
  color: var(--text-light);
  font-size: 0.8em;
  line-height: 1.4;
  margin-bottom: 10px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-wrap: break-word;
  
  @media (max-width: 768px) {
    font-size: 0.75em;
    line-height: 1.4;
    margin-bottom: 8px;
    -webkit-line-clamp: 2;
  }
  
  @media (max-width: 480px) {
    font-size: 0.7em;
    line-height: 1.35;
    margin-bottom: 6px;
    -webkit-line-clamp: 2;
  }
  
  @media (max-width: 360px) {
    font-size: 0.65em;
    margin-bottom: 5px;
  }
`

const CourseFooter = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  
  @media (max-width: 480px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
`

const CourseInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.75em;
  color: var(--text-lighter);
  flex-wrap: wrap;
  
  @media (max-width: 768px) {
    gap: 10px;
    font-size: 0.7em;
  }
  
  @media (max-width: 480px) {
    gap: 8px;
    font-size: 0.65em;
    width: 100%;
  }
  
  @media (max-width: 360px) {
    gap: 6px;
    font-size: 0.6em;
  }
`

const InfoItem = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  
  svg {
    width: 14px;
    height: 14px;
  }
`

const CourseMeta = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
`

const CourseCategory = styled.span`
  font-size: 0.75em;
  color: var(--text-light);
  background: var(--hover-bg);
  padding: 4px 8px;
  border-radius: 4px;
`

const CourseDifficulty = styled.span`
  font-size: 0.75em;
  color: var(--text-light);
  background: var(--hover-bg);
  padding: 4px 8px;
  border-radius: 4px;
`

const CourseAction = styled.div`
  display: flex;
  align-items: center;
  margin-top: 8px;
`

const ProgressBar = styled.div`
  width: 100%;
  height: 4px;
  background: var(--border);
  border-radius: 10px;
  overflow: hidden;
  margin-top: 8px;
`

const ProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  border-radius: 10px;
  width: ${props => props.progress || 0}%;
  transition: width 0.3s ease;
`

const TabContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
`

const Tab = styled.button`
  padding: 14px 18px;
  background: ${props => props.active ? 'rgba(10, 102, 194, 0.1)' : 'transparent'};
  border: 1px solid ${props => props.active ? 'var(--primary)' : 'var(--border)'};
  border-radius: 8px;
  color: ${props => props.active ? 'var(--primary)' : 'var(--text-light)'};
  font-size: 0.9em;
  font-weight: 300;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  min-height: 44px; /* Better touch target */
  word-wrap: break-word;
  
  &:hover {
    background: rgba(10, 102, 194, 0.1);
    border-color: var(--primary);
    color: var(--primary);
  }
  
  @media (max-width: 1024px) {
    padding: 12px 16px;
    font-size: 0.85em;
    min-height: 42px;
  }
  
  @media (max-width: 768px) {
    padding: 12px 14px;
    font-size: 0.85em;
    border-radius: 6px;
  }
  
  @media (max-width: 480px) {
    padding: 10px 12px;
    font-size: 0.8em;
    min-height: 40px;
    border-radius: 6px;
  }
  
  @media (max-width: 360px) {
    padding: 10px;
    font-size: 0.75em;
    min-height: 38px;
  }
`

const EmptyState = styled.div`
  text-align: center;
  padding: 40px 20px;
  color: var(--text-light);
`

const EmptyIcon = styled.div`
  width: 60px;
  height: 60px;
  margin: 0 auto 12px;
  opacity: 0.5;
  
  svg {
    width: 100%;
    height: 100%;
    color: var(--text-light);
  }
`

const EmptyText = styled.p`
  font-size: 0.9em;
`

const PortalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(10px) saturate(120%);
  -webkit-backdrop-filter: blur(10px) saturate(120%);
  z-index: 1000;
  opacity: ${props => props.isOpen ? 1 : 0};
  visibility: ${props => props.isOpen ? 'visible' : 'hidden'};
  transition: opacity 0.3s ease, visibility 0.3s ease, backdrop-filter 0.3s ease;
`

const PortalContainer = styled.div`
  position: fixed;
  top: 50%;
  left: 50%;
  width: 90vw;
  max-width: 1400px;
  max-height: 85vh;
  background: var(--bg-white);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1);
  transform: ${props => props.isOpen ? 'translate(-50%, -50%) scale(1)' : 'translate(-50%, -50%) scale(0.9)'};
  opacity: ${props => props.isOpen ? 1 : 0};
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.4s ease;
  z-index: 1001;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  visibility: ${props => props.isOpen ? 'visible' : 'hidden'};

  @media (max-width: 1024px) {
    width: 92vw;
    max-width: 100%;
  }

  @media (max-width: 768px) {
    width: 95vw;
    max-height: 90vh;
  }

  @media (max-width: 480px) {
    width: 98vw;
    max-height: 95vh;
    border-radius: 12px;
  }
`

const PortalHeader = styled.div`
  padding: 24px 28px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-white);
  border-radius: 16px 16px 0 0;
  flex-shrink: 0;

  @media (max-width: 768px) {
    padding: 20px 24px;
  }

  @media (max-width: 480px) {
    padding: 16px 20px;
    border-radius: 12px 12px 0 0;
  }
`

const PortalTitle = styled.h2`
  font-size: 1.5em;
  font-weight: 300;
  color: var(--text);
  margin: 0;

  @media (max-width: 768px) {
    font-size: 1.35em;
  }

  @media (max-width: 480px) {
    font-size: 1.2em;
  }
`

const CloseButton = styled.button`
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: var(--text-light);
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  &:hover {
    background: var(--hover-bg);
    color: var(--text);
  }

  svg {
    width: 24px;
    height: 24px;
  }
`

const PortalContent = styled.div`
  flex: 1;
  display: flex;
  overflow: hidden;

  @media (max-width: 768px) {
    flex-direction: column;
  }
`

const PortalSidePanel = styled.div`
  width: 280px;
  background: var(--hover-bg);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  flex-shrink: 0;

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
  
  &::-webkit-scrollbar-thumb:hover {
    background: var(--text-lighter);
  }

  @media (max-width: 1024px) {
    width: 250px;
  }

  @media (max-width: 768px) {
    width: 100%;
    max-height: 200px;
    border-right: none;
    border-bottom: 1px solid var(--border);
    overflow-x: auto;
  }

  @media (max-width: 480px) {
    max-height: 180px;
  }
`

const PortalMainContent = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 28px;
  min-width: 0;

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
  
  &::-webkit-scrollbar-thumb:hover {
    background: var(--text-lighter);
  }

  @media (max-width: 768px) {
    padding: 24px;
  }

  @media (max-width: 480px) {
    padding: 16px;
  }
`

const SidePanelSection = styled.div`
  padding: 20px;
  border-bottom: 1px solid var(--border);

  &:last-child {
    border-bottom: none;
  }

  @media (max-width: 768px) {
    padding: 16px;
  }

  @media (max-width: 480px) {
    padding: 12px 16px;
  }
`

const SidePanelTitle = styled.h3`
  font-size: 0.9em;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;

  @media (max-width: 768px) {
    font-size: 0.85em;
    margin-bottom: 10px;
  }

  @media (max-width: 480px) {
    font-size: 0.8em;
    margin-bottom: 8px;
  }
`

const SidePanelItem = styled.div`
  padding: 10px 12px;
  margin-bottom: 8px;
  background: ${props => props.active ? 'rgba(10, 102, 194, 0.1)' : 'transparent'};
  border: 1px solid ${props => props.active ? 'var(--primary)' : 'transparent'};
  border-radius: 6px;
  color: ${props => props.active ? 'var(--primary)' : 'var(--text-light)'};
  font-size: 0.9em;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(10, 102, 194, 0.1);
    border-color: var(--primary);
    color: var(--primary);
  }

  @media (max-width: 768px) {
    padding: 8px 10px;
    margin-bottom: 6px;
    font-size: 0.875em;
  }

  @media (max-width: 480px) {
    padding: 7px 10px;
    font-size: 0.85em;
  }
`

const ResourcesScrollContainer = styled.div`
  max-height: 260px;
  overflow-y: auto;
  padding-right: 4px;

  &::-webkit-scrollbar {
    width: 5px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
    border-radius: 10px;
  }

  &::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 10px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: var(--text-lighter);
  }

  /* Firefox */
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
`

const ProgressIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
`

const ProgressDot = styled.div`
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: ${props => props.completed ? 'var(--primary)' : 'var(--border)'};
`

const GenerateQuestionsButton = styled.button`
  width: calc(100% - 40px);
  margin: 20px;
  padding: 12px 20px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.95em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(10, 102, 194, 0.3);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  svg {
    width: 18px;
    height: 18px;
    
    &[style*="animation"] {
      animation: ${spin} 1s linear infinite;
    }
  }

  @media (max-width: 768px) {
    width: calc(100% - 32px);
    margin: 16px;
    padding: 10px 16px;
    font-size: 0.9em;
  }

  @media (max-width: 480px) {
    width: calc(100% - 32px);
    margin: 12px 16px;
    padding: 10px 14px;
    font-size: 0.85em;
  }
`

const QuestionSection = styled.div`
  margin-bottom: 32px;

  @media (max-width: 768px) {
    margin-bottom: 24px;
  }

  @media (max-width: 480px) {
    margin-bottom: 20px;
  }
`

const QuestionLabel = styled.label`
  display: block;
  font-size: 1em;
  font-weight: 400;
  color: var(--text);
  margin-bottom: 12px;
  line-height: 1.5;

  @media (max-width: 768px) {
    font-size: 0.95em;
    margin-bottom: 10px;
  }

  @media (max-width: 480px) {
    font-size: 0.9em;
    margin-bottom: 8px;
    line-height: 1.4;
  }
`

const QuestionNumber = styled.span`
  color: var(--primary);
  font-weight: 500;
  margin-right: 8px;
`

const AnswerInput = styled.textarea`
  width: 100%;
  min-height: 120px;
  padding: 14px 16px;
  background: var(--hover-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  font-size: 0.95em;
  font-family: inherit;
  resize: vertical;
  transition: all 0.2s ease;
  box-sizing: border-box;

  &:focus {
    outline: none;
    border-color: var(--primary);
    background: var(--bg-white);
    box-shadow: 0 0 0 3px rgba(10, 102, 194, 0.1);
  }

  &::placeholder {
    color: var(--text-lighter);
  }

  @media (max-width: 768px) {
    min-height: 100px;
    padding: 12px 14px;
    font-size: 0.9em;
  }

  @media (max-width: 480px) {
    min-height: 90px;
    padding: 10px 12px;
    font-size: 0.875em;
  }
`

const ButtonContainer = styled.div`
  display: flex;
  gap: 16px;
  margin-top: 20px;

  @media (max-width: 768px) {
    gap: 12px;
    margin-top: 16px;
  }

  @media (max-width: 600px) {
    flex-direction: column;
    gap: 12px;
  }
`

const SubmitButton = styled.button`
  flex: 1;
  padding: 14px 24px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1em;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(10, 102, 194, 0.3);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.45;
    cursor: not-allowed;
    background: var(--border, #555);
    box-shadow: none;
    transform: none;
  }

  @media (max-width: 768px) {
    padding: 12px 20px;
    font-size: 0.95em;
  }

  @media (max-width: 480px) {
    padding: 11px 18px;
    font-size: 0.9em;
  }
`

const EvaluateButton = styled.button`
  flex: 1;
  padding: 14px 24px;
  background: transparent;
  color: var(--primary);
  border: 2px solid var(--primary);
  border-radius: 8px;
  font-size: 1em;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: rgba(10, 102, 194, 0.1);
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(10, 102, 194, 0.2);
  }

  &:active {
    transform: translateY(0);
  }

  @media (max-width: 768px) {
    padding: 12px 20px;
    font-size: 0.95em;
  }

  @media (max-width: 480px) {
    padding: 11px 18px;
    font-size: 0.9em;
  }
`

const PortalProgressWrapper = styled.div`
  margin-bottom: 20px;
`

const PortalProgressLabel = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85em;
  color: var(--text-light);
  margin-bottom: 6px;
`

const PortalProgressTrack = styled.div`
  width: 100%;
  height: 8px;
  background: var(--hover-bg);
  border-radius: 10px;
  overflow: hidden;
`

const PortalProgressFill = styled.div`
  height: 100%;
  border-radius: 10px;
  background: linear-gradient(90deg, var(--primary), var(--secondary));
  transition: width 0.4s ease;
  width: ${props => props.progress || 0}%;
`

const PortalCourseInfo = styled.div`
  background: rgba(10, 102, 194, 0.1);
  border: 1px solid rgba(10, 102, 194, 0.2);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 28px;

  @media (max-width: 768px) {
    padding: 14px;
    margin-bottom: 20px;
  }

  @media (max-width: 480px) {
    padding: 12px;
    margin-bottom: 16px;
  }
`

const PortalCourseInfoText = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
  margin: 4px 0;
  display: flex;
  align-items: center;
  gap: 8px;

  svg {
    width: 16px;
    height: 16px;
    color: var(--primary);
    flex-shrink: 0;
  }

  @media (max-width: 768px) {
    font-size: 0.875em;
    gap: 6px;

    svg {
      width: 15px;
      height: 15px;
    }
  }

  @media (max-width: 480px) {
    font-size: 0.85em;

    svg {
      width: 14px;
      height: 14px;
    }
  }
`

const AnimatedCourseCard = ({ course, index, onCourseClick }) => {
  const ref = useRef(null)
  const inView = useInView(ref, { amount: 0.5, triggerOnce: false })
  
  return (
    <motion.div
      ref={ref}
      initial={{ scale: 0.7, opacity: 0 }}
      animate={inView ? { scale: 1, opacity: 1 } : { scale: 0.7, opacity: 0 }}
      transition={{ duration: 0.2, delay: 0.1 }}
    >
      <CourseCard onClick={() => onCourseClick(course)}>
        <CourseIcon>{course.icon}</CourseIcon>
        <CourseContent>
          <CourseTitle>{course.title}</CourseTitle>
          <CourseDescription>{course.description}</CourseDescription>
          {course.progress > 0 && (
            <ProgressBar>
              <ProgressFill progress={course.progress} />
            </ProgressBar>
          )}
        </CourseContent>
      </CourseCard>
    </motion.div>
  )
}

// ---------------------------------------------------------------------------
// Rate-limit constants — module-level so they are never re-declared per render
// ---------------------------------------------------------------------------
const MAX_RECS_REFRESHES = 3
const MAX_GENERATE_QUESTIONS = 3

/**
 * usePersistentCounter
 * A small custom hook that keeps a numeric counter in both React state and
 * localStorage so the value survives page refreshes and logout/login cycles.
 *
 * @param {string}  key  - localStorage key (should be user-scoped by the caller)
 * @param {number}  max  - upper bound; stored value is clamped to [0, max]
 * @returns {[number, (updater: number | ((prev: number) => number)) => void]}
 */
function usePersistentCounter(key, max) {
  const [count, _setCount] = useState(() => {
    const raw = parseInt(localStorage.getItem(key) || '0', 10)
    // Clamp to [0, max] to neutralise any manual localStorage tampering
    return Math.min(Math.max(0, isNaN(raw) ? 0 : raw), max)
  })

  const setCount = React.useCallback((updater) => {
    _setCount(prev => {
      const next = typeof updater === 'function' ? updater(prev) : updater
      const clamped = Math.min(Math.max(0, next), max)
      localStorage.setItem(key, String(clamped))
      return clamped
    })
  }, [key, max]) // eslint-disable-line react-hooks/exhaustive-deps

  return [count, setCount]
}

const LMS = () => {
  const [activeTab, setActiveTab] = useState('all')
  const [topGradientOpacity, setTopGradientOpacity] = useState(0)
  const [bottomGradientOpacity, setBottomGradientOpacity] = useState(1)
  const [selectedCourse, setSelectedCourse] = useState(null)
  const [isPortalOpen, setIsPortalOpen] = useState(false)
  const scrollRef = useRef(null)
  const navigate = useNavigate()
  const { logout, user: authUser } = useAuth()

  // State for API data
  const [courses, setCourses] = useState([])
  const [dashboard, setDashboard] = useState(null)
  const [weeklyPerformance, setWeeklyPerformance] = useState([])
  const [domainPerformance, setDomainPerformance] = useState([])
  const [activities, setActivities] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [deadlines, setDeadlines] = useState([])
  const [certificates, setCertificates] = useState([])
  const [courseQuestions, setCourseQuestions] = useState([])
  const [courseSections, setCourseSections] = useState([])
  const [courseResources, setCourseResources] = useState([])
  const [selectedSectionId, setSelectedSectionId] = useState(null)
  const [answers, setAnswers] = useState({}) // questionId -> answer text
  const [sectionPerf, setSectionPerf] = useState([])  // [{section_id, title, questions_answered, accuracy_percentage}]
  const [currentPage, setCurrentPage] = useState(0)   // 0-based page index, 5 questions per page
  const [enrollingLoading, setEnrollingLoading] = useState(false)
  const [enrollingMessage, setEnrollingMessage] = useState('')
  const [weeklyPerfDays, setWeeklyPerfDays] = useState(7)
  const [weeklyPerfLoading, setWeeklyPerfLoading] = useState(false)

  // Derived: title of the currently selected section (avoids repeated .find() in JSX)
  const selectedSectionTitle = (courseSections.find(s => s.id === selectedSectionId)?.title) || ''

  /**
   * Returns true if the given section is locked (user has not passed the previous level).
   * Basic (index 0) is always unlocked.
   * Subsequent levels require >= 20 questions answered AND >= 50% accuracy on the prior level.
   */
  const isSectionLocked = (section) => {
    const idx = courseSections.findIndex(s => s.id === section.id)
    if (idx <= 0) return false // Basic always open
    const prevSection = courseSections[idx - 1]
    const prevPerf = sectionPerf.find(p => p.section_id === prevSection.id)
    if (!prevPerf) return true
    return prevPerf.questions_answered < 20 || prevPerf.accuracy_percentage < 50
  }

  /**
   * Shared helper — fetches questions for a given course+section and updates state.
   * Reused by fetchCourseDetails and handleSectionSelect to avoid duplicating logic.
   */
  const fetchSectionQuestions = async (courseId, sectionId) => {
    try {
      const questionsRes = await lmsAPI.getCourseQuestions(courseId, sectionId)
      if (questionsRes.data && questionsRes.data.questions) {
        setCourseQuestions(questionsRes.data.questions)
        return questionsRes.data.questions.length
      }
      setCourseQuestions([])
      return 0
    } catch (err) {
      console.error(`[LMS] fetchSectionQuestions: Error for course=${courseId}, section=${sectionId}:`, err)
      setCourseQuestions([])
      return 0
    }
  }

  // Loading and error states
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [questionsLoading, setQuestionsLoading] = useState(false)
  const [refreshingRecs, setRefreshingRecs] = useState(false)

  // Persistent rate-limit counters — scoped per user, clamped, tamper-resistant
  // Keys are memoised so they never change identity mid-session
  const recsKey = React.useMemo(
    () => authUser?.id ? `lms_recs_refresh_count_${authUser.id}` : null,
    [authUser?.id]
  )
  const genKey = React.useMemo(
    () => authUser?.id ? `lms_gen_questions_count_${authUser.id}` : null,
    [authUser?.id]
  )
  const [recsRefreshCount, setRecsRefreshCount] = usePersistentCounter(recsKey ?? '__noop__', MAX_RECS_REFRESHES)
  const [generateQuestionsCount, setGenerateQuestionsCount] = usePersistentCounter(genKey ?? '__noop__', MAX_GENERATE_QUESTIONS)

  // Fetch all data on component mount
  useEffect(() => {
    console.log('[LMS] ===== PAGE LOAD: LMS page mounted, fetching all data =====')
    fetchAllData()
  }, [])

  const fetchAllData = async () => {
    const startTime = performance.now()
    console.log('[LMS] ===== fetchAllData START: Fetching all LMS data (single combined call) =====')
    
    try {
      setLoading(true)
      setError(null)

      // Single API call replaces the previous 8 parallel calls
      const response = await lmsAPI.getDashboardAll()
      
      const fetchTime = performance.now() - startTime
      console.log(`[LMS] fetchAllData: Combined API call completed in ${fetchTime.toFixed(2)}ms`)

      const data = response.data
      if (!data) {
        throw new Error('Empty response from dashboard/all endpoint')
      }

      // Set courses
      const coursesData = data.courses?.courses || []
      if (Array.isArray(coursesData) && coursesData.length > 0) {
        const mappedCourses = coursesData.map(course => {
          // Backend returns LMSUserCourse with course data in flat structure:
          // course_title, course_icon, course_description, course_lessons, course_duration
          // OR nested course object
          const title = course.course_title || course.title || 'Untitled Course'
          const icon = course.course_icon || course.icon || (title ? title.substring(0, 2).toUpperCase() : 'CO')
          const description = course.course_description || course.description || ''
          const lessons = course.course_lessons !== undefined ? course.course_lessons : (course.lessons || 0)
          const duration = course.course_duration || course.duration || 'N/A'
          const category = course.course_category || course.category || 'General'
          const difficulty = course.course_difficulty || course.difficulty || 'beginner'
          
          return {
            id: course.course_id || course.id,
            title: title,
            description: description,
            icon: icon,
            lessons: lessons,
            duration: duration,
            progress: course.progress || 0,
            status: course.status || 'not_started',
            category: category,
            difficulty: difficulty
          }
        })
        setCourses(mappedCourses)
        console.log(`[LMS] fetchAllData: SUCCESS - Loaded ${mappedCourses.length} courses`)
      } else {
        setCourses([])
        console.log('[LMS] fetchAllData: No courses found for user (empty array)')
      }

      // Set dashboard
      if (data.dashboard) {
        setDashboard(data.dashboard)
        console.log('[LMS] fetchAllData: SUCCESS - Dashboard loaded')
      }

      // Set weekly performance
      if (data.weekly_performance?.performance) {
        setWeeklyPerformance(data.weekly_performance.performance)
        console.log(`[LMS] fetchAllData: SUCCESS - Weekly performance loaded (${data.weekly_performance.performance.length} entries)`)
      }

      // Set domain performance
      if (data.domain_performance?.domains) {
        setDomainPerformance(data.domain_performance.domains)
        console.log(`[LMS] fetchAllData: SUCCESS - Domain performance loaded (${data.domain_performance.domains.length} entries)`)
      }

      // Set activities
      if (data.activities?.activities) {
        setActivities(data.activities.activities)
        console.log(`[LMS] fetchAllData: SUCCESS - Activities loaded (${data.activities.activities.length} entries)`)
      }

      // Set recommendations
      if (data.recommendations?.recommendations) {
        setRecommendations(data.recommendations.recommendations)
        console.log(`[LMS] fetchAllData: SUCCESS - Recommendations loaded (${data.recommendations.recommendations.length} entries)`)
      }

      // Set deadlines
      if (data.deadlines?.deadlines) {
        setDeadlines(data.deadlines.deadlines)
        console.log(`[LMS] fetchAllData: SUCCESS - Deadlines loaded (${data.deadlines.deadlines.length} entries)`)
      }

      // Set certificates
      if (data.certificates?.certificates) {
        setCertificates(data.certificates.certificates)
        console.log(`[LMS] fetchAllData: SUCCESS - Certificates loaded (${data.certificates.certificates.length} entries)`)
      }

      const totalTime = performance.now() - startTime
      console.log(`[LMS] ===== fetchAllData END: Completed in ${totalTime.toFixed(2)}ms =====`)

    } catch (err) {
      const totalTime = performance.now() - startTime
      console.error(`[LMS] ===== fetchAllData ERROR: Failed after ${totalTime.toFixed(2)}ms:`, err)
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to load LMS data'
      if (errorMsg.includes('timeout')) {
        setError('Dashboard is taking longer than expected to load. Please refresh the page or try again in a moment.')
      } else {
        setError(errorMsg)
      }
    } finally {
      setLoading(false)
    }
  }

  // Auto-refresh recommendations on every page load (runs after initial data fetch)
  useEffect(() => {
    if (!loading) {
      handleRefreshRecommendations(true) // silent = true (no extra loading UI on initial load)
    }
  }, [loading]) // fires once loading flips to false after fetchAllData

  /**
   * Refresh AI recommendations by calling the backend generate-recommendations
   * endpoint which dismisses stale recs and creates fresh ones based on the
   * user's latest profile + Zed context.
   *
   * @param {boolean} silent - if true, skip the refreshingRecs state (used on page load)
   */
  const handleWeeklyPerfFilter = async (days) => {
    if (days === weeklyPerfDays || weeklyPerfLoading) return
    setWeeklyPerfDays(days)
    setWeeklyPerfLoading(true)
    try {
      const res = await lmsAPI.getWeeklyPerformance(days)
      if (res?.data?.performance) {
        setWeeklyPerformance(res.data.performance)
      }
    } catch (err) {
      console.warn('[LMS] handleWeeklyPerfFilter: Failed to fetch weekly performance', err)
    } finally {
      setWeeklyPerfLoading(false)
    }
  }

  const handleRefreshRecommendations = async (silent = false) => {
    if (refreshingRecs) return // prevent double-trigger
    if (!silent && recsRefreshCount >= MAX_RECS_REFRESHES) return // local guard
    if (!silent) setRefreshingRecs(true)
    console.log('[LMS] handleRefreshRecommendations: Generating fresh recommendations...')
    try {
      const res = await lmsAPI.generateRecommendations(5)
      const data = res.data
      if (data?.recommendations) {
        setRecommendations(data.recommendations)
        console.log(`[LMS] handleRefreshRecommendations: SUCCESS - ${data.recommendations.length} recommendations`)
      }
      // Sync frontend counter with authoritative server value
      if (!silent && data?.rate_limit != null) {
        const usedOnServer = MAX_RECS_REFRESHES - data.rate_limit.remaining
        setRecsRefreshCount(usedOnServer)
      }
    } catch (err) {
      if (err?.response?.status === 429) {
        // Server says limit exceeded — pin the counter to max so the button disables
        setRecsRefreshCount(MAX_RECS_REFRESHES)
        console.warn('[LMS] handleRefreshRecommendations: Rate limit exceeded (server)')
      } else {
        console.error('[LMS] handleRefreshRecommendations: Error:', err)
      }
      // Don't overwrite the UI — stale recs are better than none
    } finally {
      setRefreshingRecs(false)
    }
  }

  // Fetch course details when portal opens
  useEffect(() => {
    if (selectedCourse && isPortalOpen) {
      console.log(`[LMS] ===== PORTAL OPEN: Fetching details for course_id=${selectedCourse.id} =====`)
      fetchCourseDetails(selectedCourse.id)
    }
  }, [selectedCourse, isPortalOpen])

  const fetchCourseDetails = async (courseId, showLoading = true, sectionIdOverride = null) => {
    const startTime = performance.now()
    console.log(`[LMS] fetchCourseDetails START: course_id=${courseId}, showLoading=${showLoading}, sectionIdOverride=${sectionIdOverride}`)
    
    try {
      if (showLoading) {
        setQuestionsLoading(true)
      }
      
      // Fetch sections and resources first (sections call also seeds defaults + backfills)
      console.log(`[LMS] fetchCourseDetails: Making API calls for sections, resources`)
      const [sectionsRes, resourcesRes] = await Promise.all([
        lmsAPI.getCourseSections(courseId),
        lmsAPI.getCourseResources(courseId)
      ])

      let activeSectionId = sectionIdOverride

      if (sectionsRes.data && sectionsRes.data.sections) {
        const sections = sectionsRes.data.sections
        setCourseSections(sections)
        console.log(`[LMS] fetchCourseDetails: SUCCESS - Loaded ${sections.length} sections`)
        
        // Auto-select first section if nothing selected yet
        if (!activeSectionId && sections.length > 0) {
          activeSectionId = sections[0].id
          setSelectedSectionId(activeSectionId)
        }
      }

      if (resourcesRes.data && resourcesRes.data.resources) {
        setCourseResources(resourcesRes.data.resources)
        console.log(`[LMS] fetchCourseDetails: SUCCESS - Loaded ${resourcesRes.data.resources.length} resources`)
      }

      // Fetch questions scoped to the active section (shared helper)
      console.log(`[LMS] fetchCourseDetails: Fetching questions for section_id=${activeSectionId}`)
      const qCount = await fetchSectionQuestions(courseId, activeSectionId)
      console.log(`[LMS] fetchCourseDetails: Loaded ${qCount} questions for section_id=${activeSectionId}`)

      const totalTime = performance.now() - startTime
      console.log(`[LMS] ===== fetchCourseDetails END: Completed in ${totalTime.toFixed(2)}ms =====`)

    } catch (err) {
      const totalTime = performance.now() - startTime
      console.error(`[LMS] ===== fetchCourseDetails ERROR: Failed after ${totalTime.toFixed(2)}ms:`, err)
    } finally {
      if (showLoading) {
        setQuestionsLoading(false)
      }
    }
  }
  
  // Handler when user clicks a section in the side panel
  const handleSectionSelect = async (sectionId) => {
    if (sectionId === selectedSectionId) return
    setSelectedSectionId(sectionId)
    setAnswers({}) // Clear previous answers
    setCurrentPage(0) // Reset to first page for the new section
    
    if (selectedCourse) {
      try {
        setQuestionsLoading(true)
        await fetchSectionQuestions(selectedCourse.id, sectionId)
      } finally {
        setQuestionsLoading(false)
      }
    }
  }

  const filteredCourses = courses.filter(course => {
    if (activeTab === 'all') return true
    if (activeTab === 'inProgress') return course.progress > 0 && course.progress < 100
    if (activeTab === 'completed') return course.progress === 100 || course.status === 'completed'
    if (activeTab === 'notStarted') return course.progress === 0 || course.status === 'not_started'
    return true
  })

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return ''
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

  // Format deadline date
  const formatDeadline = (deadlineDate) => {
    if (!deadlineDate) return ''
    const date = new Date(deadlineDate)
    const now = new Date()
    const diffTime = date - now
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays < 0) return 'Overdue'
    if (diffDays === 0) return 'Due today'
    if (diffDays === 1) return 'Due tomorrow'
    if (diffDays < 7) return `Due in ${diffDays} days`
    if (diffDays < 30) return `Due in ${Math.floor(diffDays / 7)} weeks`
    return `Due in ${Math.floor(diffDays / 30)} months`
  }

  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target
    setTopGradientOpacity(Math.min(scrollTop / 50, 1))
    const bottomDistance = scrollHeight - (scrollTop + clientHeight)
    setBottomGradientOpacity(scrollHeight <= clientHeight ? 0 : Math.min(bottomDistance / 50, 1))
  }

  const handleBackToFeed = () => {
    navigate('/feed')
  }

  const handleCourseClick = async (course) => {
    setSelectedCourse(course)
    setSelectedSectionId(null) // Reset section selection for new course
    setAnswers({}) // Clear previous answers
    setCurrentPage(0)
    setGenerateQuestionsCount(0) // Reset generate attempts for new course
    setIsPortalOpen(true)

    // Fetch per-section performance so level-locking and progress bar are accurate
    try {
      const perfRes = await lmsAPI.getSectionPerformance(course.id)
      if (perfRes.data && perfRes.data.sections) {
        setSectionPerf(perfRes.data.sections)
      }
    } catch (err) {
      console.warn('[LMS] handleCourseClick: Could not fetch section performance:', err)
      setSectionPerf([])
    }
  }

  const handleEnrollCourse = async (courseId) => {
    if (!courseId) return

    const messages = [
      'Fetching your profile',
      'Loading user preferences',
      'Checking course availability',
      'Syncing knowledge vectors',
      'Updating learning profile',
      'Configuring course sections',
      'Personalising your curriculum',
      'Finalising enrollment',
    ]

    let msgIdx = 0
    setEnrollingMessage(messages[0])
    setEnrollingLoading(true)

    const msgTimer = setInterval(() => {
      msgIdx = (msgIdx + 1) % messages.length
      setEnrollingMessage(messages[msgIdx])
    }, 1800)

    try {
      console.log(`[LMS] handleEnrollCourse: Enrolling in course_id=${courseId}`)
      await lmsAPI.enrollInCourse(courseId)

      setEnrollingMessage('Enrollment successful! 🎉')
      await new Promise(r => setTimeout(r, 900))

      await fetchAllData()
    } catch (err) {
      console.error(`[LMS] handleEnrollCourse: Failed to enroll:`, err)

      if (err.response?.status === 403) {
        // Use userMessage from interceptor if available, otherwise extract from response
        let message = err.userMessage || err.message
        // If message is the generic axios error, extract from response instead
        if (message && message.includes('Request failed with status code')) {
          message = null // Reset to extract from response
        }
        
        if (!message) {
          const detail = err.response.data?.detail
          // Handle quota exceeded errors (course enrollments, AI messages, etc.)
          if (detail && typeof detail === 'object' && detail.feature) {
            // Use the message from backend, which includes upgrade suggestion
            message = detail.message || `Your ${detail.feature.replace('_', ' ')} limit has been reached (${detail.used}/${detail.limit} on ${detail.plan} plan). Upgrade your plan to increase your limit.`
          } else if (detail) {
            // Handle other 403 errors - check if it's a string or object
            message = typeof detail === 'string' ? detail : detail?.message
          }
        }
        
        // Final fallback
        if (!message) {
          message = 'Your enrollment limit has been reached. Upgrade your plan to increase your limit.'
        }
        
        alert(message)
      } else {
        // Handle non-403 errors
        const errorMsg = err.response?.data?.detail || err.message || 'Failed to enroll in course'
        alert(`Error: ${typeof errorMsg === 'string' ? errorMsg : errorMsg.message || 'Failed to enroll'}`)
      }
    } finally {
      clearInterval(msgTimer)
      setEnrollingLoading(false)
      setEnrollingMessage('')
    }
  }

  const handleClosePortal = () => {
    setIsPortalOpen(false)

    // Update the matching course card's progress bar before tearing down portal state
    if (selectedCourse && sectionPerf.length > 0) {
      const totalAnswered = sectionPerf.reduce((sum, p) => sum + (p.questions_answered || 0), 0)
      const newProgress = Math.min(Math.round((totalAnswered / 60) * 100), 100)
      setCourses(prev => prev.map(c =>
        c.id === selectedCourse.id ? { ...c, progress: newProgress } : c
      ))
    }

    setTimeout(() => {
      setSelectedCourse(null)
      setSelectedSectionId(null)
      setCourseQuestions([])
      setCourseSections([])
      setCourseResources([])
      setAnswers({})
      setCurrentPage(0)
      setSectionPerf([])
    }, 400)
  }

  const handleAnswerChange = (questionId, answerText) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answerText
    }))
  }

  const handleNextQuestions = async () => {
    if (!selectedCourse) return

    const answeredEntries = Object.entries(answers).filter(([_, a]) => a && a.trim())
    if (answeredEntries.length === 0) {
      alert('Please provide at least one answer before continuing.')
      return
    }

    const PAGE_SIZE = 5
    const totalPages = Math.ceil(courseQuestions.length / PAGE_SIZE)
    const isLastPage = currentPage >= totalPages - 1

    try {
      console.log(`[LMS] handleNextQuestions: Submitting ${answeredEntries.length} answer(s) for page ${currentPage + 1}...`)

      // Submit current page's answers
      await Promise.all(
        answeredEntries.map(([questionId, answerText]) =>
          lmsAPI.submitAnswer(parseInt(questionId), answerText)
        )
      )
      console.log(`[LMS] handleNextQuestions: Submitted successfully`)

      // Fire-and-forget evaluation so progress stats update in the background
      lmsAPI.triggerSeezEvaluateCourse(selectedCourse.id)
        .then(() => console.log('[LMS] handleNextQuestions: Background evaluation completed'))
        .catch(err => console.warn('[LMS] handleNextQuestions: Background evaluation error:', err))

      // Refresh section performance so progress bar and lock status stay current
      try {
        const perfRes = await lmsAPI.getSectionPerformance(selectedCourse.id)
        if (perfRes.data && perfRes.data.sections) setSectionPerf(perfRes.data.sections)
      } catch (e) {
        console.warn('[LMS] handleNextQuestions: Could not refresh section performance:', e)
      }

      setAnswers({})

      if (isLastPage) {
        // No more questions — inform user and close portal
        alert('You have completed all questions for this level! Your answers have been submitted.')
        handleClosePortal()
        await fetchAllData()
      } else {
        // Advance to next page (pure frontend slice — no API call)
        setCurrentPage(p => p + 1)
      }
    } catch (err) {
      console.error('[LMS] handleNextQuestions: Error submitting answers:', err)
      alert('Failed to submit answers. Please try again.')
    }
  }

  const handleSubmitAndEvaluate = async () => {
    if (!selectedCourse) return

    const answeredEntries = Object.entries(answers).filter(([_, a]) => a && a.trim())
    if (answeredEntries.length === 0) {
      alert('Please provide at least one answer before submitting.')
      return
    }

    const startTime = performance.now()
    const courseId = selectedCourse.id
    console.log(`[LMS] ===== SUBMIT & EVALUATE START: course_id=${courseId} =====`)

    try {
      // Step 1: Submit all answers
      console.log('[LMS] handleSubmitAndEvaluate: Step 1 - Submitting answers...')
      await Promise.all(
        answeredEntries.map(([questionId, answerText]) =>
          lmsAPI.submitAnswer(parseInt(questionId), answerText)
        )
      )
      console.log(`[LMS] handleSubmitAndEvaluate: Step 1 SUCCESS - Submitted ${answeredEntries.length} answer(s)`)

      // Step 2: Trigger Seez evaluation (await so results are ready on the Evaluation page)
      console.log('[LMS] handleSubmitAndEvaluate: Step 2 - Triggering Seez agent evaluation...')
      await lmsAPI.triggerSeezEvaluateCourse(courseId)

      const totalTime = performance.now() - startTime
      console.log(`[LMS] ===== SUBMIT & EVALUATE END: Completed in ${totalTime.toFixed(2)}ms =====`)

      // Clean up portal state
      setAnswers({})
      handleClosePortal()

      // Step 3: Navigate to Evaluation page with the course pre-selected
      navigate('/evaluation', { state: { courseId } })
    } catch (err) {
      const totalTime = performance.now() - startTime
      console.error(`[LMS] ===== SUBMIT & EVALUATE ERROR: Failed after ${totalTime.toFixed(2)}ms:`, err)

      const errorMsg = err.response?.data?.detail || err.message || 'Failed to submit and evaluate answers'

      if (err.code === 'ECONNABORTED' || errorMsg.includes('timeout')) {
        // Answers were likely submitted; navigate anyway so user can check results
        setAnswers({})
        handleClosePortal()
        navigate('/evaluation', { state: { courseId } })
      } else {
        alert(`Error: ${errorMsg}`)
      }
    }
  }

  const handleGenerateQuestions = async () => {
    if (!selectedCourse) {
      console.warn('[LMS] handleGenerateQuestions: No course selected')
      return
    }
    if (generateQuestionsCount >= MAX_GENERATE_QUESTIONS) {
      console.warn('[LMS] handleGenerateQuestions: Attempt limit reached')
      return
    }

    setGenerateQuestionsCount(c => c + 1)

    const sectionId = selectedSectionId
    const sectionLabel = selectedSectionTitle || 'Basic'

    const startTime = performance.now()
    console.log(`[LMS] ===== GENERATE QUESTIONS START: course_id=${selectedCourse.id}, section_id=${sectionId} (${sectionLabel}) =====`)

    try {
      // Show loading state
      setQuestionsLoading(true)
      console.log('[LMS] handleGenerateQuestions: Button disabled, loading state set')
      
      // Call Azel agent to process course and generate questions for the selected section
      // This is a long-running operation (30-150 seconds)
      console.log(`[LMS] handleGenerateQuestions: Making API call to trigger Azel agent with section_id=${sectionId}`)
      const response = await lmsAPI.triggerAzelProcessCourse(selectedCourse.id, sectionId)
      
      const apiTime = performance.now() - startTime
      console.log(`[LMS] handleGenerateQuestions: API call completed in ${apiTime.toFixed(2)}ms`)
      
      if (response.data) {
        const result = response.data.result || {}
        const success = response.data.success !== false && result.success !== false

        // Sync counter with authoritative server value
        if (response.data.rate_limit != null) {
          const usedOnServer = MAX_GENERATE_QUESTIONS - response.data.rate_limit.remaining
          setGenerateQuestionsCount(usedOnServer)
        }

        console.log(`[LMS] handleGenerateQuestions: Response received, success=${success}`)
        console.log(`[LMS] handleGenerateQuestions: Result - topics=${result.topics_extracted?.length || 0}, urls=${result.urls_saved || 0}, questions=${result.questions_saved || 0}`)
        
        if (success) {
          // Show detailed success message
          const questionsCount = result.questions_saved || 0
          const topicsCount = result.topics_extracted?.length || 0
          const urlsCount = result.urls_saved || 0
          
          let successMsg = `Successfully generated ${questionsCount} question${questionsCount !== 1 ? 's' : ''}!`
          if (topicsCount > 0) {
            successMsg += `\n\nFound ${topicsCount} topic${topicsCount !== 1 ? 's' : ''} of interest`
          }
          if (urlsCount > 0) {
            successMsg += `\nSearched ${urlsCount} educational resource${urlsCount !== 1 ? 's' : ''}`
          }
          
          console.log(`[LMS] handleGenerateQuestions: SUCCESS - Showing success message to user`)
          alert(successMsg)
          
          // Refetch course questions for the selected section to display newly generated ones
          // Don't show loading state again since we're already in loading state
          console.log(`[LMS] handleGenerateQuestions: Auto-refreshing questions list for section_id=${sectionId}`)
          await fetchCourseDetails(selectedCourse.id, false, sectionId)
          
          const totalTime = performance.now() - startTime
          console.log(`[LMS] ===== GENERATE QUESTIONS END (SUCCESS): Completed in ${totalTime.toFixed(2)}ms =====`)
        } else {
          // Show detailed error message
          const errorMsg = result.error || response.data.message || 'Failed to generate questions'
          
          console.error(`[LMS] handleGenerateQuestions: FAILED - ${errorMsg}`)
          
          let errorDetails = `Question generation failed:\n${errorMsg}`
          
          // Provide helpful suggestions based on error
          if (errorMsg.includes('Zed context') || errorMsg.includes('No Zed context')) {
            errorDetails += '\n\nTip: Make sure you have updated your profile and interests so the system can understand what topics you want to learn about.'
          } else if (errorMsg.includes('topics')) {
            errorDetails += '\n\nTip: The system couldn\'t find highlighted topics in your profile. Try updating your interests and preferences.'
          } else if (errorMsg.includes('Qdrant') || errorMsg.includes('OpenAI')) {
            errorDetails += '\n\nTip: There may be a configuration issue with the AI services. Please contact support if this persists.'
          }
          
          alert(errorDetails)
          
          const totalTime = performance.now() - startTime
          console.log(`[LMS] ===== GENERATE QUESTIONS END (FAILED): Completed in ${totalTime.toFixed(2)}ms =====`)
        }
      } else {
        console.warn(`[LMS] handleGenerateQuestions: No response data received`)
        alert('Question generation completed, but no questions were generated. Please check your Zed context and try again.')
      }
    } catch (err) {
      const totalTime = performance.now() - startTime
      console.error(`[LMS] ===== GENERATE QUESTIONS ERROR: Exception after ${totalTime.toFixed(2)}ms:`, err)
      
      let errorMsg = 'Failed to generate questions. Please try again.'
      
      if (err.response) {
        if (err.response.status === 429) {
          // Rate limit hit on the server — pin counter to max to disable button
          setGenerateQuestionsCount(MAX_GENERATE_QUESTIONS)
          const detail = err.response.data?.detail
          errorMsg = (typeof detail === 'object' ? detail?.message : detail)
            || 'Question generation limit reached. Maximum 3 attempts allowed.'
          console.warn(`[LMS] handleGenerateQuestions: Rate limit exceeded (server)`)
        } else {
          // Server responded with error
          errorMsg = err.response.data?.detail || err.response.data?.message || err.message
          console.error(`[LMS] handleGenerateQuestions: Server error response:`, err.response.data)
        }
      } else if (err.request) {
        // Request made but no response
        if (err.code === 'ECONNABORTED') {
          errorMsg = 'Request timed out. The question generation process takes 30-150 seconds. Please try again.'
          console.error(`[LMS] handleGenerateQuestions: Request timeout after ${totalTime.toFixed(2)}ms`)
        } else if (err.code === 'ERR_NETWORK') {
          errorMsg = 'Network error. Please check your connection and try again.'
          console.error(`[LMS] handleGenerateQuestions: Network error`)
        } else {
          errorMsg = 'Network error. Please try again.'
          console.error(`[LMS] handleGenerateQuestions: Unknown network error:`, err.code)
        }
      } else {
        errorMsg = err.message || errorMsg
        console.error(`[LMS] handleGenerateQuestions: Client error:`, err.message)
      }
      
      alert(`Error: ${errorMsg}`)
    } finally {
      setQuestionsLoading(false)
      const finalTime = performance.now() - startTime
      console.log(`[LMS] ===== GENERATE QUESTIONS FINALLY: Total time ${finalTime.toFixed(2)}ms, loading state cleared =====`)
    }
  }

  return (
    <Container>
      {/* Full-screen enrollment loading overlay */}
      {enrollingLoading && (
        <EnrollOverlay>
          <EnrollOverlayRow>
            <EnrollOverlayText key={enrollingMessage}>
              <span className="msg">{enrollingMessage}</span>
            </EnrollOverlayText>
            <EnrollDots>
              <span /><span /><span />
            </EnrollDots>
          </EnrollOverlayRow>
        </EnrollOverlay>
      )}

      <Navbar />

      <MainContainer>
        <SidePanel>
          <PanelHeader>
            <PageTitle>Learning Management</PageTitle>
            <PageSubtitle>Explore & learn</PageSubtitle>
          </PanelHeader>
          
          <TabContainer className="tab-container-padded">
            <Tab active={activeTab === 'all'} onClick={() => setActiveTab('all')}>
              All Courses
            </Tab>
            <Tab active={activeTab === 'inProgress'} onClick={() => setActiveTab('inProgress')}>
              In Progress
            </Tab>
            <Tab active={activeTab === 'completed'} onClick={() => setActiveTab('completed')}>
              Completed
            </Tab>
            <Tab active={activeTab === 'notStarted'} onClick={() => setActiveTab('notStarted')}>
              Not Started
            </Tab>
          </TabContainer>

          <PanelContent>
            <ScrollGradientTop opacity={topGradientOpacity} />
            <ScrollableContent ref={scrollRef} onScroll={handleScroll}>
              {loading ? (
                <EmptyState>
                  <EmptyText>Loading courses...</EmptyText>
                </EmptyState>
              ) : error ? (
                <EmptyState>
                  <EmptyText>Error: {error}</EmptyText>
                </EmptyState>
              ) : filteredCourses.length > 0 ? (
                <CoursesGrid>
                  {filteredCourses.map((course, index) => (
                    <AnimatedCourseCard key={course.id} course={course} index={index} onCourseClick={handleCourseClick} />
                  ))}
                </CoursesGrid>
              ) : activeTab === 'all' && recommendations.length > 0 ? (
                // Only show recommended courses on the "All Courses" tab when no enrolled courses exist
                <>
                  <PanelHeader>
                    <PanelTitle>Recommended Courses</PanelTitle>
                    <PanelSubtitle>Based on your interests and learning goals</PanelSubtitle>
                  </PanelHeader>
                  <CoursesGrid>
                    {recommendations.map((rec) => {
                      // Backend returns flat structure: course_id, course_title, course_icon, course_description
                      // OR nested: rec.course (if include_relations returns full course object)
                      const courseId = rec.course_id || (rec.course && rec.course.id)
                      const courseTitle = rec.course_title || 'Recommended Course'
                      const courseIcon = rec.course_icon || (courseTitle ? courseTitle.substring(0, 2).toUpperCase() : 'RC')
                      const courseDescription = rec.course_description || rec.reason || 'A course recommended for you'
                      const courseCategory = rec.course_category || 'General'
                      const courseDifficulty = rec.course_difficulty || 'beginner'
                      
                      if (!courseId) {
                        console.warn('[LMS] Recommendation missing course_id:', rec)
                        return null
                      }
                      
                      return (
                        <CourseCard
                          key={rec.id || courseId}
                          onClick={() => {
                            handleEnrollCourse(courseId)
                          }}
                        >
                          <CourseIcon>{courseIcon}</CourseIcon>
                          <CourseContent>
                            <CourseTitle>{courseTitle}</CourseTitle>
                            <CourseDescription>{courseDescription}</CourseDescription>
                            <CourseMeta>
                              <CourseCategory>{courseCategory}</CourseCategory>
                              <CourseDifficulty>{courseDifficulty}</CourseDifficulty>
                            </CourseMeta>
                            <CourseAction>
                              <EnrollButton>Enroll</EnrollButton>
                            </CourseAction>
                          </CourseContent>
                        </CourseCard>
                      )
                    }).filter(Boolean)}
                  </CoursesGrid>
                </>
              ) : (
                <EmptyState>
                  <EmptyIcon>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                      <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                    </svg>
                  </EmptyIcon>
                  <EmptyText>
                    {activeTab === 'inProgress' && 'No courses in progress'}
                    {activeTab === 'completed' && 'No completed courses yet'}
                    {activeTab === 'notStarted' && 'No unstarted courses'}
                    {activeTab === 'all' && 'No courses found'}
                  </EmptyText>
                  <EmptySubtext>
                    {activeTab === 'all'
                      ? 'Course recommendations will appear here based on your interests'
                      : 'Enroll in a course to get started'}
                  </EmptySubtext>
                </EmptyState>
              )}
            </ScrollableContent>
            <ScrollGradientBottom opacity={bottomGradientOpacity} />
          </PanelContent>
        </SidePanel>

        <MainContent>
          <DashboardContainer>
            {/* Top Banner - Full Width */}
            <TopBanner>
              <BannerIcon>
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
              </BannerIcon>
              <BannerContent>
                <BannerTitle>
                  AI-Powered Learning Platform
                  <AIBadge>AI Enhanced</AIBadge>
                </BannerTitle>
                <BannerDescription>
                  Our intelligent learning management system analyzes your selections and past actions, such as job postings you've clicked on, to create personalized learning courses tailored to your career goals and help you improve the skills that matter most.
                </BannerDescription>
              </BannerContent>
            </TopBanner>
            
            {/* Stats Overview */}
            {loading ? (
              <StatCard>
                <div>
                  <StatValue>...</StatValue>
                  <StatLabel>Loading...</StatLabel>
                </div>
              </StatCard>
            ) : dashboard ? (
              <>
                <StatCard>
                  <div>
                    <StatValue>{dashboard.total_questions || 0}</StatValue>
                    <StatLabel>Total Questions</StatLabel>
                  </div>
                </StatCard>

                <StatCard>
                  <div>
                    <StatValue>{dashboard.correct_answers || 0}</StatValue>
                    <StatLabel>Correct Answers</StatLabel>
                  </div>
                </StatCard>

                <StatCard>
                  <div>
                    <StatValue>{dashboard.wrong_answers || 0}</StatValue>
                    <StatLabel>Wrong Answers</StatLabel>
                  </div>
                </StatCard>
              </>
            ) : null}

            {/* Overall Accuracy Circle */}
            <DashboardCard>
              <CardTitle>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                Overall Accuracy
              </CardTitle>
              {loading ? (
                <div style={{ textAlign: 'center', padding: '40px' }}>Loading...</div>
              ) : dashboard ? (() => {
                const totalQ = dashboard.total_questions || 0
                const correctA = dashboard.correct_answers || 0
                // Use backend's pre-computed value first; fall back to frontend calculation
                const accuracy = dashboard.overall_accuracy != null
                  ? parseFloat(dashboard.overall_accuracy)
                  : totalQ > 0 ? (correctA / totalQ) * 100 : 0
                return (
                  <ProgressCircle>
                    <svg width="150" height="150">
                      <defs>
                        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="var(--primary)" />
                          <stop offset="100%" stopColor="var(--secondary)" />
                        </linearGradient>
                      </defs>
                      <CircleBackground cx="75" cy="75" r="60" />
                      <CircleProgress
                        cx="75"
                        cy="75"
                        r="60"
                        circumference={2 * Math.PI * 60}
                        offset={2 * Math.PI * 60 * (1 - accuracy / 100)}
                      />
                    </svg>
                    <CircleText>
                      <CircleValue>{accuracy.toFixed(1)}%</CircleValue>
                      <CircleLabel>Accuracy</CircleLabel>
                    </CircleText>
                  </ProgressCircle>
                )
              })() : null}
            </DashboardCard>

            {/* Learning Streak */}
            <StatCard>
              <div>
                <StatValue>{dashboard?.day_streak || 0}</StatValue>
                <StatLabel>Day Streak</StatLabel>
              </div>
              {(dashboard?.day_streak || 0) > 0 && (
                <StatChange positive>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                  </svg>
                  Keep it up!
                </StatChange>
              )}
            </StatCard>



            {/* AI Recommendations */}
            <DashboardCard className="dashboard-card-span-2">
              <CardTitle>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
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
                AI Recommendations
                <RefreshRecsButton
                  onClick={() => handleRefreshRecommendations(false)}
                  disabled={refreshingRecs || recsRefreshCount >= MAX_RECS_REFRESHES}
                  title={recsRefreshCount >= MAX_RECS_REFRESHES ? 'Refresh limit reached (3/3)' : `Refresh recommendations (${MAX_RECS_REFRESHES - recsRefreshCount} attempts left)`}
                >
                  <svg
                    className={refreshingRecs ? 'spinning' : ''}
                    width="14" height="14" viewBox="0 0 24 24"
                    fill="none" stroke="currentColor" strokeWidth="2"
                    strokeLinecap="round" strokeLinejoin="round"
                  >
                    <polyline points="23 4 23 10 17 10"></polyline>
                    <polyline points="1 20 1 14 7 14"></polyline>
                    <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10"></path>
                    <path d="M20.49 15a9 9 0 0 1-14.85 3.36L1 14"></path>
                  </svg>
                  {refreshingRecs ? 'Refreshing...' : recsRefreshCount >= MAX_RECS_REFRESHES ? 'Limit Reached' : `Refresh (${MAX_RECS_REFRESHES - recsRefreshCount} left)`}
                </RefreshRecsButton>
              </CardTitle>
              <RecommendationsScrollContainer>
{(loading || refreshingRecs) ? (
                  <div style={{ textAlign: 'center', padding: '20px' }}>Loading...</div>
                ) : recommendations.length > 0 ? (
                  recommendations.map((rec) => {
                    const courseId = rec.course_id || (rec.course && rec.course.id)
                    const canEnroll = courses.length < 5
                    
                    return (
                      <ActivityItem key={rec.id} style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                        <div style={{ display: 'flex', width: '100%', alignItems: 'center', gap: '12px' }}>
                          <ActivityIcon>
                            {rec.course_icon || rec.course_title?.substring(0, 2).toUpperCase() || 'RC'}
                          </ActivityIcon>
                          <ActivityContent style={{ flex: 1 }}>
                            <ActivityTitle>{rec.course_title || 'Recommended Course'}</ActivityTitle>
                            <ActivityTime>{rec.reason || 'Based on your learning history'}</ActivityTime>
                          </ActivityContent>
                        </div>
                        {courseId && (
                          <div style={{ width: '100%', marginTop: '8px', paddingLeft: '52px' }}>
                            {canEnroll ? (
                              <EnrollButton
                                onClick={(e) => {
                                  e.stopPropagation()
                                  handleEnrollCourse(courseId)
                                }}
                                style={{ padding: '6px 12px', fontSize: '0.85em' }}
                              >
                                Enroll
                              </EnrollButton>
                            ) : (
                              <span style={{ fontSize: '0.8em', color: 'var(--text-light)', padding: '6px 12px' }}>
                                Limit Reached
                              </span>
                            )}
                          </div>
                        )}
                      </ActivityItem>
                    )
                  })
                ) : (
                  <EmptyState>
                    <EmptyText>No recommendations available</EmptyText>
                  </EmptyState>
                )}
              </RecommendationsScrollContainer>
            </DashboardCard>

            {/* Weekly Performance */}
            <DashboardCard className="dashboard-card-span-2">
              <WeeklyPerfHeader>
                <CardTitle style={{ marginBottom: 0 }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="18" y1="20" x2="18" y2="10"></line>
                    <line x1="12" y1="20" x2="12" y2="4"></line>
                    <line x1="6" y1="20" x2="6" y2="14"></line>
                  </svg>
                  Performance
                </CardTitle>
                <WeeklyPerfFilters>
                  <WeeklyPerfFilterBtn
                    active={weeklyPerfDays === 7}
                    onClick={() => handleWeeklyPerfFilter(7)}
                  >
                    Last 7 Days
                  </WeeklyPerfFilterBtn>
                  <WeeklyPerfFilterBtn
                    active={weeklyPerfDays === 30}
                    onClick={() => handleWeeklyPerfFilter(30)}
                  >
                    Last 30 Days
                  </WeeklyPerfFilterBtn>
                </WeeklyPerfFilters>
              </WeeklyPerfHeader>
              {(loading || weeklyPerfLoading) ? (
                <div style={{ textAlign: 'center', padding: '40px' }}>Loading...</div>
              ) : weeklyPerformance.length > 0 ? (
                <BarChartScrollWrapper>
                  <BarChart>
                    {weeklyPerformance.map((day, index) => {
                      const maxValue = Math.max(...weeklyPerformance.map(d => d.questions_answered || 0), 1)
                      const height = ((day.questions_answered || 0) / maxValue) * 100
                      const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
                      const dateObj = new Date(day.date)
                      const label = weeklyPerfDays <= 7
                        ? (dayNames[dateObj.getDay()] || `Day ${index + 1}`)
                        : dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })

                      return (
                        <div key={day.date || index} className="trend-bar-wrapper">
                          <Bar height={height}>
                            <BarValue>{day.questions_answered || 0}</BarValue>
                          </Bar>
                          <BarLabel>{label}</BarLabel>
                        </div>
                      )
                    })}
                  </BarChart>
                </BarChartScrollWrapper>
              ) : (
                <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-light)' }}>
                  No performance data available
                </div>
              )}
            </DashboardCard>
          </DashboardContainer>
        </MainContent>
      </MainContainer>

      {/* Course Portal */}
      <PortalOverlay isOpen={isPortalOpen} onClick={handleClosePortal} />
      <PortalContainer isOpen={isPortalOpen}>
        <PortalHeader>
          <PortalTitle>{selectedCourse?.title || 'Course Questions'}</PortalTitle>
          <CloseButton onClick={handleClosePortal}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </CloseButton>
        </PortalHeader>
        
        <PortalContent>
          {selectedCourse && (
            <>
              <PortalSidePanel>
                <SidePanelSection>
                  <SidePanelTitle>Level / Section</SidePanelTitle>
                  {courseSections.length > 0 ? (
                    courseSections.map((section) => {
                      const locked = isSectionLocked(section)
                      const perf = sectionPerf.find(p => p.section_id === section.id)
                      return (
                        <SidePanelItem
                          key={section.id}
                          active={section.id === selectedSectionId}
                          onClick={() => !locked && handleSectionSelect(section.id)}
                          style={{
                            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                            opacity: locked ? 0.45 : 1,
                            cursor: locked ? 'not-allowed' : 'pointer',
                          }}
                          title={locked ? 'Complete the previous level with ≥20 answers and ≥50% accuracy to unlock' : ''}
                        >
                          <span>{section.title || `Section ${section.order_index + 1}`}</span>
                          <span style={{ fontSize: '0.75em', opacity: 0.8, display: 'flex', alignItems: 'center', gap: '4px' }}>
                            {locked
                              ? '🔒'
                              : section.id === selectedSectionId
                                ? '● selected'
                                : perf && perf.questions_answered > 0
                                  ? `${perf.questions_answered}/20`
                                  : null}
                          </span>
                        </SidePanelItem>
                      )
                    })
                  ) : (
                    <SidePanelItem>No sections available</SidePanelItem>
                  )}
                </SidePanelSection>

                <SidePanelSection style={{ display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                  <SidePanelTitle>Resources</SidePanelTitle>
                  {courseResources.length > 0 ? (
                    <ResourcesScrollContainer>
                    {courseResources.map((resource) => {
                      const icon = resource.resource_type === 'material' ? '📚'
                        : resource.resource_type === 'code' ? '💻'
                        : resource.resource_type === 'document' ? '📄'
                        : '🔗'
                      return resource.url ? (
                        <SidePanelItem
                          key={resource.id}
                          as="a"
                          href={resource.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none' }}
                        >
                          <span>{icon}</span>
                          <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {resource.title || resource.resource_type}
                          </span>
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, opacity: 0.6 }}>
                            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                            <polyline points="15 3 21 3 21 9"></polyline>
                            <line x1="10" y1="14" x2="21" y2="3"></line>
                          </svg>
                        </SidePanelItem>
                      ) : (
                        <SidePanelItem key={resource.id} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span>{icon}</span>
                          <span>{resource.title || resource.resource_type}</span>
                        </SidePanelItem>
                      )
                    })}
                    </ResourcesScrollContainer>
                  ) : (
                    <SidePanelItem style={{ cursor: 'default' }}>No resources available</SidePanelItem>
                  )}
                </SidePanelSection>

                <GenerateQuestionsButton 
                  onClick={handleGenerateQuestions}
                  disabled={questionsLoading || !selectedSectionId || generateQuestionsCount >= MAX_GENERATE_QUESTIONS}
                  title={
                    !selectedSectionId ? 'Select a section first'
                    : generateQuestionsCount >= MAX_GENERATE_QUESTIONS ? 'Generation limit reached (3/3)'
                    : `Generate questions for ${selectedSectionTitle || 'selected section'} (${MAX_GENERATE_QUESTIONS - generateQuestionsCount} attempts left)`
                  }
                >
                  {questionsLoading ? (
                    <>
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ animation: 'spin 1s linear infinite' }}>
                        <path d="M21 12a9 9 0 11-6.219-8.56"></path>
                      </svg>
                      Generating Questions...
                    </>
                  ) : generateQuestionsCount >= MAX_GENERATE_QUESTIONS ? (
                    <>
                      Limit Reached (3/3)
                    </>
                  ) : (
                    <>
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
                      Generate Questions
                      {selectedSectionId && courseSections.length > 0 && (
                        <span style={{ fontSize: '0.8em', opacity: 0.85, marginLeft: '4px' }}>
                          ({selectedSectionTitle}) · {MAX_GENERATE_QUESTIONS - generateQuestionsCount} left
                        </span>
                      )}
                    </>
                  )}
                </GenerateQuestionsButton>
              </PortalSidePanel>

              <PortalMainContent>
                {/* Overall progress bar — answers across all levels, target 60 */}
                {(() => {
                  const totalAnswered = sectionPerf.reduce((sum, p) => sum + (p.questions_answered || 0), 0)
                  const progressPct = Math.min(Math.round((totalAnswered / 60) * 100), 100)
                  return (
                    <PortalProgressWrapper>
                      <PortalProgressLabel>
                        <span>Overall Progress</span>
                        <span>{totalAnswered} / 60 questions answered ({progressPct}%)</span>
                      </PortalProgressLabel>
                      <PortalProgressTrack>
                        <PortalProgressFill progress={progressPct} />
                      </PortalProgressTrack>
                    </PortalProgressWrapper>
                  )
                })()}

                <PortalCourseInfo>
                  <PortalCourseInfoText className="portal-course-info-text-large">
                    📝 {selectedSectionId && courseSections.length > 0
                      ? `${selectedSectionTitle} — Questions & Assessment`
                      : 'Course Questions & Assessment'}
                  </PortalCourseInfoText>
                  <PortalCourseInfoText>
                    {selectedSectionId && courseSections.length > 0
                      ? `Showing questions for the "${selectedSectionTitle}" level. Select a different section on the left to switch.`
                      : 'Complete the following questions to assess your understanding of the course material.'}
                  </PortalCourseInfoText>
                </PortalCourseInfo>

                {questionsLoading ? (
                  <div style={{ textAlign: 'center', padding: '40px' }}>Loading questions...</div>
                ) : courseQuestions.length > 0 ? (() => {
                  const PAGE_SIZE = 5
                  const pageQuestions = courseQuestions.slice(currentPage * PAGE_SIZE, (currentPage + 1) * PAGE_SIZE)
                  const totalPages = Math.ceil(courseQuestions.length / PAGE_SIZE)
                  return (
                    <>
                      {/* Page indicator */}
                      <div style={{ fontSize: '0.85em', color: 'var(--text-light)', marginBottom: '12px' }}>
                        Page {currentPage + 1} of {totalPages} &nbsp;·&nbsp; Questions {currentPage * PAGE_SIZE + 1}–{Math.min((currentPage + 1) * PAGE_SIZE, courseQuestions.length)} of {courseQuestions.length}
                      </div>
                      {pageQuestions.map((q, idx) => (
                        <QuestionSection key={q.id}>
                          <QuestionLabel>
                            <QuestionNumber>Question {currentPage * PAGE_SIZE + idx + 1}:</QuestionNumber>
                            {q.question_text || q.question || 'No question text available'}
                          </QuestionLabel>
                          {q.question_type === 'multiple_choice' && q.options ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' }}>
                              {Object.entries(q.options).map(([key, value]) => (
                                <label key={key} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                                  <input
                                    type="radio"
                                    name={`question-${q.id}`}
                                    value={key}
                                    onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                                  />
                                  <span>{key}: {value}</span>
                                </label>
                              ))}
                            </div>
                          ) : (
                            <AnswerInput
                              placeholder="Type your answer here..."
                              rows="4"
                              value={answers[q.id] || ''}
                              onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                            />
                          )}
                        </QuestionSection>
                      ))}
                    </>
                  )
                })() : (
                  <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-light)' }}>
                    No questions available for this course
                  </div>
                )}

                <ButtonContainer>
                  {(() => {
                    const PAGE_SIZE = 5
                    const pageQuestions = courseQuestions.slice(currentPage * PAGE_SIZE, (currentPage + 1) * PAGE_SIZE)
                    const totalPages = Math.ceil(courseQuestions.length / PAGE_SIZE)
                    const isLastPage = currentPage >= totalPages - 1
                    const allAnswered = pageQuestions.length > 0 && pageQuestions.every(q => answers[q.id] && answers[q.id].trim())
                    return (
                      <SubmitButton onClick={handleNextQuestions} disabled={!allAnswered}>
                        {isLastPage ? 'Next Page' : 'Next Questions'}
                      </SubmitButton>
                    )
                  })()}
                  <EvaluateButton onClick={handleSubmitAndEvaluate} disabled={Object.keys(answers).length === 0}>
                    Submit & Evaluate
                  </EvaluateButton>
                </ButtonContainer>
              </PortalMainContent>
            </>
          )}
        </PortalContent>
      </PortalContainer>
    </Container>
  )
}

export default LMS

