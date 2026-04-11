import axios from 'axios'

// Token storage keys
const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

// Create axios instance with default configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 250000, // 250 second default timeout (increased for LLM and complex queries)
})

/** Public (no auth) — post-login pre-launch modal copy from backoffice. */
export const fetchPublicPrelaunchNotice = () =>
  api.get('/api/public/prelaunch-notice')

// Token management functions
export const tokenService = {
  getAccessToken: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  
  setTokens: (accessToken, refreshToken) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  },
  
  clearTokens: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  },
  
  isAuthenticated: () => !!localStorage.getItem(ACCESS_TOKEN_KEY),
}

// Request interceptor - add JWT token to requests
api.interceptors.request.use(
  (config) => {
    const token = tokenService.getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // Let the runtime set multipart boundary; a bare "multipart/form-data" header breaks uploads
    if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
      if (config.headers && typeof config.headers.delete === 'function') {
        config.headers.delete('Content-Type')
      } else {
        delete config.headers['Content-Type']
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle token refresh
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
      // Handle specific error codes
      if (error.response) {
        const { status } = error.response
        
        // Log error for debugging
        console.error('API Error:', {
          status,
          url: error.config?.url,
          message: error.response?.data?.detail || error.response?.data?.message || error.response?.data?.error
        })
        
        // Handle quota exceeded (403) - extract user-friendly message
        if (status === 403) {
          const detail = error.response.data?.detail
          if (detail && typeof detail === 'object' && detail.feature) {
            // Quota exceeded error - extract the message
            const userMessage = detail.message || `Your ${detail.feature.replace('_', ' ')} limit has been reached (${detail.used}/${detail.limit} on ${detail.plan} plan). Upgrade your plan to increase your limit.`
            error.userMessage = userMessage
            // Override the default axios error message
            error.message = userMessage
          } else if (detail) {
            // Other 403 errors - extract message
            const userMessage = typeof detail === 'string' ? detail : (detail?.message || 'Access denied')
            error.userMessage = userMessage
            // Override the default axios error message
            error.message = userMessage
          } else {
            // No detail provided, use a generic message
            error.userMessage = 'Access denied'
            error.message = 'Access denied'
          }
        }
        
        // Handle rate limiting (429)
        if (status === 429) {
          const retryAfter = error.response.headers?.['retry-after'] || error.response.headers?.['Retry-After'] || 60
          const rateLimitInfo = error.response.data?.detail || error.response.data?.message
          
          // Enhance error object with rate limit info
          error.rateLimitInfo = {
            retryAfter: parseInt(retryAfter),
            remaining: error.response.data?.remaining || 0,
            limit: error.response.headers?.['x-ratelimit-limit'] || error.response.headers?.['X-RateLimit-Limit'] || null,
            message: rateLimitInfo
          }
        }
      
      // Handle 401 Unauthorized - try to refresh token
      if (status === 401 && !originalRequest._retry) {
        originalRequest._retry = true
        
        const refreshToken = tokenService.getRefreshToken()
        if (refreshToken) {
          try {
            const response = await axios.post(
              `${api.defaults.baseURL}/api/auth/refresh`,
              { refresh_token: refreshToken }
            )
            
            const { access_token, refresh_token } = response.data
            tokenService.setTokens(access_token, refresh_token)
            
            // Retry original request with new token
            originalRequest.headers.Authorization = `Bearer ${access_token}`
            return api(originalRequest)
          } catch (refreshError) {
            // Refresh failed, clear tokens and redirect to login
            tokenService.clearTokens()
            window.dispatchEvent(new CustomEvent('auth:unauthorized'))
          }
        } else {
          // No refresh token, trigger logout
          window.dispatchEvent(new CustomEvent('auth:unauthorized'))
        }
      }
    }
    
    return Promise.reject(error)
  }
)

// Auth API methods (JWT-based)
export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/api/auth/login', { username, password })
    // Check if 2FA is required
    if (response.data.requires_2fa) {
      // Return temp token for 2FA verification
      return response
    }
    // Normal login - set tokens
    if (response.data.access_token) {
      tokenService.setTokens(response.data.access_token, response.data.refresh_token)
    }
    return response
  },
  
  verify2FA: async (tempToken, code) => {
    const response = await api.post('/api/auth/2fa/verify', { 
      temp_token: tempToken, 
      code: code 
    })
    if (response.data.access_token) {
      tokenService.setTokens(response.data.access_token, response.data.refresh_token)
    }
    return response
  },
  
  register: async (userData) => {
    const response = await api.post('/api/auth/register', userData)
    if (response.data.access_token) {
      tokenService.setTokens(response.data.access_token, response.data.refresh_token)
    }
    return response
  },
  
  logout: async () => {
    try {
      // Call backend logout endpoint to trigger context refresh
      await api.post('/api/auth/logout')
    } catch (error) {
      // Don't fail logout if backend call fails
      console.warn('Backend logout call failed:', error)
    } finally {
      // Always clear tokens locally
      tokenService.clearTokens()
    }
  },
  
  getCurrentUser: () => api.get('/api/auth/me'),
  
  refreshToken: async () => {
    const refreshToken = tokenService.getRefreshToken()
    if (!refreshToken) throw new Error('No refresh token')
    
    const response = await api.post('/api/auth/refresh', { refresh_token: refreshToken })
    if (response.data.access_token) {
      tokenService.setTokens(response.data.access_token, response.data.refresh_token)
    }
    return response
  },
  
  isAuthenticated: () => tokenService.isAuthenticated(),
}

// User API methods
export const userAPI = {
  getCurrentUser: () => api.get('/api/user'),
  getUserProfile: (userId) => api.get(`/api/user/${userId}`),
  updateProfile: (data) => api.put('/api/user', data),
  searchUsers: (query) => api.get('/api/user/search', { params: { q: query } }),
  getConnectionCounts: (userId) => api.get(`/api/user/${userId}/connections/count`),
  getUserCertificates: (userId) => api.get(`/api/user/${userId}/certificates`),
  // Subscription & quota usage
  getSubscription: () => api.get('/api/user/subscription'),
  getSubscriptionUsage: () => api.get('/api/user/subscription/usage'),
  cancelSubscription: (body) => api.post('/api/user/subscription/cancel', body),
  changeSubscriptionPlan: (body) => api.post('/api/user/subscription/change-plan', body),
}

// Profile Features API methods
export const profileFeaturesAPI = {
  // Experience
  getExperiences: (userId, limit = 50, offset = 0) => 
    api.get(`/api/profile/experience/${userId}`, { params: { limit, offset } }),
  createExperience: (data) => api.post('/api/profile/experience', data),
  updateExperience: (experienceId, data) => api.put(`/api/profile/experience/${experienceId}`, data),
  deleteExperience: (experienceId) => api.delete(`/api/profile/experience/${experienceId}`),
  
  // Education
  getEducations: (userId, limit = 50, offset = 0) => 
    api.get(`/api/profile/education/${userId}`, { params: { limit, offset } }),
  createEducation: (data) => api.post('/api/profile/education', data),
  updateEducation: (educationId, data) => api.put(`/api/profile/education/${educationId}`, data),
  deleteEducation: (educationId) => api.delete(`/api/profile/education/${educationId}`),
  
  // Projects
  getProjects: (userId, limit = 50, offset = 0) => 
    api.get(`/api/profile/projects/${userId}`, { params: { limit, offset } }),
  createProject: (data) => api.post('/api/profile/projects', data),
  updateProject: (projectId, data) => api.put(`/api/profile/projects/${projectId}`, data),
  deleteProject: (projectId) => api.delete(`/api/profile/projects/${projectId}`),
  
  // Recommendations
  getRecommendations: (userId, limit = 50, offset = 0) => 
    api.get(`/api/profile/recommendations/${userId}`, { params: { limit, offset } }),
  createRecommendation: (data) => api.post('/api/profile/recommendations', data),
  updateRecommendation: (recommendationId, data) => api.put(`/api/profile/recommendations/${recommendationId}`, data),
  deleteRecommendation: (recommendationId) => api.delete(`/api/profile/recommendations/${recommendationId}`),
  
  // Interests
  getInterests: (userId, interestType = null, limit = 50, offset = 0) => {
    const params = { limit, offset }
    if (interestType) params.interest_type = interestType
    return api.get(`/api/profile/interests/${userId}`, { params })
  },
  createInterest: (data) => api.post('/api/profile/interests', data),
  updateInterest: (interestId, data) => api.put(`/api/profile/interests/${interestId}`, data),
  deleteInterest: (interestId) => api.delete(`/api/profile/interests/${interestId}`),
  
  // Analytics
  getAnalytics: (userId, days = 30) => api.get(`/api/profile/analytics/${userId}`, { params: { days } }),
  getProfileViews: (userId, days = 30) => api.get(`/api/profile/analytics/${userId}/views`, { params: { days } }),
  trackProfileView: (userId, source = 'direct') => api.post('/api/profile/analytics/track-view', { user_id: userId, source }),
}

// Post API methods
export const postAPI = {
  createPost: (data) => api.post('/api/posts', data),
  getPost: (postId) => api.get(`/api/posts/${postId}`),
  getUserPosts: (userId, params = {}) => api.get(`/api/posts/user/${userId}`, { params }),
  getUserFeaturedPosts: (userId, params = {}) => {
    // Support both object and number for backward compatibility
    if (typeof params === 'number') {
      return api.get(`/api/posts/user/${userId}/featured`, { params: { limit: params, offset: 0 } })
    }
    return api.get(`/api/posts/user/${userId}/featured`, { params })
  },
  updatePost: (postId, data) => api.put(`/api/posts/${postId}`, data),
  deletePost: (postId) => api.delete(`/api/posts/${postId}`),
  toggleLike: (postId) => api.post(`/api/posts/${postId}/like`),
  getLikes: (postId) => api.get(`/api/posts/${postId}/likes`),
}

// Feed API methods
export const feedAPI = {
  getFeed: (limit = 20, cursor = null) => {
    const params = { limit }
    if (cursor) params.cursor = cursor
    return api.get('/api/feed', { params })
  },
}

// Network API methods
export const networkAPI = {
  // Discover new users (20% of user base)
  discoverUsers: (limit = 20) => 
    api.get('/api/network/discover', { params: { limit } }),
  
  // Get friend-of-friend suggestions
  getSuggestions: (limit = 20) => 
    api.get('/api/network/suggestions', { params: { limit } }),
  
  // Get current user's connections
  getConnections: () => 
    api.get('/api/network/connections'),
}

// Connection Request API methods
export const connectionAPI = {
  // Send connection request to a user
  sendRequest: (userUuid, message = null) => {
    // Always send an object, even if message is null/undefined
    const payload = message ? { message } : {};
    return api.post(`/api/connections/request/${userUuid}`, payload);
  },
  
  // Accept a connection request
  acceptRequest: (requestId) => 
    api.put(`/api/connections/accept/${requestId}`),
  
  // Reject a connection request
  rejectRequest: (requestId) => 
    api.put(`/api/connections/reject/${requestId}`),
  
  // Remove an existing connection
  removeConnection: (connectionId) => 
    api.delete(`/api/connections/${connectionId}`),
  
  // Get pending requests received
  getPendingRequests: () => 
    api.get('/api/connections/pending'),
  
  // Get sent requests
  getSentRequests: () => 
    api.get('/api/connections/sent'),
}

// Job API methods
export const jobAPI = {
  // Get all jobs (with optional filters)
  getJobs: (params = {}) =>
    api.get('/api/jobs', { params }),
  
  // Get remote jobs
  getRemoteJobs: (limit = 50, offset = 0) =>
    api.get('/api/jobs/remote', { params: { limit, offset } }),
  
  // Get jobs posted by current user
  getMyPostedJobs: (limit = 50, offset = 0) =>
    api.get('/api/jobs/my-posts', { params: { limit, offset } }),
  
  // Get saved/bookmarked jobs
  getSavedJobs: (limit = 50, offset = 0) =>
    api.get('/api/jobs/saved', { params: { limit, offset } }),
  
  // Get user's job applications
  getMyApplications: (limit = 50, offset = 0) =>
    api.get('/api/jobs/applications', { params: { limit, offset } }),
  
  // Get a specific job by ID
  getJob: (jobId) =>
    api.get(`/api/jobs/${jobId}`),
  
  // Create a new job posting
  createJob: (jobData) =>
    api.post('/api/jobs', jobData),
  
  // Update a job posting
  updateJob: (jobId, jobData) =>
    api.put(`/api/jobs/${jobId}`, jobData),
  
  // Close a job posting
  closeJob: (jobId) =>
    api.post(`/api/jobs/${jobId}/close`),
  
  // Delete a job posting
  deleteJob: (jobId) =>
    api.delete(`/api/jobs/${jobId}`),
  
  // Apply to a job
  applyToJob: (jobId, applicationData = {}) =>
    api.post(`/api/jobs/${jobId}/apply`, { job_id: jobId, ...applicationData }),
  
  // Get applicants for a job (poster only)
  getJobApplicants: (jobId, limit = 100, offset = 0) =>
    api.get(`/api/jobs/${jobId}/applicants`, { params: { limit, offset } }),
  
  // Update application status (poster only)
  updateApplicationStatus: (applicationId, status) =>
    api.put(`/api/jobs/applications/${applicationId}/status`, { status }),
  
  // Withdraw application
  withdrawApplication: (applicationId) =>
    api.delete(`/api/jobs/applications/${applicationId}`),
  
  // Toggle save/bookmark job
  toggleSaveJob: (jobId) =>
    api.post(`/api/jobs/${jobId}/save`),
  
  // Search jobs
  searchJobs: (query, filters = {}) =>
    api.get('/api/jobs', { params: { query, ...filters } }),
  
  // Get personalized job recommendations
  getJobRecommendations: (userId, limit = 10) =>
    api.get(`/api/jobs/recommendations/${userId}`, { params: { limit } }),
  
  // Get interview recommendations (jobs with attempt counts)
  getInterviewRecommendations: (userId, limit = 10) =>
    api.get(`/api/interviews/recommendations/${userId}`, { params: { limit } }),
}

// Notification API methods
export const notificationAPI = {
  // Get all notifications
  getNotifications: (limit = 50, offset = 0, unreadOnly = false) => 
    api.get('/api/notifications', { params: { limit, offset, unread_only: unreadOnly } }),
  
  // Get unread count
  getUnreadCount: () => 
    api.get('/api/notifications/unread/count'),
  
  // Mark notification as read
  markAsRead: (notificationId) => 
    api.put(`/api/notifications/${notificationId}/read`),
  
  // Mark all as read
  markAllAsRead: () => 
    api.put('/api/notifications/read-all'),
}

// Messaging API methods
export const messagingAPI = {
  // Get all conversations for current user
  getConversations: () => 
    api.get('/api/messaging/conversations'),
  
  // Get messages with a specific user
  getMessages: (recipientId, limit = 50) => 
    api.get(`/api/messaging/messages/${recipientId}`, { params: { limit } }),
  
  // Send a message
  sendMessage: (recipientId, content, messageType = 'text') => 
    api.post('/api/messaging/messages', {
      recipient_id: recipientId,
      content,
      message_type: messageType
    }),
  
  // Mark conversation as read
  markConversationRead: (recipientId) => 
    api.post(`/api/messaging/messages/${recipientId}/read`),
}

// LMS API methods
export const lmsAPI = {
  // Course endpoints
  getCourses: (params = {}) =>
    api.get('/api/lms/courses', { params }),
  
  getCourse: (courseId) =>
    api.get(`/api/lms/courses/${courseId}`),
  
  createCourse: (courseData) =>
    api.post('/api/lms/courses', courseData),
  
  updateCourse: (courseId, courseData) =>
    api.put(`/api/lms/courses/${courseId}`, courseData),
  
  getCourseSections: (courseId) =>
    api.get(`/api/lms/courses/${courseId}/sections`),
  
  getCourseResources: (courseId) =>
    api.get(`/api/lms/courses/${courseId}/resources`),
  
  // User course endpoints
  enrollInCourse: (courseId) =>
    api.post(`/api/lms/courses/${courseId}/enroll`),
  
  getMyCourses: (params = {}) =>
    api.get('/api/lms/my-courses', { params, timeout: 250000 }), // 250 seconds
  
  getMyCourse: (courseId) =>
    api.get(`/api/lms/my-courses/${courseId}`, { timeout: 250000 }),
  
  updateCourseProgress: (courseId, progress) =>
    api.put(`/api/lms/my-courses/${courseId}/progress`, { progress }),
  
  // Dashboard endpoints
  getDashboardAll: () =>
    api.get('/api/lms/dashboard/all', { timeout: 250000 }), // 250 seconds

  getDashboard: () =>
    api.get('/api/lms/dashboard', { timeout: 250000 }),
  
  getWeeklyPerformance: (days = 7) =>
    api.get('/api/lms/dashboard/weekly', { params: { days }, timeout: 250000 }),
  
  getDomainPerformance: () =>
    api.get('/api/lms/dashboard/domains', { timeout: 250000 }),
  
  // Question/Answer endpoints
  getCourseQuestions: (courseId, sectionId = null) => {
    const params = sectionId ? { section_id: sectionId } : {}
    return api.get(`/api/lms/courses/${courseId}/questions`, { params })
  },
  
  getQuestion: (questionId) =>
    api.get(`/api/lms/questions/${questionId}`),
  
  createQuestion: (questionData) =>
    api.post('/api/lms/questions', questionData),
  
  submitAnswer: (questionId, answerText) =>
    api.post(`/api/lms/questions/${questionId}/answer`, {
      question_id: questionId,
      answer_text: answerText
    }),
  
  evaluateAnswer: (answerId, evaluation) =>
    api.put(`/api/lms/answers/${answerId}/evaluate`, evaluation),
  
  getMyAnswers: (params = {}) =>
    api.get('/api/lms/my-answers', { params }),
  
  // Activity endpoints
  getActivities: (limit = 10) =>
    api.get('/api/lms/activities', { params: { limit }, timeout: 250000 }), // 250 seconds
  
  // Recommendation endpoints
  getRecommendations: (limit = 5) =>
    api.get('/api/lms/recommendations', { params: { limit }, timeout: 250000 }), // 250 seconds
  
  dismissRecommendation: (recommendationId) =>
    api.post(`/api/lms/recommendations/${recommendationId}/dismiss`),
  
  // Deadline endpoints
  getDeadlines: (limit = 10) =>
    api.get('/api/lms/deadlines', { params: { limit }, timeout: 250000 }), // 250 seconds
  
  createDeadline: (deadlineData) =>
    api.post('/api/lms/deadlines', deadlineData),
  
  completeDeadline: (deadlineId) =>
    api.put(`/api/lms/deadlines/${deadlineId}/complete`),
  
  // Certificate endpoints
  getCertificates: () =>
    api.get('/api/lms/certificates', { timeout: 250000 }), // 250 seconds
  
  getCertificateByNumber: (certificateNumber) =>
    api.get(`/api/lms/certificates/${certificateNumber}`),
  
  // Section progress endpoints
  getSectionProgress: (sectionId) =>
    api.get(`/api/lms/sections/${sectionId}/progress`),
  
  updateSectionProgress: (sectionId, progressData) =>
    api.put(`/api/lms/sections/${sectionId}/progress`, progressData),
  
  // Azel Agent: queues a background job (202) — poll getAzelJobStatus until completed
  triggerAzelProcessCourse: (courseId, sectionId = null) =>
    api.post(
      `/api/lms/azel/process-course/${courseId}`,
      sectionId ? { section_id: sectionId } : {},
      { timeout: 120000 }
    ),
  // Generous timeout: server can be slow under load while Azel holds the GIL / DB pool
  getAzelJobStatus: (jobId) =>
    api.get(`/api/lms/azel/process-course/jobs/${jobId}`, { timeout: 120000 }),
  
  // Course performance endpoint
  getCoursePerformance: (courseId) =>
    api.get(`/api/lms/dashboard/courses/${courseId}`, { timeout: 250000 }), // 250 seconds

  // Section-level performance (per-level accuracy breakdown)
  getSectionPerformance: (courseId) =>
    api.get(`/api/lms/courses/${courseId}/section-performance`),

  getCourseAnalysis: (courseId) =>
    api.get(`/api/lms/courses/${courseId}/analysis`),
  
  // Seez Agent endpoints (longer timeout for LLM evaluation calls)
  triggerSeezEvaluateCourse: (courseId) =>
    api.post(`/api/lms/seez/evaluate-course/${courseId}`, {}, { timeout: 250000 }), // 250 seconds
  
  triggerSeezEvaluateAnswers: (answerIds) =>
    api.post('/api/lms/seez/evaluate-answers', answerIds, { timeout: 250000 }), // 250 seconds

    // Course Recommendation endpoints
    generateRecommendations: (limit = 5) =>
      api.post(`/api/lms/generate-recommendations?limit=${limit}`, {}, { timeout: 250000 }), // 250 seconds
  }

// Nemz API methods
export const nemzAPI = {
  chat: ({ message, sessionId }) =>
    api.post('/api/nemz/chat', { message, session_id: sessionId }),
  
  deleteSession: (sessionId) =>
    api.delete(`/api/nemz/chat/session/${sessionId}`),
  
  searchAll: ({ query, searchType, limit = 10 }) =>
    api.post('/api/nemz/search', { query, search_type: searchType, limit }),
  
  searchJobs: ({ query, limit = 10 }) =>
    api.post('/api/nemz/search/jobs', { query, limit }),
  
  searchProfiles: ({ query, limit = 10 }) =>
    api.post('/api/nemz/search/profiles', { query, limit }),
  
  searchPosts: ({ query, limit = 10 }) =>
    api.post('/api/nemz/search/posts', { query, limit }),
}

// Vec API methods (Vector Database Sync)
export const vecAPI = {
  sync: (force = false) =>
    api.post('/api/vec/sync', { force }, { timeout: 250000 }), // 250 seconds
  
  syncBackground: (force = false) =>
    api.post('/api/vec/sync/background', { force }, { timeout: 250000 }),
  
  getStatus: () =>
    api.get('/api/vec/status', { timeout: 250000 }),
}

// Interview API methods
export const interviewAPI = {
  startInterview: (jobId) =>
    api.post('/api/interviews/start', { job_id: jobId }),
  
  getInterview: (interviewId) =>
    api.get(`/api/interviews/${interviewId}`),
  
  completeInterview: (interviewId) =>
    api.post(`/api/interviews/${interviewId}/complete`),
  
  getMyInterviews: ({ jobId } = {}) => {
    const params = jobId ? { job_id: jobId } : {}
    return api.get('/api/interviews/my-interviews', { params })
  },
  
  getInterviewRizFeedback: (interviewId) =>
    api.get(`/api/interviews/${interviewId}/riz-feedback`),
  
  refreshRizFeedback: (interviewId) =>
    api.post(`/api/interviews/${interviewId}/riz-feedback/refresh`),
}

// Context API methods - Generic context update endpoint
export const contextAPI = {
  /**
   * Update user context based on actions
   * @param {string} action - Action type: "apply" | "like" | "view"
   * @param {string} entityType - Entity type: "job" | "post" | "profile"
   * @param {number} entityId - Entity ID
   * @returns {Promise} API response
   */
  updateContext: async (action, entityType, entityId) => {
    try {
      const response = await api.post('/api/context/update', {
        action,
        entity_type: entityType,
        entity_id: entityId
      })
      return response
    } catch (error) {
      // Silently fail - context updates are non-critical
      console.warn('Context update failed:', error)
      return { data: { success: false } }
    }
  }
}

// WebSocket connection for real-time notifications
export class NotificationWebSocket {
  constructor(onNotification, onError = null) {
    this.ws = null
    this.onNotification = onNotification
    this.onError = onError
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
  }
  
  connect() {
    const token = tokenService.getAccessToken()
    if (!token) {
      return
    }

    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000'
    const wsUrl = apiUrl
      .replace('http://', 'ws://')
      .replace('https://', 'wss://')
    const fullWsUrl = `${wsUrl}/ws/notifications`

    try {
      this.ws = new WebSocket(fullWsUrl)

      this.ws.onopen = () => {
        this.reconnectAttempts = 0
        this.ws.send(JSON.stringify({ type: 'auth', token }))
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          // Ignore pong messages (keepalive responses)
          if (data.type === 'pong') {
            return
          }
          if (data.type === 'notification' && this.onNotification) {
            this.onNotification(data)
          }
        } catch {
          // non-JSON messages ignored (e.g. legacy pong)
        }
      }
      
      this.ws.onerror = (error) => {
        if (this.onError) this.onError(error)
      }
    } catch (error) {
      if (this.onError) this.onError(error)
    }
    
    this.ws.onclose = (event) => {
      // Don't reconnect if it was an authentication error (4001)
      if (event.code === 4001) {
        return
      }
      
      // Attempt to reconnect if not intentionally closed
      if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++
        setTimeout(() => this.connect(), this.reconnectDelay * this.reconnectAttempts)
      }
    }
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close(1000) // Normal closure
      this.ws = null
    }
  }
  
  // Send ping to keep connection alive
  ping() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send('ping')
    }
  }
}

// WebSocket connection for real-time messaging
export class MessagingWebSocket {
  constructor(onMessage, onError = null) {
    this.ws = null
    this.onMessage = onMessage
    this.onError = onError
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
    this.pingInterval = null
  }
  
  connect() {
    const token = tokenService.getAccessToken()
    if (!token) {
      return
    }

    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000'
    const wsUrl = apiUrl
      .replace('http://', 'ws://')
      .replace('https://', 'wss://')
    const fullWsUrl = `${wsUrl}/api/messaging/messages`

    try {
      this.ws = new WebSocket(fullWsUrl)

      this.ws.onopen = () => {
        this.reconnectAttempts = 0
        this.ws.send(JSON.stringify({ type: 'auth', token }))
        this.pingInterval = setInterval(() => this.ping(), 30000)
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          // Handle pong responses
          if (data.type === 'pong') {
            return
          }
          
          // Handle connection confirmation
          if (data.type === 'connected') {
            return
          }
          
          // Handle new messages
          if (data.type === 'new_message' && this.onMessage) {
            this.onMessage(data.message)
          }
          
          // Handle message sent confirmation
          if (data.type === 'message_sent' && this.onMessage) {
            this.onMessage(data.message)
          }
          
          // Handle messages list
          if (data.type === 'messages' && this.onMessage) {
            this.onMessage({ type: 'messages_list', ...data })
          }
          
          // Handle errors
          if (data.type === 'error') {
            if (this.onError) {
              this.onError(new Error(data.message))
            }
          }
        } catch {
          // non-JSON messages ignored (e.g. pong)
        }
      }
      
      this.ws.onerror = () => {
        // connection failures handled in onclose
      }
      
      this.ws.onclose = (event) => {
        // Clear ping interval
        if (this.pingInterval) {
          clearInterval(this.pingInterval)
          this.pingInterval = null
        }
        
        // Don't reconnect if authentication error
        if (event.code === 4001) {
          if (this.onError) {
            this.onError(new Error('Authentication failed. Please log in again.'))
          }
          return
        }
        
        // Don't reconnect if manually closed (code 1000)
        if (event.wasClean && event.code === 1000) {
          return
        }
        
        // Handle connection failures (code 1006) - server unreachable
        if (event.code === 1006) {
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++
            this.reconnectDelay = Math.min(this.reconnectDelay * 2, 60000) // Max 60s for server issues
            setTimeout(() => this.connect(), this.reconnectDelay)
          }
          return
        }
        
        // Attempt to reconnect for other errors
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++
          setTimeout(() => this.connect(), this.reconnectDelay)
          this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000) // Exponential backoff, max 30s
        } else {
          if (this.onError) {
            this.onError(new Error('Failed to connect to messaging server after multiple attempts.'))
          }
        }
      }
    } catch (error) {
      if (this.onError) this.onError(error)
    }
  }
  
  disconnect() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
    }
    if (this.ws) {
      this.ws.close(1000) // Normal closure
      this.ws = null
    }
  }
  
  // Send ping to keep connection alive
  ping() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'ping' }))
    }
  }
  
  // Send a message
  sendMessage(recipientId, content, messageType = 'text') {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'send_message',
        recipient_id: recipientId,
        content,
        message_type: messageType
      }))
    }
  }
  
  // Get messages for a conversation
  getMessages(recipientId, limit = 50) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'get_messages',
        recipient_id: recipientId,
        limit
      }))
    }
  }
  
  // Mark conversation as read
  markRead(recipientId, messageId = null) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'mark_read',
        recipient_id: recipientId,
        message_id: messageId
      }))
    }
  }
}

export default api
