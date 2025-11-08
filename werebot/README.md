# Werebot - Reddit User Tagging System

Updated version of the Hidden Werewolves user notification bot that tags users when someone mentions WEREBOT in a comment.

## What's New in This Version

### Fixed Issues
1. **Updated authentication** - Modern PRAW 7.x OAuth2 authentication
2. **Comprehensive error handling** - Detailed logging and automatic recovery
3. **Better regex** - Fixed username extraction using standard Python `re` module
4. **Checkpoint system** - Tracks stats and can resume after interruption
5. **Rate limit handling** - Proper delays and retry logic
6. **Improved logic** - Cleaner code with better error messages

### Key Changes from Original

**OLD (broken regex import):**
```python
import regex as re  # This was a non-standard library
```

**NEW (standard library):**
```python
import re  # Standard Python regex
```

**OLD (bare except blocks):**
```python
try:
    comment.reply(message)
except:
    pass  # Silently fails!
```

**NEW (proper error handling):**
```python
try:
    comment.reply(message)
except praw.exceptions.RedditAPIException as e:
    logger.error(f"API error: {e}")
    # Retry logic with exponential backoff
```

## How Werebot Works

1. **Monitors comments** in r/HiddenWerewolves, r/HiddenWerewolvesA, r/HiddenWerewolvesB, and r/BadgerStudyGroup
2. **Detects WEREBOT mentions** - When someone types "WEREBOT" or "WERE-BOT" in a comment
3. **Extracts usernames** - Finds all /u/username mentions in that comment
4. **Posts notifications** - Tags users in reply comments (3 users per comment due to Reddit's notification limits)
5. **Handles subscriptions** - Users can opt-out with "WEREBOT!UNSUBSCRIBE" and opt back in with "WEREBOT!SUBSCRIBE"
6. **Thread snooze** - Users can snooze specific threads with "WEREBOT SNOOZE" to stop tags in just that post
7. **Random picker** - Users can make random choices with "WEREBOT RANDOM option1 | option2 | option3"
8. **Vote tracking** - Users can declare votes with "WEREBOT VOTE username" and request tallies with "WEREBOT TALLY"
9. **K9 mode** - Transform messages into cryptic emoji messages with "WEREBOT K9 your message" (tribute to /u/K9moonmoon!)
10. **Nickname support** - Users can tag people using short nicknames from a Google Sheet (optional feature)
11. **Easter eggs** - Fun personality responses and hidden features:
   - "I HATE FRRRRK" → Adds user to r/Fck__Frrrrk (functional)
   - "fuck werebot" → Responds "wow rude 😔"
   - "thanks werebot" or "thank you werebot" → Responds "😊"
   - "good bot" (when mentioning werebot) → Responds "😊"

## Usage Examples

### Tagging Users
```
Hey everyone! WEREBOT

/u/player1 /u/player2 /u/player3 /u/player4 /u/player5

Check out this important announcement!
```

Werebot will reply with:
```
Werebot Tagging: /u/player1 /u/player2 /u/player3 

/u/originalauthor wants you to see this comment! I am a bot, so please don't reply here.
```
(And continue with additional comments for remaining users)

### Unsubscribing
```
WEREBOT!UNSUBSCRIBE
```

Werebot replies:
```
/u/username has unsubscribed from Werebot.
```

### Resubscribing
```
WEREBOT!SUBSCRIBE
```

Werebot replies:
```
/u/username has resubscribed to Werebot.
```

### Snoozing a Thread

If you don't want to be tagged anymore in THIS specific thread (but still want tags in other threads):

```
WEREBOT SNOOZE
```

Werebot replies:
```
/u/username has snoozed this thread. You won't be tagged in any more Werebot notifications here.
```

Now you won't be tagged in any future WEREBOT comments in that specific Reddit post, but you'll still be tagged normally in other posts!

### Making Random Choices

Need Werebot to pick randomly from a list?

```
WEREBOT RANDOM option1 | option2 | option3
```

Werebot replies:
```
Werebot randomly chose: **option2**

(from 3 options)
```

**Examples:**
- `WEREBOT RANDOM pizza | tacos | sushi | burger` - Dinner decision
- `WEREBOT RANDOM Alice | Bob | Charlie` - Random vote
- `WEREBOT RANDOM Yes | No` - Quick yes/no choice
- `WEREBOT RANDOM Heads | Tails` - Coin flip

### Vote Tracking

Declare your vote publicly and track votes during a phase:

**Declare a vote:**
```
WEREBOT VOTE Alice
```

Were-Bot replies:
```
✓ Vote recorded: /u/username is voting for **Alice**
```

**Request current tally:**
```
WEREBOT TALLY
```

Were-Bot replies:
```
## Vote Tally

**Top Candidates:**

🥇 **Alice** - 3 votes
🥈 **Bob** - 2 votes
🥉 **Charlie** - 1 vote

**All Votes:**

• **Alice** (3 votes): /u/PLAYER1, /u/PLAYER2, /u/PLAYER3
• **Bob** (2 votes): /u/PLAYER4, /u/PLAYER5
• **Charlie** (1 vote): /u/PLAYER6

*Total: 6 declared votes*
```

**Key features:**
- Votes are per-thread (each phase/post has separate tracking)
- Changing your vote overwrites the previous one
- Anyone can request a tally
- Shows top 3 candidates + full breakdown

### K9 Mode

Transform your message into cryptic K9-style emoji messages! 🎨✨

```
WEREBOT K9 I love this game
```

Were-Bot replies:
```
## 🎨 K9-ified Message:

I ❤️ this 🎮

*K9-ified by Were-Bot in honor of /u/K9moonmoon* 🐕🌙
```

**Words are REPLACED with emojis!** More examples:

```
WEREBOT K9 The wolf killed the doctor at night
→ The 🐺 🔪 the ⚕️ at 🌙

WEREBOT K9 I vote for Alice she is suspicious
→ I 🗳️ for Alice she is 🤨

WEREBOT K9 I think the wolves are hiding
→ I 🤔 the 🐺 are hiding
```

The bot has 100+ word-to-emoji mappings including:
- Emotions (happy 😊, sad 😢, think 🤔, suspicious 🤨)
- Game terms (wolf 🐺, vote 🗳️, kill 🔪, night 🌙)
- Common words (love ❤️, yes ✅, no ❌, good 👍)
- And many more!

Named after /u/K9moonmoon, famous for legendary cryptic emoji messages in HWW!

### Easter Eggs

Werebt has some fun personality responses!

**Being rude:**
```
fuck werebot
```
Werebot: "wow rude 😔"

**Saying thanks:**
```
thanks werebot!
```
Werebot: "😊"

**Or:**
```
thank you werebot
```
Werebot: "😊"

**Being nice:**
```
good bot werebot!
```
Were-Bot: "😊"

**Secret subreddit:**
```
I HATE FRRRRK
```
Werebot adds you as a contributor to r/Fck__Frrrrk!

## Installation

1. Install dependencies:
```bash
pip install praw
```

2. Ensure you have these files:
   - `werebot_updated.py` - The bot
   - `test_werebot_auth.py` - Testing script

## Testing

**ALWAYS test authentication first:**

```bash
python test_werebot_auth.py
```

Expected output:
```
✓ Successfully authenticated as: u/Were-Bot
✓ Can access r/HiddenWerewolves
✓ Can read comment stream
✓ Regex extraction working correctly
```

## Running the Bot

```bash
python werebot_updated.py
```

The bot will:
1. Connect to Reddit
2. Load previous state (processed comments, unsubscribed users)
3. Monitor comments every 10 seconds
4. Process WEREBOT mentions and commands
5. Log all activity to `werebot.log`

## File Structure

```
.
├── werebot_updated.py           # Main bot script
├── test_werebot_auth.py         # Authentication test
├── comments_replied_to.txt      # Processed comments (auto-generated)
├── unsubscribed_users.txt       # Unsubscribed users (auto-generated)
├── werebot_checkpoint.json      # Stats & checkpoint (auto-generated)
└── werebot.log                  # Log file (auto-generated)
```

## Important Behavior Notes

### Minimum User Requirement
- Bot only activates when **MORE THAN 3 users** are mentioned (4+)
- This prevents spam from small tag requests
- Original logic: `if n > 3:`

### User Batching
- Reddit only notifies the first 3 username mentions per comment
- Bot automatically splits tags into multiple comments
- Each comment tags exactly 3 users (except the last batch)

### Unsubscribe List
- Stored in UPPERCASE for case-insensitive matching
- Persists between bot restarts
- Users removed from tags automatically

### Comment Tracking
- Bot remembers all processed comment IDs
- Won't process the same comment twice
- Persists between restarts

## Logging & Monitoring

### Log Levels
- **INFO**: Normal operations, successful tags
- **WARNING**: Skipped operations, retries
- **ERROR**: Failed operations
- **CRITICAL**: Fatal errors requiring intervention

### What Gets Logged
```
2025-10-23 15:30:45 - INFO - Processing tag request from u/username with 5 users
2025-10-23 15:30:47 - INFO - Tagged batch 1/2: player1, player2, player3
2025-10-23 15:30:49 - INFO - Tagged batch 2/2: player4, player5
2025-10-23 15:30:49 - INFO - Processed 1 new comments this cycle
```

### Monitoring Commands
```bash
# Watch logs in real-time
tail -f werebot.log

# Check stats
cat werebot_checkpoint.json

# Count processed comments
wc -l comments_replied_to.txt

# View unsubscribed users
cat unsubscribed_users.txt
```

## Troubleshooting

### Error: "invalid_grant" or authentication failed

**Problem:** Reddit credentials are wrong or 2FA is enabled.

**Solution:**
1. Verify credentials at https://www.reddit.com/prefs/apps
2. If 2FA enabled, append code to password: `"password:123456"`
3. Regenerate app credentials if needed

### Error: Bot not detecting WEREBOT mentions

**Problem:** Case sensitivity or spacing issues.

**Solution:**
- Bot detects: "WEREBOT", "werebot", "WERE-BOT", "were-bot"
- Case insensitive matching
- Check logs for "Skipping tag request" messages

### Error: Users not getting notified

**Possible causes:**
1. Less than 4 users mentioned (requirement is >3)
2. Users are unsubscribed
3. Username format incorrect (must be /u/username or u/username)

**Check:**
```bash
# See what usernames were extracted
grep "Processing tag request" werebot.log
```

### Error: "403 Forbidden" when posting

**Problem:** Bot is banned or doesn't have posting permissions.

**Solution:**
1. Verify bot account isn't banned from subreddits
2. Check account age/karma requirements
3. Verify bot has positive karma in target subreddits

### Bot keeps retrying the same comment

**Problem:** Comment ID not being saved to file.

**Solution:**
```bash
# Check file permissions
ls -l comments_replied_to.txt

# Verify bot can write
touch comments_replied_to.txt
```

## Rate Limiting

### Reddit API Limits
- 60 requests per minute
- 600 requests per 10 minutes

### Bot's Rate Limit Strategy
- 2 second delay between each tag comment
- 10 second cycle between comment checks
- Exponential backoff on errors (30s → 5min)
- Automatic retry on transient failures

### Staying Within Limits
Current bot behavior:
- Fetches 50 comments per cycle (1 request)
- Posts ~1-5 tag comments per cycle (varies)
- Total: ~6-10 requests per 10 seconds
- **Well within limits** at ~36-60 requests/minute peak

## Statistics Tracking

The bot tracks:
- `total_tags`: Total users tagged since bot started
- `total_unsubscribes`: Number of unsubscribe requests
- `total_subscribes`: Number of resubscribe requests
- `last_run`: Timestamp of last successful cycle

View stats:
```bash
cat werebot_checkpoint.json
```

Example output:
```json
{
  "last_run": "2025-10-23T15:45:30.123456",
  "total_tags": 247,
  "total_unsubscribes": 12,
  "total_subscribes": 3
}
```

## Security Notes

1. **Credentials**: Keep `client_secret` and `password` secure
2. **Don't commit to git**: Add to `.gitignore`:
   ```
   *.log
   *checkpoint.json
   comments_replied_to.txt
   unsubscribed_users.txt
   ```
3. **Monitor for abuse**: Check logs regularly for unusual activity
4. **Rate limiting**: Don't modify sleep timers without understanding impact

## Advanced Usage

### Running in Background

**Linux/Mac with screen:**
```bash
screen -S werebot
python werebot_updated.py
# Press Ctrl+A, then D to detach
# Reattach: screen -r werebot
```

**Linux/Mac with nohup:**
```bash
nohup python werebot_updated.py &
tail -f nohup.out
```

**Windows Task Scheduler:**
1. Create Basic Task
2. Trigger: At startup
3. Action: `pythonw.exe C:\path\to\werebot_updated.py`

### Resetting Bot State

**Clear processed comments** (bot will reprocess old comments):
```bash
rm comments_replied_to.txt
```

**Clear unsubscribed users** (everyone resubscribed):
```bash
rm unsubscribed_users.txt
```

**Reset stats**:
```bash
rm werebot_checkpoint.json
```

**WARNING**: Only do this if you know what you're doing!

## Comparison: Original vs Updated

| Feature | Original | Updated |
|---------|----------|---------|
| Error handling | Bare `except:` | Specific exceptions + retry logic |
| Logging | Print statements | Comprehensive logging system |
| Regex library | `regex` (non-standard) | `re` (standard) |
| State tracking | File-based only | File + JSON checkpoint |
| Recovery | Manual restart needed | Automatic retry with backoff |
| Monitoring | No visibility | Detailed logs + stats |
| Testing | None | Dedicated test script |

## Known Limitations

1. **3-user notification limit**: Reddit limitation, not bot limitation
2. **10-second polling**: Can miss comments posted and deleted quickly
3. **No edit detection**: Bot doesn't monitor comment edits
4. **Case-sensitive usernames**: /u/User and /u/user are treated as different
5. **No validation**: Bot doesn't check if mentioned users exist

## Future Enhancements

Possible improvements:
1. Database instead of text files for better scaling
2. Web dashboard for monitoring
3. Username validation against Reddit API
4. Configurable minimum user threshold
5. Support for editing tags after posting
6. Notification aggregation (daily digest option)

## Support

If issues persist:
1. Check `werebot.log` for detailed errors
2. Run `test_werebot_auth.py` to isolate auth issues
3. Verify all prerequisites are met
4. Check Reddit's status: https://www.redditstatus.com
