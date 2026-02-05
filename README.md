# ZedRec - AI-Powered Professional Networking Platform

ZedRec is a comprehensive professional networking and career development platform that combines social networking, job discovery, and learning management with AI-powered features.

## Overview

ZedRec provides a LinkedIn-like experience with enhanced AI capabilities for career growth. The platform enables professionals to connect, share content, discover opportunities, and develop skills through an integrated learning management system.

## Key Features

- **Professional Social Network**: Connect with professionals, share posts, and build your network
- **Job Portal**: Discover job opportunities, apply to positions, and track applications
- **Learning Management System**: Enroll in courses, take quizzes, and track your learning progress
- **AI-Powered Features**: AI-generated questions, course recommendations, and learning analytics
- **Real-time Communication**: Direct messaging and real-time notifications
- **Career Development**: Track skills, progress, and receive personalized recommendations

## Architecture

### Architecture Type

ZedRec follows a **monolithic architecture** pattern with a modular, layered design. All backend services are integrated into a single FastAPI application, organized into distinct modules (routers, services, models) for maintainability and future scalability.

### Architecture Layers

- **Presentation Layer**: React frontend with component-based UI
- **Application Layer**: FastAPI backend with RESTful APIs and WebSocket support
- **Data Layer**: PostgreSQL for structured data, Qdrant for vector embeddings

### Scalability

The platform is designed with scalability in mind:

- **Horizontal Scaling**: Stateless API design allows running multiple FastAPI instances behind a load balancer
- **Database Connection Pooling**: Efficient connection management for high concurrency
- **Stateless Authentication**: JWT-based authentication enables distributed deployment
- **Modular Service Layer**: Business logic separated into independent service classes for easy refactoring
- **WebSocket Management**: Connection manager supports multi-instance deployment with proper connection handling

### Scaling Approach

**Current Implementation:**
- Horizontal scaling of FastAPI application instances
- Database read replicas for read-heavy operations
- Connection pooling for optimal database resource usage
- Caching strategies for frequently accessed data (e.g., LMS dashboard)

**Future Scalability Path:**
- Migration to microservices architecture for independent scaling of features
- Event-driven architecture for asynchronous processing
- CQRS (Command Query Responsibility Segregation) pattern for read/write optimization
- Distributed database architecture for high availability
- Separate WebSocket service for real-time features
- Message queue integration for background job processing

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React 18
- **Database**: PostgreSQL
- **AI Integration**: OpenAI, LangChain, Qdrant
- **Real-time**: WebSocket

## Project Structure

```
ZedRec/
├── backend/          # FastAPI backend application
├── frontend/          # React frontend application
└── ZedRec_Documentation.html  # Complete codebase documentation
```

## Documentation

For detailed technical documentation including architecture, database design, API endpoints, and implementation details, see `ZedRec_Documentation.html`.
