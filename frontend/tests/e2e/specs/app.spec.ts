/**
 * E2E Tests for InConnect Frontend
 *
 * Using Playwright for browser automation
 */

import { test, expect } from '@playwright/test'

// Test data
const TEST_USER = {
  username: 'test_user',
  password: 'test_password',
}

test.describe('Authentication', () => {
  test('should login successfully', async ({ page }) => {
    await page.goto('http://localhost:3000/login')

    await page.fill('input[name="username"]', TEST_USER.username)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('button[type="submit"]')

    await expect(page).toHaveURL('http://localhost:3000/')
    await expect(page.locator('text=工作台')).toBeVisible()
  })

  test('should show error on invalid credentials', async ({ page }) => {
    await page.goto('http://localhost:3000/login')

    await page.fill('input[name="username"]', 'invalid')
    await page.fill('input[name="password"]', 'invalid')
    await page.click('button[type="submit"]')

    await expect(page.locator('text=用户名或密码错误')).toBeVisible()
  })
})

test.describe('Ticket Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="username"]', TEST_USER.username)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('button[type="submit"]')
    await page.waitForURL('http://localhost:3000/')
  })

  test('should create a new ticket', async ({ page }) => {
    await page.click('text=工单管理')
    await page.waitForURL('http://localhost:3000/tickets')

    await page.click('button:has-text("新建工单")')

    // Fill ticket form
    await page.fill('input[name="title"]', 'E2E测试工单')
    await page.selectOption('select[name="category"]', 'maintenance')
    await page.selectOption('select[name="priority"]', 'P2')
    await page.fill('textarea[name="description"]', '这是一个E2E自动化测试创建的工单')

    await page.click('button:has-text("提交")')

    // Verify success
    await expect(page.locator('text=创建成功')).toBeVisible()
  })

  test('should filter tickets by status', async ({ page }) => {
    await page.click('text=工单管理')
    await page.waitForURL('http://localhost:3000/tickets')

    // Select pending status
    await page.click('select[placeholder="状态筛选"]')
    await page.click('text=待处理')

    // Verify filter applied
    const tickets = page.locator('table tbody tr')
    const count = await tickets.count()

    for (let i = 0; i < count; i++) {
      await expect(tickets.nth(i)).toContainText('待处理')
    }
  })

  test('should batch assign tickets', async ({ page }) => {
    await page.click('text=工单管理')
    await page.waitForURL('http://localhost:3000/tickets')

    // Select multiple tickets
    await page.locator('input[type="checkbox"]').first().check()
    await page.locator('input[type="checkbox"]').nth(1).check()

    // Click batch operations dropdown
    await page.click('button:has-text("批量操作")')
    await page.click('text=批量分配')

    // Select staff
    await page.click('.ant-modal input[placeholder*="请选择"]')
    await page.click('text=张三')

    // Verify assignment
    await expect(page.locator('text=成功分配')).toBeVisible()
  })
})

test.describe('Message Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="username"]', TEST_USER.username)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('button[type="submit"]')
    await page.waitForURL('http://localhost:3000/')
  })

  test('should view conversations and send message', async ({ page }) => {
    await page.click('text=消息管理')
    await page.waitForURL('http://localhost:3000/messages')

    // Click on first conversation
    await page.locator('table tbody tr').first().click()

    // Should navigate to chat page
    await page.waitForURL('http://localhost:3000/messages/*')

    // Send message
    await page.fill('textarea[placeholder*="输入消息"]', '您好，有什么可以帮助您的吗？')
    await page.click('button:has-text("发送")')

    // Verify message sent
    await expect(page.locator('text=您好，有什么可以帮助您的吗？')).toBeVisible()
  })

  test('should search message history', async ({ page }) => {
    await page.click('text=消息管理')
    await page.waitForURL('http://localhost:3000/messages')

    // Click on message history link
    await page.click('text=消息历史')

    // Search for keyword
    await page.fill('input[placeholder*="搜索消息"]', '空调')
    await page.click('button:has-text("搜索")')

    // Verify search results
    const results = page.locator('table tbody tr')
    const count = await results.count()
    expect(count).toBeGreaterThan(0)
  })
})

test.describe('Reports & Analytics', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="username"]', TEST_USER.username)
    await page.fill('input[name="password"]', TEST_USER.password)
    await page.click('button[type="submit"]')
  })

  test('should view dashboard report', async ({ page }) => {
    await page.click('text=数据报表')

    // Dashboard tab should be visible
    await expect(page.locator('text=仪表盘')).toBeVisible()

    // Check statistics cards
    await expect(page.locator('text=总工单')).toBeVisible()
    await expect(page.locator('text=待处理')).toBeVisible()
    await expect(page.locator('text=超时工单')).toBeVisible()
  })

  test('should view ticket report', async ({ page }) => {
    await page.click('text=数据报表')

    // Click on ticket report tab
    await page.click('text=工单报表')

    // Verify charts and stats
    await expect(page.locator('text=工单状态分布')).toBeVisible()
    await expect(page.locator('text=工单优先级分布')).toBeVisible()
  })

  test('should change time range', async ({ page }) => {
    await page.click('text=数据报表')

    // Change time range
    await page.click('select:has-text("本周")')
    await page.click('text=本月')

    // Verify data refreshed
    await expect(page.locator('text=本月')).toBeVisible()
  })
})

test.describe('Settings Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'admin_password')
    await page.click('button[type="submit"]')
  })

  test('should configure ticket categories', async ({ page }) => {
    await page.click('text=系统设置')

    // Click on categories tab
    await page.click('text=工单分类')

    // Update a category
    await page.fill('input[placeholder*="名称"]', '维修服务', { timeout: 5000 })

    // Save configuration
    await page.click('button:has-text("保存配置")')

    // Verify success
    await expect(page.locator('text=保存成功')).toBeVisible()
  })

  test('should view permission matrix', async ({ page }) => {
    await page.click('text=系统设置')

    // Click on permissions tab
    await page.click('text=权限矩阵')

    // Verify permission table
    await expect(page.locator('text=超管')).toBeVisible()
    await expect(page.locator('text=店长')).toBeVisible()
    await expect(page.locator('text=员工')).toBeVisible()
  })
})

test.describe('Rule Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000/login')
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'admin_password')
    await page.click('button[type="submit"]')
  })

  test('should create and test routing rule', async ({ page }) => {
    await page.click('text=规则管理')

    // Create new rule
    await page.click('button:has-text("新建规则")')

    // Fill rule form
    await page.fill('input[name="name"]', 'Wi-Fi咨询规则')
    await page.selectOption('select[name="rule_type"]', 'keyword')
    await page.fill('textarea[name="keywords"]', 'Wi-Fi\nwifi\n网络')

    // Select staff
    await page.click('div:has-text("分配员工")')
    await page.click('.ant-select-dropdown-option:has-text("前台接待")')

    // Save
    await page.click('button:has-text("确定")')

    // Test the rule
    await page.click('text=规则测试')

    // Enter test message
    await page.fill('textarea[placeholder*="测试消息"]', '请问房间Wi-Fi密码是多少？')
    await page.click('button:has-text("运行测试")')

    // Verify test result
    await expect(page.locator('text=匹配规则')).toBeVisible()
  })
})
