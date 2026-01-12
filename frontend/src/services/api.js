import axios from 'axios'

// Create axios instance with default configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // You can add auth tokens here if using JWT instead of sessions
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle specific error codes
    if (error.response) {
      const { status } = error.response
      
      // Log error for debugging
      console.error('API Error:', {
        status,
        url: error.config?.url,
        message: error.response?.data?.message
      })
      
      // Handle 401 Unauthorized - redirect to login if needed
      if (status === 401) {
        // Only redirect if not already on auth pages
        const isAuthPage = window.location.pathname === '/landing' || 
                          window.location.pathname === '/login' ||
                          window.location.pathname === '/'
        
        if (!isAuthPage && !error.config?.url?.includes('/session')) {
          // Optionally trigger a redirect or event
          window.dispatchEvent(new CustomEvent('auth:unauthorized'))
        }
      }
    }
    
    return Promise.reject(error)
  }
)

// Auth API methods
export const authAPI = {
  login: (username, password) => api.post('/login', { username, password }),
  register: (userData) => api.post('/register', userData),
  logout: () => api.get('/logout'),
  checkSession: () => api.get('/session'),
}

// User API methods
export const userAPI = {
  getCurrentUser: () => api.get('/api/user'),
  updateProfile: (data) => api.put('/api/user', data),
  searchUsers: (query) => api.get('/api/users/search', { params: { q: query } }),
}

export default api
