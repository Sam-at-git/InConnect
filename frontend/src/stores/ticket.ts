/**
 * Ticket Store
 */

import { create } from 'zustand'
import apiClient, { APIResponse } from '../api/client'

interface Ticket {
  id: string
  hotel_id: string
  title: string
  description?: string
  category: string
  priority: string
  status: string
  assigned_to?: string
  created_at: string
  updated_at: string
}

interface PaginatedTickets {
  items: Ticket[]
  total: number
  page: number
  page_size: number
  pages: number
}

interface TicketState {
  tickets: Ticket[]
  loading: boolean
  error: string | null
  pagination: {
    total: number
    page: number
    pageSize: number
    pages: number
  }
  fetchTickets: (params?: {
    page?: number
    pageSize?: number
    status?: string
    hotel_id?: string
  }) => Promise<void>
  createTicket: (data: Partial<Ticket>) => Promise<Ticket>
}

export const useTicketStore = create<TicketState>((set, get) => ({
  tickets: [],
  loading: false,
  error: null,
  pagination: {
    total: 0,
    page: 1,
    pageSize: 20,
    pages: 0,
  },

  fetchTickets: async (params = {}) => {
    set({ loading: true, error: null })
    try {
      const { page = 1, pageSize = 20, ...filters } = params
      const skip = (page - 1) * pageSize

      const response = await apiClient.get<APIResponse<PaginatedTickets>>('/tickets', {
        params: { skip, limit: pageSize, ...filters },
      })

      if (response.data) {
        set({
          tickets: response.data.items,
          pagination: {
            total: response.data.total,
            page: response.data.page,
            pageSize: response.data.page_size,
            pages: response.data.pages,
          },
          loading: false,
        })
      }
    } catch (error: unknown) {
      const err = error as APIResponse
      set({ error: err.message, loading: false })
    }
  },

  createTicket: async (data) => {
    const response = await apiClient.post<APIResponse<Ticket>>('/tickets', data)
    if (response.data) {
      return response.data
    }
    throw new Error('Failed to create ticket')
  },
}))
