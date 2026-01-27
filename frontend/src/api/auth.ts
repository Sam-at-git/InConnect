/**
 * Authentication API
 */

import apiClient, { APIResponse } from './client'

export interface LoginRequest {
  wechat_userid: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  staff_id: string
  staff_name: string
  hotel_id: string
  role: string
}

export const authApi = {
  // Login
  login: async (data: LoginRequest) => {
    const response = await apiClient.post<APIResponse<LoginResponse>>('/login', data)
    return response.data
  },

  // Logout
  logout: async () => {
    const response = await apiClient.post<APIResponse>('/logout')
    return response.data
  },

  // Refresh token
  refreshToken: async () => {
    const response = await apiClient.post<APIResponse<LoginResponse>>('/refresh')
    return response.data
  },
}
