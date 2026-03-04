# ZedReq Backoffice System

Complete standalone backoffice/admin system for managing ZedReq platform with comprehensive user management, financial analytics, and security features.

## Features

- **User Management**: Complete control over all users with search, filtering, and role management
- **Financial Analytics**: Revenue tracking, cost analysis, and cash flow monitoring
- **Security**: OWASP Top 10 compliant with comprehensive audit logging
- **Professional UI**: Modern React frontend with shadcn/ui components

## Project Structure

```
backoffice/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── .env              # Environment variables (create from .env.example)
└── README.md         # This file
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- npm or yarn

### Setup Instructions

1. **Create virtual environment** (in backend directory):
   ```bash
   cd backoffice/backend
   python -m venv venv
   ```

2. **Activate virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **Install backend dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**:
   ```bash
   cd ../frontend
   npm install
   cd ../backend
   ```

5. **Create database**:
   ```sql
   CREATE DATABASE zedreq_backoffice;
   ```

6. **Create `.env` file** in backoffice root:
   ```bash
   # Copy the example and update with your values
   # See .env.example for required variables
   ```

7. **Update `.env`** with your database credentials and JWT secret key

8. **Initialize database**:
   ```bash
   python db/init_database.py
   ```

9. **Seed initial data**:
   ```bash
   python scripts/seed_data.py
   ```

10. **Start the application** (backend will build and serve frontend automatically):
    ```bash
    python main.py
    ```
    
    The application will:
    - Build the React frontend automatically (if not already built)
    - Start the backend server on http://localhost:5001
    - Serve the frontend from the same port
    
    **Access the application at:** http://localhost:5001

## Default Admin Credentials

After running seed script:
- Username: `admin`
- Password: `admin123` (change immediately in production!)

## Security

See `SECURITY.md` for comprehensive security documentation including OWASP risk assessments.

## API Documentation

Once the server is running, visit:
- **Application**: http://localhost:5001
- **Swagger UI**: http://localhost:5001/docs
- **ReDoc**: http://localhost:5001/redoc

**Note:** The backend automatically builds and serves the frontend. You only need to run `python main.py` from the backend directory.

## Development

- Backend: FastAPI with SQLAlchemy ORM
- Frontend: React 18 with Vite, shadcn/ui, Tailwind CSS
- Database: PostgreSQL
- Authentication: JWT tokens

## License

Proprietary - ZedReq Platform
