# Credentials & IDs Setup Guide

This guide walks you through obtaining all the credentials and Discord IDs needed to configure the Challonge Discord Thread Creator.

## Table of Contents

1. [Challonge OAuth2 Credentials](#challonge-oauth2-credentials)
2. [Discord Bot Token](#discord-bot-token)
3. [Discord Channel ID](#discord-channel-id)
4. [Discord User IDs (for Player Mapping)](#discord-user-ids-for-player-mapping)
5. [Discord Role IDs](#discord-role-ids)
6. [Challonge Tournament Slug](#challonge-tournament-slug)

---

## Challonge OAuth2 Credentials

The `client_id` and `client_secret` are used to authenticate with the Challonge API v2.1.

### Steps to Get Your Credentials

1. **Log in to Challonge**
   - Go to [https://challonge.com](https://challonge.com)
   - Sign in with your account

2. **Navigate to Developer Settings**
   - Click your profile picture (top right) → **Settings**
   - In the sidebar, scroll down to **Developer** section
   - Click **API** or **OAuth Applications**

3. **Create a New OAuth Application**
   - Look for a button like "Create New OAuth Application" or "New Application"
   - Fill in the application details:
     - **Name**: Something like "Discord Thread Creator"
     - **Redirect URI**: `http://localhost:8080/callback` (or your app URL)
     - **Scopes**: `tournaments:read matches:read` (or leave default)
   - Click **Create**

4. **Copy Your Credentials**
   - You'll see your **Client ID** and **Client Secret**
   - Copy both and save them securely
   - ⚠️ **Never commit these to version control** - use `config.yaml` (which is in `.gitignore`)

5. **Add to config.yaml**
   ```yaml
   oauth2:
     client_id: "YOUR_CLIENT_ID"
     client_secret: "YOUR_CLIENT_SECRET"
   ```

### Getting Your Challonge Tournament Slug

The tournament slug is the identifier in your Challonge URL.

1. Go to your tournament on Challonge
2. Look at the URL: `https://challonge.com/YOUR-TOURNAMENT-SLUG`
   - Example: `https://challonge.com/umebura9` → slug is `umebura9`
3. If it's an organization tournament: `https://org-name.challonge.com/YOUR-TOURNAMENT-SLUG`
   - You'll also need to set `subdomain: "org-name"` in the config

4. **Add to config.yaml**
   ```yaml
   challonge:
     tournament: "your-tournament-slug"
     subdomain: ""  # only if it's an org tournament
   ```

---

## Discord Bot Token

The bot token allows the tool to create threads in your Discord server.

### Steps to Get Your Bot Token

1. **Open Discord Developer Portal**
   - Go to [https://discord.com/developers/applications](https://discord.com/developers/applications)
   - Sign in with your Discord account

2. **Create a New Application (if needed)**
   - Click **New Application**
   - Give it a name (e.g., "Tourney Threads Bot")
   - Click **Create**

3. **Create a Bot User**
   - In the left sidebar, click **Bot**
   - Click **Add Bot**

4. **Copy the Token**
   - Under the "TOKEN" section, click **Copy**
   - This is your bot token
   - ⚠️ **Treat this like a password** - never share it or commit to git
   - If you accidentally leak it, regenerate immediately

5. **Enable Message Content Intent (Optional)**
   - Scroll down to "INTENTS" section
   - Toggle on **Message Content Intent** if you need the bot to read message content
   - For basic thread creation, this is not required

6. **Add to config.yaml**
   ```yaml
   discord:
     bot_token: "YOUR_DISCORD_BOT_TOKEN"
   ```

### Inviting Your Bot to Your Server

1. **Set Bot Permissions**
   - In Developer Portal, go to **OAuth2** → **URL Generator**
   - Select scopes: `bot`
   - Select permissions:
     - **Send Messages**
     - **Create Public Threads**
     - **Mention @everyone, @here, and All Roles** (if using role mentions)
   - Copy the generated URL

2. **Invite the Bot**
   - Paste the URL in your browser
   - Select your server
   - Click **Authorize**
   - Complete the CAPTCHA

3. **Verify in Discord**
   - Go to your server
   - You should see your bot in the member list
   - The bot should appear offline until you run the tool

---

## Discord Channel ID

The channel ID specifies which Discord channel to create threads in.

### Steps to Get Your Channel ID

1. **Enable Developer Mode in Discord**
   - Open Discord (desktop or web)
   - Go to **User Settings** (gear icon, bottom left)
   - Click **Advanced** (in the left sidebar, under "APP SETTINGS")
   - Toggle on **Developer Mode**
   - Close settings

2. **Copy the Channel ID**
   - Right-click on the channel name in your server
   - Click **Copy Channel ID**
   - This is your channel ID (a long number)

3. **Add to config.yaml**
   ```yaml
   discord:
     channel_id: 123456789012345678
   ```

### Verify the Bot Can Access This Channel

- Make sure the bot has permission to send messages and create threads in this channel
- In Discord: Right-click channel → Edit channel → Permissions
- Look for your bot in the member list with at least these permissions:
  - Send Messages
  - Create Public Threads

---

## Discord User IDs (for Player Mapping)

User IDs are used to mention specific Discord users in thread messages (via `runner_map`).

### Steps to Get User IDs

1. **Enable Developer Mode** (see above if not already enabled)

2. **Get a User ID**
   - Right-click on a user's name anywhere in Discord
   - Click **Copy User ID**
   - This is their Discord user ID

3. **Map Players to Discord Users**
   - In `config.yaml`, use the `runner_map` to map Challonge participant names to Discord user IDs:
   ```yaml
   runner_map:
     "ChallongeUsername1": 123456789012345678
     "ChallongeUsername2": 234567890123456789
   ```

4. **These IDs Appear in Thread Messages**
   - When mentioned in templates: `{p1_mention}` and `{p2_mention}`
   - This mentions the Discord user in the thread
   - Example: `"Hi {p1_mention} vs {p2_mention}, here's your match thread!"`

### Finding Participant Names in Challonge

1. Go to your tournament on Challonge
2. Look at the participant list or bracket view
3. The participant display name is what goes in `runner_map`
4. It might be their username or a custom display name they set

---

## Discord Role IDs

Role IDs are used to mention specific Discord roles in thread messages (e.g., @Admins, @Commentators).

### Steps to Get Role IDs

1. **Enable Developer Mode** (see above if not already enabled)

2. **Get a Role ID**
   - Right-click on a role name in Server Settings or in a member's profile
   - Click **Copy Role ID**
   - This is the role ID

3. **Add Role IDs to Config**
   - In `config.yaml`, list the role IDs you want to mention:
   ```yaml
   discord:
     role_ids_to_tag:
       - 234567890123456789    # @Tournament Admins
       - 345678901234567890    # @Commentators
       - 456789012345678901    # @Streamers
   ```

4. **Use in Templates**
   - In your message template, use `{role_mentions}` to include all tagged roles:
   ```yaml
   message_template: |
     Match thread for {round_label}!
     Players: {p1_mention} vs {p2_mention}
     
     {role_mentions} - please keep an eye on this match
   ```

5. **Example Output**
   - Without tags: "Match thread for R1! Players: @Player1 vs @Player2"
   - With tags: "Match thread for R1! Players: @Player1 vs @Player2 @Tournament Admins @Commentators"

---

## Verification Checklist

Before running the tool, verify you have all credentials:

```yaml
# ✓ Challonge OAuth2
oauth2:
  client_id: "___"              # ✓ From Challonge Dev Settings
  client_secret: "___"          # ✓ From Challonge Dev Settings

# ✓ Challonge Tournament
challonge:
  tournament: "___"             # ✓ From tournament URL slug
  subdomain: ""                 # ✓ Only if org tournament

# ✓ Discord Bot
discord:
  bot_token: "___"              # ✓ From Discord Developer Portal
  channel_id: 123456789012345   # ✓ Right-click channel → Copy ID
  role_ids_to_tag:              # ✓ Optional - right-click roles
    - 123456789012345

# ✓ Player Mapping (Optional)
runner_map:
  "ChallongeUsername": 123456789012345  # ✓ Right-click user → Copy ID
```

### Quick Test

Once configured, test with a dry run:

```bash
tourney-threads --dry-run
```

If you see thread previews without errors, all credentials are working!

---

## Troubleshooting

### "Invalid OAuth2 credentials"
- Double-check your `client_id` and `client_secret` from Challonge
- Make sure they're copied completely (no extra spaces)
- Regenerate them if unsure

### "Invalid bot token"
- Make sure you copied the full token (very long string)
- Check that you regenerated the token after creating the bot
- Never share this token with anyone

### "Bot missing permissions"
- In Discord, go to your server settings → Roles
- Find your bot's role
- Ensure it has "Send Messages" and "Create Public Threads"
- May need admin permission if role hierarchy is complex

### "Channel ID not found"
- Make sure you right-clicked the channel (not a category)
- Verify it's a text channel, not a voice channel
- Check that the bot can access the channel (not hidden/restricted)

### "User ID format invalid"
- User/Role IDs are always long numbers (17-20 digits)
- Don't include mentions like `<@123>` in the config, just the number
- If unsure, copy directly from Discord (right-click → Copy ID)

---

## Security Notes

⚠️ **Important:** Never commit credentials to version control!

- `config.yaml` is in `.gitignore` - always use this for credentials
- Use `config.example.yaml` as a template (it's safe to commit)
- If you accidentally commit credentials:
  1. Regenerate them immediately (Challonge client secret, Discord token)
  2. Remove the commit from git history
  3. Force push (carefully!)

### Managing Multiple Environments

Use separate config files:
```bash
# Development
tourney-threads --config config.dev.yaml

# Production
tourney-threads --config config.prod.yaml
```

Keep separate credentials for each environment for security.

---

## Next Steps

- See [CONFIGURATION.md](CONFIGURATION.md) for advanced configuration options
- See [USAGE.md](USAGE.md) for how to use the tool
- See [TEMPLATES.md](TEMPLATES.md) for customizing thread names and messages
