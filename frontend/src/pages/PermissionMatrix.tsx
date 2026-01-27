/**
 * Permission Matrix Management Page
 */

import { useEffect, useState } from 'react'
import {
  Card,
  Table,
  Typography,
  Switch,
  Tag,
  Space,
  Row,
  Col,
  Statistic,
} from 'antd'
import {
  CheckOutlined,
  CloseOutlined,
  SafetyOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { permissionsApi, Permission, Role } from '../api/permissions'

const { Title, Text } = Typography

const roleColors: Record<string, string> = {
  super_admin: 'red',
  hotel_admin: 'orange',
  dept_manager: 'blue',
  staff: 'green',
  read_only: 'default',
}

const roleNames: Record<string, string> = {
  super_admin: '超管',
  hotel_admin: '店长',
  dept_manager: '主管',
  staff: '员工',
  read_only: '只读',
}

export default function PermissionMatrixPage() {
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [permsRes, rolesRes] = await Promise.all([
        permissionsApi.list(),
        permissionsApi.listRoles(),
      ])
      setPermissions(permsRes.data || [])
      setRoles(rolesRes.data || [])
    } catch (error) {
      console.error('Failed to load permissions:', error)
    } finally {
      setLoading(false)
    }
  }

  // Group permissions by category
  const groupedPermissions = permissions.reduce((acc, perm) => {
    if (!acc[perm.category]) {
      acc[perm.category] = []
    }
    acc[perm.category].push(perm)
    return acc
  }, {} as Record<string, Permission[]>)

  const columns: ColumnsType<any> = [
    {
      title: '功能',
      dataIndex: 'permission',
      key: 'permission',
      fixed: 'left',
      width: 200,
      render: (perm: string) => (
        <Text style={{ fontSize: '12px' }}>{perm.replace(/_/g, ' ')}</Text>
      ),
    },
    ...roles.map((role) => ({
      title: roleNames[role.name] || role.name,
      dataIndex: role.name,
      key: role.name,
      align: 'center' as const,
      width: 100,
      render: (hasPerm: boolean) => (
        hasPerm ? (
          <CheckOutlined style={{ color: '#52c41a' }} />
        ) : (
          <CloseOutlined style={{ color: '#d9d9d9' }} />
        )
      ),
    })),
  ]

  // Build table data
  const tableData = permissions.map((perm) => {
    const row: any = {
      key: perm.name,
      permission: perm.description,
      category: perm.category,
    }

    roles.forEach((role) => {
      row[role.name] = role.permissions.includes(perm.name)
    })

    return row
  })

  // Calculate stats
  const totalPerms = permissions.length
  const totalRoles = roles.length
  const adminPerms = roles.find((r) => r.name === 'super_admin')?.permissions.length || 0

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总权限数"
              value={totalPerms}
              prefix={<SafetyOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="角色数" value={totalRoles} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="超管权限"
              value={adminPerms}
              suffix={`/ ${totalPerms}`}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="权限覆盖率"
              value={totalRoles > 0 ? Math.round((totalPerms / totalPerms) * 100) : 0}
              suffix="%"
            />
          </Card>
        </Col>
      </Row>

      <Card title="权限矩阵" loading={loading}>
        <Table
          columns={columns}
          dataSource={tableData}
          scroll={{ x: 'max-content' }}
          pagination={false}
          size="small"
          rowClassName={(record) => {
            const category = record.category
            const colorMap: Record<string, string> = {
              ticket: '#fff7e6',
              message: '#e6f7ff',
              report: '#f6ffed',
              rule: '#fff0f6',
              settings: '#f9f0ff',
              staff: '#fff1f0',
              admin: '#fff1f0',
            }
            return colorMap[category] || ''
          }}
        />

        <div style={{ marginTop: 24 }}>
          <Title level={5}>角色说明</Title>
          <Space wrap>
            {roles.map((role) => (
              <Tag key={role.name} color={roleColors[role.name]}>
                {roleNames[role.name] || role.name}: {role.permissions.length} 项权限
              </Tag>
            ))}
          </Space>
        </div>

        <div style={{ marginTop: 16 }}>
          <Title level={5}>权限分类</Title>
          <Space direction="vertical" size="small">
            {Object.entries(groupedPermissions).map(([category, perms]) => (
              <div key={category}>
                <Text strong>{category.toUpperCase()}:</Text>
                <Space wrap style={{ marginLeft: 8 }}>
                  {perms.map((perm) => (
                    <Tag key={perm.name}>{perm.description}</Tag>
                  ))}
                </Space>
              </div>
            ))}
          </Space>
        </div>
      </Card>
    </div>
  )
}
