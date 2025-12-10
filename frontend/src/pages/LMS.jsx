import React, { useState, useEffect, useRef } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { motion, useInView } from 'framer-motion'
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

  const courses = [
    {
      id: 1,
      title: 'Introduction to React',
      description: 'Learn the fundamentals of React and build modern web applications',
      icon: 'RC',
      lessons: 24,
      duration: '6h 30m',
      progress: 65
    },
    {
      id: 2,
      title: 'Advanced JavaScript',
      description: 'Master advanced JavaScript concepts and ES6+ features',
      icon: 'JS',
      lessons: 32,
      duration: '8h 15m',
      progress: 40
    },
    {
      id: 3,
      title: 'Node.js Backend Development',
      description: 'Build scalable backend applications with Node.js and Express',
      icon: 'ND',
      lessons: 28,
      duration: '7h 45m',
      progress: 20
    },
    {
      id: 4,
      title: 'Database Design',
      description: 'Learn SQL, NoSQL databases and database optimization techniques',
      icon: 'DB',
      lessons: 20,
      duration: '5h 20m',
      progress: 0
    },
    {
      id: 5,
      title: 'UI/UX Design Principles',
      description: 'Create beautiful and user-friendly interfaces',
      icon: 'UI',
      lessons: 18,
      duration: '4h 30m',
      progress: 100
    },
    {
      id: 6,
      title: 'Python for Data Science',
      description: 'Data analysis and visualization with Python libraries',
      icon: 'PY',
      lessons: 30,
      duration: '9h 00m',
      progress: 15
    },
    {
      id: 7,
      title: 'TypeScript Fundamentals',
      description: 'Learn TypeScript and build type-safe applications',
      icon: 'TS',
      lessons: 26,
      duration: '7h 00m',
      progress: 85
    },
    {
      id: 8,
      title: 'Docker & Containerization',
      description: 'Master containerization and deployment with Docker',
      icon: 'DK',
      lessons: 22,
      duration: '6h 15m',
      progress: 0
    },
    {
      id: 9,
      title: 'GraphQL API Development',
      description: 'Build modern APIs with GraphQL and Apollo',
      icon: 'GQ',
      lessons: 25,
      duration: '6h 45m',
      progress: 50
    },
    {
      id: 10,
      title: 'AWS Cloud Services',
      description: 'Deploy and manage applications on Amazon Web Services',
      icon: 'AWS',
      lessons: 35,
      duration: '10h 30m',
      progress: 0
    },
    {
      id: 11,
      title: 'Redux State Management',
      description: 'Manage complex application state with Redux and Redux Toolkit',
      icon: 'RX',
      lessons: 20,
      duration: '5h 45m',
      progress: 100
    },
    {
      id: 12,
      title: 'Testing with Jest',
      description: 'Write comprehensive tests for JavaScript applications',
      icon: 'JT',
      lessons: 18,
      duration: '4h 50m',
      progress: 75
    },
    {
      id: 13,
      title: 'Next.js Full Stack',
      description: 'Build server-side rendered React applications with Next.js',
      icon: 'NX',
      lessons: 30,
      duration: '8h 30m',
      progress: 30
    },
    {
      id: 14,
      title: 'MongoDB Mastery',
      description: 'Master NoSQL database design and operations with MongoDB',
      icon: 'MG',
      lessons: 24,
      duration: '6h 20m',
      progress: 0
    },
    {
      id: 15,
      title: 'Git Version Control',
      description: 'Professional Git workflows and collaboration techniques',
      icon: 'GT',
      lessons: 15,
      duration: '3h 40m',
      progress: 100
    },
    {
      id: 16,
      title: 'CSS Grid & Flexbox',
      description: 'Modern CSS layouts and responsive design techniques',
      icon: 'CS',
      lessons: 22,
      duration: '5h 30m',
      progress: 95
    },
    {
      id: 17,
      title: 'REST API Best Practices',
      description: 'Design and build robust RESTful APIs',
      icon: 'API',
      lessons: 20,
      duration: '5h 15m',
      progress: 0
    },
    {
      id: 18,
      title: 'Webpack & Build Tools',
      description: 'Optimize and bundle modern web applications',
      icon: 'WP',
      lessons: 16,
      duration: '4h 25m',
      progress: 45
    },
    {
      id: 19,
      title: 'Web Security Essentials',
      description: 'Protect applications from common security vulnerabilities',
      icon: 'SEC',
      lessons: 28,
      duration: '7h 50m',
      progress: 60
    },
    {
      id: 20,
      title: 'Microservices Architecture',
      description: 'Design and implement scalable microservices systems',
      icon: 'MS',
      lessons: 32,
      duration: '9h 15m',
      progress: 0
    },
    {
      id: 21,
      title: 'Tailwind CSS',
      description: 'Rapidly build modern websites with utility-first CSS',
      icon: 'TW',
      lessons: 18,
      duration: '4h 35m',
      progress: 100
    },
    {
      id: 22,
      title: 'Vue.js Essentials',
      description: 'Build interactive user interfaces with Vue.js framework',
      icon: 'VU',
      lessons: 26,
      duration: '7h 10m',
      progress: 25
    },
    {
      id: 23,
      title: 'PostgreSQL Database',
      description: 'Advanced relational database management with PostgreSQL',
      icon: 'PG',
      lessons: 24,
      duration: '6h 40m',
      progress: 0
    },
    {
      id: 24,
      title: 'Agile & Scrum',
      description: 'Modern project management and agile methodologies',
      icon: 'AG',
      lessons: 12,
      duration: '3h 20m',
      progress: 100
    }
  ]

  const filteredCourses = courses.filter(course => {
    if (activeTab === 'all') return true
    if (activeTab === 'inProgress') return course.progress > 0 && course.progress < 100
    if (activeTab === 'completed') return course.progress === 100
    if (activeTab === 'notStarted') return course.progress === 0
    return true
  })

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

  const handleSubmitAnswers = () => {
    // Handle answer submission
    alert('Answers submitted successfully!')
    handleClosePortal()
  }

  const courseQuestions = [
    {
      id: 1,
      question: "What are the key concepts you've learned from this course so far?"
    },
    {
      id: 2,
      question: "Describe a practical application where you can use the skills from this course."
    },
    {
      id: 3,
      question: "What challenges did you face while learning this topic, and how did you overcome them?"
    },
    {
      id: 4,
      question: "How would you explain the core concepts of this course to a beginner?"
    }
  ]

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
              {filteredCourses.length > 0 ? (
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
            <StatCard>
              <div>
                <StatValue>847</StatValue>
                <StatLabel>Total Questions</StatLabel>
              </div>
              <StatChange positive>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                  <polyline points="17 6 23 6 23 12"></polyline>
                </svg>
                +12% from last week
              </StatChange>
            </StatCard>

            <StatCard>
              <div>
                <StatValue>682</StatValue>
                <StatLabel>Correct Answers</StatLabel>
              </div>
              <StatChange positive>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                  <polyline points="17 6 23 6 23 12"></polyline>
                </svg>
                +8% improvement
              </StatChange>
            </StatCard>

            <StatCard>
              <div>
                <StatValue>165</StatValue>
                <StatLabel>Wrong Answers</StatLabel>
              </div>
              <StatChange>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
                  <polyline points="17 18 23 18 23 12"></polyline>
                </svg>
                -5% from last week
              </StatChange>
            </StatCard>

            {/* Overall Accuracy Circle */}
            <DashboardCard>
              <CardTitle>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                Overall Accuracy
              </CardTitle>
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
                    offset={2 * Math.PI * 60 * (1 - 0.805)}
                  />
                </svg>
                <CircleText>
                  <CircleValue>80.5%</CircleValue>
                  <CircleLabel>Accuracy</CircleLabel>
                </CircleText>
              </ProgressCircle>
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
              <BarChart>
                <div className="trend-bar-wrapper">
                  <Bar height={68}>
                    <BarValue>52</BarValue>
                  </Bar>
                  <BarLabel>Mon</BarLabel>
                </div>
                <div className="trend-bar-wrapper">
                  <Bar height={84}>
                    <BarValue>64</BarValue>
                  </Bar>
                  <BarLabel>Tue</BarLabel>
                </div>
                <div className="trend-bar-wrapper">
                  <Bar height={95}>
                    <BarValue>72</BarValue>
                  </Bar>
                  <BarLabel>Wed</BarLabel>
                </div>
                <div className="trend-bar-wrapper">
                  <Bar height={79}>
                    <BarValue>60</BarValue>
                  </Bar>
                  <BarLabel>Thu</BarLabel>
                </div>
                <div className="trend-bar-wrapper">
                  <Bar height={100}>
                    <BarValue>76</BarValue>
                  </Bar>
                  <BarLabel>Fri</BarLabel>
                </div>
                <div className="trend-bar-wrapper">
                  <Bar height={58}>
                    <BarValue>44</BarValue>
                  </Bar>
                  <BarLabel>Sat</BarLabel>
                </div>
                <div className="trend-bar-wrapper">
                  <Bar height={74}>
                    <BarValue>56</BarValue>
                  </Bar>
                  <BarLabel>Sun</BarLabel>
                </div>
              </BarChart>
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
              <DomainList>
                <DomainItem>
                  <DomainHeader>
                    <DomainName>React & Frontend</DomainName>
                    <DomainPercentage>87%</DomainPercentage>
                  </DomainHeader>
                  <DomainProgressBar>
                    <DomainProgressFill width={87} />
                  </DomainProgressBar>
                </DomainItem>
                <DomainItem>
                  <DomainHeader>
                    <DomainName>JavaScript ES6+</DomainName>
                    <DomainPercentage>92%</DomainPercentage>
                  </DomainHeader>
                  <DomainProgressBar>
                    <DomainProgressFill width={92} />
                  </DomainProgressBar>
                </DomainItem>
                <DomainItem>
                  <DomainHeader>
                    <DomainName>Node.js & Backend</DomainName>
                    <DomainPercentage>75%</DomainPercentage>
                  </DomainHeader>
                  <DomainProgressBar>
                    <DomainProgressFill width={75} />
                  </DomainProgressBar>
                </DomainItem>
                <DomainItem>
                  <DomainHeader>
                    <DomainName>Database & SQL</DomainName>
                    <DomainPercentage>68%</DomainPercentage>
                  </DomainHeader>
                  <DomainProgressBar>
                    <DomainProgressFill width={68} />
                  </DomainProgressBar>
                </DomainItem>
                <DomainItem>
                  <DomainHeader>
                    <DomainName>UI/UX Design</DomainName>
                    <DomainPercentage>95%</DomainPercentage>
                  </DomainHeader>
                  <DomainProgressBar>
                    <DomainProgressFill width={95} />
                  </DomainProgressBar>
                </DomainItem>
              </DomainList>
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
              <ActivityItem>
                <ActivityIcon>RC</ActivityIcon>
                <ActivityContent>
                  <ActivityTitle>Completed React Hooks Module</ActivityTitle>
                  <ActivityTime>2 hours ago</ActivityTime>
                </ActivityContent>
              </ActivityItem>
              <ActivityItem>
                <ActivityIcon>JS</ActivityIcon>
                <ActivityContent>
                  <ActivityTitle>Mastered Async/Await Patterns</ActivityTitle>
                  <ActivityTime>5 hours ago</ActivityTime>
                </ActivityContent>
              </ActivityItem>
              <ActivityItem>
                <ActivityIcon>ND</ActivityIcon>
                <ActivityContent>
                  <ActivityTitle>Started Express.js Basics</ActivityTitle>
                  <ActivityTime>Yesterday</ActivityTime>
                </ActivityContent>
              </ActivityItem>
              <ActivityItem>
                <ActivityIcon>DB</ActivityIcon>
                <ActivityContent>
                  <ActivityTitle>SQL Joins Practice</ActivityTitle>
                  <ActivityTime>2 days ago</ActivityTime>
                </ActivityContent>
              </ActivityItem>
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
              <ActivityItem>
                <ActivityIcon>TS</ActivityIcon>
                <ActivityContent>
                  <ActivityTitle>Complete TypeScript Fundamentals</ActivityTitle>
                  <ActivityTime>85% progress - almost done!</ActivityTime>
                </ActivityContent>
              </ActivityItem>
              <ActivityItem>
                <ActivityIcon>DK</ActivityIcon>
                <ActivityContent>
                  <ActivityTitle>Start Docker & Containerization</ActivityTitle>
                  <ActivityTime>Based on your backend skills</ActivityTime>
                </ActivityContent>
              </ActivityItem>
              <ActivityItem>
                <ActivityIcon>AWS</ActivityIcon>
                <ActivityContent>
                  <ActivityTitle>AWS Cloud Services</ActivityTitle>
                  <ActivityTime>Recommended for your career path</ActivityTime>
                </ActivityContent>
              </ActivityItem>
            </DashboardCard>

            {/* Learning Streak */}
            <StatCard>
              <div>
                <StatValue>15</StatValue>
                <StatLabel>Day Streak</StatLabel>
              </div>
              <StatChange positive>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                </svg>
                Keep it up!
              </StatChange>
            </StatCard>

            {/* Certificates Earned */}
            <StatCard>
              <div>
                <StatValue>8</StatValue>
                <StatLabel>Certificates</StatLabel>
              </div>
              <StatChange positive>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                2 new this month
              </StatChange>
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
              <DomainList>
                <DomainItem>
                  <DomainHeader>
                    <DomainName>TypeScript Final Project</DomainName>
                    <DomainPercentage className="domain-percentage-due-soon">Due in 2 days</DomainPercentage>
                  </DomainHeader>
                </DomainItem>
                <DomainItem>
                  <DomainHeader>
                    <DomainName>React Quiz - Advanced Concepts</DomainName>
                    <DomainPercentage className="domain-percentage-due-medium">Due in 5 days</DomainPercentage>
                  </DomainHeader>
                </DomainItem>
                <DomainItem>
                  <DomainHeader>
                    <DomainName>GraphQL Assignment Submission</DomainName>
                    <DomainPercentage className="domain-percentage-due-far">Due in 1 week</DomainPercentage>
                  </DomainHeader>
                </DomainItem>
              </DomainList>
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
                  <SidePanelItem active>
                    Introduction
                    <ProgressIndicator>
                      <ProgressDot completed />
                      <ProgressDot completed />
                      <ProgressDot completed />
                    </ProgressIndicator>
                  </SidePanelItem>
                  <SidePanelItem>
                    Core Concepts
                    <ProgressIndicator>
                      <ProgressDot completed />
                      <ProgressDot completed />
                      <ProgressDot />
                    </ProgressIndicator>
                  </SidePanelItem>
                  <SidePanelItem>
                    Advanced Topics
                    <ProgressIndicator>
                      <ProgressDot completed />
                      <ProgressDot />
                      <ProgressDot />
                    </ProgressIndicator>
                  </SidePanelItem>
                  <SidePanelItem>
                    Practice & Projects
                    <ProgressIndicator>
                      <ProgressDot />
                      <ProgressDot />
                      <ProgressDot />
                    </ProgressIndicator>
                  </SidePanelItem>
                </SidePanelSection>

                <SidePanelSection>
                  <SidePanelTitle>Resources</SidePanelTitle>
                  <SidePanelItem>
                    📚 Course Materials
                  </SidePanelItem>
                  <SidePanelItem>
                    💻 Code Examples
                  </SidePanelItem>
                  <SidePanelItem>
                    🎥 Video Lectures
                  </SidePanelItem>
                </SidePanelSection>

                <GenerateQuestionsButton onClick={() => alert('Generating AI questions...')}>
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

                {courseQuestions.map((q) => (
                  <QuestionSection key={q.id}>
                    <QuestionLabel>
                      <QuestionNumber>Question {q.id}:</QuestionNumber>
                      {q.question}
                    </QuestionLabel>
                    <AnswerInput 
                      placeholder="Type your answer here..."
                      rows="4"
                    />
                  </QuestionSection>
                ))}

                <ButtonContainer>
                  <SubmitButton onClick={handleSubmitAnswers}>
                    Submit Answers
                  </SubmitButton>
                  <EvaluateButton onClick={() => navigate('/evaluation')}>
                    Evaluate
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

