import axios from 'axios'

const isLocalhost = typeof window !== 'undefined' && ['localhost', '127.0.0.1'].includes(window.location.hostname)
const apiBaseURL = import.meta.env.VITE_API_URL || (isLocalhost ? '/api' : 'https://student-feedback-emotion-analyzer-api.onrender.com/api')

const api = axios.create({
  baseURL: apiBaseURL,
  timeout: 300000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor
api.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
)

// Response interceptor for consistent error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.error ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred'
    return Promise.reject(new Error(message))
  }
)

// Feedback APIs
export const analyzesFeedback = (data) => api.post('/analyze', data)
export const getFeedback = (params) => api.get('/feedback', { params })
export const getFeedbackById = (id) => api.get(`/feedback/${id}`)
export const deleteFeedback = (id) => api.delete(`/feedback/${id}`)

// Dashboard APIs
export const getDashboardSummary = () => api.get('/dashboard/summary')
export const getEmotionDistribution = () => api.get('/dashboard/emotions')
export const getSentimentDistribution = () => api.get('/dashboard/sentiments')
export const getCourseAnalysis = () => api.get('/dashboard/courses')
export const getSemesterTrends = () => api.get('/dashboard/semesters')
export const getCategoryAnalysis = () => api.get('/dashboard/categories')

// Model APIs
export const getModelMetrics = () => api.get('/model/metrics')

// Courses
export const getCourses = () => api.get('/courses')

// Health
export const getHealth = () => api.get('/health')

// Export
export const getExportURL = (params = {}) => {
  const qs = new URLSearchParams(params).toString()
  return `/api/export/csv${qs ? '?' + qs : ''}`
}

export default api
