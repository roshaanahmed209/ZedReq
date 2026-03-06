# Backoffice-Main App Architecture & Data Flow

## Overview

The backoffice system uses a **hybrid data collection approach** to monitor the main ZedReq application. This document explains how the backoffice queries the main app, CORS configuration, and the theoretical data flow.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    MAIN ZEDREQ APP                              │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Port: 5000                                                │ │
│  │  Database: zedreq (PostgreSQL)                            │ │
│  │  Frontend: React (Port 3000/5173)                         │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  MonitoringMiddleware                                      │ │
│  │  - Intercepts ALL API requests                            │ │
│  │  - Tracks: endpoint, method, status, response_time        │ │
│  │  - Sends metrics → Backoffice Collector API              │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Frontend Analytics (analytics.js)                        │ │
│  │  - Tracks: page views, link clicks, interactions         │ │
│  │  - Sends events → Backoffice Collector API                │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  /api/monitoring/* Endpoints                              │ │
│  │  - /health: Health check                                  │ │
│  │  - /metrics: Basic metrics                                │ │
│  │  - /stats: Statistics                                      │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP Requests (with API Key)
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKOFFICE SYSTEM                            │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Port: 5001                                                │ │
│  │  Database: zedreq_backoffice (PostgreSQL)                │ │
│  │  Frontend: React (Served from backend)                    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Collector API (/api/collect/*)                           │ │
│  │  - POST /metrics: Receives API metrics                    │ │
│  │  - POST /events: Receives user events                     │ │
│  │  - POST /errors: Receives error logs                      │ │
│  │  - POST /security: Receives security events               │ │
│  │  - POST /session/*: Session management                    │ │
│  │  - Authentication: X-API-Key header                      │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Background Collectors (APScheduler)                       │ │
│  │  - InfrastructureCollector: CPU, RAM, Disk, Network       │ │
│  │  - UptimeMonitor: Health checks → Main App /health        │ │
│  │  - DatabaseCollector: Query main DB directly (read-only)  │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Direct Database Access (Read-Only)                        │ │
│  │  - Connects to: MAIN_APP_DB_* settings                    │ │
│  │  - Database: zedreq (same as main app)                    │ │
│  │  - Purpose: Historical data, user stats, growth metrics  │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Analytics Service                                         │ │
│  │  - Queries backoffice database (collected metrics)       │ │
│  │  - Queries main app database (historical data)             │ │
│  │  - Aggregates and processes data                          │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Data Collection Methods

### 1. **Real-Time API Metrics** (Push Model)
**Flow:**
1. Main app's `MonitoringMiddleware` intercepts every API request
2. Collects: endpoint, method, status_code, response_time, user_id, IP, user_agent
3. Buffers metrics (batch of 10)
4. Sends HTTP POST to: `http://localhost:5001/api/collect/metrics`
5. Includes `X-API-Key` header for authentication
6. Backoffice stores in `api_metrics` table

**CORS:** Not needed here - this is **server-to-server** communication (backend → backend)

### 2. **Frontend User Events** (Push Model)
**Flow:**
1. Main app's frontend loads `analytics.js`
2. Tracks: page views, link clicks, user interactions
3. Sends HTTP POST to: `http://localhost:5001/api/collect/events`
4. Includes `X-API-Key` header
5. Backoffice stores in `page_views`, `link_clicks`, `user_interactions` tables

**CORS:** **REQUIRED** - Browser makes cross-origin request
- Main app frontend: `http://localhost:3000` or `http://localhost:5173`
- Backoffice API: `http://localhost:5001`
- **Solution:** Backoffice CORS must allow main app frontend origins

### 3. **Direct Database Queries** (Pull Model)
**Flow:**
1. Backoffice's `DatabaseCollector` runs every 5 minutes (background job)
2. Connects directly to main app's PostgreSQL database using:
   - `MAIN_APP_DB_HOST`, `MAIN_APP_DB_PORT`, `MAIN_APP_DB_NAME`, etc.
3. Executes read-only queries:
   - Database health metrics
   - Query performance
   - Connection pool usage
   - Database size
4. Stores results in backoffice's `database_metrics` table

**CORS:** Not needed - direct database connection (no HTTP)

### 4. **Uptime Monitoring** (Pull Model)
**Flow:**
1. Backoffice's `UptimeMonitor` runs every 60 seconds (background job)
2. Makes HTTP GET request to: `http://localhost:5000/api/monitoring/health`
3. Checks response status and response time
4. Records downtime incidents in `uptime_incidents` table

**CORS:** Not needed - server-to-server communication

### 5. **Infrastructure Metrics** (Local Collection)
**Flow:**
1. Backoffice's `InfrastructureCollector` runs every 5 minutes
2. Uses `psutil` to collect local system metrics:
   - CPU usage
   - RAM usage
   - Disk usage
   - Network I/O
3. Stores in `infrastructure_metrics` table

**Note:** This collects metrics from the **backoffice server**, not the main app server. For main app server metrics, you'd need a separate collector on that server.

## CORS Configuration

### Main App CORS Settings
**File:** `backend/config/settings.py`
```python
CORS_ORIGINS: str  # From .env: "http://localhost:3000,http://localhost:5173"
```

**Configuration:**
- Allows frontend origins (React dev server)
- Allows backoffice frontend if needed
- Configured in `backend/main.py`:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=cors_origins,
      allow_credentials=True,
      allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
      allow_headers=["*"],
  )
  ```

### Backoffice CORS Settings
**File:** `backoffice/backend/config/settings.py`
```python
BACKOFFICE_CORS_ORIGINS: str  # From .env
```

**Configuration:**
- Must include main app frontend origins (for analytics.js)
- Must include backoffice frontend origin
- Configured in `backoffice/backend/main.py`:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=cors_origins,
      allow_credentials=True,
      allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
      allow_headers=["Content-Type", "Authorization", "X-API-Key", "Accept"],
      expose_headers=["Content-Type", "X-Request-ID"],
  )
  ```

**Why CORS is needed:**
- Main app frontend (browser) → Backoffice API (cross-origin)
- Browser enforces Same-Origin Policy
- CORS headers allow the cross-origin request

## Authentication & Security

### API Key Authentication
**For Collector Endpoints:**
- Main app sends `X-API-Key` header with requests
- Backoffice verifies using `COLLECTOR_API_KEY` from `.env`
- Timing-safe comparison using `hmac.compare_digest()`
- Fail-secure: Denies access if key not configured

**Configuration:**
- Main app: `COLLECTOR_API_KEY` in `.env`
- Backoffice: `COLLECTOR_API_KEY` in `backoffice/.env` (must match)

### Database Access
**For Direct Database Queries:**
- Backoffice connects using `MAIN_APP_DB_*` credentials
- Should use **read-only database user** in production
- Connection pooling configured
- No CORS needed (direct database connection)

## Data Flow Examples

### Example 1: User Clicks a Link
1. **User clicks link** in main app frontend
2. **analytics.js** captures click event
3. **Browser** sends POST to `http://localhost:5001/api/collect/events`
   - Includes `X-API-Key` header
   - CORS preflight check (OPTIONS request)
   - Backoffice responds with CORS headers
4. **Backoffice Collector API** receives event
   - Validates API key
   - Validates and sanitizes input
   - Stores in `link_clicks` table
5. **Backoffice frontend** can query this data via `/api/monitoring/interactions`

### Example 2: API Request in Main App
1. **User makes API request** to main app (e.g., `POST /api/posts`)
2. **MonitoringMiddleware** intercepts request
3. **Main app processes** request and returns response
4. **MonitoringMiddleware** calculates response time
5. **Main app backend** sends POST to `http://localhost:5001/api/collect/metrics`
   - Server-to-server (no CORS needed)
   - Includes `X-API-Key` header
6. **Backoffice Collector API** receives metrics
   - Validates API key
   - Stores in `api_metrics` table
7. **Backoffice frontend** can query via `/api/monitoring/performance`

### Example 3: Uptime Check
1. **APScheduler** triggers `UptimeMonitor.check_uptime()` every 60 seconds
2. **Backoffice backend** makes GET request to `http://localhost:5000/api/monitoring/health`
   - Server-to-server (no CORS needed)
3. **Main app** responds with health status
4. **UptimeMonitor** records result
   - If down: Creates `uptime_incident` record
   - If up: Updates last check time
5. **Backoffice frontend** displays uptime percentage

### Example 4: Database Health Check
1. **APScheduler** triggers `DatabaseCollector.collect_metrics()` every 5 minutes
2. **Backoffice backend** connects directly to main app database
   - Uses `MAIN_APP_DB_*` connection settings
   - Executes read-only queries:
     ```sql
     SELECT pg_database_size('zedreq');
     SELECT count(*) FROM pg_stat_activity;
     ```
3. **DatabaseCollector** stores results in `database_metrics` table
4. **Backoffice frontend** can query via `/api/monitoring/database`

## Configuration Files

### Main App `.env`
```env
# CORS for frontend
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Backoffice connection
BACKOFFICE_COLLECTOR_URL=http://localhost:5001/api/collect
COLLECTOR_API_KEY=your-secret-api-key-here
```

### Backoffice `.env`
```env
# Backoffice database
BACKOFFICE_DB_HOST=localhost
BACKOFFICE_DB_PORT=5432
BACKOFFICE_DB_NAME=zedreq_backoffice
BACKOFFICE_DB_USER=postgres
BACKOFFICE_DB_PASSWORD=password

# CORS (must include main app frontend)
BACKOFFICE_CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:3001

# Main app connection
MAIN_APP_DB_HOST=localhost
MAIN_APP_DB_PORT=5432
MAIN_APP_DB_NAME=zedreq
MAIN_APP_DB_USER=postgres_readonly  # Use read-only user!
MAIN_APP_DB_PASSWORD=password
MAIN_APP_API_URL=http://localhost:5000

# Collector API key (must match main app)
COLLECTOR_API_KEY=your-secret-api-key-here
```

## Summary

### How Backoffice Queries Main App:

1. **Real-Time Metrics (Push):**
   - Main app → Backoffice via HTTP POST
   - No CORS needed (server-to-server)
   - Authenticated with API key

2. **Frontend Events (Push):**
   - Main app frontend → Backoffice via HTTP POST
   - **CORS required** (browser cross-origin)
   - Authenticated with API key

3. **Uptime Checks (Pull):**
   - Backoffice → Main app via HTTP GET
   - No CORS needed (server-to-server)
   - No authentication (public health endpoint)

4. **Database Queries (Pull):**
   - Backoffice → Main app database (direct connection)
   - No CORS needed (not HTTP)
   - Authenticated with database credentials

### CORS Configuration:

- **Main App:** Allows frontend origins
- **Backoffice:** Must allow main app frontend origins (for analytics.js)
- **Server-to-Server:** No CORS needed (backend → backend)

### Security:

- API key authentication for collector endpoints
- Read-only database user for main app database access
- Input validation and sanitization
- Rate limiting on collector endpoints
- Fail-secure authentication
