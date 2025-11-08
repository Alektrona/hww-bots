# Were-Bot Snooze Feature Guide

Allow users to opt out of notifications for a specific thread without unsubscribing completely!

## What It Does

**Problem:** User is tagged in a busy thread but doesn't want notifications anymore for THAT thread, but still wants to be tagged in OTHER threads.

**Solution:** `WEREBOT SNOOZE` - stops notifications for just that one thread!

## Usage

### Snoozing a Thread

If you're being tagged in a thread and want to stop getting notifications:

```
WEREBOT SNOOZE
```

Were-Bot replies:
```
/u/username has snoozed this thread. You won't be tagged in any more Were-Bot notifications here.
```

That's it! You're now snoozed for this specific Reddit post.

### What Happens After Snoozing

**In this thread:**
- You won't be tagged anymore (even if people mention you)
- You won't get Reddit notifications from Were-Bot

**In other threads:**
- You'll still be tagged normally
- You'll get notifications as usual
- Your subscription to Were-Bot is unchanged

## Examples

### Example 1: Basic Snooze

**Scenario:** There's a long discussion thread and you're done reading it.

**You post:**
```
WEREBOT SNOOZE
```

**Result:** Future tags in this thread won't notify you, but you'll still be tagged in other threads.

### Example 2: Snooze vs Unsubscribe

| Command | Effect | Scope |
|---------|--------|-------|
| `WEREBOT SNOOZE` | Stop tags in THIS thread | This thread only |
| `WEREBOT!UNSUBSCRIBE` | Stop ALL tags | All threads, all subreddits |

### Example 3: Snooze in Action

**Thread:** "Game Phase 5 Discussion"

**Comment 1:** 
```
WEREBOT /u/Alice /u/Bob /u/Charlie check this out
```
→ Alice, Bob, and Charlie all get tagged

**Bob posts:**
```
WEREBOT SNOOZE
```
→ Bob snoozed this thread

**Comment 2:**
```
WEREBOT /u/Alice /u/Bob /u/Charlie /u/Dave new info!
```
→ Alice, Charlie, and Dave get tagged
→ Bob does NOT get tagged (snoozed)

## How It Works

### Thread-Specific

Snooze is tied to the Reddit **submission** (post), not individual comment chains.

**Example:**
- Post: "Game Day 5 Voting"
  - Comment: "Hey WEREBOT /u/Alice" → Alice gets tagged
  - Alice: "WEREBOT SNOOZE" → Alice snoozed
  - Comment: "WEREBOT /u/Alice again" → Alice NOT tagged
  
- Different Post: "Game Day 6 Voting"
  - Comment: "WEREBOT /u/Alice" → Alice gets tagged (different thread!)

### Persistence

Snoozes are permanent per thread. They're stored in `snoozed_threads.json` and persist across bot restarts.

### Filtering Order

When someone uses WEREBOT, usernames are filtered in this order:
1. Extract all mentioned usernames
2. Remove globally unsubscribed users
3. Remove users who snoozed THIS thread
4. Tag remaining users (if 4+)

## Technical Details

### Storage Format

Snoozes stored in `snoozed_threads.json`:
```json
{
  "abc123xyz": ["ALICE", "BOB"],
  "def456uvw": ["CHARLIE"],
  "ghi789rst": ["ALICE", "DAVE"]
}
```

Where:
- Keys are Reddit submission IDs
- Values are arrays of uppercase usernames

### File Location

```
/opt/reddit-bots/werebot/snoozed_threads.json
```

### Memory Usage

Minimal. Each snooze entry is ~50 bytes. Even 1000 snoozed threads = ~50KB.

## Commands Summary

| Command | Effect | Scope |
|---------|--------|-------|
| `WEREBOT` | Tag users | N/A |
| `WEREBOT SNOOZE` | Stop tags in this thread | This thread only |
| `WEREBOT!UNSUBSCRIBE` | Stop all tags everywhere | Global |
| `WEREBOT!SUBSCRIBE` | Resubscribe to all tags | Global |

## FAQ

**Q: How do I un-snooze a thread?**
A: You can't directly un-snooze. Just post normally in the thread - you can always manually check it even when snoozed. Snooze only affects automatic Were-Bot tags.

**Q: Does snooze work with nicknames?**
A: Yes! If someone tags you via nickname, you'll still be snoozed.

**Q: What if I snooze and then unsubscribe?**
A: Unsubscribe is global and takes precedence. You won't get tagged anywhere.

**Q: Does "WERE-BOT SNOOZE" work?**
A: Yes! Both "WEREBOT SNOOZE" and "WERE-BOT SNOOZE" work.

**Q: Is it case sensitive?**
A: No. "werebot snooze", "WEREBOT SNOOZE", "WereBot Snooze" all work.

**Q: Can I snooze multiple threads?**
A: Yes! Snooze as many threads as you want. Each is tracked separately.

**Q: Does my snooze expire?**
A: No, snoozes are permanent for that thread. The thread eventually becomes inactive naturally.

**Q: What if someone typos "WEREBOT SNOOZ"?**
A: It won't trigger. Must be exactly "WEREBOT SNOOZE" (with the E).

**Q: Can I snooze someone else?**
A: No, only you can snooze yourself. Each user must snooze individually.

## Use Cases

### Use Case 1: Busy Thread
You're in a game phase discussion that's very active, and you're being tagged frequently. You've read everything you need to read.
→ `WEREBOT SNOOZE` to stop notifications while the thread continues

### Use Case 2: Going to Bed
There's an active discussion late at night. You want to sleep without phone notifications.
→ `WEREBOT SNOOZE` to stop that specific thread's tags


## Moderator View

Moderators can check snoozed threads:

```bash
cat /opt/reddit-bots/werebot/snoozed_threads.json | python3 -m json.tool
```

Output:
```json
{
  "abc123": [
    "ALICE",
    "BOB"
  ],
  "xyz789": [
    "CHARLIE"
  ]
}
```

This shows which users have snoozed which threads.

## Troubleshooting

### Snooze not working

**Check logs:**
```bash
tail -f /opt/reddit-bots/werebot/werebot.log | grep -i snooze
```

**Expected log:**
```
INFO - User u/Alice snoozed thread abc123xyz
```

### Still getting tagged after snooze

**Possible reasons:**
1. You snoozed a different thread (each post is separate)
2. Someone is tagging you directly (not via WEREBOT)
3. Snooze command had a typo

**Verify snooze:**
```bash
grep "ALICE" /opt/reddit-bots/werebot/snoozed_threads.json
```

### Snoozed_threads.json missing

**Normal:** File is created when first snooze happens. If no one has snoozed yet, file won't exist.

### Too many snoozed threads

**Cleanup:** The file only grows when users snooze. Old threads naturally become inactive.

**Manual cleanup** (optional):
```bash
# Backup first
cp snoozed_threads.json snoozed_threads.json.backup

# Edit to remove old thread IDs
nano snoozed_threads.json
```

## Implementation Notes

### Code Location

Snooze functionality in `werebot_updated.py`:
- `get_snoozed_threads()` - Load snooze data
- `add_snooze()` - Add a snooze
- `is_snoozed()` - Check if user is snoozed
- `filter_snoozed_users()` - Remove snoozed users from tag list
- `handle_snooze()` - Process "WEREBOT SNOOZE" command

### Backwards Compatibility

Bot works fine if `snoozed_threads.json` doesn't exist. It will be created on first snooze.

### Migration

No migration needed. Just deploy the updated bot. Snooze tracking starts automatically.

## Privacy

**Who can see who snoozed?**
- Moderators with server access can view the JSON file
- Other users cannot see who snoozed
- Were-Bot doesn't announce when someone snoozes (except confirmation to the user)

**Data stored:**
- Username (uppercase)
- Thread ID (Reddit submission ID)
- No timestamps, no reason, no other data

## Statistics

Check how many users have snoozed:

```bash
python3 << 'EOF'
import json
with open('/opt/reddit-bots/werebot/snoozed_threads.json') as f:
    data = json.load(f)
    total_threads = len(data)
    total_users = sum(len(users) for users in data.values())
    print(f"Threads with snoozes: {total_threads}")
    print(f"Total snoozes: {total_users}")
EOF
```

---

Your users can now control notifications per-thread!
