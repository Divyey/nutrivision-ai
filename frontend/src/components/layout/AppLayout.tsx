import { DashboardOutlined, LogoutOutlined, UserOutlined } from '@ant-design/icons'
import { Avatar, Breadcrumb, Dropdown, Grid, Layout, Menu, Space, Typography, theme } from 'antd'
import { useState } from 'react'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'

const { Header, Sider, Content } = Layout

function breadcrumbItems(pathname: string) {
  if (pathname === '/profile') {
    return [{ title: <Link to="/dashboard">Dashboard</Link> }, { title: 'My Profile' }]
  }
  return [{ title: 'Dashboard' }]
}

export function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const screens = Grid.useBreakpoint()
  const isMobile = !screens.md
  const [collapsed, setCollapsed] = useState(false)
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken()

  return (
    <Layout className="page-shell">
      <Header className="app-header">
        <Typography.Title level={4} className="app-header-brand">
          NutriVision AI
        </Typography.Title>
        <Dropdown
          menu={{
            items: [
              {
                key: 'profile',
                icon: <UserOutlined />,
                label: 'My Profile',
                onClick: () => navigate('/profile'),
              },
              { type: 'divider' },
              {
                key: 'logout',
                icon: <LogoutOutlined />,
                label: 'Logout',
                onClick: () => {
                  logout()
                  navigate('/login')
                },
              },
            ],
          }}
        >
          <Space className="app-header-user">
            <Avatar icon={<UserOutlined />} />
            <Typography.Text className="app-header-username">{user?.name}</Typography.Text>
          </Space>
        </Dropdown>
      </Header>
      <Layout>
        <Sider
          width={200}
          breakpoint="md"
          collapsedWidth={isMobile ? 0 : 80}
          collapsed={collapsed}
          onCollapse={setCollapsed}
          style={{ background: colorBgContainer }}
        >
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            style={{ height: '100%', borderInlineEnd: 0 }}
            items={[
              {
                key: '/dashboard',
                icon: <DashboardOutlined />,
                label: <Link to="/dashboard">Dashboard</Link>,
              },
            ]}
          />
        </Sider>
        <Layout style={{ padding: '0 24px 24px' }}>
          <Breadcrumb items={breadcrumbItems(location.pathname)} style={{ margin: '16px 0' }} />
          <Content
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
            }}
          >
            <Outlet />
          </Content>
        </Layout>
      </Layout>
    </Layout>
  )
}
