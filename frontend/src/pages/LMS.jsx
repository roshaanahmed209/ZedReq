import React, { useState, useEffect, useRef } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { motion, useInView } from 'framer-motion'
import { lmsAPI } from '../services/api'
import '../css/pages/LMS.css'

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

  @media (max-width: 600px) {
    gap: 15px;
    padding: 10px 0;
  }

  @media (max-width: 480px) {
    gap: 10px;
  }
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

  @media (max-width: 600px) {
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
`

const TopBanner = styled.div`
  width: 100%;
  grid-column: 1 / -1;
  padding: 24px 32px;
  display: flex;
  align-items: center;
  gap: 16px;

  @media (max-width: 768px) {
    padding: 20px 24px;
    gap: 12px;
  }

  @media (max-width: 600px) {
    padding: 16px 20px;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  @media (max-width: 480px) {
    padding: 16px;
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
  
  svg {
    width: 32px;
    height: 32px;
    color: white;
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

  @media (max-width: 768px) {
    font-size: 1.5em;
    gap: 10px;
  }

  @media (max-width: 600px) {
    font-size: 1.3em;
    flex-wrap: wrap;
  }

  @media (max-width: 480px) {
    font-size: 1.2em;
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

  @media (max-width: 768px) {
    font-size: 1em;
  }

  @media (max-width: 600px) {
    font-size: 0.95em;
    line-height: 1.5;
  }

  @media (max-width: 480px) {
    font-size: 0.9em;
  }
`

const DashboardContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  width: 100%;

  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
  }

  @media (max-width: 600px) {
    grid-template-columns: 1fr;
    gap: 16px;
  }
`

const DashboardCard = styled.div`
  background: var(--bg-white);
  border-radius: 16px;
  border: 1px solid var(--border);
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  animation: ${slideUp} 0.4s ease-out;
`

const CardTitle = styled.h3`
  font-size: 1.1em;
  color: var(--text);
  margin-bottom: 20px;
  font-weight: 300;
  display: flex;
  align-items: center;
  gap: 8px;
`

const StatCard = styled(DashboardCard)`
  display: flex;
  flex-direction: column;
  justify-content: space-between;
`

const StatValue = styled.div`
  font-size: 2.5em;
  font-weight: 300;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;

  @media (max-width: 600px) {
    font-size: 2.2em;
  }

  @media (max-width: 480px) {
    font-size: 2em;
  }
`

const StatLabel = styled.div`
  font-size: 0.9em;
  color: var(--text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
`

const StatChange = styled.div`
  font-size: 0.85em;
  color: ${props => props.positive ? '#2ecc71' : '#e74c3c'};
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
`

const ProgressCircle = styled.div`
  position: relative;
  width: 150px;
  height: 150px;
  margin: 20px auto;

  @media (max-width: 600px) {
    width: 130px;
    height: 130px;
  }

  @media (max-width: 480px) {
    width: 120px;
    height: 120px;
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
`

const CircleLabel = styled.div`
  font-size: 0.8em;
  color: var(--text-light);
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
`

const BarLabel = styled.div`
  font-size: 0.85em;
  color: var(--text);
  text-align: center;
  margin-top: 10px;
  font-weight: 400;
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
`

const CourseFooter = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
`

const CourseInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.75em;
  color: var(--text-lighter);
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
  
  &:hover {
    background: rgba(10, 102, 194, 0.1);
    border-color: var(--primary);
    color: var(--primary);
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

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(10, 102, 194, 0.3);
  }

  &:active {
    transform: translateY(0);
  }

  svg {
    width: 18px;
    height: 18px;
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

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(10, 102, 194, 0.3);
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
          <CourseFooter>
            <CourseInfo>
              <InfoItem>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                {course.duration}
              </InfoItem>
              <InfoItem>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                  <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                </svg>
                {course.lessons}
              </InfoItem>
            </CourseInfo>
          </CourseFooter>
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

const LMS = () => {
  const [activeTab, setActiveTab] = useState('all')
  const [topGradientOpacity, setTopGradientOpacity] = useState(0)
  const [bottomGradientOpacity, setBottomGradientOpacity] = useState(1)
  const [selectedCourse, setSelectedCourse] = useState(null)
  const [isPortalOpen, setIsPortalOpen] = useState(false)
  const scrollRef = useRef(null)
  const navigate = useNavigate()
  const { logout } = useAuth()

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
  const [answers, setAnswers] = useState({}) // questionId -> answer text

  // Loading and error states
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [questionsLoading, setQuestionsLoading] = useState(false)

  // Fetch all data on component mount
  useEffect(() => {
    fetchAllData()
  }, [])

  const fetchAllData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch all data in parallel
      const [
        coursesRes,
        dashboardRes,
        weeklyRes,
        domainRes,
        activitiesRes,
        recommendationsRes,
        deadlinesRes,
        certificatesRes
      ] = await Promise.all([
        lmsAPI.getMyCourses({ limit: 100 }),
        lmsAPI.getDashboard(),
        lmsAPI.getWeeklyPerformance(7),
        lmsAPI.getDomainPerformance(),
        lmsAPI.getActivities(10),
        lmsAPI.getRecommendations(5),
        lmsAPI.getDeadlines(10),
        lmsAPI.getCertificates()
      ])

      // Set courses
      if (coursesRes.data && coursesRes.data.courses) {
        setCourses(coursesRes.data.courses.map(course => ({
          id: course.id,
          title: course.title,
          description: course.description || '',
          icon: course.icon || course.title.substring(0, 2).toUpperCase(),
          lessons: course.lessons || 0,
          duration: course.duration || 'N/A',
          progress: course.progress || 0,
          status: course.status || 'not_started',
          category: course.category,
          difficulty: course.difficulty
        })))
      }

      // Set dashboard
      if (dashboardRes.data) {
        setDashboard(dashboardRes.data)
      }

      // Set weekly performance
      if (weeklyRes.data && weeklyRes.data.performance) {
        setWeeklyPerformance(weeklyRes.data.performance)
      }

      // Set domain performance
      if (domainRes.data && domainRes.data.performance) {
        setDomainPerformance(domainRes.data.performance)
      }

      // Set activities
      if (activitiesRes.data && activitiesRes.data.activities) {
        setActivities(activitiesRes.data.activities)
      }

      // Set recommendations
      if (recommendationsRes.data && recommendationsRes.data.recommendations) {
        setRecommendations(recommendationsRes.data.recommendations)
      }

      // Set deadlines
      if (deadlinesRes.data && deadlinesRes.data.deadlines) {
        setDeadlines(deadlinesRes.data.deadlines)
      }

      // Set certificates
      if (certificatesRes.data && certificatesRes.data.certificates) {
        setCertificates(certificatesRes.data.certificates)
      }

    } catch (err) {
      console.error('Error fetching LMS data:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to load LMS data')
    } finally {
      setLoading(false)
    }
  }

  // Fetch course details when portal opens
  useEffect(() => {
    if (selectedCourse && isPortalOpen) {
      fetchCourseDetails(selectedCourse.id)
    }
  }, [selectedCourse, isPortalOpen])

  const fetchCourseDetails = async (courseId) => {
    try {
      setQuestionsLoading(true)
      
      const [questionsRes, sectionsRes, resourcesRes] = await Promise.all([
        lmsAPI.getCourseQuestions(courseId),
        lmsAPI.getCourseSections(courseId),
        lmsAPI.getCourseResources(courseId)
      ])

      if (questionsRes.data && questionsRes.data.questions) {
        setCourseQuestions(questionsRes.data.questions)
      }

      if (sectionsRes.data && sectionsRes.data.sections) {
        setCourseSections(sectionsRes.data.sections)
      }

      if (resourcesRes.data && resourcesRes.data.resources) {
        setCourseResources(resourcesRes.data.resources)
      }

    } catch (err) {
      console.error('Error fetching course details:', err)
    } finally {
      setQuestionsLoading(false)
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

  const handleCourseClick = (course) => {
    setSelectedCourse(course)
    setIsPortalOpen(true)
  }

  const handleClosePortal = () => {
    setIsPortalOpen(false)
    setTimeout(() => {
      setSelectedCourse(null)
    }, 400)
  }

  const handleAnswerChange = (questionId, answerText) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answerText
    }))
  }

  const handleSubmitAnswers = async () => {
    if (!selectedCourse) return

    try {
      // Submit all answers
      const submitPromises = Object.entries(answers)
        .filter(([_, answer]) => answer && answer.trim())
        .map(([questionId, answerText]) =>
          lmsAPI.submitAnswer(parseInt(questionId), answerText)
        )

      await Promise.all(submitPromises)
      
      alert('Answers submitted successfully!')
      setAnswers({})
      handleClosePortal()
      
      // Refresh dashboard to update stats
      fetchAllData()
    } catch (err) {
      console.error('Error submitting answers:', err)
      alert('Failed to submit answers. Please try again.')
    }
  }

  const handleGenerateQuestions = async () => {
    if (!selectedCourse) return

    try {
      // This would call the agent to generate questions
      // For now, we'll just show an alert
      alert('Question generation feature coming soon!')
      // TODO: Integrate with LMS agent when ready
    } catch (err) {
      console.error('Error generating questions:', err)
      alert('Failed to generate questions. Please try again.')
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
            <BackButton onClick={handleBackToFeed}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
              </svg>
            </BackButton>
          </NavRight>
        </NavContainer>
      </Navbar>

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
              ) : (
                <EmptyState>
                  <EmptyIcon>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                      <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                    </svg>
                  </EmptyIcon>
                  <EmptyText>No courses found</EmptyText>
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
                  {dashboard.questions_change && (
                    <StatChange positive={dashboard.questions_change > 0}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                        <polyline points="17 6 23 6 23 12"></polyline>
                      </svg>
                      {dashboard.questions_change > 0 ? '+' : ''}{dashboard.questions_change}% from last week
                    </StatChange>
                  )}
                </StatCard>

                <StatCard>
                  <div>
                    <StatValue>{dashboard.correct_answers || 0}</StatValue>
                    <StatLabel>Correct Answers</StatLabel>
                  </div>
                  {dashboard.correct_change && (
                    <StatChange positive={dashboard.correct_change > 0}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                        <polyline points="17 6 23 6 23 12"></polyline>
                      </svg>
                      {dashboard.correct_change > 0 ? '+' : ''}{dashboard.correct_change}% improvement
                    </StatChange>
                  )}
                </StatCard>

                <StatCard>
                  <div>
                    <StatValue>{dashboard.wrong_answers || 0}</StatValue>
                    <StatLabel>Wrong Answers</StatLabel>
                  </div>
                  {dashboard.wrong_change && (
                    <StatChange positive={dashboard.wrong_change > 0}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
                        <polyline points="17 18 23 18 23 12"></polyline>
                      </svg>
                      {dashboard.wrong_change > 0 ? '+' : ''}{dashboard.wrong_change}% from last week
                    </StatChange>
                  )}
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
              ) : dashboard ? (
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
                      offset={2 * Math.PI * 60 * (1 - (dashboard.accuracy || 0) / 100)}
                    />
                  </svg>
                  <CircleText>
                    <CircleValue>{(dashboard.accuracy || 0).toFixed(1)}%</CircleValue>
                    <CircleLabel>Accuracy</CircleLabel>
                  </CircleText>
                </ProgressCircle>
              ) : null}
            </DashboardCard>

            {/* Weekly Performance */}
            <DashboardCard className="dashboard-card-span-2">
              <CardTitle>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="20" x2="18" y2="10"></line>
                  <line x1="12" y1="20" x2="12" y2="4"></line>
                  <line x1="6" y1="20" x2="6" y2="14"></line>
                </svg>
                Weekly Performance
              </CardTitle>
              {loading ? (
                <div style={{ textAlign: 'center', padding: '40px' }}>Loading...</div>
              ) : weeklyPerformance.length > 0 ? (
                <BarChart>
                  {weeklyPerformance.map((day, index) => {
                    const maxValue = Math.max(...weeklyPerformance.map(d => d.questions_answered || 0), 1)
                    const height = ((day.questions_answered || 0) / maxValue) * 100
                    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
                    const dayName = day.day_name || dayNames[new Date(day.date).getDay()] || `Day ${index + 1}`
                    
                    return (
                      <div key={day.date || index} className="trend-bar-wrapper">
                        <Bar height={height}>
                          <BarValue>{day.questions_answered || 0}</BarValue>
                        </Bar>
                        <BarLabel>{dayName}</BarLabel>
                      </div>
                    )
                  })}
                </BarChart>
              ) : (
                <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-light)' }}>
                  No performance data available
                </div>
              )}
            </DashboardCard>

            {/* Domain-Specific Performance */}
            <DashboardCard className="dashboard-card-span-2">
              <CardTitle>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                  <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                </svg>
                Domain-Specific Performance
              </CardTitle>
              {loading ? (
                <div style={{ textAlign: 'center', padding: '40px' }}>Loading...</div>
              ) : domainPerformance.length > 0 ? (
                <DomainList>
                  {domainPerformance.map((domain) => (
                    <DomainItem key={domain.domain_id || domain.domain_name}>
                      <DomainHeader>
                        <DomainName>{domain.domain_name || 'Unknown Domain'}</DomainName>
                        <DomainPercentage>{domain.accuracy || 0}%</DomainPercentage>
                      </DomainHeader>
                      <DomainProgressBar>
                        <DomainProgressFill width={domain.accuracy || 0} />
                      </DomainProgressBar>
                    </DomainItem>
                  ))}
                </DomainList>
              ) : (
                <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-light)' }}>
                  No domain performance data available
                </div>
              )}
            </DashboardCard>

            {/* Recent Learning Activity */}
            <DashboardCard>
              <CardTitle>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                Recent Activity
              </CardTitle>
              {loading ? (
                <div style={{ textAlign: 'center', padding: '20px' }}>Loading...</div>
              ) : activities.length > 0 ? (
                activities.map((activity) => (
                  <ActivityItem key={activity.id}>
                    <ActivityIcon>
                      {activity.course_icon || activity.activity_type?.substring(0, 2).toUpperCase() || 'AC'}
                    </ActivityIcon>
                    <ActivityContent>
                      <ActivityTitle>{activity.description || activity.activity_type || 'Activity'}</ActivityTitle>
                      <ActivityTime>{formatDate(activity.created_at)}</ActivityTime>
                    </ActivityContent>
                  </ActivityItem>
                ))
              ) : (
                <EmptyState>
                  <EmptyText>No recent activity</EmptyText>
                </EmptyState>
              )}
            </DashboardCard>

            {/* AI Recommendations */}
            <DashboardCard>
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
              </CardTitle>
              {loading ? (
                <div style={{ textAlign: 'center', padding: '20px' }}>Loading...</div>
              ) : recommendations.length > 0 ? (
                recommendations.map((rec) => (
                  <ActivityItem key={rec.id}>
                    <ActivityIcon>
                      {rec.course_icon || rec.course_title?.substring(0, 2).toUpperCase() || 'RC'}
                    </ActivityIcon>
                    <ActivityContent>
                      <ActivityTitle>{rec.course_title || rec.recommendation_text || 'Recommended Course'}</ActivityTitle>
                      <ActivityTime>{rec.reason || 'Based on your learning history'}</ActivityTime>
                    </ActivityContent>
                  </ActivityItem>
                ))
              ) : (
                <EmptyState>
                  <EmptyText>No recommendations available</EmptyText>
                </EmptyState>
              )}
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

            {/* Certificates Earned */}
            <StatCard>
              <div>
                <StatValue>{certificates.length || 0}</StatValue>
                <StatLabel>Certificates</StatLabel>
              </div>
              {certificates.length > 0 && (
                <StatChange positive>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                  </svg>
                  {certificates.length} earned
                </StatChange>
              )}
            </StatCard>

            {/* Upcoming Deadlines */}
            <DashboardCard className="dashboard-card-span-2">
              <CardTitle>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="16" y1="2" x2="16" y2="6"></line>
                  <line x1="8" y1="2" x2="8" y2="6"></line>
                  <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
                Upcoming Deadlines
              </CardTitle>
              {loading ? (
                <div style={{ textAlign: 'center', padding: '40px' }}>Loading...</div>
              ) : deadlines.length > 0 ? (
                <DomainList>
                  {deadlines.map((deadline) => {
                    const dueText = formatDeadline(deadline.deadline_date)
                    const isOverdue = dueText === 'Overdue'
                    const isDueSoon = dueText.includes('today') || dueText.includes('tomorrow') || dueText.includes('in 1 days') || dueText.includes('in 2 days')
                    
                    return (
                      <DomainItem key={deadline.id}>
                        <DomainHeader>
                          <DomainName>{deadline.title || deadline.course_title || 'Deadline'}</DomainName>
                          <DomainPercentage 
                            className={isOverdue ? 'domain-percentage-due-soon' : isDueSoon ? 'domain-percentage-due-soon' : 'domain-percentage-due-medium'}
                          >
                            {dueText}
                          </DomainPercentage>
                        </DomainHeader>
                      </DomainItem>
                    )
                  })}
                </DomainList>
              ) : (
                <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-light)' }}>
                  No upcoming deadlines
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
                  <SidePanelTitle>Course Info</SidePanelTitle>
                  <PortalCourseInfoText>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10"></circle>
                      <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    {selectedCourse.duration}
                  </PortalCourseInfoText>
                  <PortalCourseInfoText>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                      <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                    </svg>
                    {selectedCourse.lessons} lessons
                  </PortalCourseInfoText>
                  <PortalCourseInfoText>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="22" y1="12" x2="2" y2="12"></line>
                      <polyline points="12 2 2 12 12 22"></polyline>
                    </svg>
                    {selectedCourse.progress}% complete
                  </PortalCourseInfoText>
                </SidePanelSection>

                <SidePanelSection>
                  <SidePanelTitle>Sections</SidePanelTitle>
                  {courseSections.length > 0 ? (
                    courseSections.map((section, index) => (
                      <SidePanelItem key={section.id} active={index === 0}>
                        {section.title || `Section ${section.order_index || index + 1}`}
                        <ProgressIndicator>
                          <ProgressDot completed={section.completed || false} />
                          <ProgressDot completed={section.completed || false} />
                          <ProgressDot completed={section.completed || false} />
                        </ProgressIndicator>
                      </SidePanelItem>
                    ))
                  ) : (
                    <SidePanelItem>No sections available</SidePanelItem>
                  )}
                </SidePanelSection>

                <SidePanelSection>
                  <SidePanelTitle>Resources</SidePanelTitle>
                  {courseResources.length > 0 ? (
                    courseResources.map((resource) => (
                      <SidePanelItem key={resource.id}>
                        {resource.resource_type === 'material' ? '📚' : resource.resource_type === 'code' ? '💻' : '🎥'} {resource.title || resource.resource_type}
                      </SidePanelItem>
                    ))
                  ) : (
                    <SidePanelItem>No resources available</SidePanelItem>
                  )}
                </SidePanelSection>

                <GenerateQuestionsButton onClick={handleGenerateQuestions}>
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
                </GenerateQuestionsButton>
              </PortalSidePanel>

              <PortalMainContent>
                <PortalCourseInfo>
                  <PortalCourseInfoText className="portal-course-info-text-large">
                    📝 Course Questions & Assessment
                  </PortalCourseInfoText>
                  <PortalCourseInfoText>
                    Complete the following questions to assess your understanding of the course material.
                  </PortalCourseInfoText>
                </PortalCourseInfo>

                {questionsLoading ? (
                  <div style={{ textAlign: 'center', padding: '40px' }}>Loading questions...</div>
                ) : courseQuestions.length > 0 ? (
                  courseQuestions.map((q) => (
                    <QuestionSection key={q.id}>
                      <QuestionLabel>
                        <QuestionNumber>Question {q.order_index || q.id}:</QuestionNumber>
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
                  ))
                ) : (
                  <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-light)' }}>
                    No questions available for this course
                  </div>
                )}

                <ButtonContainer>
                  <SubmitButton onClick={handleSubmitAnswers}>
                    Submit Answers
                  </SubmitButton>
                  <EvaluateButton onClick={handleSubmitAnswers} disabled={Object.keys(answers).length === 0}>
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

