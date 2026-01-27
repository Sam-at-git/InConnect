/**
 * Reports Page - 综合报表页面
 */

import { useEffect, useState } from 'react'
import {
  Card,
  Tabs,
  Row,
  Col,
  Statistic,
  Select,
  Spin,
  Typography,
  Progress,
  Table,
  Tag,
  Space,
} from 'antd'
import {
  ReloadOutlined,
  FileTextOutlined,
  TeamOutlined,
  MessageOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { useReportStore } from '../stores/report'
import { reportsApi, TimeRangeType, StaffPerformanceStats } from '../api/reports'

const { Title } = Typography
const { Option } = Select

const timeRangeOptions = [
  { label: '今日', value: 'today' },
  { label: '昨日', value: 'yesterday' },
  { label: '本周', value: 'this_week' },
  { label: '上周', value: 'last_week' },
  { label: '本月', value: 'this_month' },
  { label: '上月', value: 'last_month' },
]

const statusMap: Record<string, string> = {
  pending: '待处理',
  assigned: '已分配',
  in_progress: '处理中',
  resolved: '已解决',
  closed: '已关闭',
  reopened: '已重开',
}

const categoryMap: Record<string, string> = {
  maintenance: '维修',
  housekeeping: '客房',
  service: '服务',
  complaint: '投诉',
  inquiry: '咨询',
  other: '其他',
}

// Dashboard Summary Tab
function DashboardTab() {
  const { dashboard, dashboardLoading, fetchDashboard } = useReportStore()
  const [timeRange, setTimeRange] = useState<TimeRangeType>('this_week')

  useEffect(() => {
    fetchDashboard(timeRange)
  }, [timeRange])

  const handleRefresh = () => {
    fetchDashboard(timeRange)
  }

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Select
          value={timeRange}
          onChange={setTimeRange}
          style={{ width: 120 }}
          options={timeRangeOptions}
        />
        <ReloadOutlined onClick={handleRefresh} style={{ cursor: 'pointer', fontSize: 16 }} />
      </Space>

      <Spin spinning={dashboardLoading}>
        <Row gutter={16}>
          <Col span={6}>
            <Card>
              <Statistic title="总工单数" value={dashboard?.total_tickets || 0} />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="待处理"
                value={dashboard?.pending_tickets || 0}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="处理中"
                value={dashboard?.in_progress_tickets || 0}
                valueStyle={{ color: '#1890ff' }}
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

        <Row gutter={16} style={{ marginTop: 16 }}>
          <Col span={6}>
            <Card>
              <Statistic title="总消息数" value={dashboard?.total_messages || 0} />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic title="未读消息" value={dashboard?.unread_messages || 0} />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic title="活跃会话" value={dashboard?.active_conversations || 0} />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic title="可用员工" value={dashboard?.available_staff || 0} />
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  )
}

// Ticket Report Tab
function TicketReportTab() {
  const {
    ticketReport,
    ticketReportLoading,
    ticketTimeRange,
    fetchTicketReport,
    setTicketTimeRange,
  } = useReportStore()

  useEffect(() => {
    fetchTicketReport()
  }, [])

  const handleTimeRangeChange = (value: TimeRangeType) => {
    setTicketTimeRange(value)
    fetchTicketReport(value)
  }

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Select
          value={ticketTimeRange}
          onChange={handleTimeRangeChange}
          style={{ width: 120 }}
          options={timeRangeOptions}
        />
      </Space>

      <Spin spinning={ticketReportLoading}>
        <Row gutter={16}>
          <Col span={8}>
            <Card title="工单状态分布">
              {ticketReport?.by_status.map((item) => (
                <div key={item.status} style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>{statusMap[item.status] || item.status}</span>
                    <span>{item.count} ({item.percentage}%)</span>
                  </div>
                  <Progress percent={item.percentage} size="small" />
                </div>
              ))}
            </Card>
          </Col>
          <Col span={8}>
            <Card title="工单优先级分布">
              {ticketReport?.by_priority.map((item) => (
                <div key={item.priority} style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Tag color={item.priority === 'P1' ? 'red' : item.priority === 'P2' ? 'orange' : 'blue'}>
                      {item.priority}
                    </Tag>
                    <span>{item.count} ({item.percentage}%)</span>
                  </div>
                  <Progress percent={item.percentage} size="small" />
                </div>
              ))}
            </Card>
          </Col>
          <Col span={8}>
            <Card title="工单分类分布">
              {ticketReport?.by_category.map((item) => (
                <div key={item.category} style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>{categoryMap[item.category] || item.category}</span>
                    <span>{item.count} ({item.percentage}%)</span>
                  </div>
                  <Progress percent={item.percentage} size="small" />
                </div>
              ))}
            </Card>
          </Col>
        </Row>

        <Row gutter={16} style={{ marginTop: 16 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="本期新增"
                value={ticketReport?.created_in_period || 0}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="本期已解决"
                value={ticketReport?.resolved_in_period || 0}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="本期已关闭"
                value={ticketReport?.closed_in_period || 0}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="平均解决时长"
                value={ticketReport?.avg_resolution_hours || 0}
                suffix="小时"
                precision={1}
              />
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  )
}

// Staff Report Tab
function StaffReportTab() {
  const {
    staffReport,
    staffReportLoading,
    staffTimeRange,
    fetchStaffReport,
    setStaffTimeRange,
  } = useReportStore()

  useEffect(() => {
    fetchStaffReport()
  }, [])

  const handleTimeRangeChange = (value: TimeRangeType) => {
    setStaffTimeRange(value)
    fetchStaffReport(value)
  }

  const columns: ColumnsType<StaffPerformanceStats> = [
    {
      title: '员工',
      dataIndex: 'staff_name',
      key: 'staff_name',
    },
    {
      title: '部门',
      dataIndex: 'department',
      key: 'department',
      render: (dept) => dept || '-',
    },
    {
      title: '已分配',
      dataIndex: 'total_assigned',
      key: 'total_assigned',
    },
    {
      title: '已解决',
      dataIndex: 'total_resolved',
      key: 'total_resolved',
    },
    {
      title: '处理中',
      dataIndex: 'total_in_progress',
      key: 'total_in_progress',
    },
    {
      title: '解决率',
      dataIndex: 'resolution_rate',
      key: 'resolution_rate',
      render: (rate) => `${rate}%`,
      sorter: (a, b) => a.resolution_rate - b.resolution_rate,
    },
    {
      title: '平均解决时长',
      dataIndex: 'avg_resolution_hours',
      key: 'avg_resolution_hours',
      render: (hours) => (hours ? `${hours}小时` : '-'),
    },
    {
      title: '平均响应时长',
      dataIndex: 'avg_response_hours',
      key: 'avg_response_hours',
      render: (hours) => (hours ? `${hours}小时` : '-'),
    },
  ]

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Select
          value={staffTimeRange}
          onChange={handleTimeRangeChange}
          style={{ width: 120 }}
          options={timeRangeOptions}
        />
      </Space>

      <Spin spinning={staffReportLoading}>
        <Card style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={8}>
              <Statistic title="员工总数" value={staffReport?.total_staff || 0} />
            </Col>
            <Col span={8}>
              <Statistic
                title="已解决工单"
                value={staffReport?.staff_stats.reduce((sum, s) => sum + s.total_resolved, 0) || 0}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="平均解决率"
                value={
                  staffReport && staffReport.staff_stats.length > 0
                    ? (
                        staffReport.staff_stats.reduce((sum, s) => sum + s.resolution_rate, 0) /
                        staffReport.staff_stats.length
                      ).toFixed(1)
                    : 0
                }
                suffix="%"
              />
            </Col>
          </Row>
        </Card>

        <Table
          columns={columns}
          dataSource={staffReport?.staff_stats || []}
          rowKey="staff_id"
          pagination={false}
        />
      </Spin>
    </div>
  )
}

// Message Report Tab
function MessageReportTab() {
  const {
    messageReport,
    messageReportLoading,
    messageTimeRange,
    fetchMessageReport,
    setMessageTimeRange,
  } = useReportStore()

  useEffect(() => {
    fetchMessageReport()
  }, [])

  const handleTimeRangeChange = (value: TimeRangeType) => {
    setMessageTimeRange(value)
    fetchMessageReport(value)
  }

  const messageTypeMap: Record<string, string> = {
    text: '文本',
    image: '图片',
    voice: '语音',
    video: '视频',
    file: '文件',
    location: '位置',
    link: '链接',
    event: '事件',
  }

  const directionMap: Record<string, string> = {
    inbound: '客人发送',
    outbound: '酒店发送',
  }

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Select
          value={messageTimeRange}
          onChange={handleTimeRangeChange}
          style={{ width: 120 }}
          options={timeRangeOptions}
        />
      </Space>

      <Spin spinning={messageReportLoading}>
        <Row gutter={16}>
          <Col span={12}>
            <Card title="消息类型分布">
              {messageReport?.by_type.map((item) => (
                <div key={item.message_type} style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>{messageTypeMap[item.message_type] || item.message_type}</span>
                    <span>{item.count} ({item.percentage}%)</span>
                  </div>
                  <Progress percent={item.percentage} size="small" />
                </div>
              ))}
            </Card>
          </Col>
          <Col span={12}>
            <Card title="消息方向分布">
              {messageReport?.by_direction.map((item) => (
                <div key={item.direction} style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>{directionMap[item.direction] || item.direction}</span>
                    <span>{item.count} ({item.percentage}%)</span>
                  </div>
                  <Progress percent={item.percentage} size="small" />
                </div>
              ))}
            </Card>
          </Col>
        </Row>

        <Row gutter={16} style={{ marginTop: 16 }}>
          <Col span={8}>
            <Card>
              <Statistic
                title="本期消息总数"
                value={messageReport?.total || 0}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="日均消息数"
                value={messageReport?.avg_daily_count || 0}
                precision={1}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card>
              <Statistic
                title="活跃会话数"
                value={messageReport?.peak_conversations || 0}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  )
}

// Main Reports Page
export default function ReportsPage() {
  const tabItems = [
    {
      key: 'dashboard',
      label: (
        <span>
          <FileTextOutlined /> 仪表盘
        </span>
      ),
      children: <DashboardTab />,
    },
    {
      key: 'tickets',
      label: (
        <span>
          <FileTextOutlined /> 工单报表
        </span>
      ),
      children: <TicketReportTab />,
    },
    {
      key: 'staff',
      label: (
        <span>
          <TeamOutlined /> 员工绩效
        </span>
      ),
      children: <StaffReportTab />,
    },
    {
      key: 'messages',
      label: (
        <span>
          <MessageOutlined /> 消息报表
        </span>
      ),
      children: <MessageReportTab />,
    },
  ]

  return (
    <Card>
      <Title level={4}>数据报表</Title>
      <Tabs items={tabItems} />
    </Card>
  )
}
