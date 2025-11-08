# Were-Bot Random Picker Feature

Let Were-Bot make decisions for you! Randomly pick from a list of options.

## Usage

### Basic Syntax

```
WEREBOT RANDOM option1 | option2 | option3
```

Were-Bot will randomly choose one option and reply with the result!

### Response Format

```
Were-Bot randomly chose: **option2**

(from 3 options)
```

## Examples

### Example 1: Simple Choice

**User posts:**
```
What should I have for dinner?

WEREBOT RANDOM pizza | tacos | sushi | burger
```

**Were-Bot replies:**
```
Were-Bot randomly chose: **tacos**

(from 4 options)
```

### Example 2: Game Decision

**User posts:**
```
Who should we vote for?

WEREBOT RANDOM Alice | Bob | Charlie
```

**Were-Bot replies:**
```
Were-Bot randomly chose: **Charlie**

(from 3 options)
```

### Example 3: Role Assignment

**User posts:**
```
WEREBOT RANDOM Vanilla Town | Doctor | Cop | Seer | Mason
```

**Were-Bot replies:**
```
Were-Bot randomly chose: **Doctor**

(from 5 options)
```

### Example 4: Yes/No Decision

**User posts:**
```
Should we lynch today or no lynch?

WEREBOT RANDOM Lynch | No Lynch
```

**Were-Bot replies:**
```
Were-Bot randomly chose: **No Lynch**

(from 2 options)
```

### Example 5: Multi-line Options

**User posts:**
```
WEREBOT RANDOM 
Strategy A: Focus on player analysis |
Strategy B: Vote pattern review |
Strategy C: Role claim verification
```

**Were-Bot replies:**
```
Were-Bot randomly chose: **Strategy C: Role claim verification**

(from 3 options)
```

## Format Variations

All of these work:

```
WEREBOT RANDOM option1 | option2 | option3
WERE-BOT RANDOM option1 | option2 | option3
WEREBOT! RANDOM option1 | option2 | option3
WERE-BOT! RANDOM option1 | option2 | option3
werebot random option1 | option2 | option3  (case-insensitive)
```

## Rules

### Minimum Options
- **Need at least 2 options**
- If fewer than 2 options provided, Were-Bot will ask for more

**Example error:**
```
User: WEREBOT RANDOM only one option

Were-Bot: Please provide at least 2 options separated by `|` 
(e.g., `WEREBOT RANDOM option1 | option2 | option3`)
```

### Separator
- **Must use pipe character `|`** to separate options
- Spaces around pipes are optional (automatically trimmed)

**All equivalent:**
```
option1|option2|option3
option1 | option2 | option3
option1  |  option2  |  option3
```

### Option Content
- Options can contain **any text** (spaces, punctuation, numbers, etc.)
- Options are trimmed (leading/trailing spaces removed)
- Empty options are ignored

**Valid examples:**
```
WEREBOT RANDOM Yes! | No way | Maybe? | I don't know
WEREBOT RANDOM Player #1 | Player #2 | Player #3
WEREBOT RANDOM Vote now | Wait until phase end | Abstain from voting
```

## Technical Details

### Randomness
- Uses Python's `random.choice()` function
- Cryptographically secure? No (uses pseudorandom number generator)
- Fair distribution? Yes (each option has equal probability)

### Case Sensitivity
- Command keywords (`WEREBOT`, `RANDOM`) are case-insensitive
- Option content is case-sensitive (preserved exactly as typed)

**Example:**
```
WEREBOT RANDOM Alice | alice | ALICE
```
These are treated as 3 different options!

### Maximum Options
- No hard limit on number of options
- Practical limit: Reddit comment character limit (~10,000 chars)

### Whitespace Handling
- Leading/trailing spaces in options are removed
- Internal spaces are preserved

**Example:**
```
WEREBOT RANDOM   option 1   |   option 2   |   option 3   
```
Becomes: `option 1`, `option 2`, `option 3` (trimmed)

## Use Cases

### Werewolf Games

**Random voting:**
```
WEREBOT RANDOM Alice | Bob | Charlie | Dave | Eve
```

**Random action:**
```
WEREBOT RANDOM Investigate | Protect | Kill | Block
```

**Tie-breaker:**
```
We have a tie! 
WEREBOT RANDOM Alice | Bob
```

### Decision Making

**Group choices:**
```
Where should we meet for the event?
WEREBOT RANDOM Discord | Zoom | Reddit Chat
```

**Activity selection:**
```
What should we play next?
WEREBOT RANDOM Among Us | Jackbox | Codenames | Tabletop Simulator
```

### Fun & Games

**Truth or dare:**
```
WEREBOT RANDOM Truth | Dare
```

**Random name picker:**
```
Who goes first?
WEREBOT RANDOM Player1 | Player2 | Player3 | Player4
```

**Coin flip:**
```
WEREBOT RANDOM Heads | Tails
```

## Combining with Other Features

### With User Tags

You can combine random picking with tagging:

```
Let's see who gets investigated tonight!

WEREBOT RANDOM /u/Alice | /u/Bob | /u/Charlie

WEREBOT /u/Alice /u/Bob /u/Charlie /u/Dave
```

This will:
1. Pick one random user for investigation
2. Tag all users to see the result

### With Nicknames

Works with nickname mapping too:

```
WEREBOT RANDOM Puff | K9 | rpm | TNTM
```

(Note: The random picker shows the nickname, not the resolved username)

## Error Handling

### Too Few Options

**Input:**
```
WEREBOT RANDOM only-one-option
```

**Response:**
```
Please provide at least 2 options separated by `|` 
(e.g., `WEREBOT RANDOM option1 | option2 | option3`)
```

### No Options

**Input:**
```
WEREBOT RANDOM
```

**Response:**
```
Please provide at least 2 options separated by `|` 
(e.g., `WEREBOT RANDOM option1 | option2 | option3`)
```

### Empty Options Filtered

**Input:**
```
WEREBOT RANDOM option1 | | | option2
```

Empty options between pipes are ignored, treated as:
```
WEREBOT RANDOM option1 | option2
```

## FAQ

**Q: Is this truly random?**
A: It uses Python's random module, which is pseudorandom. Good enough for games, not for cryptography.

**Q: Can I use emojis in options?**
A: Yes! `WEREBOT RANDOM 🍕 | 🌮 | 🍣` works fine.

**Q: What if options have pipes in them?**
A: Unfortunately, pipe `|` is the separator, so you can't use it within options. Use alternatives like `or`, `/`, `-`, etc.

**Q: Can I weight options (make some more likely)?**
A: Not currently. All options have equal probability.

**Q: Does it prevent duplicate choices?**
A: No, each random command is independent. Same option can be chosen multiple times across different commands.

**Q: Can I make multiple random choices at once?**
A: No, one choice per command. But you can post multiple commands!

**Q: Is the result edited if I edit my comment?**
A: No, Were-Bot responds once and doesn't check for edits.

**Q: Can I see the random number generator seed?**
A: No, that's not exposed. Each choice is independent.

**Q: Does it work in private messages?**
A: No, only in the monitored subreddits (same as regular WEREBOT commands).

## Command Summary

| Command | Description | Example |
|---------|-------------|---------|
| `WEREBOT RANDOM opt1 \| opt2` | Pick randomly | Pizza or tacos? |
| Minimum options | 2 | Need at least 2 choices |
| Separator | `\|` (pipe) | Must separate with pipes |
| Case | Insensitive for command | `werebot random` works |

## Tips

### Multi-line for Readability

Instead of:
```
WEREBOT RANDOM option1 | option2 | option3 | option4 | option5
```

Try:
```
WEREBOT RANDOM 
option1 | 
option2 | 
option3 | 
option4 | 
option5
```

Both work the same!

### Descriptive Options

Instead of:
```
WEREBOT RANDOM A | B | C
```

Use:
```
WEREBOT RANDOM Strategy A: Aggressive play | Strategy B: Defensive play | Strategy C: Mixed approach
```

More context = better decisions!

### Quick Polls

Great for quick yes/no questions:
```
Should we do X?
WEREBOT RANDOM Yes ✅ | No ❌
```

## Logging

Random choices are logged:
```
INFO - RANDOM command from u/Alice: chose 'option2' from 5 options
```

Moderators can check logs to see random choices made:
```bash
tail -f /opt/reddit-bots/werebot/werebot.log | grep RANDOM
```

---

Let Were-Bot make the tough choices! 
