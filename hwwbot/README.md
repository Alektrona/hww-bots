# HWWBot - AutoModerator Configuration Manager

Automated bot for managing AutoModerator configurations across Hidden Werewolves game subreddits.

## What It Does

HWWBot automatically updates AutoModerator rules for the game subreddits based on a Google Sheets control panel. This allows moderators to easily switch between "game mode" (only approved players can comment) and "off-season mode" (new users restrictions) without manually editing AutoMod configs.

### Key Features

- **Automatic AutoMod Updates** - Changes AutoMod rules based on Google Sheets
- **Game Mode Management** - Restricts comments to approved players during games
- **Player List Control** - Manages approved player lists from spreadsheet
- **New User Protection** - Enforces account age requirements during off-season
- **Multi-Subreddit** - Manages HiddenWerewolves, HiddenWerewolvesA, and HiddenWerewolvesB
- **One-Click Control** - Mods change one cell, bot does the rest

## How It Works

### The Workflow

1. **Mod updates Google Sheet** - Changes status to "Updating..." or sets game ON/OFF
2. **HWWBot checks spreadsheet** every cycle (default: every 30 seconds)
3. **Bot reads configuration** - Gets player lists, status, and settings
4. **Bot updates AutoMod** - Pushes new rules to each subreddit
5. **Bot confirms completion** - Updates spreadsheet status to "Complete"

### Two Modes

**Game Mode (ON):**
- Only approved players (from player list) can comment
- Non-players' comments are auto-removed
- Meta posts are exempt

**Off-Season Mode (OFF):**
- New users (accounts < 1 month) are restricted
- Approved new users (from whitelist) can still comment
- Regular users can comment freely

## Google Sheets Setup

### Required Spreadsheet

**Name:** `Hidden Werewolves - Game Sign Ups (Responses)`

This spreadsheet must have two worksheets:

### 1. "Backend" Worksheet

Controls the actual game settings.

**Layout:**

| Column A | Column B | Column C | Column D |
|----------|----------|----------|----------|
| **Row 1:** List1 | List2 | List3 | NewUsers |
| **Row 2:** Status1 | Status2 | Status3 | (unused) |

**Cell Definitions:**

**Row 1 (Headers/Lists):**
- **A1 (List1):** Player list for HiddenWerewolves (e.g., `[user1, user2, user3]`)
- **B1 (List2):** Player list for HiddenWerewolvesA
- **C1 (List3):** Player list for HiddenWerewolvesB
- **D1 (NewUsers):** Whitelist of new users allowed to comment

**Row 2 (Status):**
- **A2 (Status1):** `ON` or `OFF` for HiddenWerewolves
- **B2 (Status2):** `ON` or `OFF` for HiddenWerewolvesA
- **C2 (Status3):** `ON` or `OFF` for HiddenWerewolvesB

**Example:**

| A | B | C | D |
|---|---|---|---|
| `[alice, bob, charlie, dave]` | `[eve, frank, grace]` | `[henry, iris, jack]` | `[newbie1, newbie2]` |
| `ON` | `OFF` | `ON` | |

### 2. "HWWbot" Worksheet

Controls when the bot runs updates.

**Layout:**

| Column A | Column B | Column C | Column D | Column E |
|----------|----------|----------|----------|----------|
| (unused) | (unused) | (unused) | (unused) | **Status** |
| (unused) | (unused) | (unused) | (unused) | `Ready` or `Updating...` |

**Cell Definition:**

- **E2:** Control cell
  - Set to `Updating...` → Bot will process updates
  - Bot changes to `Complete` when done
  - Change to `Ready` to prepare for next update

**Workflow:**
1. Mod updates Backend sheet with new settings
2. Mod changes E2 in HWWbot sheet to `Updating...`
3. Bot sees "Updating...", processes changes
4. Bot updates all subreddits
5. Bot changes E2 to `Complete`
6. Mod can change to `Ready` for next time

### Player List Format

Player lists must be in AutoModerator format:

**Correct:**
```
[username1, username2, username3]
```

**Rules:**
-  Square brackets
-  Comma-separated
-  Usernames without /u/
-  All lowercase recommended
-  No spaces in usernames
-  No special characters except underscores and hyphens

### Sheet Permissions

The Google Sheet must be shared with the bot's service account:

**Share with:**
- `points-bot@points-bot-228115.iam.gserviceaccount.com`
- `hwwbot@points-bot-228115.iam.gserviceaccount.com`

**Permission level:** Editor (bot needs to write status updates)

## Usage

### Starting a Game

1. **Update player list** in Backend sheet (Column A, B, or C - Row 1)
2. **Set status to ON** in Backend sheet (Column A, B, or C - Row 2)
3. **Trigger update** by setting HWWbot sheet E2 to `Updating...`
4. **Wait ~30 seconds** for bot to process
5. **Verify** - E2 should change to `Complete`
6. **Check subreddit** - AutoMod should restrict to players only

### Ending a Game

1. **Set status to OFF** in Backend sheet (appropriate column - Row 2)
2. **Update new users list** if needed (Column D - Row 1)
3. **Trigger update** by setting HWWbot sheet E2 to `Updating...`
4. **Wait ~30 seconds** for bot to process
5. **Verify** - E2 should change to `Complete`

### Adding/Removing Players Mid-Game

1. **Update player list** in Backend sheet (add/remove usernames)
2. **Keep status as ON**
3. **Trigger update** by setting HWWbot sheet E2 to `Updating...`
4. **Wait ~30 seconds** for bot to process

### Multiple Concurrent Games

Each subreddit (HiddenWerewolves, HiddenWerewolvesA, HiddenWerewolvesB) has independent settings:

- **Column A = HiddenWerewolves**
- **Column B = HiddenWerewolvesA**
- **Column C = HiddenWerewolvesB**

You can run games in multiple subs simultaneously with different player lists.

## AutoMod Rules Generated

### When Game is ON

```yaml
# Lynch warning (always included)
type: comment
body+title (includes, regex): ['lynch']
moderators_exempt: false
comment: |
    [Message discouraging use of 'lynch' word]

# Player restriction
type: any
is_edited: false
author:
    ~name: [player_list]
parent_submission:
    ~flair_css_class: ["Meta"]
action: remove
comment: "Only players may comment in game threads"
```

### When Game is OFF

```yaml
# Lynch warning (always included)
[Same as above]

# New user restriction
type: any
is_edited: false
author:
    account_age: < 1 month
    ~name: [new_users_whitelist]
parent_submission:
    ~flair_css_class: ["Meta"]
action: remove
comment: "Account age requirements not met"
```

## Configuration

### Environment Variables

```bash
REDDIT_CLIENT_ID=your_hwwbot_client_id
REDDIT_CLIENT_SECRET=your_hwwbot_client_secret
REDDIT_USERNAME=HWWBot
REDDIT_PASSWORD=your_hwwbot_password
REDDIT_USER_AGENT=HWWBot:X.0 (by /u/yourusername)
```

### Required Files

- `creds.json` or `creds2.json` - Google service account credentials
- `hwwbot_checkpoint.json` - Auto-generated checkpoint file
- `hwwbot.log` - Auto-generated log file

## Deployment

See the main [Portainer Deployment Guide](../deployment/PORTAINER_DEPLOYMENT_GUIDE.md) for complete deployment instructions.

### Docker Compose

HWWBot is included in the main `docker-compose.yml`:

```yaml
hwwbot:
  image: python:3.11-slim
  container_name: hwwbot
  restart: unless-stopped
  environment:
    - REDDIT_CLIENT_ID=${HWWBOT_CLIENT_ID}
    - REDDIT_CLIENT_SECRET=${HWWBOT_CLIENT_SECRET}
    # ... other env vars
```

## Monitoring

### Logs

Check bot activity:
```bash
# View logs in Portainer
Containers → hwwbot → Logs

# Or via command line
docker logs hwwbot -f
```

**What to look for:**
```
INFO - Bot initialized successfully. Starting main loop...
INFO - Checking spreadsheet for updates...
INFO - Status is 'Updating...', proceeding with update
INFO - Processing r/HiddenWerewolves (Status: ON)
INFO - Successfully updated r/HiddenWerewolves
INFO - Update complete! Changed status to 'Complete'
```

### Common Log Messages

**Normal operation:**
- `Status is 'Ready', skipping this cycle` - Bot waiting for trigger
- `Successfully updated r/...` - AutoMod config updated
- `Update complete!` - All changes applied

**Issues:**
- `Failed to connect to Google Sheets` - Check credentials/permissions
- `Failed to update r/...` - Check bot has wiki edit permissions
- `Worksheet not found` - Check sheet names match exactly

## Troubleshooting

### Bot Not Updating AutoMod

**Check:**
1. Is HWWbot sheet E2 set to `Updating...`?
2. Does bot have wiki edit permissions on subreddit?
3. Are sheet names exactly `Backend` and `HWWbot`?
4. Check bot logs for errors

**Fix:**
- Grant bot wiki edit permissions: Subreddit Settings → User Management → Add as approved wiki contributor
- Verify spreadsheet name is exactly: `Hidden Werewolves - Game Sign Ups (Responses)`

### "Worksheet not found" Error

**Check:**
- Sheet must be named: `Hidden Werewolves - Game Sign Ups (Responses)`
- Worksheets must be named: `Backend` and `HWWbot`
- Capitalization matters!

**Fix:**
Rename worksheets to match exactly (including capitalization and spaces)

### Changes Not Taking Effect

**Check:**
1. Did E2 change to `Complete`? If not, bot hasn't processed yet
2. Wait 30-60 seconds between trigger and checking
3. Check bot logs to see if it ran

**Fix:**
- Set E2 back to `Ready`, then to `Updating...` again
- Restart bot if stuck

### Player Comments Still Being Removed

**Check:**
1. Is player list formatted correctly? `[user1, user2, user3]`
2. Are usernames spelled correctly?
3. Is status set to `ON`?
4. Did bot confirm update completed?

**Fix:**
- Check AutoMod wiki page directly: `reddit.com/r/subreddit/wiki/config/AutoModerator`
- Verify player list was updated
- Re-trigger update if needed

### Google Sheets Permission Denied

**Check:**
- Is sheet shared with service account email?
- Does service account have Editor permission?

**Fix:**
```
Share sheet with:
- points-bot@points-bot-228115.iam.gserviceaccount.com
- hwwbot@points-bot-228115.iam.gserviceaccount.com

Permission: Editor
```

## Advanced Usage

### Custom AutoMod Rules

The bot generates standard AutoMod configs. For custom rules:

1. Let bot update base config
2. Manually edit wiki to add custom rules
3. Note: Next bot update will overwrite custom rules

**Better approach:** Modify `hwwbot.py` to include your custom rules in the template.

### Multiple Games in Same Sub

The bot manages one config per sub. For multiple concurrent games in one sub:
- Use role/flair-based AutoMod rules
- Or manually manage AutoMod for complex scenarios

### Backup AutoMod Configs

Before major changes:
1. Copy current AutoMod wiki page
2. Save as backup
3. Make changes
4. Restore backup if needed

## Support

For issues with HWWBot:
1. Check the logs in Portainer
2. Verify Google Sheets setup matches this guide
3. Test with one subreddit first
4. Check bot has required Reddit permissions

## Credits

HWWBot manages AutoModerator configurations for r/HiddenWerewolves game subreddits.

Maintained by the HWW mod team.
