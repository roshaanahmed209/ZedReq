import React, { useState, useEffect } from 'react'
import { usersAPI } from '../services/api'
import { Button } from './ui/button'
import { Input } from './ui/input'
import {
  X, User, CreditCard, Shield, LogOut, Download, Bell,
  Trash2, Ban, CheckCircle, Key, Lock, ArrowUpCircle, Activity
} from 'lucide-react'

// Two-step confirmation wrapper for destructive actions
const ConfirmAction = ({ label, icon: Icon, variant, onConfirm, disabled, className, title }) => {
  const [confirming, setConfirming] = useState(false)

  if (confirming) {
    return (
      <div className="flex items-center gap-2" title={title}>
        <span className="text-sm text-muted-foreground">Are you sure?</span>
        <Button
          size="sm"
          variant="destructive"
          onClick={() => { onConfirm(); setConfirming(false) }}
          disabled={disabled}
          title={title}
        >
          Confirm
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => setConfirming(false)}
        >
          Cancel
        </Button>
      </div>
    )
  }

  return (
    <Button
      size="sm"
      variant={variant || 'outline'}
      onClick={() => setConfirming(true)}
      disabled={disabled}
      className={className}
      title={title}
    >
      {Icon && <Icon className="h-4 w-4 mr-2" />}
      {label}
    </Button>
  )
}

const UserDetailModal = ({ userId, onClose, onUserUpdated }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [actionLoading, setActionLoading] = useState(null)
  const [actionResult, setActionResult] = useState(null)

  // Form states
  const [selectedPlan, setSelectedPlan] = useState('')
  const [reason, setReason] = useState('')
  const [notifySubject, setNotifySubject] = useState('')
  const [notifyMessage, setNotifyMessage] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [showResetForm, setShowResetForm] = useState(false)

  useEffect(() => {
    fetchUser()
  }, [userId])

  const fetchUser = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await usersAPI.getById(userId)
      setUser(response.data)
      setSelectedPlan(response.data?.subscription?.plan || 'free')
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load user details')
    } finally {
      setLoading(false)
    }
  }

  const handleAction = async (actionName, apiCall) => {
    try {
      setActionLoading(actionName)
      setActionResult(null)
      const response = await apiCall()
      setActionResult({ type: 'success', message: response.data?.message || 'Action completed' })
      // Refresh user data after action
      await fetchUser()
      if (onUserUpdated) onUserUpdated()
    } catch (err) {
      setActionResult({
        type: 'error',
        message: err.response?.data?.detail || err.message || 'Action failed'
      })
    } finally {
      setActionLoading(null)
    }
  }

  const handleDeleteUser = async () => {
    try {
      setActionLoading('delete')
      setActionResult(null)
      const response = await usersAPI.delete(userId, 'Admin deletion')
      let message = response.data?.message || 'Account deleted'
      if (response.data?.email_sent === true) {
        message += ' A confirmation email was sent to the user.'
      } else if (response.data?.email_sent === false) {
        message += ' Notification email was not sent (configure SMTP in backoffice .env).'
      }
      setUser(null)
      setActionResult({ type: 'success', message })
      if (onUserUpdated) onUserUpdated()
      setTimeout(() => onClose(), 2000)
    } catch (err) {
      setActionResult({
        type: 'error',
        message: err.response?.data?.detail || err.message || 'Delete failed'
      })
    } finally {
      setActionLoading(null)
    }
  }

  const handleExport = async () => {
    try {
      setActionLoading('export')
      setActionResult(null)
      const response = await usersAPI.exportData(userId)
      // Trigger download
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `user_${userId}_export.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      setActionResult({ type: 'success', message: 'User data exported' })
    } catch (err) {
      setActionResult({
        type: 'error',
        message: err.response?.data?.detail || err.message || 'Export failed'
      })
    } finally {
      setActionLoading(null)
    }
  }

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/50 z-40" onClick={onClose} />

      {/* Slide-over panel */}
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-lg bg-card border-l border-border shadow-xl overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-card border-b border-border px-6 py-4 flex items-center justify-between z-10">
          <h2 className="text-xl font-bold">User Management</h2>
          <Button variant="ghost" size="sm" onClick={onClose} className="h-9 w-9 p-0">
            <X className="h-5 w-5" />
          </Button>
        </div>

        <div className="p-6 space-y-6">
          {/* Loading state */}
          {loading && (
            <div className="text-center py-12 text-muted-foreground">Loading user details...</div>
          )}

          {/* Error state */}
          {error && (
            <div className="text-center py-12">
              <div className="text-destructive font-medium mb-2">Error</div>
              <div className="text-sm text-muted-foreground">{error}</div>
              <Button onClick={fetchUser} variant="outline" className="mt-4">Retry</Button>
            </div>
          )}

          {/* Action result toast */}
          {actionResult && (
            <div className={`rounded-lg px-4 py-3 text-sm ${
              actionResult.type === 'success'
                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
            }`}>
              {actionResult.message}
            </div>
          )}

          {user && !loading && (
            <>
              {/* ================= User Info Header ================= */}
              <section className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                    <User className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold">{user.full_name || user.username}</h3>
                    <p className="text-sm text-muted-foreground">@{user.username}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-muted-foreground">Email</span>
                    <p className="font-medium truncate">{user.email}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">User ID</span>
                    <p className="font-medium">{user.id}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Joined</span>
                    <p className="font-medium">
                      {user.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Last Login</span>
                    <p className="font-medium">
                      {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                    </p>
                  </div>
                  {user.profile_url && (
                    <div className="col-span-2">
                      <span className="text-muted-foreground">Profile URL</span>
                      <p className="font-medium text-primary truncate">
                        <a href={user.profile_url} target="_blank" rel="noopener noreferrer">
                          {user.profile_url}
                        </a>
                      </p>
                    </div>
                  )}
                </div>
              </section>

              {/* ================= Subscription Details ================= */}
              <section className="border-t border-border pt-4 space-y-3">
                <div className="flex items-center gap-2">
                  <CreditCard className="h-4 w-4 text-muted-foreground" />
                  <h4 className="font-semibold">Subscription Details</h4>
                </div>

                {user.subscription ? (
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="text-muted-foreground">Plan</span>
                      <p>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                          user.subscription.plan === 'enterprise' ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400' :
                          user.subscription.plan === 'premium' ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400' :
                          user.subscription.plan === 'pro' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400' :
                          'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                        }`}>
                          {user.subscription.plan || 'free'}
                        </span>
                      </p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Status</span>
                      <p>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                          user.subscription.status === 'active'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                            : user.subscription.status === 'cancelled'
                            ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                        }`}>
                          {user.subscription.status || 'inactive'}
                        </span>
                      </p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Start Date</span>
                      <p className="font-medium">
                        {user.subscription.start ? new Date(user.subscription.start).toLocaleDateString() : '-'}
                      </p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">End Date</span>
                      <p className="font-medium">
                        {user.subscription.end ? new Date(user.subscription.end).toLocaleDateString() : '-'}
                      </p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Trial Taken</span>
                      <p className="font-medium">{user.subscription.trial_taken ? 'Yes' : 'No'}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Payment Provider</span>
                      <p className="font-medium">{user.subscription.payment_provider || '-'}</p>
                    </div>
                    {user.subscription.billing_email && (
                      <div className="col-span-2">
                        <span className="text-muted-foreground">Billing Email</span>
                        <p className="font-medium">{user.subscription.billing_email}</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No subscription data available</p>
                )}
              </section>

              {/* ================= User Stats ================= */}
              {user.stats && (
                <section className="border-t border-border pt-4 space-y-3">
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    <h4 className="font-semibold">User Stats</h4>
                  </div>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="text-muted-foreground">Posts</span>
                      <p className="font-medium text-lg">{user.stats.posts || 0}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Connections</span>
                      <p className="font-medium text-lg">{user.stats.connections || 0}</p>
                    </div>
                  </div>
                </section>
              )}

              {/* ================= Actions ================= */}
              <section className="border-t border-border pt-4 space-y-4">
                <h4 className="font-semibold">Actions</h4>

                {/* Upgrade/Change Plan */}
                <div className="space-y-2 p-3 rounded-lg bg-accent/50">
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <ArrowUpCircle className="h-4 w-4" />
                    Change Plan
                  </div>
                  <div className="flex items-center gap-2">
                    <select
                      value={selectedPlan}
                      onChange={(e) => setSelectedPlan(e.target.value)}
                      className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      <option value="free">Free</option>
                      <option value="pro">Pro</option>
                      <option value="premium">Premium</option>
                      <option value="enterprise">Enterprise</option>
                    </select>
                    <Button
                      size="sm"
                      onClick={() => handleAction('changePlan', () => usersAPI.changePlan(userId, selectedPlan))}
                      disabled={actionLoading === 'changePlan' || selectedPlan === (user.subscription?.plan || 'free')}
                    >
                      {actionLoading === 'changePlan' ? 'Updating...' : 'Apply'}
                    </Button>
                  </div>
                  {selectedPlan === 'enterprise' && (
                    <p className="text-xs text-amber-600 dark:text-amber-400">
                      Enterprise plan assignment requires super_admin privileges.
                    </p>
                  )}
                </div>

                {/* Cancel Subscription */}
                {user.subscription?.status === 'active' && (
                  <div className="space-y-2 p-3 rounded-lg bg-accent/50">
                    <div className="flex items-center gap-2 text-sm font-medium">
                      <Ban className="h-4 w-4" />
                      Cancel Subscription
                    </div>
                    <Input
                      placeholder="Reason for cancellation..."
                      value={reason}
                      onChange={(e) => setReason(e.target.value)}
                      maxLength={500}
                    />
                    <ConfirmAction
                      label={actionLoading === 'cancelSub' ? 'Cancelling...' : 'Cancel Subscription'}
                      icon={Ban}
                      variant="destructive"
                      disabled={actionLoading === 'cancelSub' || !reason.trim()}
                      onConfirm={() => handleAction('cancelSub', () => usersAPI.cancelSubscription(userId, reason))}
                    />
                  </div>
                )}

                {/* Standard action buttons */}
                <div className="grid grid-cols-2 gap-2">
                  {/* Suspend / Unsuspend */}
                  <ConfirmAction
                    label={actionLoading === 'suspend' ? 'Processing...' : 'Suspend Account'}
                    icon={Ban}
                    variant="outline"
                    disabled={!!actionLoading}
                    onConfirm={() => handleAction('suspend', () => usersAPI.suspend(userId, 'Admin action'))}
                    title="Not functional"
                  />
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleAction('unsuspend', () => usersAPI.unsuspend(userId))}
                    disabled={!!actionLoading}
                    title="Not functional"
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    {actionLoading === 'unsuspend' ? 'Processing...' : 'Unsuspend'}
                  </Button>

                  {/* Force Logout */}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleAction('forceLogout', () => usersAPI.forceLogout(userId))}
                    disabled={!!actionLoading}
                    title="Not functional"
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    {actionLoading === 'forceLogout' ? 'Processing...' : 'Force Logout'}
                  </Button>

                  {/* Export User Data */}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleExport}
                    disabled={!!actionLoading}
                  >
                    <Download className="h-4 w-4 mr-2" />
                    {actionLoading === 'export' ? 'Exporting...' : 'Export Data'}
                  </Button>
                </div>

                {/* Send Notification (audit-only; not wired to email/in-app) */}
                <div
                  className="space-y-2 p-3 rounded-lg bg-accent/50"
                  title="Not functional"
                >
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <Bell className="h-4 w-4" />
                    Send Notification
                  </div>
                  <Input
                    placeholder="Subject..."
                    value={notifySubject}
                    onChange={(e) => setNotifySubject(e.target.value)}
                    maxLength={200}
                    title="Not functional"
                  />
                  <textarea
                    placeholder="Message..."
                    value={notifyMessage}
                    onChange={(e) => setNotifyMessage(e.target.value)}
                    maxLength={2000}
                    rows={3}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none"
                    title="Not functional"
                  />
                  <Button
                    size="sm"
                    onClick={() => handleAction('notify', () => usersAPI.sendNotification(userId, notifySubject, notifyMessage))}
                    disabled={actionLoading === 'notify' || !notifySubject.trim() || !notifyMessage.trim()}
                    title="Not functional"
                  >
                    {actionLoading === 'notify' ? 'Sending...' : 'Send'}
                  </Button>
                </div>

                {/* Destructive Actions (super_admin) */}
                <div className="border-t border-border pt-4 space-y-3">
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <Shield className="h-3 w-3" />
                    The following actions require Super Admin privileges
                  </p>

                  <div className="grid grid-cols-1 gap-2">
                    {/* Reset Password */}
                    {!showResetForm ? (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setShowResetForm(true)}
                        disabled={!!actionLoading}
                        className="w-full justify-start"
                      >
                        <Key className="h-4 w-4 mr-2" />
                        Reset Password
                      </Button>
                    ) : (
                      <div className="space-y-2 p-3 rounded-lg bg-accent/50">
                        <div className="flex items-center gap-2 text-sm font-medium">
                          <Key className="h-4 w-4" />
                          Set New Password
                        </div>
                        <Input
                          type="password"
                          placeholder="Enter new password (min 8 characters)..."
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          maxLength={128}
                          autoFocus
                        />
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => {
                              handleAction('resetPw', () => usersAPI.resetPassword(userId, newPassword))
                              setNewPassword('')
                              setShowResetForm(false)
                            }}
                            disabled={actionLoading === 'resetPw' || newPassword.length < 8}
                          >
                            {actionLoading === 'resetPw' ? 'Resetting...' : 'Confirm Reset'}
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => { setShowResetForm(false); setNewPassword('') }}
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>
                    )}

                    {/* Disable 2FA */}
                    <ConfirmAction
                      label={actionLoading === 'disable2fa' ? 'Disabling...' : 'Disable 2FA'}
                      icon={Lock}
                      variant="outline"
                      disabled={!!actionLoading}
                      onConfirm={() => handleAction('disable2fa', () => usersAPI.disable2fa(userId, 'Admin override'))}
                      className="w-full justify-start"
                    />

                    {/* Delete Account */}
                    <ConfirmAction
                      label={actionLoading === 'delete' ? 'Deleting...' : 'Delete Account'}
                      icon={Trash2}
                      variant="destructive"
                      disabled={!!actionLoading}
                      onConfirm={handleDeleteUser}
                      className="w-full justify-start"
                    />
                  </div>
                </div>

                {/* View Activity link */}
                <div className="border-t border-border pt-4">
                  <a
                    href={`/activity?user_id=${userId}`}
                    className="text-sm text-primary hover:underline flex items-center gap-1"
                    title="Not functional"
                  >
                    <Activity className="h-3 w-3" />
                    View Activity Logs for this user
                  </a>
                </div>
              </section>
            </>
          )}
        </div>
      </div>
    </>
  )
}

export default UserDetailModal
