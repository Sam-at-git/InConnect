/**
 * Quick Reply Templates
 */

import { apiClient, APIResponse } from './client'

export interface QuickReplyTemplate {
  id: string
  hotel_id: string
  name: string
  category: string
  content: string
  variables?: string[]
  is_active: boolean
  usage_count: number
  created_at: string
  updated_at: string
}

export interface TemplateCreate {
  hotel_id: string
  name: string
  category: string
  content: string
  variables?: string[]
}

export interface TemplateUpdate {
  name?: string
  category?: string
  content?: string
  variables?: string[]
  is_active?: boolean
}

export const quickReplyApi = {
  // List templates
  list: async (params?: {
    hotel_id?: string
    category?: string
    is_active?: boolean
  }) => {
    const response = await apiClient.get<APIResponse<QuickReplyTemplate[]>>(
      '/quick-replies',
      { params }
    )
    return response.data
  },

  // Get template by ID
  get: async (id: string) => {
    const response = await apiClient.get<APIResponse<QuickReplyTemplate>>(
      `/quick-replies/${id}`
    )
    return response.data
  },

  // Create template
  create: async (data: TemplateCreate) => {
    const response = await apiClient.post<APIResponse<QuickReplyTemplate>>(
      '/quick-replies',
      data
    )
    return response.data
  },

  // Update template
  update: async (id: string, data: TemplateUpdate) => {
    const response = await apiClient.put<APIResponse<QuickReplyTemplate>>(
      `/quick-replies/${id}`,
      data
    )
    return response.data
  },

  // Delete template
  delete: async (id: string) => {
    const response = await apiClient.delete<APIResponse>(
      `/quick-replies/${id}`
    )
    return response.data
  },

  // Use template (increments usage count)
  use: async (id: string, variables?: Record<string, string>) => {
    const response = await apiClient.post<APIResponse<{ content: string }>>(
      `/quick-replies/${id}/use`,
      { variables }
    )
    return response.data
  },
}
