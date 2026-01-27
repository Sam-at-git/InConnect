/**
 * Enhanced Dashboard with Trends and Alerts
 */

import { useEffect, useState } from 'react'
import {
  Card,
  Row,
  Col,
  Statistic,
  Select,
  DatePicker,
  Space,
  Typography,
  Alert,
  List,
  Tag,
  Button,
  Modal,
  Form,
  InputNumber,
  Switch,
} from 'antd'
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  BellOutlined,
  SettingOutlined,
  PlusOutlined,
} from '@ant-design/icons'
import { Line, Column } from '@ant-design/plots'
import dayjs from 'dayjs'
import { useReportStore } from '../stores/report'
import { reportsApi, TimeRangeType } from '../api/reports'

const { Title } = Typography
const { Option } = Select

interface AlertConfig {
  id: string
  name: string
  metric: string
  threshold: number
  condition: 'above' | 'below'
  is_enabled: boolean
}

export default function EnhancedDashboard() {
  const {
    dashboard,
    ticketReport,
    messageReport,
    fetchDashboard,
    fetchTicketReport,
    fetchMessageReport,
    ticketTimeRange,
    messageTimeRange,
    setTicketTimeRange,
    setMessageTimeRange,
  } = useReportStore()

  const [trendData, setTrendData] = useState<any[]>([])
  const [alerts, setAlerts] = useState<AlertConfig[]>([])
  const [alertModalVisible, setAlertModalVisible] = useState(false)
  const [loadingTrends, setLoadingTrends] = useState(false)

  useEffect(() => {
    fetchDashboard()
    loadTrends()
    loadAlerts()
  }, [])

  const loadTrends = async () => {
    setLoadingTrends(true)
    try {
      // Mock trend data - in real implementation, fetch from API
      const today = dayjs()
      const data = []
      for (let i = 6; i >= 0; i--) {
        const date = today.subtract(i, 'day')
        data.push({
          date: date.format('MM-DD'),
          tickets: Math.floor(Math.random() * 50) + 20,
          messages: Math.floor(Math.random() * 200) + 100,
          resolved: Math.floor(Math.random() * 40) + 15,
        })
      }
      setTrendData(data)
    } catch (error) {
      console.error('Failed to load trends:', error)
    } finally {
      setLoadingTrends(false)
    }
  }

  const loadAlerts = () => {
    // Mock alerts
    setAlerts([
      {
        id: '1',
        name: '待处理工单告警',
        metric: 'pending_tickets',
        threshold: 50,
        condition: 'above',
        is_enabled: true,
      },
      {
        id: '2',
        name: '超时工单告警',
        metric: 'overdue_tickets',
        threshold: 10,
        condition: 'above',
        is_enabled: true,
      },
      {
        id: '3',
        name: '可用员工告警',
        metric: 'available_staff',
        threshold: 3,
        condition: 'below',
        is_enabled: true,
      },
    ])
  }

  const handleRefresh = () => {
    fetchDashboard(ticketTimeRange as TimeRangeType)
    fetchTicketReport(ticketTimeRange as TimeRangeType)
    fetchMessageReport(messageTimeRange as TimeRangeType)
    loadTrends()
  }

  const activeAlerts = alerts.filter((a) => a.is_enabled)

  // Check for triggered alerts
  const triggeredAlerts = activeAlerts.filter((alert) => {
    const value = (dashboard as any)?.[alert.metric] || 0
    if (alert.condition === 'above') {
      return value > alert.threshold
    } else {
      return value < alert.threshold
    }
  })

  const trendChartData = trendData.map((d) => ({
    date: d.date,
    value: d.tickets,
    category: '新增工单',
  }))

  trendChartData.push(
    ...trendData.map((d) => ({
      date: d.date,
      value: d.resolved,
      category: '已解决',
    }))
  )

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={18}>
          <Space>
            <Select
              value={ticketTimeRange}
              onChange={(v) => {
                setTicketTimeRange(v)
                fetchDashboard(v)
              }}
              style={{ width: 120 }}
            >
              <Option value="today">今日</Option>
              <Option value="this_week">本周</Option>
              <Option value="this_month">本月</Option>
            </Select>
            <Button onClick={handleRefresh}>刷新</Button>
          </Space>
        </Col>
        <Col span={6} style={{ textAlign: 'right' }}>
          <Button icon={<SettingOutlined />} onClick={() => setAlertModalVisible(true)}>
            告警设置
          </Button>
        </Col>
      </Row>

      {/* Triggered Alerts */}
      {triggeredAlerts.length > 0 && (
        <Alert
          message="告警提醒"
          description={
            <List
              size="small"
              dataSource={triggeredAlerts}
              renderItem={(alert) => (
                <List.Item>
                  <Tag color="red">{alert.name}</Tag>
                  当前值 {(dashboard as any)?.[alert.metric] || 0}
                  {alert.condition === 'above' ? '>' : '<'} 阈值 {alert.threshold}
                </List.Item>
              )}
            />
          }
          type="error"
          showIcon
          closable
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Key Metrics */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总工单"
              value={dashboard?.total_tickets || 0}
              prefix={<BellOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待处理"
              value={dashboard?.pending_tickets || 0}
              prefix={<ArrowDownOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="处理中"
              value={dashboard?.in_progress_tickets || 0}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="超时工单"
              value={dashboard?.overdue_tickets || 0}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Trend Charts */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={24}>
          <Card title="工单趋势（最近7天）" loading={loadingTrends}>
            <Line
              data={trendChartData}
              xField="date"
              yField="value"
              seriesField="category"
              smooth={true}
              height={250}
              color={['#1890ff', '#52c41a']}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="工单分类统计">
            <Column
              data={
                ticketReport?.by_category.map((c: any) => ({
                  type: c.category,
                  value: c.count,
                })) || []
              }
              xField="type"
              yField="value"
              height={250}
              color="#1890ff"
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="消息统计">
            <Column
              data={
                messageReport?.by_type.map((m: any) => ({
                  type: m.message_type,
                  value: m.count,
                })) || []
              }
              xField="type"
              yField="value"
              height={250}
              color="#52c41a"
            />
          </Card>
        </Col>
      </Row>

      {/* Alert Configuration Modal */}
      <Modal
        title="告警配置"
        open={alertModalVisible}
        onCancel={() => setAlertModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setAlertModalVisible(false)}>
            关闭
          </Button>,
          <Button key="add" type="primary" icon={<PlusOutlined />}>
            新增告警
          </Button>,
        ]}
      >
        <List
          dataSource={alerts}
          renderItem={(alert) => (
            <List.Item
              actions={[
                <Switch
                  checked={alert.is_enabled}
                  size="small"
                  onChange={(checked) => {
                    setAlerts(
                      alerts.map((a) =>
                        a.id === alert.id ? { ...a, is_enabled: checked } : a
                      )
                    )
                  }}
                />,
              ]}
            >
              <List.Item.Meta
                title={alert.name}
                description={
                  <span>
                    当{' '}
                    <Tag>{alert.metric}</Tag>
                    {alert.condition === 'above' ? '>' : '<'}
                    <Tag color="blue">{alert.threshold}</Tag>
                    时触发
                  </span>
                }
              />
            </List.Item>
          )}
        />
      </Modal>
    </div>
  )
}
