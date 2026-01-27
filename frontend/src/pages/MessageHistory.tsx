/**
 * Message History Search Page
 */

import { useEffect, useState } from 'react'
import {
  Card,
  Table,
  Button,
  Input,
  Select,
  Space,
  Typography,
  message,
  DatePicker,
  Tag,
  Row,
  Col,
} from 'antd'
import { SearchOutlined, ExportOutlined, ReloadOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { messageApi, Message } from '../api/messages'
import dayjs from 'dayjs'

const { Title } = Typography
const { Option } = Select
const { RangePicker } = DatePicker

const typeColors: Record<string, string> = {
  text: 'blue',
  image: 'green',
  voice: 'orange',
  video: 'purple',
  file: 'cyan',
  link: 'geekblue',
}

const directionMap: Record<string, string> = {
  inbound: '客人发送',
  outbound: '酒店发送',
}

const directionColors: Record<string, string> = {
  inbound: 'orange',
  outbound: 'blue',
}

export default function MessageHistoryPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [keyword, setKeyword] = useState('')
  const [conversationFilter, setConversationFilter] = useState<string | undefined>()
  const [typeFilter, setTypeFilter] = useState<string | undefined>()
  const [directionFilter, setDirectionFilter] = useState<string | undefined>()
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs] | null>(null)

  // Load initial data
  useEffect(() => {
    handleSearch()
  }, [])

  const handleSearch = async () => {
    setLoading(true)
    try {
      const params: any = {
        hotel_id: 'default-hotel',
        limit: 100,
      }

      if (keyword) params.keyword = keyword
      if (conversationFilter) params.conversation_id = conversationFilter
      if (typeFilter) params.message_type = typeFilter
      if (directionFilter) params.direction = directionFilter
      if (dateRange) {
        params.start_date = dateRange[0].toISOString()
        params.end_date = dateRange[1].toISOString()
      }

      const response = await messageApi.search(params)
      setMessages(response.data || [])
    } catch (error) {
      message.error('搜索失败')
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    try {
      const params: any = {
        hotel_id: 'default-hotel',
      }

      if (keyword) params.keyword = keyword
      if (conversationFilter) params.conversation_id = conversationFilter
      if (dateRange) {
        params.start_date = dateRange[0].toISOString()
        params.end_date = dateRange[1].toISOString()
      }

      const blob = await messageApi.export(params)

      // Create download link
      const url = window.URL.createObjectURL(new Blob([blob]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `messages_${new Date().getTime()}.csv`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)

      message.success('导出成功')
    } catch (error) {
      message.error('导出失败')
    }
  }

  const handleReset = () => {
    setKeyword('')
    setConversationFilter(undefined)
    setTypeFilter(undefined)
    setDirectionFilter(undefined)
    setDateRange(null)
  }

  const columns: ColumnsType<Message> = [
    {
      title: '消息ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
      ellipsis: true,
    },
    {
      title: '会话ID',
      dataIndex: 'conversation_id',
      key: 'conversation_id',
      width: 100,
      ellipsis: true,
    },
    {
      title: '消息类型',
      dataIndex: 'message_type',
      key: 'message_type',
      width: 100,
      render: (type: string) => (
        <Tag color={typeColors[type]}>{type}</Tag>
      ),
    },
    {
      title: '方向',
      dataIndex: 'direction',
      key: 'direction',
      width: 100,
      render: (direction: string) => (
        <Tag color={directionColors[direction]}>
          {directionMap[direction] || direction}
        </Tag>
      ),
    },
    {
      title: '内容',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
      render: (content: string) => (
        <span style={{ fontSize: '12px' }}>
          {content || '-'}
        </span>
      ),
    },
    {
      title: '发送者',
      dataIndex: 'sender_id',
      key: 'sender_id',
      width: 120,
      ellipsis: true,
      render: (sender) => sender || '-',
    },
    {
      title: '发送时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
  ]

  return (
    <Card>
      <Title level={4}>消息历史查询</Title>

      {/* Search Filters */}
      <Card size="small" style={{ marginBottom: 16, background: '#f5f5f5' }}>
        <Row gutter={16}>
          <Col span={6}>
            <label>关键字搜索：</label>
            <Input
              placeholder="搜索消息内容"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onPressEnter={handleSearch}
            />
          </Col>
          <Col span={4}>
            <label>消息类型：</label>
            <Select
              style={{ width: '100%' }}
              value={typeFilter}
              onChange={setTypeFilter}
              allowClear
            >
              <Option value="text">文本</Option>
              <Option value="image">图片</Option>
              <Option value="voice">语音</Option>
              <Option value="video">视频</Option>
              <Option value="file">文件</Option>
              <Option value="link">链接</Option>
            </Select>
          </Col>
          <Col span={4}>
            <label>消息方向：</label>
            <Select
              style={{ width: '100%' }}
              value={directionFilter}
              onChange={setDirectionFilter}
              allowClear
            >
              <Option value="inbound">客人发送</Option>
              <Option value="outbound">酒店发送</Option>
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
          <Col span={4}>
            <label>&nbsp;</label>
            <Space style={{ width: '100%' }}>
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={handleSearch}
              >
                搜索
              </Button>
              <Button icon={<ReloadOutlined />} onClick={handleReset}>
                重置
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Action Bar */}
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <span>找到 {messages.length} 条消息</span>
        <Button icon={<ExportOutlined />} onClick={handleExport}>
          导出结果
        </Button>
      </Space>

      {/* Results Table */}
      <Table
        columns={columns}
        dataSource={messages}
        rowKey="id"
        loading={loading}
        pagination={{
          pageSize: 50,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
        }}
      />
    </Card>
  )
}
