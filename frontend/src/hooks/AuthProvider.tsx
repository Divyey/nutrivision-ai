import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import { clearAccessToken, getAccessToken } from '../lib/token'
import { AuthService } from '../services/AuthService/AuthService'
import { UserService } from '../services/UserService/UserService'
import type { LoginRequest, RegisterRequest, UserPublic } from '../types/auth'
import type { UserProfile } from '../types/user'
import { AuthContext } from './useAuth'

async function loadIdentityAndProfile(): Promise<{
  user: UserPublic
  profile: UserProfile | null
}> {
  const identity = await AuthService.me()
  try {
    return { user: identity, profile: await UserService.getMe() }
  } catch {
    return { user: identity, profile: null }
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserPublic | null>(null)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [ready, setReady] = useState(() => !getAccessToken())

  const applySession = useCallback((identity: UserPublic, nextProfile: UserProfile | null) => {
    setUser(identity)
    setProfile(nextProfile)
  }, [])

  useEffect(() => {
    const token = getAccessToken()
    if (!token) {
      return
    }

    let cancelled = false
    loadIdentityAndProfile()
      .then(({ user: identity, profile: nextProfile }) => {
        if (!cancelled) {
          applySession(identity, nextProfile)
        }
      })
      .catch(() => {
        clearAccessToken()
        if (!cancelled) {
          setUser(null)
          setProfile(null)
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
  }, [applySession])

  const login = useCallback(async (payload: LoginRequest) => {
    await AuthService.login(payload)
    const session = await loadIdentityAndProfile()
    applySession(session.user, session.profile)
  }, [applySession])

  const register = useCallback(async (payload: RegisterRequest) => {
    await AuthService.register(payload)
    await login({ email: payload.email, password: payload.password })
  }, [login])

  const logout = useCallback(() => {
    clearAccessToken()
    setUser(null)
    setProfile(null)
  }, [])

  const refreshProfile = useCallback(async () => {
    const session = await loadIdentityAndProfile()
    applySession(session.user, session.profile)
  }, [applySession])

  const value = useMemo(
    () => ({ user, profile, ready, login, register, logout, refreshProfile }),
    [user, profile, ready, login, register, logout, refreshProfile],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
