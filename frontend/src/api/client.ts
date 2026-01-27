/**
 * API Client for InConnect
 */

import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// API Response type
interface APIResponse<T = unknown> {
  code: number
  message: string
  data: T | null
}

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Add auth token if available
    const token = localStorage.getItem('access_token')
    if (config.headers && token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => Promise.reject(error)
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error: AxiosError<APIResponse>) => {
    if (error.response?.data) {
      return Promise.reject(error.response.data)
    }
    return Promise.reject({
      code: 5000,
      message: 'Network error',
      data: null,
    })
  }
)

export default apiClient
export type { APIResponse }
