/**
 * Conversation List Page
 */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Card,
  List,
  Tag,
  Typography,
  Space,
  Button,
  Input,
} from 'antd'
import { SearchOutlined, MessageOutlined } from '@ant-design/icons'
import { messageApi, Conversation } from '../api/messages'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

const { Title, Text } = Typography
const { Search } = Input

export default function ConversationListPage() {
  const navigate = useNavigate()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)
  const [searchText, setSearchText] = useState('')

  useEffect(() => {
    fetchConversations()
  }, [])

  const fetchConversations = async () => {
    setLoading(true)
    try {
      const response = await messageApi.listConversations({ status: 'active', limit: 100 })
      if (response.data) {
        setConversations(response.data)
      }
    } catch (error) {
      console.error('Failed to fetch conversations:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredConversations = conversations.filter((conv) => {
    if (!searchText) return true
    const searchLower = searchText.toLowerCase()
    return (
      conv.guest_name?.toLowerCase().includes(searchLower) ||
      conv.guest_phone?.includes(searchLower) ||
      conv.guest_id.toLowerCase().includes(searchLower)
    )
  })

  return (
    <Card>
      <div style={{ marginBottom: 16 }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Title level={4} style={{ margin: 0 }}>
            会话列表
          </Title>
          <Search
            placeholder="搜索客人信息"
            allowClear
            style={{ width: 300 }}
            onSearch={setSearchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
        </Space>
      </div>

      <List
        loading={loading}
        dataSource={filteredConversations}
        renderItem={(item) => (
          <List.Item
            key={item.id}
            style={{ cursor: 'pointer', padding: '16px 0' }}
            onClick={() => navigate(`/messages/${item.id}`)}
          >
            <List.Item.Meta
              avatar={
                <div
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: '50%',
                    background: '#1890ff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                    fontSize: 20,
                  }}
                >
                  {item.guest_name?.charAt(0) || '客'}
                </div>
              }
              title={
                <Space>
                  <Text strong>{item.guest_name || item.guest_id}</Text>
                  <Tag color="green">active</Tag>
                </Space>
              }
              description={
                <Space direction="vertical" size={0}>
                  <Text type="secondary">{item.guest_phone || '无电话'}</Text>
                  {item.last_message_at && (
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {formatDistanceToNow(new Date(item.last_message_at), {
                        addSuffix: true,
                        locale: zhCN,
                      })}
                    </Text>
                  )}
                </Space>
              }
            />
            <Button
              type="primary"
              icon={<MessageOutlined />}
              onClick={(e) => {
                e.stopPropagation()
                navigate(`/messages/${item.id}`)
              }}
            >
              查看消息
            </Button>
          </List.Item>
        )}
      />
    </Card>
  )
}
