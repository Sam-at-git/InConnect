/**
 * Batch Operations API
 */

import apiClient, { APIResponse } from './client'

export interface BatchAssignRequest {
  ticket_ids: string[]
  staff_id: string
  comment?: string
}

export interface BatchStatusUpdateRequest {
  ticket_ids: string[]
  status: string
  comment?: string
}

export interface BatchOperationResult {
  success_count: number
  failed_count: number
  failed_ids: string[]
  errors: string[]
}

export const batchApi = {
  // Batch assign tickets
  assign: async (request: BatchAssignRequest) => {
    const response = await apiClient.post<APIResponse<BatchOperationResult>>(
      '/batch/assign',
      request
    )
    return response.data
  },

  // Batch update status
  updateStatus: async (request: BatchStatusUpdateRequest) => {
    const response = await apiClient.post<APIResponse<BatchOperationResult>>(
      '/batch/status',
      request
    )
    return response.data
  },

  // Export tickets
  export: async (params: {
    hotel_id: string
    status?: string
    priority?: string
    category?: string
    start_date?: string
    end_date?: string
    format?: string
  }) => {
    const response = await apiClient.get('/batch/export', {
      params,
      responseType: 'blob',
    })
    return response
  },
}
