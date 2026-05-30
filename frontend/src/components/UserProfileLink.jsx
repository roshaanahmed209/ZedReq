import React from 'react'
import { Link } from 'react-router-dom'
import styled, { css } from 'styled-components'
import { generateProfileUrl } from '../utils/profileUrl'

const baseLinkStyles = css`
  text-decoration: none;
  cursor: pointer;

  &:hover {
    color: var(--primary);
    text-decoration: underline;
  }
`

const DefaultLink = styled(Link)`
  color: inherit;
  ${baseLinkStyles}
`

const NameLink = styled(Link)`
  display: block;
  color: var(--text);
  font-weight: inherit;
  font-size: inherit;
  line-height: inherit;
  margin: inherit;
  ${baseLinkStyles}
`

const UsernameLink = styled(Link)`
  color: var(--text-lighter);
  font-size: inherit;
  ${baseLinkStyles}

  &:hover {
    color: var(--primary);
  }
`

const InlineLink = styled(Link)`
  color: inherit;
  font-weight: inherit;
  font-size: inherit;
  ${baseLinkStyles}
`

const VARIANT_MAP = {
  default: DefaultLink,
  name: NameLink,
  username: UsernameLink,
  inline: InlineLink,
}

/**
 * Clickable link to a user's profile. Renders plain text when userId is missing.
 */
export function UserProfileLink({
  userId,
  username,
  children,
  variant = 'default',
  className,
  onClick,
  stopPropagation = false,
}) {
  const label = children ?? username ?? 'Member'

  if (!userId) {
    return <span className={className}>{label}</span>
  }

  const to = generateProfileUrl(userId, username || `user${userId}`)
  const LinkComponent = VARIANT_MAP[variant] || DefaultLink

  const handleClick = (e) => {
    if (stopPropagation) {
      e.stopPropagation()
    }
    onClick?.(e)
  }

  return (
    <LinkComponent to={to} className={className} onClick={handleClick}>
      {label}
    </LinkComponent>
  )
}

/** Company name when set; otherwise a link to the job poster's profile. */
export function JobCompanyOrPoster({ job, variant = 'inline', stopPropagation = true }) {
  if (!job) {
    return 'Unknown Company'
  }
  if (job.company_name) {
    return job.company_name
  }
  return (
    <UserProfileLink
      userId={job.poster_id}
      username={job.poster_username}
      variant={variant}
      stopPropagation={stopPropagation}
    >
      {job.poster_name || 'Unknown'}
    </UserProfileLink>
  )
}

export default UserProfileLink
