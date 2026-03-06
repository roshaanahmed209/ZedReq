import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { monitoringApi } from '../services/api'

export default function Monitoring() {
  const [uptime, setUptime] = useState(null)
  const [infrastructure, setInfrastructure] = useState(null)
  const [performance, setPerformance] = useState(null)
  const [users, setUsers] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [uptimeRes, infraRes, perfRes, usersRes] = await Promise.all([
        monitoringApi.getUptime(30),
        monitoringApi.getInfrastructure(24),
        monitoringApi.getPerformance(24),
        monitoringApi.getUsers(30)
      ])
      
      setUptime(uptimeRes.data)
      setInfrastructure(infraRes.data)
      setPerformance(perfRes.data)
      setUsers(usersRes.data)
    } catch (error) {
      console.error('Error loading monitoring data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="p-6">Loading monitoring data...</div>
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Monitoring Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Uptime</CardTitle>
          </CardHeader>
          <CardContent>
            {uptime && (
              <div className="text-2xl font-bold">
                {uptime.uptime_percent?.toFixed(2)}%
              </div>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Active Users</CardTitle>
          </CardHeader>
          <CardContent>
            {users && (
              <div className="text-2xl font-bold">{users.active_users || 0}</div>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>CPU Usage</CardTitle>
          </CardHeader>
          <CardContent>
            {infrastructure && (
              <div className="text-2xl font-bold">
                {infrastructure.cpu_avg?.toFixed(1)}%
              </div>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Error Rate</CardTitle>
          </CardHeader>
          <CardContent>
            {performance && (
              <div className="text-2xl font-bold">
                {performance.error_rate?.toFixed(2)}%
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
