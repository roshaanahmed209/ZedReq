import React, { useState, useRef } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { motion, useInView } from 'framer-motion'

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
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px 20px;

  @media (max-width: 768px) {
    padding: 20px 15px;
  }

  @media (max-width: 480px) {
    padding: 15px 12px;
  }
`

const Header = styled.div`
  margin-bottom: 30px;
  animation: ${slideUp} 0.4s ease-out;

  @media (max-width: 768px) {
    margin-bottom: 20px;
  }
`

const PageTitle = styled.h1`
  font-size: 2em;
  color: var(--text);
  margin-bottom: 8px;
  font-weight: 300;

  @media (max-width: 768px) {
    font-size: 1.7em;
  }

  @media (max-width: 480px) {
    font-size: 1.5em;
  }
`

const PageSubtitle = styled.p`
  font-size: 1em;
  color: var(--text-light);

  @media (max-width: 480px) {
    font-size: 0.9em;
  }
`

const FilterContainer = styled.div`
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
  flex-wrap: wrap;
  animation: ${slideUp} 0.5s ease-out;

  @media (max-width: 768px) {
    margin-bottom: 20px;
    gap: 10px;
  }
`

const FilterButton = styled.button`
  padding: 10px 18px;
  background: ${props => props.active ? 'var(--primary)' : 'var(--bg-white)'};
  color: ${props => props.active ? 'white' : 'var(--text)'};
  border: 1px solid ${props => props.active ? 'var(--primary)' : 'var(--border)'};
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 400;
  transition: all 0.3s ease;

  &:hover {
    background: ${props => props.active ? 'var(--primary)' : 'rgba(10, 102, 194, 0.1)'};
    border-color: var(--primary);
    color: ${props => props.active ? 'white' : 'var(--primary)'};
    transform: translateY(-2px);
  }

  &:active {
    transform: translateY(0);
  }

  @media (max-width: 480px) {
    padding: 8px 14px;
    font-size: 0.85em;
  }
`

const PeopleGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;

  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
  }

  @media (max-width: 600px) {
    grid-template-columns: 1fr;
    gap: 16px;
  }
`

const PersonCard = styled.div`
  background: var(--bg-white);
  border-radius: 16px;
  border: 1px solid var(--border);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  animation: ${slideUp} 0.4s ease-out;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    border-color: var(--primary);
  }
`

const PersonHeader = styled.div`
  height: 80px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  position: relative;
`

const PersonContent = styled.div`
  padding: 60px 20px 20px;
  position: relative;
`

const PersonAvatar = styled.div`
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: var(--primary);
  border: 4px solid var(--bg-white);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2em;
  font-weight: 500;
  position: absolute;
  top: -50px;
  left: 50%;
  transform: translateX(-50%);
  transition: all 0.3s ease;

  ${PersonCard}:hover & {
    transform: translateX(-50%) scale(1.05);
  }
`

const PersonName = styled.h3`
  font-size: 1.2em;
  color: var(--text);
  margin-bottom: 4px;
  font-weight: 400;
  text-align: center;
`

const PersonTitle = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
  margin-bottom: 8px;
  text-align: center;
`

const PersonCompany = styled.p`
  font-size: 0.85em;
  color: var(--text-lighter);
  margin-bottom: 16px;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;

  svg {
    width: 14px;
    height: 14px;
  }
`

const PersonBio = styled.p`
  font-size: 0.85em;
  color: var(--text-light);
  line-height: 1.5;
  margin-bottom: 16px;
  text-align: center;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
`

const PersonSkills = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
  justify-content: center;
`

const SkillTag = styled.span`
  font-size: 0.75em;
  padding: 4px 10px;
  background: rgba(10, 102, 194, 0.1);
  color: var(--primary);
  border-radius: 12px;
  font-weight: 400;
  transition: all 0.2s ease;

  &:hover {
    background: var(--primary);
    color: white;
    transform: scale(1.05);
  }
`

const PersonStats = styled.div`
  display: flex;
  justify-content: space-around;
  padding: 12px 0;
  margin-bottom: 16px;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
`

const StatItem = styled.div`
  text-align: center;
`

const StatValue = styled.div`
  font-size: 1.1em;
  font-weight: 500;
  color: var(--primary);
`

const StatLabel = styled.div`
  font-size: 0.75em;
  color: var(--text-lighter);
  margin-top: 2px;
`

const ConnectButton = styled.button`
  width: 100%;
  padding: 12px 20px;
  background: ${props => props.connected ? 'transparent' : 'linear-gradient(135deg, var(--primary), var(--secondary))'};
  color: ${props => props.connected ? 'var(--primary)' : 'white'};
  border: ${props => props.connected ? '2px solid var(--primary)' : 'none'};
  border-radius: 8px;
  font-size: 0.95em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  svg {
    width: 18px;
    height: 18px;
    transition: transform 0.3s ease;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(10, 102, 194, 0.3);

    svg {
      transform: scale(1.2);
    }
  }

  &:active {
    transform: translateY(0);
  }
`

const AnimatedPersonCard = ({ person, index, onConnect, isConnected }) => {
  const ref = useRef(null)
  const inView = useInView(ref, { amount: 0.3, triggerOnce: true })
  
  return (
    <motion.div
      ref={ref}
      initial={{ scale: 0.9, opacity: 0 }}
      animate={inView ? { scale: 1, opacity: 1 } : { scale: 0.9, opacity: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
    >
      <PersonCard>
        <PersonHeader />
        <PersonContent>
          <PersonAvatar>{person.avatar}</PersonAvatar>
          <PersonName>{person.name}</PersonName>
          <PersonTitle>{person.title}</PersonTitle>
          <PersonCompany>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
            </svg>
            {person.company}
          </PersonCompany>
          <PersonBio>{person.bio}</PersonBio>
          <PersonSkills>
            {person.skills.map((skill, idx) => (
              <SkillTag key={idx}>{skill}</SkillTag>
            ))}
          </PersonSkills>
          <PersonStats>
            <StatItem>
              <StatValue>{person.connections}</StatValue>
              <StatLabel>Connections</StatLabel>
            </StatItem>
            <StatItem>
              <StatValue>{person.posts}</StatValue>
              <StatLabel>Posts</StatLabel>
            </StatItem>
            <StatItem>
              <StatValue>{person.followers}</StatValue>
              <StatLabel>Followers</StatLabel>
            </StatItem>
          </PersonStats>
          <ConnectButton 
            connected={isConnected}
            onClick={() => onConnect(person.id)}
          >
            {isConnected ? (
              <>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                Connected
              </>
            ) : (
              <>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="8.5" cy="7" r="4"></circle>
                  <line x1="20" y1="8" x2="20" y2="14"></line>
                  <line x1="23" y1="11" x2="17" y2="11"></line>
                </svg>
                Connect
              </>
            )}
          </ConnectButton>
        </PersonContent>
      </PersonCard>
    </motion.div>
  )
}

const Network = () => {
  const [activeFilter, setActiveFilter] = useState('all')
  const [connectedPeople, setConnectedPeople] = useState([])
  const navigate = useNavigate()
  const { logout } = useAuth()

  const people = [
    {
      id: 1,
      name: 'Sarah Mitchell',
      avatar: 'SM',
      title: 'Senior Product Manager',
      company: 'TechCorp',
      bio: 'Passionate about building products that solve real problems. 10+ years in tech product management.',
      skills: ['Product Strategy', 'Agile', 'UX Design'],
      connections: 1240,
      posts: 87,
      followers: 2150
    },
    {
      id: 2,
      name: 'David Chen',
      avatar: 'DC',
      title: 'Full Stack Developer',
      company: 'InnovateLabs',
      bio: 'Building scalable web applications with modern technologies. Open source contributor.',
      skills: ['React', 'Node.js', 'AWS'],
      connections: 856,
      posts: 142,
      followers: 1320
    },
    {
      id: 3,
      name: 'Emily Rodriguez',
      avatar: 'ER',
      title: 'UX/UI Designer',
      company: 'DesignStudio',
      bio: 'Creating beautiful and intuitive user experiences. Advocate for accessible design.',
      skills: ['Figma', 'User Research', 'Prototyping'],
      connections: 2100,
      posts: 205,
      followers: 3420
    },
    {
      id: 4,
      name: 'Michael Park',
      avatar: 'MP',
      title: 'DevOps Engineer',
      company: 'CloudSystems',
      bio: 'Automating infrastructure and improving deployment pipelines. Cloud architecture enthusiast.',
      skills: ['Docker', 'Kubernetes', 'CI/CD'],
      connections: 678,
      posts: 54,
      followers: 890
    },
    {
      id: 5,
      name: 'Jennifer Liu',
      avatar: 'JL',
      title: 'Data Scientist',
      company: 'Analytics Pro',
      bio: 'Turning data into actionable insights. Machine learning and AI researcher.',
      skills: ['Python', 'TensorFlow', 'SQL'],
      connections: 1450,
      posts: 98,
      followers: 2680
    },
    {
      id: 6,
      name: 'Alex Thompson',
      avatar: 'AT',
      title: 'Marketing Director',
      company: 'BrandCo',
      bio: 'Digital marketing strategist with a focus on growth and customer engagement.',
      skills: ['SEO', 'Content Strategy', 'Analytics'],
      connections: 3200,
      posts: 312,
      followers: 5100
    },
    {
      id: 7,
      name: 'Priya Sharma',
      avatar: 'PS',
      title: 'Backend Engineer',
      company: 'DataFlow',
      bio: 'Specializing in microservices and distributed systems. Performance optimization expert.',
      skills: ['Java', 'Spring Boot', 'Kafka'],
      connections: 920,
      posts: 76,
      followers: 1540
    },
    {
      id: 8,
      name: 'James Wilson',
      avatar: 'JW',
      title: 'Tech Lead',
      company: 'StartupHub',
      bio: 'Leading engineering teams to build innovative solutions. Mentor and public speaker.',
      skills: ['Leadership', 'System Design', 'Mentoring'],
      connections: 1680,
      posts: 134,
      followers: 2890
    },
    {
      id: 9,
      name: 'Rachel Green',
      avatar: 'RG',
      title: 'Frontend Developer',
      company: 'WebWorks',
      bio: 'Crafting responsive and performant web interfaces. Animation and interaction specialist.',
      skills: ['React', 'CSS', 'JavaScript'],
      connections: 745,
      posts: 89,
      followers: 1120
    },
    {
      id: 10,
      name: 'Omar Hassan',
      avatar: 'OH',
      title: 'Mobile Developer',
      company: 'AppLabs',
      bio: 'Building native and cross-platform mobile apps. iOS and Android development expert.',
      skills: ['React Native', 'Swift', 'Kotlin'],
      connections: 1030,
      posts: 67,
      followers: 1650
    },
    {
      id: 11,
      name: 'Sophie Anderson',
      avatar: 'SA',
      title: 'Product Designer',
      company: 'CreativeMinds',
      bio: 'Designing user-centered products that delight. Passionate about design systems.',
      skills: ['Sketch', 'Design Systems', 'Branding'],
      connections: 1890,
      posts: 156,
      followers: 2940
    },
    {
      id: 12,
      name: 'Daniel Kim',
      avatar: 'DK',
      title: 'Security Engineer',
      company: 'SecureNet',
      bio: 'Protecting applications and infrastructure from security threats. Cybersecurity advocate.',
      skills: ['Security', 'Penetration Testing', 'Compliance'],
      connections: 560,
      posts: 45,
      followers: 780
    },
    {
      id: 13,
      name: 'Maria Garcia',
      avatar: 'MG',
      title: 'Business Analyst',
      company: 'ConsultPro',
      bio: 'Bridging the gap between business and technology. Data-driven decision maker.',
      skills: ['Business Intelligence', 'SQL', 'Tableau'],
      connections: 1340,
      posts: 112,
      followers: 1890
    },
    {
      id: 14,
      name: 'Kevin Brown',
      avatar: 'KB',
      title: 'Software Architect',
      company: 'EnterpriseIT',
      bio: 'Designing scalable system architectures. Expert in distributed systems and cloud.',
      skills: ['Architecture', 'Microservices', 'Cloud'],
      connections: 2450,
      posts: 189,
      followers: 4120
    },
    {
      id: 15,
      name: 'Lisa Wang',
      avatar: 'LW',
      title: 'HR Manager',
      company: 'TalentFirst',
      bio: 'Building great teams and fostering inclusive workplace cultures. People-first approach.',
      skills: ['Recruitment', 'Talent Development', 'Culture'],
      connections: 2890,
      posts: 245,
      followers: 3650
    }
  ]

  const filteredPeople = people.filter(person => {
    if (activeFilter === 'all') return true
    if (activeFilter === 'connected') return connectedPeople.includes(person.id)
    if (activeFilter === 'suggested') return !connectedPeople.includes(person.id)
    return true
  })

  const handleConnect = (personId) => {
    if (connectedPeople.includes(personId)) {
      setConnectedPeople(connectedPeople.filter(id => id !== personId))
    } else {
      setConnectedPeople([...connectedPeople, personId])
    }
  }

  const handleBackToFeed = () => {
    navigate('/feed')
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
        <Header>
          <PageTitle>My Network</PageTitle>
          <PageSubtitle>Grow your professional network and discover new opportunities</PageSubtitle>
        </Header>

        <FilterContainer>
          <FilterButton 
            active={activeFilter === 'all'} 
            onClick={() => setActiveFilter('all')}
          >
            All People ({people.length})
          </FilterButton>
          <FilterButton 
            active={activeFilter === 'suggested'} 
            onClick={() => setActiveFilter('suggested')}
          >
            Suggested ({people.length - connectedPeople.length})
          </FilterButton>
          <FilterButton 
            active={activeFilter === 'connected'} 
            onClick={() => setActiveFilter('connected')}
          >
            My Connections ({connectedPeople.length})
          </FilterButton>
        </FilterContainer>

        <PeopleGrid>
          {filteredPeople.map((person, index) => (
            <AnimatedPersonCard
              key={person.id}
              person={person}
              index={index}
              onConnect={handleConnect}
              isConnected={connectedPeople.includes(person.id)}
            />
          ))}
        </PeopleGrid>
      </MainContainer>
    </Container>
  )
}

export default Network

