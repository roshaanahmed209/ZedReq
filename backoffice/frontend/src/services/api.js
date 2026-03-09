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
  changePlan: (userId, plan) =>
    api.put(`/admin/users/${userId}/plan`, { plan }),
  cancelSubscription: (userId, reason) =>
    api.post(`/admin/users/${userId}/cancel-subscription`, { reason }),
  suspend: (userId, reason) =>
    api.post(`/admin/users/${userId}/suspend`, { reason }),
  unsuspend: (userId) =>
    api.post(`/admin/users/${userId}/unsuspend`),
  resetPassword: (userId, newPassword) =>
    api.post(`/admin/users/${userId}/reset-password`, { new_password: newPassword }),
  forceLogout: (userId) =>
    api.post(`/admin/users/${userId}/force-logout`),
  disable2fa: (userId, reason) =>
    api.post(`/admin/users/${userId}/disable-2fa`, { reason }),
  exportData: (userId) =>
    api.get(`/admin/users/${userId}/export`),
  sendNotification: (userId, subject, message) =>
    api.post(`/admin/users/${userId}/notify`, { subject, message }),
  delete: (userId, reason) =>
    api.delete(`/admin/users/${userId}`, { data: { reason: reason || 'Admin deletion' } }),
  assignEnterprise: (email) =>
    api.post('/admin/users/assign-enterprise', { email }),
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

// Monitoring API
export const monitoringApi = {
  // Uptime
  getUptime: (days = 30) => api.get('/monitoring/uptime', { params: { days } }),
  
  // Infrastructure
  getInfrastructure: (hours = 24, serverName = 'main') => 
    api.get('/monitoring/infrastructure', { params: { hours, server_name: serverName } }),
  
  // Performance
  getPerformance: (hours = 24, endpoint = null) => 
    api.get('/monitoring/performance', { params: { hours, endpoint } }),
  
  // Users
  getUsers: (days = 30) => api.get('/monitoring/users', { params: { days } }),
  
  // Pages
  getPages: (days = 7) => api.get('/monitoring/pages', { params: { days } }),
  
  // Interactions
  getInteractions: (days = 7) => api.get('/monitoring/interactions', { params: { days } }),
  
  // Links
  getLinks: (days = 7) => api.get('/monitoring/links', { params: { days } }),
  
  // Errors
  getErrors: (days = 7) => api.get('/monitoring/errors', { params: { days } }),
  
  // Security
  getSecurity: (days = 7) => api.get('/monitoring/security', { params: { days } }),
  
  // Database
  getDatabase: (hours = 24) => api.get('/monitoring/database', { params: { hours } }),
  
  // Growth
  getGrowth: (days = 30) => api.get('/monitoring/growth', { params: { days } }),
  
  // Alerts
  getAlertRules: () => api.get('/monitoring/alerts/rules'),
  createAlertRule: (ruleData) => api.post('/monitoring/alerts/rules', ruleData),
  getAlertHistory: (ruleId = null, limit = 50) => 
    api.get('/monitoring/alerts/history', { params: { rule_id: ruleId, limit } }),
  checkAlerts: () => api.post('/monitoring/alerts/check'),
}

export default api
