import { Card, Typography } from 'antd'

import { useAuth } from '../../hooks/useAuth'

export function DashboardPage() {
  const { user } = useAuth()

  return (
    <Card>
      <Typography.Title level={3}>Dashboard</Typography.Title>
      <Typography.Paragraph>
        Signed in as {user?.name} ({user?.email}).
      </Typography.Paragraph>
      <Typography.Paragraph type="secondary">
        Food detection, tracking, and recommendations will land here as those
        backend services are built.
      </Typography.Paragraph>
    </Card>
  )
}
