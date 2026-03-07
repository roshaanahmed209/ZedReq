import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { analyticsAPI, monitoringApi } from '../services/api'
import { 
  DollarSign, 
  TrendingDown, 
  TrendingUp, 
  Users, 
  Server,
  Activity,
  AlertCircle,
  Zap,
  Clock
} from 'lucide-react'
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await analyticsAPI.getDashboard()
      setDashboardData(response.data)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return ''
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    } catch {
      return dateString
    }
  }

  // Format currency
  const formatCurrency = (amount) => {
    if (amount === null || amount === undefined) return '$0'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  // Format number with K/M suffixes
  const formatNumber = (num) => {
    if (num === null || num === undefined) return '0'
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
    return num.toString()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Loading dashboard...</div>
      </div>
    )
  }

  if (!dashboardData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-destructive">Failed to load dashboard data</div>
      </div>
    )
  }

  const revenueData = dashboardData.revenue?.over_time || []
  const costData = dashboardData.costs?.by_category || []
  const subscriptions = dashboardData.subscriptions || {}
  const trialConversion = dashboardData.trial_conversion || {}
  const devops = dashboardData.devops || {}
  
  // Prepare revenue chart data with formatted dates
  const revenueChartData = revenueData.map(item => ({
    ...item,
    date: formatDate(item.timestamp || item.date),
    revenue: item.revenue || 0
  }))

  // Prepare plan distribution data
  const plansBreakdown = subscriptions.plans_breakdown || {}
  const planDistributionData = Object.entries(plansBreakdown).map(([plan, data]) => ({
    name: plan.charAt(0).toUpperCase() + plan.slice(1),
    value: typeof data === 'object' ? data.active || data.total || 0 : data,
    total: typeof data === 'object' ? data.total || 0 : data
  }))

  // Prepare trial conversion funnel data
  const trialFunnelData = [
    { name: 'Trial Started', value: trialConversion.trial_taken || 0 },
    { name: 'Converted', value: trialConversion.trial_converted || 0 },
    { name: 'Not Converted', value: trialConversion.trial_not_converted || 0 }
  ]

  // Prepare revenue vs costs chart
  const revenueVsCostsData = revenueChartData.map((item, index) => {
    const costItem = costData[index] || { total: 0 }
    return {
      date: item.date,
      revenue: item.revenue || 0,
      costs: costItem.total || 0
    }
  })

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d']

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Comprehensive overview of platform metrics and DevOps analytics</p>
      </div>

      {/* ============================================
          USER & REVENUE DASHBOARD SECTION
          ============================================ */}
      <div className="space-y-6">
        <div className="border-b border-border pb-2">
          <h2 className="text-2xl font-semibold">User & Revenue Dashboard</h2>
          <p className="text-sm text-muted-foreground">Financial metrics, user analytics, and subscription data</p>
        </div>

        {/* Financial Metrics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(dashboardData.revenue?.total || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              {dashboardData.revenue?.transactions || 0} transactions
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Costs</CardTitle>
            <TrendingDown className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(dashboardData.costs?.total || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Across all categories
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Net Profit</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(dashboardData.cash_flow?.net || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              {dashboardData.cash_flow?.profit_margin?.toFixed(1) || '0'}% margin
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Subscriptions</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {subscriptions.active_subscriptions || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              {formatCurrency(subscriptions.mrr || 0)} MRR
            </p>
          </CardContent>
        </Card>
      </div>

      {/* User Metrics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(subscriptions.total_users || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              All registered users
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Paid Users</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(subscriptions.paid_users || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              {subscriptions.total_users > 0 
                ? ((subscriptions.paid_users / subscriptions.total_users) * 100).toFixed(1)
                : '0'}% of total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Free Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(subscriptions.free_users || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Non-paying users
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {subscriptions.conversion_rate?.toFixed(1) || '0'}%
            </div>
            <p className="text-xs text-muted-foreground">
              Trial to paid conversion
            </p>
          </CardContent>
        </Card>
      </div>

        {/* Charts Section - User & Revenue */}
        <div className="grid gap-4 md:grid-cols-2">
          {/* Revenue Over Time */}
          <Card>
            <CardHeader>
              <CardTitle>Revenue Over Time</CardTitle>
              <CardDescription>Revenue trends with proper date formatting</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={revenueChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis />
                  <Tooltip 
                    formatter={(value) => formatCurrency(value)}
                    labelFormatter={(label) => `Date: ${label}`}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="revenue"
                    stroke="#0088FE"
                    name="Revenue"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Cost Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Cost Breakdown</CardTitle>
              <CardDescription>Costs by category</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={costData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) =>
                      `${name} ${(percent * 100).toFixed(0)}%`
                    }
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="total"
                  >
                    {costData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => formatCurrency(value)} />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Users by Plan Type */}
          <Card>
            <CardHeader>
              <CardTitle>Users by Plan Type</CardTitle>
              <CardDescription>Distribution of users across subscription plans</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={planDistributionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#0088FE" name="Active Users" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Trial Conversion Funnel */}
          <Card>
            <CardHeader>
              <CardTitle>Trial Conversion Funnel</CardTitle>
              <CardDescription>Users who took trial but did not continue</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={trialFunnelData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#FF8042" name="Users" />
                </BarChart>
              </ResponsiveContainer>
              <div className="mt-4 text-sm text-muted-foreground">
                <p>Conversion Rate: {trialConversion.conversion_rate?.toFixed(1) || '0'}%</p>
                <p>Trial Taken: {trialConversion.trial_taken || 0}</p>
                <p>Converted: {trialConversion.trial_converted || 0}</p>
                <p>Not Converted: {trialConversion.trial_not_converted || 0}</p>
              </div>
            </CardContent>
          </Card>

          {/* Revenue vs Costs Over Time */}
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Revenue vs Costs Over Time</CardTitle>
              <CardDescription>Financial performance comparison</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={revenueVsCostsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis yAxisId="left" />
                  <YAxis yAxisId="right" orientation="right" />
                  <Tooltip 
                    formatter={(value) => formatCurrency(value)}
                    labelFormatter={(label) => `Date: ${label}`}
                  />
                  <Legend />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="revenue"
                    stroke="#0088FE"
                    name="Revenue"
                    strokeWidth={2}
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="costs"
                    stroke="#FF8042"
                    name="Costs"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* ============================================
          DEVOPS & TECHNICAL DASHBOARD SECTION
          ============================================ */}
      <div className="space-y-6">
        <div className="border-b border-border pb-2">
          <h2 className="text-2xl font-semibold">DevOps & Technical Dashboard</h2>
          <p className="text-sm text-muted-foreground">Infrastructure monitoring, performance metrics, and system health</p>
        </div>

        {/* DevOps Metrics Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Uptime</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {devops.uptime?.uptime_percent?.toFixed(2) || '0'}%
            </div>
            <p className="text-xs text-muted-foreground">
              Last 30 days
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(devops.users?.active_users || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Real-time active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">DAU</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(devops.users?.dau || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Daily active users
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Error Rate</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {devops.errors?.total_errors || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Last 7 days
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Response</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {devops.performance?.avg_response_time_ms 
                ? Math.round(devops.performance.avg_response_time_ms) + 'ms'
                : '0ms'}
            </div>
            <p className="text-xs text-muted-foreground">
              API response time
            </p>
          </CardContent>
        </Card>
      </div>

        {/* Infrastructure Metrics Section */}
        {(devops.infrastructure?.cpu_avg || devops.infrastructure?.ram_avg) && (
          <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">CPU Usage</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {devops.infrastructure.cpu_avg?.toFixed(1) || '0'}%
              </div>
              <p className="text-xs text-muted-foreground">
                Max: {devops.infrastructure.cpu_max?.toFixed(1) || '0'}%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">RAM Usage</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {devops.infrastructure.ram_avg?.toFixed(1) || '0'}%
              </div>
              <p className="text-xs text-muted-foreground">
                Max: {devops.infrastructure.ram_max?.toFixed(1) || '0'}%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Disk Usage</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {devops.infrastructure.disk_avg?.toFixed(1) || '0'}%
              </div>
              <p className="text-xs text-muted-foreground">
                Max: {devops.infrastructure.disk_max?.toFixed(1) || '0'}%
              </p>
            </CardContent>
          </Card>
        </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard
