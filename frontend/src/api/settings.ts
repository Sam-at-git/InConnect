/**
 * System Settings API
 */

import apiClient, { APIResponse } from './client'

export interface SystemConfig {
  id: string
  key: string
  value: Record<string, any> | null
  description: string | null
  category: string
  created_at: string
  updated_at: string
}

export interface TicketCategoryConfig {
  key: string
  label: string
  color: string
  sla_hours?: number
  is_enabled: boolean
}

export interface PriorityConfig {
  key: string
  label: string
  color: string
  urgency_hours?: number
  is_enabled: boolean
}

export const settingsApi = {
  // List configs
  listConfigs: async (params?: { category?: string; skip?: number; limit?: number }) => {
    const response = await apiClient.get<APIResponse<SystemConfig[]>>(
      '/settings/configs',
      { params }
    )
    return response.data
  },

  // Get config by ID
  getConfig: async (id: string) => {
    const response = await apiClient.get<APIResponse<SystemConfig>>(`/settings/configs/${id}`)
    return response.data
  },

  // Create config
  createConfig: async (data: { key: string; value: Record<string, any>; category?: string; description?: string }) => {
    const response = await apiClient.post<APIResponse<SystemConfig>>('/settings/configs', data)
    return response.data
  },

  // Update config
  updateConfig: async (id: string, data: { value?: Record<string, any>; description?: string }) => {
    const response = await apiClient.put<APIResponse<SystemConfig>>(`/settings/configs/${id}`, data)
    return response.data
  },

  // Delete config
  deleteConfig: async (id: string) => {
    const response = await apiClient.delete<APIResponse>(`/settings/configs/${id}`)
    return response.data
  },

  // Get ticket categories
  getCategories: async () => {
    const response = await apiClient.get<APIResponse<TicketCategoryConfig[]>>('/settings/categories')
    return response.data
  },

  // Update ticket categories
  updateCategories: async (categories: TicketCategoryConfig[]) => {
    const response = await apiClient.put<APIResponse<TicketCategoryConfig[]>>('/settings/categories', categories)
    return response.data
  },

  // Get priorities
  getPriorities: async () => {
    const response = await apiClient.get<APIResponse<PriorityConfig[]>>('/settings/priorities')
    return response.data
  },

  // Update priorities
  updatePriorities: async (priorities: PriorityConfig[]) => {
    const response = await apiClient.put<APIResponse<PriorityConfig[]>>('/settings/priorities', priorities)
    return response.data
  },

  // Get system info
  getSystemInfo: async () => {
    const response = await apiClient.get<APIResponse<{
      version: string
      name: string
      stats: {
        tickets: number
        staff: number
        conversations: number
        messages: number
      }
    }>>('/settings/info')
    return response.data
  },
}
