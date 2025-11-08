# Nickname Mapping Guide for Were-Bot

Allow users to tag people using short nicknames instead of full Reddit usernames!

## What It Does

Instead of typing:
```
Hey WEREBOT /u/Team-Hufflepuff /u/K9moonmoon /u/redpoemage /u/TalkNerdyToMe20
```

Users can type:
```
Hey WEREBOT Puff K9 rpm TNTM
```

Were-Bot automatically converts nicknames to Reddit usernames before tagging!

## Features

**Shorthand tagging** - Use simple nicknames instead of long usernames
**Google Sheets backend** - Easy to update without code changes
**Auto-refresh** - Nicknames update every 5 minutes
**Case-insensitive** - "puff", "Puff", "PUFF" all work
**Optional** - Works alongside regular /u/username mentions
**Cached** - Minimizes Google Sheets API calls

## Setup

### Step 1: Create Google Sheet

1. Go to Google Sheets
2. Create a new spreadsheet
3. Name it something like "Were-Bot Nicknames"
4. Set up columns:

| Nickname | Reddit Username |
|----------|----------------|
| Puff | Team-Hufflepuff |
| K9 | K9moonmoon |
| rpm | redpoemage |
| TNTM | TalkNerdyToMe20 |
| Chef | chefsk |

**Format rules:**
- Column A: Nickname (can be anything - letters, numbers, hyphens, underscores)
- Column B: Reddit Username (without /u/ prefix)
- First row is headers (will be skipped)
- Case doesn't matter for nicknames (they're matched case-insensitively)

### Step 2: Share Sheet with Bot

1. Click "Share" button in Google Sheets
2. Add this email address: `hwwbot@points-bot-228115.iam.gserviceaccount.com`
3. Give it "Viewer" permission (not Editor - bot only reads)
4. Click "Send"

### Step 3: Get Spreadsheet URL

Copy the URL from your browser, which looks like:
```
https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v/edit
```

### Step 4: Configure Were-Bot

Set environment variable:
```bash
export NICKNAME_SPREADSHEET_URL="https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit"
```

Or add to Docker:
```yaml
environment:
  - NICKNAME_SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/...
```

Or add to systemd service file:
```ini
Environment="NICKNAME_SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/..."
```

### Step 5: Copy nickname_mapper.py

Make sure `nickname_mapper.py` is in the same directory as `werebot_updated.py`:
```bash
cp nickname_mapper.py /opt/reddit-bots/werebot/
```

### Step 6: Restart Were-Bot

```bash
systemctl restart werebot
# or
docker-compose restart werebot
```

Check logs to confirm:
```
INFO - Nickname mapper enabled with 5 nicknames
```

## Usage Examples

### Example 1: Simple Nicknames

**User posts:**
```
WEREBOT

Puff K9 rpm TNTM Chef

Check out this cool thing!
```

**Were-Bot sees:**
```
/u/Team-Hufflepuff /u/K9moonmoon /u/redpoemage /u/TalkNerdyToMe20 /u/chefsk
```

**Were-Bot tags:**
```
Were-Bot Tagging: /u/Team-Hufflepuff /u/K9moonmoon /u/redpoemage

/u/author wants you to see this comment!
```

### Example 2: Mixed with Regular Usernames

**User posts:**
```
WEREBOT

Puff K9 /u/redpoemage /u/TalkNerdyToMe20

Important announcement!
```

**Were-Bot sees:**
Both nicknames AND regular /u/ mentions work together!

### Example 3: Case Insensitive

All of these work:
- `puff` → Team-Hufflepuff
- `Puff` → Team-Hufflepuff
- `PUFF` → Team-Hufflepuff
- `PuFf` → Team-Hufflepuff

### Example 4: With @ or # Prefix

These also work (optional):
- `@Puff` → Team-Hufflepuff
- `#K9` → K9moonmoon

## Updating Nicknames

Just edit the Google Sheet! Changes take effect within 5 minutes (cache refresh time).

**Add new nickname:**
1. Add row to sheet: `NewNick | their-reddit-username`
2. Wait up to 5 minutes
3. Users can now use `NewNick`

**Remove nickname:**
1. Delete row from sheet
2. Wait up to 5 minutes
3. Nickname no longer works

**Change mapping:**
1. Edit the username in Column B
2. Wait up to 5 minutes
3. Nickname now points to new username

## Advanced Configuration

### Custom Cache Duration

Default is 5 minutes. To change, edit `werebot_updated.py`:

```python
nickname_mapper = NicknameMapper(
    spreadsheet_url=NICKNAME_SPREADSHEET_URL,
    credentials_file=NICKNAME_CREDENTIALS,
    cache_duration=600  # 10 minutes instead of 5
)
```

### Different Credentials File

If not using `creds2.json`:

```bash
export NICKNAME_CREDENTIALS="/path/to/different-creds.json"
```

### Multiple Worksheets

By default, uses first worksheet. To use a different one, modify `nickname_mapper.py`:

```python
worksheet = sheet.get_worksheet(1)  # Second worksheet (0-indexed)
# or
worksheet = sheet.worksheet("Nicknames")  # By name
```

## Troubleshooting

### Nicknames not working

**Check logs:**
```bash
tail -f /opt/reddit-bots/werebot/werebot.log
```

**Look for:**
```
INFO - Nickname mapper enabled with X nicknames
```

**If you see:**
```
WARNING - Failed to load nicknames: ...
```

Check:
1. Spreadsheet URL is correct
2. Bot has access to sheet (hwwbot@points-bot-228115.iam.gserviceaccount.com)
3. Sheet format is correct (2 columns, headers in row 1)

### Bot can't access sheet

**Error:** "Permission denied" or "403"

**Solution:**
1. Share sheet with: `hwwbot@points-bot-228115.iam.gserviceaccount.com`
2. Make sure you clicked "Send" not just added the email
3. Permission must be "Viewer" or "Editor"

### Nicknames not updating

**Cache duration:** Changes take up to 5 minutes

**Force refresh:** Restart bot
```bash
systemctl restart werebot
```

### Some nicknames work, others don't

**Check sheet format:**
- No empty rows between nicknames
- Both columns filled in
- No extra spaces in usernames
- Usernames don't have /u/ prefix

### nickname_mapper.py not found

**Error:** "ModuleNotFoundError: No module named 'nickname_mapper'"

**Solution:**
```bash
# Copy to bot directory
cp nickname_mapper.py /opt/reddit-bots/werebot/

# Or check file is in same directory as werebot_updated.py
ls -la /opt/reddit-bots/werebot/
```

## Sheet Format Examples

### Good Format

```
| Nickname | Reddit Username    |
|----------|--------------------|
| Puff     | Team-Hufflepuff    |
| K9       | K9moonmoon         |
| rpm      | redpoemage         |
```

### Bad Format (with /u/)

```
| Nickname | Reddit Username    |
|----------|--------------------|
| Puff     | /u/Team-Hufflepuff |  ← Remove /u/
```

### Bad Format (reversed columns)

```
| Reddit Username | Nickname |
|-----------------|----------|
| Team-Hufflepuff | Puff     |  ← Wrong order
```

### Good Format (works with underscores/hyphens)

```
| Nickname  | Reddit Username  |
|-----------|------------------|
| K-9       | K9moonmoon       |
| TNTM_20   | TalkNerdyToMe20  |
| Chef_SK   | chefsk           |
```

## How It Works

1. User posts comment with "WEREBOT" and nicknames
2. Were-Bot fetches comment
3. Were-Bot checks nickname mapper cache (refreshes if >5 min old)
4. Were-Bot replaces nicknames with /u/username
5. Were-Bot extracts all usernames (converted + original /u/ mentions)
6. Were-Bot tags users as normal

**Example flow:**
```
Original comment:
  "WEREBOT Puff K9 /u/rpm check this out"

After nickname resolution:
  "WEREBOT /u/Team-Hufflepuff /u/K9moonmoon /u/rpm check this out"

Extracted usernames:
  ["Team-Hufflepuff", "K9moonmoon", "rpm"]

Tagged:
  /u/Team-Hufflepuff /u/K9moonmoon /u/rpm
```

## Disabling Nickname Mapping

### Temporary (until restart)

Just don't set the environment variable. Bot will run without nicknames.

### Permanent

1. Remove `NICKNAME_SPREADSHEET_URL` from config
2. Restart bot
3. Bot will log: "Nickname mapping disabled (no spreadsheet URL configured)"

## Performance

**Impact:** Minimal
- First load: ~1-2 seconds to fetch sheet
- Subsequent loads: Cached, no API call
- Cache refresh: Every 5 minutes, ~1 second

**API Quota:** 
- Google Sheets: 100 requests per 100 seconds (free tier)
- Bot uses: ~12 requests per hour (refresh every 5 min)
- Well within limits!

## Security

**Sheet access:**
- Bot only needs "Viewer" permission (read-only)
- Can't modify your sheet
- Can't access other sheets

**Credentials:**
- Same `creds2.json` used by HWWBot
- Already configured and secure

## Example Google Sheet Template

Here's a starter template you can copy:

```
Nickname	Reddit Username
Puff	Team-Hufflepuff
K9	K9moonmoon
rpm	redpoemage
TNTM	TalkNerdyToMe20
Chef	chefsk
bubba	bubbasaurus
disco	DiscoRiotSaturday
DUQ	DirtyMarTeeny
H501	Huffleypuffy501
KB	KemKatt
Kelshan	Kelshan
MLou	MyOGotS
MPW	MoonPrincesssWolf
RPS	rpspinkpanther
Sam	saraberry12
Samu	samuraintj
Wiz	wizkvothe
```

**To use this:**
1. Create new Google Sheet
2. Copy the table above
3. Paste into Sheet
4. Share with bot
5. Set environment variable
6. Restart bot


## FAQ

**Q: Can I use the same nickname for multiple people?**
A: No, last one in the sheet wins. Keep nicknames unique.

**Q: Can multiple nicknames map to the same username?**
A: Yes! You can have `Puff` and `Hufflepuff` both map to `Team-Hufflepuff`.

**Q: What if someone's Reddit username changes?**
A: Just update Column B in the sheet. Takes effect in 5 minutes.

**Q: Can players add their own nicknames?**
A: If you give them Editor access to the sheet, yes! Or use a suggestion form and mods add them.

**Q: Does this work with the 4-user minimum?**
A: Yes! Nicknames count as users. `WEREBOT Puff K9 rpm TNTM` = 4 users = will tag.

**Q: What about unsubscribed users?**
A: Nickname resolution happens first, then unsubscribe filtering. Works normally.

---
