import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { analyticsAPI } from '../services/api'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const CashFlow = () => {
  const [cashFlowData, setCashFlowData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const response = await analyticsAPI.getCashFlow()
      setCashFlowData(response.data)
    } catch (error) {
      console.error('Error fetching cash flow data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading...</div>
  }

  // Prepare chart data
  const chartData = cashFlowData?.revenue?.revenue_by_period?.map((rev) => {
    const cost = cashFlowData?.costs?.costs_by_category?.find(
      (c) => c.period === rev.period
    )
    return {
      period: rev.period,
      revenue: rev.total,
      costs: cost?.total || 0,
      net: rev.total - (cost?.total || 0),
    }
  }) || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Cash Flow Analysis</h1>
        <p className="text-muted-foreground">Revenue vs costs and profitability</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Total Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              ${cashFlowData?.revenue?.total_revenue?.toLocaleString() || '0'}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Total Costs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              ${cashFlowData?.costs?.total_costs?.toLocaleString() || '0'}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Net Cash Flow</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              ${cashFlowData?.net_cash_flow?.toLocaleString() || '0'}
            </div>
            <div className="text-sm text-muted-foreground">
              {cashFlowData?.profit_margin?.toFixed(2) || '0'}% margin
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Cash Flow Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#0088FE"
                name="Revenue"
              />
              <Line
                type="monotone"
                dataKey="costs"
                stroke="#FF8042"
                name="Costs"
              />
              <Line
                type="monotone"
                dataKey="net"
                stroke="#00C49F"
                name="Net Profit"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}

export default CashFlow
