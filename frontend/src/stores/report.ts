/**
 * Report Store
 */

import { create } from 'zustand'
import {
  reportsApi,
  TicketReport,
  StaffReport,
  MessageReport,
  DashboardSummary,
  TimeRangeType,
} from '../api/reports'

interface ReportState {
  // Dashboard
  dashboard: DashboardSummary | null
  dashboardLoading: boolean

  // Tickets
  ticketReport: TicketReport | null
  ticketReportLoading: boolean
  ticketTimeRange: TimeRangeType

  // Staff
  staffReport: StaffReport | null
  staffReportLoading: boolean
  staffTimeRange: TimeRangeType

  // Messages
  messageReport: MessageReport | null
  messageReportLoading: boolean
  messageTimeRange: TimeRangeType

  // Current hotel ID
  hotelId: string

  // Actions
  setHotelId: (hotelId: string) => void
  fetchDashboard: (rangeType?: TimeRangeType) => Promise<void>
  fetchTicketReport: (rangeType?: TimeRangeType, department?: string) => Promise<void>
  fetchStaffReport: (rangeType?: TimeRangeType) => Promise<void>
  fetchMessageReport: (rangeType?: TimeRangeType) => Promise<void>
  setTicketTimeRange: (range: TimeRangeType) => void
  setStaffTimeRange: (range: TimeRangeType) => void
  setMessageTimeRange: (range: TimeRangeType) => void
}

export const useReportStore = create<ReportState>((set, get) => ({
  // Initial state
  dashboard: null,
  dashboardLoading: false,

  ticketReport: null,
  ticketReportLoading: false,
  ticketTimeRange: 'this_week',

  staffReport: null,
  staffReportLoading: false,
  staffTimeRange: 'this_month',

  messageReport: null,
  messageReportLoading: false,
  messageTimeRange: 'this_week',

  hotelId: 'default-hotel', // Default hotel ID

  // Actions
  setHotelId: (hotelId: string) => set({ hotelId }),

  fetchDashboard: async (rangeType: TimeRangeType = 'this_week') => {
    const { hotelId } = get()
    set({ dashboardLoading: true })
    try {
      const response = await reportsApi.getDashboard(hotelId, rangeType)
      set({ dashboard: response.data, dashboardLoading: false })
    } catch (error) {
      console.error('Failed to fetch dashboard:', error)
      set({ dashboardLoading: false })
    }
  },

  fetchTicketReport: async (rangeType?: TimeRangeType, department?: string) => {
    const { hotelId } = get()
    const finalRangeType = rangeType || get().ticketTimeRange
    set({ ticketReportLoading: true })
    try {
      const response = await reportsApi.getTickets(hotelId, finalRangeType, department)
      set({
        ticketReport: response.data,
        ticketReportLoading: false,
        ticketTimeRange: finalRangeType,
      })
    } catch (error) {
      console.error('Failed to fetch ticket report:', error)
      set({ ticketReportLoading: false })
    }
  },

  fetchStaffReport: async (rangeType?: TimeRangeType) => {
    const { hotelId } = get()
    const finalRangeType = rangeType || get().staffTimeRange
    set({ staffReportLoading: true })
    try {
      const response = await reportsApi.getStaff(hotelId, finalRangeType)
      set({
        staffReport: response.data,
        staffReportLoading: false,
        staffTimeRange: finalRangeType,
      })
    } catch (error) {
      console.error('Failed to fetch staff report:', error)
      set({ staffReportLoading: false })
    }
  },

  fetchMessageReport: async (rangeType?: TimeRangeType) => {
    const { hotelId } = get()
    const finalRangeType = rangeType || get().messageTimeRange
    set({ messageReportLoading: true })
    try {
      const response = await reportsApi.getMessages(hotelId, finalRangeType)
      set({
        messageReport: response.data,
        messageReportLoading: false,
        messageTimeRange: finalRangeType,
      })
    } catch (error) {
      console.error('Failed to fetch message report:', error)
      set({ messageReportLoading: false })
    }
  },

  setTicketTimeRange: (range: TimeRangeType) => set({ ticketTimeRange: range }),
  setStaffTimeRange: (range: TimeRangeType) => set({ staffTimeRange: range }),
  setMessageTimeRange: (range: TimeRangeType) => set({ messageTimeRange: range }),
}))
