import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import { clearAccessToken, getAccessToken } from '../lib/token'
import { AuthService } from '../services/AuthService/AuthService'
import type { LoginRequest, RegisterRequest, UserPublic } from '../types/auth'
import { AuthContext } from './useAuth'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserPublic | null>(null)
  const [ready, setReady] = useState(() => !getAccessToken())

  useEffect(() => {
    const token = getAccessToken()
    if (!token) {
      return
    }

    let cancelled = false
    AuthService.me()
      .then((profile) => {
        if (!cancelled) {
          setUser(profile)
        }
      })
      .catch(() => {
        clearAccessToken()
        if (!cancelled) {
          setUser(null)
        }
      })
      .finally(() => {
        if (!cancelled) {
          setReady(true)
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  const login = useCallback(async (payload: LoginRequest) => {
    await AuthService.login(payload)
    const profile = await AuthService.me()
    setUser(profile)
  }, [])

  const register = useCallback(async (payload: RegisterRequest) => {
    await AuthService.register(payload)
    await login({ email: payload.email, password: payload.password })
  }, [login])

  const logout = useCallback(() => {
    clearAccessToken()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({ user, ready, login, register, logout }),
    [user, ready, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
