# ZedReq Backend API

Professional, scalable Flask backend for the ZedReq platform.

## Project Structure

```
backend/
├── config/              # Configuration files
│   ├── __init__.py     # Configuration classes
│   └── database.py     # Database connection manager
├── controllers/         # Request handlers
│   ├── auth_controller.py
│   ├── user_controller.py
│   └── post_controller.py
├── middleware/         # Custom middleware
│   ├── auth_middleware.py
│   └── error_middleware.py
├── models/             # Database models
│   ├── user.py
│   ├── post.py
│   ├── like.py
│   └── connection.py
├── routes/             # Route blueprints
│   ├── auth_routes.py
│   ├── user_routes.py
│   └── post_routes.py
├── services/           # Business logic layer
│   ├── auth_service.py
│   ├── user_service.py
│   └── post_service.py
├── utils/              # Utility functions
│   ├── errors.py
│   ├── logger.py
│   └── response.py
├── validators/         # Input validation
│   ├── auth_validator.py
│   ├── post_validator.py
│   └── user_validator.py
├── app.py              # Application factory
└── __init__.py
```

## Features

- ✅ **Layered Architecture**: Separation of concerns with Models, Controllers, Services, and Routes
- ✅ **Error Handling**: Centralized error handling with custom exception classes
- ✅ **Input Validation**: Request validation with custom validators
- ✅ **Authentication**: Session-based authentication with decorators
- ✅ **Database Abstraction**: Clean database access layer
- ✅ **Logging**: Structured logging system
- ✅ **Scalable Structure**: Easy to extend and maintain

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`
2. Update environment variables as needed

```bash
cp .env.example .env
```

## Running the Server

### Development
```bash
python app.py
# or
flask run
```

### Production
```bash
gunicorn app:app
```

## API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - Login user
- `GET /logout` - Logout user

### Users
- `GET /api/user` - Get current user
- `PUT /api/user` - Update current user
- `GET /api/users/search?q=query` - Search users

### Posts
- `GET /api/posts` - Get all posts
- `POST /api/posts` - Create new post
- `PUT /api/posts/:postId` - Update post
- `DELETE /api/posts/:postId` - Delete post
- `POST /api/posts/:postId/like` - Toggle like on post

## Architecture Principles

1. **Separation of Concerns**: Each layer has a specific responsibility
2. **DRY (Don't Repeat Yourself)**: Reusable utilities and middleware
3. **Error Handling**: Consistent error responses across the API
4. **Validation**: Input validation at the route level
5. **Security**: Authentication decorators for protected routes
6. **Scalability**: Easy to add new features and endpoints

## Database

Uses SQLite3 with the following tables:
- `users` - User accounts
- `posts` - User posts
- `likes` - Post likes
- `connections` - User connections

Database is automatically initialized on server start.

## Contributing

1. Follow the existing code structure
2. Add appropriate error handling
3. Include input validation
4. Write clear, descriptive code
5. Update documentation as needed
