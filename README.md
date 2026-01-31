# votra.io

The website and API for dev.votra.io and www.votra.io.

## Overview

This repository contains the FastAPI-based backend API and web services for Votra.io, built with security, testing, and code quality as top priorities.

## Custom Agent: FastAPI Security Developer

This project includes a specialized custom agent for FastAPI development that enforces:
- ✅ **Security best practices** (OWASP, bandit, safety)
- ✅ **Comprehensive testing** (80% coverage target with pytest)
- ✅ **Code quality** (black, ruff, mypy, pylint)
- ✅ **CI/CD automation** (GitHub Actions)
- ✅ **Secrets management** (GitHub secrets, gh CLI)

### Using the Custom Agent

Reference the agent in your requests:
```
@fastapi-security-dev Please create a user authentication endpoint with JWT tokens
```

See [`.github/agents/README.md`](.github/agents/README.md) for detailed usage instructions.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- GitHub CLI (for secrets management)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/VotraIO/votra.io.git
   cd votra.io
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application** (when implemented)
   ```bash
   uvicorn app.main:app --reload
   ```

## Development Workflow

### Running Tests
```bash
# Run all tests with coverage
pytest --cov=app --cov-report=term-missing --cov-report=html

# View HTML coverage report
open htmlcov/index.html
```

### Code Quality
```bash
# Format code
black .
isort .

# Lint code
ruff check .
mypy app/
pylint app/

# Fix auto-fixable issues
ruff check . --fix
```

### Security Scanning
```bash
# Scan for security vulnerabilities
bandit -r app/
safety check
```

### Pre-commit Checks
Install pre-commit hooks (recommended):
```bash
pre-commit install
```

## CI/CD Pipeline

The project includes automated GitHub Actions workflows:

- **Tests** (`test.yml`): Runs pytest with coverage on Python 3.10, 3.11, 3.12
- **Lint** (`lint.yml`): Checks code quality with ruff, mypy, pylint, black, isort
- **Security** (`security.yml`): Scans for vulnerabilities with bandit, safety, CodeQL

All checks must pass before code can be merged to main/develop branches.

## Project Structure

```
votra.io/
├── .github/
│   ├── agents/              # Custom agent definitions
│   │   ├── README.md
│   │   └── fastapi-security-dev.md
│   └── workflows/           # GitHub Actions CI/CD
│       ├── test.yml
│       ├── lint.yml
│       └── security.yml
├── app/                     # Application code (to be created)
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   └── ...
├── tests/                   # Test files (to be created)
│   └── ...
├── .env.example            # Environment variables template
├── .gitignore
├── pyproject.toml          # Tool configurations
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── README.md
```

## Configuration

### Environment Variables

See `.env.example` for all available configuration options. Key variables:

- `SECRET_KEY`: Application secret for JWT tokens (required)
- `DATABASE_URL`: Database connection string (required)
- `CORS_ORIGINS`: Allowed CORS origins
- `DEBUG`: Enable debug mode (development only)

### GitHub Secrets

Set up required secrets using GitHub CLI:

```bash
# Authenticate with GitHub
gh auth login

# Set secrets
gh secret set SECRET_KEY --body "$(openssl rand -hex 32)"
gh secret set DATABASE_URL --body "postgresql://user:pass@host/db"

# List configured secrets
gh secret list
```

## Security

### Reporting Vulnerabilities

Please report security vulnerabilities to [security@votra.io](mailto:security@votra.io).

### Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Input validation with Pydantic
- SQL injection prevention
- CORS configuration
- Rate limiting
- Security headers
- Dependency vulnerability scanning

## Testing

### Test Coverage Target

We aim for **80% code coverage** minimum. Critical security and authentication code should have 100% coverage.

### Running Specific Tests
```bash
# Run unit tests only
pytest -m unit

# Run integration tests
pytest -m integration

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the guidelines
4. Ensure all tests pass and coverage is maintained
5. Ensure all linting and security checks pass
6. Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New features
- `fix:` Bug fixes
- `security:` Security improvements
- `test:` Test additions or changes
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `ci:` CI/CD changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions or support:
- Open an issue on GitHub
- Contact: support@votra.io
- Documentation: [docs.votra.io](https://docs.votra.io)

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
