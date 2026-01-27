/**
 * Quick Reply Template Store
 */

import { create } from 'zustand'
import { quickReplyApi, QuickReplyTemplate } from '../api/quickReply'

interface TemplateState {
  templates: QuickReplyTemplate[]
  loading: boolean
  error: string | null
  categories: string[]
  fetchTemplates: (hotelId: string) => Promise<void>
  createTemplate: (data: Partial<QuickReplyTemplate>) => Promise<void>
  useTemplate: (id: string, variables?: Record<string, string>) => Promise<string>
}

export const useTemplateStore = create<TemplateState>((set, get) => ({
  templates: [],
  loading: false,
  error: null,
  categories: ['问候', '确认', '道歉', '查询', '其他'],

  fetchTemplates: async (hotelId: string) => {
    set({ loading: true, error: null })
    try {
      const response = await quickReplyApi.list({ hotel_id: hotelId, is_active: true })
      if (response.data) {
        set({ templates: response.data, loading: false })
      }
    } catch (error: unknown) {
      const err = error as { message?: string }
      set({ error: err.message || 'Failed to fetch templates', loading: false })
    }
  },

  createTemplate: async (data) => {
    const response = await quickReplyApi.create(data as any)
    if (response.data) {
      set((state) => ({
        templates: [...state.templates, response.data!],
      }))
    }
  },

  useTemplate: async (id: string, variables = {}) => {
    const response = await quickReplyApi.use(id, variables)
    if (response.data) {
      return response.data.content
    }
    throw new Error('Failed to use template')
  },
}))
