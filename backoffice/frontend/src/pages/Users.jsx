import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'
import { usersAPI } from '../services/api'
import { Search, Crown, UserPlus } from 'lucide-react'
import UserDetailModal from '../components/UserDetailModal'

const Users = () => {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [error, setError] = useState(null)
  const [selectedUserId, setSelectedUserId] = useState(null)
  const limit = 50

  // Enterprise assignment state
  const [enterpriseEmail, setEnterpriseEmail] = useState('')
  const [enterpriseLoading, setEnterpriseLoading] = useState(false)
  const [enterpriseResult, setEnterpriseResult] = useState(null)

  const [provisionEmail, setProvisionEmail] = useState('')
  const [provisionName, setProvisionName] = useState('')
  const [provisionLoading, setProvisionLoading] = useState(false)
  const [provisionResult, setProvisionResult] = useState(null)

  useEffect(() => {
    fetchUsers()
  }, [page, search])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await usersAPI.getAll({
        page,
        limit,
        search: search || undefined,
      })
      setUsers(response.data.users || [])
      setTotal(response.data.total || 0)
    } catch (error) {
      console.error('Error fetching users:', error)
      setError(error.response?.data?.detail || error.message || 'Failed to fetch users. Check database connection and configuration.')
      setUsers([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }

  const handleRowClick = (userId) => {
    setSelectedUserId(userId)
  }

  const handleModalClose = () => {
    setSelectedUserId(null)
  }

  const handleUserUpdated = () => {
    // Refresh the user list when an action is performed in the modal
    fetchUsers()
  }

  const handleProvisionMainApp = async () => {
    if (!provisionEmail.trim()) return
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(provisionEmail.trim())) {
      setProvisionResult({ type: 'error', message: 'Please enter a valid email address.' })
      return
    }
    try {
      setProvisionLoading(true)
      setProvisionResult(null)
      const body = {
        email: provisionEmail.trim(),
        ...(provisionName.trim() ? { full_name: provisionName.trim() } : {}),
      }
      const { data } = await usersAPI.provisionMainApp(body)
      setProvisionResult({
        type: 'success',
        message: data?.message || 'User created.',
        detail: {
          username: data?.username,
          email: data?.email,
          temporary_password: data?.temporary_password,
          user_id: data?.user_id,
        },
      })
      setProvisionEmail('')
      setProvisionName('')
      fetchUsers()
    } catch (err) {
      setProvisionResult({
        type: 'error',
        message: err.response?.data?.detail || err.message || 'Failed to create main app user.',
      })
    } finally {
      setProvisionLoading(false)
    }
  }

  const handleAssignEnterprise = async () => {
    if (!enterpriseEmail.trim()) return
    // Basic email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(enterpriseEmail.trim())) {
      setEnterpriseResult({ type: 'error', message: 'Please enter a valid email address.' })
      return
    }
    try {
      setEnterpriseLoading(true)
      setEnterpriseResult(null)
      const response = await usersAPI.assignEnterprise(enterpriseEmail.trim())
      setEnterpriseResult({ type: 'success', message: response.data?.message || 'Enterprise plan assigned successfully.' })
      setEnterpriseEmail('')
      fetchUsers() // Refresh user list
    } catch (err) {
      setEnterpriseResult({
        type: 'error',
        message: err.response?.data?.detail || err.message || 'Failed to assign enterprise plan.'
      })
    } finally {
      setEnterpriseLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">User Management</h1>
        <p className="text-muted-foreground">Manage all platform users</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UserPlus className="h-5 w-5 text-primary" />
            Create main app user
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Adds an account in the <strong>main ZedReq</strong> database so the person can sign in on the main product
            with this email and a generated password. This does <strong>not</strong> create backoffice admin access.
            <span className="block mt-1 text-xs text-amber-600 dark:text-amber-400">
              Super admin only. Copy the password now — it is only shown once.
            </span>
          </p>
          <div className="flex flex-col gap-3 max-w-lg">
            <Input
              type="email"
              placeholder="Email (main app login)"
              value={provisionEmail}
              onChange={(e) => setProvisionEmail(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') handleProvisionMainApp() }}
            />
            <Input
              type="text"
              placeholder="Display name (optional)"
              value={provisionName}
              onChange={(e) => setProvisionName(e.target.value)}
            />
            <div>
              <Button
                onClick={handleProvisionMainApp}
                disabled={provisionLoading || !provisionEmail.trim()}
              >
                {provisionLoading ? 'Creating…' : 'Create main app user'}
              </Button>
            </div>
          </div>
          {provisionResult && (
            <div
              className={`mt-3 rounded-lg px-4 py-3 text-sm space-y-2 ${
                provisionResult.type === 'success'
                  ? 'bg-green-100 text-green-900 dark:bg-green-900/30 dark:text-green-300'
                  : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
              }`}
            >
              <div>{provisionResult.message}</div>
              {provisionResult.type === 'success' && provisionResult.detail && (
                <div className="font-mono text-xs space-y-1 border-t border-green-200/50 dark:border-green-700/50 pt-2 mt-2">
                  <div>User ID: {provisionResult.detail.user_id}</div>
                  <div>Username: {provisionResult.detail.username}</div>
                  <div>Email: {provisionResult.detail.email}</div>
                  <div className="break-all">
                    Temporary password: {provisionResult.detail.temporary_password}
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Assign Enterprise Plan Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Crown className="h-5 w-5 text-amber-500" />
            Assign Enterprise Plan
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Manually assign the Enterprise subscription plan to a registered user by email.
            This grants unlimited AI messages, course enrollments, and extended interview sessions.
            <span className="block mt-1 text-xs text-amber-600 dark:text-amber-400">Requires Super Admin privileges.</span>
          </p>
          <div className="flex items-center gap-3">
            <Input
              type="email"
              placeholder="user@example.com"
              value={enterpriseEmail}
              onChange={(e) => setEnterpriseEmail(e.target.value)}
              className="max-w-md"
              onKeyDown={(e) => { if (e.key === 'Enter') handleAssignEnterprise() }}
            />
            <Button
              onClick={handleAssignEnterprise}
              disabled={enterpriseLoading || !enterpriseEmail.trim()}
            >
              {enterpriseLoading ? 'Assigning...' : 'Assign Enterprise'}
            </Button>
          </div>
          {enterpriseResult && (
            <div className={`mt-3 rounded-lg px-4 py-2 text-sm ${
              enterpriseResult.type === 'success'
                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
            }`}>
              {enterpriseResult.message}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Users</CardTitle>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search users..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading users...
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <div className="text-destructive font-medium mb-2">Error loading users</div>
              <div className="text-sm text-muted-foreground">{error}</div>
              <Button 
                onClick={fetchUsers} 
                className="mt-4"
                variant="outline"
              >
                Retry
              </Button>
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No users found
            </div>
          ) : (
            <div className="space-y-4">
              <div className="text-sm text-muted-foreground">
                Showing {users.length} of {total} users
              </div>
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-4 font-medium">ID</th>
                      <th className="text-left p-4 font-medium">Username</th>
                      <th className="text-left p-4 font-medium">Email</th>
                      <th className="text-left p-4 font-medium">Name</th>
                      <th className="text-left p-4 font-medium">Plan</th>
                      <th className="text-left p-4 font-medium">Status</th>
                      <th className="text-left p-4 font-medium">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr
                        key={user.id}
                        className="border-b hover:bg-accent cursor-pointer transition-colors"
                        onClick={() => handleRowClick(user.id)}
                      >
                        <td className="p-4">{user.id}</td>
                        <td className="p-4 font-medium">{user.username}</td>
                        <td className="p-4 text-muted-foreground">{user.email}</td>
                        <td className="p-4">{user.full_name}</td>
                        <td className="p-4">
                          <span className={`px-2 py-1 rounded text-xs ${
                            user.subscription_plan === 'enterprise' ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400' :
                            user.subscription_plan === 'premium' ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400' :
                            user.subscription_plan === 'pro' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400' :
                            'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                          }`}>
                            {user.subscription_plan || 'free'}
                          </span>
                        </td>
                        <td className="p-4">
                          <span className={`px-2 py-1 rounded text-xs ${
                            user.subscription_status === 'active'
                              ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                              : user.subscription_status === 'cancelled'
                              ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                              : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                          }`}>
                            {user.subscription_status}
                          </span>
                        </td>
                        <td className="p-4 text-sm text-muted-foreground">
                          {user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {total > limit && (
                <div className="flex justify-between items-center">
                  <Button
                    variant="outline"
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    Previous
                  </Button>
                  <span className="text-sm text-muted-foreground">
                    Page {page} of {Math.ceil(total / limit)}
                  </span>
                  <Button
                    variant="outline"
                    onClick={() => setPage(p => p + 1)}
                    disabled={page >= Math.ceil(total / limit)}
                  >
                    Next
                  </Button>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* User Detail Modal */}
      {selectedUserId && (
        <UserDetailModal
          userId={selectedUserId}
          onClose={handleModalClose}
          onUserUpdated={handleUserUpdated}
        />
      )}
    </div>
  )
}

export default Users
