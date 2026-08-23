import { useEffect, useRef } from 'react'
import { Col, Form, Input, InputNumber, Row, Select, Space } from 'antd'

import {
  ACTIVITY_OPTIONS,
  ALLERGY_OPTIONS,
  GENDER_OPTIONS,
  VEGAN_OPTIONS,
  WEIGHT_UNIT_OPTIONS,
  type ProfileFormValues,
  type WeightUnit,
} from '../../types/user'
import { convertWeight } from '../../utils/profileUnits'

const compactStyle = { width: '100%' }
const MEAL_FILTER_HINT =
  'Saved for meal recommendations later. It does not change calorie or macro math.'

type ProfileFormFieldsProps = {
  storedWeightUnit?: WeightUnit
  disabled?: boolean
  showName?: boolean
}

export function ProfileFormFields({
  storedWeightUnit = 'kg',
  disabled = false,
  showName = false,
}: ProfileFormFieldsProps) {
  const form = Form.useFormInstance<ProfileFormValues>()
  const weightUnitRef = useRef<WeightUnit>(storedWeightUnit)

  useEffect(() => {
    weightUnitRef.current = storedWeightUnit
  }, [storedWeightUnit])

  return (
    <Row gutter={16}>
      {showName ? (
        <Col xs={24} sm={12}>
          <Form.Item
            label="Name"
            name="name"
            rules={[{ required: true, message: 'Enter your name' }]}
          >
            <Input disabled={disabled} maxLength={100} autoComplete="name" />
          </Form.Item>
        </Col>
      ) : null}
      <Col xs={24} sm={12}>
        <Form.Item label="Age" name="age" rules={[{ required: true, message: 'Enter your age' }]}>
          <InputNumber min={10} max={120} style={compactStyle} disabled={disabled} />
        </Form.Item>
      </Col>
      <Col xs={24} sm={12}>
        <Form.Item
          label="Gender"
          name="gender"
          extra={
            disabled
              ? undefined
              : 'Mifflin–St Jeor is sex-specific. Not specified uses the midpoint of male and female, so the calorie goal is an estimate.'
          }
          rules={[{ required: true, message: 'Select gender' }]}
        >
          <Select options={GENDER_OPTIONS} disabled={disabled} />
        </Form.Item>
      </Col>
      <Col xs={24} sm={12}>
        <Form.Item label="Weight" required>
          <Space.Compact block>
            <Form.Item
              name={['weight', 'value']}
              noStyle
              rules={[{ required: true, message: 'Enter your weight' }]}
            >
              <InputNumber min={1} max={600} step={0.1} style={compactStyle} disabled={disabled} />
            </Form.Item>
            <Form.Item name={['weight', 'unit']} noStyle initialValue="kg">
              <Select
                options={WEIGHT_UNIT_OPTIONS}
                style={{ width: 90 }}
                disabled={disabled}
                onChange={(next: WeightUnit) => {
                  const current = form.getFieldValue(['weight', 'value'])
                  const from = weightUnitRef.current
                  if (typeof current === 'number' && from !== next) {
                    form.setFieldValue(['weight', 'value'], convertWeight(current, from, next))
                  }
                  weightUnitRef.current = next
                }}
              />
            </Form.Item>
          </Space.Compact>
        </Form.Item>
      </Col>
      <Col xs={24} sm={12}>
        <Form.Item label="Height" required>
          <Space.Compact block>
            <Form.Item
              name={['height', 'feet']}
              noStyle
              rules={[{ required: true, message: 'Enter feet' }]}
            >
              <InputNumber min={3} max={8} placeholder="feet" style={compactStyle} disabled={disabled} />
            </Form.Item>
            <Form.Item
              name={['height', 'inches']}
              noStyle
              rules={[{ required: true, message: 'Enter inches' }]}
            >
              <InputNumber
                min={0}
                max={11}
                placeholder="inches"
                style={compactStyle}
                disabled={disabled}
              />
            </Form.Item>
          </Space.Compact>
        </Form.Item>
      </Col>
      <Col xs={24} sm={12}>
        <Form.Item
          label="Activity level"
          name="activity_level"
          rules={[{ required: true, message: 'Select activity level' }]}
        >
          <Select options={ACTIVITY_OPTIONS} disabled={disabled} />
        </Form.Item>
      </Col>
      <Col xs={24} sm={12}>
        <Form.Item
          label="Vegan"
          name="vegan"
          extra={disabled ? undefined : MEAL_FILTER_HINT}
          rules={[{ required: true, message: 'Select yes or no' }]}
        >
          <Select options={VEGAN_OPTIONS} disabled={disabled} />
        </Form.Item>
      </Col>
      <Col xs={24} sm={12}>
        <Form.Item
          label="Allergy"
          name="allergy"
          extra={disabled ? undefined : MEAL_FILTER_HINT}
          rules={[{ required: true, message: 'Select an allergy option' }]}
        >
          <Select options={ALLERGY_OPTIONS} disabled={disabled} />
        </Form.Item>
      </Col>
    </Row>
  )
}
