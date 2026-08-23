import {
  CalendarOutlined,
  CameraOutlined,
  HomeOutlined,
  LineChartOutlined,
  StarOutlined,
} from '@ant-design/icons'

type BottomNavigationBarProps = {
  pathname: string
  onNavigate: (path: string) => void
}

const tabs = [
  { path: '/dashboard', label: 'Home', icon: <HomeOutlined className="app-bottom-nav-icon" /> },
  { path: '/recommend', label: 'Recommend', icon: <StarOutlined className="app-bottom-nav-icon" /> },
  { path: '/detect', label: 'Scan', camera: true },
  { path: '/tracking', label: 'Tracking', icon: <CalendarOutlined className="app-bottom-nav-icon" /> },
  { path: '/progress', label: 'Progress', icon: <LineChartOutlined className="app-bottom-nav-icon" /> },
] as const

export function BottomNavigationBar({ pathname, onNavigate }: BottomNavigationBarProps) {
  return (
    <nav className="app-bottom-nav" aria-label="Primary">
      {tabs.map((tab) => {
        if (!('icon' in tab)) {
          return (
            <button
              key={tab.path}
              type="button"
              className="app-bottom-nav-scan"
              aria-label="Scan food"
              onClick={() => onNavigate(tab.path)}
            >
              <CameraOutlined />
            </button>
          )
        }

        const active = pathname === tab.path
        return (
          <button
            key={tab.path}
            type="button"
            className={active ? 'app-bottom-nav-item app-bottom-nav-item-active' : 'app-bottom-nav-item'}
            aria-current={active ? 'page' : undefined}
            onClick={() => onNavigate(tab.path)}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        )
      })}
    </nav>
  )
}
