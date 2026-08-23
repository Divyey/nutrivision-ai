import { Card, Typography } from 'antd'

export function RecommendationPage() {
  return (
    <Card>
      <Typography.Title level={3}>Recommend</Typography.Title>
      <Typography.Paragraph type="secondary">
        Meal recommendations
      </Typography.Paragraph>
    </Card>
  )
}
