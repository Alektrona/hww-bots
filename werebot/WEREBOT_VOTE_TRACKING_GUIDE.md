# Were-Bot Vote Tracking Feature

Track declared votes during game phases! Were-Bot maintains a vote log and provides summaries on demand.

## What It Does

Players can declare their votes publicly, and Were-Bot tracks them per thread (phase). Anyone can request a tally to see the current vote standings.

**Key Features:**
- Per-thread tracking (each phase has independent votes)
- Easy vote declaration
- Top 3 candidates summary
- Full breakdown of who's voting for whom
- Auto-resets between phases (different posts = different vote logs)

## Commands

### Declare a Vote

```
WEREBOT VOTE username
```

or

```
WEREBOT VOTE /u/username
```

**Were-Bot replies:**
```
✓ Vote recorded: /u/YourName is voting for **username**
```

### Request Vote Tally

```
WEREBOT TALLY
```

**Were-Bot replies with:**
1. Top 3 candidates by vote count
2. Full breakdown of all votes

## Examples

### Example 1: Basic Usage

**Alice posts:**
```
WEREBOT VOTE Bob
```

**Were-Bot:**
```
✓ Vote recorded: /u/Alice is voting for **Bob**
```

**Charlie posts:**
```
WEREBOT VOTE Bob
```

**Were-Bot:**
```
✓ Vote recorded: /u/Charlie is voting for **Bob**
```

**Dave posts:**
```
WEREBOT VOTE Alice
```

**Were-Bot:**
```
✓ Vote recorded: /u/Dave is voting for **Alice**
```

### Example 2: Request Tally

**Anyone posts:**
```
WEREBOT TALLY
```

**Were-Bot:**
```
## Vote Tally

**Top Candidates:**

🥇 **Bob** - 2 votes
🥈 **Alice** - 1 vote

**All Votes:**

• **Bob** (2 votes): /u/ALICE, /u/CHARLIE
• **Alice** (1 vote): /u/DAVE

*Total: 3 declared votes*
```

### Example 3: Changing Your Vote

**Alice originally voted Bob, now changes to Charlie:**

```
WEREBOT VOTE Charlie
```

**Were-Bot:**
```
✓ Vote recorded: /u/Alice is voting for **Charlie**
```

Alice's vote is automatically updated. The vote tracker only remembers your most recent declaration.

### Example 4: New Phase

When a new phase starts (new Reddit post), the vote log automatically resets. Each submission has its own independent vote tracking.

**Phase 5 Post:** Vote declarations here
**Phase 6 Post:** Fresh start, no votes carried over

## Usage Details

### Formats Supported

All of these work:

```
WEREBOT VOTE username
WERE-BOT VOTE username
WEREBOT! VOTE username
WEREBOT VOTE /u/username
werebot vote username  (case-insensitive)
```

### Vote Changes

- Declaring a new vote **overwrites** your previous vote
- Only your most recent vote counts
- No "unvote" command needed - just vote for someone else

**Example:**
```
WEREBOT VOTE Alice  ← Your vote is Alice
WEREBOT VOTE Bob    ← Your vote is now Bob (Alice removed)
```

### Tally Format

The tally shows:
1. **Top 3 Candidates** - With medal emojis (🥇🥈🥉)
2. **All Votes** - Complete list of who's voting for whom
3. **Total Count** - Number of declared votes

### Thread-Specific

Votes are tracked **per Reddit post** (submission), not per comment chain.

- Each game phase (new post) = fresh vote log
- All comments in the same post share the same vote tracker
- Moving to next phase (new post) = automatic reset

## Game Integration

### During a Phase

**Start of Phase:**
```
It's Day 5! Time to vote!
```

**Players declare votes:**
```
WEREBOT VOTE Alice
WEREBOT VOTE Bob
WEREBOT VOTE Alice
...
```

**Moderator checks progress:**
```
WEREBOT TALLY
```

**Result shows current standings**

### Close to Deadline

```
10 minutes until phase end! 
WEREBOT TALLY
```

See who hasn't voted, who's leading, etc.

### New Phase

New post = automatic reset. Votes from Phase 5 don't carry to Phase 6.

## Use Cases

### Werewolf Games

**Day phase voting:**
- Players declare votes for who to lynch
- Moderators can see current tally
- Players can check standings before deadline
- Helps track who needs to vote

**Strategy discussions:**
- See how votes are trending
- Identify vote trains
- Spot unexpected vote patterns

### Other Games

**Any voting scenario:**
- Survivor-style games
- Mafia games
- Social deduction games
- Group decision-making

## Technical Details

### Storage

Votes stored in `vote_declarations.json`:

```json
{
  "abc123": {
    "ALICE": "Bob",
    "CHARLIE": "Bob",
    "DAVE": "Alice"
  },
  "xyz789": {
    "ALICE": "Charlie"
  }
}
```

Where:
- Keys are Reddit submission IDs (posts)
- Values are dicts of VOTER → target
- Voter names are uppercase (case-insensitive matching)
- Target names preserve original capitalization

### Per-Thread Isolation

Each Reddit post (submission) has its own vote log. The submission ID is the key.

**Example:**
- Post "Day 5 Voting": submission_id = `abc123`
- Post "Day 6 Voting": submission_id = `xyz789`
- Completely separate vote trackers

### Vote Updates

When you declare a vote:
1. Bot extracts target username from your comment
2. Bot records: `YOUR_USERNAME` → `target`
3. Overwrites any previous vote by you in this thread
4. Saves to file

### Tally Generation

When someone requests `WEREBOT TALLY`:
1. Bot loads votes for this submission
2. Counts votes per candidate
3. Sorts by vote count
4. Formats response with top 3 + full breakdown

## Privacy & Visibility

**Who can see votes?**
- Everyone! Votes are declared publicly via bot reply
- Tally is visible to anyone who requests it
- This is by design (public voting)

**Who can see the vote file?**
- Moderators with server access
- Not accessible to regular users
- Contains same info as public bot replies

## FAQ

**Q: Can I vote secretly?**
A: No, all votes are public when declared to Were-Bot.

**Q: Can I unvote?**
A: Just vote for someone else. Your vote changes to the new person.

**Q: Can I vote for myself?**
A: Yes! `WEREBOT VOTE myusername` works.

**Q: What if there's a tie?**
A: The tally shows all tied candidates with the same count.

**Q: Does capitalization matter?**
A: For voters, no (tracked uppercase). For targets, display preserves your capitalization.

**Q: Can I vote in old phases?**
A: Yes, but each phase is separate. Voting in an old post only affects that post's tally.

**Q: How do I see who hasn't voted?**
A: Check the tally and compare to your player list. The bot doesn't track "should vote" vs "has voted".

**Q: Can the mod override votes?**
A: Not through the bot. Mods would need to manually edit the JSON file (not recommended).

**Q: What if someone declares multiple votes in one comment?**
A: Bot only processes the first username mentioned after "VOTE".

**Q: Does this replace manual vote counts?**
A: It's a supplementary tool! Always confirm official votes per your game rules.


## Troubleshooting

### Vote not recorded

**Check:**
1. Did you spell "VOTE" correctly?
2. Did you include a username after VOTE?
3. Did bot reply with confirmation?

**If no confirmation:**
- Bot might be offline
- Comment might not have been processed yet (10-second cycle)

### Wrong vote recorded

**Fix:**
Just declare again with correct username. Latest declaration wins.

```
WEREBOT VOTE CorrectUsername
```

### Tally shows old votes

**Check:**
Are you in the correct thread (post)? Each post has separate votes.

### Can't see tally

**Try:**
Post `WEREBOT TALLY` yourself. Anyone can request it.

### Vote file corrupted

**Moderator fix:**
```bash
# Backup first
cp vote_declarations.json vote_declarations.json.backup

# Start fresh (or edit manually)
echo '{}' > vote_declarations.json

# Restart bot
systemctl restart werebot
```

## Limitations

**What it doesn't do:**
- Verify votes are "legal" (that's mod job)
- Track who hasn't voted yet
- Enforce vote changes/restrictions
- Handle secret/private votes
- Automatically close voting at deadline
- Determine vote outcomes (just tracks declarations)

**What it does:**
- Track public vote declarations
- Show current standings
- Make vote trends visible

---

Track votes easily during game phases! 🗳️
