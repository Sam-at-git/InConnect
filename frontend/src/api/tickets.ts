/**
 * Ticket API
 */

import apiClient, { APIResponse } from './client'

export interface Ticket {
  id: string
  hotel_id: string
  title: string
  description?: string
  category: string
  priority: string
  status: string
  assigned_to?: string
  due_at?: string
  resolved_at?: string
  closed_at?: string
  created_at: string
  updated_at: string
}

export interface PaginatedTickets {
  items: Ticket[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface TicketCreate {
  hotel_id: string
  conversation_id?: string
  title: string
  description?: string
  category: string
  priority: string
  due_at?: string
}

export interface TicketTimeline {
  id: string
  ticket_id: string
  staff_id?: string
  event_type: string
  old_value?: string
  new_value?: string
  comment?: string
  created_at: string
}

export const ticketApi = {
  // List tickets
  list: async (params?: {
    page?: number
    pageSize?: number
    status?: string
    hotel_id?: string
    priority?: string
  }) => {
    const { page = 1, pageSize = 20, ...filters } = params || {}
    const skip = (page - 1) * pageSize
    const response = await apiClient.get<APIResponse<PaginatedTickets>>('/tickets', {
      params: { skip, limit: pageSize, ...filters },
    })
    return response.data
  },

  // Get ticket by ID
  get: async (id: string) => {
    const response = await apiClient.get<APIResponse<Ticket>>(`/tickets/${id}`)
    return response.data
  },

  // Create ticket
  create: async (data: TicketCreate) => {
    const response = await apiClient.post<APIResponse<Ticket>>('/tickets', data)
    return response.data
  },

  // Update ticket
  update: async (id: string, data: Partial<Ticket>) => {
    const response = await apiClient.put<APIResponse<Ticket>>(`/tickets/${id}`, data)
    return response.data
  },

  // Assign ticket
  assign: async (id: string, staffId: string, comment?: string) => {
    const response = await apiClient.post<APIResponse<Ticket>>(`/tickets/${id}/assign`, {
      staff_id: staffId,
      comment,
    })
    return response.data
  },

  // Update ticket status
  updateStatus: async (id: string, status: string, comment?: string) => {
    const response = await apiClient.post<APIResponse<Ticket>>(`/tickets/${id}/status`, {
      status,
      comment,
    })
    return response.data
  },

  // Get ticket timeline
  getTimeline: async (id: string) => {
    const response = await apiClient.get<APIResponse<TicketTimeline[]>>(
      `/tickets/${id}/timeline`
    )
    return response.data
  },

  // Get open tickets
  getOpen: async (hotelId?: string, limit = 50) => {
    const response = await apiClient.get<APIResponse<Ticket[]>>('/tickets/open', {
      params: { hotel_id: hotelId, limit },
    })
    return response.data
  },
}
