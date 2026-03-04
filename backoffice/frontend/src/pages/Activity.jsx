import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'
import { activityAPI } from '../services/api'
import { Search } from 'lucide-react'

const Activity = () => {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)

  useEffect(() => {
    fetchLogs()
  }, [page])

  const fetchLogs = async () => {
    try {
      setLoading(true)
      const response = await activityAPI.getLogs({ page, limit: 50 })
      setLogs(response.data.logs || [])
      setTotal(response.data.total || 0)
    } catch (error) {
      console.error('Error fetching activity logs:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Activity Logs</h1>
        <p className="text-muted-foreground">View all admin activities</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Activity Log</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading logs...</div>
          ) : logs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No activity logs found
            </div>
          ) : (
            <div className="space-y-4">
              <div className="text-sm text-muted-foreground">
                Showing {logs.length} of {total} logs
              </div>
              <div className="space-y-2">
                {logs.map((log) => (
                  <div
                    key={log.id}
                    className="p-4 border rounded-lg hover:bg-accent"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-medium">{log.action_type}</div>
                        <div className="text-sm text-muted-foreground">
                          {log.target_type} #{log.target_id} • {log.created_at}
                        </div>
                        {log.details && (
                          <div className="text-sm text-muted-foreground mt-1">
                            {JSON.stringify(log.details)}
                          </div>
                        )}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {log.ip_address}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default Activity
