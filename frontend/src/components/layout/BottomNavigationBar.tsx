import {
  CalendarOutlined,
  CameraOutlined,
  HomeOutlined,
  LineChartOutlined,
  StarOutlined,
} from '@ant-design/icons'
import { Tooltip } from 'antd'

type BottomNavigationBarProps = {
  pathname: string
  onNavigate: (path: string) => void
}

const tabs = [
  { path: '/dashboard', label: 'Home', icon: <HomeOutlined className="app-bottom-nav-icon" /> },
  {
    path: '/recommend',
    label: 'Recommend',
    comingSoon: true,
    icon: <StarOutlined className="app-bottom-nav-icon" />,
  },
  { path: '/detect', label: 'Scan', camera: true },
  { path: '/tracking', label: 'Tracking', icon: <CalendarOutlined className="app-bottom-nav-icon" /> },
  {
    path: '/progress',
    label: 'Progress',
    comingSoon: true,
    icon: <LineChartOutlined className="app-bottom-nav-icon" />,
  },
] as const

function tabClassName(active: boolean, scan: boolean): string {
  const names = ['app-bottom-nav-item']
  if (scan) names.push('app-bottom-nav-item-scan')
  if (active) names.push('app-bottom-nav-item-active')
  return names.join(' ')
}

export function BottomNavigationBar({ pathname, onNavigate }: BottomNavigationBarProps) {
  return (
    <div className="app-bottom-nav-wrap">
      <svg className="app-bottom-nav-shell" viewBox="0 0 390 84" preserveAspectRatio="none" aria-hidden>
        <path
          fill="#fff"
          d="M29 22H150C163 22 169 6 195 6s32 16 45 16h121a29 29 0 0 1 29 29 29 29 0 0 1-29 29H29A29 29 0 0 1 0 51a29 29 0 0 1 29-29Z"
        />
      </svg>
      <nav className="app-bottom-nav" aria-label="Primary">
        {tabs.map((tab) => {
          const scan = 'camera' in tab
          const comingSoon = 'comingSoon' in tab
          const active = pathname === tab.path
          const button = (
            <button
              type="button"
              className={tabClassName(active, scan)}
              aria-label={scan ? 'Scan food' : undefined}
              aria-current={active ? 'page' : undefined}
              title={comingSoon ? 'Coming soon' : undefined}
              onClick={() => onNavigate(tab.path)}
            >
              {scan ? (
                <span className="app-bottom-nav-scan">
                  <CameraOutlined />
                </span>
              ) : (
                tab.icon
              )}
              <span className="app-bottom-nav-label">{tab.label}</span>
              <span className="app-bottom-nav-mark" aria-hidden />
            </button>
          )

          return (
            <span key={tab.path} className="app-bottom-nav-cell">
              {comingSoon ? <Tooltip title="Coming soon">{button}</Tooltip> : button}
            </span>
          )
        })}
      </nav>
    </div>
  )
}
