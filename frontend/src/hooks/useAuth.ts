import { createContext, useContext } from 'react'

import type { LoginRequest, RegisterRequest, UserPublic } from '../types/auth'
import type { UserProfile } from '../types/user'

export type AuthContextValue = {
  user: UserPublic | null
  profile: UserProfile | null
  ready: boolean
  login: (payload: LoginRequest) => Promise<void>
  register: (payload: RegisterRequest) => Promise<void>
  logout: () => void
  refreshProfile: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
