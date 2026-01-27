/**
 * Audit Logs Page
 */

import { useEffect, useState } from 'react'
import {
  Card,
  Table,
  Tag,
  Space,
  Select,
  DatePicker,
  Button,
  Typography,
  message,
  Statistic,
  Row,
  Col,
} from 'antd'
import {
  ReloadOutlined,
  DownloadOutlined,
  EyeOutlined,
  HistoryOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'

const { Title } = Typography
const { RangePicker } = DatePicker
const { Option } = Select

const actionColors: Record<string, string> = {
  ticket_create: 'green',
  ticket_update: 'blue',
  ticket_delete: 'red',
  ticket_assign: 'orange',
  ticket_status_change: 'cyan',
  message_send: 'green',
  message_view: 'default',
  staff_create: 'green',
  staff_update: 'blue',
  staff_delete: 'red',
  rule_create: 'green',
  rule_update: 'blue',
  rule_delete: 'red',
  settings_update: 'orange',
  login: 'green',
  logout: 'default',
  login_failed: 'red',
  data_export: 'purple',
}

const actionLabels: Record<string, string> = {
  ticket_create: '创建工单',
  ticket_update: '更新工单',
  ticket_delete: '删除工单',
  ticket_assign: '分配工单',
  ticket_status_change: '工单状态变更',
  message_send: '发送消息',
  message_view: '查看消息',
  staff_create: '创建员工',
  staff_update: '更新员工',
  staff_delete: '删除员工',
  rule_create: '创建规则',
  rule_update: '更新规则',
  rule_delete: '删除规则',
  settings_update: '更新设置',
  login: '登录',
  logout: '登出',
  login_failed: '登录失败',
  data_export: '导出数据',
}

const resourceLabels: Record<string, string> = {
  ticket: '工单',
  message: '消息',
  staff: '员工',
  rule: '规则',
  settings: '设置',
  auth: '认证',
}

interface AuditLog {
  id: string
  action: string
  resource_type: string
  resource_id: string | null
  staff_id: string | null
  staff_name: string
  ip_address: string | null
  created_at: string
}

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState<any>(null)
  const [actionFilter, setActionFilter] = useState<string | undefined>()
  const [resourceFilter, setResourceFilter] = useState<string | undefined>()
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null)

  useEffect(() => {
    loadLogs()
    loadSummary()
  }, [])

  const loadLogs = async () => {
    setLoading(true)
    try {
      const params: any = {
        hotel_id: 'default-hotel',
        limit: 100,
      }

      if (actionFilter) params.action = actionFilter
      if (resourceFilter) params.resource_type = resourceFilter
      if (dateRange) {
        params.start_date = dateRange[0].toISOString()
        params.end_date = dateRange[1].toISOString()
      }

      // Mock API call - in real implementation, use auditApi
      setLogs([])
    } catch (error) {
      message.error('加载审计日志失败')
    } finally {
      setLoading(false)
    }
  }

  const loadSummary = async () => {
    try {
      // Mock API call
      setSummary({
        period_days: 7,
        total_actions: 1250,
        by_action: [
          { action: 'ticket_create', count: 450 },
          { action: 'ticket_update', count: 320 },
          { action: 'message_send', count: 280 },
          { action: 'login', count: 120 },
          { action: 'data_export', count: 80 },
        ],
        by_resource: [
          { resource_type: 'ticket', count: 770 },
          { resource_type: 'message', count: 280 },
          { resource_type: 'staff', count: 120 },
          { resource_type: 'auth', count: 120 },
        ],
      })
    } catch (error) {
      console.error('Failed to load summary:', error)
    }
  }

  const handleExport = async () => {
    try {
      // Mock export
      message.success('导出成功')
    } catch (error) {
      message.error('导出失败')
    }
  }

  const columns: ColumnsType<AuditLog> = [
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      width: 120,
      render: (action: string) => (
        <Tag color={actionColors[action]}>{actionLabels[action] || action}</Tag>
      ),
    },
    {
      title: '资源类型',
      dataIndex: 'resource_type',
      key: 'resource_type',
      width: 100,
      render: (type: string) => resourceLabels[type] || type,
    },
    {
      title: '资源ID',
      dataIndex: 'resource_id',
      key: 'resource_id',
      width: 150,
      ellipsis: true,
    },
    {
      title: '操作人',
      dataIndex: 'staff_name',
      key: 'staff_name',
      width: 120,
    },
    {
      title: 'IP地址',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 150,
      render: (ip) => ip || '-',
    },
  ]

  return (
    <div>
      <Card>
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={6}>
            <Statistic
              title="本期操作"
              value={summary?.total_actions || 0}
              prefix={<HistoryOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="工单操作"
              value={
                summary?.by_action.find((a: any) => a.action.startsWith('ticket'))?.count || 0
              }
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="消息操作"
              value={
                summary?.by_action.find((a: any) => a.action.startsWith('message'))?.count || 0
              }
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="登录次数"
              value={
                summary?.by_action.find((a: any) => a.action === 'login')?.count || 0
              }
            />
          </Col>
        </Row>

        <Card size="small" style={{ marginBottom: 16, background: '#f5f5f5' }}>
          <Row gutter={16}>
            <Col span={6}>
              <label>操作类型：</label>
              <Select
                style={{ width: '100%' }}
                value={actionFilter}
                onChange={setActionFilter}
                allowClear
              >
                <Option value="ticket_create">创建工单</Option>
                <Option value="ticket_update">更新工单</Option>
                <Option value="ticket_assign">分配工单</Option>
                <Option value="message_send">发送消息</Option>
                <Option value="login">登录</Option>
                <Option value="data_export">导出数据</Option>
              </Select>
            </Col>
            <Col span={6}>
              <label>资源类型：</label>
              <Select
                style={{ width: '100%' }}
                value={resourceFilter}
                onChange={setResourceFilter}
                allowClear
              >
                <Option value="ticket">工单</Option>
                <Option value="message">消息</Option>
                <Option value="staff">员工</Option>
                <Option value="auth">认证</Option>
              </Select>
            </Col>
            <Col span={6}>
              <label>日期范围：</label>
              <RangePicker
                style={{ width: '100%' }}
                value={dateRange}
                onChange={setDateRange}
              />
            </Col>
            <Col span={6}>
              <label>&nbsp;</label>
              <Space style={{ width: '100%' }}>
                <Button icon={<ReloadOutlined />} onClick={loadLogs}>
                  查询
                </Button>
                <Button icon={<DownloadOutlined />} onClick={handleExport}>
                  导出
                </Button>
              </Space>
            </Col>
          </Row>
        </Card>

        <Table
          columns={columns}
          dataSource={logs}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 50,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>
    </div>
  )
}
