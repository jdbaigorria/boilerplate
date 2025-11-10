# FastAPI SaaS Boilerplate

A production-ready, modular, and highly configurable SaaS boilerplate built with **FastAPI**. This template provides a solid foundation for building scalable Software-as-a-Service applications with best practices, clean architecture, and enterprise-grade features.

## ✨ Features

### Core Features
- ✅ **FastAPI** - Modern, fast (high-performance) web framework
- ✅ **Pydantic Settings** - Type-safe configuration management
- ✅ **SQLAlchemy 2.0** - Async ORM with PostgreSQL support
- ✅ **Alembic** - Database migrations
- ✅ **JWT Authentication** - Secure token-based authentication
- ✅ **Password Hashing** - Bcrypt password encryption
- ✅ **Input Validation** - Comprehensive request/response validation
- ✅ **Error Handling** - Global exception handling with detailed error responses
- ✅ **Logging** - Structured JSON logging with multiple levels

### SaaS Features (Modular - Enable/Disable via Config)
- 🏢 **Multi-Tenancy** - Organization-based isolation
- 💳 **Subscription Management** - Multiple plans with feature flags
- 🎫 **Invitation System** - Invite users to organizations
- 👥 **Role-Based Access Control (RBAC)** - Granular permissions system
- 🔐 **OAuth Integration** - Google & GitHub authentication (optional)
- 📧 **Email Service** - SMTP email sending with templates
- 🤖 **AI Service Integration** - OpenAI, Anthropic, Google Gemini support
- 🚦 **Rate Limiting** - Redis-based request throttling
- 📊 **Health Checks** - Readiness and liveness probes
- 🔄 **Background Tasks** - Celery integration (optional)

### Developer Experience
- 🐳 **Docker Support** - Complete Docker Compose setup
- 🧪 **Testing** - Pytest with fixtures and coverage
- 📝 **API Documentation** - Auto-generated OpenAPI/Swagger docs
- 🎨 **Code Quality** - Ruff, Black, isort, mypy
- 🪝 **Pre-commit Hooks** - Automated code quality checks
- ⚡ **UV** - Ultra-fast Python package manager
- 🔧 **Makefile** - Convenient development commands

## 🏗️ Architecture

This boilerplate follows **Clean Architecture** principles with clear separation of concerns:

```
app/
├── api/              # API endpoints and routers
├── core/             # Core functionality (security, logging, exceptions)
├── db/               # Database configuration (PostgreSQL, MongoDB)
├── models/           # SQLAlchemy models
├── repositories/     # Data access layer (Repository pattern)
├── schemas/          # Pydantic schemas (DTOs)
├── services/         # Business logic
├── middleware/       # Custom middleware
├── tasks/            # Background tasks (Celery)
├── templates/        # Email templates
└── utils/            # Utility functions
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [UV](https://github.com/astral-sh/uv) - Fast Python package manager
- PostgreSQL 15+
- Redis 7+ (optional, for rate limiting/caching)
- Docker & Docker Compose (optional)

**Install UV:**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### Option 1: Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd fastapi-saas-boilerplate
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start services with Docker**
   ```bash
   make docker-up
   ```

4. **Run migrations**
   ```bash
   docker-compose -f docker/docker-compose.yml exec app alembic upgrade head
   ```

5. **Access the application**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/api/v1/health

### Option 2: Local Development with UV

1. **Install dependencies**
   ```bash
   # Install production dependencies
   uv pip install -e .

   # Or install with dev dependencies
   make install-dev
   # or
   uv pip install -e ".[dev]"

   # Sync dependencies (creates uv.lock)
   uv sync
   ```

2. **Setup database**
   ```bash
   # Create PostgreSQL database
   createdb saas_db

   # Run migrations
   make migrate
   # or
   uv run alembic upgrade head
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Run development server**
   ```bash
   make dev
   # or
   uv run uvicorn app.main:app --reload
   ```

## ⚙️ Configuration

All configuration is managed through environment variables. See `.env.example` for all available options.

### Essential Configuration

```bash
# Application
SECRET_KEY=your-secret-key-min-32-characters
DEBUG=false
ENVIRONMENT=production

# Database
USE_POSTGRES=true
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=saas_db

# Redis (for rate limiting)
ENABLE_RATE_LIMITING=true
REDIS_HOST=localhost
```

### Feature Flags

Enable or disable features by setting these variables:

```bash
ENABLE_MULTI_TENANCY=true      # Organizations and multi-tenant support
ENABLE_SUBSCRIPTIONS=true      # Subscription and billing
ENABLE_INVITATIONS=true        # User invitations
ENABLE_BACKGROUND_TASKS=false  # Celery background tasks
ENABLE_EMAIL=false             # Email sending
ENABLE_AI_SERVICE=false        # AI integrations
ENABLE_OAUTH_GOOGLE=false      # Google OAuth
```

## 📚 Usage Examples

### Register a New User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "John Doe"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

### Access Protected Endpoint

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <your-access-token>"
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run with coverage report
uv run pytest --cov=app --cov-report=html

# Or use make commands
make test-integration
make test-e2e
```

## 🎨 Code Quality

```bash
# Format code
make format
# or
uv run black app tests
uv run isort app tests

# Run linters
make lint
# or
uv run ruff check app tests
uv run mypy app

# Run all checks
make check
```

## 📦 Database Migrations

```bash
# Create a new migration
make migrations message="add users table"

# Apply migrations
make migrate

# Rollback last migration
make migrate-down

# View migration history
make migrate-history
```

## 🐳 Docker Commands

```bash
# Start all services
make docker-up

# Stop all services
make docker-down

# View logs
make docker-logs

# Rebuild containers
make docker-rebuild

# Open shell in app container
make docker-shell
```

## 📖 API Documentation

Once the application is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## 🔒 Security Features

- **Password Hashing**: Bcrypt with salt
- **JWT Tokens**: Secure access and refresh tokens
- **Rate Limiting**: Prevent brute force attacks
- **CORS Configuration**: Configurable allowed origins
- **Input Validation**: Pydantic schemas for all inputs
- **SQL Injection Protection**: SQLAlchemy ORM
- **XSS Protection**: Automatic escaping
- **Security Headers**: Configurable security headers

## 🏭 Production Deployment

### Environment Variables

Set these for production:

```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<strong-random-secret>
POSTGRES_PASSWORD=<strong-password>
```

### Database

```bash
# Run migrations
alembic upgrade head

# Create superuser
python scripts/create_superuser.py
```

### Running with Gunicorn

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## 📝 Project Structure

```
├── app/
│   ├── api/              # API layer
│   │   └── v1/          # API version 1
│   │       ├── auth.py  # Authentication endpoints
│   │       ├── health.py # Health check endpoints
│   │       └── router.py # Main router
│   ├── core/            # Core functionality
│   │   ├── security.py  # Authentication & encryption
│   │   ├── exceptions.py # Custom exceptions
│   │   ├── logging.py   # Logging configuration
│   │   ├── rate_limiter.py # Rate limiting
│   │   └── monitoring.py # Health checks
│   ├── db/              # Database layer
│   │   ├── base.py      # Base model class
│   │   ├── session.py   # Session management
│   │   └── postgres/    # PostgreSQL config
│   ├── models/          # Domain models
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── subscription.py
│   │   ├── role.py
│   │   └── invitation.py
│   ├── repositories/    # Data access layer
│   │   ├── base.py      # Generic CRUD operations
│   │   └── user_repository.py
│   ├── schemas/         # Pydantic schemas
│   │   ├── common.py
│   │   ├── user.py
│   │   └── auth.py
│   ├── services/        # Business logic
│   │   └── auth_service.py
│   ├── middleware/      # Custom middleware
│   │   └── error_handler.py
│   ├── config.py        # Configuration
│   └── main.py          # Application entry point
├── alembic/             # Database migrations
├── docker/              # Docker configuration
├── scripts/             # Utility scripts
├── tests/               # Test suite
├── .env.example         # Environment template
├── pyproject.toml       # Project dependencies (uv/pip)
├── uv.lock              # Dependency lock file (auto-generated)
├── Makefile             # Development commands
└── README.md            # This file
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [UV](https://github.com/astral-sh/uv) - Ultra-fast Python package manager
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations
- [Ruff](https://github.com/astral-sh/ruff) - Fast Python linter

## 📧 Support

For support, email support@example.com or open an issue on GitHub.

---

**Built with ❤️ using FastAPI**
