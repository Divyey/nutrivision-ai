import { useState } from 'react'
import { App, Button, Card, Form, Input, Typography } from 'antd'
import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'
import type { LoginRequest } from '../../types/auth'

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const { message } = App.useApp()
  const [form] = Form.useForm<LoginRequest>()
  const [submitting, setSubmitting] = useState(false)

  return (
    <Card title="Log in" className="auth-card">
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
          <Input autoComplete="email" />
        </Form.Item>
        <Form.Item
          label="Password"
          name="password"
          rules={[{ required: true, message: 'Enter your password' }]}
        >
          <Input.Password autoComplete="current-password" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" block loading={submitting}>
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
