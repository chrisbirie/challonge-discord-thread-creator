# Configuration Guide

Complete guide to configuring the Challonge Discord Thread Creator.

## Configuration File

The application uses a YAML configuration file (default: `config.yaml`). See [config.example.yaml](../config.example.yaml) for a complete example.

## Required Settings

### OAuth2 (Challonge API)

```yaml
oauth2:
  client_id: "your_client_id"
  client_secret: "your_client_secret"
```

**Required fields:**
- `client_id`: Your Challonge OAuth2 client ID
- `client_secret`: Your Challonge OAuth2 client secret

**Optional fields:**
- `token_url`: OAuth token endpoint (default: `https://api.challonge.com/oauth/token`)
- `scope`: OAuth scopes (default: none)
- `path_suffix`: API path suffix (default: `.json`)

### Challonge Tournament

```yaml
challonge:
  tournament: "your-tournament-slug"
```

**Required fields:**
- `tournament`: Tournament slug (from URL: `challonge.com/SLUG`)

**Optional fields:**
- `subdomain`: Organization subdomain (e.g., for `myorg.challonge.com/tournament`, use `myorg`)
- `base_url`: API base URL (default: `https://api.challonge.com/v2.1`)
- `page`: Pagination page number (default: `1`)
- `per_page`: Matches per page (default: `25`)
- `state`: Filter by match state - `"open"`, `"pending"`, `"complete"`, or `"all"` (default: all states)

### Discord (Required for Creating Threads)

```yaml
discord:
  bot_token: "your_bot_token"
  channel_id: 123456789012345678
```

**Required fields:**
- `bot_token`: Your Discord bot token
- `channel_id`: Discord channel ID where threads will be created

**Optional fields:**
- `thread_archive_minutes`: Auto-archive after N minutes (default: `10080` = 7 days)
- `role_ids_to_tag`: List of Discord role IDs to mention in threads

**Note:** Discord settings are not needed when using `--dry-run`.

## Optional Settings

### Runner Mapping (Discord Mentions)

Map Challonge usernames to Discord user IDs for @mentions:

```yaml
runner_map:
  "ChallongeUsername1": 123456789012345678
  "ChallongeUsername2": 987654321098765432
  "Player Three": 111222333444555666
```

**How it works:**
- If a player's Challonge username matches a key in `runner_map`, they'll be mentioned with their Discord ID
- If no match, their Challonge username will be used without mention
- Discord IDs can be found by right-clicking a user (with Developer Mode enabled)

### Custom Templates

Customize how thread names and messages appear:

```yaml
thread_name_template: "{round_label}: {p1_name} vs {p2_name}"

message_template: |
  Hi {p1_mention} vs {p2_mention}! {role_mentions}
  
  Please coordinate here to schedule your match for **{round_label}**.
  Match page: {match_url}
  
  Good luck!

round_label_template: "{stage} - {bracket} Round {abs_round}"
```

**Available Templates:**
- `thread_name_template`: Thread name format (max 100 chars, auto-truncated)
- `message_template`: Initial message posted in each thread
- `round_label_template`: Custom round label format (optional)

See [TEMPLATES.md](TEMPLATES.md) for all available template variables.

## Configuration Examples

### Example 1: Basic Swiss Tournament

```yaml
oauth2:
  client_id: "abc123"
  client_secret: "secret456"

challonge:
  tournament: "my-weekly-swiss"

discord:
  bot_token: "MTIzNDU2..."
  channel_id: 1234567890123456789
```

### Example 2: Organization Tournament with Mentions

```yaml
oauth2:
  client_id: "abc123"
  client_secret: "secret456"

challonge:
  tournament: "spring-championship"
  subdomain: "myorg"
  state: "open"

discord:
  bot_token: "MTIzNDU2..."
  channel_id: 1234567890123456789
  thread_archive_minutes: 1440  # 1 day
  role_ids_to_tag:
    - 987654321098765432  # @Admins
    - 111222333444555666  # @TO Team

runner_map:
  "Alice": 222333444555666777
  "Bob": 333444555666777888
```

### Example 3: Multiple Tournaments (Separate Configs)

Create multiple config files:

**config-tournament-a.yaml:**
```yaml
oauth2:
  client_id: "abc123"
  client_secret: "secret456"

challonge:
  tournament: "tournament-a"

discord:
  bot_token: "MTIzNDU2..."
  channel_id: 1111111111111111111
```

**config-tournament-b.yaml:**
```yaml
oauth2:
  client_id: "abc123"
  client_secret: "secret456"

challonge:
  tournament: "tournament-b"

discord:
  bot_token: "MTIzNDU2..."
  channel_id: 2222222222222222222
```

**Usage:**
```bash
tourney-threads --config config-tournament-a.yaml
tourney-threads --config config-tournament-b.yaml
```

### Example 4: Custom Message Template

```yaml
# ... oauth2, challonge, discord settings ...

message_template: |
  🎮 **Match Ready!**
  
  {p1_mention} 🆚 {p2_mention}
  
  **Round:** {round_label}
  **Match ID:** {match_id}
  **Status:** {match_state}
  **Link:** {match_url}
  
  📅 **Scheduling Instructions:**
  1. Post 3-4 time slots you're available (include timezone!)
  2. Agree on a time that works for both
  3. Tag {role_mentions} to confirm
  4. Report results on Challonge when done
  
  Good luck! 🏆
```

## Environment-Specific Configurations

### Development vs Production

Use separate config files:

```bash
# Development (with test data)
tourney-threads --config config.dev.yaml --dry-run

# Production
tourney-threads --config config.prod.yaml
```

### Security Best Practices

1. **Never commit `config.yaml`** (it contains secrets)
2. Keep `config.example.yaml` as a template (no real credentials)
3. Use environment variables in production:
   ```python
   # Custom wrapper script
   import os
   import yaml
   
   config = yaml.safe_load(open('config.yaml'))
   config['oauth2']['client_secret'] = os.environ['CHALLONGE_SECRET']
   config['discord']['bot_token'] = os.environ['DISCORD_TOKEN']
   ```

## Validation

The application validates your configuration on startup:

**Required checks:**
- `oauth2.client_id` must be present
- `oauth2.client_secret` must be present
- `challonge.tournament` must be present
- `discord.bot_token` must be present (unless using `--dry-run`)
- `discord.channel_id` must be present (unless using `--dry-run`)

**Error messages:**
```
ValueError: Missing required oauth2.client_id in config
ValueError: Missing required discord.bot_token in config
```

## See Also

- [INSTALLATION.md](INSTALLATION.md) - Installation instructions
- [USAGE.md](USAGE.md) - Usage examples and CLI reference
- [TEMPLATES.md](TEMPLATES.md) - Template variable reference
- [../config.example.yaml](../config.example.yaml) - Full configuration example
