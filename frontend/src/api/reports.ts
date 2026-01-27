/**
 * Reports API
 */

import apiClient, { APIResponse } from './client'

export interface TicketStatusStats {
  status: string
  count: number
  percentage: number
}

export interface TicketPriorityStats {
  priority: string
  count: number
  percentage: number
}

export interface TicketCategoryStats {
  category: string
  count: number
  percentage: number
}

export interface TicketReport {
  total: number
  by_status: TicketStatusStats[]
  by_priority: TicketPriorityStats[]
  by_category: TicketCategoryStats[]
  created_in_period: number
  resolved_in_period: number
  closed_in_period: number
  avg_resolution_hours: number | null
  overdue_count: number
}

export interface StaffPerformanceStats {
  staff_id: string
  staff_name: string
  department: string | null
  total_assigned: number
  total_resolved: number
  total_in_progress: number
  resolution_rate: number
  avg_resolution_hours: number | null
  avg_response_hours: number | null
}

export interface StaffReport {
  total_staff: number
  staff_stats: StaffPerformanceStats[]
  period_start: string
  period_end: string
}

export interface MessageTypeStats {
  message_type: string
  count: number
  percentage: number
}

export interface MessageDirectionStats {
  direction: string
  count: number
  percentage: number
}

export interface MessageReport {
  total: number
  by_type: MessageTypeStats[]
  by_direction: MessageDirectionStats[]
  avg_daily_count: number
  peak_conversations: number
  period_start: string
  period_end: string
}

export interface DashboardSummary {
  total_tickets: number
  pending_tickets: number
  in_progress_tickets: number
  overdue_tickets: number
  total_messages: number
  unread_messages: number
  active_conversations: number
  available_staff: number
  period_start: string
  period_end: string
}

export type TimeRangeType =
  | 'today'
  | 'yesterday'
  | 'this_week'
  | 'last_week'
  | 'this_month'
  | 'last_month'
  | 'custom'

export const reportsApi = {
  // Get dashboard summary
  getDashboard: async (hotelId: string, rangeType: TimeRangeType = 'this_week') => {
    const response = await apiClient.get<APIResponse<DashboardSummary>>(
      '/reports/dashboard',
      {
        params: { hotel_id: hotelId, range_type: rangeType },
      }
    )
    return response.data
  },

  // Get ticket report
  getTickets: async (
    hotelId: string,
    rangeType: TimeRangeType = 'this_week',
    department?: string
  ) => {
    const response = await apiClient.get<APIResponse<TicketReport>>(
      '/reports/tickets',
      {
        params: { hotel_id: hotelId, range_type: rangeType, department },
      }
    )
    return response.data
  },

  // Get staff report
  getStaff: async (hotelId: string, rangeType: TimeRangeType = 'this_month') => {
    const response = await apiClient.get<APIResponse<StaffReport>>('/reports/staff', {
      params: { hotel_id: hotelId, range_type: rangeType },
    })
    return response.data
  },

  // Get message report
  getMessages: async (hotelId: string, rangeType: TimeRangeType = 'this_week') => {
    const response = await apiClient.get<APIResponse<MessageReport>>(
      '/reports/messages',
      {
        params: { hotel_id: hotelId, range_type: rangeType },
      }
    )
    return response.data
  },
}
