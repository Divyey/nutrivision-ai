import { Outlet } from 'react-router-dom'

import '../../pages/Detection/detection.css'

export function DetectionLayout() {
  return (
    <div className="detection-shell">
      <Outlet />
    </div>
  )
}
