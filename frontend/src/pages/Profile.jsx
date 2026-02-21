import React, { useState, useEffect } from 'react'
import styled, { keyframes, css } from 'styled-components'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { userAPI, connectionAPI, postAPI, profileFeaturesAPI, contextAPI } from '../services/api'
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
  @media (max-width: 480px) { padding: 0 12px 40px; }
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

  @media (max-width: 768px) { height: 200px; }
  @media (max-width: 480px) { height: 160px; }
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
  padding: 0 32px 32px;
  animation: ${slideUp} 0.55s ease;
  transition: background-color 0.3s ease, border-color 0.3s ease;

  @media (max-width: 768px) {
    margin-top: -80px;
    padding: 0 20px 24px;
    border-radius: 16px;
  }
  @media (max-width: 480px) {
    margin-top: -60px;
    padding: 0 16px 20px;
    border-radius: 14px;
  }
`

const AvatarRow = styled.div`
  display: flex;
  align-items: flex-end;
  gap: 24px;
  margin-top: -60px;
  margin-bottom: 20px;
  flex-wrap: wrap;

  @media (max-width: 768px) {
    margin-top: -50px;
    gap: 16px;
  }
  @media (max-width: 480px) {
    margin-top: -40px;
    gap: 12px;
    flex-direction: column;
    align-items: center;
    text-align: center;
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

  @media (max-width: 768px) { width: 110px; height: 110px; }
  @media (max-width: 480px) { width: 96px; height: 96px; }
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
  @media (max-width: 480px) { padding-top: 8px; }
`

const UserName = styled.h1`
  font-size: 1.85em;
  font-weight: 500;
  color: var(--text);
  margin: 0 0 4px;
  line-height: 1.2;
  @media (max-width: 768px) { font-size: 1.5em; }
  @media (max-width: 480px) { font-size: 1.35em; }
`

const Headline = styled.p`
  font-size: 1.05em;
  color: var(--text-light);
  margin: 0 0 6px;
  @media (max-width: 480px) { font-size: 0.95em; }
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
  -webkit-overflow-scrolling: touch;

  &::-webkit-scrollbar { display: none; }
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

const CardTitle = styled.h2`
  font-size: 1.15em;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 18px;
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
      trackProfileView()
    } else {
      setError('Invalid profile URL')
      setLoading(false)
    }
  }, [userId, location.pathname])

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
    if (!currentUser || !userId || userId === currentUser.id) return
    try {
      const connections = await connectionAPI.getConnections()
      const isConnected = connections.data?.some(c => c.user_id === userId || c.connected_user_id === userId)
      if (isConnected) { setConnectionStatus('connected'); return }
      const pending = await connectionAPI.getPendingRequests()
      const sent = await connectionAPI.getSentRequests()
      const hasPending = [...(pending.data || []), ...(sent.data || [])].some(
        r => r.sender_id === userId || r.receiver_id === userId
      )
      setConnectionStatus(hasPending ? 'pending' : 'none')
    } catch { setConnectionStatus('none') }
  }

  const handleConnect = async () => {
    try {
      await connectionAPI.sendRequest(userId)
      setConnectionStatus('pending')
    } catch (err) {
      alert(err.response?.data?.detail || err.message || 'Failed to send connection request')
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

  const trackProfileView = async () => {
    if (!userId || !currentUser || userId === currentUser.id) return
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
  const isOwn = currentUser && currentUser.id === userId
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
      {(profile.short_desc || profile.current_status || profile.role || profile.location || profile.industry) && (
        <Card>
          <CardTitle>Description</CardTitle>
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
      {profile.about && profile.about.trim() && (
        <Card>
          <CardTitle>About</CardTitle>
          <CardText>{profile.about}</CardText>
        </Card>
      )}

      {/* Skills */}
      {skills.length > 0 && (
        <Card>
          <CardTitle>Skills</CardTitle>
          <ChipsWrap>
            {skills.map((s, i) => <Chip key={i}>{s}</Chip>)}
          </ChipsWrap>
        </Card>
      )}

      {/* Certificates */}
      <Card>
        <CardTitle>Licenses & Certifications</CardTitle>
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
        <CardTitle>Experience</CardTitle>
        {loadingFeatures ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {[1, 2, 3].map(i => <SkeletonBox key={i} $h="80px" />)}
          </div>
        ) : experiences.length > 0 ? (
          <Timeline>
            {experiences.map(exp => (
              <TimelineItem key={exp.id} $color="var(--primary)">
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
              </TimelineItem>
            ))}
          </Timeline>
        ) : (
          <EmptyState>No experience entries yet</EmptyState>
        )}
      </Card>

    </TabPanel>
  )

  const renderRecommendations = () => (
    <TabPanel key="recommendations">
      <Card>
        <CardTitle>Recommendations</CardTitle>
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

  const renderEducation = () => (
    <TabPanel key="education">
      <Card>
        <CardTitle>Education</CardTitle>
        {loadingFeatures ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {[1, 2].map(i => <SkeletonBox key={i} $h="80px" />)}
          </div>
        ) : educations.length > 0 ? (
          <Timeline>
            {educations.map(edu => (
              <TimelineItem key={edu.id} $color="var(--secondary)">
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
        <CardTitle>Projects</CardTitle>
        {loadingFeatures ? (
          <ProjectsGrid>
            {[1, 2, 3].map(i => <SkeletonBox key={i} $h="140px" $r="14px" />)}
          </ProjectsGrid>
        ) : projects.length > 0 ? (
          <ProjectsGrid>
            {projects.map(proj => (
              <ProjectCard key={proj.id}>
                <ProjTitle>{proj.title}</ProjTitle>
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
        <CoverWrap $src={profile.cover_pic} />

        {/* Header Card */}
        <HeaderCard>
          <AvatarRow>
            <AvatarCircle>
              {profile.profile_pic
                ? <img src={profile.profile_pic} alt={profile.name} />
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
    </Page>
  )
}

export default Profile
