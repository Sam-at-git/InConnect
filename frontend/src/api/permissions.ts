/**
 * Permissions API
 */

import apiClient, { APIResponse } from './client'

export interface Permission {
  name: string
  category: string
  description: string
}

export interface Role {
  name: string
  display_name: string
  permissions: string[]
}

export interface PermissionCheck {
  permission: string
  role: string
  has_permission: boolean
  error?: string
}

export interface PermissionMatrix {
  [roleName: string]: string[]
}

export const permissionsApi = {
  // List all permissions
  list: async () => {
    const response = await apiClient.get<APIResponse<Permission[]>>('/permissions/list')
    return response.data
  },

  // List all roles
  listRoles: async () => {
    const response = await apiClient.get<APIResponse<Role[]>>('/permissions/roles')
    return response.data
  },

  // Check permission for role
  check: async (permission: string, role: string) => {
    const response = await apiClient.get<APIResponse<PermissionCheck>>('/permissions/check', {
      params: { permission, role },
    })
    return response.data
  },

  // Get permission matrix
  getMatrix: async () => {
    const response = await apiClient.get<APIResponse<PermissionMatrix>>('/permissions/matrix')
    return response.data
  },

  // Get staff permissions
  getStaffPermissions: async (staffId: string) => {
    const response = await apiClient.get<APIResponse<{
      staff_id: string
      staff_name: string
      role: string
      department: string | null
      permissions: string[]
    }>>(`/permissions/staff/${staffId}`)
    return response.data
  },
}
