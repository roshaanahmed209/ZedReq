const express = require('express')
const sqlite3 = require('sqlite3').verbose()
const bcrypt = require('bcryptjs')
const session = require('express-session')
const SQLiteStore = require('connect-sqlite3')(session)
const cors = require('cors')
const path = require('path')

const app = express()
const PORT = 5000

// Middleware
app.use(cors({
  origin: 'http://localhost:3000',
  credentials: true
}))
app.use(express.json())
app.use(session({
  store: new SQLiteStore({ db: 'sessions.db' }),
  secret: 'your-secret-key-change-this',
  resave: false,
  saveUninitialized: false,
  cookie: { 
    secure: false, // Set to true in production with HTTPS
    maxAge: 24 * 60 * 60 * 1000 // 24 hours
  }
}))

// Database setup
const DATABASE = 'social_network.db'

const initDb = () => {
  const db = new sqlite3.Database(DATABASE)
  
  db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT UNIQUE NOT NULL,
              email TEXT UNIQUE NOT NULL,
              password TEXT NOT NULL,
              full_name TEXT,
              headline TEXT,
              bio TEXT,
              avatar TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)`)
    
    db.run(`CREATE TABLE IF NOT EXISTS posts
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              content TEXT NOT NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (user_id) REFERENCES users (id))`)
    
    db.run(`CREATE TABLE IF NOT EXISTS connections
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              user1_id INTEGER NOT NULL,
              user2_id INTEGER NOT NULL,
              status TEXT DEFAULT 'pending',
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (user1_id) REFERENCES users (id),
              FOREIGN KEY (user2_id) REFERENCES users (id),
              UNIQUE(user1_id, user2_id))`)
    
    db.run(`CREATE TABLE IF NOT EXISTS likes
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              post_id INTEGER NOT NULL,
              user_id INTEGER NOT NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (post_id) REFERENCES posts (id),
              FOREIGN KEY (user_id) REFERENCES users (id),
              UNIQUE(post_id, user_id))`)
  })
  
  db.close()
}

// Routes
app.get('/', (req, res) => {
  res.json({ message: 'ZedReq API Server' })
})

app.post('/register', async (req, res) => {
  const { username, email, password, full_name } = req.body
  
  if (!username || !email || !password) {
    return res.status(400).json({ success: false, message: 'Missing required fields' })
  }
  
  const db = new sqlite3.Database(DATABASE)
  const hashedPassword = await bcrypt.hash(password, 10)
  
  db.run('INSERT INTO users (username, email, password, full_name) VALUES (?, ?, ?, ?)',
    [username, email, hashedPassword, full_name || ''], function(err) {
      if (err) {
        if (err.code === 'SQLITE_CONSTRAINT') {
          res.json({ success: false, message: 'Username or email already exists' })
        } else {
          res.status(500).json({ success: false, message: 'Database error' })
        }
      } else {
        req.session.user_id = this.lastID
        req.session.username = username
        res.json({ success: true, message: 'Registration successful' })
      }
      db.close()
    })
})

app.post('/login', async (req, res) => {
  const { username, password } = req.body
  
  if (!username || !password) {
    return res.status(400).json({ success: false, message: 'Missing credentials' })
  }
  
  const db = new sqlite3.Database(DATABASE)
  
  db.get('SELECT id, username, password FROM users WHERE username = ? OR email = ?', 
    [username, username], async (err, user) => {
      if (err) {
        res.status(500).json({ success: false, message: 'Database error' })
        db.close()
        return
      }
      
      if (user) {
        // No credential check - login with any entry
        req.session.user_id = user.id
        req.session.username = user.username
        res.json({ success: true, message: 'Login successful' })
        db.close()
      } else {
        // Auto-create user if they don't exist
        const hashedPassword = await bcrypt.hash(password, 10)
        db.run('INSERT INTO users (username, email, password, full_name) VALUES (?, ?, ?, ?)',
          [username, `${username}@temp.com`, hashedPassword, username], function(err) {
            if (err) {
              res.json({ success: false, message: 'User already exists' })
            } else {
              req.session.user_id = this.lastID
              req.session.username = username
              res.json({ success: true, message: 'Account created and logged in' })
            }
            db.close()
          })
      }
    })
})

app.get('/logout', (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      res.status(500).json({ success: false, message: 'Logout failed' })
    } else {
      res.json({ success: true, message: 'Logged out successfully' })
    }
  })
})

app.get('/api/user', (req, res) => {
  if (!req.session.user_id) {
    return res.status(401).json({ error: 'Not authenticated' })
  }
  
  const db = new sqlite3.Database(DATABASE)
  db.get('SELECT id, username, full_name, headline, bio, avatar FROM users WHERE id = ?', 
    [req.session.user_id], (err, user) => {
      if (err) {
        res.status(500).json({ error: 'Database error' })
      } else if (user) {
        res.json({
          id: user.id,
          username: user.username,
          full_name: user.full_name,
          headline: user.headline,
          bio: user.bio,
          avatar: user.avatar
        })
      } else {
        res.status(404).json({ error: 'User not found' })
      }
      db.close()
    })
})

app.get('/api/posts', (req, res) => {
  if (!req.session.user_id) {
    return res.status(401).json({ error: 'Not authenticated' })
  }
  
  const db = new sqlite3.Database(DATABASE)
  const query = `SELECT p.id, p.user_id, p.content, p.created_at, u.username, u.full_name, u.avatar,
                 (SELECT COUNT(*) FROM likes WHERE post_id = p.id) as like_count,
                 (SELECT COUNT(*) FROM likes WHERE post_id = p.id AND user_id = ?) as is_liked
                 FROM posts p
                 JOIN users u ON p.user_id = u.id
                 ORDER BY p.created_at DESC
                 LIMIT 20`
  
  db.all(query, [req.session.user_id], (err, rows) => {
    if (err) {
      res.status(500).json({ error: 'Database error' })
    } else {
      const posts = rows.map(row => ({
        id: row.id,
        user_id: row.user_id,
        content: row.content,
        created_at: row.created_at,
        username: row.username,
        full_name: row.full_name,
        avatar: row.avatar,
        like_count: row.like_count,
        is_liked: row.is_liked > 0
      }))
      res.json(posts)
    }
    db.close()
  })
})

app.post('/api/posts', (req, res) => {
  if (!req.session.user_id) {
    return res.status(401).json({ error: 'Not authenticated' })
  }
  
  const { content } = req.body
  
  if (!content || !content.trim()) {
    return res.status(400).json({ error: 'Content cannot be empty' })
  }
  
  const db = new sqlite3.Database(DATABASE)
  db.run('INSERT INTO posts (user_id, content) VALUES (?, ?)', 
    [req.session.user_id, content.trim()], function(err) {
      if (err) {
        res.status(500).json({ error: 'Database error' })
      } else {
        res.json({ success: true, post_id: this.lastID })
      }
      db.close()
    })
})

app.post('/api/posts/:postId/like', (req, res) => {
  if (!req.session.user_id) {
    return res.status(401).json({ error: 'Not authenticated' })
  }
  
  const postId = parseInt(req.params.postId)
  const db = new sqlite3.Database(DATABASE)
  
  // Check if already liked
  db.get('SELECT id FROM likes WHERE post_id = ? AND user_id = ?', 
    [postId, req.session.user_id], (err, like) => {
      if (err) {
        res.status(500).json({ error: 'Database error' })
        db.close()
        return
      }
      
      if (like) {
        // Unlike
        db.run('DELETE FROM likes WHERE post_id = ? AND user_id = ?', 
          [postId, req.session.user_id], (err) => {
            if (err) {
              res.status(500).json({ error: 'Database error' })
            } else {
              // Get updated like count
              db.get('SELECT COUNT(*) as count FROM likes WHERE post_id = ?', 
                [postId], (err, result) => {
                  res.json({ like_count: result.count })
                  db.close()
                })
            }
          })
      } else {
        // Like
        db.run('INSERT INTO likes (post_id, user_id) VALUES (?, ?)', 
          [postId, req.session.user_id], (err) => {
            if (err) {
              res.status(500).json({ error: 'Database error' })
            } else {
              // Get updated like count
              db.get('SELECT COUNT(*) as count FROM likes WHERE post_id = ?', 
                [postId], (err, result) => {
                  res.json({ like_count: result.count })
                  db.close()
                })
            }
          })
      }
    })
})

app.get('/api/users/search', (req, res) => {
  if (!req.session.user_id) {
    return res.status(401).json({ error: 'Not authenticated' })
  }
  
  const query = req.query.q || ''
  if (!query.trim()) {
    return res.json([])
  }
  
  const db = new sqlite3.Database(DATABASE)
  const searchQuery = `SELECT id, username, full_name, headline, avatar 
                       FROM users 
                       WHERE (username LIKE ? OR full_name LIKE ?) AND id != ?
                       LIMIT 10`
  
  db.all(searchQuery, [`%${query}%`, `%${query}%`, req.session.user_id], (err, rows) => {
    if (err) {
      res.status(500).json({ error: 'Database error' })
    } else {
      const users = rows.map(row => ({
        id: row.id,
        username: row.username,
        full_name: row.full_name,
        headline: row.headline,
        avatar: row.avatar
      }))
      res.json(users)
    }
    db.close()
  })
})

// Initialize database and start server
initDb()

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`)
})
