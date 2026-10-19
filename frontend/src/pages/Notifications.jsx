import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { notificationAPI, connectionAPI } from '../services/api'
import Navbar from '../components/Navbar'
import './Notifications.css'

const Notifications = () => {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState({})
  const [unreadCount, setUnreadCount] = useState(0)

  useEffect(() => {
    loadNotifications()
  }, [])

  const loadNotifications = async () => {
    try {
      setLoading(true)
      const [notifResponse, countResponse] = await Promise.all([
        notificationAPI.getNotifications(50, 0, false),
        notificationAPI.getUnreadCount()
      ])
      
      setNotifications(notifResponse.data || [])
      setUnreadCount(countResponse.data?.count || 0)
    } catch (error) {
      console.error('Error loading notifications:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleMarkAsRead = async (notificationId) => {
    try {
      await notificationAPI.markAsRead(notificationId)
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
      )
      setUnreadCount(prev => Math.max(0, prev - 1))
    } catch (error) {
      console.error('Error marking as read:', error)
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      await notificationAPI.markAllAsRead()
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
      setUnreadCount(0)
    } catch (error) {
      console.error('Error marking all as read:', error)
    }
  }

  const handleAcceptRequest = async (requestId, notificationId) => {
    setActionLoading(prev => ({ ...prev, [notificationId]: 'accepting' }))
    try {
      await connectionAPI.acceptRequest(requestId)
      await handleMarkAsRead(notificationId)
      setNotifications(prev => 
        prev.map(n => n.id === notificationId 
          ? { ...n, type: 'connection_accepted_action', is_read: true } 
          : n
        )
      )
    } catch (error) {
      console.error('Error accepting request:', error)
      // If already accepted/rejected, update UI to reflect that
      const errorMsg = error.response?.data?.detail || ''
      if (errorMsg.includes('already')) {
        setNotifications(prev => 
          prev.map(n => n.id === notificationId 
            ? { ...n, type: 'connection_already_handled', is_read: true } 
            : n
          )
        )
      } else {
        alert('Failed to accept connection request')
      }
    } finally {
      setActionLoading(prev => ({ ...prev, [notificationId]: null }))
    }
  }

  const handleRejectRequest = async (requestId, notificationId) => {
    setActionLoading(prev => ({ ...prev, [notificationId]: 'rejecting' }))
    try {
      await connectionAPI.rejectRequest(requestId)
      await handleMarkAsRead(notificationId)
      setNotifications(prev => prev.filter(n => n.id !== notificationId))
    } catch (error) {
      console.error('Error rejecting request:', error)
      // If already accepted/rejected, update UI to reflect that
      const errorMsg = error.response?.data?.detail || ''
      if (errorMsg.includes('already')) {
        setNotifications(prev => 
          prev.map(n => n.id === notificationId 
            ? { ...n, type: 'connection_already_handled', is_read: true } 
            : n
          )
        )
      } else {
        alert('Failed to reject connection request')
      }
    } finally {
      setActionLoading(prev => ({ ...prev, [notificationId]: null }))
    }
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now - date
    
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)
    
    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    if (days < 7) return `${days}d ago`
    return date.toLocaleDateString()
  }

  const getInitials = (name) => {
    if (!name) return '?'
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
  }


  return (
    <div className="notifications-container">
      <Navbar />
      <main className="notifications-main">
        <div className="notifications-header">
          <h1 className="notifications-title">
            Notifications
            {unreadCount > 0 && <span className="notifications-unread-badge">{unreadCount} new</span>}
          </h1>
          {unreadCount > 0 && (
            <button className="notifications-mark-all-btn" onClick={handleMarkAllAsRead}>
              Mark all as read
            </button>
          )}
        </div>

        {loading ? (
          <div className="notifications-loading">Loading notifications...</div>
        ) : notifications.length === 0 ? (
          <div className="notifications-empty">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
            <h3>No notifications yet</h3>
            <p>When you get notifications, they'll show up here</p>
          </div>
        ) : (
          <div className="notifications-list">
            {notifications.map(notification => (
              <div 
                key={notification.id}
                className={`notification-card ${!notification.is_read ? 'unread' : ''}`}
                onClick={() => !notification.is_read && handleMarkAsRead(notification.id)}
              >
                <div className="notification-header">
                  <div className="notification-avatar">
                    {notification.related_profile_pic ? (
                      <img src={notification.related_profile_pic} alt="" />
                    ) : (
                      getInitials(notification.related_name || notification.title)
                    )}
                  </div>
                  <div className="notification-info">
                    <h3 className="notification-title">{notification.title}</h3>
                    <p className="notification-message">{notification.message}</p>
                  </div>
                  <span className="notification-time">{formatTime(notification.created_at)}</span>
                </div>
                
                {notification.type === 'connection_request' && notification.related_request_id && (
                  <div className="notification-actions">
                    <button 
                      className="notification-action-btn primary"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleAcceptRequest(notification.related_request_id, notification.id)
                      }}
                      disabled={actionLoading[notification.id]}
                    >
                      {actionLoading[notification.id] === 'accepting' ? 'Accepting...' : 'Accept'}
                    </button>
                    <button
                      className="notification-action-btn"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleRejectRequest(notification.related_request_id, notification.id)
                      }}
                      disabled={actionLoading[notification.id]}
                    >
                      {actionLoading[notification.id] === 'rejecting' ? 'Rejecting...' : 'Reject'}
                    </button>
                  </div>
                )}
                
                {notification.type === 'connection_accepted_action' && (
                  <div className="notification-actions">
                    <button className="notification-action-btn" disabled>✓ Connection accepted</button>
                  </div>
                )}
                
                {notification.type === 'connection_already_handled' && (
                  <div className="notification-actions">
                    <button className="notification-action-btn" disabled>Already handled</button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

export default Notifications
