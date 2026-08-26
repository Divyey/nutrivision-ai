import { useState } from 'react'
import { App, Button, Card, Form, Input, Typography } from 'antd'
import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'
import type { LoginRequest } from '../../types/auth'

const TEST_LOGIN = {
  name: 'Test User',
  email: 'nutrivision.ai@gmail.com',
  password: '12345678',
}

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const { message } = App.useApp()
  const [form] = Form.useForm<LoginRequest>()
  const [submitting, setSubmitting] = useState(false)

  return (
    <Card className="auth-card">
      <Typography.Title level={3} className="auth-card-title">
        Log in
      </Typography.Title>
      <Typography.Paragraph type="secondary" className="auth-card-lead">
        You will land on Home. From there, Scan photographs a plate and Tracking keeps the diary.
      </Typography.Paragraph>
      <Typography.Paragraph type="secondary" className="auth-card-demo">
        {TEST_LOGIN.name}
      </Typography.Paragraph>
      <Form
        form={form}
        layout="vertical"
        onFinish={async (values) => {
          setSubmitting(true)
          try {
            await login(values)
            navigate('/dashboard')
          } catch (error) {
            message.error(error instanceof Error ? error.message : 'Login failed')
          } finally {
            setSubmitting(false)
          }
        }}
      >
        <Form.Item
          label="Email"
          name="email"
          rules={[
            { required: true, message: 'Enter your email' },
            { type: 'email', message: 'Enter a valid email' },
          ]}
        >
          <Input autoComplete="email" placeholder={TEST_LOGIN.email} />
        </Form.Item>
        <Form.Item
          label="Password"
          name="password"
          rules={[{ required: true, message: 'Enter your password' }]}
        >
          <Input.Password autoComplete="current-password" placeholder={TEST_LOGIN.password} />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" block loading={submitting} className="home-cta">
            Log in
          </Button>
        </Form.Item>
      </Form>
      <Typography.Paragraph>
        No account? <Link to="/register">Register</Link>
      </Typography.Paragraph>
    </Card>
  )
}
