/**
 * Staff API
 */

import apiClient, { APIResponse } from './client'

export interface Staff {
  id: string
  hotel_id: string
  name: string
  wechat_userid?: string
  phone?: string
  email?: string
  role: string
  department?: string
  status: string
  is_available: boolean
  created_at: string
  updated_at: string
}

export interface StaffListParams {
  skip?: number
  limit?: number
  hotel_id?: string
  role?: string
  status?: string
  is_available?: boolean
}

export interface PaginatedStaffList {
  items: Staff[]
  total: number
  page: number
  page_size: number
  pages: number
}

export const staffApi = {
  // List staff with pagination
  list: async (params?: StaffListParams) => {
    const response = await apiClient.get<APIResponse<PaginatedStaffList>>('/staff', {
      params,
    })
    return response.data
  },

  // Get staff by ID
  get: async (staffId: string) => {
    const response = await apiClient.get<APIResponse<Staff>>(`/staff/${staffId}`)
    return response.data
  },

  // Create staff
  create: async (staff: Omit<Staff, 'id' | 'created_at' | 'updated_at'>) => {
    const response = await apiClient.post<APIResponse<Staff>>('/staff', staff)
    return response.data
  },

  // Update staff
  update: async (staffId: string, staff: Partial<Staff>) => {
    const response = await apiClient.put<APIResponse<Staff>>(`/staff/${staffId}`, staff)
    return response.data
  },

  // Delete staff
  delete: async (staffId: string) => {
    const response = await apiClient.delete<APIResponse>(`/staff/${staffId}`)
    return response.data
  },

  // Toggle availability
  toggleAvailability: async (staffId: string) => {
    const response = await apiClient.post<APIResponse<Staff>>(
      `/staff/${staffId}/toggle-availability`
    )
    return response.data
  },
}
