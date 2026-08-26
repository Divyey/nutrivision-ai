import { Button, Layout, Typography } from 'antd'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'

const { Header, Content, Footer } = Layout

export function PublicLayout({ authLinks = true }: { authLinks?: boolean }) {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const isHome = pathname === '/'

  return (
    <Layout className="page-shell">
      <Header className="public-header">
        <Link to="/" className="public-header-brand">
          <Typography.Title level={4} className="public-header-title">
            NutriVision AI
          </Typography.Title>
        </Link>
        {authLinks ? (
          <div className="public-header-actions">
            <Button type="text" className="public-header-login" onClick={() => navigate('/login')}>
              Log in
            </Button>
            <Button type="primary" className="home-cta" onClick={() => navigate('/register')}>
              Get started
            </Button>
          </div>
        ) : null}
      </Header>
      <Content className={isHome ? 'public-content public-content-home' : 'public-content'}>
        <Outlet />
      </Content>
      <Footer className="public-footer">NutriVision AI · tester preview</Footer>
    </Layout>
  )
}
