import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Layout, Typography, ConfigProvider, theme, Menu } from 'antd'
import { useLocation } from 'react-router-dom'
import {
  HomeOutlined,
  MessageOutlined,
  CheckSquareOutlined,
  BarChartOutlined,
  SettingOutlined,
  ControlOutlined,
} from '@ant-design/icons'
import { useState, useEffect } from 'react'
import LoginPage from './pages/Login'
import TicketListPage from './pages/TicketList'
import TicketDetailPage from './pages/TicketDetail'
import StaffDashboardPage from './pages/StaffDashboard'
import ConversationListPage from './pages/ConversationList'
import MessageChatPage from './pages/MessageChat'
import MessageHistoryPage from './pages/MessageHistory'
import ReportsPage from './pages/Reports'
import SettingsPage from './pages/Settings'
import RuleManagementPage from './pages/RuleManagement'
import { useAuthStore } from './stores/auth'

const { Header, Content, Sider } = Layout
const { Title } = Typography

function App() {
  const location = useLocation()
  const isAuthenticated = !!localStorage.getItem('access_token')
  const clearAuth = useAuthStore((state) => state.clearAuth)
  const [collapsed, setCollapsed] = useState(false)

  const menuItems = [
    { key: '/', icon: <HomeOutlined />, label: '工作台' },
    { key: '/tickets', icon: <CheckSquareOutlined />, label: '工单管理' },
    { key: '/messages', icon: <MessageOutlined />, label: '消息管理' },
    { key: '/reports', icon: <BarChartOutlined />, label: '数据报表' },
    { key: '/rules', icon: <ControlOutlined />, label: '规则管理' },
    { key: '/settings', icon: <SettingOutlined />, label: '系统设置' },
  ]

  const handleLogout = () => {
    clearAuth()
  }

  // Don't show layout for login page
  if (location.pathname === '/login') {
    return (
      <ConfigProvider
        theme={{
          algorithm: theme.defaultAlgorithm,
          token: { colorPrimary: '#1890ff' },
        }}
      >
        <LoginPage />
      </ConfigProvider>
    )
  }

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <BrowserRouter>
        <Layout style={{ minHeight: '100vh' }}>
          <Header style={{
            background: '#001529',
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}>
            <Title level={3} style={{ color: '#fff', margin: 0 }}>
              迎客通 InConnect
            </Title>
            {isAuthenticated && (
              <a onClick={handleLogout} style={{ color: '#fff', cursor: 'pointer' }}>
                退出登录
              </a>
            )}
          </Header>
          <Layout>
            <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed} width={200}>
              <Menu
                theme="dark"
                mode="inline"
                selectedKeys={[location.pathname]}
                items={menuItems}
                onClick={({ key }) => {
                  if (key !== location.pathname) {
                    window.location.href = key
                  }
                }}
              />
            </Sider>
            <Content style={{ padding: '24px' }}>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route
                  path="/"
                  element={
                    isAuthenticated ? <StaffDashboardPage /> : <Navigate to="/login" replace />
                  }
                />
                <Route
                  path="/tickets"
                  element={
                    isAuthenticated ? <TicketListPage /> : <Navigate to="/login" replace />
                  }
                />
                <Route
                  path="/tickets/:id"
                  element={
                    isAuthenticated ? <TicketDetailPage /> : <Navigate to="/login" replace />
                  }
                />
                <Route
                  path="/messages"
                  element={
                    isAuthenticated ? <ConversationListPage /> : <Navigate to="/login" replace />
                  }
                />
                <Route
                  path="/messages/:id"
                  element={
                    isAuthenticated ? <MessageChatPage /> : <Navigate to="/login" replace />
                  }
                />
                <Route
                  path="/messages/history"
                  element={
                    isAuthenticated ? <MessageHistoryPage /> : <Navigate to="/login" replace />
                  }
                />
                <Route
                  path="/reports"
                  element={
                    isAuthenticated ? <ReportsPage /> : <Navigate to="/login" replace />
                  }
                />
                <Route
                  path="/settings"
                  element={
                    isAuthenticated ? <SettingsPage /> : <Navigate to="/login" replace />
                  }
                />
                <Route
                  path="/rules"
                  element={
                    isAuthenticated ? <RuleManagementPage /> : <Navigate to="/login" replace />
                  }
                />
                <Route
                  path="*"
                  element={<Navigate to="/" replace />}
                />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </BrowserRouter>
    </ConfigProvider>
  )
}

export default App
