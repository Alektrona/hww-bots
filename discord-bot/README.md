# Discord Bot Setup Guide

Discord bot for monitoring and managing Were-Bot from Discord.

## Features

**Automatic Log Posting** - Posts Were-Bot logs to Discord channel in real-time
**Bot Status** - Check if Were-Bot is running
**Remote Restart** - Restart Were-Bot from Discord (mods only)
**Log Viewer** - View recent logs on demand
**Error Alerts** - Get notified when errors occur

## Prerequisites

### 1. Create Discord Bot

1. Go to https://discord.com/developers/applications
2. Click **New Application**
3. Name it "Were-Bot Manager" (or whatever you want)
4. Go to **Bot** tab
5. Click **Add Bot**
6. Under **Privileged Gateway Intents**, enable:
   - SERVER MEMBERS INTENT
   - MESSAGE CONTENT INTENT
7. Click **Reset Token** and copy the token (you'll need this!)

### 2. Invite Bot to Your Server

1. Go to **OAuth2** → **URL Generator**
2. Select scopes:
   - `bot`
   - `applications.commands`
3. Select bot permissions:
   - Send Messages
   - Embed Links
   - Read Message History
   - Read Messages/View Channels
4. Copy the generated URL and open it in browser
5. Select your server and authorize

### 3. Get Discord IDs

**Guild (Server) ID:**
1. Enable Developer Mode in Discord: Settings → Advanced → Developer Mode
2. Right-click your server icon → Copy Server ID

**Channel IDs:**
1. Right-click the log channel → Copy Channel ID
2. Right-click the alert channel → Copy Channel ID (can be same as log channel)

### 4. Get Portainer API Key

1. Log into Portainer: https://oracle.hufflepuff.fun:9443/
2. Go to your **User** (click username in top-right)
3. Scroll to **Access tokens**
4. Click **Add access token**
5. Description: "Discord Bot"
6. Click **Create**
7. **COPY THE TOKEN IMMEDIATELY** (you can't see it again!)

## Deployment in Portainer

### Option 1: Add to Existing Were-Bot Stack (Recommended)

1. Go to **Stacks** in Portainer
2. Click on your `werebot` stack
3. Click **Editor**
4. Update the compose file to add the Discord bot:

```yaml
version: '3.8'

services:
  werebot:
    image: python:3.11-slim
    container_name: werebot
    restart: unless-stopped
    
    command: >
      /bin/bash -c "
        pip install --break-system-packages praw gspread google-auth &&
        cd /app/data &&
        python -u /app/werebot_updated.py
      "
    
    volumes:
      - werebot-files:/app:ro
      - werebot-data:/app/data
    
    environment:
      - REDDIT_CLIENT_ID=${REDDIT_CLIENT_ID}
      - REDDIT_CLIENT_SECRET=${REDDIT_CLIENT_SECRET}
      - REDDIT_USERNAME=${REDDIT_USERNAME}
      - REDDIT_PASSWORD=${REDDIT_PASSWORD}
      - REDDIT_USER_AGENT=${REDDIT_USER_AGENT}
      - NICKNAME_SPREADSHEET_URL=${NICKNAME_SPREADSHEET_URL:-}
      - NICKNAME_CREDENTIALS=/app/creds2.json
    
    working_dir: /app/data
    
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  discord-bot:
    image: python:3.11-slim
    container_name: werebot-discord
    restart: unless-stopped
    
    command: >
      /bin/bash -c "
        pip install --break-system-packages discord.py aiohttp &&
        python -u /app/discord_bot.py
      "
    
    volumes:
      - werebot-files:/app:ro
      - werebot-data:/shared/werebot/data:ro
    
    environment:
      - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
      - DISCORD_GUILD_ID=${DISCORD_GUILD_ID}
      - LOG_CHANNEL_ID=${LOG_CHANNEL_ID}
      - ALERT_CHANNEL_ID=${ALERT_CHANNEL_ID}
      - PORTAINER_URL=https://oracle.hufflepuff.fun:9443
      - PORTAINER_API_KEY=${PORTAINER_API_KEY}
      - WEREBOT_CONTAINER_NAME=werebot
      - MOD_ROLE_NAME=PermaMods
      - WEREBOT_LOG_FILE=/shared/werebot/data/werebot.log
    
    working_dir: /app

volumes:
  werebot-files:
    external: true
  werebot-data:
    driver: local
```

5. Add environment variables at the bottom (or in the Environment variables section):

```
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_server_id_here
LOG_CHANNEL_ID=your_log_channel_id_here
ALERT_CHANNEL_ID=your_alert_channel_id_here
PORTAINER_API_KEY=your_portainer_api_key_here
```

6. Click **Update the stack**

### Option 2: Separate Stack

If you prefer to keep them separate:

1. Go to **Stacks** → **Add stack**
2. Name: `werebot-discord`
3. Paste this:

```yaml
version: '3.8'

services:
  discord-bot:
    image: python:3.11-slim
    container_name: werebot-discord
    restart: unless-stopped
    
    command: >
      /bin/bash -c "
        pip install --break-system-packages discord.py aiohttp &&
        python -u /app/discord_bot.py
      "
    
    volumes:
      - werebot-files:/app:ro
      - werebot-data:/shared/werebot/data:ro
    
    environment:
      - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
      - DISCORD_GUILD_ID=${DISCORD_GUILD_ID}
      - LOG_CHANNEL_ID=${LOG_CHANNEL_ID}
      - ALERT_CHANNEL_ID=${ALERT_CHANNEL_ID}
      - PORTAINER_URL=https://oracle.hufflepuff.fun:9443
      - PORTAINER_API_KEY=${PORTAINER_API_KEY}
      - WEREBOT_CONTAINER_NAME=werebot
      - MOD_ROLE_NAME=PermaMods
      - WEREBOT_LOG_FILE=/shared/werebot/data/werebot.log
    
    working_dir: /app

volumes:
  werebot-files:
    external: true
  werebot-data:
    external: true
```

4. Add environment variables
5. Click **Deploy the stack**

## Upload Discord Bot File

1. Go to **Volumes** → `werebot-files` → **Browse**
2. Upload `discord_bot.py`
3. The container should pick it up automatically

## Discord Setup

### Create Channels

Create two channels in your Discord server:

1. **#were-bot-logs** - For automatic log posting
2. **#were-bot-alerts** - For error alerts (can be same as logs)

### Set Up Roles

Make sure you have a role named **PermaMods** (or change `MOD_ROLE_NAME` in config).

Only users with this role can use:
- `!bot restart`
- `!bot tail`

## Commands

### Available to Everyone

**!bot status**
- Check if Were-Bot is running
- Shows current status and uptime

**!bot help**
- Show available commands

### Mod-Only Commands

**!bot restart**
- Restart the Were-Bot container
- Requires Moderator role
- Logs who triggered the restart

**!bot tail [lines]**
- Show last N lines of logs (default 20, max 50)
- Requires Moderator role
- Example: `!bot tail 30`

## How It Works

### Automatic Log Monitoring

The Discord bot:
1. Watches the Were-Bot log file (`werebot.log`)
2. Every 10 seconds, checks for new log entries
3. Posts new logs to the log channel
4. Color-codes by severity:
   - Red = Errors
   - Orange = Warnings
   - Blue = Info

### Error Alerts

When errors are detected:
1. Posts to log channel (as usual)
2. Also sends alert to alert channel
3. Rate-limited (max 1 alert per 5 minutes to avoid spam)

### Remote Restart

When mod uses `!bot restart`:
1. Discord bot calls Portainer API
2. Finds Were-Bot container by name
3. Issues restart command
4. Reports success/failure to Discord
5. Logs who triggered it

## Environment Variables

### Required:
```
DISCORD_BOT_TOKEN        # From Discord Developer Portal
DISCORD_GUILD_ID         # Your Discord server ID
LOG_CHANNEL_ID           # Channel for automatic logs
PORTAINER_URL            # https://oracle.hufflepuff.fun:9443
PORTAINER_API_KEY        # From Portainer user settings
```

### Optional:
```
ALERT_CHANNEL_ID         # Channel for error alerts (defaults to LOG_CHANNEL_ID)
WEREBOT_CONTAINER_NAME   # Container name (default: werebot)
MOD_ROLE_NAME            # Role name for mod commands (default: PermaMods)
WEREBOT_LOG_FILE         # Path to log file (default: /shared/werebot/data/werebot.log)
```

## Testing

### 1. Check Bot is Online

In Discord:
```
!bot help
```

You should see the help embed.

### 2. Check Status

```
!bot status
```

Should show Were-Bot's current status.

### 3. Test Logs

Make Were-Bot do something (tag users in Reddit), then watch the Discord log channel for automatic updates.

### 4. Test Restart (Mods)

```
!bot restart
```

Bot should restart Were-Bot and report success.

## Troubleshooting

### Bot Not Responding

**Check container status:**
1. Portainer → Containers → werebot-discord
2. Check status is "running"
3. Check logs for errors

**Common issues:**
- Invalid Discord token
- Bot not invited to server
- Missing intents (enable in Discord Developer Portal)

### Can't Restart Were-Bot

**Check Portainer API key:**
1. Make sure key is valid
2. Check container logs for API errors
3. Verify PORTAINER_URL is correct

### Logs Not Posting

**Check file path:**
1. Verify WEREBOT_LOG_FILE path is correct
2. Check volume mount is correct
3. SSH into server and verify file exists

**Check permissions:**
```bash
ls -la /path/to/werebot/data/werebot.log
```

### Mod Commands Not Working

**Check role name:**
- Role must be named "PermaMods" (or update MOD_ROLE_NAME)
- Role must be assigned to users
- Check spelling is exact

## Security

### Best Practices

**Keep tokens secret** - Never share Discord token or Portainer API key
**Use environment variables** - Don't hardcode credentials
**Limit mod role** - Only give to trusted users
**Monitor usage** - Check logs regularly
**Read-only mounts** - Bot code is mounted read-only (`:ro`)

### Token Security

**Discord Token:**
- If compromised, regenerate in Discord Developer Portal
- Bot will need to be redeployed with new token

**Portainer API Key:**
- If compromised, revoke in Portainer and create new
- Update stack with new key

## Viewing Logs

### Discord Bot Logs

In Portainer:
1. Containers → werebot-discord
2. Logs tab
3. Look for:
   - "has connected to Discord!" = Good
   - "Monitoring Were-Bot logs at" = Good
   - Any errors = Bad

### Were-Bot Logs (via Discord)

Just use: `!bot tail 30`

## Updating Discord Bot

1. Update `discord_bot.py` locally
2. Stop container in Portainer
3. Upload new version to `werebot-files` volume
4. Start container

Or with SSH + Git:
```bash
cd /opt/bots/werebot
git pull
docker restart werebot-discord
```

## Example Discord Setup

### Channel Setup

```
📁 WERE-BOT MANAGEMENT
├── #were-bot-logs     (automatic logs posted here)
└── #were-bot-alerts   (errors posted here)
```

### Role Setup

Create "Moderator" role with permissions:
- ✅ Can use mod commands
- ❌ Can't delete bot messages
- ❌ Can't manage channels

## Advanced: Custom Alerts

You can customize alert thresholds by editing `discord_bot.py`:

```python
# Alert on specific patterns
if 'CRITICAL' in line or 'Failed to initialize' in line:
    # Send urgent alert
    ...
```

## GitHub Structure

Recommended repo structure:

```
werebot/
├── reddit-bot/
│   ├── werebot_updated.py
│   └── nickname_mapper.py
├── discord-bot/
│   └── discord_bot.py
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

Monitor and manage Were-Bot from Discord! 🤖💬
