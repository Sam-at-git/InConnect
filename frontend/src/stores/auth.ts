/**
 * Authentication Store
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  isAuthenticated: boolean
  accessToken: string | null
  user: {
    id: string
    name: string
    hotelId: string
    role: string
  } | null
  setAuth: (token: string, user: AuthState['user']) => void
  clearAuth: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      accessToken: null,
      user: null,
      setAuth: (token, user) => {
        localStorage.setItem('access_token', token)
        set({ isAuthenticated: true, accessToken: token, user })
      },
      clearAuth: () => {
        localStorage.removeItem('access_token')
        set({ isAuthenticated: false, accessToken: null, user: null })
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)
