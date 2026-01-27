/**
 * Staff Dashboard Page
 */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Card,
  Row,
  Col,
  Statistic,
  List,
  Tag,
  Typography,
  Space,
  Button,
} from 'antd'
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  RightOutlined,
} from '@ant-design/icons'
import { ticketApi, Ticket } from '../api/tickets'
import { useAuthStore } from '../stores/auth'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

const { Title } = Typography

export default function StaffDashboardPage() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [myTickets, setMyTickets] = useState<Ticket[]>([])
  const [pendingTickets, setPendingTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(true)

  // Stats
  const [stats, setStats] = useState({
    myTickets: 0,
    pending: 0,
    todayCompleted: 0,
    overdue: 0,
  })

  useEffect(() => {
    if (user) {
      fetchDashboardData()
    }
  }, [user])

  const fetchDashboardData = async () => {
    setLoading(true)
    try {
      // Fetch tickets assigned to me
      const myResponse = await ticketApi.list({ limit: 20 })
      if (myResponse.data) {
        const assignedToMe = myResponse.data.items.filter(
          (t) => t.assigned_to === user?.id
        )
        setMyTickets(assignedToMe)
        setStats((prev) => ({ ...prev, myTickets: assignedToMe.length }))
      }

      // Fetch pending tickets
      const pendingResponse = await ticketApi.list({ status: 'pending', limit: 20 })
      if (pendingResponse.data) {
        setPendingTickets(pendingResponse.data.items)
        setStats((prev) => ({ ...prev, pending: pendingResponse.data.total }))
      }

      // Simulated stats for demo
      setStats((prev) => ({
        ...prev,
        todayCompleted: Math.floor(Math.random() * 10),
        overdue: Math.floor(Math.random() * 5),
      }))
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      P1: 'red',
      P2: 'orange',
      P3: 'blue',
      P4: 'default',
    }
    return colors[priority] || 'default'
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'orange',
      assigned: 'blue',
      in_progress: 'cyan',
      resolved: 'green',
      closed: 'default',
    }
    return colors[status] || 'default'
  }

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      pending: '待处理',
      assigned: '已分配',
      in_progress: '处理中',
      resolved: '已解决',
      closed: '已关闭',
    }
    return texts[status] || status
  }

  return (
    <div>
      <Title level={3}>欢迎回来, {user?.name}</Title>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="我的工单"
              value={stats.myTickets}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待分配"
              value={stats.pending}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日完成"
              value={stats.todayCompleted}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="逾期工单"
              value={stats.overdue}
              prefix={<ExclamationCircleOutlined />}
              valueStyle={{ color: '#f5222d' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        <Col span={12}>
          <Card
            title="我的工单"
            extra={
              <Button
                type="link"
                icon={<RightOutlined />}
                onClick={() => navigate('/tickets?assigned_to_me=true')}
              >
                查看全部
              </Button>
            }
          >
            <List
              loading={loading}
              dataSource={myTickets.slice(0, 5)}
              renderItem={(ticket) => (
                <List.Item
                  style={{ cursor: 'pointer' }}
                  onClick={() => navigate(`/tickets/${ticket.id}`)}
                >
                  <List.Item.Meta
                    title={
                      <Space>
                        <Tag color={getPriorityColor(ticket.priority)}>
                          {ticket.priority}
                        </Tag>
                        {ticket.title}
                      </Space>
                    }
                    description={
                      <Space>
                        <Tag color={getStatusColor(ticket.status)}>
                          {getStatusText(ticket.status)}
                        </Tag>
                        <span>
                          {formatDistanceToNow(new Date(ticket.created_at), {
                            addSuffix: true,
                            locale: zhCN,
                          })}
                        </span>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        <Col span={12}>
          <Card
            title="待分配工单"
            extra={
              <Button
                type="link"
                icon={<RightOutlined />}
                onClick={() => navigate('/tickets?status=pending')}
              >
                查看全部
              </Button>
            }
          >
            <List
              loading={loading}
              dataSource={pendingTickets.slice(0, 5)}
              renderItem={(ticket) => (
                <List.Item
                  style={{ cursor: 'pointer' }}
                  onClick={() => navigate(`/tickets/${ticket.id}`)}
                >
                  <List.Item.Meta
                    title={
                      <Space>
                        <Tag color={getPriorityColor(ticket.priority)}>
                          {ticket.priority}
                        </Tag>
                        {ticket.title}
                      </Space>
                    }
                    description={
                      <Space>
                        <span>{ticket.category}</span>
                        <span>
                          {formatDistanceToNow(new Date(ticket.created_at), {
                            addSuffix: true,
                            locale: zhCN,
                          })}
                        </span>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}
