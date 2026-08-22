import { useEffect, useState } from 'react'
import {
  App,
  Button,
  Card,
  Col,
  Descriptions,
  Form,
  Row,
  Space,
  Statistic,
  Typography,
} from 'antd'

import { useAuth } from '../../hooks/useAuth'
import { UserService } from '../../services/UserService/UserService'
import {
  ACTIVITY_OPTIONS,
  ALLERGY_OPTIONS,
  GENDER_OPTIONS,
  VEGAN_OPTIONS,
  optionLabel,
  profileToFormValues,
  type UpdateProfileRequest,
} from '../../types/user'
import { formatHeight, formatWeight } from '../../utils/profileUnits'
import { ProfileFormFields } from './ProfileFormFields'

export function ProfilePage() {
  const { user, profile, refreshProfile } = useAuth()
  const { message } = App.useApp()
  const [form] = Form.useForm<UpdateProfileRequest>()
  const [editing, setEditing] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!profile) {
      return
    }
    form.setFieldsValue(profileToFormValues(profile))
  }, [form, profile])

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Card>
        <Typography.Title level={3} style={{ marginTop: 0 }}>
          My Profile
        </Typography.Title>
        <Row gutter={[24, 24]}>
          <Col xs={24} md={12} lg={8}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Name">{user?.name ?? '—'}</Descriptions.Item>
              <Descriptions.Item label="Weight">{formatWeight(profile?.weight)}</Descriptions.Item>
              <Descriptions.Item label="Height">{formatHeight(profile?.height)}</Descriptions.Item>
              <Descriptions.Item label="Age">{profile?.age ?? '—'}</Descriptions.Item>
              <Descriptions.Item label="Gender">
                {optionLabel(GENDER_OPTIONS, profile?.gender)}
              </Descriptions.Item>
              <Descriptions.Item label="Current status">{profile?.status ?? '—'}</Descriptions.Item>
            </Descriptions>
          </Col>
          <Col xs={24} md={12} lg={8}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Vegan">
                {optionLabel(VEGAN_OPTIONS, profile?.vegan)}
              </Descriptions.Item>
              <Descriptions.Item label="Allergy">
                {optionLabel(ALLERGY_OPTIONS, profile?.allergy)}
              </Descriptions.Item>
              <Descriptions.Item label="Activity">
                {optionLabel(ACTIVITY_OPTIONS, profile?.activity_level)}
              </Descriptions.Item>
            </Descriptions>
          </Col>
          <Col xs={24} lg={8}>
            <Typography.Text strong>Daily requirements</Typography.Text>
            <Row gutter={[16, 16]} style={{ marginTop: 12 }}>
              <Col span={12}>
                <Statistic title="Calories" suffix="kcal" value={profile?.target_calories ?? '—'} />
              </Col>
              <Col span={12}>
                <Statistic title="Protein" suffix="g" value={profile?.target_protein ?? '—'} />
              </Col>
              <Col span={12}>
                <Statistic title="Carbs" suffix="g" value={profile?.target_carb ?? '—'} />
              </Col>
              <Col span={12}>
                <Statistic title="Fat" suffix="g" value={profile?.target_fat ?? '—'} />
              </Col>
            </Row>
          </Col>
        </Row>
        {!editing ? (
          <Button type="primary" style={{ marginTop: 16 }} onClick={() => setEditing(true)}>
            Edit Profile
          </Button>
        ) : null}
      </Card>
      {editing ? (
        <Card title="Edit profile">
          <Form
            form={form}
            layout="vertical"
            onFinish={async (values) => {
              setSubmitting(true)
              try {
                await UserService.updateMe(values)
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
            <ProfileFormFields storedWeightUnit={profile?.weight?.unit ?? 'kg'} />
            <Form.Item>
              <Space>
                <Button type="primary" htmlType="submit" loading={submitting}>
                  Save Profile
                </Button>
                <Button
                  onClick={() => {
                    setEditing(false)
                    if (profile) {
                      form.setFieldsValue(profileToFormValues(profile))
                    }
                  }}
                >
                  Cancel
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>
      ) : null}
    </Space>
  )
}
