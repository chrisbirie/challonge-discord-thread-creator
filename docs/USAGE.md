# Usage Guide

Complete guide to using the Challonge Discord Thread Creator.

## Basic Usage

```bash
tourney-threads [OPTIONS]
```

## Command Line Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--config <path>` | Path to YAML configuration file | `config.yaml` | `--config prod.yaml` |
| `--tournament <slug>` | Override tournament slug from config file | From config | `--tournament my-event-2026` |
| `--debug` | Print raw JSON API responses and match summary | Disabled | `--debug` |
| `--dry-run` | Preview threads without creating them on Discord | Disabled | `--dry-run` |

## Common Workflows

### 1. Preview Threads (Recommended First Step)

**Always start with a dry-run to verify everything looks correct:**

```bash
tourney-threads --dry-run
```

**Output:**
```
=== DRY RUN: Discord threads preview ===

THREAD: Winners R1: Alice vs Bob
MESSAGE:
Hi @Alice vs @Bob! @TournamentAdmins
This is your scheduling thread for Winners R1.
Match page: https://challonge.com/tournament/matches/12345

THREAD: Winners R1: Charlie vs Dana
MESSAGE:
Hi @Charlie vs @Dana! @TournamentAdmins
This is your scheduling thread for Winners R1.
Match page: https://challonge.com/tournament/matches/12346

=== END DRY RUN ===
```

### 2. Create Threads (Production)

**Once everything looks good, create the threads:**

```bash
tourney-threads
```

**What happens:**
- Fetches matches from Challonge via OAuth2
- Creates a Discord thread for each match
- Posts the configured message in each thread
- Mentions players (if mapped) and roles

### 3. Debug API Issues

**If something isn't working, use debug mode:**

```bash
tourney-threads --debug --dry-run
```

**Output includes:**
```
=== API Response (raw JSON) ===
{"data": [{"type": "match", "id": "12345", ...}], ...}

=== Match Summary ===
Found 8 matches:
- Match #1: Alice vs Bob (Round 1, Winners, State: open)
- Match #2: Charlie vs Dana (Round 1, Winners, State: open)
...
```

**Use this to:**
- Verify OAuth authentication is working
- Check if matches are being fetched
- Understand tournament structure
- Debug template variable issues

### 4. Override Tournament

**Use different tournaments without changing config:**

```bash
tourney-threads --tournament winter-championship-2026
```

**Useful for:**
- Managing multiple tournaments with one config
- Quick testing with different tournaments
- Automated scripts across events

### 5. Use Custom Config File

**Use different configuration files:**

```bash
tourney-threads --config production.yaml
```

**Useful for:**
- Separate dev/staging/production environments
- Multiple Discord servers
- Different tournament organizers

## Advanced Usage

### Combining Options

```bash
# Test new tournament with full debug output
tourney-threads --tournament new-event --debug --dry-run

# Production deployment with absolute path
tourney-threads --config /etc/tourney/prod.yaml

# Maximum verbosity for troubleshooting
tourney-threads --config test.yaml --tournament debug-tourney --debug --dry-run
```

### Managing Multiple Tournaments

**Option A: Use `--tournament` flag**
```bash
tourney-threads --tournament event-a --dry-run
tourney-threads --tournament event-a

tourney-threads --tournament event-b --dry-run
tourney-threads --tournament event-b
```

**Option B: Use separate config files**
```bash
tourney-threads --config config-event-a.yaml
tourney-threads --config config-event-b.yaml
```

### Automated Workflows

**Example: Bash script for weekly tournaments**
```bash
#!/bin/bash
# weekly-threads.sh

# Activate virtual environment
source .venv/bin/activate

# Preview first
echo "=== Previewing threads... ==="
tourney-threads --dry-run

# Ask for confirmation
read -p "Create these threads? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    tourney-threads
    echo "Threads created successfully!"
else
    echo "Cancelled."
fi
```

**Example: PowerShell script for Windows**
```powershell
# weekly-threads.ps1

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# Preview first
Write-Host "=== Previewing threads... ===" -ForegroundColor Cyan
tourney-threads --dry-run

# Ask for confirmation
$response = Read-Host "Create these threads? (y/n)"
if ($response -eq 'y') {
    tourney-threads
    Write-Host "Threads created successfully!" -ForegroundColor Green
} else {
    Write-Host "Cancelled." -ForegroundColor Yellow
}
```

## Typical Tournament Workflow

### Setup (Once per Tournament)

1. **Create tournament on Challonge**
2. **Update config.yaml:**
   ```yaml
   challonge:
     tournament: "new-tournament-slug"
   ```
3. **Test configuration:**
   ```bash
   tourney-threads --debug --dry-run
   ```

### Each Round

1. **After bracket advances, preview threads:**
   ```bash
   tourney-threads --dry-run
   ```

2. **Verify output looks correct:**
   - Player names are right
   - Round labels make sense
   - Mentions are working

3. **Create threads:**
   ```bash
   tourney-threads
   ```

4. **Verify in Discord:**
   - Check threads were created
   - Verify messages look good
   - Test mentions work

### Filtering Matches

**Only fetch open matches:**
```yaml
challonge:
  tournament: "my-tournament"
  state: "open"
```

**Pagination for large tournaments:**
```yaml
challonge:
  tournament: "my-tournament"
  per_page: 50  # Fetch 50 matches per page
  page: 1       # Start at page 1
```

## Troubleshooting Common Issues

### No Threads Created

**Check:**
1. Run with `--debug` to see API response
2. Verify tournament slug is correct
3. Check match state filter
4. Ensure bot has proper permissions

### Wrong Player Names

**Solutions:**
1. Update `runner_map` in config
2. Check Challonge participant names
3. Verify "(invitation pending)" is being stripped

### Mentions Not Working

**Check:**
1. Discord user IDs are correct (right-click → Copy ID)
2. `runner_map` keys exactly match Challonge usernames
3. Bot has permission to mention users

### OAuth Errors

**Solutions:**
1. Verify `client_id` and `client_secret` are correct
2. Check OAuth application is active on Challonge
3. Try regenerating credentials

### Rate Limiting

If you hit rate limits:
```yaml
challonge:
  per_page: 10  # Reduce page size
```

Or add delays between requests in custom scripts.

## Exit Codes

- `0`: Success
- `1`: Error (check error message)

## Getting Help

```bash
# Show command help
tourney-threads --help

# Check version
tourney-threads --version
```

## See Also

- [CONFIGURATION.md](CONFIGURATION.md) - Configuration reference
- [TEMPLATES.md](TEMPLATES.md) - Template variables
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Detailed troubleshooting
- [../CONTRIBUTING.md](../CONTRIBUTING.md) - Contributing guidelines
