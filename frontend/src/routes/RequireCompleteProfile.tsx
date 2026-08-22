import { Navigate, Outlet } from 'react-router-dom'

import { PageSpinner } from '../components/layout/PageSpinner'
import { useAuth } from '../hooks/useAuth'
import { isProfileComplete } from '../types/user'

export function RequireCompleteProfile() {
  const { ready, profile } = useAuth()

  if (!ready) {
    return <PageSpinner />
  }

  if (!isProfileComplete(profile)) {
    return <Navigate to="/register/setup" replace />
  }

  return <Outlet />
}
