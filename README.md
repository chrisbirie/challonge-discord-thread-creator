# Tourney Threads Bot (Challonge ➜ Discord)

Automatically create Discord threads for tournament matchups from Challonge. Fetch matches via the Challonge v2.1 API and generate organized Discord threads for player coordination.

## Features

- 🔐 **OAuth2 Authentication** - Secure integration with Challonge API
- 🎯 **Stage Detection** - Automatically detects Swiss, Groups, or Elimination formats
- ✏️ **Customizable Templates** - Configure thread names and messages with variables
- 👀 **Dry-run Mode** - Preview threads before creating them
- 💬 **Discord Mentions** - Tag players and roles in threads
- 📄 **Pagination Support** - Handle large tournaments efficiently

## Quick Start

```bash
# 1. Install
git clone https://github.com/chrisbirie/challonge-discord-thread-creator.git
cd challonge-discord-thread-creator
pip install -e .

# 2. Configure
cp config.example.yaml config.yaml
# Edit config.yaml with your credentials

# 3. Preview
tourney-threads --dry-run

# 4. Create threads
tourney-threads
```

📚 **See the [Installation Guide](docs/INSTALLATION.md) for detailed setup instructions.**

## Documentation

📚 **Complete documentation is available in the [docs/](docs/) directory:**

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup, prerequisites, Discord/Challonge configuration
- **[Configuration Reference](docs/CONFIGURATION.md)** - Complete guide to all config options with examples
- **[Usage Guide](docs/USAGE.md)** - CLI reference, common workflows, automation
- **[Template Variables](docs/TEMPLATES.md)** - Customize thread names and messages
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing, testing, code quality

## Basic Usage

```bash
# Preview threads without creating them
tourney-threads --dry-run

# Create threads for a tournament
tourney-threads

# Use a different config file
tourney-threads --config prod.yaml

# Override tournament from config
tourney-threads --tournament my-event-2026

# Debug mode (shows API responses)
tourney-threads --debug --dry-run
```

📘 **See the [Usage Guide](docs/USAGE.md) for detailed examples and workflows.**

## Configuration

The tool uses a YAML configuration file (default: `config.yaml`). See [config.example.yaml](config.example.yaml) for a complete example.

### Minimal Configuration

```yaml
oauth2:
  client_id: "your_client_id"
  client_secret: "your_client_secret"

challonge:
  tournament: "your-tournament-slug"

discord:
  bot_token: "your_bot_token"
  channel_id: 123456789012345678
```

### Optional Customization

```yaml
# Map Challonge usernames to Discord user IDs
runner_map:
  "ChallongeUsername": 123456789012345678

# Customize thread names and messages
thread_name_template: "{round_label}: {p1_name} vs {p2_name}"
message_template: |
  Hi {p1_mention} vs {p2_mention}!
  This is your scheduling thread for {round_label}.

# Filter matches by state
challonge:
  state: "open"  # open, pending, complete, or all
```

📖 **See the [Configuration Reference](docs/CONFIGURATION.md) for all available options.**  
✏️ **See the [Template Variables](docs/TEMPLATES.md) for customization options.**

## Development

### Quick Start

```bash
# Clone and install
git clone https://github.com/chrisbirie/challonge-discord-thread-creator.git
cd challonge-discord-thread-creator
pip install -e ".[dev]"

# Run tests
pytest

# Run linting and formatting
black src tests
ruff check src tests
mypy src
```

### Testing

```bash
# Run all tests with coverage
pytest --cov=tourney_threads --cov-report=html

# Run specific test categories
pytest tests/test_tourney_threads/integration/
pytest tests/test_tourney_threads/e2e/
```

**Test Coverage:** 99% (115 tests)

### CI/CD

GitHub Actions automatically runs on all PRs and commits to `main`:
- ✅ Code Quality (Ruff, Black, isort, MyPy)
- ✅ Security (Bandit, Safety)
- ✅ Tests (Python 3.10, 3.11, 3.12)
- ✅ Build validation
- ✅ Integration tests

📘 **See the [Development Guide](docs/DEVELOPMENT.md) for detailed information on contributing, testing, and code quality standards.**

## Troubleshooting

### Quick Fixes

**Configuration errors:**
```bash
# Verify YAML syntax
python -c "import yaml; print(yaml.safe_load(open('config.yaml')))"

# Check for missing required fields
tourney-threads --debug --dry-run
```

**API issues:**
```bash
# Test OAuth credentials
tourney-threads --debug --dry-run

# Check tournament slug
# From URL: https://challonge.com/my-tournament
# Slug is: my-tournament
```

**Discord issues:**
- Ensure bot has "Create Public Threads" permission
- Verify `channel_id` is a text channel
- Check bot is in the Discord server

🔧 **See the [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for detailed solutions to common issues.**

## Project Structure

```
challonge-discord-thread-creator/
├── docs/                    # Documentation
│   ├── INSTALLATION.md
│   ├── CONFIGURATION.md
│   ├── USAGE.md
│   ├── TEMPLATES.md
│   ├── TROUBLESHOOTING.md
│   └── DEVELOPMENT.md
├── src/tourney_threads/     # Main source code
│   ├── app.py              # Application logic
│   └── version.py
├── tests/                   # Test suite (99% coverage)
│   └── test_tourney_threads/
│       ├── api/
│       ├── config/
│       ├── discord_client/
│       ├── utils/
│       ├── integration/
│       └── e2e/
├── config.example.yaml      # Example configuration
├── pyproject.toml          # Project metadata
└── README.md               # This file
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and add tests
4. Run tests and linting: `pytest && black src tests && ruff check src tests`
5. Commit: `git commit -m "feat: add new feature"`
6. Push and create a Pull Request

📖 **See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.**  
🛠️ **See the [Development Guide](docs/DEVELOPMENT.md) for development setup and workflows.**

## License

See LICENSE file for details.
