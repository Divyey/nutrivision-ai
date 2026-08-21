import { DashboardOutlined, LogoutOutlined } from '@ant-design/icons'
import { Grid, Layout, Menu, Typography } from 'antd'
import { useState } from 'react'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'

const { Header, Sider, Content } = Layout

export function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const screens = Grid.useBreakpoint()
  const isMobile = !screens.md
  const [collapsed, setCollapsed] = useState(false)

  return (
    <Layout className="page-shell">
      <Sider
        breakpoint="md"
        collapsedWidth={isMobile ? 0 : 80}
        collapsed={collapsed}
        onCollapse={setCollapsed}
      >
        <div className="sider-brand">
          <Typography.Text strong style={{ color: '#fff' }}>
            NutriVision AI
          </Typography.Text>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={[
            {
              key: '/dashboard',
              icon: <DashboardOutlined />,
              label: <Link to="/dashboard">Dashboard</Link>,
            },
            {
              key: 'logout',
              icon: <LogoutOutlined />,
              label: 'Logout',
              onClick: () => {
                logout()
                navigate('/login')
              },
            },
          ]}
        />
      </Sider>
      <Layout>
        <Header className="app-header">
          <Typography.Text>{user?.name}</Typography.Text>
        </Header>
        <Content className="app-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
