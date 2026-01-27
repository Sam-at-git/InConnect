/**
 * Message API
 */

import apiClient, { APIResponse } from './client'

export interface Conversation {
  id: string
  hotel_id: string
  guest_id: string
  guest_name?: string
  guest_phone?: string
  status: string
  last_message_at?: string
}

export interface Message {
  id: string
  conversation_id: string
  message_type: string
  direction: string
  content?: string
  media_url?: string
  sender_id?: string
  is_read: boolean
  sent_at: string
  created_at: string
}

export interface MessageSendRequest {
  conversation_id: string
  content: string
  message_type?: string
  media_url?: string
}

export interface MessageSendResponse {
  message_id: string
  status: string
  wechat_msgid?: string
}

export const messageApi = {
  // List conversations
  listConversations: async (params?: {
    hotel_id?: string
    status?: string
    limit?: number
  }) => {
    const response = await apiClient.get<APIResponse<Conversation[]>>(
      '/messages/conversations',
      { params }
    )
    return response.data
  },

  // Get conversation messages
  getMessages: async (conversationId: string, limit = 50) => {
    const response = await apiClient.get<APIResponse<Message[]>>(
      `/messages/conversations/${conversationId}/messages`,
      { params: { limit } }
    )
    return response.data
  },

  // Send message
  send: async (data: MessageSendRequest) => {
    const response = await apiClient.post<APIResponse<MessageSendResponse>>(
      '/messages/send',
      data
    )
    return response.data
  },

  // Close conversation
  closeConversation: async (conversationId: string) => {
    const response = await apiClient.post<APIResponse>(
      `/messages/conversations/${conversationId}/close`
    )
    return response.data
  },

  // Advanced search
  search: async (params: {
    hotel_id: string
    keyword?: string
    conversation_id?: string
    message_type?: string
    direction?: string
    start_date?: string
    end_date?: string
    limit?: number
  }) => {
    const response = await apiClient.get<APIResponse<Message[]>>(
      '/messages/search',
      { params }
    )
    return response.data
  },

  // Export messages
  export: async (params: {
    hotel_id: string
    keyword?: string
    conversation_id?: string
    start_date?: string
    end_date?: string
  }) => {
    const response = await apiClient.get('/messages/export', {
      params,
      responseType: 'blob',
    })
    return response
  },
}
