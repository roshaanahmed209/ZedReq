import React, { useState, useEffect, useRef, Suspense, lazy } from 'react'
import styled from 'styled-components'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import { generateProfileUrl } from '../utils/profileUrl'
import './Navbar.css'

/** Lazy-loaded to avoid circular import: Messages → Navbar → Messages (TDZ in production bundle). */
const Messages = lazy(() => import('../pages/Messages'))

/* ═══════════════════════════════════════════════════════════════
   Styled Components (Extracted from Feed.jsx)
   ═══════════════════════════════════════════════════════════════ */

const NavWrapper = styled.nav`
  background: color-mix(in srgb, var(--bg-light) 70%, transparent);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  position: fixed;
  top: ${props => props.$scrolled ? '20px' : '0'};
  z-index: 100;
  
  /* Transition properties for shrink effect */
  width: ${props => props.$scrolled ? (props.$searchActive ? 'min(96%, 1680px)' : 'min(90%, 1200px)') : '100%'};
  border-radius: ${props => props.$scrolled ? '50px' : '0'};
  padding: ${props => props.$scrolled ? (props.$searchActive ? '0 56px' : '0 40px') : '0 20px'};
  box-shadow: ${props => props.$scrolled ? 'var(--shadow-lg)' : 'var(--shadow)'};
  border: 1px solid color-mix(in srgb, var(--border) 30%, transparent);
  
  /* Centering */
  left: 50%;
  transform: translateX(-50%);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.3s ease, border-color 0.3s ease;
  
  /* Reclaim side room on narrower capsules so the shifted menu still clears
     both the search bar and Logout (the generous 56px is only for wide screens). */
  @media (max-width: 1280px) {
    padding: ${props => props.$scrolled ? (props.$searchActive ? '0 28px' : '0 24px') : '0 20px'};
  }
  @media (max-width: 768px) {
    padding: ${props => props.$scrolled ? '0 20px' : '0 15px'};
    width: ${props => props.$scrolled ? 'calc(100% - 30px)' : '100%'};
    top: ${props => props.$scrolled ? '15px' : '0'};
  }
  @media (max-width: 480px) { padding: 0 12px; }
`

const NavContainer = styled.div`
  width: 100%;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${props => props.$scrolled ? '8px 0' : '12px 0'};
  gap: ${props => props.$scrolled ? (props.$searchActive ? '40px' : '30px') : '30px'};
  position: relative;
  transition: all 0.3s ease;
  
  @media (max-width: 768px) { gap: 15px; padding: 10px 0; }
  @media (max-width: 480px) { gap: 10px; padding: 8px 0; }
`

const NavLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
  position: ${props => props.$scrolled ? 'relative' : 'relative'};
  z-index: 10; /* Ensure search input is above centered menu if overlap */
  flex-shrink: 0;
  
  @media (max-width: 1024px) { gap: 15px; }
  @media (max-width: 480px) { gap: 10px; }
`

const Logo = styled.h1`
  font-size: 1.8em;
  font-weight: 300;
  color: var(--primary);
  cursor: pointer;
  transition: transform 0.2s ease;
  white-space: nowrap;
  
  &:hover { transform: scale(1.05); }
  @media (max-width: 768px) { font-size: 1.5em; }
  @media (max-width: 480px) { font-size: 1.3em; }
  @media (max-width: 480px) { font-size: 1.3em; }
`

const NavCenter = styled.div`
  position: absolute;
  /* When the capsule is scrolled AND the search is expanded, slide the centered
     menu toward the open right-side space so it clears the search input. */
  left: ${props => (props.$scrolled && props.$searchActive) ? 'calc(50% + 130px)' : '50%'};
  transform: translateX(-50%);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  height: 100%;
  z-index: ${props => props.$searchActive ? '0' : '1'};
  pointer-events: none; /* Prevent blocking clicks if covering empty space, but buttons need events */
  overflow: visible;
  transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  & > * { pointer-events: auto; }

  @media (max-width: 1024px) { display: none; }
`

const NavRight = styled.div`
  display: flex;
  align-items: center;
  gap: 30px;
  position: relative;
  z-index: 10; 
  flex-shrink: 0;
  margin-left: auto;

  @media (max-width: 768px) { gap: 15px; }
  @media (max-width: 480px) { gap: 10px; }
`

const NavMenu = styled.div`
  display: flex;
  align-items: center;
  /* Tighten the menu in capsule mode so it occupies less width and stays clear
     of the expanded search bar on the left and the Logout button on the right. */
  gap: ${props => props.$scrolled ? '16px' : '30px'};
  transition: gap 0.3s ease;
  @media (max-width: 768px) { display: none; }
`

const NavMenuItem = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  color: var(--text-light);
  font-size: 0.85em;
  transition: all 0.2s ease;
  padding: 8px 12px;
  border-radius: 8px;
  min-width: 80px;
  text-align: center;
  position: relative;
  transform-origin: bottom center;
  
  svg { width: 22px; height: 22px; }
  span { white-space: nowrap; }
  
  &:hover {
    color: var(--primary);
    background: rgba(21, 133, 161, 0.1);
    transform: translateY(-4px) scale(1.1);
  }
  
  &.active { color: var(--primary); }
`

const NavPlaceholder = styled.div`
  height: 80px;
  width: 100%;
  @media (max-width: 768px) { height: 70px; }
`

const SearchInput = styled.input`
  padding: 10px 16px;
  border: 1px solid color-mix(in srgb, var(--border) 50%, transparent);
  border-radius: 6px;
  background: color-mix(in srgb, var(--bg-white) 20%, transparent);
  color: var(--text);
  font-size: 0.9em;
  transition: all 0.2s ease;
  position: relative;
  z-index: 21;
  
  &:focus {
    outline: none;
    border-color: var(--primary);
    background: color-mix(in srgb, var(--bg-white) 30%, transparent);
  }
  &::placeholder { color: var(--text-lighter); }
`

const SearchResults = styled.div`
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 280px;
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 12px;
  margin-top: 8px;
  z-index: 1000;
  box-shadow: var(--shadow-lg);
  max-height: 400px;
  overflow-y: auto;
`

const SearchResultItem = styled.div`
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  
  &:hover { background: var(--hover-bg); }
  &:first-child { border-radius: 8px 8px 0 0; }
  &:last-child { border-radius: 0 0 8px 8px; }
`

const SearchAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
`

const LogoutButton = styled.button`
  padding: 8px 16px;
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: var(--hover-bg);
    border-color: var(--primary);
  }
  
  @media (max-width: 1024px) {
    display: none;
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
    background: color-mix(in srgb, var(--primary) 10%, transparent);
    color: var(--primary);
  }
  
  svg { width: 24px; height: 24px; }
`

const MobileMenuOverlay = styled.div`
  display: none;
  position: fixed;
  inset: 0;
  background: color-mix(in srgb, var(--bg-light) 70%, black);
  backdrop-filter: blur(4px);
  z-index: 199;
  opacity: ${props => props.isOpen ? 1 : 0};
  pointer-events: ${props => props.isOpen ? 'auto' : 'none'};
  transition: opacity 0.3s ease, background-color 0.3s ease;
  
  @media (max-width: 1024px) { display: block; }
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
  box-shadow: var(--shadow-lg);
  transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.3s ease;
  
  @media (max-width: 1024px) { display: block; }
  @media (max-width: 480px) { width: 260px; max-width: 90vw; }
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
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 200;
  opacity: ${props => props.isOpen ? 1 : 0};
  pointer-events: ${props => props.isOpen ? 'auto' : 'none'};
  transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.4s ease, background-color 0.3s ease;

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
  
  svg { width: 24px; height: 24px; }
`

const SidePanel = styled.div`
  background: var(--bg-white);
  /* Reset styles for mobile panel consistency */
  border-radius: 0;
  border: none;
  box-shadow: none;
  margin: 0;
`

const PanelSection = styled.div`
  padding: 14px 20px;
  border-bottom: 1px solid color-mix(in srgb, var(--border) 30%, transparent);
  transition: all 0.2s ease;
  
  &:last-child { border-bottom: none; }
  &:hover {
    background: var(--hover-bg);
    cursor: pointer;
    padding-left: 24px;
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
    background: rgba(21, 133, 161, 0.1);
    border-radius: 8px;
    transition: all 0.2s ease;
    
    svg { color: var(--text-light); transition: all 0.2s ease; }
  }
  
  &:hover {
    color: var(--primary);
    transform: translateX(2px);
    
    .icon {
      background: var(--primary);
      transform: scale(1.05);
      svg { color: white; }
    }
  }
`

const PanelDivider = styled.div`
  height: 1px;
  background: var(--border);
  margin: 10px 20px;
`

const NavMoreWrapper = styled.div`
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
`

const NavMoreDropdown = styled.div`
  position: absolute;
  top: calc(100% + 10px);
  right: 50%;
  transform: translateX(50%);
  min-width: 210px;
  background: var(--bg-white);
  border: 1px solid var(--border);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  padding: 6px 0;
  z-index: 1100;
`

const NavMoreDropdownItem = styled.button`
  width: 100%;
  text-align: left;
  padding: 10px 16px;
  border: none;
  background: transparent;
  color: var(--text);
  font-size: 0.9em;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;

  &:hover {
    background: var(--hover-bg);
    color: var(--primary);
  }

  &.active {
    color: var(--primary);
    font-weight: 500;
    background: rgba(21, 133, 161, 0.08);
  }
`

const NAV_MORE_LINKS = [
  { label: 'LMS', path: '/lms' },
  { label: 'Evaluation', path: '/evaluation' },
  { label: 'AI Mode', path: '/ai-mode' },
  { label: 'AI Mock Interviews', path: '/ai-interviews' },
  { label: 'Profile', profile: true },
  { label: 'Settings', path: '/settings' },
]

function isNavMorePathActive(pathname, link) {
  if (link.profile) {
    return pathname.startsWith('/profile')
  }
  return pathname === link.path || pathname.startsWith(`${link.path}/`)
}


function Navbar() {
    const navigate = useNavigate()
    const location = useLocation()
    const { user, logout, sessionFeedStats } = useAuth()

    const [searchQuery, setSearchQuery] = useState('')
    const [searchResults, setSearchResults] = useState([])
    const [searchTimeout, setSearchTimeout] = useState(null)
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
    const [messagesOpen, setMessagesOpen] = useState(false)
    const [searchActive, setSearchActive] = useState(false)
    const [isScrolled, setIsScrolled] = useState(false)
    const [moreMenuOpen, setMoreMenuOpen] = useState(false)
    const searchWrapperRef = useRef(null)
    const inputRef = useRef(null)
    const moreMenuRef = useRef(null)

    const isMoreMenuActive = NAV_MORE_LINKS.some((link) =>
        isNavMorePathActive(location.pathname, link)
    )

    const handleMoreNav = (link) => {
        if (link.profile) {
            if (user?.id && user?.username) {
                navigate(generateProfileUrl(user.id, user.username))
            }
        } else {
            navigate(link.path)
        }
        setMoreMenuOpen(false)
    }

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 20)
        }
        window.addEventListener('scroll', handleScroll)
        return () => window.removeEventListener('scroll', handleScroll)
    }, [])

    useEffect(() => {
        function handleClickOutside(event) {
            if (searchWrapperRef.current && !searchWrapperRef.current.contains(event.target)) {
                // Only collapse if query is empty
                if (!searchQuery) {
                    setSearchActive(false)
                }
            }
            if (moreMenuRef.current && !moreMenuRef.current.contains(event.target)) {
                setMoreMenuOpen(false)
            }
        }
        document.addEventListener("mousedown", handleClickOutside)
        return () => {
            document.removeEventListener("mousedown", handleClickOutside)
        }
    }, [searchQuery])

    useEffect(() => {
        setMoreMenuOpen(false)
    }, [location.pathname])

    /* ── Search Logic ────────────────────────────────────────── */
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
            // Normalize user data
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

        if (searchTimeout) clearTimeout(searchTimeout)

        const timeout = setTimeout(() => {
            searchUsers(query)
        }, 300)

        setSearchTimeout(timeout)
    }

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    /* ── JSX Render ──────────────────────────────────────────── */
    return (
        <>
            <NavWrapper $scrolled={isScrolled} $searchActive={searchActive || searchQuery}>
                <NavContainer $scrolled={isScrolled} $searchActive={searchActive || searchQuery}>
                    <NavLeft $scrolled={isScrolled} $searchActive={searchActive || searchQuery}>
                        <MobileMenuButton onClick={() => setMobileMenuOpen(true)}>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <line x1="3" y1="12" x2="21" y2="12"></line>
                                <line x1="3" y1="6" x2="21" y2="6"></line>
                                <line x1="3" y1="18" x2="21" y2="18"></line>
                            </svg>
                        </MobileMenuButton>
                        <Logo onClick={() => navigate('/feed')}>ZedReq</Logo>

                        <button
                            className="search-button"
                            onClick={() => {
                                if (searchActive) {
                                    if (searchQuery.trim()) {
                                        searchUsers(searchQuery)
                                    } else {
                                        setSearchActive(false)
                                    }
                                } else {
                                    setSearchActive(true)
                                    setTimeout(() => inputRef.current?.focus(), 100)
                                }
                            }}
                        >
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <circle cx="11" cy="11" r="8"></circle>
                                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                            </svg>
                        </button>

                        <div
                            className={`search-wrapper ${searchActive || searchQuery ? 'active' : ''}`}
                            ref={searchWrapperRef}
                        >
                            <SearchInput
                                ref={inputRef}
                                type="text"
                                placeholder="Search..."
                                value={searchQuery}
                                onChange={handleSearchChange}
                                onFocus={() => setSearchActive(true)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') {
                                        searchUsers(searchQuery)
                                    } else if (e.key === 'Escape') {
                                        setSearchActive(false)
                                    }
                                }}
                                className="search-input-wide"
                            />
                            {searchResults.length > 0 && (
                                <SearchResults className="search-results-positioned">
                                    {searchResults.map(u => (
                                        <SearchResultItem key={u.id} onClick={() => {
                                            navigate(generateProfileUrl(u.id, u.username))
                                            setSearchResults([])
                                            setSearchQuery('')
                                            setSearchActive(false)
                                        }}>
                                            <SearchAvatar>
                                                {u.full_name ? u.full_name.charAt(0).toUpperCase() : 'U'}
                                            </SearchAvatar>
                                            <div>
                                                <div><strong>{u.full_name || u.username}</strong></div>
                                                <div className="search-username">@{u.username}</div>
                                            </div>
                                        </SearchResultItem>
                                    ))}
                                </SearchResults>
                            )}
                        </div>

                    </NavLeft>

                    <NavCenter $scrolled={isScrolled} $searchActive={searchActive || searchQuery}>
                        <NavMenu $scrolled={isScrolled}>
                            <NavMenuItem className={location.pathname === '/feed' ? 'active' : ''} onClick={() => navigate('/feed')}>
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                                    <polyline points="9 22 9 12 15 12 15 22"></polyline>
                                </svg>
                                <span>Home</span>
                            </NavMenuItem>

                            <NavMenuItem className={location.pathname === '/network' ? 'active' : ''} onClick={() => navigate('/network')}>
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                                    <circle cx="9" cy="7" r="4"></circle>
                                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                                    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                                </svg>
                                <span>Network</span>
                            </NavMenuItem>

                            <NavMenuItem className={location.pathname.startsWith('/jobs') ? 'active' : ''} onClick={() => navigate('/jobs')}>
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                                    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                                </svg>
                                <span>Jobs</span>
                            </NavMenuItem>

                            <NavMenuItem className={location.pathname === '/messages' ? 'active' : ''} onClick={() => setMessagesOpen(!messagesOpen)}>
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                                </svg>
                                <span>Messages</span>
                            </NavMenuItem>

                            <NavMenuItem className={location.pathname === '/notifications' ? 'active' : ''} onClick={() => navigate('/notifications')}>
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                                    <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                                </svg>
                                <span>Notifications</span>
                            </NavMenuItem>

                            <NavMoreWrapper ref={moreMenuRef}>
                                <NavMenuItem
                                    className={moreMenuOpen || isMoreMenuActive ? 'active' : ''}
                                    onClick={() => setMoreMenuOpen((open) => !open)}
                                    aria-label="More pages"
                                    aria-haspopup="menu"
                                    aria-expanded={moreMenuOpen}
                                >
                                    <svg viewBox="0 0 24 24" fill="currentColor" stroke="none">
                                        <circle cx="12" cy="5" r="1.75"></circle>
                                        <circle cx="12" cy="12" r="1.75"></circle>
                                        <circle cx="12" cy="19" r="1.75"></circle>
                                    </svg>
                                    <span>More</span>
                                </NavMenuItem>
                                {moreMenuOpen && (
                                    <NavMoreDropdown role="menu">
                                        {NAV_MORE_LINKS.map((link) => (
                                            <NavMoreDropdownItem
                                                key={link.label}
                                                type="button"
                                                role="menuitem"
                                                className={isNavMorePathActive(location.pathname, link) ? 'active' : ''}
                                                onClick={() => handleMoreNav(link)}
                                            >
                                                {link.label}
                                            </NavMoreDropdownItem>
                                        ))}
                                    </NavMoreDropdown>
                                )}
                            </NavMoreWrapper>
                        </NavMenu>
                    </NavCenter>

                    <NavRight $scrolled={isScrolled} $searchActive={searchActive || searchQuery}>
                        <LogoutButton onClick={handleLogout}>Logout</LogoutButton>
                    </NavRight>
                </NavContainer>
            </NavWrapper>
            <NavPlaceholder />

            {/* Mobile Menu Overlay */}
            < MobileMenuOverlay
                isOpen={mobileMenuOpen}
                onClick={() => setMobileMenuOpen(false)
                }
            />

            {/* Mobile Side Panel */}
            <MobileSidePanel isOpen={mobileMenuOpen}>
                <MobileMenuHeader>
                    <h2>Menu</h2>
                    <MobileMenuCloseButton onClick={() => setMobileMenuOpen(false)}>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </MobileMenuCloseButton>
                </MobileMenuHeader>

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

                    <PanelSection onClick={() => { navigate('/feed'); setMobileMenuOpen(false); }}>
                        <PanelLink>
                            <span className="icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                                    <polyline points="9 22 9 12 15 12 15 22"></polyline>
                                </svg>
                            </span>
                            <span>Home</span>
                        </PanelLink>
                    </PanelSection>

                    <PanelSection onClick={() => { navigate('/network'); setMobileMenuOpen(false); }}>
                        <PanelLink>
                            <span className="icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                                    <circle cx="9" cy="7" r="4"></circle>
                                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                                    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                                </svg>
                            </span>
                            <span>Network</span>
                        </PanelLink>
                    </PanelSection>

                    <PanelSection onClick={() => { setMessagesOpen(true); setMobileMenuOpen(false); }}>
                        <PanelLink>
                            <span className="icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                                </svg>
                            </span>
                            <span>Messages</span>
                        </PanelLink>
                    </PanelSection>

                    <PanelSection onClick={() => { navigate('/notifications'); setMobileMenuOpen(false); }}>
                        <PanelLink>
                            <span className="icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                                    <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                                </svg>
                            </span>
                            <span>Notifications</span>
                        </PanelLink>
                    </PanelSection>

                    <PanelDivider />

                    <PanelSection onClick={() => { navigate('/lms'); setMobileMenuOpen(false); }}>
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
                    
                    <PanelSection onClick={() => { navigate('/evaluation'); setMobileMenuOpen(false); }}>
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

                    <PanelSection onClick={() => { navigate('/ai-mode'); setMobileMenuOpen(false); }}>
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
                    
                    <PanelSection onClick={() => { navigate('/ai-interviews'); setMobileMenuOpen(false); }}>
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
                    
                    <PanelSection onClick={() => { navigate('/jobs'); setMobileMenuOpen(false); }}>
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
                    
                    <PanelSection onClick={() => { user?.id && user?.username && navigate(generateProfileUrl(user.id, user.username)); setMobileMenuOpen(false); }}>
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
                    
                    <PanelSection onClick={() => { navigate('/settings'); setMobileMenuOpen(false); }}>
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
                    
                    <PanelDivider />
                    
                    <PanelSection onClick={() => { handleLogout(); setMobileMenuOpen(false); }}>
                        <PanelLink>
                            <span className="icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                                    <polyline points="16 17 21 12 16 7"></polyline>
                                    <line x1="21" y1="12" x2="9" y2="12"></line>
                                </svg>
                            </span>
                            <span>Logout</span>
                        </PanelLink>
                    </PanelSection>
                </SidePanel>
            </MobileSidePanel>

            <MessagesPanel isOpen={messagesOpen}>
                <Suspense fallback={<div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)' }}>Loading messages…</div>}>
                    <Messages overlay={true} onClose={() => setMessagesOpen(false)} />
                </Suspense>
            </MessagesPanel>
        </>
    )
}

export default Navbar
