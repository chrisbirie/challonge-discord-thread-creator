# Contributing to Tourney Threads

Thank you for your interest in contributing! We welcome contributions of all kinds: bug reports, feature requests, documentation improvements, and code contributions.

## Quick Start

📘 **See the complete [Development Guide](docs/DEVELOPMENT.md) for detailed information on:**
- Development environment setup
- Project structure
- Running tests and code quality checks
- Making changes and submitting PRs
- CI/CD pipeline

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

Found a bug? Please [open an issue](https://github.com/chrisbirie/challonge-discord-thread-creator/issues) with:
- Description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Relevant logs (use `--debug` flag)

### Suggesting Features

Have an idea? [Open a feature request](https://github.com/chrisbirie/challonge-discord-thread-creator/issues) describing:
- The problem you're trying to solve
- Your proposed solution
- Alternative solutions you've considered
- Why this would be useful to others

### Contributing Code

**Quick workflow:**

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/challonge-discord-thread-creator.git
cd challonge-discord-thread-creator

# 2. Create a virtual environment and install
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# 3. Create a feature branch
git checkout -b feature/your-feature-name

# 4. Make your changes, add tests

# 5. Run checks
pytest  # Tests
black src tests  # Format
ruff check src tests  # Lint
mypy src  # Type check

# 6. Commit and push
git commit -m "feat: add new feature"
git push origin feature/your-feature-name

# 7. Create a Pull Request on GitHub
```

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
- `feat: add support for multiple tournaments`
- `fix: handle TBD players correctly`
- `docs: update installation instructions`

### Pull Request Checklist

Before submitting your PR, ensure:

- ✅ All tests pass: `pytest`
- ✅ Code is formatted: `black src tests`
- ✅ Linting passes: `ruff check src tests`
- ✅ Type checking passes: `mypy src`
- ✅ Coverage is maintained: `pytest --cov=tourney_threads`
- ✅ Documentation is updated if needed
- ✅ Commit messages follow convention

### Documentation

When updating documentation:

- **[README.md](README.md)** - Brief overview, links to detailed docs
- **[docs/INSTALLATION.md](docs/INSTALLATION.md)** - Installation and setup
- **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)** - Configuration options
- **[docs/USAGE.md](docs/USAGE.md)** - CLI usage and workflows
- **[docs/TEMPLATES.md](docs/TEMPLATES.md)** - Template variables
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Development guide
- **[config.example.yaml](config.example.yaml)** - Configuration examples

## Security

### Reporting Security Vulnerabilities

**⚠️ DO NOT open public issues for security vulnerabilities.**

If you discover a security issue, please report it privately:

1. **Email:** [maintainer email] (or use GitHub's private vulnerability reporting)
2. **Include:**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond as quickly as possible to address security issues.

### Security Best Practices

- Never commit credentials or secrets to the repository
- Use environment variables or secure config files for sensitive data
- Keep dependencies up to date
- Run security checks: `bandit -r src` and `safety check`

## Getting Help

Need help or have questions?

- 📖 **Documentation:** Check [docs/](docs/) for guides
- 🐛 **Bug Reports:** [Open an issue](https://github.com/chrisbirie/challonge-discord-thread-creator/issues)
- 💡 **Feature Requests:** [Open an issue](https://github.com/chrisbirie/challonge-discord-thread-creator/issues)
- 💬 **Questions:** [GitHub Discussions](https://github.com/chrisbirie/challonge-discord-thread-creator/discussions)
- 🔧 **Troubleshooting:** See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## Development Resources

- **[Development Guide](docs/DEVELOPMENT.md)** - Complete development documentation
- **[GitHub Actions](.github/workflows/ci.yml)** - CI/CD pipeline configuration
- **[pyproject.toml](pyproject.toml)** - Project metadata and tool configurations
- **[Tests](tests/)** - Test suite with 99% coverage

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes (for significant contributions)

---

Thank you for contributing to Tourney Threads! 🎉

For detailed development information, see the **[Development Guide](docs/DEVELOPMENT.md)**.
