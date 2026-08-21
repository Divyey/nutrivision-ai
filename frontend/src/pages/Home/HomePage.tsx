import { Button, Card, Typography } from 'antd'
import { useNavigate } from 'react-router-dom'

export function HomePage() {
  const navigate = useNavigate()

  return (
    <Card className="home-card">
      <Typography.Title level={2}>NutriVision AI</Typography.Title>
      <Typography.Paragraph>
        Track meals, recognize food from photos, and follow a diet that fits you.
      </Typography.Paragraph>
      <Button type="primary" size="large" onClick={() => navigate('/register')}>
        Get started
      </Button>
    </Card>
  )
}
