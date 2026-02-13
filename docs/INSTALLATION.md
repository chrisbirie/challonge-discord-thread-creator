# Installation Guide

This guide covers how to install and set up the Challonge Discord Thread Creator.

## Prerequisites

- **Python 3.10 or higher** (3.11 or 3.12 recommended)
- **Discord Bot** with appropriate permissions
- **Challonge OAuth2 Credentials** (client ID and secret)

### Getting Challonge OAuth2 Credentials

1. Log in to [Challonge](https://challonge.com)
2. Go to Settings → Developer Settings → OAuth Applications
3. Create a new OAuth application
4. Save your Client ID and Client Secret

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Navigate to "Bot" and create a bot
4. Copy the bot token
5. Enable "Message Content Intent" if you need it
6. Invite the bot to your server with these permissions:
   - Send Messages
   - Create Public Threads
   - Mention @everyone, @here, and All Roles (if using role mentions)

## Installation Methods

### Method 1: Install from Source (Recommended for Development)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/chrisbirie/challonge-discord-thread-creator.git
   cd challonge-discord-thread-creator
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate on Windows
   .venv\Scripts\activate

   # Activate on macOS/Linux
   source .venv/bin/activate
   ```

3. **Install the package in editable mode:**
   ```bash
   pip install -e .
   ```

   This makes the `tourney-threads` command available globally (within your virtual environment).

### Method 2: Install from PyPI (When Published)

```bash
# Once published to PyPI
pip install tourney-threads
```

## Configuration

1. **Copy the example configuration:**
   ```bash
   cp config.example.yaml config.yaml
   ```

2. **Edit `config.yaml` with your credentials:**
   ```yaml
   oauth2:
     client_id: "YOUR_CHALLONGE_CLIENT_ID"
     client_secret: "YOUR_CHALLONGE_CLIENT_SECRET"

   challonge:
     tournament: "your-tournament-slug"

   discord:
     bot_token: "YOUR_DISCORD_BOT_TOKEN"
     channel_id: 123456789012345678  # Your Discord channel ID
   ```

3. **Find your Discord Channel ID:**
   - Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
   - Right-click on the channel → Copy ID

## Verify Installation

Test that everything is working:

```bash
# Run a dry-run to preview (doesn't post to Discord)
tourney-threads --dry-run

# If you see thread previews, you're good to go!
```

## Running Without Virtual Environment Activation

If you don't want to activate the virtual environment every time:

```bash
# Windows
.venv\Scripts\tourney-threads.exe --dry-run

# macOS/Linux
.venv/bin/tourney-threads --dry-run
```

## Troubleshooting

### Command Not Found

If you get "command not found" or "tourney-threads is not recognized":

1. Make sure your virtual environment is activated
2. Or use the full path to the command (see above)
3. Verify installation: `pip show tourney-threads`

### Import Errors

If you see import errors:

1. Make sure you're in the virtual environment
2. Reinstall: `pip install -e .`
3. Check Python version: `python --version` (must be 3.10+)

### Permission Errors

If you get permission errors on Windows:

1. Run terminal as administrator, or
2. Use `pip install --user -e .`

## Next Steps

- See [USAGE.md](USAGE.md) for how to use the tool
- See [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration options
- See [DEVELOPMENT.md](DEVELOPMENT.md) for development setup
