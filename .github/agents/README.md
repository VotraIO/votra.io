# Custom Agents for Votra.io

This directory contains custom agent definitions for specialized development tasks in the Votra.io project.

## Available Agents

### FastAPI Security Developer (`fastapi-security-dev.md`)

**Purpose**: Expert FastAPI Python developer specializing in secure, well-tested, production-ready code.

**Key Capabilities**:
- ✅ Secure FastAPI development following OWASP guidelines
- ✅ Automated unit test generation with 80% coverage target
- ✅ Security scanning (bandit, safety)
- ✅ Code quality enforcement (black, ruff, mypy, pylint)
- ✅ GitHub Actions CI/CD setup
- ✅ GitHub secrets management
- ✅ Dependency vulnerability scanning

**When to Use**:
- Creating or modifying FastAPI endpoints
- Implementing authentication/authorization
- Setting up new API routes or services
- Adding security features
- Creating or updating tests
- Setting up CI/CD pipelines
- Managing application secrets

**Example Usage**:

1. **Create a new API endpoint**:
   ```
   @fastapi-security-dev Please create a new REST API endpoint for user registration 
   with email verification. Include proper validation, security measures, and tests.
   ```

2. **Add authentication**:
   ```
   @fastapi-security-dev Implement JWT-based authentication for the API with 
   refresh tokens. Include security best practices and comprehensive tests.
   ```

3. **Security audit**:
   ```
   @fastapi-security-dev Review the authentication code in app/routers/auth.py 
   for security vulnerabilities and suggest improvements with tests.
   ```

4. **Set up CI/CD**:
   ```
   @fastapi-security-dev Set up GitHub Actions workflows for testing, linting, 
   and security scanning with 80% coverage requirement.
   ```

## How Custom Agents Work

Custom agents are specialized AI assistants with deep expertise in specific domains. They:

1. **Have domain expertise**: Pre-configured with best practices, patterns, and guidelines
2. **Follow standards**: Enforce coding standards, security practices, and testing requirements
3. **Iterate**: Work through problems step-by-step, testing after each change
4. **Ensure quality**: Run linters, formatters, security scans, and tests automatically

## Best Practices for Using Agents

### Be Specific
❌ "Add authentication"
✅ "Implement OAuth2 password flow with JWT tokens for user authentication, including password hashing with bcrypt and token refresh mechanism"

### Provide Context
Include relevant information about:
- Existing code structure
- Integration points
- Specific requirements
- Constraints or preferences

### Request Tests
Agents are configured to write tests, but be explicit:
✅ "Include unit tests with at least 90% coverage"
✅ "Add security tests for common attack vectors"

### Security Considerations
For any security-related work, mention:
- Data sensitivity
- Compliance requirements (GDPR, HIPAA, etc.)
- Authentication/authorization needs
- External service integrations

### Review Agent Output
While agents are expert-level, always:
1. Review the generated code
2. Understand the security implications
3. Verify tests cover edge cases
4. Check that secrets are properly managed

## Agent Configuration

Agents are configured using Markdown files in this directory. Each agent definition includes:

- **Identity**: Role and expertise area
- **Responsibilities**: Core tasks and duties
- **Best Practices**: Domain-specific guidelines
- **Tools**: Required dependencies and utilities
- **Workflows**: Step-by-step processes
- **Examples**: Common patterns and code samples
- **Checklists**: Quality gates and verification steps

## Adding New Agents

To create a new custom agent:

1. Create a new `.md` file in this directory
2. Define the agent's expertise and responsibilities
3. Include relevant best practices and examples
4. Add quality checklists and verification steps
5. Document when and how to use the agent

See `fastapi-security-dev.md` as a reference template.

## Environment Setup

Before using the FastAPI agent, ensure you have:

### Required Tools
```bash
# Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install GitHub CLI
# macOS: brew install gh
# Linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md
# Windows: https://github.com/cli/cli/releases
```

### GitHub CLI Setup
```bash
# Authenticate
gh auth login

# Verify access
gh auth status

# Set secrets
gh secret set DATABASE_URL --body "postgresql://user:pass@localhost/db"
gh secret set SECRET_KEY --body "your-secret-key-here"
```

### Local Development
```bash
# Run tests with coverage
pytest --cov=app --cov-report=term-missing --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Run linting
ruff check .
mypy app/
pylint app/

# Format code
black .
isort .

# Security scan
bandit -r app/
safety check
```

## Troubleshooting

### Agent Not Following Guidelines
- Check that the agent file is in `.github/agents/`
- Ensure the file is properly formatted Markdown
- Be more explicit in your request

### Tests Failing
- Review the test output carefully
- Check that dependencies are installed
- Verify database/service connections
- Ensure environment variables are set

### Coverage Below 80%
- Ask the agent to add more test cases
- Focus on untested branches and edge cases
- Use `--cov-report=html` to see what's missing

### Security Scan Failures
- Review the bandit/safety output
- Ask the agent to fix specific vulnerabilities
- Update dependencies if needed
- Use `# nosec` sparingly and document why

## Resources

### FastAPI
- [Official Documentation](https://fastapi.tiangolo.com/)
- [Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)

### Security
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

### Testing
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

### Tools
- [Black Code Formatter](https://black.readthedocs.io/)
- [Ruff Linter](https://docs.astral.sh/ruff/)
- [MyPy Type Checker](https://mypy.readthedocs.io/)
- [Bandit Security Scanner](https://bandit.readthedocs.io/)

## Contributing

To improve or extend the custom agents:

1. Test changes thoroughly
2. Update documentation
3. Add examples if introducing new capabilities
4. Submit a pull request with clear description

## Support

For questions or issues with custom agents:
1. Review this README and the agent definition
2. Check the troubleshooting section
3. Open an issue with details about the problem
