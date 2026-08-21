import { createContext, useContext } from 'react'

import type { LoginRequest, RegisterRequest, UserPublic } from '../types/auth'

export type AuthContextValue = {
  user: UserPublic | null
  ready: boolean
  login: (payload: LoginRequest) => Promise<void>
  register: (payload: RegisterRequest) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
