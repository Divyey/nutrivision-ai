import { useState } from 'react'
import { App, Button, Card, Form, Input, Typography } from 'antd'
import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'
import type { RegisterRequest } from '../../types/auth'

export function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const { message } = App.useApp()
  const [form] = Form.useForm<RegisterRequest>()
  const [submitting, setSubmitting] = useState(false)

  return (
    <Card title="Create an account" className="auth-card">
      <Form
        form={form}
        layout="vertical"
        onFinish={async (values) => {
          setSubmitting(true)
          try {
            await register(values)
            navigate('/dashboard')
          } catch (error) {
            message.error(error instanceof Error ? error.message : 'Registration failed')
          } finally {
            setSubmitting(false)
          }
        }}
      >
        <Form.Item
          label="Name"
          name="name"
          rules={[{ required: true, message: 'Enter your name' }]}
        >
          <Input autoComplete="name" />
        </Form.Item>
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
          rules={[
            { required: true, message: 'Enter a password' },
            { min: 8, message: 'Use at least 8 characters' },
          ]}
        >
          <Input.Password autoComplete="new-password" />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" block loading={submitting}>
            Register
          </Button>
        </Form.Item>
      </Form>
      <Typography.Paragraph>
        Already registered? <Link to="/login">Log in</Link>
      </Typography.Paragraph>
    </Card>
  )
}
