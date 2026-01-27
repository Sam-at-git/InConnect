/**
 * Message Chat Page
 */

import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  List,
  Input,
  Button,
  Space,
  Typography,
  Tag,
  Avatar,
} from 'antd'
import {
  SendOutlined,
  ArrowLeftOutlined,
  CloseOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons'
import { messageApi, Message, Conversation } from '../api/messages'
import { formatDistanceToNow } from 'date-fns'
import { zhCN } from 'date-fns/locale'

const { Title, Text } = Typography
const { TextArea } = Input

export default function MessageChatPage() {
  const { conversationId } = useParams<{ conversationId: string }>()
  const navigate = useNavigate()
  const [messages, setMessages] = useState<Message[]>([])
  const [conversation, setConversation] = useState<Conversation | null>(null)
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [inputText, setInputText] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (conversationId) {
      fetchMessages()
    }
  }, [conversationId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const fetchMessages = async () => {
    setLoading(true)
    try {
      const response = await messageApi.getMessages(conversationId!)
      if (response.data) {
        setMessages(response.data)
      }

      // Get conversation info from first message or fetch separately
      if (response.data && response.data.length > 0) {
        setConversation({
          id: conversationId!,
          guest_id: response.data[0].sender_id || 'unknown',
          status: 'active',
        } as Conversation)
      }
    } catch (error) {
      console.error('Failed to fetch messages:', error)
    } finally {
      setLoading(false)
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSend = async () => {
    if (!inputText.trim()) return

    setSending(true)
    try {
      const response = await messageApi.send({
        conversation_id: conversationId!,
        content: inputText,
      })

      if (response.code === 0) {
        // Add optimistic message
        const newMessage: Message = {
          id: response.data?.message_id || '',
          conversation_id: conversationId!,
          message_type: 'text',
          direction: 'outbound',
          content: inputText,
          is_read: false,
          sent_at: new Date().toISOString(),
          created_at: new Date().toISOString(),
        }
        setMessages([...messages, newMessage])
        setInputText('')
      } else {
        console.error('Failed to send message:', response.message)
      }
    } catch (error) {
      console.error('Failed to send message:', error)
    } finally {
      setSending(false)
    }
  }

  const handleCloseConversation = async () => {
    try {
      await messageApi.closeConversation(conversationId!)
      navigate('/messages')
    } catch (error) {
      console.error('Failed to close conversation:', error)
    }
  }

  const renderMessage = (msg: Message) => {
    const isInbound = msg.direction === 'inbound'

    return (
      <div
        key={msg.id}
        style={{
          display: 'flex',
          justifyContent: isInbound ? 'flex-start' : 'flex-end',
          marginBottom: 16,
        }}
      >
        <div style={{ maxWidth: '70%' }}>
          <div
            style={{
              background: isInbound ? '#f0f0f0' : '#1890ff',
              color: isInbound ? '#000' : '#fff',
              padding: '12px 16px',
              borderRadius: 8,
              borderTopLeftRadius: isInbound ? 0 : 8,
              borderTopRightRadius: isInbound ? 8 : 0,
            }}
          >
            <Text style={{ color: isInbound ? '#000' : '#fff' }}>
              {msg.content}
            </Text>
          </div>
          <div style={{ marginTop: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {formatDistanceToNow(new Date(msg.sent_at), {
                addSuffix: true,
                locale: zhCN,
              })}
            </Text>
            {!isInbound && msg.is_read && (
              <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 12 }} />
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <Card>
      <div style={{ marginBottom: 16 }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/messages')}
          >
            返回列表
          </Button>
          <Space>
            <Title level={4} style={{ margin: 0 }}>
              {conversation?.guest_name || conversation?.guest_id}
            </Title>
            <Tag color="green">进行中</Tag>
            <Button
              danger
              icon={<CloseOutlined />}
              onClick={handleCloseConversation}
            >
              结束会话
            </Button>
          </Space>
        </Space>
      </div>

      <div
        style={{
          height: 'calc(100vh - 350px)',
          overflowY: 'auto',
          padding: '16px 0',
        }}
      >
        {loading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>加载中...</div>
        ) : messages.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 40 }}>暂无消息</div>
        ) : (
          <>{messages.map(renderMessage)}</>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ borderTop: '1px solid #f0f0f0', paddingTop: 16 }}>
        <Space style={{ width: '100%' }} direction="vertical">
          <TextArea
            rows={3}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onPressEnter={(e) => {
              if (e.shiftKey) return
              e.preventDefault()
              handleSend()
            }}
            placeholder="输入消息... (Shift+Enter 换行)"
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Space>
              <Text type="secondary">{inputText.length}/2000</Text>
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleSend}
                loading={sending}
                disabled={!inputText.trim()}
              >
                发送
              </Button>
            </Space>
          </div>
        </Space>
      </div>
    </Card>
  )
}
