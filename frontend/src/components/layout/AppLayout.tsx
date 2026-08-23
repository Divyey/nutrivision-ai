import { UserOutlined } from '@ant-design/icons'
import { Avatar, Grid, Layout, Typography, theme } from 'antd'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'
import { BottomNavigationBar } from './BottomNavigationBar'

const { Header, Content } = Layout

export function AppLayout() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const screens = Grid.useBreakpoint()
  const isCompactHeader = !screens.md
  const {
    token: { colorBgContainer },
  } = theme.useToken()

  return (
    <Layout className="page-shell page-shell-app">
      <Header className={isCompactHeader ? 'app-header app-header-mobile' : 'app-header'}>
        <Typography.Title level={4} className="app-header-brand">
          NutriVision AI
        </Typography.Title>
        <button
          type="button"
          className="app-header-user"
          aria-label="My Profile"
          onClick={() => navigate('/profile')}
        >
          <Avatar icon={<UserOutlined />} />
          {isCompactHeader ? null : (
            <Typography.Text className="app-header-username">{user?.name}</Typography.Text>
          )}
        </button>
      </Header>
      <Content className="app-content" style={{ background: colorBgContainer }}>
        <Outlet />
      </Content>
      <BottomNavigationBar pathname={location.pathname} onNavigate={navigate} />
    </Layout>
  )
}
