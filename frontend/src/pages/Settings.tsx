/**
 * System Settings Page
 */

import { useEffect, useState } from 'react'
import {
  Card,
  Tabs,
  Form,
  Input,
  InputNumber,
  Switch,
  Button,
  Space,
  Typography,
  message,
  Row,
  Col,
  Statistic,
  Tag,
  ColorPicker,
} from 'antd'
import {
  SaveOutlined,
  ReloadOutlined,
  SettingOutlined,
  TagOutlined,
  ThunderboltOutlined,
  InfoCircleOutlined,
  SafetyOutlined,
} from '@ant-design/icons'
import type { ColorValue } from 'antd/es/color-picker'
import { settingsApi, TicketCategoryConfig, PriorityConfig } from '../api/settings'
import PermissionMatrixPage from './PermissionMatrix'

const { Title, Text } = Typography

// Ticket Categories Tab
function CategoriesTab() {
  const [categories, setCategories] = useState<TicketCategoryConfig[]>([])
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    setLoading(true)
    try {
      const response = await settingsApi.getCategories()
      setCategories(response.data || [])
      form.setFieldsValue({ categories: response.data || [] })
    } catch (error) {
      message.error('加载工单分类失败')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      await settingsApi.updateCategories(values.categories)
      message.success('保存成功')
      loadCategories()
    } catch (error) {
      message.error('保存失败')
    }
  }

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Text type="secondary">配置工单分类及其SLA时间</Text>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadCategories}>
            刷新
          </Button>
          <Button type="primary" icon={<SaveOutlined />} onClick={handleSave}>
            保存配置
          </Button>
        </Space>
      </Space>

      <Form form={form} initialValues={{ categories }}>
        <Form.List name="categories">
          {(fields) => (
            <>
              {fields.map((field, index) => (
                <Card key={field.key} size="small" style={{ marginBottom: 8 }}>
                  <Row gutter={16} align="middle">
                    <Col span={6}>
                      <Form.Item
                        {...field}
                        name={[field.name, 'key']}
                        label="Key"
                        rules={[{ required: true }]}
                      >
                        <Input disabled />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item
                        {...field}
                        name={[field.name, 'label']}
                        label="名称"
                        rules={[{ required: true }]}
                      >
                        <Input />
                      </Form.Item>
                    </Col>
                    <Col span={4}>
                      <Form.Item
                        {...field}
                        name={[field.name, 'sla_hours']}
                        label="SLA(小时)"
                      >
                        <InputNumber min={0} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={4}>
                      <Form.Item
                        {...field}
                        name={[field.name, 'is_enabled']}
                        label="启用"
                        valuePropName="checked"
                      >
                        <Switch />
                      </Form.Item>
                    </Col>
                    <Col span={4}>
                      <Form.Item
                        {...field}
                        name={[field.name, 'color']}
                        label="颜色"
                      >
                        <Input />
                      </Form.Item>
                    </Col>
                  </Row>
                </Card>
              ))}
            </>
          )}
        </Form.List>
      </Form>
    </div>
  )
}

// Priorities Tab
function PrioritiesTab() {
  const [priorities, setPriorities] = useState<PriorityConfig[]>([])
  const [loading, setLoading] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    loadPriorities()
  }, [])

  const loadPriorities = async () => {
    setLoading(true)
    try {
      const response = await settingsApi.getPriorities()
      setPriorities(response.data || [])
      form.setFieldsValue({ priorities: response.data || [] })
    } catch (error) {
      message.error('加载优先级配置失败')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      await settingsApi.updatePriorities(values.priorities)
      message.success('保存成功')
      loadPriorities()
    } catch (error) {
      message.error('保存失败')
    }
  }

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Text type="secondary">配置优先级及其响应时间要求</Text>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadPriorities}>
            刷新
          </Button>
          <Button type="primary" icon={<SaveOutlined />} onClick={handleSave}>
            保存配置
          </Button>
        </Space>
      </Space>

      <Form form={form} initialValues={{ priorities }}>
        <Form.List name="priorities">
          {(fields) => (
            <>
              {fields.map((field) => (
                <Card key={field.key} size="small" style={{ marginBottom: 8 }}>
                  <Row gutter={16} align="middle">
                    <Col span={6}>
                      <Form.Item
                        {...field}
                        name={[field.name, 'key']}
                        label="Key"
                        rules={[{ required: true }]}
                      >
                        <Input disabled />
                      </Form.Item>
                    </Col>
                    <Col span={6}>
                      <Form.Item
                        {...field}
                        name={[field.name, 'label']}
                        label="名称"
                        rules={[{ required: true }]}
                      >
                        <Input />
                      </Form.Item>
                    </Col>
                    <Col span={4}>
                      <Form.Item
                        {...field}
                        name={[field.name, 'urgency_hours']}
                        label="响应(小时)"
                      >
                        <InputNumber min={0} style={{ width: '100%' }} />
                      </Form.Item>
                    </Col>
                    <Col span={4}>
                      <Form.Item
                        {...field}
                        name={[field.name, 'is_enabled']}
                        label="启用"
                        valuePropName="checked"
                      >
                        <Switch />
                      </Form.Item>
                    </Col>
                    <Col span={4}>
                      <Form.Item
                        {...field}
                        name={[field.name, 'color']}
                        label="颜色"
                      >
                        <Input />
                      </Form.Item>
                    </Col>
                  </Row>
                </Card>
              ))}
            </>
          )}
        </Form.List>
      </Form>
    </div>
  )
}

// System Info Tab
function SystemInfoTab() {
  const [info, setInfo] = useState<any>(null)

  useEffect(() => {
    loadInfo()
  }, [])

  const loadInfo = async () => {
    try {
      const response = await settingsApi.getSystemInfo()
      setInfo(response.data)
    } catch (error) {
      message.error('加载系统信息失败')
    }
  }

  if (!info) return null

  return (
    <div>
      <Card>
        <Row gutter={16}>
          <Col span={24}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Title level={4}>{info.name}</Title>
              <Text>版本: <Tag color="blue">{info.version}</Tag></Text>
            </Space>
          </Col>
        </Row>
      </Card>

      <Title level={5} style={{ marginTop: 24 }}>数据统计</Title>
      <Row gutter={16}>
        <Col span={6}>
          <Card>
            <Statistic title="工单数" value={info.stats.tickets} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="员工数" value={info.stats.staff} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="会话数" value={info.stats.conversations} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="消息数" value={info.stats.messages} />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

// Main Settings Page
export default function SettingsPage() {
  const tabItems = [
    {
      key: 'categories',
      label: (
        <span>
          <TagOutlined /> 工单分类
        </span>
      ),
      children: <CategoriesTab />,
    },
    {
      key: 'priorities',
      label: (
        <span>
          <ThunderboltOutlined /> 优先级
        </span>
      ),
      children: <PrioritiesTab />,
    },
    {
      key: 'permissions',
      label: (
        <span>
          <SafetyOutlined /> 权限矩阵
        </span>
      ),
      children: <PermissionMatrixPage />,
    },
    {
      key: 'info',
      label: (
        <span>
          <InfoCircleOutlined /> 系统信息
        </span>
      ),
      children: <SystemInfoTab />,
    },
  ]

  return (
    <Card>
      <Title level={4}>系统设置</Title>
      <Tabs items={tabItems} />
    </Card>
  )
}
