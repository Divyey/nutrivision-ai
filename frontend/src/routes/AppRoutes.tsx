import { Navigate, Route, Routes } from 'react-router-dom'

import { AppLayout } from '../components/layout/AppLayout'
import { PublicLayout } from '../components/layout/PublicLayout'
import { DashboardPage } from '../pages/Dashboard/DashboardPage'
import { HomePage } from '../pages/Home/HomePage'
import { LoginPage } from '../pages/Login/LoginPage'
import { ProfilePage } from '../pages/Profile/ProfilePage'
import { ProfileSetupPage } from '../pages/ProfileSetup/ProfileSetupPage'
import { RegisterPage } from '../pages/Register/RegisterPage'
import { GuestRoute } from './GuestRoute'
import { PrivateRoute } from './PrivateRoute'
import { RequireCompleteProfile } from './RequireCompleteProfile'
import { RequireIncompleteProfile } from './RequireIncompleteProfile'

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route element={<GuestRoute />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Route>
      </Route>
      <Route element={<PrivateRoute />}>
        <Route element={<PublicLayout authLinks={false} />}>
          <Route element={<RequireIncompleteProfile />}>
            <Route path="/register/setup" element={<ProfileSetupPage />} />
          </Route>
        </Route>
        <Route element={<RequireCompleteProfile />}>
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Route>
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
