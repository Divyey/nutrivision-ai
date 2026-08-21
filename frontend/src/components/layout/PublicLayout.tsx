import { Layout, Space, Typography } from 'antd'
import { Link, Outlet } from 'react-router-dom'

const { Header, Content, Footer } = Layout

export function PublicLayout() {
  return (
    <Layout className="page-shell">
      <Header className="public-header">
        <Space size="large">
          <Link to="/">
            <Typography.Title level={4} style={{ color: '#fff', margin: 0 }}>
              NutriVision AI
            </Typography.Title>
          </Link>
          <Link to="/login" style={{ color: '#fff' }}>
            Login
          </Link>
          <Link to="/register" style={{ color: '#fff' }}>
            Register
          </Link>
        </Space>
      </Header>
      <Content style={{ padding: '24px 16px' }}>
        <Outlet />
      </Content>
      <Footer style={{ textAlign: 'center' }}>NutriVision AI</Footer>
    </Layout>
  )
}
