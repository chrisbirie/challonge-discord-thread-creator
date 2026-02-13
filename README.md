# Tourney Threads Bot (Challonge ➜ Discord)

Create Discord threads for tournament matchups pulled from Challonge v2.1 API. This tool automatically fetches matches from a tournament and creates Discord threads for scheduling and communication.

## Features

- **OAuth2 Authentication**: Secure client credentials flow with Challonge API
- **Stage Detection**: Automatically detects Swiss, Groups, or Elimination stages
- **Customizable Templates**: Configure thread names and messages with template variables
- **Dry-run Mode**: Preview threads before creating them
- **Discord Mentions**: Map Challonge usernames to Discord user IDs for @mentions
- **Role Tagging**: Automatically tag Discord roles in thread messages
- **Pagination Support**: Configure page size and filters for match retrieval

## Quick Start

### Prerequisites

- Python 3.10+ recommended
- Discord bot with appropriate permissions (create threads, mention roles)
- Challonge API OAuth2 credentials

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd tourney_threads
```

2. Create and activate a virtual environment (recommended):
```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on macOS/Linux
source .venv/bin/activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

This installs the package and all dependencies, making the `tourney-threads` command available.

4. Configure the application:
```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your credentials
```

5. Run a dry-run to preview:
```bash
tourney-threads --dry-run
```

6. Create threads:
```bash
tourney-threads
```

**Note:** If you haven't activated your virtual environment, use the full path:
```bash
# Windows
.venv\Scripts\tourney-threads.exe --dry-run

# macOS/Linux
.venv/bin/tourney-threads --dry-run
```

## CLI Usage

```bash
tourney-threads [OPTIONS]
```

### Command Line Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--config <path>` | Path to YAML configuration file | `config.yaml` | `--config prod.yaml` |
| `--tournament <slug>` | Override tournament slug from config file | From config | `--tournament my-event-2026` |
| `--debug` | Print raw JSON API responses and match summary | Disabled | `--debug` |
| `--dry-run` | Preview threads without creating them on Discord | Disabled | `--dry-run` |

### Most Common Commands

#### 1. Preview Before Creating (Recommended First Step)
```bash
tourney-threads --dry-run
```
**What it does:** Shows exactly what threads would be created without actually posting to Discord. Perfect for verifying your configuration and seeing what the output will look like.

**Example output:**
```
=== DRY RUN: Would create 8 threads ===
Thread: "Winners R1: Alice vs Bob"
Message: Hi @Alice vs @Bob! This is your scheduling thread for Winners R1.
---
Thread: "Winners R1: Charlie vs Dana"
Message: Hi @Charlie vs @Dana! This is your scheduling thread for Winners R1.
...
```

#### 2. Create Threads (Production)
```bash
tourney-threads
```
**What it does:** Fetches matches from Challonge and creates Discord threads in the configured channel. This is the main production command after you've verified everything with `--dry-run`.

#### 3. Debug API Issues
```bash
tourney-threads --debug --dry-run
```
**What it does:** Shows detailed API responses and match data structure. Use this when:
- Troubleshooting API authentication issues
- Verifying match data is being fetched correctly
- Understanding the tournament structure (Swiss vs Elimination, etc.)

**Example output:**
```
=== API Response (raw JSON) ===
{"data": [{"type": "match", "id": "12345", ...}], "included": [...]}

=== Match Summary ===
Found 8 matches:
- Match #1: Alice vs Bob (Round 1, Winners)
- Match #2: Charlie vs Dana (Round 1, Winners)
...
```

#### 4. Override Tournament
```bash
tourney-threads --tournament winter-championship-2026
```
**What it does:** Uses a different tournament than specified in `config.yaml`. Useful for:
- Managing multiple tournaments with the same config file
- Quick testing with different tournaments
- Running automated scripts across multiple events

#### 5. Use Custom Config File
```bash
tourney-threads --config production.yaml
```
**What it does:** Loads configuration from a different file. Useful for:
- Separate development and production configurations
- Managing multiple Discord servers or tournaments
- Testing configuration changes without modifying your main config

### Advanced Usage Examples

#### Test new tournament with debug info
```bash
tourney-threads --tournament new-event --debug --dry-run
```
Shows API data and thread preview for a different tournament.

#### Production deployment with custom config
```bash
tourney-threads --config /etc/tourney/prod.yaml
```
Uses absolute path to configuration file for production deployments.

#### Combine all options for maximum verbosity
```bash
tourney-threads --config test.yaml --tournament debug-tourney --debug --dry-run
```
Perfect for comprehensive testing and troubleshooting.

### Workflow Recommendations

**First time setup:**
```bash
# 1. Copy example config
cp config.example.yaml config.yaml

# 2. Edit config.yaml with your credentials
# (Add your OAuth tokens, Discord bot token, tournament slug, etc.)

# 3. Test with dry-run
tourney-threads --dry-run

# 4. Add --debug if something looks wrong
tourney-threads --debug --dry-run

# 5. Create threads once everything looks good
tourney-threads
```

**Regular tournament operation:**
```bash
# Preview threads before each round
tourney-threads --dry-run

# Create threads when ready
tourney-threads
```

**Managing multiple tournaments:**
```bash
# Preview tournament A
tourney-threads --tournament event-a --dry-run

# Create threads for tournament A
tourney-threads --tournament event-a

# Switch to tournament B
tourney-threads --tournament event-b --dry-run
tourney-threads --tournament event-b
```

## Configuration

See [config.example.yaml](config.example.yaml) for a complete example. Place your configuration in `config.yaml`.

### Required Settings

#### OAuth2 (Challonge API)
```yaml
oauth2:
  client_id: "your_client_id"
  client_secret: "your_client_secret"
  token_url: "https://api.challonge.com/oauth/token"  # optional
  scope: null  # optional
  path_suffix: ".json"  # optional
```

#### Challonge Tournament
```yaml
challonge:
  tournament: "your-tournament-slug"
  subdomain: ""  # optional, for organization tournaments
  base_url: "https://api.challonge.com/v2.1"  # optional
  page: 1  # pagination
  per_page: 25  # matches per page
  state: "open"  # optional: open, pending, complete, all
```

#### Discord (not needed for dry-run)
```yaml
discord:
  bot_token: "your_bot_token"
  channel_id: 123456789  # text channel ID where threads will be created
  thread_archive_minutes: 10080  # 7 days
  role_ids_to_tag:  # optional
    - 987654321
```

### Optional Settings

#### Runner Mapping (for Discord mentions)
```yaml
runner_map:
  "ChallongeUsername": 123456789  # Discord user ID
  "AnotherPlayer": 987654321
```

#### Custom Templates
```yaml
# Thread name template (truncated to 100 chars)
thread_name_template: "{round_label}: {p1_name} vs {p2_name}"

# Initial message template
message_template: |
  Hi {p1_mention} vs {p2_mention}! {role_mentions}
  This is your scheduling thread for {round_label}.

# Custom round label template (optional)
round_label_template: "{stage} - {bracket} Round {abs_round}"
```

**Template Variables:**

*Player Information:*
- `{p1_name}`, `{p2_name}`: Player usernames (or "TBD" if not set)
- `{p1_mention}`, `{p2_mention}`: Discord mentions (<@user_id>) or usernames if no mapping

*Round Information:*
- `{round_label}`: Full round label (e.g., "Winners R1", "Swiss R3", "Losers R2")
- `{stage}`: Tournament stage type ("Swiss", "Groups", "Elimination", or empty)
- `{bracket}`: Bracket name ("Winners", "Losers", or "Round")
- `{round}`: Raw round number from Challonge (positive for winners, negative for losers)
- `{abs_round}`: Absolute round number (always positive)

*Match Information:*
- `{match_id}`: Challonge match ID (useful for reference/tracking)
- `{match_state}`: Match status ("open", "pending", "complete")
- `{match_url}`: Direct link to match on Challonge (e.g., "https://challonge.com/tournament/matches/12345")
- `{tournament_name}`: Tournament slug from your config

*Other:*
- `{role_mentions}`: Space-separated Discord role mentions (e.g., "<@&123> <@&456>")

## Project Structure

The codebase is organized into the following modules:

```
src/tourney_threads/
├── api/                    # Challonge API integration
│   ├── __init__.py
│   ├── oauth.py           # OAuth2 authentication
│   ├── challonge.py       # API client
│   └── models.py          # Match and Participant dataclasses
├── discord_client/        # Discord integration
│   ├── __init__.py
│   ├── thread_manager.py  # Thread creation logic
│   └── formatters.py      # Template formatting
├── utils/                 # Utilities
│   ├── __init__.py
│   ├── names.py          # Name cleaning and mentions
│   └── rounds.py         # Round labeling
├── config/               # Configuration handling
│   ├── __init__.py
│   ├── constants.py      # Default values
│   └── loader.py         # Config loading and validation
├── app.py               # Main entry point
├── cli.py               # Command-line interface
└── version.py           # Version info
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_logic.py

# Run with coverage
pytest --cov=tourney_threads
```

### Code Style

The project uses:
- **Type hints** throughout for better IDE support
- **Dataclasses** for structured data (Match, Participant)
- **Google-style docstrings** for documentation
- **Modular architecture** for maintainability

## Notes

- For double-elimination tournaments, losers bracket rounds use negative integers
- The `(invitation pending)` suffix is automatically removed from participant names
- Thread names are automatically truncated to Discord's 100-character limit
- Error handling includes per-thread try-catch to prevent cascading failures
- Stage detection is best-effort; falls back gracefully if detection fails

## Troubleshooting

### Configuration Errors

If you see `ValueError: Missing required oauth2.client_id`:
- Ensure your `config.yaml` has all required fields
- Check for typos in configuration keys

### API Errors

If you see `RuntimeError: OAuth token request failed`:
- Verify your client_id and client_secret are correct
- Check that your OAuth application is active in Challonge

### Discord Errors

If threads aren't being created:
- Verify the bot has "Create Public Threads" permission
- Ensure the channel_id points to a text channel
- Check that the bot is in the server

## License

See LICENSE file for details.
