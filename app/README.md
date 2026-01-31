# FastAPI Application Structure

This directory contains the FastAPI application code following security best practices and clean architecture principles.

## Directory Structure

```
app/
├── __init__.py              # Package initialization with version
├── main.py                  # FastAPI app instance and middleware
├── config.py                # Application settings (Pydantic Settings)
├── dependencies.py          # Dependency injection functions
│
├── models/                  # Pydantic models (request/response)
│   ├── __init__.py
│   ├── user.py             # User-related models
│   └── common.py           # Common response models
│
├── routers/                 # API route handlers
│   ├── __init__.py
│   ├── health.py           # Health check endpoints
│   ├── auth.py             # Authentication endpoints
│   └── users.py            # User management endpoints
│
├── services/                # Business logic layer
│   ├── __init__.py
│   ├── auth_service.py     # Authentication logic
│   └── user_service.py     # User management logic
│
├── database/                # Database configuration and models
│   ├── __init__.py
│   ├── base.py             # Database connection and session
│   └── models.py           # SQLAlchemy ORM models
│
└── utils/                   # Utility functions
    ├── __init__.py
    └── security.py          # Security utilities (hashing, JWT)
```

## Key Components

### Main Application (`main.py`)
- FastAPI app initialization
- CORS middleware configuration
- Security headers middleware
- Rate limiting setup
- Global exception handling
- Router inclusion

### Configuration (`config.py`)
- Environment-based settings using Pydantic
- Secure defaults for production
- Validates configuration on startup
- Centralized settings access with `get_settings()`

### Models (`models/`)
- **Pydantic models** for request/response validation
- Input sanitization and type checking
- Password strength validation
- Email validation

### Routers (`routers/`)
- **Health Check**: `/health` - API health status
- **Authentication**: `/api/v1/auth/*` - Login, token refresh
- **Users**: `/api/v1/users/*` - User registration and management

### Services (`services/`)
- Business logic separated from routes
- Reusable across different endpoints
- Easy to test in isolation
- Currently using mock data (TODO: integrate with database)

### Database (`database/`)
- Async SQLAlchemy configuration
- Database models (ORM)
- Session management
- Migration support (Alembic ready)

### Security (`utils/security.py`)
- Password hashing with bcrypt
- JWT token creation and validation
- Secure token expiration handling

## Security Features

### Authentication
- JWT-based authentication
- Refresh token support
- Secure password hashing (bcrypt)
- Token expiration handling

### Input Validation
- Pydantic model validation
- Password strength requirements:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
- Email format validation
- Username pattern validation

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HSTS)
- `Content-Security-Policy`

### Rate Limiting
- Per-endpoint rate limits
- IP-based rate limiting
- Configurable limits

### CORS
- Configurable allowed origins
- Credential support
- Proper headers configuration

## API Endpoints

### Health Check
- `GET /health` - Health check with version info
- `GET /` - Root endpoint with API info

### Authentication
- `POST /api/v1/auth/token` - Login (OAuth2 form)
- `POST /api/v1/auth/login` - Login (JSON)
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `POST /api/v1/users/register` - Register new user
- `GET /api/v1/users/me` - Get current user (protected)
- `GET /api/v1/users/` - List users (protected)
- `GET /api/v1/users/{username}` - Get user by username (protected)

## Running the Application

### Development Mode
```bash
# Using the startup script (recommended)
./start.sh

# Or manually
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment Variables
Copy `.env.example` to `.env` and configure:
- `SECRET_KEY` - JWT secret (generate with `openssl rand -hex 32`)
- `DATABASE_URL` - Database connection string
- `CORS_ORIGINS` - Allowed CORS origins
- See `.env.example` for all options

## Testing

Run tests with coverage:
```bash
pytest --cov=app --cov-report=term-missing
```

Run specific test files:
```bash
pytest tests/test_auth.py -v
```

## Next Steps (TODOs)

### Database Integration
1. Configure Alembic for migrations
2. Replace mock data in services with actual database queries
3. Add database initialization in lifespan events
4. Implement proper user CRUD operations

### Additional Features
1. Email verification for new users
2. Password reset functionality
3. User profile updates
4. Admin role and permissions
5. Logging configuration
6. API documentation improvements

### Security Enhancements
1. Implement token blacklisting for logout
2. Add two-factor authentication (2FA)
3. Implement account lockout after failed attempts
4. Add security audit logging
5. Implement CSRF protection for web forms

### Production Readiness
1. Set up database connection pooling
2. Add caching layer (Redis)
3. Implement proper logging (structured logs)
4. Add monitoring and alerting
5. Set up background task processing

## Code Quality Standards

- **Format**: Black (88 char line length)
- **Linting**: Ruff, Pylint
- **Type Checking**: MyPy with strict mode
- **Security Scanning**: Bandit, Safety
- **Test Coverage**: 80% minimum target

## Contributing

1. Follow the established directory structure
2. Write tests for all new features
3. Ensure all security checks pass
4. Update documentation
5. Follow conventional commits format
