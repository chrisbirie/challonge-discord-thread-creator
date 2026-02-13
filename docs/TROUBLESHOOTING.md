# Troubleshooting Guide

Common issues and their solutions.

## Table of Contents

- [Configuration Issues](#configuration-issues)
- [OAuth / API Issues](#oauth--api-issues)
- [Discord Issues](#discord-issues)
- [Match Data Issues](#match-data-issues)
- [Performance Issues](#performance-issues)

## Configuration Issues

### Error: "Missing required oauth2.client_id"

**Cause:** OAuth2 configuration is incomplete or missing.

**Solution:**
```yaml
# Ensure config.yaml has:
oauth2:
  client_id: "your_actual_client_id"
  client_secret: "your_actual_client_secret"
```

**Check:**
1. File exists at `config.yaml` (or path specified with `--config`)
2. YAML syntax is valid (use a YAML validator)
3. No extra spaces or tabs in indentation

### Error: "Missing required discord.bot_token"

**Cause:** Discord configuration missing or incomplete.

**Solution:**
```yaml
discord:
  bot_token: "YOUR_BOT_TOKEN"
  channel_id: 123456789012345678
```

**Note:** This error won't occur with `--dry-run` flag.

### Config file not found

**Error:** `FileNotFoundError: [Errno 2] No such file or directory: 'config.yaml'`

**Solutions:**
1. Create config file: `cp config.example.yaml config.yaml`
2. Specify path: `tourney-threads --config /path/to/config.yaml`
3. Check current directory: `pwd` or `cd`

### YAML parsing errors

**Error:** `yaml.scanner.ScannerError: while scanning...`

**Common causes:**
- Mixed tabs and spaces (use spaces only)
- Missing quotes around strings with special characters
- Incorrect indentation

**Fix:**
```yaml
# Bad
message_template: Hi {p1_mention}: let's play!

# Good
message_template: "Hi {p1_mention}: let's play!"
```

## OAuth / API Issues

### Error: "OAuth token request failed"

**Cause:** Invalid credentials or OAuth application issues.

**Solutions:**

1. **Verify credentials:**
   - Double-check `client_id` and `client_secret`
   - Ensure no extra spaces or newlines
   - Try regenerating credentials on Challonge

2. **Check OAuth application:**
   - Log into Challonge → Settings → Developer Settings
   - Verify application is active (not deleted)
   - Check redirect URIs are configured

3. **Test with debug:**
   ```bash
   tourney-threads --debug --dry-run
   ```
   Look for the API response details.

### Error: "Tournament not found"

**Cause:** Invalid tournament slug or permissions.

**Solutions:**

1. **Check tournament slug:**
   - From URL `https://challonge.com/my-tournament`
   - Slug is `my-tournament`

2. **For organization tournaments:**
   ```yaml
   challonge:
     tournament: "tournament-name"
     subdomain: "myorg"  # If URL is myorg.challonge.com/tournament-name
   ```

3. **Check permissions:**
   - Ensure OAuth application has access to tournament
   - Verify tournament is not private/hidden

### Rate limiting

**Error:** HTTP 429 or "Too many requests"

**Solutions:**

1. **Reduce page size:**
   ```yaml
   challonge:
     per_page: 10  # Instead of 25 or 50
   ```

2. **Add delays in scripts:**
   ```bash
   tourney-threads --tournament event-1
   sleep 5
   tourney-threads --tournament event-2
   ```

3. **Contact Challonge** if you need higher limits

## Discord Issues

### Threads not being created

**Possible causes:**

1. **Bot permissions:**
   - Bot needs "Create Public Threads" permission
   - Bot needs "Send Messages" permission
   - Check role hierarchy

2. **Channel type:**
   - Must be a text channel (not voice, announcement, etc.)
   - Threads must be enabled for the channel

3. **Bot not in server:**
   - Verify bot is in the Discord server
   - Check bot status (online/offline)

**Debug steps:**
```bash
# 1. Test with dry-run
tourney-threads --dry-run

# 2. Check if preview shows threads correctly
# 3. Try creating threads manually to test bot permissions
# 4. Check Discord bot logs
```

### Mentions not working

**Issue:** `@username` instead of proper Discord mention

**Causes & Solutions:**

1. **Runner map not configured:**
   ```yaml
   runner_map:
     "ExactChallongeUsername": 123456789012345678
   ```

2. **Username mismatch:**
   - Check exact spelling (case-sensitive)
   - Remove any extra spaces
   - Check for special characters

3. **Get correct Discord ID:**
   - Enable Developer Mode in Discord
   - Right-click user → Copy ID

4. **Test:**
   ```bash
   tourney-threads --dry-run
   # Check if mentions show as <@123456789012345678>
   ```

### Role mentions not appearing

**Issue:** Role IDs in config but not showing in threads

**Solutions:**

1. **Check role ID format:**
   ```yaml
   discord:
     role_ids_to_tag:
       - 987654321098765432  # Numbers, not strings
   ```

2. **Bot permissions:**
   - Bot needs "Mention @everyone, @here, and All Roles"

3. **Role hierarchy:**
   - Bot's role must be above roles it's mentioning

### Thread names truncated

**Cause:** Discord's 100-character limit

**Solutions:**

1. **Shorten template:**
   ```yaml
   thread_name_template: "{p1_name} vs {p2_name} - R{abs_round}"
   ```

2. **Use abbreviations:**
   ```yaml
   thread_name_template: "W R{round}: {p1_name} vs {p2_name}"
   ```

3. **Preview first:**
   ```bash
   tourney-threads --dry-run
   ```

## Match Data Issues

### No matches found

**Issue:** "No matches returned" or empty preview

**Causes & Solutions:**

1. **Check match state filter:**
   ```yaml
   challonge:
     state: "open"  # Try removing this or use "all"
   ```

2. **Tournament hasn't started:**
   - Matches might not exist yet
   - Check tournament on Challonge website

3. **Pagination:**
   ```yaml
   challonge:
     page: 1
     per_page: 50  # Try higher number
   ```

4. **Debug:**
   ```bash
   tourney-threads --debug --dry-run
   # Check "Match Summary" section
   ```

### Wrong player names

**Issue:** Names don't match expected

**Causes:**

1. **Challonge participant names:**
   - Check participant list on Challonge
   - Tool uses exact names from Challonge

2. **"(invitation pending)" suffix:**
   - Automatically stripped by tool
   - If still appearing, report as bug

3. **Unicode characters:**
   - May display differently depending on terminal

### TBD players

**Issue:** Threads show "TBD vs TBD"

**Explanation:**
- Normal for matches where players aren't determined yet
- Happens in bracket stages before earlier rounds complete

**Solutions:**
- Filter to only show matches with players:
  ```yaml
  challonge:
    state: "open"  # Usually has players assigned
  ```
- Wait for previous rounds to complete

### Wrong round labels

**Issue:** Round labels don't match expectations

**Solutions:**

1. **Check stage detection:**
   ```bash
   tourney-threads --debug --dry-run
   # Look for "Stage: Swiss" or similar
   ```

2. **Custom round labels:**
   ```yaml
   round_label_template: "{bracket} Round {abs_round}"
   ```

3. **Understand Challonge numbering:**
   - Winners: positive (1, 2, 3...)
   - Losers: negative (-1, -2, -3...)

## Performance Issues

### Slow execution

**Causes & Solutions:**

1. **Large tournament:**
   - Use pagination
   - Filter by state

2. **Network latency:**
   - Check internet connection
   - Try different time of day

3. **API rate limits:**
   - See [Rate limiting](#rate-limiting)

### Timeout errors

**Error:** Connection timeout or request timeout

**Solutions:**

1. **Check network:**
   ```bash
   ping api.challonge.com
   ```

2. **Increase timeout (in custom wrapper):**
   ```python
   # Not currently configurable - file feature request
   ```

3. **Try again:**
   - Transient network issues
   - Challonge API may be slow

## Getting More Help

### Enable Debug Mode

Always start with debug mode:
```bash
tourney-threads --debug --dry-run
```

### Check Logs

The tool outputs to stdout/stderr. Redirect to file:
```bash
tourney-threads --debug &> debug.log
```

### Verify Versions

```bash
python --version  # Should be 3.10+
tourney-threads --version
pip show tourney-threads
```

### Test Components

1. **Test OAuth separately:**
   - Use Challonge API test tools
   - Verify credentials work elsewhere

2. **Test Discord bot:**
   - Try creating threads manually
   - Check bot responds to commands

3. **Test configuration:**
   ```bash
   python -c "import yaml; print(yaml.safe_load(open('config.yaml')))"
   ```

### Report Issues

If you can't resolve the issue:

1. **GitHub Issues:** https://github.com/chrisbirie/challonge-discord-thread-creator/issues
2. **Include:**
   - Debug output (`--debug` flag)
   - Config file (remove secrets!)
   - Python version
   - OS/platform
   - Steps to reproduce

## Common Error Messages

| Error | Likely Cause | Solution |
|-------|-------------|----------|
| `ModuleNotFoundError: No module named 'tourney_threads'` | Package not installed | Run `pip install -e .` |
| `PermissionError` | File permissions or bot permissions | Check file access or Discord permissions |
| `KeyError: 'oauth2'` | Missing config section | Add required config sections |
| `RuntimeError: OAuth token request failed` | Invalid credentials | Check OAuth credentials |
| `discord.errors.Forbidden` | Bot lacks permissions | Grant bot required Discord permissions |
| `aiohttp.ClientError` | Network/API issue | Check internet connection |

## See Also

- [INSTALLATION.md](INSTALLATION.md) - Installation help
- [CONFIGURATION.md](CONFIGURATION.md) - Configuration reference
- [USAGE.md](USAGE.md) - Usage examples
- [GitHub Issues](https://github.com/chrisbirie/challonge-discord-thread-creator/issues) - Report bugs
