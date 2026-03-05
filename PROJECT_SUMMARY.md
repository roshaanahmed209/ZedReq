# ZedReq Project Summary

**Date:** December 10, 2025

---

## Point 1: Project Overview & Decisions

### Your AI-Powered LinkedIn Replica (Next-Generation Career Platform)

You are building a full LinkedIn clone with major enhancements powered by AI. It includes social networking, job discovery, LMS, AI interviews, chat, user profiles, and career-focused analytics—all integrated into a modern platform.

**Platform's Working Title:** ZedReq

---

## 🔥 Core System Features Finalized

### 1. Professional Social Network (LinkedIn-like)

- User profiles
- Posts, likes, comments
- Feed system
- Connection system
- Messaging
- Profile discovery with filters
- Modern UX with animations

### 2. AI Capabilities (Your Competitive Edge)

- AI resume analysis
- AI cover letter generation
- AI job matcher
- AI professional coach
- AI mock interviews (video + text)
- Skill gap analysis
- ATS score predictions
- AI summaries in chat & feed

### 3. LMS & Skills Platform

- Courses (25+ planned)
- Quizzes
- Course performance tracking
- AI grading & difficulty scaling
- Learning analytics dashboard

### 4. Intelligent Job Portal

- Job postings
- AI match scores
- Parsing job descriptions
- Career insights
- Recommended jobs feed

---

## 🧱 Infrastructure & Storage Decisions (Finalized)

The system is production-oriented, starting with free or low-cost scalable services.

### 1. Textual Data

**✔ Decision: PostgreSQL**

**Reason:** Reliable, scalable, ACID, ideal for structured data.

**Used for:**
- Users
- Jobs
- Courses
- Comments
- Posts
- Connections
- Notifications
- Analytics
- Profile data

### 2. Chat Messages

**✔ Decision: MongoDB**

**Candidates Evaluated:**
- MongoDB Atlas (Free forever tier)
- Firebase Firestore (Free Spark tier)
- DynamoDB free tier (AWS Free for 12 months)

**Why MongoDB:**
- JSON-based
- Scales horizontally
- Document-oriented (perfect for chat)
- Free tier supports millions of documents

**Used for:**
- Messages
- Chat rooms
- Message threading
- Presence/indexing

### 3. Images & Video Storage

**Options Evaluated:**
| Service | Notes |
|---------|-------|
| Supabase Storage | 10GB free |
| Cloudflare R2 | Free tier |
| Firebase Storage | Free tier |
| Backblaze B2 | Cheap, not fully free |
| AWS S3 | Free tier 12 months only |

**✔ Decision: Cloudflare R2 (with CDN)**

**Why Cloudflare R2:**
- Permanent free tier
- No egress cost
- Ideal for large user-generated content
- Highly scalable for millions of files

**Used for:**
- Profile pictures
- Post images
- Course videos
- AI mock interview videos
- Company logos
- Attachments

---

## 📂 Database Design (Completed)

### PostgreSQL Schema (Relational)

**Tables include:**
- `users`
- `posts`
- `comments`
- `reactions`
- `connections`
- `jobs`
- `job_applications`
- `courses`
- `lessons`
- `quizzes`
- `analytics`
- `notifications`
- AI-related tables

### MongoDB Schema (NoSQL for Chat)

**Collections:**
- `chats`
- `messages`
- `participants`
- `presence`
- `attachments` metadata (linked to R2)

**Indexes:**
- `conversation_id` index
- Compound index (`sender_id` + `timestamp`)
- Text index for full-text search

---

## 📈 Scalability Assumptions for Initial Deployment

**Target:** 200,000 users at launch

### User Activity Estimates (Industry Averages)

| Metric | Estimate |
|--------|----------|
| Monthly active users | 30–40% |
| Daily active users | 10% (~20k–30k users) |
| Messages per user | 1–3 average |
| Post creation rate | ~2–3% of users |

### Data Estimates

| Component | Estimate |
|-----------|----------|
| **PostgreSQL** | ~5–10GB structured data |
| **MongoDB** | ~40–60M documents ≈ 10–20GB (compressed) |
| **Cloudflare R2** | ~300–600GB for 200k users (images, videos, course media, resumes) |

### Cost Estimates

| Service | Cost |
|---------|------|
| Cloudflare R2 | Free + minimal |
| MongoDB | Free tier, then $9–$20/mo |
| PostgreSQL | ~$20–40/mo (provider dependent) |
| CDN | Free (Cloudflare) |

---

## 🧩 System Architecture (High-level)

### Frontend
- Next.js or React
- Chat interface
- Social feed
- LMS UI
- Profile pages
- Job portal

### Backend
- Node.js / Python FastAPI / Go
- REST + WebSockets
- AI microservices (OpenAI)
- Authentication (JWT + OAuth)

### Databases

| Component | Database | Reason |
|-----------|----------|--------|
| Core platform | PostgreSQL | ACID / structured |
| Chat | MongoDB | Flexible / fast |
| Media | Cloudflare R2 | Cheap & scalable |

### AI Engines
- Resume parser
- Job matcher
- Interview generator
- Content summarizer
- Course auto-grading

---

## 🎯 Final Decision Summary

| Category | Decision |
|----------|----------|
| Platform | LinkedIn clone + AI enhancements |
| Architecture | Microservices + event-driven |
| Main DB | PostgreSQL |
| Chat DB | MongoDB |
| Media Storage | Cloudflare R2 |
| Users | Start with 200,000 target |
| AI | OpenAI + custom Ranker models |
| LMS | Integrated |
| Job System | AI-based scoring |
| Messaging | WebSockets |
| Scaling | Future: distributed DB + CQRS |

---

*Document created: December 10, 2025*

