import React, { useState, useEffect } from 'react'
import styled, { keyframes, css } from 'styled-components'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { userAPI, connectionAPI, postAPI, profileFeaturesAPI, contextAPI, networkAPI } from '../services/api'
import api from '../services/api'
import { parseProfileUrl, generateProfileUrl } from '../utils/profileUrl'
import Navbar from '../components/Navbar'
import '../css/pages/Profile.css'

/* ═══════════════════════════════════════════════════════════════
   Animations
   ═══════════════════════════════════════════════════════════════ */

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`

const slideUp = keyframes`
  from { transform: translateY(24px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`

const shimmer = keyframes`
  0% { background-position: -400px 0; }
  100% { background-position: 400px 0; }
`

const pulseGlow = keyframes`
  0%, 100% { box-shadow: 0 0 0 0 rgba(10, 102, 194, 0.25); }
  50% { box-shadow: 0 0 20px 4px rgba(10, 102, 194, 0.15); }
`

const tabSlide = keyframes`
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
`

/* ═══════════════════════════════════════════════════════════════
   Layout Shells
   ═══════════════════════════════════════════════════════════════ */

const Page = styled.div`
  min-height: 100vh;
  background: var(--bg-light);
  animation: ${fadeIn} 0.5s ease;
`

const Shell = styled.div`
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px 60px;
  
  @media (max-width: 1024px) {
    padding: 0 18px 50px;
  }
  
  @media (max-width: 768px) {
    padding: 0 16px 45px;
  }
  
  @media (max-width: 600px) {
    padding: 0 14px 40px;
  }
  
  @media (max-width: 480px) {
    padding: 0 12px 40px;
  }
  
  @media (max-width: 360px) {
    padding: 0 10px 35px;
  }
`

/* ═══════════════════════════════════════════════════════════════
   Cover + Header
   ═══════════════════════════════════════════════════════════════ */

const CoverWrap = styled.div`
  position: relative;
  width: 100%;
  height: 260px;
  background: ${p => p.$src
    ? `url(${p.$src}) center/cover no-repeat`
    : 'linear-gradient(135deg, #0a66c2 0%, #004182 50%, #00a0dc 100%)'
  };
  
  &::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom, transparent 40%, color-mix(in srgb, var(--bg-light) 85%, black) 100%);
  }

  @media (max-width: 1024px) {
    height: 240px;
  }
  
  @media (max-width: 768px) {
    height: 200px;
  }
  
  @media (max-width: 600px) {
    height: 180px;
  }
  
  @media (max-width: 480px) {
    height: 160px;
  }
  
  @media (max-width: 360px) {
    height: 140px;
  }
`

const HeaderCard = styled.div`
  position: relative;
  margin-top: -100px;
  z-index: 10;
  background: color-mix(in srgb, var(--bg-white) 70%, transparent);
  backdrop-filter: blur(28px) saturate(160%);
  -webkit-backdrop-filter: blur(28px) saturate(160%);
  border: 1px solid color-mix(in srgb, var(--border) 30%, transparent);
  border-radius: 20px;
  padding: 100px 32px 32px 32px; /* Add top padding to prevent text overlap */
  animation: ${slideUp} 0.55s ease;
  transition: background-color 0.3s ease, border-color 0.3s ease;

  @media (max-width: 1024px) {
    margin-top: -90px;
    padding: 90px 28px 28px 28px;
  }

  @media (max-width: 768px) {
    margin-top: -80px;
    padding: 80px 20px 24px 20px;
    border-radius: 16px;
  }
  
  @media (max-width: 600px) {
    margin-top: -70px;
    padding: 70px 18px 22px 18px;
    border-radius: 14px;
  }
  
  @media (max-width: 480px) {
    margin-top: -60px;
    padding: 60px 16px 20px 16px;
    border-radius: 14px;
  }
  
  @media (max-width: 360px) {
    margin-top: -50px;
    padding: 50px 14px 18px 14px;
    border-radius: 12px;
  }
`

const AvatarRow = styled.div`
  display: flex;
  align-items: flex-end;
  gap: 24px;
  margin-top: -60px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  position: relative;
  z-index: 1; /* Ensure avatar row is above background */

  @media (max-width: 768px) {
    margin-top: -50px;
    gap: 16px;
    margin-bottom: 18px;
  }
  
  @media (max-width: 600px) {
    margin-top: -45px;
    margin-bottom: 16px;
  }
  
  @media (max-width: 480px) {
    margin-top: -40px;
    gap: 12px;
    flex-direction: column;
    align-items: center;
    text-align: center;
    margin-bottom: 14px;
  }
  
  @media (max-width: 360px) {
    margin-top: -35px;
    margin-bottom: 12px;
  }
`

const AvatarCircle = styled.div`
  width: 130px;
  height: 130px;
  border-radius: 50%;
  border: 4px solid var(--bg-white);
  overflow: hidden;
  flex-shrink: 0;
  background: var(--bg-white);
  box-shadow: var(--shadow-lg);
  animation: ${pulseGlow} 3s ease-in-out infinite;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  @media (max-width: 1024px) {
    width: 120px;
    height: 120px;
    border-width: 3.5px;
  }

  @media (max-width: 768px) {
    width: 110px;
    height: 110px;
    border-width: 3px;
  }
  
  @media (max-width: 600px) {
    width: 100px;
    height: 100px;
  }
  
  @media (max-width: 480px) {
    width: 96px;
    height: 96px;
    border-width: 3px;
  }
  
  @media (max-width: 360px) {
    width: 85px;
    height: 85px;
    border-width: 2.5px;
  }
`

const AvatarFallback = styled.div`
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 2.6em;
  font-weight: 300;
  letter-spacing: -1px;
  @media (max-width: 480px) { font-size: 2em; }
`

const HeaderMeta = styled.div`
  flex: 1;
  min-width: 0;
  padding-top: 16px;
  position: relative;
  z-index: 1; /* Ensure text is above background */
  
  @media (max-width: 768px) {
    padding-top: 14px;
  }
  
  @media (max-width: 600px) {
    padding-top: 12px;
  }
  
  @media (max-width: 480px) { 
    padding-top: 10px; 
  }
  
  @media (max-width: 360px) {
    padding-top: 8px;
  }
`

const UserName = styled.h1`
  font-size: 1.85em;
  font-weight: 500;
  color: var(--text);
  margin: 0 0 4px;
  line-height: 1.2;
  word-wrap: break-word;
  
  @media (max-width: 1024px) {
    font-size: 1.7em;
  }
  
  @media (max-width: 768px) {
    font-size: 1.5em;
  }
  
  @media (max-width: 600px) {
    font-size: 1.4em;
  }
  
  @media (max-width: 480px) {
    font-size: 1.35em;
  }
  
  @media (max-width: 360px) {
    font-size: 1.2em;
  }
`

const Headline = styled.p`
  font-size: 1.05em;
  color: var(--text-light);
  margin: 0 0 6px;
  word-wrap: break-word;
  
  @media (max-width: 1024px) {
    font-size: 1em;
  }
  
  @media (max-width: 768px) {
    font-size: 0.98em;
  }
  
  @media (max-width: 600px) {
    font-size: 0.95em;
    margin-bottom: 5px;
  }
  
  @media (max-width: 480px) {
    font-size: 0.95em;
    margin-bottom: 4px;
  }
  
  @media (max-width: 360px) {
    font-size: 0.9em;
  }
`

const SubInfo = styled.p`
  font-size: 0.9em;
  color: var(--text-lighter);
  margin: 0 0 4px;
  display: flex;
  align-items: center;
  gap: 6px;
  @media (max-width: 480px) {
    justify-content: center;
    font-size: 0.85em;
  }
`

/* Stats Row */
const StatsRow = styled.div`
  display: flex;
  gap: 28px;
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid color-mix(in srgb, var(--border) 30%, transparent);
  flex-wrap: wrap;
  @media (max-width: 480px) {
    gap: 20px;
    justify-content: center;
  }
`

const Stat = styled.div`
  cursor: pointer;
  transition: color 0.2s;
  text-align: center;
  &:hover span:first-child { color: var(--primary); }
`

const StatNum = styled.span`
  display: block;
  font-size: 1.3em;
  font-weight: 600;
  color: var(--text);
  transition: color 0.2s;
`

const StatLabel = styled.span`
  font-size: 0.82em;
  color: var(--text-lighter);
  letter-spacing: 0.3px;
`

/* Action Pills */
const Pills = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 20px;
  flex-wrap: wrap;
  @media (max-width: 480px) { justify-content: center; }
`

const Pill = styled.button`
  padding: 9px 22px;
  border-radius: 100px;
  font-size: 0.9em;
  font-weight: 500;
  cursor: ${p => p.disabled ? 'not-allowed' : 'pointer'};
  border: ${p => p.$solid ? 'none' : '1px solid var(--primary)'};
  min-height: 44px; /* Better touch target */
  transition: all 0.2s ease;
  
  @media (max-width: 768px) {
    padding: 8px 18px;
    font-size: 0.85em;
  }
  
  @media (max-width: 600px) {
    padding: 8px 16px;
    font-size: 0.8em;
  }
  
  @media (max-width: 480px) {
    padding: 7px 14px;
    font-size: 0.8em;
    min-height: 40px;
  }
  
  @media (max-width: 360px) {
    padding: 6px 12px;
    font-size: 0.75em;
    min-height: 38px;
  }
  background: ${p => p.$solid ? 'var(--primary)' : 'transparent'};
  color: ${p => p.$solid ? '#fff' : 'var(--primary)'};
  opacity: ${p => p.disabled ? 0.55 : 1};
  transition: all 0.25s;
  display: flex;
  align-items: center;
  gap: 6px;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    background: ${p => p.$solid ? 'var(--primary-dark)' : 'rgba(10,102,194,0.12)'};
    box-shadow: 0 4px 14px rgba(10,102,194,0.25);
  }
`

/* ═══════════════════════════════════════════════════════════════
   Tab Navigation
   ═══════════════════════════════════════════════════════════════ */

const TabBar = styled.div`
  display: flex;
  gap: 0;
  margin-top: 28px;
  border-bottom: 1px solid var(--border);
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  -ms-overflow-style: none;

  &::-webkit-scrollbar { 
    display: none; 
    width: 0;
    height: 0;
  }
  
  @media (max-width: 768px) {
    margin-top: 24px;
  }
  
  @media (max-width: 480px) {
    margin-top: 20px;
    /* Ensure tabs are scrollable on mobile */
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
  }
  
  @media (max-width: 360px) {
    margin-top: 18px;
  }
`

const Tab = styled.button`
  position: relative;
  padding: 14px 22px;
  background: none;
  border: none;
  color: ${p => p.$active ? 'var(--primary)' : 'var(--text-lighter)'};
  font-size: 0.92em;
  font-weight: ${p => p.$active ? 600 : 400};
  cursor: pointer;
  white-space: nowrap;
  transition: color 0.2s;
  flex-shrink: 0; /* Prevent tabs from shrinking */
  min-height: 44px; /* Better touch target */

  &::after {
    content: '';
    position: absolute;
    left: 12px;
    right: 12px;
    bottom: -1px;
    height: 2.5px;
    background: var(--primary);
    border-radius: 2px 2px 0 0;
    transform: scaleX(${p => p.$active ? 1 : 0});
    transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  }

  &:hover {
    color: var(--primary);
  }
  
  @media (max-width: 768px) {
    padding: 12px 18px;
    font-size: 0.88em;
    min-height: 42px;
    
    &::after {
      left: 10px;
      right: 10px;
    }
  }
  
  @media (max-width: 480px) {
    padding: 10px 16px;
    font-size: 0.85em;
    min-height: 40px;
    scroll-snap-align: start; /* Snap to start of each tab */
    
    &::after {
      left: 8px;
      right: 8px;
      height: 2px;
    }
  }
  
  @media (max-width: 360px) {
    padding: 10px 14px;
    font-size: 0.8em;
    min-height: 38px;
    
    &::after {
      left: 6px;
      right: 6px;
    }
  }
`

/* Tab Content Wrapper */
const TabPanel = styled.div`
  animation: ${tabSlide} 0.35s ease;
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
`

/* ═══════════════════════════════════════════════════════════════
   Section Cards
   ═══════════════════════════════════════════════════════════════ */

const Card = styled.div`
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px;
  transition: box-shadow 0.25s;
  &:hover { box-shadow: 0 2px 16px rgba(0,0,0,0.08); }
  @media (max-width: 768px) { padding: 22px; border-radius: 14px; }
  @media (max-width: 480px) { padding: 18px; border-radius: 12px; }
`

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
`

const CardTitle = styled.h2`
  font-size: 1.15em;
  font-weight: 600;
  color: var(--text);
  margin: 0;
`

const EditButton = styled.button`
  background: none;
  border: 1px solid var(--border);
  color: var(--text-light);
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 0.85em;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;

  &:hover {
    background: var(--hover-bg);
    border-color: var(--primary);
    color: var(--primary);
  }

  svg {
    width: 14px;
    height: 14px;
  }
`

const CardText = styled.div`
  color: var(--text-light);
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 0.95em;
`

const EmptyState = styled.div`
  text-align: center;
  padding: 36px 16px;
  color: var(--text-lighter);
  font-size: 0.92em;
`

/* ═══════════════════════════════════════════════════════════════
   Skills
   ═══════════════════════════════════════════════════════════════ */

const ChipsWrap = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`

const Chip = styled.span`
  padding: 7px 16px;
  background: rgba(10, 102, 194, 0.1);
  color: var(--primary);
  border-radius: 100px;
  font-size: 0.88em;
  font-weight: 500;
  transition: all 0.2s;
  &:hover {
    background: rgba(10, 102, 194, 0.2);
    transform: translateY(-1px);
  }
`

/* ═══════════════════════════════════════════════════════════════
   Timeline Items (Experience + Education)
   ═══════════════════════════════════════════════════════════════ */

const Timeline = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    top: 8px;
    bottom: 8px;
    left: 7px;
    width: 2px;
    background: var(--border);
    border-radius: 1px;
  }
`

const TimelineItem = styled.div`
  position: relative;
  padding-left: 32px;
  padding-bottom: 24px;

  &:last-child { padding-bottom: 0; }

  &::before {
    content: '';
    position: absolute;
    left: 2px;
    top: 6px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: ${p => p.$color || 'var(--primary)'};
    border: 2px solid var(--bg-white);
    box-shadow: 0 0 0 2px ${p => p.$color || 'var(--primary)'};
  }
`

const TLTitle = styled.h3`
  font-size: 1.05em;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 3px;
`

const TLSub = styled.div`
  font-size: 0.92em;
  color: var(--text-light);
  margin-bottom: 3px;
`

const TLDate = styled.div`
  font-size: 0.82em;
  color: var(--text-lighter);
  margin-bottom: 6px;
`

const TLDesc = styled.div`
  font-size: 0.9em;
  color: var(--text-light);
  line-height: 1.6;
  margin-top: 6px;
`

/* ═══════════════════════════════════════════════════════════════
   Project Cards
   ═══════════════════════════════════════════════════════════════ */

const ProjectsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  @media (max-width: 480px) { grid-template-columns: 1fr; }
`

const ProjectCard = styled.div`
  padding: 20px;
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 14px;
  transition: all 0.25s;
  display: flex;
  flex-direction: column;
  gap: 8px;

  &:hover {
    border-color: var(--primary);
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(10, 102, 194, 0.12);
  }
`

const ProjTitle = styled.h3`
  font-size: 1.05em;
  font-weight: 600;
  color: var(--text);
  margin: 0;
`

const ProjDesc = styled.p`
  font-size: 0.88em;
  color: var(--text-light);
  line-height: 1.55;
  margin: 0;
`

const ProjLink = styled.a`
  color: var(--primary);
  text-decoration: none;
  font-size: 0.88em;
  font-weight: 500;
  transition: opacity 0.2s;
  &:hover { text-decoration: underline; }
`

const TechTags = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 4px;
`

const TechTag = styled.span`
  padding: 3px 10px;
  background: rgba(10, 102, 194, 0.08);
  color: var(--primary);
  border-radius: 100px;
  font-size: 0.78em;
  font-weight: 500;
`

/* ═══════════════════════════════════════════════════════════════
   Certificates
   ═══════════════════════════════════════════════════════════════ */

const CertCard = styled.div`
  padding: 16px;
  background: var(--bg-light);
  border-radius: 10px;
  border-left: 3px solid var(--primary);

  h4 {
    font-size: 0.98em;
    font-weight: 500;
    color: var(--text);
    margin: 0 0 4px;
  }
`

const CertMeta = styled.div`
  font-size: 0.82em;
  color: var(--text-lighter);
  margin-top: 3px;
`

const CertLink = styled.a`
  color: var(--primary);
  text-decoration: none;
  font-size: 0.85em;
  margin-top: 6px;
  display: inline-block;
  &:hover { text-decoration: underline; }
`

/* ═══════════════════════════════════════════════════════════════
   Recommendations
   ═══════════════════════════════════════════════════════════════ */

const RecCard = styled.div`
  padding: 20px;
  background: var(--bg-light);
  border-radius: 12px;
  position: relative;

  &::before {
    content: '"';
    position: absolute;
    top: 10px;
    left: 16px;
    font-size: 3em;
    color: var(--primary);
    opacity: 0.2;
    line-height: 1;
    font-family: Georgia, serif;
  }
`

const RecText = styled.p`
  font-size: 0.93em;
  color: var(--text-light);
  line-height: 1.7;
  font-style: italic;
  margin: 0 0 10px;
  padding-left: 8px;
`

const RecAuthor = styled.div`
  font-size: 0.83em;
  color: var(--text-lighter);
  padding-left: 8px;
`

/* ═══════════════════════════════════════════════════════════════
   Interests
   ═══════════════════════════════════════════════════════════════ */

const InterestBadge = styled.div`
  padding: 8px 16px;
  background: var(--bg-light);
  border: 1px solid var(--border);
  border-radius: 100px;
  font-size: 0.88em;
  color: var(--text);
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: border-color 0.2s;

  &:hover { border-color: var(--primary); }

  a {
    color: var(--primary);
    text-decoration: none;
    &:hover { text-decoration: underline; }
  }
`

/* ═══════════════════════════════════════════════════════════════
   People Suggestions (for Recommendations tab)
   ═══════════════════════════════════════════════════════════════ */

const PeopleGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;
  }
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
  }
`

const PersonCard = styled.div`
  background: var(--bg-white);
  border-radius: 14px;
  border: 1px solid var(--border);
  overflow: hidden;
  transition: all 0.3s;
  &:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    transform: translateY(-2px);
  }
`

const PersonContent = styled.div`
  padding: 60px 20px 20px;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
`

const PersonAvatar = styled.div`
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: ${props => props.src ? `url(${props.src}) center/cover` : 'linear-gradient(135deg, var(--primary), var(--secondary))'};
  border: 4px solid var(--bg-white);
  position: absolute;
  top: -45px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 2em;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
`

const PersonName = styled.h3`
  font-size: 1.1em;
  color: var(--text);
  margin: 8px 0 4px;
  font-weight: 500;
`

const PersonTitle = styled.p`
  font-size: 0.88em;
  color: var(--text-light);
  margin: 0 0 8px;
`

const PersonCompany = styled.p`
  font-size: 0.85em;
  color: var(--text-lighter);
  margin: 0 0 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
`

const MutualConnections = styled.div`
  font-size: 0.82em;
  color: var(--primary);
  margin-bottom: 12px;
  padding: 6px 12px;
  background: rgba(10, 102, 194, 0.08);
  border-radius: 8px;
`

const ButtonGroup = styled.div`
  display: flex;
  gap: 8px;
  width: 100%;
  margin-top: 8px;
`

const ConnectButton = styled.button`
  flex: 1;
  padding: 10px 16px;
  background: ${props => {
    if (props.pending) return 'var(--bg-light)'
    if (props.connected) return 'transparent'
    return 'var(--primary)'
  }};
  color: ${props => {
    if (props.pending) return 'var(--text-light)'
    if (props.connected) return 'var(--primary)'
    return '#fff'
  }};
  border: ${props => props.connected ? '1px solid var(--primary)' : 'none'};
  border-radius: 8px;
  font-size: 0.9em;
  font-weight: 500;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  opacity: ${props => props.disabled ? 0.6 : 1};
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;

  &:hover:not(:disabled) {
    background: ${props => {
      if (props.pending || props.connected) return 'var(--hover-bg)'
      return 'var(--primary-dark)'
    }};
    transform: translateY(-1px);
  }
`

/* ═══════════════════════════════════════════════════════════════
   Posts
   ═══════════════════════════════════════════════════════════════ */

const PostCard = styled.div`
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 22px;
  transition: border-color 0.2s;
  &:hover { border-color: rgba(10,102,194,0.3); }
  @media (max-width: 480px) { padding: 16px; border-radius: 12px; }
`

const PostHead = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
`

const PostAv = styled.div`
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 500;
  font-size: 1em;
  flex-shrink: 0;
`

const PostBody = styled.div`
  color: var(--text-light);
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
  font-size: 0.93em;
  margin-bottom: 12px;
`

const PostMedia = styled.div`
  margin: 12px 0;
  border-radius: 10px;
  overflow: hidden;
  img, video {
    max-width: 100%;
    max-height: 420px;
    object-fit: contain;
    border-radius: 10px;
  }
`

const PostFooter = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
`

const LikeBtn = styled.button`
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: ${p => p.$liked ? 'var(--primary)' : 'var(--text-lighter)'};
  cursor: pointer;
  transition: all 0.2s;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.9em;
  font-weight: 500;

  &:hover {
    background: var(--hover-bg);
    color: var(--primary);
  }

  svg {
    width: 18px;
    height: 18px;
  }
`

/* Featured Grid */
const FeatGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  @media (max-width: 600px) { grid-template-columns: repeat(2, 1fr); }
`

const FeatThumb = styled.div`
  aspect-ratio: 1;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s;
  &:hover { transform: scale(1.03); }
  img, video { width: 100%; height: 100%; object-fit: cover; }
`

/* ═══════════════════════════════════════════════════════════════
   Contact Modal
   ═══════════════════════════════════════════════════════════════ */

const Overlay = styled.div`
  position: fixed;
  inset: 0;
  background: color-mix(in srgb, var(--bg-light) 65%, black);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: ${fadeIn} 0.2s;
`

const Modal = styled.div`
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px;
  max-width: 440px;
  width: 100%;
  animation: ${slideUp} 0.3s ease;
`

const ModalHead = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 22px;

  h2 {
    font-size: 1.3em;
    font-weight: 500;
    color: var(--text);
    margin: 0;
  }

  button {
    background: none;
    border: none;
    font-size: 1.4em;
    color: var(--text-lighter);
    cursor: pointer;
    width: 34px;
    height: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.2s;
    &:hover { background: var(--hover-bg); color: var(--text); }
  }
`

const InfoRow = styled.div`
  margin-bottom: 14px;
  &:last-child { margin-bottom: 0; }
  strong {
    color: var(--text);
    display: block;
    margin-bottom: 3px;
    font-size: 0.88em;
  }
  span {
    color: var(--text-light);
    font-size: 0.95em;
  }
`

/* ═══════════════════════════════════════════════════════════════
   Edit Modal Styles
   ═══════════════════════════════════════════════════════════════ */

const EditModal = styled(Modal)`
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
`

const FormGroup = styled.div`
  margin-bottom: 20px;

  label {
    display: block;
    font-size: 0.9em;
    font-weight: 500;
    color: var(--text);
    margin-bottom: 8px;
  }

  input, textarea, select {
    width: 100%;
    padding: 10px 14px;
    border: 1px solid var(--border);
    border-radius: 8px;
    font-size: 0.95em;
    color: var(--text);
    background: var(--bg-white);
    transition: border-color 0.2s;

    &:focus {
      outline: none;
      border-color: var(--primary);
    }
  }

  textarea {
    resize: vertical;
    min-height: 100px;
    font-family: inherit;
  }

  small {
    display: block;
    margin-top: 4px;
    font-size: 0.8em;
    color: var(--text-lighter);
  }
`

const FormActions = styled.div`
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
`

const Button = styled.button`
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.9em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;

  &.primary {
    background: var(--primary);
    color: #fff;

    &:hover:not(:disabled) {
      background: var(--primary-dark);
    }
  }

  &.secondary {
    background: var(--bg-light);
    color: var(--text);
    border: 1px solid var(--border);

    &:hover {
      background: var(--hover-bg);
    }
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`

const SkillsInput = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: 8px;
  min-height: 50px;
  background: var(--bg-white);

  input {
    border: none;
    padding: 4px 8px;
    background: transparent;
    flex: 1;
    min-width: 120px;
    font-size: 0.9em;

    &:focus {
      outline: none;
    }
  }
`

/* ═══════════════════════════════════════════════════════════════
   Skeleton Loading
   ═══════════════════════════════════════════════════════════════ */

const SkeletonBox = styled.div`
  background: linear-gradient(90deg, var(--bg-white) 25%, var(--hover-bg) 50%, var(--bg-white) 75%);
  background-size: 800px 100%;
  animation: ${shimmer} 1.6s infinite ease-in-out;
  border-radius: ${p => p.$r || '8px'};
  height: ${p => p.$h || '16px'};
  width: ${p => p.$w || '100%'};
`

/* ═══════════════════════════════════════════════════════════════
   Loading & Error States
   ═══════════════════════════════════════════════════════════════ */

const Spinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 100px 20px;

  &::after {
    content: '';
    width: 36px;
    height: 36px;
    border: 3px solid var(--border);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin 0.85s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`

const ErrorBox = styled.div`
  text-align: center;
  padding: 100px 20px;
  color: var(--text-light);
  h2 { color: var(--text); margin-bottom: 10px; font-weight: 500; }
`

/* ═══════════════════════════════════════════════════════════════
   Component
   ═══════════════════════════════════════════════════════════════ */

const TABS = ['About', 'Experience', 'Education', 'Projects', 'Recommendations', 'Posts']

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
  const [featuredPosts, setFeaturedPosts] = useState([])
  const [loadingFeatured, setLoadingFeatured] = useState(false)
  const [connectionCounts, setConnectionCounts] = useState({ followers: 0, following: 0, connections: 0 })
  const [certificates, setCertificates] = useState([])
  const [loadingCertificates, setLoadingCertificates] = useState(false)
  const [showContactModal, setShowContactModal] = useState(false)
  const [experiences, setExperiences] = useState([])
  const [educations, setEducations] = useState([])
  const [projects, setProjects] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [interests, setInterests] = useState([])
  const [loadingFeatures, setLoadingFeatures] = useState(false)
  const [activeTab, setActiveTab] = useState('About')
  const [suggestions, setSuggestions] = useState([])
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)
  
  // Edit modal states
  const [editModal, setEditModal] = useState(null) // 'description', 'about', 'skills', 'experience', 'education', 'projects', 'recommendations'
  const [editingItem, setEditingItem] = useState(null) // For editing specific items
  const [formData, setFormData] = useState({})
  const [saving, setSaving] = useState(false)

  /* ── URL parsing ─────────────────────────────────────────── */
  const getUserIdFromUrl = () => {
    if (params.username && params.hashedId) {
      const parsed = parseProfileUrl(`profile/${params.username}-${params.hashedId}`)
      if (parsed.userId) return parsed.userId
    }
    if (params.userId) {
      const n = parseInt(params.userId)
      if (!isNaN(n)) return n
    }
    const parsed = parseProfileUrl(location.pathname)
    return parsed.userId
  }

  const userId = getUserIdFromUrl()

  const currentUserId =
    currentUser != null ? Number(currentUser.id ?? currentUser.uid) : null
  const currentUserIdValid = currentUserId != null && !Number.isNaN(currentUserId)

  /* ── Refetch profile when settings (or elsewhere) updates photos for this user ── */
  useEffect(() => {
    if (!userId) return
    const onUpdated = (e) => {
      const vid = e.detail?.userId
      if (vid == null || Number(vid) !== Number(userId)) return
      userAPI.getUserProfile(userId).then((r) => setProfile(r.data)).catch(() => {})
    }
    window.addEventListener('zedreq:profile-updated', onUpdated)
    return () => window.removeEventListener('zedreq:profile-updated', onUpdated)
  }, [userId])

  /* ── Data loading ────────────────────────────────────────── */
  useEffect(() => {
    if (userId) {
      loadProfile()
      checkConnectionStatus()
      loadUserPosts()
      loadFeaturedPosts()
      loadConnectionCounts()
      loadCertificates()
      loadProfileFeatures()
      loadSuggestions()
      trackProfileView()
    } else {
      setError('Invalid profile URL')
      setLoading(false)
    }
  }, [userId, location.pathname, location.key])

  const loadProfile = async () => {
    if (!userId) { setError('Invalid user ID'); setLoading(false); return }
    try {
      setLoading(true); setError(null)
      const response = await userAPI.getUserProfile(userId)
      setProfile(response.data)
      if (response.data && response.data.username && params.userId && !params.hashedId) {
        const newUrl = generateProfileUrl(userId, response.data.username)
        if (newUrl !== location.pathname) navigate(newUrl, { replace: true })
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const checkConnectionStatus = async () => {
    if (!currentUser || !userId || (currentUserIdValid && Number(userId) === currentUserId)) return
    try {
      // Check if already connected - API returns list of connected users with id/uid fields
      const connectionsResponse = await networkAPI.getConnections()
      const connections = connectionsResponse.data || connectionsResponse || []
      const isConnected = Array.isArray(connections) && connections.some(
        c => (c.id === userId || c.uid === userId || c.user_id === userId || c.connected_user_id === userId)
      )
      if (isConnected) { 
        setConnectionStatus('connected')
        return 
      }
      
      // Check for pending requests
      const pendingResponse = await connectionAPI.getPendingRequests()
      const sentResponse = await connectionAPI.getSentRequests()
      const pending = pendingResponse.data || pendingResponse || []
      const sent = sentResponse.data || sentResponse || []
      const hasPending = [...pending, ...sent].some(
        r => (r.sender_id === userId || r.receiver_id === userId)
      )
      setConnectionStatus(hasPending ? 'pending' : 'none')
    } catch (err) {
      console.error('Error checking connection status:', err)
      setConnectionStatus('none')
    }
  }

  const handleConnect = async () => {
    // Don't allow connecting if already connected or pending
    if (connectionStatus === 'connected' || connectionStatus === 'pending') {
      return
    }
    
    try {
      await connectionAPI.sendRequest(userId)
      setConnectionStatus('pending')
      // Refresh connection counts
      loadConnectionCounts()
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to send connection request'
      
      // If already connected, update status
      if (errorMessage.toLowerCase().includes('already connected')) {
        setConnectionStatus('connected')
        checkConnectionStatus() // Refresh status
      } else if (errorMessage.toLowerCase().includes('pending')) {
        setConnectionStatus('pending')
      } else {
        alert(errorMessage)
      }
    }
  }

  const loadConnectionCounts = async () => {
    if (!userId) return
    try {
      const r = await userAPI.getConnectionCounts(userId)
      setConnectionCounts(r.data)
    } catch { }
  }

  const loadCertificates = async () => {
    if (!userId) return
    try {
      setLoadingCertificates(true)
      const r = await userAPI.getUserCertificates(userId)
      setCertificates(r.data.certificates || [])
    } catch { setCertificates([]) }
    finally { setLoadingCertificates(false) }
  }

  const loadFeaturedPosts = async () => {
    if (!userId) return
    try {
      setLoadingFeatured(true)
      const r = await postAPI.getUserFeaturedPosts(userId, { limit: 6, offset: 0 })
      setFeaturedPosts(r.data?.posts || [])
    } catch { setFeaturedPosts([]) }
    finally { setLoadingFeatured(false) }
  }

  const loadProfileFeatures = async () => {
    if (!userId) return
    try {
      setLoadingFeatures(true)
      const [expRes, eduRes, projRes, recRes, intRes] = await Promise.allSettled([
        profileFeaturesAPI.getExperiences(userId, 50, 0),
        profileFeaturesAPI.getEducations(userId, 50, 0),
        profileFeaturesAPI.getProjects(userId, 50, 0),
        profileFeaturesAPI.getRecommendations(userId, 50, 0),
        profileFeaturesAPI.getInterests(userId, null, 50, 0)
      ])
      setExperiences(expRes.status === 'fulfilled' ? expRes.value.data?.experiences || [] : [])
      setEducations(eduRes.status === 'fulfilled' ? eduRes.value.data?.educations || [] : [])
      setProjects(projRes.status === 'fulfilled' ? projRes.value.data?.projects || [] : [])
      setRecommendations(recRes.status === 'fulfilled' ? recRes.value.data?.recommendations || [] : [])
      setInterests(intRes.status === 'fulfilled' ? intRes.value.data?.interests || [] : [])
    } catch {
      setExperiences([]); setEducations([]); setProjects([]); setRecommendations([]); setInterests([])
    } finally { setLoadingFeatures(false) }
  }

  const loadSuggestions = async () => {
    if (!currentUser || !isOwn) return
    try {
      setLoadingSuggestions(true)
      const response = await networkAPI.getSuggestions(20)
      setSuggestions(response.data || [])
    } catch {
      setSuggestions([])
    } finally {
      setLoadingSuggestions(false)
    }
  }

  const trackProfileView = async () => {
    if (!userId || !currentUser || (currentUserIdValid && Number(userId) === currentUserId)) return
    try {
      const fire = () => {
        profileFeaturesAPI.trackProfileView(userId, 'direct').catch(() => { })
        // Update context for profile view
        contextAPI.updateContext('view', 'profile', userId).catch(() => { })
      }
      if (window.requestIdleCallback) window.requestIdleCallback(fire, { timeout: 2000 })
      else setTimeout(fire, 100)
    } catch { }
  }

  const loadUserPosts = async () => {
    if (!userId) return
    try {
      setLoadingPosts(true)
      const r = await postAPI.getUserPosts(userId, { limit: 20, offset: 0 })
      setPosts(r.data?.posts || [])
    } catch { setPosts([]) }
    finally { setLoadingPosts(false) }
  }

  const handleLike = async (postId) => {
    try {
      const r = await postAPI.toggleLike(postId)
      setPosts(prev => prev.map(p =>
        (p.id === postId || p.post_id === postId)
          ? { ...p, is_liked: r.data.is_liked, like_count: r.data.like_count }
          : p
      ))
      
      // Update context if post was liked
      if (r.data.is_liked) {
        contextAPI.updateContext('like', 'post', postId)
      }
    } catch { }
  }

  /* ── Edit handlers ─────────────────────────────────────────── */
  const openEditModal = (section, item = null) => {
    setEditingItem(item)
    setEditModal(section)
    
    if (section === 'description') {
      setFormData({
        short_desc: profile.short_desc || '',
        current_status: profile.current_status || '',
        role: profile.role || '',
        company: profile.company || '',
        location: profile.location || '',
        industry: profile.industry || ''
      })
    } else if (section === 'about') {
      setFormData({ about: profile.about || '' })
    } else if (section === 'skills') {
      setFormData({ skills: skills.join(', ') })
    } else if (section === 'experience' && item) {
      setFormData({
        title: item.title || '',
        company: item.company || '',
        location: item.location || '',
        start_date: item.start_date ? item.start_date.split('T')[0] : '',
        end_date: item.end_date ? item.end_date.split('T')[0] : '',
        is_current: item.is_current || false,
        employment_type: item.employment_type || '',
        description: item.description || ''
      })
    } else if (section === 'education' && item) {
      setFormData({
        school: item.school || '',
        degree: item.degree || '',
        field_of_study: item.field_of_study || '',
        start_year: item.start_year || '',
        end_year: item.end_year || '',
        grade: item.grade || '',
        description: item.description || ''
      })
    } else if (section === 'projects' && item) {
      setFormData({
        title: item.title || '',
        description: item.description || '',
        url: item.url || '',
        associated_with: item.associated_with || '',
        technologies: Array.isArray(item.technologies) ? item.technologies.join(', ') : ''
      })
    } else if (section === 'recommendations' && item) {
      setFormData({
        recommendation_text: item.recommendation_text || '',
        relationship: item.relationship || ''
      })
    } else if (section === 'certificates') {
      // For certificates, we'll edit the legacy certificates field
      const certs = parseCertificates(profile.certificates || '')
      setFormData({
        certificates: certs.join('\n')
      })
    } else {
      setFormData({})
    }
  }

  const closeEditModal = () => {
    setEditModal(null)
    setEditingItem(null)
    setFormData({})
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      if (editModal === 'description') {
        // Use direct API call to update profile description fields via ProfileService
        const response = await api.put('/api/user/profile/description', {
          short_desc: formData.short_desc,
          current_status: formData.current_status,
          role: formData.role,
          company: formData.company,
          location: formData.location,
          industry: formData.industry
        })
        if (response.data) {
          setProfile(prev => ({ ...prev, ...response.data }))
        }
        await loadProfile() // Reload to get updated data
      } else if (editModal === 'about') {
        const response = await api.put('/api/user/profile/description', { about: formData.about })
        if (response.data) {
          setProfile(prev => ({ ...prev, about: formData.about }))
        }
        await loadProfile()
      } else if (editModal === 'skills') {
        const skillsArray = formData.skills.split(',').map(s => s.trim()).filter(Boolean)
        const response = await api.put('/api/user/profile/description', { skills: JSON.stringify(skillsArray) })
        if (response.data) {
          setProfile(prev => ({ ...prev, skills: JSON.stringify(skillsArray) }))
        }
        await loadProfile()
      } else if (editModal === 'experience') {
        if (editingItem) {
          await profileFeaturesAPI.updateExperience(editingItem.id, formData)
        } else {
          await profileFeaturesAPI.createExperience({ ...formData, user_id: userId })
        }
        await loadProfileFeatures()
      } else if (editModal === 'education') {
        if (editingItem) {
          await profileFeaturesAPI.updateEducation(editingItem.id, formData)
        } else {
          await profileFeaturesAPI.createEducation({ ...formData, user_id: userId })
        }
        await loadProfileFeatures()
      } else if (editModal === 'projects') {
        if (editingItem) {
          await profileFeaturesAPI.updateProject(editingItem.id, {
            ...formData,
            technologies: formData.technologies ? formData.technologies.split(',').map(t => t.trim()).filter(Boolean) : []
          })
        } else {
          await profileFeaturesAPI.createProject({
            ...formData,
            user_id: userId,
            technologies: formData.technologies ? formData.technologies.split(',').map(t => t.trim()).filter(Boolean) : []
          })
        }
        await loadProfileFeatures()
      } else if (editModal === 'recommendations') {
        if (editingItem) {
          await profileFeaturesAPI.updateRecommendation(editingItem.id, formData)
        } else {
          await profileFeaturesAPI.createRecommendation({ ...formData, user_id: userId })
        }
        await loadProfileFeatures()
      } else if (editModal === 'certificates') {
        // Update legacy certificates field
        const certsArray = formData.certificates.split('\n').map(c => c.trim()).filter(Boolean)
        const response = await api.put('/api/user/profile/description', { 
          certificates: certsArray.join('\n') 
        })
        if (response.data) {
          setProfile(prev => ({ ...prev, certificates: certsArray.join('\n') }))
        }
        await loadProfile()
      }
      
      closeEditModal()
    } catch (error) {
      alert(error.response?.data?.detail || error.message || 'Failed to save changes')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (section, itemId) => {
    if (!confirm('Are you sure you want to delete this item?')) return
    
    try {
      if (section === 'experience') {
        await profileFeaturesAPI.deleteExperience(itemId)
      } else if (section === 'education') {
        await profileFeaturesAPI.deleteEducation(itemId)
      } else if (section === 'projects') {
        await profileFeaturesAPI.deleteProject(itemId)
      } else if (section === 'recommendations') {
        await profileFeaturesAPI.deleteRecommendation(itemId)
      }
      await loadProfileFeatures()
    } catch (error) {
      alert(error.response?.data?.detail || error.message || 'Failed to delete item')
    }
  }

  /* ── Helpers ─────────────────────────────────────────────── */
  const parseSkills = (s) => {
    if (!s) return []
    try { const p = JSON.parse(s); return Array.isArray(p) ? p : [] }
    catch { return s.split(/[,\n]/).map(x => x.trim()).filter(Boolean) }
  }

  const parseCertificates = (s) => {
    if (!s) return []
    try { const p = JSON.parse(s); return Array.isArray(p) ? p : [s] }
    catch { return s.split('\n').map(x => x.trim()).filter(Boolean) }
  }

  const getTimeAgo = (d) => {
    if (!d) return ''
    try {
      const sec = Math.floor((Date.now() - new Date(d)) / 1000)
      if (isNaN(sec)) return ''
      if (sec < 60) return 'just now'
      if (sec < 3600) return `${Math.floor(sec / 60)}m ago`
      if (sec < 86400) return `${Math.floor(sec / 3600)}h ago`
      return `${Math.floor(sec / 86400)}d ago`
    } catch { return '' }
  }

  const formatDate = (d, opts = { year: 'numeric', month: 'short' }) => {
    if (!d) return ''
    try {
      const dt = new Date(d)
      return isNaN(dt.getTime()) ? d : dt.toLocaleDateString('en-US', opts)
    } catch { return d }
  }

  const escapeHtml = (t) => {
    if (!t) return ''
    const el = document.createElement('div')
    el.textContent = t
    return el.innerHTML
  }

  /* ── Loading state ───────────────────────────────────────── */
  if (loading) {
    return (
      <Page>
        <Navbar />
        <Shell>
          <div style={{ marginTop: 24 }}>
            <SkeletonBox $h="240px" $r="16px" style={{ marginBottom: 24 }} />
            <SkeletonBox $h="180px" $r="16px" style={{ marginBottom: 16 }} />
            <SkeletonBox $h="120px" $r="16px" />
          </div>
        </Shell>
      </Page>
    )
  }

  /* ── Error state ─────────────────────────────────────────── */
  if (error || !profile) {
    return (
      <Page>
        <Navbar />
        <ErrorBox>
          <h2>Profile Not Found</h2>
          <p>{error || 'The user you are looking for does not exist.'}</p>
        </ErrorBox>
      </Page>
    )
  }

  /* ── Derived data ────────────────────────────────────────── */
  const isOwn =
    currentUserIdValid && userId != null && currentUserId === Number(userId)
  const displayCoverPic =
    profile.cover_pic ?? (isOwn ? currentUser?.cover_pic : null)
  const displayProfilePic =
    profile.profile_pic ?? (isOwn ? currentUser?.profile_pic : null)
  const skills = parseSkills(profile.skills)
  const legacyCerts = parseCertificates(profile.certificates || '')
  const initials = profile.name
    ? profile.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : 'U'

  const interestIcons = { company: '🏢', group: '👥', influencer: '⭐', school: '🎓' }

  /* ── Tab content renderers ───────────────────────────────── */

  const renderAbout = () => (
    <TabPanel key="about">
      {/* Description / Headline */}
      {(profile.short_desc || profile.current_status || profile.role || profile.location || profile.industry || isOwn) && (
        <Card>
          <CardHeader>
            <CardTitle>Description</CardTitle>
            {isOwn && (
              <EditButton onClick={() => openEditModal('description')}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
                Edit
              </EditButton>
            )}
          </CardHeader>
          {profile.short_desc && (
            <CardText style={{ fontSize: '1.05em', marginBottom: 14 }}>{profile.short_desc}</CardText>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: profile.short_desc ? 0 : 0 }}>
            {profile.current_status && (
              <SubInfo style={{ margin: 0 }}>🎯 {profile.current_status}</SubInfo>
            )}
            {profile.role && (
              <SubInfo style={{ margin: 0 }}>💼 {profile.role}{profile.company ? ` at ${profile.company}` : ''}</SubInfo>
            )}
            {profile.location && (
              <SubInfo style={{ margin: 0 }}>📍 {profile.location}</SubInfo>
            )}
            {profile.industry && (
              <SubInfo style={{ margin: 0 }}>🏢 {profile.industry}</SubInfo>
            )}
          </div>
        </Card>
      )}

      {/* About */}
      {(profile.about && profile.about.trim() || isOwn) && (
        <Card>
          <CardHeader>
            <CardTitle>About</CardTitle>
            {isOwn && (
              <EditButton onClick={() => openEditModal('about')}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
                Edit
              </EditButton>
            )}
          </CardHeader>
          {profile.about && profile.about.trim() ? (
            <CardText>{profile.about}</CardText>
          ) : (
            <EmptyState>No about section yet. Click Edit to add one.</EmptyState>
          )}
        </Card>
      )}

      {/* Skills */}
      {(skills.length > 0 || isOwn) && (
        <Card>
          <CardHeader>
            <CardTitle>Skills</CardTitle>
            {isOwn && (
              <EditButton onClick={() => openEditModal('skills')}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
                Edit
              </EditButton>
            )}
          </CardHeader>
          {skills.length > 0 ? (
            <ChipsWrap>
              {skills.map((s, i) => <Chip key={i}>{s}</Chip>)}
            </ChipsWrap>
          ) : (
            <EmptyState>No skills yet. Click Edit to add skills.</EmptyState>
          )}
        </Card>
      )}

      {/* Certificates */}
      <Card>
        <CardHeader>
          <CardTitle>Licenses & Certifications</CardTitle>
          {isOwn && (
            <EditButton onClick={() => openEditModal('certificates')}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
              Edit
            </EditButton>
          )}
        </CardHeader>
        {loadingCertificates ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <SkeletonBox $h="60px" />
            <SkeletonBox $h="60px" />
          </div>
        ) : (certificates.length > 0 || legacyCerts.length > 0) ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {certificates.map(c => (
              <CertCard key={c.id}>
                <h4>{c.title || c.course_title}</h4>
                {c.issued_at && <CertMeta>Issued: {formatDate(c.issued_at, { year: 'numeric', month: 'long', day: 'numeric' })}</CertMeta>}
                {c.expiry_date && <CertMeta>Expires: {formatDate(c.expiry_date, { year: 'numeric', month: 'long', day: 'numeric' })}</CertMeta>}
                {c.pdf_url && <CertLink href={c.pdf_url} target="_blank" rel="noopener noreferrer">View Certificate PDF</CertLink>}
              </CertCard>
            ))}
            {certificates.length === 0 && legacyCerts.map((c, i) => (
              <CertCard key={`l-${i}`}><h4>{c}</h4></CertCard>
            ))}
          </div>
        ) : (
          <EmptyState>No certificates yet</EmptyState>
        )}
      </Card>

      {/* Interests */}
      {interests.length > 0 && (
        <Card>
          <CardTitle>Interests</CardTitle>
          <ChipsWrap>
            {interests.map(int => (
              <InterestBadge key={int.id}>
                <span>{interestIcons[int.interest_type] || '•'}</span>
                {int.url ? (
                  <a href={int.url} target="_blank" rel="noopener noreferrer"
                    onClick={e => { try { new URL(int.url) } catch { e.preventDefault() } }}
                  >{int.name}</a>
                ) : <span>{int.name}</span>}
              </InterestBadge>
            ))}
          </ChipsWrap>
        </Card>
      )}

      {/* Profile Info */}
      <Card>
        <CardTitle>Profile Information</CardTitle>
        <InfoRow>
          <strong>Member since</strong>
          <span>{profile.created_at ? formatDate(profile.created_at, { year: 'numeric', month: 'long' }) : 'N/A'}</span>
        </InfoRow>
        {profile.email && (
          <InfoRow>
            <strong>Email</strong>
            <span>{profile.email}</span>
          </InfoRow>
        )}
      </Card>
    </TabPanel>
  )

  const renderExperience = () => (
    <TabPanel key="experience">
      <Card>
        <CardHeader>
          <CardTitle>Experience</CardTitle>
          {isOwn && (
            <EditButton onClick={() => openEditModal('experience')}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              Add
            </EditButton>
          )}
        </CardHeader>
        {loadingFeatures ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {[1, 2, 3].map(i => <SkeletonBox key={i} $h="80px" />)}
          </div>
        ) : experiences.length > 0 ? (
          <Timeline>
            {experiences.map(exp => (
              <TimelineItem key={exp.id} $color="var(--primary)">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <div style={{ flex: 1 }}>
                    <TLTitle>{exp.title || 'Untitled Position'}</TLTitle>
                    <TLSub>{exp.company || 'Unknown Company'}</TLSub>
                    {exp.location && <TLDate>📍 {exp.location}</TLDate>}
                    <TLDate>
                      {exp.start_date ? formatDate(exp.start_date) : ''}
                      {' — '}
                      {exp.is_current ? 'Present' : (exp.end_date ? formatDate(exp.end_date) : '')}
                      {exp.employment_type && ` · ${exp.employment_type}`}
                    </TLDate>
                    {exp.description && <TLDesc>{exp.description}</TLDesc>}
                  </div>
                  {isOwn && (
                    <div style={{ display: 'flex', gap: 8, marginLeft: 12 }}>
                      <EditButton onClick={() => openEditModal('experience', exp)} style={{ padding: '4px 8px', fontSize: '0.8em' }}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '12px', height: '12px' }}>
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                      </EditButton>
                      <EditButton onClick={() => handleDelete('experience', exp.id)} style={{ padding: '4px 8px', fontSize: '0.8em', color: '#dc3545', borderColor: '#dc3545' }}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '12px', height: '12px' }}>
                          <polyline points="3 6 5 6 21 6"></polyline>
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                      </EditButton>
                    </div>
                  )}
                </div>
              </TimelineItem>
            ))}
          </Timeline>
        ) : (
          <EmptyState>No experience entries yet</EmptyState>
        )}
      </Card>

    </TabPanel>
  )

  const renderRecommendations = () => {
    // For own profile, show friend-of-friend suggestions
    if (isOwn) {
      return (
        <TabPanel key="recommendations">
          <Card>
            <CardHeader>
              <CardTitle>People You May Know</CardTitle>
            </CardHeader>
            {loadingSuggestions ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {[1, 2, 3, 4].map(i => <SkeletonBox key={i} $h="120px" />)}
              </div>
            ) : suggestions.length > 0 ? (
              <PeopleGrid>
                {suggestions.map(user => {
                  const userConnectionStatus = connectionStatus // This would need to be per-user, simplified for now
                  return (
                    <PersonCard key={user.id || user.uid}>
                      <PersonContent>
                        <PersonAvatar src={user.profile_pic}>
                          {!user.profile_pic && (user.name || user.full_name)?.charAt(0).toUpperCase()}
                        </PersonAvatar>
                        <PersonName>{user.name || user.full_name}</PersonName>
                        <PersonTitle>@{user.username}</PersonTitle>
                        {user.job_title && user.company && (
                          <PersonCompany>
                            {user.job_title} at {user.company}
                          </PersonCompany>
                        )}
                        {user.mutual_connections > 0 && (
                          <MutualConnections>
                            {user.mutual_connections} mutual connection{user.mutual_connections > 1 ? 's' : ''}
                            {user.mutual_connection_names?.length > 0 && (
                              <> including {user.mutual_connection_names.slice(0, 2).join(', ')}</>
                            )}
                          </MutualConnections>
                        )}
                        <ButtonGroup style={{ marginTop: 12 }}>
                          <ConnectButton 
                            onClick={() => handleConnect(user.id || user.uid)}
                            pending={userConnectionStatus === 'pending'}
                            disabled={userConnectionStatus === 'pending' || userConnectionStatus === 'connected'}
                          >
                            {userConnectionStatus === 'pending' ? 'Pending...' : userConnectionStatus === 'connected' ? 'Connected' : 'Connect'}
                          </ConnectButton>
                        </ButtonGroup>
                      </PersonContent>
                    </PersonCard>
                  )
                })}
              </PeopleGrid>
            ) : (
              <EmptyState>No suggestions available. Connect with more people to see friend-of-friend suggestions.</EmptyState>
            )}
          </Card>
        </TabPanel>
      )
    }

    // For other users, show recommendations
    return (
      <TabPanel key="recommendations">
        <Card>
          <CardHeader>
            <CardTitle>Recommendations</CardTitle>
          </CardHeader>
          {loadingFeatures ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {[1, 2, 3].map(i => <SkeletonBox key={i} $h="80px" />)}
            </div>
          ) : recommendations.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {recommendations.map(rec => (
                <RecCard key={rec.id}>
                  <RecText>"{rec.recommendation_text}"</RecText>
                  {rec.recommender && (
                    <RecAuthor>
                      — {rec.recommender.name || rec.recommender.username}
                      {rec.relationship && `, ${rec.relationship}`}
                    </RecAuthor>
                  )}
                </RecCard>
              ))}
            </div>
          ) : (
            <EmptyState>No recommendations yet</EmptyState>
          )}
        </Card>
      </TabPanel>
    )
  }

  const renderEducation = () => (
    <TabPanel key="education">
      <Card>
        <CardHeader>
          <CardTitle>Education</CardTitle>
          {isOwn && (
            <EditButton onClick={() => openEditModal('education')}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              Add
            </EditButton>
          )}
        </CardHeader>
        {loadingFeatures ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {[1, 2].map(i => <SkeletonBox key={i} $h="80px" />)}
          </div>
        ) : educations.length > 0 ? (
          <Timeline>
            {educations.map(edu => (
              <TimelineItem key={edu.id} $color="var(--secondary)">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <div style={{ flex: 1 }}>
                    <TLTitle>{edu.school || 'Unknown School'}</TLTitle>
                    {edu.degree && <TLSub>{edu.degree}</TLSub>}
                    {edu.field_of_study && <TLSub>{edu.field_of_study}</TLSub>}
                    <TLDate>
                      {edu.start_year && `${edu.start_year}`}
                      {edu.end_year && ` — ${edu.end_year}`}
                      {!edu.end_year && edu.start_year && ' — Present'}
                      {edu.grade && ` · Grade: ${edu.grade}`}
                    </TLDate>
                    {edu.description && <TLDesc>{edu.description}</TLDesc>}
                  </div>
                  {isOwn && (
                    <div style={{ display: 'flex', gap: 8, marginLeft: 12 }}>
                      <EditButton onClick={() => openEditModal('education', edu)} style={{ padding: '4px 8px', fontSize: '0.8em' }}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '12px', height: '12px' }}>
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                      </EditButton>
                      <EditButton onClick={() => handleDelete('education', edu.id)} style={{ padding: '4px 8px', fontSize: '0.8em', color: '#dc3545', borderColor: '#dc3545' }}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '12px', height: '12px' }}>
                          <polyline points="3 6 5 6 21 6"></polyline>
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                      </EditButton>
                    </div>
                  )}
                </div>
              </TimelineItem>
            ))}
          </Timeline>
        ) : (
          <EmptyState>No education entries yet</EmptyState>
        )}
      </Card>
    </TabPanel>
  )

  const renderProjects = () => (
    <TabPanel key="projects">
      <Card>
        <CardHeader>
          <CardTitle>Projects</CardTitle>
          {isOwn && (
            <EditButton onClick={() => openEditModal('projects')}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              Add
            </EditButton>
          )}
        </CardHeader>
        {loadingFeatures ? (
          <ProjectsGrid>
            {[1, 2, 3].map(i => <SkeletonBox key={i} $h="140px" $r="14px" />)}
          </ProjectsGrid>
        ) : projects.length > 0 ? (
          <ProjectsGrid>
            {projects.map(proj => (
              <ProjectCard key={proj.id}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <ProjTitle style={{ flex: 1 }}>{proj.title}</ProjTitle>
                  {isOwn && (
                    <div style={{ display: 'flex', gap: 6, marginLeft: 8 }}>
                      <EditButton onClick={() => openEditModal('projects', proj)} style={{ padding: '4px 8px', fontSize: '0.75em' }}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '12px', height: '12px' }}>
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                      </EditButton>
                      <EditButton onClick={() => handleDelete('projects', proj.id)} style={{ padding: '4px 8px', fontSize: '0.75em', color: '#dc3545', borderColor: '#dc3545' }}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '12px', height: '12px' }}>
                          <polyline points="3 6 5 6 21 6"></polyline>
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                      </EditButton>
                    </div>
                  )}
                </div>
                {proj.description && <ProjDesc>{proj.description}</ProjDesc>}
                {proj.associated_with && (
                  <TLDate>Associated with: {proj.associated_with}</TLDate>
                )}
                {proj.url && (
                  <ProjLink href={proj.url} target="_blank" rel="noopener noreferrer"
                    onClick={e => { try { new URL(proj.url) } catch { e.preventDefault() } }}
                  >View Project →</ProjLink>
                )}
                {proj.technologies && Array.isArray(proj.technologies) && proj.technologies.length > 0 && (
                  <TechTags>
                    {proj.technologies.map((t, i) => <TechTag key={i}>{t}</TechTag>)}
                  </TechTags>
                )}
              </ProjectCard>
            ))}
          </ProjectsGrid>
        ) : (
          <EmptyState>No projects yet</EmptyState>
        )}
      </Card>
    </TabPanel>
  )

  const renderPosts = () => (
    <TabPanel key="posts">
      {/* Featured */}
      {featuredPosts.length > 0 && (
        <Card>
          <CardTitle>Featured</CardTitle>
          <FeatGrid>
            {featuredPosts.map(p => (
              <FeatThumb key={p.id || p.post_id} onClick={() => navigate(`/post/${p.id || p.post_id}`)}>
                {p.media_type === 'video'
                  ? <video src={p.media_url} preload="metadata" />
                  : <img src={p.media_url} alt="Featured" loading="lazy" />
                }
              </FeatThumb>
            ))}
          </FeatGrid>
        </Card>
      )}

      {/* Posts */}
      <Card>
        <CardTitle>Posts</CardTitle>
        {loadingPosts ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {[1, 2, 3].map(i => <SkeletonBox key={i} $h="120px" $r="12px" />)}
          </div>
        ) : posts.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {posts.map(post => (
              <PostCard key={post.id || post.post_id}>
                <PostHead>
                  <PostAv>{post.full_name ? post.full_name.charAt(0).toUpperCase() : 'U'}</PostAv>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 500, color: 'var(--text)', fontSize: '0.95em', marginBottom: 2 }}>
                      {post.full_name || post.name || post.username}
                    </div>
                    <div style={{ fontSize: '0.82em', color: 'var(--text-lighter)' }}>{getTimeAgo(post.created_at)}</div>
                  </div>
                </PostHead>
                <PostBody dangerouslySetInnerHTML={{ __html: escapeHtml(post.content || post.post_desc) }} />
                {post.media_url && (
                  <PostMedia>
                    {post.media_type === 'video'
                      ? <video src={post.media_url} controls preload="metadata" />
                      : <img src={post.media_url} alt="Post media" loading="lazy" />
                    }
                  </PostMedia>
                )}
                <PostFooter>
                  <LikeBtn $liked={post.is_liked} onClick={() => handleLike(post.id || post.post_id)}>
                    <svg viewBox="0 0 24 24" fill={post.is_liked ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                    </svg>
                    {post.like_count || post.likes || 0}
                  </LikeBtn>
                </PostFooter>
              </PostCard>
            ))}
          </div>
        ) : (
          <EmptyState>No posts yet</EmptyState>
        )}
      </Card>
    </TabPanel>
  )

  const tabRenderers = { About: renderAbout, Experience: renderExperience, Education: renderEducation, Projects: renderProjects, Recommendations: renderRecommendations, Posts: renderPosts }

  /* ── Main Render ─────────────────────────────────────────── */
  return (
    <Page>
      <Navbar />

      <Shell>
        {/* Cover Photo */}
        <CoverWrap key={displayCoverPic || 'cover'} $src={displayCoverPic} />

        {/* Header Card */}
        <HeaderCard>
          <AvatarRow>
            <AvatarCircle>
              {displayProfilePic
                ? <img key={displayProfilePic} src={displayProfilePic} alt={profile.name} />
                : <AvatarFallback>{initials}</AvatarFallback>
              }
            </AvatarCircle>
            <HeaderMeta>
              <UserName>{profile.name || 'No Name'}</UserName>
              {profile.short_desc && <Headline>{profile.short_desc}</Headline>}
              {profile.role && profile.company && (
                <SubInfo>{profile.role} at {profile.company}</SubInfo>
              )}
              {!profile.role && profile.current_status && (
                <SubInfo>{profile.current_status}</SubInfo>
              )}
              {profile.location && <SubInfo>📍 {profile.location}</SubInfo>}
              {profile.industry && <SubInfo>🏢 {profile.industry}</SubInfo>}
            </HeaderMeta>
          </AvatarRow>

          {/* Stats */}
          <StatsRow>
            <Stat onClick={() => navigate('/network')}>
              <StatNum>{connectionCounts.followers}</StatNum>
              <StatLabel>Followers</StatLabel>
            </Stat>
            <Stat onClick={() => navigate('/network')}>
              <StatNum>{connectionCounts.following}</StatNum>
              <StatLabel>Following</StatLabel>
            </Stat>
            <Stat onClick={() => navigate('/network')}>
              <StatNum>{connectionCounts.connections}</StatNum>
              <StatLabel>Connections</StatLabel>
            </Stat>
          </StatsRow>

          {/* Action Pills */}
          {!isOwn && (
            <Pills>
              {connectionStatus === 'none' && (
                <Pill $solid onClick={handleConnect}>Connect</Pill>
              )}
              {connectionStatus === 'pending' && (
                <Pill disabled>Request Sent</Pill>
              )}
              {connectionStatus === 'connected' && (
                <Pill>✓ Connected</Pill>
              )}
              <Pill onClick={() => navigate('/messages')}>Message</Pill>
              {profile.email && (
                <Pill onClick={() => setShowContactModal(true)}>Contact</Pill>
              )}
            </Pills>
          )}

          {/* Tab Bar */}
          <TabBar>
            {TABS.map(t => (
              <Tab key={t} $active={activeTab === t} onClick={() => setActiveTab(t)}>
                {t}
              </Tab>
            ))}
          </TabBar>
        </HeaderCard>

        {/* Active Tab Content */}
        {tabRenderers[activeTab]?.()}
      </Shell>

      {/* Contact Modal */}
      {showContactModal && (
        <Overlay onClick={() => setShowContactModal(false)}>
          <Modal onClick={e => e.stopPropagation()}>
            <ModalHead>
              <h2>Contact Information</h2>
              <button onClick={() => setShowContactModal(false)}>×</button>
            </ModalHead>
            <InfoRow>
              <strong>Email</strong>
              <span>{profile.email || profile.user_email || 'Not available'}</span>
            </InfoRow>
            {profile.username && (
              <InfoRow>
                <strong>Username</strong>
                <span>@{profile.username}</span>
              </InfoRow>
            )}
          </Modal>
        </Overlay>
      )}

      {/* Edit Modals */}
      {editModal && (
        <Overlay onClick={closeEditModal}>
          <EditModal onClick={e => e.stopPropagation()}>
            <ModalHead>
              <h2>
                {editModal === 'description' && 'Edit Description'}
                {editModal === 'about' && 'Edit About'}
                {editModal === 'skills' && 'Edit Skills'}
                {editModal === 'experience' && (editingItem ? 'Edit Experience' : 'Add Experience')}
                {editModal === 'education' && (editingItem ? 'Edit Education' : 'Add Education')}
                {editModal === 'projects' && (editingItem ? 'Edit Project' : 'Add Project')}
                {editModal === 'recommendations' && (editingItem ? 'Edit Recommendation' : 'Add Recommendation')}
                {editModal === 'certificates' && 'Edit Certificates'}
              </h2>
              <button onClick={closeEditModal}>×</button>
            </ModalHead>

            {editModal === 'description' && (
              <>
                <FormGroup>
                  <label>Short Description / Headline</label>
                  <textarea
                    value={formData.short_desc || ''}
                    onChange={e => setFormData({ ...formData, short_desc: e.target.value })}
                    placeholder="e.g., Software Engineer passionate about AI"
                    rows={3}
                  />
                </FormGroup>
                <FormGroup>
                  <label>Current Status</label>
                  <input
                    type="text"
                    value={formData.current_status || ''}
                    onChange={e => setFormData({ ...formData, current_status: e.target.value })}
                    placeholder="e.g., Open to opportunities"
                  />
                </FormGroup>
                <FormGroup>
                  <label>Role</label>
                  <input
                    type="text"
                    value={formData.role || ''}
                    onChange={e => setFormData({ ...formData, role: e.target.value })}
                    placeholder="e.g., Senior Software Engineer"
                  />
                </FormGroup>
                <FormGroup>
                  <label>Company</label>
                  <input
                    type="text"
                    value={formData.company || ''}
                    onChange={e => setFormData({ ...formData, company: e.target.value })}
                    placeholder="e.g., Tech Corp"
                  />
                </FormGroup>
                <FormGroup>
                  <label>Location</label>
                  <input
                    type="text"
                    value={formData.location || ''}
                    onChange={e => setFormData({ ...formData, location: e.target.value })}
                    placeholder="e.g., San Francisco, CA"
                  />
                </FormGroup>
                <FormGroup>
                  <label>Industry</label>
                  <input
                    type="text"
                    value={formData.industry || ''}
                    onChange={e => setFormData({ ...formData, industry: e.target.value })}
                    placeholder="e.g., Technology"
                  />
                </FormGroup>
              </>
            )}

            {editModal === 'about' && (
              <FormGroup>
                <label>About</label>
                <textarea
                  value={formData.about || ''}
                  onChange={e => setFormData({ ...formData, about: e.target.value })}
                  placeholder="Tell us about yourself..."
                  rows={8}
                />
              </FormGroup>
            )}

            {editModal === 'skills' && (
              <FormGroup>
                <label>Skills (comma-separated)</label>
                <input
                  type="text"
                  value={formData.skills || ''}
                  onChange={e => setFormData({ ...formData, skills: e.target.value })}
                  placeholder="e.g., JavaScript, Python, React, Node.js"
                />
                <small>Separate multiple skills with commas</small>
              </FormGroup>
            )}

            {editModal === 'experience' && (
              <>
                <FormGroup>
                  <label>Job Title *</label>
                  <input
                    type="text"
                    value={formData.title || ''}
                    onChange={e => setFormData({ ...formData, title: e.target.value })}
                    placeholder="e.g., Software Engineer"
                    required
                  />
                </FormGroup>
                <FormGroup>
                  <label>Company *</label>
                  <input
                    type="text"
                    value={formData.company || ''}
                    onChange={e => setFormData({ ...formData, company: e.target.value })}
                    placeholder="e.g., Tech Corp"
                    required
                  />
                </FormGroup>
                <FormGroup>
                  <label>Location</label>
                  <input
                    type="text"
                    value={formData.location || ''}
                    onChange={e => setFormData({ ...formData, location: e.target.value })}
                    placeholder="e.g., San Francisco, CA"
                  />
                </FormGroup>
                <FormGroup>
                  <label>Employment Type</label>
                  <select
                    value={formData.employment_type || ''}
                    onChange={e => setFormData({ ...formData, employment_type: e.target.value })}
                  >
                    <option value="">Select type</option>
                    <option value="Full-time">Full-time</option>
                    <option value="Part-time">Part-time</option>
                    <option value="Contract">Contract</option>
                    <option value="Internship">Internship</option>
                    <option value="Freelance">Freelance</option>
                  </select>
                </FormGroup>
                <FormGroup>
                  <label>Start Date</label>
                  <input
                    type="date"
                    value={formData.start_date || ''}
                    onChange={e => setFormData({ ...formData, start_date: e.target.value })}
                  />
                </FormGroup>
                <FormGroup>
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.is_current || false}
                      onChange={e => setFormData({ ...formData, is_current: e.target.checked, end_date: e.target.checked ? '' : formData.end_date })}
                    />
                    {' '}I currently work here
                  </label>
                </FormGroup>
                {!formData.is_current && (
                  <FormGroup>
                    <label>End Date</label>
                    <input
                      type="date"
                      value={formData.end_date || ''}
                      onChange={e => setFormData({ ...formData, end_date: e.target.value })}
                    />
                  </FormGroup>
                )}
                <FormGroup>
                  <label>Description</label>
                  <textarea
                    value={formData.description || ''}
                    onChange={e => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Describe your role and achievements..."
                    rows={5}
                  />
                </FormGroup>
              </>
            )}

            {editModal === 'education' && (
              <>
                <FormGroup>
                  <label>School / University *</label>
                  <input
                    type="text"
                    value={formData.school || ''}
                    onChange={e => setFormData({ ...formData, school: e.target.value })}
                    placeholder="e.g., Stanford University"
                    required
                  />
                </FormGroup>
                <FormGroup>
                  <label>Degree</label>
                  <input
                    type="text"
                    value={formData.degree || ''}
                    onChange={e => setFormData({ ...formData, degree: e.target.value })}
                    placeholder="e.g., Bachelor of Science"
                  />
                </FormGroup>
                <FormGroup>
                  <label>Field of Study</label>
                  <input
                    type="text"
                    value={formData.field_of_study || ''}
                    onChange={e => setFormData({ ...formData, field_of_study: e.target.value })}
                    placeholder="e.g., Computer Science"
                  />
                </FormGroup>
                <FormGroup>
                  <label>Start Year</label>
                  <input
                    type="number"
                    value={formData.start_year || ''}
                    onChange={e => setFormData({ ...formData, start_year: e.target.value })}
                    placeholder="e.g., 2018"
                    min="1900"
                    max={new Date().getFullYear()}
                  />
                </FormGroup>
                <FormGroup>
                  <label>End Year</label>
                  <input
                    type="number"
                    value={formData.end_year || ''}
                    onChange={e => setFormData({ ...formData, end_year: e.target.value })}
                    placeholder="e.g., 2022"
                    min="1900"
                    max={new Date().getFullYear() + 10}
                  />
                </FormGroup>
                <FormGroup>
                  <label>Grade / GPA</label>
                  <input
                    type="text"
                    value={formData.grade || ''}
                    onChange={e => setFormData({ ...formData, grade: e.target.value })}
                    placeholder="e.g., 3.8 GPA"
                  />
                </FormGroup>
                <FormGroup>
                  <label>Description</label>
                  <textarea
                    value={formData.description || ''}
                    onChange={e => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Additional details..."
                    rows={4}
                  />
                </FormGroup>
              </>
            )}

            {editModal === 'projects' && (
              <>
                <FormGroup>
                  <label>Project Title *</label>
                  <input
                    type="text"
                    value={formData.title || ''}
                    onChange={e => setFormData({ ...formData, title: e.target.value })}
                    placeholder="e.g., E-commerce Platform"
                    required
                  />
                </FormGroup>
                <FormGroup>
                  <label>Description</label>
                  <textarea
                    value={formData.description || ''}
                    onChange={e => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Describe your project..."
                    rows={5}
                  />
                </FormGroup>
                <FormGroup>
                  <label>Project URL</label>
                  <input
                    type="url"
                    value={formData.url || ''}
                    onChange={e => setFormData({ ...formData, url: e.target.value })}
                    placeholder="https://example.com"
                  />
                </FormGroup>
                <FormGroup>
                  <label>Associated With</label>
                  <input
                    type="text"
                    value={formData.associated_with || ''}
                    onChange={e => setFormData({ ...formData, associated_with: e.target.value })}
                    placeholder="e.g., Company name or organization"
                  />
                </FormGroup>
                <FormGroup>
                  <label>Technologies (comma-separated)</label>
                  <input
                    type="text"
                    value={formData.technologies || ''}
                    onChange={e => setFormData({ ...formData, technologies: e.target.value })}
                    placeholder="e.g., React, Node.js, MongoDB"
                  />
                </FormGroup>
              </>
            )}

            {editModal === 'recommendations' && (
              <>
                <FormGroup>
                  <label>Recommendation Text *</label>
                  <textarea
                    value={formData.recommendation_text || ''}
                    onChange={e => setFormData({ ...formData, recommendation_text: e.target.value })}
                    placeholder="Enter the recommendation text..."
                    rows={6}
                    required
                  />
                </FormGroup>
                <FormGroup>
                  <label>Relationship</label>
                  <input
                    type="text"
                    value={formData.relationship || ''}
                    onChange={e => setFormData({ ...formData, relationship: e.target.value })}
                    placeholder="e.g., Former Manager, Colleague"
                  />
                </FormGroup>
              </>
            )}

            {editModal === 'certificates' && (
              <FormGroup>
                <label>Certificates (one per line)</label>
                <textarea
                  value={formData.certificates || ''}
                  onChange={e => setFormData({ ...formData, certificates: e.target.value })}
                  placeholder="Enter certificates, one per line:&#10;AWS Certified Solutions Architect&#10;Google Cloud Professional&#10;Microsoft Azure Fundamentals"
                  rows={8}
                />
                <small>Enter each certificate on a new line. These are legacy certificates (non-LMS).</small>
              </FormGroup>
            )}

            <FormActions>
              <Button className="secondary" onClick={closeEditModal} disabled={saving}>
                Cancel
              </Button>
              <Button className="primary" onClick={handleSave} disabled={saving}>
                {saving ? 'Saving...' : 'Save'}
              </Button>
            </FormActions>
          </EditModal>
        </Overlay>
      )}
    </Page>
  )
}

export default Profile
