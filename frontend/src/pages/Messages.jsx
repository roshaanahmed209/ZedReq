import React, { useState, useEffect, useRef } from 'react'
import styled, { keyframes } from 'styled-components'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { messagingAPI, MessagingWebSocket } from '../services/api'
import '../css/pages/Feed.css'

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`

const slideUp = keyframes`
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
`

const Container = styled.div`
  ${props => props.overlay ? `
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
  ` : `
    min-height: 100vh;
    background: var(--bg-light);
    animation: ${fadeIn} 0.6s ease-in;
    display: flex;
    flex-direction: column;
  `}
`

const MessagesContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  ${props => props.overlay ? `
    width: 100%;
    height: 100%;
  ` : `
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
    margin-top: 20px;
    margin-bottom: 20px;
    height: calc(100vh - 100px);
  `}
  background: var(--bg-white);
  border-radius: ${props => props.overlay ? '16px' : '16px'};
  border: 1px solid var(--border);
  box-shadow: ${props => props.overlay ? '0 4px 20px rgba(0, 0, 0, 0.3)' : '0 4px 20px rgba(0, 0, 0, 0.1)'};
  overflow: hidden;
`

const MessagesPanelHeader = styled.div`
  padding: 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--bg-white);
  flex-shrink: 0;
`

const MessagesPanelTitle = styled.h3`
  font-size: 1.2em;
  color: var(--text);
  font-weight: 300;
`

const CloseButton = styled.button`
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--text-light);
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;

  &:hover {
    background: var(--hover-bg);
    color: var(--text);
    transform: rotate(90deg);
  }

  svg {
    width: 20px;
    height: 20px;
  }
`

const ContactsList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  animation: ${fadeIn} 0.3s ease-in;

  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 10px;
  }
`

const ContactItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 4px;
  opacity: 1;
  transform: translateX(0);
  background: ${props => props.active ? 'var(--hover-bg)' : 'transparent'};

  &:hover {
    background: var(--hover-bg);
    transform: translateX(4px);
  }
`

const ContactAvatar = styled.div`
  width: 44px;
  height: 44px;
  min-width: 44px;
  border-radius: 50%;
  background: ${props => props.isBot ? 'linear-gradient(135deg, var(--primary), var(--secondary))' : 'var(--primary)'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
  font-size: 0.9em;
  transition: all 0.3s ease;

  svg {
    width: 24px;
    height: 24px;
    transition: transform 0.3s ease;
  }

  &:hover svg {
    transform: rotate(15deg) scale(1.1);
  }
`

const ContactInfo = styled.div`
  flex: 1;
  min-width: 0;
`

const ContactName = styled.div`
  font-size: 0.95em;
  color: var(--text);
  font-weight: 400;
  margin-bottom: 2px;
`

const ContactStatus = styled.div`
  font-size: 0.8em;
  color: var(--text-lighter);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`

const ChatView = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: ${fadeIn} 0.3s ease-in;
`

const ChatHeader = styled.div`
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--hover-bg);
  flex-shrink: 0;
`

const ChatHeaderLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
`

const ChatHeaderName = styled.div`
  font-size: 1em;
  color: var(--text);
  font-weight: 400;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`

const ChatMessages = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;

  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 10px;
  }
`

const ChatMessage = styled.div`
  display: flex;
  gap: 8px;
  align-items: flex-start;
  animation: ${fadeIn} 0.4s ease-in, ${slideUp} 0.4s ease-out;
  opacity: 1;
  transform: translateY(0);

  ${props => props.isUser && `
    flex-direction: row-reverse;
  `}
`

const MessageBubble = styled.div`
  background: ${props => props.isUser ? 'var(--primary)' : 'var(--hover-bg)'};
  color: ${props => props.isUser ? 'white' : 'var(--text)'};
  padding: 10px 14px;
  border-radius: ${props => props.isUser ? '12px 12px 4px 12px' : '12px 12px 12px 4px'};
  max-width: 75%;
  font-size: 0.9em;
  line-height: 1.4;
  word-wrap: break-word;
  transition: all 0.3s ease;
  opacity: 1;

  &:hover {
    opacity: 0.95;
    transform: scale(1.02);
  }
`

const ChatInputContainer = styled.div`
  padding: 16px;
  border-top: 1px solid var(--border);
  display: flex;
  gap: 10px;
  background: var(--bg-white);
  flex-shrink: 0;
`

const ChatInput = styled.input`
  flex: 1;
  padding: 10px 14px;
  background: var(--hover-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text);
  font-size: 0.9em;
  font-family: inherit;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: var(--primary);
    background: var(--bg-white);
    box-shadow: 0 0 0 3px rgba(10, 102, 194, 0.1);
    transform: scale(1.01);
  }

  &::placeholder {
    color: var(--text-lighter);
  }
`

const SendButton = styled.button`
  padding: 10px 14px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 1;

  &:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 4px 12px rgba(10, 102, 194, 0.3);
    opacity: 0.9;
  }

  &:active {
    transform: translateY(0) scale(0.98);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }

  svg {
    width: 18px;
    height: 18px;
  }
`

const BackIconButton = styled.button`
  width: 32px;
  height: 32px;
  min-width: 32px;
  border: none;
  background: var(--primary);
  color: white;
  cursor: pointer;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 1;

  &:hover {
    transform: scale(1.15);
    box-shadow: 0 4px 12px rgba(10, 102, 194, 0.4);
    opacity: 0.9;
  }

  &:active {
    transform: scale(0.95);
  }

  svg {
    width: 16px;
    height: 16px;
  }
`

const Loading = styled.div`
  padding: 20px;
  text-align: center;
  color: var(--text-lighter);
  font-size: 0.9em;
`

const EmptyState = styled.div`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-lighter);
  font-size: 0.9em;
`

const Messages = ({ overlay = false, onClose = null, initialRecipientId = null, initialRecipient = null }) => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [conversations, setConversations] = useState([])
  const [selectedContact, setSelectedContact] = useState(null)
  const [chatMessages, setChatMessages] = useState({})
  const [messageInput, setMessageInput] = useState('')
  const [loading, setLoading] = useState(true)
  const [loadingContacts, setLoadingContacts] = useState(false)
  const [sending, setSending] = useState(false)
  const [ws, setWs] = useState(null)
  const messagesEndRef = useRef(null)

  // Initialize WebSocket connection
  useEffect(() => {
    if (!user) return

    const messagingWs = new MessagingWebSocket(
      (message) => {
        // Handle incoming messages
        if (message.type === 'messages_list') {
          // Messages list received
          const formattedMessages = (message.messages || []).map(msg => ({
            id: msg.id,
            text: msg.content,
            isUser: msg.sender_id === user.id,
            timestamp: new Date(msg.timestamp)
          }))
          setChatMessages(prev => ({
            ...prev,
            [message.recipient_id]: formattedMessages
          }))
        } else if (message.sender_id || message.recipient_id) {
          // New message received
          const contactId = message.sender_id === user.id ? message.recipient_id : message.sender_id
          const newMessage = {
            id: message.id,
            text: message.content,
            isUser: message.sender_id === user.id,
            timestamp: new Date(message.timestamp)
          }
          
          setChatMessages(prev => {
            const existing = prev[contactId] || []
            // Check if message already exists by ID
            const exists = existing.some(m => m.id === message.id)
            if (exists) return prev
            
            // Remove any temp messages with matching content (for optimistic updates)
            const filtered = existing.filter(m => {
              // Keep real messages (not temp ones)
              if (!m.id.toString().startsWith('temp_')) return true
              // Remove temp messages that match this real message's content
              return m.text !== message.content
            })
            
            return {
              ...prev,
              [contactId]: [...filtered, newMessage]
            }
          })
          
          // Update conversations list
          loadConversations()
        }
      },
      (error) => {
        console.error('Messaging WebSocket error:', error)
      }
    )

    messagingWs.connect()
    setWs(messagingWs)

    return () => {
      messagingWs.disconnect()
    }
  }, [user])

  // Load conversations
  const loadConversations = async () => {
    try {
      setLoadingContacts(true)
      const response = await messagingAPI.getConversations()
      console.log('Conversations response:', response.data)
      
      if (response.data.success) {
        const convs = response.data.conversations || []
        console.log('Loaded conversations:', convs)
        
        // Convert conversations to contacts format
        const contactsList = convs.map(conv => {
          const otherUser = conv.other_user || {}
          const name = otherUser.name || otherUser.username || `User ${conv.other_user_id}`
          const initials = name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
          
          return {
            id: conv.other_user_id,
            conversation_id: conv.conversation_id,
            name: name,
            status: 'Connected',
            isBot: false,
            avatar: initials,
            last_message: conv.last_message,
            other_user: otherUser
          }
        })
        
        setConversations(contactsList)
      }
    } catch (error) {
      console.error('Error loading conversations:', error)
    } finally {
      setLoading(false)
      setLoadingContacts(false)
    }
  }

  // Initial load
  useEffect(() => {
    loadConversations()
  }, [])

  // Auto-select contact when initialRecipientId is provided
  useEffect(() => {
    if (initialRecipientId && (!selectedContact || selectedContact.id !== initialRecipientId)) {
      // First, try to find in existing conversations
      const existingContact = conversations.find(c => c.id === initialRecipientId)
      
      if (existingContact) {
        // Contact exists in conversations, select it (this will load messages)
        handleContactSelect(existingContact)
      } else if (initialRecipient) {
        // If not in conversations but we have user data, create a contact object
        const name = initialRecipient.name || initialRecipient.username || `User ${initialRecipientId}`
        const initials = name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
        
        const newContact = {
          id: initialRecipientId,
          conversation_id: null, // No conversation yet
          name: name,
          status: 'Connected',
          isBot: false,
          avatar: initials,
          last_message: null,
          other_user: initialRecipient
        }
        
        // Select the contact and try to load any existing messages
        setSelectedContact(newContact)
        
        // Try to load messages for this user (even if no conversation exists yet)
        if (!chatMessages[initialRecipientId]) {
          messagingAPI.getMessages(initialRecipientId, 50)
            .then(response => {
              if (response.data.success) {
                const messages = response.data.messages || []
                const formattedMessages = messages.map(msg => ({
                  id: msg.id,
                  text: msg.content,
                  isUser: msg.sender_id === user.id,
                  timestamp: new Date(msg.timestamp)
                }))
                
                setChatMessages(prev => ({
                  ...prev,
                  [initialRecipientId]: formattedMessages
                }))
              }
            })
            .catch(error => {
              console.error('Error loading messages:', error)
              // Set empty array if no messages exist
              setChatMessages(prev => ({
                ...prev,
                [initialRecipientId]: []
              }))
            })
        }
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialRecipientId, initialRecipient, conversations])

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages, selectedContact])

  // Handle conversation selection
  const handleContactSelect = async (contact) => {
    setSelectedContact(contact)
    
    // Load messages for this conversation
    if (!chatMessages[contact.id] && !contact.isBot) {
      try {
        const response = await messagingAPI.getMessages(contact.id, 50)
        if (response.data.success) {
          const messages = response.data.messages || []
          const formattedMessages = messages.map(msg => ({
            id: msg.id,
            text: msg.content,
            isUser: msg.sender_id === user.id,
            timestamp: new Date(msg.timestamp)
          }))
          
          setChatMessages(prev => ({
            ...prev,
            [contact.id]: formattedMessages
          }))
        }
      } catch (error) {
        console.error('Error loading messages:', error)
        setChatMessages(prev => ({
          ...prev,
          [contact.id]: []
        }))
      }
    }
  }

  // Handle sending message
  const handleSendMessage = async () => {
    if (!messageInput.trim() || !selectedContact || selectedContact.isBot || sending) return

    const messageText = messageInput.trim()
    setMessageInput('')
    setSending(true)

    // Optimistically add message to UI
    const tempMessage = {
      id: `temp_${Date.now()}`,
      text: messageText,
      isUser: true,
      timestamp: new Date()
    }

    setChatMessages(prev => ({
      ...prev,
      [selectedContact.id]: [...(prev[selectedContact.id] || []), tempMessage]
    }))

    try {
      // Send via WebSocket if available
      if (ws && ws.ws && ws.ws.readyState === WebSocket.OPEN) {
        ws.sendMessage(selectedContact.id, messageText, 'text')
        // The WebSocket handler will receive the message and replace the temp message
        // Just wait a bit and mark as not sending
        setTimeout(() => {
          setSending(false)
        }, 500)
      } else {
        // Fallback to HTTP API
        const response = await messagingAPI.sendMessage(selectedContact.id, messageText, 'text')
        if (response.data.success) {
          // Replace temp message with real message
          const realMessage = {
            id: response.data.message.id,
            text: response.data.message.content,
            isUser: true,
            timestamp: new Date(response.data.message.timestamp)
          }
          setChatMessages(prev => {
            const existing = prev[selectedContact.id] || []
            // Remove temp message and add real message
            const filtered = existing.filter(msg => msg.id !== tempMessage.id)
            return {
              ...prev,
              [selectedContact.id]: [...filtered, realMessage]
            }
          })
        }
        setSending(false)
      }

      // Reload conversations to update last message
      loadConversations()
    } catch (error) {
      console.error('Error sending message:', error)
      // Remove temp message on error
      setChatMessages(prev => ({
        ...prev,
        [selectedContact.id]: (prev[selectedContact.id] || []).filter(msg => msg.id !== tempMessage.id)
      }))
      setMessageInput(messageText) // Restore input
      setSending(false)
    }
  }

  // Handle Enter key
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // Handle back to contacts
  const handleBackToContacts = () => {
    setSelectedContact(null)
  }

  // Handle close button
  const handleClose = () => {
    if (overlay && onClose) {
      onClose()
    } else {
      navigate('/feed')
    }
  }

  // Format timestamp
  const formatTime = (timestamp) => {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now - date
    
    if (diff < 60000) return 'Just now'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`
    
    return date.toLocaleDateString()
  }

  return (
    <Container overlay={overlay}>
      <MessagesContainer overlay={overlay}>
        <MessagesPanelHeader>
          <MessagesPanelTitle>Messages</MessagesPanelTitle>
          <CloseButton onClick={handleClose}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </CloseButton>
        </MessagesPanelHeader>

        {!selectedContact ? (
          <ContactsList>
            {loadingContacts ? (
              <Loading>Loading conversations...</Loading>
            ) : conversations.length === 0 ? (
              <EmptyState>No conversations yet</EmptyState>
            ) : (
              conversations.map(contact => (
                <ContactItem
                  key={contact.id}
                  active={selectedContact?.id === contact.id}
                  onClick={() => handleContactSelect(contact)}
                >
                  <ContactAvatar isBot={contact.isBot}>
                    {contact.isBot ? (
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 3v3"></path>
                        <path d="M12 18v3"></path>
                        <path d="M5.5 5.5l2.1 2.1"></path>
                        <path d="M16.4 16.4l2.1 2.1"></path>
                        <path d="M3 12h3"></path>
                        <path d="M18 12h3"></path>
                        <path d="M5.5 18.5l2.1-2.1"></path>
                        <path d="M16.4 7.6l2.1-2.1"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                      </svg>
                    ) : (
                      contact.avatar
                    )}
                  </ContactAvatar>
                  <ContactInfo>
                    <ContactName>{contact.name}</ContactName>
                    <ContactStatus>
                      {contact.last_message 
                        ? (contact.last_message.content.length > 30 
                            ? contact.last_message.content.substring(0, 30) + '...' 
                            : contact.last_message.content)
                        : contact.status}
                    </ContactStatus>
                  </ContactInfo>
                </ContactItem>
              ))
            )}
          </ContactsList>
        ) : (
          <ChatView>
            <ChatHeader>
              <ChatHeaderLeft>
                <ContactAvatar isBot={selectedContact.isBot}>
                  {selectedContact.isBot ? (
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M12 3v3"></path>
                      <path d="M12 18v3"></path>
                      <path d="M5.5 5.5l2.1 2.1"></path>
                      <path d="M16.4 16.4l2.1 2.1"></path>
                      <path d="M3 12h3"></path>
                      <path d="M18 12h3"></path>
                      <path d="M5.5 18.5l2.1-2.1"></path>
                      <path d="M16.4 7.6l2.1-2.1"></path>
                      <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                  ) : (
                    selectedContact.avatar
                  )}
                </ContactAvatar>
                <ChatHeaderName>{selectedContact.name}</ChatHeaderName>
              </ChatHeaderLeft>
              <BackIconButton onClick={handleBackToContacts}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="19" y1="12" x2="5" y2="12"></line>
                  <polyline points="12 19 5 12 12 5"></polyline>
                </svg>
              </BackIconButton>
            </ChatHeader>

            <ChatMessages>
              {(chatMessages[selectedContact.id] || []).map(msg => (
                <ChatMessage key={msg.id} isUser={msg.isUser}>
                  <MessageBubble isUser={msg.isUser}>
                    {msg.text}
                  </MessageBubble>
                </ChatMessage>
              ))}
              <div ref={messagesEndRef} />
            </ChatMessages>

            <ChatInputContainer>
              <ChatInput
                type="text"
                placeholder="Type a message..."
                value={messageInput}
                onChange={(e) => setMessageInput(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={sending || selectedContact.isBot}
              />
              <SendButton
                onClick={handleSendMessage}
                disabled={sending || !messageInput.trim() || selectedContact.isBot}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              </SendButton>
            </ChatInputContainer>
          </ChatView>
        )}
      </MessagesContainer>
    </Container>
  )
}

export default Messages
