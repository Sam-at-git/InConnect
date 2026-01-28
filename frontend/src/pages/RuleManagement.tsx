/**
 * Routing Rules Management Page
 */

import { useEffect, useState } from 'react'
import {
  Card,
  Table,
  Button,
  Space,
  Typography,
  message,
  Modal,
  Form,
  Input,
  Select,
  Switch,
  InputNumber,
  Tag,
  Drawer,
  Divider,
  Row,
  Col,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ExperimentOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { rulesApi, RoutingRule, RuleTestRequest } from '../api/rules'
import { staffApi } from '../api/staff'
import { settingsApi, TicketCategoryConfig, PriorityConfig } from '../api/settings'

const { Title, Text } = Typography
const { TextArea } = Input
const { Option } = Select

const typeColors: Record<string, string> = {
  keyword: 'blue',
  category: 'green',
  priority: 'orange',
  round_robin: 'purple',
  manual: 'default',
}

const typeMap: Record<string, string> = {
  keyword: '关键词匹配',
  category: '分类匹配',
  priority: '优先级匹配',
  round_robin: '轮询分配',
  manual: '手动分配',
}

export default function RuleManagementPage() {
  const [rules, setRules] = useState<RoutingRule[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [testDrawerVisible, setTestDrawerVisible] = useState(false)
  const [editingRule, setEditingRule] = useState<RoutingRule | null>(null)
  const [testResult, setTestResult] = useState<any>(null)
  const [form] = Form.useForm()

  // Options data
  const [staffList, setStaffList] = useState<Array<{ id: string; name: string }>>([])
  const [categories, setCategories] = useState<TicketCategoryConfig[]>([])
  const [priorities, setPriorities] = useState<PriorityConfig[]>([])

  useEffect(() => {
    loadRules()
    loadOptions()
  }, [])

  const loadRules = async () => {
    setLoading(true)
    try {
      const response = await rulesApi.getSummary('default-hotel')
      setRules(response.data || [])
    } catch (error) {
      message.error('加载规则失败')
    } finally {
      setLoading(false)
    }
  }

  const loadOptions = async () => {
    try {
      const [staffRes, catRes, priRes] = await Promise.all([
        staffApi.list(),
        settingsApi.getCategories(),
        settingsApi.getPriorities(),
      ])
      setStaffList(staffRes.data || [])
      setCategories(catRes.data || [])
      setPriorities(priRes.data || [])
    } catch (error) {
      console.error('Failed to load options:', error)
    }
  }

  const handleCreate = () => {
    setEditingRule(null)
    form.resetFields()
    setModalVisible(true)
  }

  const handleEdit = (rule: RoutingRule) => {
    setEditingRule(rule)
    form.setFieldsValue({
      name: rule.name,
      rule_type: rule.type,
      keywords: rule.keywords || [],
      category: rule.category,
      priority: rule.priority,
      target_staff_ids: [],
      rule_priority: rule.rule_priority,
      is_active: rule.is_active,
    })
    setModalVisible(true)
  }

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      const request = {
        ...values,
        target_staff_ids: values.target_staff_ids || [],
      }

      if (editingRule) {
        await rulesApi.update(editingRule.id, request)
        message.success('更新成功')
      } else {
        await rulesApi.create('default-hotel', request)
        message.success('创建成功')
      }

      setModalVisible(false)
      loadRules()
    } catch (error) {
      message.error('保存失败')
    }
  }

  const handleDelete = (rule: RoutingRule) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除规则 "${rule.name}" 吗？`,
      onOk: async () => {
        try {
          await rulesApi.delete(rule.id)
          message.success('删除成功')
          loadRules()
        } catch (error) {
          message.error('删除失败')
        }
      },
    })
  }

  const handleReorder = async (rule: RoutingRule, direction: 'up' | 'down') => {
    const newPriority = direction === 'up' ? rule.rule_priority + 1 : rule.rule_priority - 1
    try {
      await rulesApi.reorder(rule.id, newPriority)
      loadRules()
    } catch (error) {
      message.error('调整优先级失败')
    }
  }

  const handleTest = async () => {
    try {
      const values = await form.validateFields()
      const request: RuleTestRequest = {
        message_content: values.test_message || '',
        category: values.test_category,
        priority: values.test_priority,
      }

      const result = await rulesApi.test('default-hotel', request)
      setTestResult(result.data)
    } catch (error) {
      message.error('测试失败')
    }
  }

  const columns: ColumnsType<RoutingRule> = [
    {
      title: '优先级',
      dataIndex: 'rule_priority',
      key: 'rule_priority',
      width: 80,
      sorter: (a, b) => a.rule_priority - b.rule_priority,
      render: (priority) => <Tag color="blue">{priority}</Tag>,
    },
    {
      title: '规则名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 120,
      render: (type) => (
        <Tag color={typeColors[type]}>{typeMap[type] || type}</Tag>
      ),
    },
    {
      title: '关键词',
      dataIndex: 'keywords',
      key: 'keywords',
      width: 200,
      render: (keywords) =>
        keywords?.length ? (
          <Space wrap>
            {keywords.slice(0, 3).map((kw, i) => (
              <Tag key={i}>{kw}</Tag>
            ))}
            {keywords.length > 3 && <Tag>+{keywords.length - 3}</Tag>}
          </Space>
        ) : '-',
    },
    {
      title: '分类/优先级',
      key: 'conditions',
      width: 150,
      render: (_, record) => (
        <Space direction="vertical" size="small">
          {record.category && <Tag color="green">{record.category}</Tag>}
          {record.priority && <Tag color="orange">{record.priority}</Tag>}
          {!record.category && !record.priority && '-'}
        </Space>
      ),
    },
    {
      title: '分配人数',
      dataIndex: 'target_staff_count',
      key: 'target_staff_count',
      width: 100,
      render: (count) => `${count} 人`,
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 80,
      render: (active) => (
        <Tag color={active ? 'green' : 'red'}>
          {active ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Button
            type="text"
            icon={<ArrowUpOutlined />}
            onClick={() => handleReorder(record, 'up')}
          />
          <Button
            type="text"
            icon={<ArrowDownOutlined />}
            onClick={() => handleReorder(record, 'down')}
          />
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <Card>
      <div style={{ marginBottom: 16 }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Title level={4} style={{ margin: 0 }}>
            路由规则管理
          </Title>
          <Space>
            <Button
              icon={<ExperimentOutlined />}
              onClick={() => setTestDrawerVisible(true)}
            >
              规则测试
            </Button>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
              新建规则
            </Button>
          </Space>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={rules}
        rowKey="id"
        loading={loading}
        pagination={false}
      />

      {/* Create/Edit Modal */}
      <Modal
        title={editingRule ? '编辑规则' : '新建规则'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={handleSave}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="规则名称"
            rules={[{ required: true, message: '请输入规则名称' }]}
          >
            <Input placeholder="请输入规则名称" />
          </Form.Item>

          <Form.Item
            name="rule_type"
            label="规则类型"
            rules={[{ required: true, message: '请选择规则类型' }]}
          >
            <Select placeholder="请选择规则类型">
              <Option value="keyword">关键词匹配</Option>
              <Option value="category">分类匹配</Option>
              <Option value="priority">优先级匹配</Option>
              <Option value="manual">手动分配</Option>
            </Select>
          </Form.Item>

          <Form.Item noStyle shouldUpdate={(prev, curr) => prev.rule_type !== curr.rule_type}>
            {({ getFieldValue }) =>
              getFieldValue('rule_type') === 'keyword' ? (
                <Form.Item name="keywords" label="关键词（每行一个）">
                  <TextArea
                    rows={4}
                    placeholder="请输入关键词，每行一个&#10;例如：&#10;空调&#10;维修&#10;漏水"
                  />
                </Form.Item>
              ) : null
            }
          </Form.Item>

          <Form.Item noStyle shouldUpdate={(prev, curr) => prev.rule_type !== curr.rule_type}>
            {({ getFieldValue }) =>
              getFieldValue('rule_type') === 'category' ? (
                <Form.Item name="category" label="工单分类">
                  <Select placeholder="请选择分类">
                    {categories.map((cat) => (
                      <Option key={cat.key} value={cat.key}>
                        {cat.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              ) : null
            }
          </Form.Item>

          <Form.Item noStyle shouldUpdate={(prev, curr) => prev.rule_type !== curr.rule_type}>
            {({ getFieldValue }) =>
              getFieldValue('rule_type') === 'priority' ? (
                <Form.Item name="priority" label="工单优先级">
                  <Select placeholder="请选择优先级">
                    {priorities.map((pri) => (
                      <Option key={pri.key} value={pri.key}>
                        {pri.label}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              ) : null
            }
          </Form.Item>

          <Form.Item
            name="target_staff_ids"
            label="分配员工"
            rules={[{ required: true, message: '请选择分配员工' }]}
          >
            <Select mode="multiple" placeholder="请选择员工" options={
              staffList.map(s => ({ label: s.name, value: s.id }))
            } />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="rule_priority"
                label="规则优先级"
                initialValue={0}
                rules={[{ required: true }]}
              >
                <InputNumber min={0} max={100} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="is_active"
                label="启用状态"
                valuePropName="checked"
                initialValue={true}
              >
                <Switch checkedChildren="启用" unCheckedChildren="禁用" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* Rule Test Drawer */}
      <Drawer
        title="规则测试"
        placement="right"
        width={500}
        open={testDrawerVisible}
        onClose={() => setTestDrawerVisible(false)}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="test_message"
            label="测试消息内容"
            rules={[{ required: true, message: '请输入消息内容' }]}
          >
            <TextArea
              rows={4}
              placeholder="请输入要测试的消息内容"
            />
          </Form.Item>

          <Form.Item name="test_category" label="工单分类（可选）">
            <Select placeholder="请选择分类" allowClear>
              {categories.map((cat) => (
                <Option key={cat.key} value={cat.key}>
                  {cat.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item name="test_priority" label="工单优先级（可选）">
            <Select placeholder="请选择优先级" allowClear>
              {priorities.map((pri) => (
                <Option key={pri.key} value={pri.key}>
                  {pri.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={handleTest}
            block
          >
            运行测试
          </Button>
        </Form>

        <Divider />

        {testResult && (
          <div>
            <Title level={5}>测试结果</Title>
            <Card size="small">
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text type="secondary">匹配规则：</Text>
                  <Tag color="blue">{testResult.matched_rule.name}</Tag>
                </div>
                <div>
                  <Text type="secondary">规则类型：</Text>
                  <Tag>{typeMap[testResult.matched_rule.type] || testResult.matched_rule.type}</Tag>
                </div>
                <div>
                  <Text type="secondary">分配员工：</Text>
                  <div style={{ marginTop: 8 }}>
                    {testResult.assigned_staff.length > 0 ? (
                      testResult.assigned_staff.map((staff: any) => (
                        <Tag key={staff.id}>{staff.name}</Tag>
                      ))
                    ) : (
                      <Text type="secondary">无可用员工</Text>
                    )}
                  </div>
                </div>
              </Space>
            </Card>
          </div>
        )}
      </Drawer>
    </Card>
  )
}
