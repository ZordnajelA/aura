import axios from 'axios'

// Dynamically construct API URL based on current hostname
// This allows the app to work with localhost, IP addresses, or domain names
const getApiUrl = (): string => {
  // Use environment variable if provided (for production deployments)
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }

  // In development, construct URL using current hostname
  const protocol = window.location.protocol // 'http:' or 'https:'
  const hostname = window.location.hostname // 'localhost', '192.168.50.201', or domain
  const port = 8000 // Backend port

  return `${protocol}//${hostname}:${port}/api`
}

const API_URL = getApiUrl()

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
