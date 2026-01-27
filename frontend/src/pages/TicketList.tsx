/**
 * Ticket List Page with Batch Operations
 */

import { useEffect, useState } from 'react'
import {
  Table,
  Button,
  Tag,
  Space,
  Select,
  Input,
  Card,
  Typography,
  message,
  Modal,
  Dropdown,
  Divider,
} from 'antd'
import {
  PlusOutlined,
  ReloadOutlined,
  UserAddOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExportOutlined,
  DownOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import type { MenuProps } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useTicketStore } from '../stores/ticket'
import { ticketApi, Ticket } from '../api/tickets'
import { batchApi, BatchOperationResult } from '../api/batch'
import { staffApi } from '../api/staff'

const { Title } = Typography
const { Option } = Select

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

export default function TicketListPage() {
  const navigate = useNavigate()
  const { tickets, loading, pagination, fetchTickets } = useTicketStore()
  const [statusFilter, setStatusFilter] = useState<string | undefined>()
  const [searchText, setSearchText] = useState('')
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([])
  const [staffList, setStaffList] = useState<Array<{ id: string; name: string }>>([])
  const [batchModalVisible, setBatchModalVisible] = useState(false)
  const [batchAction, setBatchAction] = useState<'assign' | 'status' | null>(null)
  const [batchLoading, setBatchLoading] = useState(false)

  useEffect(() => {
    fetchTickets()
    // Fetch staff list for batch assignment
    loadStaffList()
  }, [])

  const loadStaffList = async () => {
    try {
      const response = await staffApi.list()
      setStaffList(response.data || [])
    } catch (error) {
      console.error('Failed to load staff:', error)
    }
  }

  const handleRefresh = () => {
    fetchTickets({ status: statusFilter })
    message.success('刷新成功')
  }

  const handleStatusChange = (value: string | undefined) => {
    setStatusFilter(value)
    fetchTickets({ status: value })
  }

  const handleBatchAssign = async (staffId: string, comment?: string) => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择工单')
      return
    }

    setBatchLoading(true)
    try {
      const result = await batchApi.assign({
        ticket_ids: selectedRowKeys as string[],
        staff_id: staffId,
        comment,
      })

      if (result.data.failed_count > 0) {
        message.warning(
          `已分配 ${result.data.success_count} 个工单，失败 ${result.data.failed_count} 个`
        )
      } else {
        message.success(`成功分配 ${result.data.success_count} 个工单`)
      }

      setSelectedRowKeys([])
      fetchTickets({ status: statusFilter })
      setBatchModalVisible(false)
    } catch (error) {
      message.error('批量分配失败')
    } finally {
      setBatchLoading(false)
    }
  }

  const handleBatchStatusUpdate = async (status: string, comment?: string) => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择工单')
      return
    }

    setBatchLoading(true)
    try {
      const result = await batchApi.updateStatus({
        ticket_ids: selectedRowKeys as string[],
        status,
        comment,
      })

      if (result.data.failed_count > 0) {
        message.warning(
          `已更新 ${result.data.success_count} 个工单，失败 ${result.data.failed_count} 个`
        )
      } else {
        message.success(`成功更新 ${result.data.success_count} 个工单`)
      }

      setSelectedRowKeys([])
      fetchTickets({ status: statusFilter })
      setBatchModalVisible(false)
    } catch (error) {
      message.error('批量更新失败')
    } finally {
      setBatchLoading(false)
    }
  }

  const handleExport = async () => {
    try {
      const blob = await batchApi.export({
        hotel_id: 'default-hotel',
        status: statusFilter,
      })

      // Create download link
      const url = window.URL.createObjectURL(new Blob([blob]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `tickets_${new Date().getTime()}.csv`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)

      message.success('导出成功')
    } catch (error) {
      message.error('导出失败')
    }
  }

  const batchMenuItems: MenuProps['items'] = [
    {
      key: 'assign',
      label: '批量分配',
      icon: <UserAddOutlined />,
      onClick: () => {
        setBatchAction('assign')
        setBatchModalVisible(true)
      },
    },
    {
      key: 'resolved',
      label: '标记为已解决',
      icon: <CheckCircleOutlined />,
      onClick: () => handleBatchStatusUpdate('resolved'),
    },
    {
      key: 'closed',
      label: '标记为已关闭',
      icon: <CloseCircleOutlined />,
      onClick: () => handleBatchStatusUpdate('closed'),
    },
    {
      type: 'divider',
    },
    {
      key: 'export',
      label: '导出选中',
      icon: <ExportOutlined />,
      onClick: () => handleExport(),
    },
  ]

  const columns: ColumnsType<Ticket> = [
    {
      title: '工单ID',
      dataIndex: 'id',
      key: 'id',
      width: 150,
      render: (id: string) => (
        <a onClick={() => navigate(`/tickets/${id}`)}>{id}</a>
      ),
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 100,
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      render: (priority: string) => (
        <Tag color={priorityColors[priority]}>{priority}</Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusMap: Record<string, string> = {
          pending: '待处理',
          assigned: '已分配',
          in_progress: '处理中',
          resolved: '已解决',
          closed: '已关闭',
          reopened: '已重开',
        }
        return <Tag color={statusColors[status]}>{statusMap[status] || status}</Tag>
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Button
          type="link"
          onClick={() => navigate(`/tickets/${record.id}`)}
        >
          查看
        </Button>
      ),
    },
  ]

  const rowSelection = {
    selectedRowKeys,
    onChange: (newSelectedRowKeys: React.Key[]) => {
      setSelectedRowKeys(newSelectedRowKeys)
    },
  }

  return (
    <Card>
      <div style={{ marginBottom: 16 }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Title level={4} style={{ margin: 0 }}>
            工单列表
            {selectedRowKeys.length > 0 && (
              <Tag color="blue" style={{ marginLeft: 8 }}>
                已选 {selectedRowKeys.length} 项
              </Tag>
            )}
          </Title>
          <Space>
            <Input.Search
              placeholder="搜索工单"
              style={{ width: 200 }}
              onSearch={(value) => console.log('Search:', value)}
            />
            <Select
              placeholder="状态筛选"
              style={{ width: 120 }}
              allowClear
              onChange={handleStatusChange}
            >
              <Option value="pending">待处理</Option>
              <Option value="assigned">已分配</Option>
              <Option value="in_progress">处理中</Option>
              <Option value="resolved">已解决</Option>
              <Option value="closed">已关闭</Option>
            </Select>
            <Button icon={<ReloadOutlined />} onClick={handleRefresh}>
              刷新
            </Button>
            <Dropdown
              menu={{ items: batchMenuItems }}
              disabled={selectedRowKeys.length === 0}
            >
              <Button>
                批量操作 <DownOutlined />
              </Button>
            </Dropdown>
            <Button
              type="primary"
              icon={<ExportOutlined />}
              onClick={() => handleExport()}
            >
              导出全部
            </Button>
            <Button type="primary" icon={<PlusOutlined />}>
              新建工单
            </Button>
          </Space>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={tickets}
        rowKey="id"
        loading={loading}
        rowSelection={rowSelection}
        pagination={{
          current: pagination.page,
          pageSize: pagination.pageSize,
          total: pagination.total,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条`,
          onChange: (page, pageSize) => {
            fetchTickets({ page, pageSize, status: statusFilter })
          },
        }}
      />

      {/* Batch Assign Modal */}
      <Modal
        title="批量分配工单"
        open={batchModalVisible && batchAction === 'assign'}
        onCancel={() => {
          setBatchModalVisible(false)
          setBatchAction(null)
        }}
        footer={null}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <label>选择员工：</label>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              placeholder="请选择员工"
              onSelect={(value) => handleBatchAssign(value)}
            >
              {staffList.map((staff) => (
                <Option key={staff.id} value={staff.id}>
                  {staff.name}
                </Option>
              ))}
            </Select>
          </div>
        </Space>
      </Modal>
    </Card>
  )
}
