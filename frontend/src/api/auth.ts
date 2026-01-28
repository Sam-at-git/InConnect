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
  // Login - interceptor already unwraps response.data, so return directly
  login: async (data: LoginRequest): Promise<APIResponse<LoginResponse>> => {
    return apiClient.post('/login', data) as Promise<APIResponse<LoginResponse>>
  },

  // Logout
  logout: async (): Promise<APIResponse> => {
    return apiClient.post('/logout') as Promise<APIResponse>
  },

  // Refresh token
  refreshToken: async (): Promise<APIResponse<LoginResponse>> => {
    return apiClient.post('/refresh') as Promise<APIResponse<LoginResponse>>
  },
}
