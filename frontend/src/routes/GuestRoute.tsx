import { Navigate, Outlet } from 'react-router-dom'

import { PageSpinner } from '../components/layout/PageSpinner'
import { useAuth } from '../hooks/useAuth'

export function GuestRoute() {
  const { user, ready } = useAuth()

  if (!ready) {
    return <PageSpinner />
  }

  if (user) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}
