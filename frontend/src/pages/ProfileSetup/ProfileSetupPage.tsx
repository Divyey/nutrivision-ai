import { useState } from 'react'
import { App, Button, Card, Form, Typography } from 'antd'
import { useNavigate } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'
import { UserService } from '../../services/UserService/UserService'
import type { UpdateProfileRequest } from '../../types/user'
import { ProfileFormFields } from '../Profile/ProfileFormFields'

export function ProfileSetupPage() {
  const { refreshProfile } = useAuth()
  const navigate = useNavigate()
  const { message } = App.useApp()
  const [form] = Form.useForm<UpdateProfileRequest>()
  const [submitting, setSubmitting] = useState(false)

  return (
    <Card title="Profile setup" className="setup-card">
      <Typography.Paragraph type="secondary">
        Tell us a bit about you so we can calculate calorie and macro goals.
      </Typography.Paragraph>
      <Form
        form={form}
        layout="vertical"
        initialValues={{ weight: { unit: 'kg' }, vegan: 'no', allergy: 'none' }}
        onFinish={async (values) => {
          setSubmitting(true)
          try {
            await UserService.updateMe(values)
            await refreshProfile()
            navigate('/dashboard')
          } catch (error) {
            message.error(error instanceof Error ? error.message : 'Could not save profile')
          } finally {
            setSubmitting(false)
          }
        }}
      >
        <ProfileFormFields />
        <Form.Item>
          <Button type="primary" htmlType="submit" block loading={submitting}>
            Save and continue
          </Button>
        </Form.Item>
      </Form>
    </Card>
  )
}
