# Semantic Versioning Guide

This repository uses automated semantic versioning based on conventional commits. When you push to the `main` branch, the semantic versioning GitHub Action will automatically:

1. Analyze commit messages
2. Determine the next version number
3. Create a git tag
4. Generate a CHANGELOG.md
5. Create a GitHub release

## Commit Message Format

Use conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types and Version Impact

| Type | Version Impact | Description |
|------|---------------|-------------|
| `feat` | **MINOR** (0.X.0) | A new feature |
| `fix` | **PATCH** (0.0.X) | A bug fix |
| `perf` | **PATCH** (0.0.X) | Performance improvement |
| `docs` | **PATCH** (0.0.X) | Documentation changes |
| `style` | **PATCH** (0.0.X) | Code style changes (formatting, etc.) |
| `refactor` | **PATCH** (0.0.X) | Code refactoring |
| `test` | **PATCH** (0.0.X) | Adding or updating tests |
| `build` | **PATCH** (0.0.X) | Build system changes |
| `ci` | **PATCH** (0.0.X) | CI/CD changes |
| `chore` | **NO RELEASE** | Maintenance tasks |
| `security` | **PATCH** (0.0.X) | Security fixes |

### Breaking Changes

To trigger a **MAJOR** version bump (X.0.0), include `BREAKING CHANGE:` in the commit footer or add `!` after the type:

```bash
feat!: redesign API authentication

BREAKING CHANGE: The authentication endpoint has changed from /auth to /api/v2/auth
```

## Examples

### Feature (Minor Version Bump)
```bash
git commit -m "feat(auth): add JWT token refresh endpoint

Implement automatic token refresh mechanism to improve user experience"
```
**Result:** 0.1.0 → 0.2.0

### Bug Fix (Patch Version Bump)
```bash
git commit -m "fix(api): prevent SQL injection in user query

Sanitize user inputs before database queries"
```
**Result:** 0.1.0 → 0.1.1

### Breaking Change (Major Version Bump)
```bash
git commit -m "feat(api)!: redesign authentication system

BREAKING CHANGE: Changed authentication from API keys to OAuth2.
All clients must update their authentication mechanism."
```
**Result:** 0.1.0 → 1.0.0

### Security Fix (Patch Version Bump)
```bash
git commit -m "security(deps): update dependencies with known vulnerabilities

Updated packages with CVE fixes"
```
**Result:** 0.1.0 → 0.1.1

### Chore (No Version Bump)
```bash
git commit -m "chore: update development dependencies"
```
**Result:** No release created

## Common Scopes

Use scopes to indicate which part of the project is affected:

- `auth` - Authentication/Authorization
- `api` - API endpoints
- `db` - Database
- `deps` - Dependencies
- `security` - Security-related changes
- `tests` - Test suite
- `ci` - CI/CD pipelines
- `docs` - Documentation

## Initial Version

If no version exists yet, the first release will be `1.0.0` when triggered by a feature commit.

## Viewing Releases

- **Tags:** `git tag -l`
- **GitHub Releases:** Visit the repository's "Releases" page
- **Changelog:** Check `CHANGELOG.md` (automatically generated)

## Best Practices

1. **One logical change per commit** - Makes version bumps predictable
2. **Write clear commit messages** - They become your release notes
3. **Use breaking changes sparingly** - Major version bumps require client updates
4. **Test before merging to main** - The version is created automatically on push
5. **Review generated CHANGELOG** - Verify release notes are clear

## Troubleshooting

### No version was created
- Check if your commit message follows the conventional format
- Verify the commit type triggers a release (not `chore`)
- Check the GitHub Actions logs for errors

### Wrong version bump
- Review your commit message type
- Check for unintended `BREAKING CHANGE:` in commit body
- Ensure the commit follows conventional commits specification

## References

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Semantic Release](https://semantic-release.gitbook.io/)
