import { Card, Typography } from 'antd'

export function ProgressPage() {
  return (
    <Card>
      <Typography.Title level={3}>Progress</Typography.Title>
      <Typography.Paragraph type="secondary">
        Daily and weekly progress
      </Typography.Paragraph>
    </Card>
  )
}
