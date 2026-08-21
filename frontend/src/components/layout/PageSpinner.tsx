import { Flex, Spin } from 'antd'

export function PageSpinner() {
  return (
    <Flex justify="center" style={{ padding: 48 }}>
      <Spin size="large" />
    </Flex>
  )
}
