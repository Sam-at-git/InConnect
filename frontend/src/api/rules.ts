/**
 * Routing Rules API
 */

import apiClient, { APIResponse } from './client'

export interface RoutingRule {
  id: string
  name: string
  type: string
  keywords?: string[]
  category?: string
  priority?: string
  target_staff_count: number
  rule_priority: number
  is_active: boolean
}

export interface RuleTestRequest {
  message_content: string
  category?: string
  priority?: string
}

export interface RuleTestResult {
  matched_rule: {
    id: string | null
    name: string
    type: string
    priority_level: number
  }
  assigned_staff: Array<{
    id: string
    name: string
    department: string | null
  }>
  message_content: string
  category?: string
  priority?: string
}

export interface RuleCreateRequest {
  name: string
  rule_type: string
  keywords?: string[]
  category?: string
  priority?: string
  target_staff_ids: string[]
  rule_priority: number
  is_active: boolean
}

export const rulesApi = {
  // Test routing rule
  test: async (hotelId: string, request: RuleTestRequest) => {
    const response = await apiClient.post<APIResponse<RuleTestResult>>(
      '/rules/test',
      request,
      { params: { hotel_id: hotelId } }
    )
    return response.data
  },

  // Get rules summary
  getSummary: async (hotelId: string) => {
    const response = await apiClient.get<APIResponse<RoutingRule[]>>('/rules/summary', {
      params: { hotel_id: hotelId },
    })
    return response.data
  },

  // Create rule
  create: async (hotelId: string, request: RuleCreateRequest) => {
    const response = await apiClient.post<APIResponse<{ id: string; name: string }>>(
      '/rules',
      request,
      { params: { hotel_id: hotelId } }
    )
    return response.data
  },

  // Update rule
  update: async (ruleId: string, request: Partial<RuleCreateRequest>) => {
    const response = await apiClient.put<APIResponse<{ id: string; name: string }>>(
      `/rules/${ruleId}`,
      request
    )
    return response.data
  },

  // Delete rule
  delete: async (ruleId: string) => {
    const response = await apiClient.delete<APIResponse>(`/rules/${ruleId}`)
    return response.data
  },

  // Reorder rule
  reorder: async (ruleId: string, newPriority: number) => {
    const response = await apiClient.post<APIResponse<{ id: string; priority_level: number }>>(
      `/rules/${ruleId}/reorder`,
      { new_priority: newPriority }
    )
    return response.data
  },
}
