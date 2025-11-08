# Were-Bot Portainer Deployment Guide

Complete guide to deploying Were-Bot using Portainer (Docker container management).

## What is Portainer?

Portainer is a web-based GUI for managing Docker containers. Instead of using command-line Docker commands, you can:
- Create containers through a web interface
- View logs in real-time
- Restart/stop containers easily
- Manage environment variables
- View resource usage

## Prerequisites

Before you start, you need:

1. **Portainer access** - URL (usually `http://your-server:9000` or `https://portainer.yourdomain.com`)
2. **Reddit bot credentials** - From https://www.reddit.com/prefs/apps
3. **Bot files** - `werebot_updated.py` and optional `nickname_mapper.py`
4. **Google credentials** - `creds2.json` (if using nickname mapping)

## Step-by-Step Deployment

### Step 1: Access Portainer

1. Open your browser
2. Go to your Portainer URL
3. Log in with your credentials
4. Select your environment (usually "local" or the server name)

### Step 2: Prepare Your Files

You need to get your bot files onto the server. There are several ways:

#### Option A: Upload via Portainer Volumes

1. In Portainer, go to **Volumes** in the left sidebar
2. Click **Add volume**
3. Name it `werebot-data`
4. Click **Create the volume**
5. Click on the volume name
6. Click **Browse** to access the volume
7. Upload your files:
   - `werebot_updated.py`
   - `nickname_mapper.py` (if using nicknames)
   - `creds2.json` (if using nicknames)

#### Option B: Use SSH/SCP

If you have SSH access:

```bash
# Copy files to server
scp werebot_updated.py user@server:/path/to/files/
scp nickname_mapper.py user@server:/path/to/files/
scp creds2.json user@server:/path/to/files/

# Or use rsync
rsync -av werebot_updated.py nickname_mapper.py creds2.json user@server:/path/to/files/
```

#### Option C: Git Repository

```bash
# On the server
cd /opt/bots/
git clone your-repo-url werebot
cd werebot
# Files are now available
```

### Step 3: Create Container via Portainer

#### Method 1: Using Portainer's Container Creation (Easiest)

1. In Portainer, go to **Containers** in the left sidebar
2. Click **Add container**
3. Fill in the form:

**Basic Settings:**
- **Name:** `werebot`
- **Image:** `python:3.11-slim`

**Command & logging:**
```
/bin/bash -c "pip install --break-system-packages praw gspread google-auth && python -u /app/werebot_updated.py"
```

**Volumes:**
Click **+ map additional volume** for each:
- **container:** `/app` → **host:** `/path/to/your/bot/files` (or use volume `werebot-data`)
- **container:** `/app/data` → **host:** `/path/to/persistent/data` (for logs, vote files, etc)

**Environment Variables:**
Click **+ add environment variable** for each:
```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USERNAME=your_bot_username
REDDIT_PASSWORD=your_bot_password
REDDIT_USER_AGENT=python:werebot:v2.0 (by /u/yourusername)
NICKNAME_SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_ID/edit
```

**Restart policy:**
- Select **Unless stopped**

**Network:**
- Select **bridge** (default is fine)

4. Click **Deploy the container**

#### Method 2: Using Docker Compose / Stacks (Recommended)

1. In Portainer, go to **Stacks** in the left sidebar
2. Click **Add stack**
3. Name it `werebot`
4. Choose **Web editor**
5. Paste this Docker Compose configuration:

```yaml
version: '3.8'

services:
  werebot:
    image: python:3.11-slim
    container_name: werebot
    restart: unless-stopped
    
    # Command to install dependencies and run bot
    command: >
      /bin/bash -c "
        pip install --break-system-packages praw gspread google-auth &&
        python -u /app/werebot_updated.py
      "
    
    # Mount bot files
    volumes:
      - /path/to/bot/files:/app:ro
      - werebot-data:/app/data
    
    # Environment variables
    environment:
      - REDDIT_CLIENT_ID=${REDDIT_CLIENT_ID}
      - REDDIT_CLIENT_SECRET=${REDDIT_CLIENT_SECRET}
      - REDDIT_USERNAME=${REDDIT_USERNAME}
      - REDDIT_PASSWORD=${REDDIT_PASSWORD}
      - REDDIT_USER_AGENT=python:werebot:v2.0 (by /u/yourusername)
      - NICKNAME_SPREADSHEET_URL=${NICKNAME_SPREADSHEET_URL:-}
      - NICKNAME_CREDENTIALS=/app/creds2.json
    
    # Working directory
    working_dir: /app/data
    
    # Logging
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  werebot-data:
    driver: local
```

6. Click **Deploy the stack**

### Step 4: Set Environment Variables

If using the Stack method, you can set variables in the **Environment variables** section:

```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USERNAME=your_bot_username
REDDIT_PASSWORD=your_bot_password
NICKNAME_SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_ID/edit
```

### Step 5: Verify Deployment

1. Go to **Containers** in Portainer
2. Find your `werebot` container
3. Check the **Status** - should be "running"
4. Click on the container name
5. Go to **Logs** tab
6. You should see:

```
INFO - Bot initialized successfully. Monitoring r/hiddenwerewolves+...
INFO - Currently tracking X processed comments
INFO - Currently X unsubscribed users
INFO - Starting main loop...
```

## File Structure on Server

Recommended layout:

```
/opt/bots/werebot/
├── werebot_updated.py          # Main bot code
├── nickname_mapper.py          # Nickname support (optional)
├── creds2.json                 # Google credentials (optional)
└── data/                       # Runtime data (mounted volume)
    ├── werebot.log
    ├── comments_replied_to.txt
    ├── unsubscribed_users.txt
    ├── snoozed_threads.json
    ├── vote_declarations.json
    └── werebot_checkpoint.json
```

## Managing the Container

### View Logs

1. Go to **Containers**
2. Click on `werebot`
3. Click **Logs** tab
4. Toggle **Auto-refresh logs** for live view

### Restart Container

1. Go to **Containers**
2. Click on `werebot`
3. Click **Restart** button at top

### Stop Container

1. Go to **Containers**
2. Click on `werebot`
3. Click **Stop** button

### Update Bot Code

1. Stop the container
2. Update files on the server (via SSH, volume browser, or git pull)
3. Start the container

### View Resource Usage

1. Go to **Containers**
2. Click on `werebot`
3. Click **Stats** tab
4. See CPU, Memory, Network usage

## Troubleshooting

### Container Won't Start

**Check logs:**
1. Go to **Containers**
2. Click on `werebot`
3. Go to **Logs** tab
4. Look for error messages

**Common issues:**
- Missing environment variables
- Wrong file paths in volumes
- Python dependencies not installing
- Credentials incorrect

### Can't See Files

**If using volume mounts:**
1. Check the path is correct on the host
2. Verify files exist: SSH into server and `ls /path/to/files`
3. Check permissions: `chmod 644 /path/to/files/*.py`

### Bot Not Responding

**Check if running:**
1. Container status should be "running"
2. Logs should show "Starting main loop..."

**Check Reddit credentials:**
1. Verify credentials at https://www.reddit.com/prefs/apps
2. Check environment variables in container

### Changes Not Taking Effect

**After updating code:**
1. Must restart container
2. In Portainer: Containers → werebot → Restart

### Out of Memory

**If container crashes:**
1. Go to container **Stats**
2. Check memory usage
3. Add memory limits in compose:

```yaml
deploy:
  resources:
    limits:
      memory: 256M
    reservations:
      memory: 128M
```

## Environment Variables Reference

### Required:
```
REDDIT_CLIENT_ID          # From Reddit app
REDDIT_CLIENT_SECRET      # From Reddit app
REDDIT_USERNAME           # Bot's Reddit username
REDDIT_PASSWORD           # Bot's Reddit password
REDDIT_USER_AGENT         # python:werebot:v2.0 (by /u/yourname)
```

### Optional:
```
NICKNAME_SPREADSHEET_URL  # Google Sheet URL for nicknames
NICKNAME_CREDENTIALS      # Path to creds.json (default: creds2.json)
```

## Updating Were-Bot

### Method 1: Via Portainer Volume Browser

1. Stop container
2. Go to **Volumes** → `werebot-data` → **Browse**
3. Delete old `werebot_updated.py`
4. Upload new version
5. Start container

### Method 2: Via SSH

```bash
# Stop container via Portainer first
ssh user@server
cd /opt/bots/werebot
# Update files
cp /path/to/new/werebot_updated.py .
# Restart container via Portainer
```

### Method 3: Via Git

```bash
ssh user@server
cd /opt/bots/werebot
git pull
# Restart container via Portainer
```

## Backup

### Backup Data Files

1. Go to **Volumes** in Portainer
2. Click on `werebot-data`
3. Click **Browse**
4. Download important files:
   - `comments_replied_to.txt`
   - `unsubscribed_users.txt`
   - `snoozed_threads.json`
   - `vote_declarations.json`

### Backup via Command Line

```bash
ssh user@server
cd /opt/bots/werebot/data
tar -czf werebot-backup-$(date +%Y%m%d).tar.gz *.txt *.json *.log
# Download backup file
```

## Security

### Best Practices

1. **Use environment variables** for secrets (don't hardcode)
2. **Read-only mounts** for code: `:ro` in volume mounts
3. **Separate data volume** for runtime data
4. **Limit resources** to prevent resource exhaustion
5. **Regular backups** of data files

### Secrets in Portainer

Instead of plain environment variables:

1. Go to **Secrets** in Portainer
2. Create secrets for sensitive values
3. Reference in stack:

```yaml
secrets:
  reddit_password:
    external: true
    
services:
  werebot:
    secrets:
      - reddit_password
```

## Monitoring

### Check Bot Health

**Portainer Quick Status:**
- Green = Running
- Red = Stopped
- Orange = Problem

**Log Patterns to Watch:**
```
INFO - Processed X new comments this cycle    # Bot is working
ERROR - Failed to ...                         # Something wrong
WARNING - ...                                 # Potential issue
```

### Set Up Notifications (Optional)

1. Go to **Notifications** in Portainer
2. Add webhook/email
3. Configure alerts for container stop/restart

## Common Portainer Tasks

### Clone Container

1. Go to **Containers**
2. Click on container
3. Click **Duplicate/Edit**
4. Modify settings
5. Deploy

### Export Container Config

1. Go to **Containers**
2. Click on container
3. Click **Inspect**
4. Copy JSON config

### View Container Details

1. Click on container name
2. Tabs available:
   - **Logs** - Real-time output
   - **Inspect** - Full config
   - **Stats** - Resource usage
   - **Console** - Access shell
   - **Exec Console** - Run commands