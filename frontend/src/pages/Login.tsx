/**
 * Login Page
 */

import { useState } from 'react'
import { Form, Input, Button, Card, message } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { authApi, LoginResponse } from '../api/auth'
import { useAuthStore } from '../stores/auth'

interface LoginForm {
  wechat_userid: string
  password: string
}

export default function LoginPage() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const setAuth = useAuthStore((state) => state.setAuth)

  const onFinish = async (values: LoginForm) => {
    setLoading(true)
    try {
      const response = await authApi.login(values)
      if (response.code === 0 && response.data) {
        const data = response.data as LoginResponse
        setAuth(
          data.access_token,
          {
            id: data.staff_id,
            name: data.staff_name,
            hotelId: data.hotel_id,
            role: data.role,
          }
        )
        message.success('登录成功')
        navigate('/')
      } else {
        message.error(response.message || '登录失败')
      }
    } catch (error: unknown) {
      const err = error as { message?: string }
      message.error(err.message || '登录失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    }}>
      <Card
        title="迎客通 InConnect"
        style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.15)' }}
      >
        <Form
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="wechat_userid"
            rules={[{ required: true, message: '请输入企业微信ID' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="企业微信ID"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}>
              登录
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center', color: '#999', fontSize: '12px' }}>
          <p>客人消息智能路由与工单管理系统</p>
        </div>
      </Card>
    </div>
  )
}
