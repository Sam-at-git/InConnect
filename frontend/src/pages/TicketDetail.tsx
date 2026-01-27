/**
 * Ticket Detail Page
 */

import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Descriptions,
  Tag,
  Button,
  Space,
  Timeline,
  message,
  Modal,
  Form,
  Select,
  Input,
} from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import { ticketApi, Ticket, TicketTimeline } from '../api/tickets'

const statusColors: Record<string, string> = {
  pending: 'orange',
  assigned: 'blue',
  in_progress: 'cyan',
  resolved: 'green',
  closed: 'default',
  reopened: 'purple',
}

const priorityColors: Record<string, string> = {
  P1: 'red',
  P2: 'orange',
  P3: 'blue',
  P4: 'default',
}

export default function TicketDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [ticket, setTicket] = useState<Ticket | null>(null)
  const [timelines, setTimelines] = useState<TicketTimeline[]>([])
  const [loading, setLoading] = useState(true)
  const [statusModalVisible, setStatusModalVisible] = useState(false)
  const [assignModalVisible, setAssignModalVisible] = useState(false)

  useEffect(() => {
    if (id) {
      fetchTicketData()
    }
  }, [id])

  const fetchTicketData = async () => {
    setLoading(true)
    try {
      const [ticketData, timelineData] = await Promise.all([
        ticketApi.get(id!),
        ticketApi.getTimeline(id!),
      ])
      if (ticketData.data) {
        setTicket(ticketData.data)
      }
      if (timelineData.data) {
        setTimelines(timelineData.data)
      }
    } catch (error) {
      message.error('加载工单详情失败')
    } finally {
      setLoading(false)
    }
  }

  const handleStatusUpdate = async (values: { status: string; comment?: string }) => {
    try {
      await ticketApi.updateStatus(id!, values.status, values.comment)
      message.success('状态更新成功')
      setStatusModalVisible(false)
      fetchTicketData()
    } catch (error) {
      message.error('状态更新失败')
    }
  }

  const getEventTypeLabel = (eventType: string) => {
    const labels: Record<string, string> = {
      created: '创建工单',
      assigned: '分配工单',
      status_changed: '状态变更',
      comment: '添加评论',
      resolved: '已解决',
      closed: '已关闭',
      reopened: '已重开',
    }
    return labels[eventType] || eventType
  }

  if (loading || !ticket) {
    return <Card loading={true} />
  }

  const statusMap: Record<string, string> = {
    pending: '待处理',
    assigned: '已分配',
    in_progress: '处理中',
    resolved: '已解决',
    closed: '已关闭',
    reopened: '已重开',
  }

  return (
    <Card>
      <div style={{ marginBottom: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/tickets')}>
          返回列表
        </Button>
      </div>

      <Card title="工单详情" style={{ marginBottom: 16 }}>
        <Descriptions column={2} bordered>
          <Descriptions.Item label="工单ID">{ticket.id}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={statusColors[ticket.status]}>
              {statusMap[ticket.status] || ticket.status}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="标题" span={2}>
            {ticket.title}
          </Descriptions.Item>
          <Descriptions.Item label="描述" span={2}>
            {ticket.description || '-'}
          </Descriptions.Item>
          <Descriptions.Item label="分类">{ticket.category}</Descriptions.Item>
          <Descriptions.Item label="优先级">
            <Tag color={priorityColors[ticket.priority]}>{ticket.priority}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="分配给">
            {ticket.assigned_to || '未分配'}
          </Descriptions.Item>
          <Descriptions.Item label="创建时间">
            {new Date(ticket.created_at).toLocaleString('zh-CN')}
          </Descriptions.Item>
        </Descriptions>

        <Space style={{ marginTop: 16 }}>
          <Button type="primary" onClick={() => setStatusModalVisible(true)}>
            更新状态
          </Button>
          <Button onClick={() => setAssignModalVisible(true)}>
            分配工单
          </Button>
        </Space>
      </Card>

      <Card title="工单时间线">
        <Timeline
          items={timelines.map((item) => ({
            children: (
              <div>
                <div>
                  <Tag>{getEventTypeLabel(item.event_type)}</Tag>
                </div>
                {item.comment && <p style={{ margin: '4px 0' }}>{item.comment}</p>}
                <p style={{ color: '#999', fontSize: '12px', margin: 0 }}>
                  {new Date(item.created_at).toLocaleString('zh-CN')}
                </p>
              </div>
            ),
          }))}
        />
      </Card>

      {/* Status Update Modal */}
      <Modal
        title="更新工单状态"
        open={statusModalVisible}
        onCancel={() => setStatusModalVisible(false)}
        footer={null}
      >
        <Form onFinish={handleStatusUpdate} layout="vertical">
          <Form.Item
            name="status"
            label="新状态"
            rules={[{ required: true }]}
          >
            <Select>
              <Select.Option value="assigned">已分配</Select.Option>
              <Select.Option value="in_progress">处理中</Select.Option>
              <Select.Option value="resolved">已解决</Select.Option>
              <Select.Option value="closed">已关闭</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="comment" label="备注">
            <Input.TextArea rows={3} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              更新
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  )
}
