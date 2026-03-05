import axios from 'axios'

// Create axios instance
// Use relative path since frontend is served from same origin as backend
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // Set to true if using cookies for auth
})

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: (username, password) =>
    api.post('/admin/auth/login', { username, password }),
  getMe: () => api.get('/admin/auth/me'),
}

// Users API
export const usersAPI = {
  getAll: (params) => api.get('/admin/users', { params }),
  getById: (userId) => api.get(`/admin/users/${userId}`),
  updateRole: (userId, newRole) =>
    api.put(`/admin/users/${userId}/role`, null, { params: { new_role: newRole } }),
  suspend: (userId, reason) =>
    api.post(`/admin/users/${userId}/suspend`, { reason }),
  delete: (userId) => api.delete(`/admin/users/${userId}`),
}

// Analytics API
export const analyticsAPI = {
  getRevenue: (params) => api.get('/admin/analytics/revenue', { params }),
  getCosts: (params) => api.get('/admin/analytics/costs', { params }),
  getCashFlow: (params) => api.get('/admin/analytics/cash-flow', { params }),
  getSubscriptions: () => api.get('/admin/analytics/subscriptions'),
  getDashboard: () => api.get('/admin/analytics/dashboard'),
}

// Financial API
export const financialAPI = {
  getTransactions: (params) => api.get('/admin/financial/transactions', { params }),
  createRevenue: (data) => api.post('/admin/financial/revenue', data),
  createCost: (data) => api.post('/admin/financial/cost', data),
  getSummaries: (params) => api.get('/admin/financial/summaries', { params }),
  generateSummary: (data) => api.post('/admin/financial/summaries/generate', data),
  getCosts: (params) => api.get('/admin/financial/costs', { params }),
}

// Activity API
export const activityAPI = {
  getLogs: (params) => api.get('/admin/activity/logs', { params }),
  getLogById: (logId) => api.get(`/admin/activity/logs/${logId}`),
}

export default api
