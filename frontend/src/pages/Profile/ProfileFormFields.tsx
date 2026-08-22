import { useEffect, useRef } from 'react'
import { Col, Form, InputNumber, Row, Select, Space } from 'antd'

import {
  ACTIVITY_OPTIONS,
  ALLERGY_OPTIONS,
  GENDER_OPTIONS,
  VEGAN_OPTIONS,
  WEIGHT_UNIT_OPTIONS,
  type UpdateProfileRequest,
  type WeightUnit,
} from '../../types/user'
import { convertWeight } from '../../utils/profileUnits'

const compactStyle = { width: '100%' }
const MEAL_FILTER_HINT =
  'Saved for meal recommendations later. It does not change calorie or macro math.'

type ProfileFormFieldsProps = {
  storedWeightUnit?: WeightUnit
}

export function ProfileFormFields({ storedWeightUnit = 'kg' }: ProfileFormFieldsProps) {
  const form = Form.useFormInstance<UpdateProfileRequest>()
  const weightUnitRef = useRef<WeightUnit>(storedWeightUnit)

  useEffect(() => {
    weightUnitRef.current = storedWeightUnit
  }, [storedWeightUnit])

  return (
    <Row gutter={16}>
      <Col xs={24} sm={12}>
        <Form.Item label="Age" name="age" rules={[{ required: true, message: 'Enter your age' }]}>
          <InputNumber min={10} max={120} style={compactStyle} />
        </Form.Item>
      </Col>
      <Col xs={24} sm={12}>
        <Form.Item
          label="Gender"
          name="gender"
          extra="Mifflin–St Jeor is sex-specific. Not specified uses the midpoint of male and female, so the calorie goal is an estimate."
          rules={[{ required: true, message: 'Select gender' }]}
        >
          <Select options={GENDER_OPTIONS} />
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
              <InputNumber min={1} max={600} step={0.1} style={compactStyle} />
            </Form.Item>
            <Form.Item name={['weight', 'unit']} noStyle initialValue="kg">
              <Select
                options={WEIGHT_UNIT_OPTIONS}
                style={{ width: 90 }}
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
              <InputNumber min={3} max={8} placeholder="feet" style={compactStyle} />
            </Form.Item>
            <Form.Item
              name={['height', 'inches']}
              noStyle
              rules={[{ required: true, message: 'Enter inches' }]}
            >
              <InputNumber min={0} max={11} placeholder="inches" style={compactStyle} />
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
          <Select options={ACTIVITY_OPTIONS} />
        </Form.Item>
      </Col>
      <Col xs={24} sm={12}>
        <Form.Item
          label="Vegan"
          name="vegan"
          extra={MEAL_FILTER_HINT}
          rules={[{ required: true, message: 'Select yes or no' }]}
        >
          <Select options={VEGAN_OPTIONS} />
        </Form.Item>
      </Col>
      <Col xs={24} sm={12}>
        <Form.Item
          label="Allergy"
          name="allergy"
          extra={MEAL_FILTER_HINT}
          rules={[{ required: true, message: 'Select an allergy option' }]}
        >
          <Select options={ALLERGY_OPTIONS} />
        </Form.Item>
      </Col>
    </Row>
  )
}
