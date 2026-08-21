import { App as AntdApp, ConfigProvider, theme } from 'antd'
import { BrowserRouter } from 'react-router-dom'

import { AppRoutes } from './AppRoutes/AppRoutes'
import { AuthProvider } from './hooks/AuthProvider'

export function App() {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1677ff',
          borderRadius: 8,
        },
      }}
    >
      <AntdApp>
        <AuthProvider>
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
        </AuthProvider>
      </AntdApp>
    </ConfigProvider>
  )
}
