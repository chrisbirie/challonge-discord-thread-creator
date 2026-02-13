# Documentation Index

Complete documentation for the Tourney Threads Bot (Challonge ➜ Discord).

## Getting Started

New to the project? Start here:

1. **[Installation Guide](INSTALLATION.md)** - Set up your environment, install dependencies, configure Discord and Challonge
2. **[Configuration Reference](CONFIGURATION.md)** - Understand all configuration options
3. **[Usage Guide](USAGE.md)** - Learn CLI commands and common workflows

## Reference Documentation

- **[Template Variables](TEMPLATES.md)** - Customize thread names and messages with template variables
- **[Troubleshooting](TROUBLESHOOTING.md)** - Solutions to common issues and error messages

## Developer Documentation

- **[Development Guide](DEVELOPMENT.md)** - Set up development environment, run tests, code quality standards
- **[Contributing Guidelines](../CONTRIBUTING.md)** - How to contribute (bug reports, features, code)

## Documentation Overview

### [Installation Guide](INSTALLATION.md)

**What's inside:**
- Prerequisites (Python, Discord bot, Challonge OAuth2)
- Installation methods (from source, future PyPI)
- Setting up Discord bot with proper permissions
- Creating Challonge OAuth2 application
- Configuration file setup
- Verification steps
- Common installation issues

**When to read:** Setting up the project for the first time

---

### [Configuration Reference](CONFIGURATION.md)

**What's inside:**
- Required configuration fields (OAuth2, Challonge, Discord)
- Optional settings (runner_map, templates, pagination)
- Configuration examples for different tournament types
- Security best practices
- Validation and troubleshooting

**When to read:** Configuring the bot for your tournament or Discord server

---

### [Usage Guide](USAGE.md)

**What's inside:**
- CLI command reference
- Common workflows (preview, debug, override)
- Advanced usage (multiple tournaments, automation)
- Automation scripts (Bash, PowerShell)
- Typical tournament workflow
- Exit codes and error handling

**When to read:** Using the bot day-to-day, automating tournament workflows

---

### [Template Variables](TEMPLATES.md)

**What's inside:**
- Complete variable reference (player, round, match, other)
- Template examples (thread names, messages, round labels)
- Special cases (TBD players, losers bracket)
- Length limits and Discord markdown
- Testing templates

**When to read:** Customizing how threads and messages appear

---

### [Troubleshooting](TROUBLESHOOTING.md)

**What's inside:**
- Configuration issues (missing fields, YAML errors)
- OAuth/API issues (authentication, rate limiting)
- Discord issues (permissions, mentions, threads)
- Match data issues (no matches, wrong names, TBD players)
- Performance issues
- Common error messages reference

**When to read:** Encountering errors or unexpected behavior

---

### [Development Guide](DEVELOPMENT.md)

**What's inside:**
- Development environment setup
- Project structure
- Running tests (unit, integration, E2E)
- Code quality tools (Black, Ruff, MyPy, Bandit)
- Making changes and contributing
- CI/CD pipeline
- Release process

**When to read:** Contributing to the project or developing new features

---

## Quick Reference

### Most Common Questions

| Question | Answer |
|----------|--------|
| How do I install? | [Installation Guide](INSTALLATION.md) |
| How do I configure OAuth2? | [Configuration Reference](CONFIGURATION.md#oauth2-required) |
| What are all the CLI options? | [Usage Guide](USAGE.md#cli-reference) |
| How do I customize thread names? | [Template Variables](TEMPLATES.md) |
| Why isn't it creating threads? | [Troubleshooting - Discord Issues](TROUBLESHOOTING.md#discord-issues) |
| How do I mention players? | [Configuration Reference](CONFIGURATION.md#runner-map-optional) |
| How do I contribute? | [Development Guide](DEVELOPMENT.md) |

### Quick Commands

```bash
# Preview threads
tourney-threads --dry-run

# Debug issues
tourney-threads --debug --dry-run

# Create threads
tourney-threads

# Different config
tourney-threads --config prod.yaml

# Different tournament
tourney-threads --tournament my-event
```

## External Links

- **GitHub Repository:** https://github.com/chrisbirie/challonge-discord-thread-creator
- **Issues:** https://github.com/chrisbirie/challonge-discord-thread-creator/issues
- **Challonge API Docs:** https://api.challonge.com/docs/v2.1
- **Discord Developer Portal:** https://discord.com/developers/applications
