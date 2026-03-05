/**
 * Profile URL utilities
 * Handles hashing user IDs and generating/parsing profile URLs
 */

/**
 * Hash a user ID to a short, URL-safe string
 * Uses a simple encoding approach (base64-like but URL-safe)
 */
export const hashUserId = (userId) => {
  if (!userId || isNaN(userId)) {
    return null
  }
  
  // Simple encoding: convert to base36, then add a prefix for uniqueness
  const num = parseInt(userId)
  const encoded = num.toString(36) // Base36 encoding (0-9, a-z)
  
  // Add a simple hash prefix to make it less predictable
  // Using a simple algorithm: multiply by a prime and encode
  const hash = (num * 7919) % 46656 // 7919 is a prime, 46656 is 36^3
  const hashPart = hash.toString(36).padStart(3, '0')
  
  return `${hashPart}${encoded}`.substring(0, 8) // Limit to 8 chars
}

/**
 * Decode a hashed user ID back to the original user ID
 */
export const decodeUserId = (hashedId) => {
  if (!hashedId || typeof hashedId !== 'string') {
    return null
  }
  
  try {
    // Remove the hash prefix (first 3 chars) and decode the rest
    const encoded = hashedId.substring(3)
    const userId = parseInt(encoded, 36)
    
    // Verify the hash matches
    const expectedHash = hashUserId(userId)
    if (expectedHash === hashedId) {
      return userId
    }
    
    // If verification fails, try direct decoding (for backward compatibility)
    const directDecode = parseInt(hashedId, 36)
    if (!isNaN(directDecode) && directDecode > 0) {
      return directDecode
    }
    
    return null
  } catch (e) {
    return null
  }
}

/**
 * Generate a profile URL with format: /profile/{username}-{hashedId}
 */
export const generateProfileUrl = (userId, username) => {
  if (!userId || !username) {
    return `/profile/${userId}` // Fallback to old format
  }
  
  const hashedId = hashUserId(userId)
  if (!hashedId) {
    return `/profile/${userId}` // Fallback to old format
  }
  
  // Sanitize username for URL (remove special chars, keep alphanumeric, hyphens, underscores)
  const sanitizedUsername = username
    .toLowerCase()
    .replace(/[^a-z0-9_-]/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
  
  return `/profile/${sanitizedUsername}-${hashedId}`
}

/**
 * Parse a profile URL to extract user ID and username
 * Supports both formats: /profile/{username}-{hashedId} and /profile/{userId}
 */
export const parseProfileUrl = (urlPath) => {
  if (!urlPath) {
    return { userId: null, username: null }
  }
  
  // Remove leading/trailing slashes
  const path = urlPath.replace(/^\/|\/$/g, '')
  
  // Check if it's the new format: username-hashedId
  const match = path.match(/^profile\/([a-z0-9_-]+)-([a-z0-9]+)$/i)
  if (match) {
    const [, username, hashedId] = match
    const userId = decodeUserId(hashedId)
    
    if (userId) {
      return { userId, username, hashedId }
    }
  }
  
  // Fallback to old format: just user ID
  const oldFormatMatch = path.match(/^profile\/(\d+)$/)
  if (oldFormatMatch) {
    const userId = parseInt(oldFormatMatch[1])
    if (!isNaN(userId)) {
      return { userId, username: null, hashedId: null }
    }
  }
  
  return { userId: null, username: null, hashedId: null }
}

/**
 * Extract user ID from profile URL (supports both formats)
 */
export const getUserIdFromUrl = (urlPath) => {
  const parsed = parseProfileUrl(urlPath)
  return parsed.userId
}
