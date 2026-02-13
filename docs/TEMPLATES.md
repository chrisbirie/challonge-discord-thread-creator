# Template Variables Reference

Complete reference for customizing thread names and messages using template variables.

## Overview

The application supports three customizable templates:

1. **`thread_name_template`** - Thread title (max 100 characters, auto-truncated)
2. **`message_template`** - Initial message posted in the thread
3. **`round_label_template`** - Custom round label format (optional)

## Available Variables

### Player Information

| Variable | Description | Example |
|----------|-------------|---------|
| `{p1_name}` | Player 1 username | `Alice` |
| `{p2_name}` | Player 2 username | `Bob` |
| `{p1_mention}` | Player 1 Discord mention or username | `<@123456>` or `Alice` |
| `{p2_mention}` | Player 2 Discord mention or username | `<@789012>` or `Bob` |

**Notes:**
- Names show `TBD` if player not yet determined
- Mentions use Discord ID if mapped in `runner_map`, otherwise shows username
- `(invitation pending)` suffix is automatically removed from names

### Round Information

| Variable | Description | Example |
|----------|-------------|---------|
| `{round_label}` | Full round label (formatted) | `Winners R1`, `Swiss R3`, `Losers R2` |
| `{stage}` | Tournament stage type | `Swiss`, `Groups`, `Elimination`, or empty |
| `{bracket}` | Bracket name | `Winners`, `Losers`, or `Round` |
| `{round}` | Raw round number | `1`, `-2`, `3` |
| `{abs_round}` | Absolute round number | `1`, `2`, `3` |

**Round Number Conventions:**
- **Positive numbers**: Winners bracket (e.g., `1`, `2`, `3`)
- **Negative numbers**: Losers bracket (e.g., `-1`, `-2`, `-3`)
- **Zero**: Not typically used by Challonge

**Stage Types:**
- **`Swiss`**: Swiss-system tournament
- **`Groups`**: Group stage
- **`Elimination`**: Single or double elimination
- Empty string if stage cannot be detected

### Match Information

| Variable | Description | Example |
|----------|-------------|---------|
| `{match_id}` | Challonge match ID | `427403394` |
| `{match_state}` | Current match status | `open`, `pending`, `complete` |
| `{match_url}` | Direct link to match on Challonge | `https://challonge.com/tournament/matches/12345` |
| `{tournament_name}` | Tournament slug from config | `my-tournament` |

**Match States:**
- **`open`**: Ready to be played
- **`pending`**: Waiting (e.g., for previous matches)
- **`complete`**: Already finished

**Match URL Format:**
- Regular: `https://challonge.com/{tournament}/matches/{match_id}`
- Subdomain: `https://{subdomain}.challonge.com/{tournament}/matches/{match_id}`

### Other Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{role_mentions}` | Space-separated role mentions | `<@&111> <@&222>` |

**Notes:**
- Role mentions are automatically generated from `discord.role_ids_to_tag`
- Empty string if no roles configured

## Template Examples

### Default Templates

```yaml
thread_name_template: "{round_label}: {p1_name} vs {p2_name}"
# Result: "Winners R1: Alice vs Bob"

message_template: |
  Hi {p1_mention} vs {p2_mention}! {role_mentions}
  This is your scheduling thread for {round_label}.

round_label_template: null  # Uses default logic
```

### Custom Thread Names

**Include match ID for reference:**
```yaml
thread_name_template: "{round_label}: {p1_name} vs {p2_name} [#{match_id}]"
# Result: "Winners R1: Alice vs Bob [#427403394]"
```

**Show tournament name:**
```yaml
thread_name_template: "[{tournament_name}] {round_label}: {p1_name} vs {p2_name}"
# Result: "[spring-2026] Winners R1: Alice vs Bob"
```

**Compact format:**
```yaml
thread_name_template: "{p1_name} vs {p2_name} - R{abs_round}"
# Result: "Alice vs Bob - R1"
```

### Custom Messages

**Detailed match information:**
```yaml
message_template: |
  🎮 **Match Ready!**
  
  {p1_mention} 🆚 {p2_mention}
  
  **Round:** {round_label}
  **Match ID:** {match_id}
  **Status:** {match_state}
  **Match Page:** {match_url}
  
  Please coordinate your match time in this thread.
  Tag {role_mentions} when you have a scheduled time!
```

**Simple and clean:**
```yaml
message_template: |
  {p1_mention} vs {p2_mention}
  
  {round_label} - {match_url}
  
  Good luck! 🏆
```

**With scheduling instructions:**
```yaml
message_template: |
  Hi {p1_mention} and {p2_mention}! {role_mentions}
  
  This is your match thread for **{round_label}**.
  
  **Match Details:**
  • Tournament: {tournament_name}
  • Match Page: {match_url}
  • Status: {match_state}
  
  **Scheduling Instructions:**
  1. Post 3-4 time windows you're available (include timezone!)
  2. Agree on a time that works for both players
  3. Tag an admin to confirm the scheduled time
  4. Report your match result on Challonge: {match_url}
  
  **Important:**
  - Matches should be completed within 48 hours
  - Best of 3 format
  - Screenshot results before reporting
  
  Good luck and have fun! 🎮
```

### Custom Round Labels

**Override default round label format:**

```yaml
round_label_template: "{stage} - {bracket} Round {abs_round}"
# Result: "Elimination - Winners Round 1"
```

**Compact format:**
```yaml
round_label_template: "{bracket} R{abs_round}"
# Result: "Winners R1"
```

**With stage prefix:**
```yaml
round_label_template: "[{stage}] {bracket} {abs_round}"
# Result: "[Swiss] Round 3"
```

**Note:** If `round_label_template` is not set, default logic is used:
- Swiss/Groups: `"Swiss R1"`, `"Groups R2"`
- Elimination: `"Winners R1"`, `"Losers R2"`

## Special Cases

### TBD Players

When a player is not yet determined (waiting for previous match):

```yaml
message_template: |
  Match for {round_label}
  
  {p1_name} vs {p2_name}
  
  (Players will be determined after previous matches complete)
```

**Output:**
```
Match for Winners R3

Alice vs TBD

(Players will be determined after previous matches complete)
```

### Losers Bracket

For double elimination losers bracket (negative round numbers):

```yaml
thread_name_template: "{bracket} R{abs_round}: {p1_name} vs {p2_name}"
# Winners R1: Alice vs Bob (round = 1)
# Losers R1: Charlie vs Dana (round = -1)
```

### No Runner Map

If players aren't in `runner_map`, mentions show usernames:

```yaml
message_template: "Hi {p1_mention} vs {p2_mention}!"
# With mapping: "Hi <@123456> vs <@789012>!"
# Without: "Hi Alice vs Bob!"
```

## Length Limits

### Thread Names

- **Maximum:** 100 characters (Discord limit)
- **Behavior:** Automatically truncated if longer
- **Recommendation:** Keep under 90 characters to account for Unicode

**Example of truncation:**
```yaml
thread_name_template: "{round_label}: {p1_name} vs {p2_name} in the amazing super long tournament name that goes on forever and ever"
# Result: "Winners R1: Alice vs Bob in the amazing super long tournament name that goes on forever and ev..."
```

### Messages

- **Maximum:** 2000 characters (Discord limit)
- **Behavior:** Will fail if exceeded
- **Recommendation:** Keep under 1500 characters for safety

## Escaping and Special Characters

### Curly Braces

To include literal `{` or `}` in templates, double them:

```yaml
message_template: "Match ID: {match_id} {{not a variable}}"
# Result: "Match ID: 427403394 {not a variable}"
```

### Discord Markdown

You can use Discord markdown in messages:

```yaml
message_template: |
  **Bold** *italic* __underline__ ~~strikethrough~~
  
  > Quote
  
  `code` ```code block```
  
  [Link text](https://example.com)
```

### Emojis

Unicode emojis work in both thread names and messages:

```yaml
thread_name_template: "🎮 {round_label}: {p1_name} vs {p2_name}"
message_template: "Good luck! 🏆🎉"
```

## Testing Templates

**Use dry-run to preview your templates:**

```bash
tourney-threads --dry-run
```

**Check the output carefully:**
- Are names correct?
- Do mentions work (show as `<@123456>`)?
- Is formatting as expected?
- Are lengths appropriate?

## Error Handling

### Missing Variables

If you use a variable that doesn't exist:

```yaml
thread_name_template: "{invalid_var}: {p1_name} vs {p2_name}"
```

**Result:** Error during formatting, falls back to defaults

### Invalid Syntax

```yaml
message_template: "Unclosed {bracket"
```

**Result:** YAML parsing error on startup

## See Also

- [CONFIGURATION.md](CONFIGURATION.md) - Full configuration reference
- [USAGE.md](USAGE.md) - Usage examples
- [config.example.yaml](../config.example.yaml) - Example configuration
