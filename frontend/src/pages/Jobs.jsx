import React, { useState } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

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
`

const MainContainer = styled.div`
  width: 100%;
  max-width: 100%;
  padding: 30px 20px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 25px;
  
  @media (max-width: 1200px) {
    gap: 20px;
  }
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  @media (max-width: 480px) {
    padding: 20px 15px;
  }
`

const JobColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: ${fadeInScale} 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  animation-delay: ${props => props.delay || '0s'};
  animation-fill-mode: both;
`

const ColumnHeader = styled.div`
  background: var(--bg-white);
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 24px;
  position: sticky;
  top: 80px;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`

const ColumnTitle = styled.h2`
  font-size: 1.4em;
  color: var(--text);
  font-weight: 400;
  margin-bottom: 8px;
  letter-spacing: -0.3px;
`

const ColumnSubtitle = styled.p`
  font-size: 0.9em;
  color: var(--text-light);
  font-weight: 300;
`

const JobsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
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

  &:hover {
    border-color: rgba(10, 102, 194, 0.4);
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  }
`

const JobHeader = styled.div`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
`

const JobInfo = styled.div`
  flex: 1;
`

const JobTitle = styled.h3`
  font-size: 1.15em;
  color: var(--text);
  font-weight: 400;
  margin-bottom: 8px;
  letter-spacing: -0.2px;
`

const JobCompany = styled.div`
  font-size: 0.95em;
  color: var(--text-light);
  margin-bottom: 4px;
`

const JobLocation = styled.div`
  font-size: 0.85em;
  color: var(--text-lighter);
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;

  svg {
    width: 14px;
    height: 14px;
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

const ApplyButton = styled.button`
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.95em;
  font-weight: 400;
  cursor: pointer;
  margin-top: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(10, 102, 194, 0.4);
  }

  &:active {
    transform: translateY(0);
  }
`

const Jobs = () => {
  const navigate = useNavigate()
  const { logout } = useAuth()

  const handleBackToFeed = () => {
    navigate('/feed')
  }

  const allJobs = [
    {
      id: 1,
      title: 'Senior Software Engineer',
      company: 'TechCorp Inc.',
      location: 'San Francisco, CA',
      type: 'Full-time',
      remote: false,
      salary: '$150k - $180k',
      description: 'We are looking for a Senior Software Engineer to join our team and help build scalable systems.',
      tags: ['JavaScript', 'React', 'Node.js']
    },
    {
      id: 2,
      title: 'Product Designer',
      company: 'Design Studio',
      location: 'New York, NY',
      type: 'Full-time',
      remote: false,
      salary: '$120k - $150k',
      description: 'Creative designer needed to work on user-centered design projects for major clients.',
      tags: ['Figma', 'UI/UX', 'Prototyping']
    },
    {
      id: 3,
      title: 'Data Scientist',
      company: 'Analytics Pro',
      location: 'Austin, TX',
      type: 'Full-time',
      remote: false,
      salary: '$130k - $160k',
      description: 'Join our data team to build predictive models and drive business insights.',
      tags: ['Python', 'ML', 'TensorFlow']
    },
    {
      id: 4,
      title: 'Marketing Manager',
      company: 'Growth Labs',
      location: 'Boston, MA',
      type: 'Full-time',
      remote: false,
      salary: '$100k - $130k',
      description: 'Lead our marketing efforts and develop strategies to grow our brand presence.',
      tags: ['Marketing', 'SEO', 'Analytics']
    },
    {
      id: 5,
      title: 'DevOps Engineer',
      company: 'Cloud Systems',
      location: 'Seattle, WA',
      type: 'Full-time',
      remote: false,
      salary: '$140k - $170k',
      description: 'Manage and optimize our cloud infrastructure and deployment pipelines.',
      tags: ['AWS', 'Docker', 'Kubernetes']
    }
  ]

  const recommendedJobs = [
    {
      id: 101,
      title: 'Full Stack Developer',
      company: 'StartupHub',
      location: 'Remote',
      type: 'Full-time',
      remote: true,
      salary: '$140k - $170k',
      matchScore: 95,
      description: 'Build end-to-end features for our growing SaaS platform with modern tech stack.',
      tags: ['React', 'Node.js', 'PostgreSQL']
    },
    {
      id: 102,
      title: 'Frontend Engineer',
      company: 'Digital Agency',
      location: 'Los Angeles, CA',
      type: 'Full-time',
      remote: false,
      salary: '$130k - $160k',
      matchScore: 92,
      description: 'Create beautiful, responsive web applications for our diverse client base.',
      tags: ['React', 'TypeScript', 'CSS']
    },
    {
      id: 103,
      title: 'Backend Developer',
      company: 'FinTech Solutions',
      location: 'Chicago, IL',
      type: 'Full-time',
      remote: false,
      salary: '$135k - $165k',
      matchScore: 88,
      description: 'Develop secure and scalable backend services for financial applications.',
      tags: ['Python', 'Django', 'PostgreSQL']
    },
    {
      id: 104,
      title: 'Mobile Developer',
      company: 'App Innovations',
      location: 'Remote',
      type: 'Full-time',
      remote: true,
      salary: '$125k - $155k',
      matchScore: 85,
      description: 'Build cross-platform mobile applications using React Native.',
      tags: ['React Native', 'iOS', 'Android']
    }
  ]

  const remoteRecommendedJobs = [
    {
      id: 201,
      title: 'Remote Full Stack Engineer',
      company: 'RemoteFirst Co.',
      location: 'Remote (Worldwide)',
      type: 'Full-time',
      remote: true,
      salary: '$150k - $180k',
      matchScore: 97,
      description: 'Join our fully remote team building next-generation collaboration tools.',
      tags: ['React', 'Node.js', 'MongoDB']
    },
    {
      id: 202,
      title: 'Senior React Developer',
      company: 'CloudWork Inc.',
      location: 'Remote (US)',
      type: 'Full-time',
      remote: true,
      salary: '$145k - $175k',
      matchScore: 94,
      description: 'Lead frontend development for our enterprise SaaS platform from anywhere.',
      tags: ['React', 'Redux', 'GraphQL']
    },
    {
      id: 203,
      title: 'Solutions Architect',
      company: 'Global Tech',
      location: 'Remote (EU)',
      type: 'Full-time',
      remote: true,
      salary: '$160k - $190k',
      matchScore: 90,
      description: 'Design and implement scalable cloud architectures for enterprise clients.',
      tags: ['AWS', 'Architecture', 'Microservices']
    },
    {
      id: 204,
      title: 'Python Engineer',
      company: 'Data Remote',
      location: 'Remote (APAC)',
      type: 'Full-time',
      remote: true,
      salary: '$135k - $165k',
      matchScore: 87,
      description: 'Build data processing pipelines and APIs for our analytics platform.',
      tags: ['Python', 'FastAPI', 'Redis']
    },
    {
      id: 205,
      title: 'Technical Lead',
      company: 'Innovation Labs',
      location: 'Remote (Americas)',
      type: 'Full-time',
      remote: true,
      salary: '$170k - $200k',
      matchScore: 93,
      description: 'Lead a distributed team of engineers building cutting-edge products.',
      tags: ['Leadership', 'JavaScript', 'Cloud']
    }
  ]

  const renderJobCard = (job, index) => (
    <JobCard key={job.id} delay={`${index * 0.1}s`}>
      <JobHeader>
        <JobInfo>
          <JobTitle>{job.title}</JobTitle>
          <JobCompany>{job.company}</JobCompany>
          <JobLocation>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
              <circle cx="12" cy="10" r="3"></circle>
            </svg>
            {job.location}
          </JobLocation>
        </JobInfo>
        {job.matchScore && <MatchScore>{job.matchScore}% Match</MatchScore>}
      </JobHeader>
      
      <JobDescription>{job.description}</JobDescription>
      
      <JobMeta>
        <JobTag primary>{job.type}</JobTag>
        <JobTag>{job.salary}</JobTag>
        {job.remote && <JobTag primary>Remote</JobTag>}
        {job.tags.map((tag, idx) => (
          <JobTag key={idx}>{tag}</JobTag>
        ))}
      </JobMeta>
      
      <ApplyButton>Apply Now</ApplyButton>
    </JobCard>
  )

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
        <JobColumn delay="0s">
          <ColumnHeader>
            <ColumnTitle>All Jobs</ColumnTitle>
            <ColumnSubtitle>{allJobs.length} opportunities available</ColumnSubtitle>
          </ColumnHeader>
          <JobsContainer>
            {allJobs.map((job, index) => renderJobCard(job, index))}
          </JobsContainer>
        </JobColumn>

        <JobColumn delay="0.1s">
          <ColumnHeader>
            <ColumnTitle>Recommended</ColumnTitle>
            <ColumnSubtitle>{recommendedJobs.length} jobs matched to your profile</ColumnSubtitle>
          </ColumnHeader>
          <JobsContainer>
            {recommendedJobs.map((job, index) => renderJobCard(job, index))}
          </JobsContainer>
        </JobColumn>

        <JobColumn delay="0.2s">
          <ColumnHeader>
            <ColumnTitle>Remote Recommended</ColumnTitle>
            <ColumnSubtitle>{remoteRecommendedJobs.length} remote opportunities for you</ColumnSubtitle>
          </ColumnHeader>
          <JobsContainer>
            {remoteRecommendedJobs.map((job, index) => renderJobCard(job, index))}
          </JobsContainer>
        </JobColumn>
      </MainContainer>
    </Container>
  )
}

export default Jobs

