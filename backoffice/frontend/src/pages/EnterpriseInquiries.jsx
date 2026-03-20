import React, { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { enterpriseInquiriesAPI } from '../services/api'

const STATUS_OPTIONS = [
  { value: '', label: 'All statuses' },
  { value: 'new', label: 'New' },
  { value: 'contacted', label: 'Contacted' },
  { value: 'closed', label: 'Closed' },
]

const EnterpriseInquiries = () => {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [pages, setPages] = useState(0)
  const [statusFilter, setStatusFilter] = useState('')
  const [updatingId, setUpdatingId] = useState(null)

  const fetchList = useCallback(async () => {
    setError('')
    try {
      setLoading(true)
      const params = { page, limit: 50 }
      if (statusFilter) params.status = statusFilter
      const { data } = await enterpriseInquiriesAPI.list(params)
      setItems(data.items || [])
      setTotal(data.total || 0)
      setPages(data.pages || 0)
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.message ||
        'Failed to load inquiries'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
      setItems([])
    } finally {
      setLoading(false)
    }
  }, [page, statusFilter])

  useEffect(() => {
    fetchList()
  }, [fetchList])

  const setStatus = async (id, nextStatus) => {
    try {
      setUpdatingId(id)
      await enterpriseInquiriesAPI.updateStatus(id, nextStatus)
      await fetchList()
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        err.message ||
        'Update failed'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setUpdatingId(null)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Enterprise inquiries</h1>
        <p className="text-muted-foreground">
          Work emails and leads submitted from the app enterprise flow
        </p>
      </div>

      {error && (
        <div
          className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive"
          role="alert"
        >
          {error}
        </div>
      )}

      <Card>
        <CardHeader className="flex flex-row flex-wrap items-end justify-between gap-4">
          <CardTitle>Requests</CardTitle>
          <div className="flex items-center gap-2">
            <label htmlFor="ent-status-filter" className="text-sm text-muted-foreground">
              Status
            </label>
            <select
              id="ent-status-filter"
              className="rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={statusFilter}
              onChange={(e) => {
                setPage(1)
                setStatusFilter(e.target.value)
              }}
            >
              {STATUS_OPTIONS.map((o) => (
                <option key={o.value || 'all'} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading…</div>
          ) : items.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No enterprise inquiries yet
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Page {page} of {pages || 1} — {total} total
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-muted-foreground">
                      <th className="pb-2 pr-4 font-medium">Date</th>
                      <th className="pb-2 pr-4 font-medium">Contact email</th>
                      <th className="pb-2 pr-4 font-medium">User</th>
                      <th className="pb-2 pr-4 font-medium">Account email</th>
                      <th className="pb-2 pr-4 font-medium">Status</th>
                      <th className="pb-2 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.map((row) => (
                      <tr key={row.id} className="border-b border-border/60">
                        <td className="py-3 pr-4 whitespace-nowrap text-muted-foreground">
                          {row.created_at
                            ? new Date(row.created_at).toLocaleString()
                            : '—'}
                        </td>
                        <td className="py-3 pr-4 font-medium">{row.contact_email}</td>
                        <td className="py-3 pr-4">
                          <span className="text-muted-foreground">#{row.user_id}</span>
                          {row.username ? ` ${row.username}` : ''}
                        </td>
                        <td className="py-3 pr-4 text-muted-foreground">
                          {row.user_email || '—'}
                        </td>
                        <td className="py-3 pr-4">
                          <span className="rounded-full bg-secondary px-2 py-0.5 text-xs capitalize">
                            {row.status}
                          </span>
                        </td>
                        <td className="py-3">
                          <div className="flex flex-wrap gap-1">
                            {row.status !== 'contacted' && (
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                disabled={updatingId === row.id}
                                onClick={() => setStatus(row.id, 'contacted')}
                              >
                                Contacted
                              </Button>
                            )}
                            {row.status !== 'closed' && (
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                disabled={updatingId === row.id}
                                onClick={() => setStatus(row.id, 'closed')}
                              >
                                Closed
                              </Button>
                            )}
                            {row.status !== 'new' && (
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                disabled={updatingId === row.id}
                                onClick={() => setStatus(row.id, 'new')}
                              >
                                Mark new
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {pages > 1 && (
                <div className="flex gap-2 pt-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    disabled={page <= 1}
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                  >
                    Previous
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    disabled={page >= pages}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    Next
                  </Button>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default EnterpriseInquiries
