import { CalendarOutlined, CameraOutlined, CheckCircleOutlined } from '@ant-design/icons'
import { Alert, Button, Card, Typography } from 'antd'
import { useNavigate } from 'react-router-dom'

import './home.css'

const STEPS = [
  {
    icon: <CameraOutlined />,
    title: 'Photo the plate',
    body: 'Open Scan and take a picture of an Indian meal. We label the dishes we recognize.',
  },
  {
    icon: <CheckCircleOutlined />,
    title: 'Confirm and log',
    body: 'Check the names, pick breakfast/lunch/dinner/snacks, and save. Calories come from our food table, not from the photo size.',
  },
  {
    icon: <CalendarOutlined />,
    title: 'See it on Tracking',
    body: 'The diary adds protein, carbs, fat, and kcal. Use Add if Scan misses something (roti, chapati, dal).',
  },
] as const

export function HomePage() {
  const navigate = useNavigate()

  return (
    <div className="home-page">
      <section className="home-hero">
        <div className="home-hero-visual" aria-hidden>
          <CameraOutlined />
        </div>
        <Typography.Text className="home-hero-kicker">Food in, calories out</Typography.Text>
        <Typography.Title level={1} className="home-hero-title">
          Photograph your plate. Log the meal.
        </Typography.Title>
        <Typography.Paragraph className="home-hero-lead">
          NutriVision spots Indian dishes in a photo so you can keep a simple food diary. Create an
          account to try Scan and Tracking — this round is for a few testers.
        </Typography.Paragraph>
        <div className="home-hero-actions">
          <Button
            type="primary"
            size="large"
            className="home-cta"
            onClick={() => navigate('/register')}
          >
            Create account
          </Button>
          <Button size="large" onClick={() => navigate('/login')}>
            Log in
          </Button>
        </div>
      </section>

      <section className="home-section">
        <Typography.Title level={3} className="home-section-title">
          How to try it
        </Typography.Title>
        <Typography.Paragraph type="secondary" className="home-section-lead">
          After you sign up we ask a few body details so calorie goals have somewhere to land.
        </Typography.Paragraph>
        <div className="home-steps">
          {STEPS.map((step) => (
            <Card key={step.title} size="small" className="home-step">
              <span className="home-step-icon">{step.icon}</span>
              <Typography.Title level={5}>{step.title}</Typography.Title>
              <Typography.Paragraph type="secondary">{step.body}</Typography.Paragraph>
            </Card>
          ))}
        </div>
      </section>

      <section className="home-section">
        <Alert
          className="home-note"
          type="success"
          showIcon
          message="In this test"
          description="Scan, Tracking (photo log and typed Add), and profile calorie goals work. Recommend and Progress are empty on purpose — tap them if you want, nothing is missing on your account."
        />
      </section>
    </div>
  )
}
