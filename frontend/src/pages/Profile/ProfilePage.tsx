import { useEffect, useState } from 'react'
import { CameraOutlined } from '@ant-design/icons'
import { App, Avatar, Button, Card, Col, Divider, Form, Row, Space, Statistic, Typography } from 'antd'

import { useNavigate } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'
import { AuthService } from '../../services/AuthService/AuthService'
import { UserService } from '../../services/UserService/UserService'
import { profileToFormValues, toProfilePatch, type ProfileFormValues } from '../../types/user'
import { ProfileFormFields } from './ProfileFormFields'
import './profile.css'

export function ProfilePage() {
  const { user, profile, refreshProfile, logout } = useAuth()
  const navigate = useNavigate()
  const { message } = App.useApp()
  const [form] = Form.useForm<ProfileFormValues>()
  const [editing, setEditing] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!profile) {
      return
    }
    form.setFieldsValue(profileToFormValues(profile))
  }, [form, profile])

  function cancelEdit() {
    setEditing(false)
    if (profile) {
      form.setFieldsValue(profileToFormValues(profile))
    }
  }

  return (
    <Card>
      <Form
        form={form}
        layout="vertical"
        onFinish={async (values) => {
          setSubmitting(true)
          try {
            const nextName = values.name?.trim()
            if (nextName && nextName !== user?.name) {
              await AuthService.updateMe({ name: nextName })
            }
            await UserService.updateMe(toProfilePatch(values))
            await refreshProfile()
            setEditing(false)
            message.success('Profile saved')
          } catch (error) {
            message.error(error instanceof Error ? error.message : 'Could not save profile')
          } finally {
            setSubmitting(false)
          }
        }}
      >
        <div className="profile-hero">
          <div className="profile-avatar-wrap">
            <Avatar size={88} src="/profile-placeholder.svg" />
            <button
              type="button"
              className="profile-avatar-edit"
              disabled
              aria-label="Change profile photo (coming soon)"
              title="Photo editing coming soon"
            >
              <CameraOutlined />
            </button>
          </div>
          <Typography.Text type="secondary" className="profile-hero-email">
            {profile?.email ?? user?.email}
          </Typography.Text>
        </div>
        <Divider className="profile-divider" />
        <div className="profile-header-actions">
          {editing ? (
            <Space>
              <Button type="primary" htmlType="submit" loading={submitting}>
                Save
              </Button>
              <Button onClick={cancelEdit} disabled={submitting} htmlType="button">
                Cancel
              </Button>
            </Space>
          ) : (
            <Button type="primary" htmlType="button" onClick={() => setEditing(true)}>
              Edit Profile
            </Button>
          )}
        </div>
        <ProfileFormFields
          storedWeightUnit={profile?.weight?.unit ?? 'kg'}
          disabled={!editing}
          showName
        />
        <Typography.Text strong>Daily requirements</Typography.Text>
        <Row gutter={[16, 16]} style={{ marginTop: 12, marginBottom: 16 }}>
          <Col xs={12} sm={6}>
            <Statistic title="Calories" suffix="kcal" value={profile?.target_calories ?? '—'} />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic title="Protein" suffix="g" value={profile?.target_protein ?? '—'} />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic title="Carbs" suffix="g" value={profile?.target_carb ?? '—'} />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic title="Fat" suffix="g" value={profile?.target_fat ?? '—'} />
          </Col>
        </Row>
      </Form>
      <Button
        danger
        htmlType="button"
        className="profile-logout"
        onClick={() => {
          logout()
          navigate('/login')
        }}
      >
        Logout
      </Button>
    </Card>
  )
}
