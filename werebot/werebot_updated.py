import praw
import math
import time
import os
import re
import logging
import json
import sys
import random
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Optional: Import nickname mapper if available
try:
    from nickname_mapper import NicknameMapper
    NICKNAME_MAPPER_AVAILABLE = True
except ImportError:
    NICKNAME_MAPPER_AVAILABLE = False
    logger.warning("Nickname mapper not available (nickname_mapper.py not found)")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('werebot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
CHECKPOINT_FILE = 'werebot_checkpoint.json'
COMMENTS_FILE = 'comments_replied_to.txt'
UNSUBSCRIBED_FILE = 'unsubscribed_users.txt'
SNOOZED_FILE = 'snoozed_threads.json'
VOTES_FILE = 'vote_declarations.json'
SUBREDDITS = 'hiddenwerewolves+hiddenwerewolvesa+hiddenwerewolvesb+badgerstudygroup+hiddenghosts'
COMMENT_LIMIT = 50
MAX_USERS_PER_COMMENT = 3

# Nickname mapping configuration (optional)
NICKNAME_SPREADSHEET_URL = os.environ.get('NICKNAME_SPREADSHEET_URL', '')
NICKNAME_CREDENTIALS = os.environ.get('NICKNAME_CREDENTIALS', 'creds2.json')

def load_checkpoint():
    """Load checkpoint data if it exists"""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load checkpoint: {e}")
    return {
        'last_run': None,
        'total_tags': 0,
        'total_unsubscribes': 0,
        'total_subscribes': 0
    }

def save_checkpoint(data):
    """Save checkpoint data"""
    try:
        data['last_run'] = datetime.now().isoformat()
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.debug("Checkpoint saved")
    except Exception as e:
        logger.error(f"Could not save checkpoint: {e}")

def bot_login():
    """
    Initialize Reddit connection with proper OAuth2 authentication.
    """
    # Get credentials from environment variables
    client_id = os.environ.get('WEREBOT_CLIENT_ID')
    client_secret = os.environ.get('WEREBOT_CLIENT_SECRET')
    username = os.environ.get('WEREBOT_USERNAME')
    password = os.environ.get('WEREBOT_PASSWORD')
    user_agent = os.environ.get('WEREBOT_USER_AGENT', 'Were-Bot:2.0 - Tagging system for HiddenWerewolves')
    
    # Validate required credentials
    if not all([client_id, client_secret, username, password]):
        logger.error("Missing required Reddit credentials in environment variables")
        raise ValueError("Missing Reddit credentials")
    
    try:
        logger.info(f"Attempting to log in to Reddit as {username}...")
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent
        )
        
        # Verify authentication
        user = reddit.user.me()
        logger.info(f"Successfully logged in as: u/{user.name}")
        return reddit
        
    except Exception as e:
        logger.error(f"Failed to log in to Reddit: {e}")
        raise

def get_saved_comments():
    """Load the list of comments we've already replied to"""
    if not os.path.isfile(COMMENTS_FILE):
        logger.info("No previous comments file found, starting fresh")
        return []
    
    try:
        with open(COMMENTS_FILE, "r") as f:
            comments = f.read().strip().split("\n")
            # Filter out empty strings
            comments = [c for c in comments if c]
            logger.info(f"Loaded {len(comments)} previously processed comments")
            return comments
    except Exception as e:
        logger.error(f"Error loading comments file: {e}")
        return []

def get_unsubscribed_users():
    """Load the list of unsubscribed users"""
    if not os.path.isfile(UNSUBSCRIBED_FILE):
        logger.info("No unsubscribed users file found, starting fresh")
        return []
    
    try:
        with open(UNSUBSCRIBED_FILE, "r") as f:
            users = f.read().strip().split("\n")
            # Filter out empty strings
            users = [u.upper() for u in users if u]
            logger.info(f"Loaded {len(users)} unsubscribed users")
            return users
    except Exception as e:
        logger.error(f"Error loading unsubscribed users file: {e}")
        return []

def get_snoozed_threads():
    """
    Load the snoozed threads data.
    
    Returns:
        dict: Maps submission_id -> list of usernames who snoozed that thread
              Example: {"abc123": ["USER1", "USER2"], "def456": ["USER3"]}
    """
    if not os.path.isfile(SNOOZED_FILE):
        logger.info("No snoozed threads file found, starting fresh")
        return {}
    
    try:
        with open(SNOOZED_FILE, "r") as f:
            data = json.load(f)
            logger.info(f"Loaded snoozed data for {len(data)} threads")
            return data
    except Exception as e:
        logger.error(f"Error loading snoozed threads file: {e}")
        return {}

def save_snoozed_threads(snoozed_threads):
    """Save the snoozed threads data to file"""
    try:
        with open(SNOOZED_FILE, "w") as f:
            json.dump(snoozed_threads, f, indent=2)
        logger.debug("Snoozed threads saved")
    except Exception as e:
        logger.error(f"Failed to save snoozed threads: {e}")

def add_snooze(submission_id, username, snoozed_threads):
    """
    Add a user's snooze for a specific thread.
    
    Args:
        submission_id: Reddit submission ID
        username: Username to snooze (will be uppercased)
        snoozed_threads: Current snoozed threads dict
    
    Returns:
        Updated snoozed_threads dict
    """
    username_upper = username.upper()
    
    if submission_id not in snoozed_threads:
        snoozed_threads[submission_id] = []
    
    if username_upper not in snoozed_threads[submission_id]:
        snoozed_threads[submission_id].append(username_upper)
        logger.info(f"Added snooze: u/{username} for thread {submission_id}")
    else:
        logger.debug(f"User u/{username} already snoozed thread {submission_id}")
    
    return snoozed_threads

def is_snoozed(submission_id, username, snoozed_threads):
    """
    Check if a user has snoozed a specific thread.
    
    Args:
        submission_id: Reddit submission ID
        username: Username to check
        snoozed_threads: Current snoozed threads dict
    
    Returns:
        bool: True if user has snoozed this thread
    """
    if submission_id not in snoozed_threads:
        return False
    
    return username.upper() in snoozed_threads[submission_id]

def get_vote_declarations():
    """
    Load vote declarations from file.
    
    Returns:
        dict: Maps submission_id -> {voter: target, ...}
              Example: {"abc123": {"ALICE": "Bob", "CHARLIE": "Alice"}}
    """
    if not os.path.isfile(VOTES_FILE):
        logger.info("No vote declarations file found, starting fresh")
        return {}
    
    try:
        with open(VOTES_FILE, "r") as f:
            data = json.load(f)
            logger.info(f"Loaded vote data for {len(data)} threads")
            return data
    except Exception as e:
        logger.error(f"Error loading vote declarations file: {e}")
        return {}

def save_vote_declarations(vote_data):
    """Save vote declarations to file"""
    try:
        with open(VOTES_FILE, "w") as f:
            json.dump(vote_data, f, indent=2)
        logger.debug("Vote declarations saved")
    except Exception as e:
        logger.error(f"Failed to save vote declarations: {e}")

def declare_vote(submission_id, voter, target, vote_data, permalink=''):
    """
    Declare a vote for a specific thread.
    
    Args:
        submission_id: Reddit submission ID
        voter: Username declaring the vote
        target: Username being voted for
        vote_data: Current vote declarations dict
        permalink: Comment permalink for the vote
    
    Returns:
        Updated vote_data dict
    """
    voter_upper = voter.upper()
    
    if submission_id not in vote_data:
        vote_data[submission_id] = {}
    
    # Store as dict with target and permalink
    vote_data[submission_id][voter_upper] = {
        'target': target,
        'permalink': permalink
    }
    logger.info(f"Vote declared: {voter} → {target} in thread {submission_id}")
    
    return vote_data

def get_vote_summary(submission_id, vote_data):
    """
    Get a summary of votes for a specific thread.
    
    Args:
        submission_id: Reddit submission ID
        vote_data: Current vote declarations dict
    
    Returns:
        tuple: (top_3_candidates, all_votes_breakdown)
    """
    if submission_id not in vote_data or not vote_data[submission_id]:
        return [], {}
    
    votes = vote_data[submission_id]
    
    # Count votes per target
    vote_counts = {}
    for voter, target in votes.items():
        target_upper = target.upper()
        if target_upper not in vote_counts:
            vote_counts[target_upper] = {
                'count': 0,
                'voters': [],
                'display_name': target  # Keep original capitalization
            }
        vote_counts[target_upper]['count'] += 1
        vote_counts[target_upper]['voters'].append(voter)
    
    # Sort by count (descending)
    sorted_candidates = sorted(
        vote_counts.items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )
    
    # Get top 3
    top_3 = [(name, data['count'], data['display_name']) 
             for name, data in sorted_candidates[:3]]
    
    return top_3, votes

def save_comment_id(comment_id):
    """Append a comment ID to the processed comments file"""
    try:
        with open(COMMENTS_FILE, "a") as f:
            f.write(comment_id + "\n")
    except Exception as e:
        logger.error(f"Failed to save comment ID {comment_id}: {e}")

def extract_usernames(text):
    """
    Extract all /u/username mentions from text.
    Returns a deduplicated list of usernames.
    """
    # Split by lines and process each line
    lines = text.split('\n')
    usernames = []
    
    for line in lines:
        # Find all /u/username patterns
        # Pattern matches: /u/ followed by alphanumeric, dash, or underscore
        # Must be surrounded by non-alphanumeric chars (or start/end of line)
        matches = re.findall(r'(?:^|[^0-9a-zA-Z])[uU]/([a-zA-Z0-9_-]+)(?:[^0-9a-zA-Z_-]|$)', " " + line + " ")
        usernames.extend(matches)
    
    # Deduplicate while preserving order (case-insensitive)
    seen = set()
    unique_usernames = []
    for username in usernames:
        username_upper = username.upper()
        if username_upper not in seen:
            seen.add(username_upper)
            unique_usernames.append(username)
    
    return unique_usernames

def filter_subscribed_users(usernames, unsubscribed_users):
    """Remove unsubscribed users from the username list"""
    unsubscribed_upper = [u.upper() for u in unsubscribed_users]
    return [u for u in usernames if u.upper() not in unsubscribed_upper]

def filter_snoozed_users(usernames, submission_id, snoozed_threads):
    """
    Remove users who have snoozed this specific thread.
    
    Args:
        usernames: List of usernames to filter
        submission_id: The Reddit submission ID
        snoozed_threads: Dict of snoozed threads
    
    Returns:
        List of usernames with snoozed users removed
    """
    if submission_id not in snoozed_threads:
        return usernames
    
    snoozed_users = snoozed_threads[submission_id]
    filtered = [u for u in usernames if u.upper() not in snoozed_users]
    
    removed_count = len(usernames) - len(filtered)
    if removed_count > 0:
        logger.info(f"Filtered out {removed_count} snoozed user(s) for thread {submission_id}")
    
    return filtered

def create_tag_message(author, comment):
    """Create the message that gets posted with tags"""
    permalink = f"https://www.reddit.com{comment.submission.permalink}{comment.id}"
    return f".\n\n/u/{author} wants you to see [this comment!]({permalink}) I am a bot, so please don't reply here."

def send_tags(comment, usernames, checkpoint):
    """
    Send tag notifications in batches of 3 users per comment.
    Reddit only notifies the first 3 users mentioned in a comment.
    """
    if not usernames:
        logger.warning("No users to tag")
        return False
    
    n = len(usernames)
    num_comments = math.ceil(n / MAX_USERS_PER_COMMENT)
    
    logger.info(f"Tagging {n} users across {num_comments} comment(s)")
    
    message = create_tag_message(comment.author, comment)
    current_comment = comment
    
    try:
        # Create comments in batches of 3
        for i in range(num_comments):
            start_idx = i * MAX_USERS_PER_COMMENT
            end_idx = min(start_idx + MAX_USERS_PER_COMMENT, n)
            batch = usernames[start_idx:end_idx]
            
            # Format the tags
            tags = " ".join([f"/u/{username}" for username in batch])
            reply_text = f"**Werebot Tagging:** {tags} {message}"
            
            # Post the comment with retry logic
            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                try:
                    current_comment = current_comment.reply(reply_text)
                    logger.info(f"Tagged batch {i+1}/{num_comments}: {', '.join(batch)}")
                    time.sleep(2)  # Rate limiting
                    break
                except praw.exceptions.RedditAPIException as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        logger.error(f"Failed to post tags after {max_retries} attempts: {e}")
                        raise
                    logger.warning(f"API error, retrying ({retry_count}/{max_retries})...")
                    time.sleep(5)
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        logger.error(f"Unexpected error posting tags: {e}")
                        raise
                    logger.warning(f"Error posting comment, retrying ({retry_count}/{max_retries})...")
                    time.sleep(5)
        
        checkpoint['total_tags'] += n
        return True
        
    except Exception as e:
        logger.error(f"Failed to send tags: {e}")
        return False

def handle_unsubscribe(comment, unsubscribed_users, checkpoint):
    """Handle a user unsubscribing from Werebot"""
    username_upper = str(comment.author).upper()
    
    if username_upper not in unsubscribed_users:
        unsubscribed_users.append(username_upper)
        
        try:
            with open(UNSUBSCRIBED_FILE, "a") as f:
                f.write(username_upper + "\n")
            logger.info(f"User u/{comment.author} unsubscribed")
        except Exception as e:
            logger.error(f"Failed to save unsubscribe: {e}")
            return False
    else:
        logger.info(f"User u/{comment.author} was already unsubscribed")
    
    # Reply to confirm
    message = f"/u/{comment.author} has unsubscribed from Werebot."
    try:
        comment.reply(message)
        checkpoint['total_unsubscribes'] += 1
        time.sleep(2)
        return True
    except Exception as e:
        logger.error(f"Failed to reply to unsubscribe: {e}")
        return False

def handle_subscribe(comment, unsubscribed_users, checkpoint):
    """Handle a user resubscribing to Werebot"""
    username_upper = str(comment.author).upper()
    
    if username_upper in unsubscribed_users:
        # Remove from list
        unsubscribed_users.remove(username_upper)
        
        # Rewrite the file without this user
        try:
            with open(UNSUBSCRIBED_FILE, "w") as f:
                for user in unsubscribed_users:
                    f.write(user + "\n")
            logger.info(f"User u/{comment.author} resubscribed")
        except Exception as e:
            logger.error(f"Failed to save subscribe: {e}")
            return False
    else:
        logger.info(f"User u/{comment.author} was not unsubscribed")
    
    # Reply to confirm
    message = f"/u/{comment.author} has resubscribed to Werebot."
    try:
        comment.reply(message)
        checkpoint['total_subscribes'] += 1
        time.sleep(2)
        return True
    except Exception as e:
        logger.error(f"Failed to reply to subscribe: {e}")
        return False

def handle_snooze(comment, snoozed_threads):
    """
    Handle a user snoozing a specific thread.
    User won't be tagged in any more WEREBOT comments in this thread.
    
    Args:
        comment: The comment containing "WEREBOT SNOOZE"
        snoozed_threads: Current snoozed threads dict
    
    Returns:
        Updated snoozed_threads dict, or None if failed
    """
    username = str(comment.author)
    submission_id = comment.submission.id
    
    # Add snooze
    snoozed_threads = add_snooze(submission_id, username, snoozed_threads)
    
    # Save to file
    save_snoozed_threads(snoozed_threads)
    
    # Reply to confirm
    message = f"/u/{username} has snoozed this thread. You won't be tagged in any more Werebot notifications here."
    try:
        comment.reply(message)
        logger.info(f"User u/{username} snoozed thread {submission_id}")
        time.sleep(2)
        return snoozed_threads
    except Exception as e:
        logger.error(f"Failed to reply to snooze: {e}")
        return None

def handle_random(comment):
    """
    Handle WEREBOT RANDOM command to pick randomly from options.
    
    Supports formats:
    - WEREBOT RANDOM option1 | option2 | option3
    - WEREBOT! RANDOM option1 | option2 | option3
    - WERE-BOT RANDOM option1 | option2 | option3
    
    Args:
        comment: The comment containing "WEREBOT RANDOM"
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Extract the text after RANDOM
        comment_text = comment.body
        
        # Find RANDOM keyword (case-insensitive)
        match = re.search(r'(?:WEREBOT|WERE-BOT)!?\s+RANDOM\s+(.+)', comment_text, re.IGNORECASE | re.DOTALL)
        
        if not match:
            logger.warning(f"RANDOM command found but couldn't parse options in comment {comment.id}")
            return False
        
        options_text = match.group(1).strip()
        
        # Split by pipe character
        options = [opt.strip() for opt in options_text.split('|')]
        
        # Filter out empty options
        options = [opt for opt in options if opt]
        
        if len(options) < 2:
            # Need at least 2 options
            message = "Please provide at least 2 options separated by `|` (e.g., `WEREBOT RANDOM option1 | option2 | option3`)"
            comment.reply(message)
            logger.info(f"RANDOM command from u/{comment.author} had insufficient options")
            time.sleep(2)
            return True
        
        # Pick random option
        chosen = random.choice(options)
        
        # Reply with result
        message = f"Werebot randomly chose: **{chosen}**\n\n"
        message += f"*(from {len(options)} options)*"
        
        comment.reply(message)
        logger.info(f"RANDOM command from u/{comment.author}: chose '{chosen}' from {len(options)} options")
        time.sleep(2)
        return True
        
    except Exception as e:
        logger.error(f"Failed to process RANDOM command: {e}")
        return False

def handle_vote_declaration(comment, vote_data, nickname_mapper=None):
    """
    Handle WEREBOT VOTE [username] command.
    
    Formats supported:
    - WEREBOT VOTE username
    - WEREBOT VOTE /u/username
    - WERE-BOT VOTE username
    
    Args:
        comment: The comment containing vote declaration
        vote_data: Current vote declarations dict
        nickname_mapper: Optional NicknameMapper for validating nicknames
    
    Returns:
        Updated vote_data dict, or None if failed
    """
    try:
        voter = str(comment.author)
        submission_id = comment.submission.id
        
        # Extract target from comment
        match = re.search(r'(?:WEREBOT|WERE-BOT)!?\s+VOTE\s+(?:/u/)?([a-zA-Z0-9_-]+)', 
                         comment.body, re.IGNORECASE)
        
        if not match:
            logger.warning(f"VOTE command found but couldn't parse target in comment {comment.id}")
            return None
        
        target = match.group(1)
        
        # Validate target
        is_valid = False
        display_target = target
        
        # Check if it starts with /u/ in the original comment
        if '/u/' in comment.body.lower():
            is_valid = True
            display_target = target
        # Check if it's a known nickname (use get_username method)
        elif nickname_mapper:
            resolved = nickname_mapper.get_username(target)
            if resolved:
                is_valid = True
                display_target = resolved
        
        # Reject invalid targets (like "and", "but", etc.)
        if not is_valid:
            message = f"⚠️ Invalid vote target: **{target}**\n\n"
            message += "Please vote for either:\n"
            message += "- A Reddit username with /u/ (e.g., `WEREBOT VOTE /u/username`)\n"
            if nickname_mapper:
                message += "- A registered nickname (e.g., `WEREBOT VOTE Puff`)\n"
            comment.reply(message)
            logger.info(f"Rejected invalid vote from u/{voter} for '{target}'")
            time.sleep(2)
            return None
        
        # Declare the vote - store permalink too
        voter_upper = voter.upper()
        if submission_id not in vote_data:
            vote_data[submission_id] = {}
        
        vote_data[submission_id][voter_upper] = {
            'target': display_target,
            'permalink': comment.permalink
        }
        save_vote_declarations(vote_data)
        
        # Reply to confirm
        message = f"✓ Vote recorded: /u/{voter} is voting for **{display_target}**"
        comment.reply(message)
        logger.info(f"Vote declaration: u/{voter} → {display_target} in thread {submission_id}")
        time.sleep(2)
        
        return vote_data
        
    except Exception as e:
        logger.error(f"Failed to process VOTE declaration: {e}")
        return None

def handle_vote_tally(comment, vote_data):
    """
    Handle WEREBOT TALLY command to show vote summary.
    
    Shows:
    - Top 3 candidates by vote count
    - Full breakdown of who's voting for whom with clickable links
    
    Args:
        comment: The comment requesting tally
        vote_data: Current vote declarations dict
    
    Returns:
        True if successful, False otherwise
    """
    try:
        submission_id = comment.submission.id
        
        top_3, all_votes = get_vote_summary(submission_id, vote_data)
        
        if not all_votes:
            message = "No votes have been declared in this thread yet.\n\n"
            message += "Use `WEREBOT VOTE username` to declare your vote!"
            comment.reply(message)
            time.sleep(2)
            return True
        
        # Build response
        message = "## Vote Tally\n\n"
        
        # Top 3 candidates
        if top_3:
            message += "**Top Candidates:**\n\n"
            for i, (name_upper, count, display_name) in enumerate(top_3, 1):
                emoji = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else "▪️"
                plural = "vote" if count == 1 else "votes"
                message += f"{emoji} **{display_name}** - {count} {plural}\n"
            message += "\n"
        
        # Full breakdown
        message += "**All Votes:**\n\n"
        
        # Group by target
        votes_by_target = {}
        for voter, vote_info in all_votes.items():
            # Handle both old format (string) and new format (dict)
            if isinstance(vote_info, dict):
                target = vote_info['target']
                permalink = vote_info.get('permalink', '')
            else:
                # Old format compatibility
                target = vote_info
                permalink = ''
            
            target_upper = target.upper()
            if target_upper not in votes_by_target:
                votes_by_target[target_upper] = {
                    'display_name': target,
                    'voters': []
                }
            votes_by_target[target_upper]['voters'].append({
                'name': voter,
                'permalink': permalink
            })
        
        # Sort by vote count
        sorted_targets = sorted(
            votes_by_target.items(),
            key=lambda x: len(x[1]['voters']),
            reverse=True
        )
        
        for target_upper, data in sorted_targets:
            # Build voter list with links
            voter_links = []
            for voter_info in data['voters']:
                voter_name = voter_info['name'].title()  # Fix ALL CAPS
                if voter_info['permalink']:
                    # Create clickable link to vote comment
                    voter_link = f"[{voter_name}](https://reddit.com{voter_info['permalink']})"
                else:
                    # No link for old data
                    voter_link = f"/u/{voter_name}"
                voter_links.append(voter_link)
            
            voters_list = ", ".join(voter_links)
            count = len(data['voters'])
            plural = "vote" if count == 1 else "votes"
            message += f"• **{data['display_name']}** ({count} {plural}): {voters_list}\n"
        
        message += f"\n*Total: {len(all_votes)} declared votes*"
        
        comment.reply(message)
        logger.info(f"Vote tally requested in thread {submission_id}: {len(all_votes)} votes")
        time.sleep(2)
        return True
        
    except Exception as e:
        logger.error(f"Failed to process TALLY command: {e}")
        return False

# K9 Emoji Dictionary
K9_EMOJI_MAP = {
    # === WEREWOLF/MAFIA GAME TERMS ===
    # Roles
    'wolf': '🐺', 'werewolf': '🐺', 'wolves': '🐺', 'wwolf': '🐺',
    'town': '🏘️', 'townie': '🏘️', 'villager': '👤', 'village': '🏘️',
    'seer': '🔮', 'oracle': '🔮', 'fortune': '🔮',
    'doctor': '⚕️', 'healer': '⚕️', 'medic': '⚕️',
    'cop': '👮', 'detective': '🕵️', 'investigator': '🕵️',
    'bodyguard': '🛡️', 'guardian': '🛡️', 'protector': '🛡️',
    'vigilante': '🔫', 'vig': '🔫', 'hunter': '🎯',
    'jester': '🤡', 'fool': '🤡',
    'godfather': '🤵', 'mafia': '🕴️',
    'witch': '🧙', 'wizard': '🧙',
    'mayor': '👔', 'veteran': '🎖️',
    'arsonist': '🔥', 'serial': '🔪',
    'vampire': '🧛', 'vamp': '🧛',
    'cultist': '👹', 'cult': '👹',
    
    # Actions
    'kill': '🔪', 'killed': '🔪', 'murder': '🔪', 'attack': '🔪',
    'die': '💀', 'died': '💀', 'dead': '💀', 'death': '💀',
    'lynch': '🪢', 'hang': '🪢', 'execute': '🪢',
    'vote': '🗳️', 'voting': '🗳️', 'ballot': '🗳️',
    'protect': '🛡️', 'save': '🛡️', 'guard': '🛡️',
    'investigate': '🔍', 'inspect': '🔍', 'check': '🔍',
    'heal': '💊', 'revive': '💊',
    'poison': '☠️', 'poisoned': '☠️',
    'shoot': '🔫', 'shot': '🔫',
    'block': '🚫', 'blocked': '🚫', 'roleblock': '🚫',
    'frame': '🖼️', 'framed': '🖼️',
    'convert': '🔄', 'recruit': '🔄',
    
    # Game States
    'night': '🌙', 'dark': '🌙', 'nighttime': '🌙',
    'day': '☀️', 'daytime': '☀️', 'morning': '🌅',
    'phase': '⏰', 'turn': '⏰',
    'game': '🎮', 'match': '🎮', 'round': '🎮',
    'start': '▶️', 'begin': '▶️',
    'end': '⏹️', 'finish': '⏹️', 'over': '⏹️',
    'win': '🏆', 'won': '🏆', 'victory': '🏆', 'winner': '🏆',
    'lose': '💔', 'lost': '💔', 'defeat': '💔', 'loser': '💔',
    
    # Suspicion & Social
    'sus': '🤨', 'suspicious': '🤨', 'suspect': '🤨', 'sketchy': '🤨',
    'trust': '🤝', 'trusted': '🤝', 'town': '🤝',
    'claim': '📢', 'claims': '📢', 'claiming': '📢',
    'lie': '🤥', 'lying': '🤥', 'liar': '🤥', 'fake': '🤥',
    'truth': '✅', 'honest': '✅', 'real': '✅',
    'guilty': '😈', 'evil': '😈', 'bad': '👎', 'scum': '😈',
    'innocent': '😇', 'good': '👍', 'townie': '😇',
    'soft': '🫣', 'softing': '🫣',
    'hard': '💪', 'hardclaim': '💪',
    
    # === EMOTIONS & REACTIONS ===
    'happy': '😊', 'smile': '😊', 'glad': '😊', 'joy': '😊',
    'sad': '😢', 'cry': '😭', 'crying': '😭', 'upset': '😢',
    'angry': '😠', 'mad': '😠', 'rage': '😡', 'furious': '😡',
    'laugh': '😂', 'lol': '😂', 'lmao': '😂', 'rofl': '😂', 'haha': '😂',
    'think': '🤔', 'thinking': '🤔', 'hmm': '🤔', 'hmmm': '🤔',
    'confused': '😕', 'confuse': '😕', 'huh': '😕', 'what': '❓',
    'shock': '😱', 'shocked': '😱', 'omg': '😱', 'gasp': '😱',
    'worry': '😰', 'worried': '😰', 'nervous': '😰', 'anxious': '😰',
    'scared': '😨', 'afraid': '😨', 'fear': '😨', 'terrified': '😨',
    'excited': '🤩', 'hype': '🤩', 'pumped': '🤩',
    'bored': '😑', 'boring': '😑', 'meh': '😑',
    'tired': '😴', 'sleep': '😴', 'sleepy': '😴', 'exhausted': '😴',
    'cool': '😎', 'nice': '👌', 'great': '👍', 'awesome': '🔥',
    'yay': '🎉', 'yeet': '🎉', 'woohoo': '🎉',
    'oof': '😬', 'ouch': '😬', 'yikes': '😬',
    'bruh': '🤦', 'facepalm': '🤦', 'smh': '🤦',
    'shrug': '🤷', 'idk': '🤷', 'dunno': '🤷',
    'eyes': '👀', 'look': '👀', 'looking': '👀', 'watch': '👀', 'see': '👀',
    'skull': '💀', 'rip': '💀', 'ded': '💀',
    'salty': '🧂', 'salt': '🧂',
    'mood': '💯', 'same': '💯', 'facts': '💯', 'fr': '💯',
    
    # === COMMON WORDS ===
    'love': '❤️', 'heart': '❤️', 'like': '👍',
    'hate': '💔', 'dislike': '👎',
    'yes': '✅', 'yeah': '✅', 'yep': '✅', 'yup': '✅',
    'no': '❌', 'nope': '❌', 'nah': '❌',
    'ok': '👌', 'okay': '👌', 'alright': '👌',
    'maybe': '🤷', 'perhaps': '🤷', 'possibly': '🤷',
    'please': '🙏', 'pls': '🙏',
    'thanks': '🙏', 'thank': '🙏', 'thx': '🙏', 'ty': '🙏',
    'sorry': '😅', 'sry': '😅', 'oops': '😅',
    'wow': '😮', 'whoa': '😮', 'woah': '😮',
    'wait': '✋', 'hold': '✋', 'stop': '✋',
    'go': '➡️', 'next': '➡️', 'continue': '➡️',
    'back': '⬅️', 'return': '⬅️', 'previous': '⬅️',
    'up': '⬆️', 'down': '⬇️',
    'new': '🆕', 'fresh': '🆕',
    'old': '👴', 'ancient': '👴',
    'fast': '⚡', 'quick': '⚡', 'speed': '⚡',
    'slow': '🐌', 'slowly': '🐌',
    'big': '📏', 'large': '📏', 'huge': '📏',
    'small': '🤏', 'tiny': '🤏', 'little': '🤏',
    'hot': '🔥', 'fire': '🔥', 'lit': '🔥', 'heat': '🔥',
    'cold': '🥶', 'freeze': '🥶', 'frozen': '🥶', 'ice': '🧊',
    
    # === NUMBERS ===
    'zero': '0️⃣', 'none': '0️⃣',
    'one': '1️⃣', 'first': '1️⃣',
    'two': '2️⃣', 'second': '2️⃣',
    'three': '3️⃣', 'third': '3️⃣',
    'four': '4️⃣', 'fourth': '4️⃣',
    'five': '5️⃣', 'fifth': '5️⃣',
    'six': '6️⃣', 'sixth': '6️⃣',
    'seven': '7️⃣', 'seventh': '7️⃣',
    'eight': '8️⃣', 'eighth': '8️⃣',
    'nine': '9️⃣', 'ninth': '9️⃣',
    'ten': '🔟', 'tenth': '🔟',
    'hundred': '💯',
    
    # === TIME ===
    'time': '⏰', 'clock': '⏰', 'hour': '⏰',
    'today': '📅', 'tonight': '🌙',
    'tomorrow': '📆', 'future': '🔮',
    'yesterday': '📆', 'past': '📜',
    'now': '⚡', 'current': '⚡',
    'soon': '⏳', 'later': '⏳', 'wait': '⏳',
    'early': '🌅', 'late': '🌙',
    
    # === CELEBRATIONS ===
    'party': '🎉', 'celebrate': '🎊', 'celebration': '🎊',
    'congratulations': '🎊', 'congrats': '🎊', 'gratz': '🎊', 'grats': '🎊',
    'birthday': '🎂', 'bday': '🎂', 'cake': '🎂',
    'gift': '🎁', 'present': '🎁',
    'cheers': '🍻', 'toast': '🥂',
    
    # === FOOD & DRINK ===
    'food': '🍔', 'eat': '🍴', 'eating': '🍴', 'hungry': '🤤',
    'pizza': '🍕', 'burger': '🍔', 'taco': '🌮', 'burrito': '🌯',
    'sandwich': '🥪', 'hotdog': '🌭', 'fries': '🍟',
    'pasta': '🍝', 'spaghetti': '🍝', 'ramen': '🍜',
    'sushi': '🍣', 'rice': '🍚',
    'chicken': '🍗', 'meat': '🥩', 'steak': '🥩',
    'salad': '🥗', 'veggies': '🥗', 'vegetables': '🥗',
    'fruit': '🍎', 'apple': '🍎', 'banana': '🍌', 'orange': '🍊',
    'strawberry': '🍓', 'watermelon': '🍉', 'grapes': '🍇',
    'bread': '🍞', 'toast': '🍞', 'bagel': '🥯',
    'cheese': '🧀', 'egg': '🥚', 'bacon': '🥓',
    'dessert': '🍰', 'sweet': '🍰', 'candy': '🍬',
    'cookie': '🍪', 'chocolate': '🍫', 'donut': '🍩',
    'icecream': '🍦', 'cream': '🍦',
    'drink': '🥤', 'beverage': '🥤',
    'coffee': '☕', 'tea': '🍵', 'latte': '☕',
    'water': '💧', 'milk': '🥛', 'juice': '🧃',
    'beer': '🍺', 'wine': '🍷', 'champagne': '🍾',
    'cocktail': '🍹', 'martini': '🍸', 'shot': '🥃',
    
    # === ANIMALS ===
    'dog': '🐕', 'puppy': '🐕', 'doggo': '🐕', 'pupper': '🐕',
    'cat': '🐱', 'kitty': '🐱', 'kitten': '🐱',
    'bird': '🐦', 'duck': '🦆', 'chicken': '🐔',
    'fish': '🐟', 'shark': '🦈', 'whale': '🐋', 'dolphin': '🐬',
    'snake': '🐍', 'dragon': '🐉',
    'bear': '🐻', 'panda': '🐼', 'koala': '🐨',
    'monkey': '🐵', 'gorilla': '🦍',
    'lion': '🦁', 'tiger': '🐯', 'leopard': '🐆',
    'fox': '🦊', 'raccoon': '🦝', 'squirrel': '🐿️',
    'rabbit': '🐰', 'bunny': '🐰', 'hamster': '🐹',
    'frog': '🐸', 'turtle': '🐢', 'lizard': '🦎',
    'bug': '🐛', 'bee': '🐝', 'butterfly': '🦋', 'spider': '🕷️',
    'unicorn': '🦄', 'pegasus': '🦄',
    'ghost': '👻', 'alien': '👽', 'robot': '🤖',
    
    # === NATURE ===
    'sun': '☀️', 'sunny': '☀️', 'sunshine': '☀️',
    'moon': '🌙', 'lunar': '🌙',
    'star': '⭐', 'stars': '✨', 'sparkle': '✨', 'shine': '✨',
    'cloud': '☁️', 'cloudy': '☁️',
    'rain': '🌧️', 'rainy': '🌧️', 'storm': '⛈️',
    'snow': '❄️', 'snowy': '❄️', 'winter': '❄️',
    'wind': '💨', 'windy': '💨', 'breeze': '💨',
    'lightning': '⚡', 'thunder': '⚡',
    'rainbow': '🌈', 'colorful': '🌈',
    'flower': '🌸', 'flowers': '🌺', 'rose': '🌹',
    'tree': '🌲', 'forest': '🌲', 'woods': '🌲',
    'plant': '🌱', 'leaf': '🍃', 'leaves': '🍃',
    'mountain': '⛰️', 'hill': '⛰️',
    'ocean': '🌊', 'sea': '🌊', 'wave': '🌊', 'beach': '🏖️',
    'island': '🏝️', 'desert': '🏜️',
    'earth': '🌍', 'world': '🌎', 'globe': '🌏',
    'planet': '🪐', 'space': '🌌', 'galaxy': '🌌',
    
    # === PLACES & TRAVEL ===
    'home': '🏠', 'house': '🏠',
    'building': '🏢', 'office': '🏢', 'work': '💼',
    'school': '🏫', 'university': '🎓', 'college': '🎓',
    'hospital': '🏥', 'pharmacy': '💊',
    'store': '🏪', 'shop': '🛍️', 'mall': '🛍️',
    'restaurant': '🍽️', 'cafe': '☕',
    'hotel': '🏨', 'motel': '🏨',
    'airport': '✈️', 'plane': '✈️', 'flight': '✈️',
    'train': '🚂', 'subway': '🚇', 'bus': '🚌',
    'car': '🚗', 'taxi': '🚕', 'truck': '🚚',
    'bike': '🚲', 'bicycle': '🚲',
    'boat': '⛵', 'ship': '🚢',
    'rocket': '🚀', 'spaceship': '🚀',
    'castle': '🏰', 'tower': '🗼',
    'city': '🌆', 'town': '🏘️',
    'country': '🗺️', 'map': '🗺️',
    'flag': '🚩', 'banner': '🚩',
    
    # === OBJECTS ===
    'phone': '📱', 'mobile': '📱', 'cell': '📱',
    'computer': '💻', 'laptop': '💻', 'pc': '💻',
    'keyboard': '⌨️', 'mouse': '🖱️',
    'camera': '📷', 'photo': '📸', 'picture': '🖼️',
    'tv': '📺', 'television': '📺', 'screen': '📺',
    'book': '📖', 'books': '📚', 'read': '📖', 'reading': '📖',
    'pen': '🖊️', 'pencil': '✏️', 'write': '✍️', 'writing': '✍️',
    'paper': '📄', 'document': '📄', 'note': '📝',
    'mail': '📧', 'email': '📧', 'letter': '✉️',
    'gift': '🎁', 'box': '📦', 'package': '📦',
    'money': '💰', 'cash': '💵', 'dollar': '💵', 'rich': '💰',
    'coin': '🪙', 'credit': '💳', 'card': '💳',
    'key': '🔑', 'lock': '🔒', 'unlock': '🔓',
    'tool': '🔧', 'wrench': '🔧', 'hammer': '🔨',
    'knife': '🔪', 'sword': '⚔️', 'shield': '🛡️',
    'gun': '🔫', 'pistol': '🔫', 'weapon': '🔫',
    'bomb': '💣', 'explosive': '💣', 'boom': '💥',
    'bell': '🔔', 'alarm': '⏰',
    'light': '💡', 'bulb': '💡', 'lamp': '💡',
    'candle': '🕯️', 'torch': '🔦',
    'battery': '🔋', 'power': '⚡', 'energy': '⚡',
    'magnet': '🧲', 'magnetic': '🧲',
    'pill': '💊', 'medicine': '💊', 'drug': '💊',
    'bandage': '🩹', 'band': '🩹',
    'mirror': '🪞', 'reflection': '🪞',
    'door': '🚪', 'window': '🪟',
    'chair': '🪑', 'couch': '🛋️', 'bed': '🛏️',
    'toilet': '🚽', 'shower': '🚿', 'bath': '🛁',
    'soap': '🧼', 'clean': '🧼',
    'trash': '🗑️', 'garbage': '🗑️', 'waste': '🗑️',
    
    # === ACTIVITIES & HOBBIES ===
    'music': '🎵', 'song': '🎵', 'sound': '🔊',
    'guitar': '🎸', 'piano': '🎹', 'drum': '🥁',
    'art': '🎨', 'paint': '🎨', 'draw': '✏️', 'drawing': '✏️',
    'dance': '💃', 'dancing': '💃', 'ballet': '🩰',
    'sing': '🎤', 'singing': '🎤', 'karaoke': '🎤',
    'movie': '🎬', 'film': '🎬', 'cinema': '🎦',
    'video': '📹', 'camera': '📹', 'record': '⏺️',
    'book': '📖', 'novel': '📖', 'story': '📖',
    'game': '🎮', 'gaming': '🎮', 'gamer': '🎮',
    'sport': '⚽', 'sports': '⚽',
    'soccer': '⚽', 'football': '🏈', 'basketball': '🏀',
    'baseball': '⚾', 'tennis': '🎾', 'volleyball': '🏐',
    'golf': '⛳', 'bowling': '🎳', 'pool': '🎱',
    'hockey': '🏒', 'skating': '⛸️',
    'swim': '🏊', 'swimming': '🏊', 'pool': '🏊',
    'run': '🏃', 'running': '🏃', 'jog': '🏃',
    'bike': '🚴', 'biking': '🚴', 'cycling': '🚴',
    'gym': '🏋️', 'workout': '🏋️', 'exercise': '🏋️', 'lift': '🏋️',
    'yoga': '🧘', 'meditate': '🧘', 'meditation': '🧘',
    'camping': '🏕️', 'tent': '⛺', 'camp': '🏕️',
    'fishing': '🎣', 'fish': '🎣',
    'cooking': '👨‍🍳', 'cook': '👨‍🍳', 'chef': '👨‍🍳',
    'garden': '🌻', 'gardening': '🌻',
    
    # === SYMBOLS & MISC ===
    'plus': '➕', 'add': '➕',
    'minus': '➖', 'subtract': '➖',
    'multiply': '✖️', 'times': '✖️',
    'divide': '➗', 'division': '➗',
    'equals': '🟰', 'equal': '🟰',
    'percent': '💯', 'percentage': '💯',
    'question': '❓', 'ask': '❓',
    'exclamation': '❗', 'important': '❗',
    'warning': '⚠️', 'caution': '⚠️', 'alert': '⚠️',
    'forbidden': '🚫', 'banned': '🚫', 'prohibit': '🚫',
    'check': '✅', 'correct': '✅', 'right': '✅',
    'cross': '❌', 'wrong': '❌', 'incorrect': '❌',
    'heart': '❤️', 'hearts': '💕',
    'broken': '💔', 'heartbreak': '💔',
    'peace': '☮️', 'yin': '☯️', 'yang': '☯️',
    'recycle': '♻️', 'eco': '♻️',
    'infinity': '♾️', 'infinite': '♾️', 'forever': '♾️',
    'trademark': '™️', 'copyright': '©️', 'registered': '®️',
    'info': 'ℹ️', 'information': 'ℹ️',
    
    # === COLORS ===
    'red': '🔴', 'crimson': '🔴',
    'orange': '🟠', 'tangerine': '🟠',
    'yellow': '🟡', 'gold': '🟡',
    'green': '🟢', 'lime': '🟢',
    'blue': '🔵', 'navy': '🔵',
    'purple': '🟣', 'violet': '🟣',
    'brown': '🟤', 'tan': '🟤',
    'black': '⚫', 'dark': '⚫',
    'white': '⚪', 'light': '⚪',
    'pink': '🩷', 'rose': '🩷',
    'rainbow': '🌈', 'colorful': '🌈',
    
    # === PEOPLE & RELATIONSHIPS ===
    'person': '🧑', 'people': '👥', 'human': '🧑',
    'man': '👨', 'guy': '👨', 'dude': '👨', 'bro': '👨',
    'woman': '👩', 'girl': '👧', 'lady': '👩',
    'boy': '👦', 'kid': '👦', 'child': '👶', 'baby': '👶',
    'family': '👪', 'parents': '👨‍👩‍👧‍👦',
    'friend': '👫', 'friends': '👭', 'buddy': '👫', 'pal': '👫',
    'couple': '💑', 'love': '❤️', 'romance': '💕',
    'wedding': '💒', 'marriage': '💒', 'bride': '👰', 'groom': '🤵',
    'king': '🤴', 'queen': '👸', 'prince': '🤴', 'princess': '👸',
    'crown': '👑', 'royal': '👑',
    'angel': '👼', 'devil': '😈', 'demon': '👹',
    'mermaid': '🧜', 'fairy': '🧚', 'elf': '🧝',
    'zombie': '🧟', 'mummy': '🧟',
    'ninja': '🥷', 'pirate': '🏴‍☠️',
    
    # === EXPRESSIONS & SLANG ===
    'gg': '🎮', 'wp': '👍', 'ez': '😎',
    'rekt': '💀', 'pwned': '💀', 'owned': '💀',
    'noob': '🆕', 'newbie': '🆕', 'beginner': '🆕',
    'pro': '🏆', 'expert': '🏆', 'master': '🏆',
    'boss': '😎', 'legend': '⭐', 'goat': '🐐',
    'flex': '💪', 'flexing': '💪', 'strong': '💪',
    'weak': '😢', 'soft': '🧸',
    'savage': '😈', 'brutal': '😈', 'ruthless': '😈',
    'cringe': '😬', 'awkward': '😬', 'uncomfortable': '😬',
    'based': '💯', 'valid': '✅', 'legit': '✅',
    'cap': '🧢', 'lie': '🤥', 'fake': '🤥',
    'nocap': '🚫🧢', 'truth': '💯', 'real': '💯',
    'bet': '💯', 'deal': '🤝', 'agree': '🤝',
    'vibe': '✨', 'vibes': '✨', 'energy': '⚡',
    'chaotic': '🌪️', 'chaos': '🌪️', 'crazy': '🤪',
    'chill': '😌', 'relax': '😌', 'calm': '😌',
}

def handle_k9_emojify(comment):
    """
    Handle WEREBOT K9 [message] command to emoji-fy text.
    
    Named after K9moonmoon who's famous for cryptic emoji messages!
    Replaces words in the message with emojis where possible (K9 style!).
    
    Formats supported:
    - WEREBOT K9 your message here
    - WERE-BOT K9 your message here
    
    Args:
        comment: The comment containing K9 command
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Extract message after K9
        match = re.search(r'(?:WEREBOT|WERE-BOT)!?\s+K9\s+(.+)', comment.body, re.IGNORECASE | re.DOTALL)
        
        if not match:
            logger.warning(f"K9 command found but couldn't parse message in comment {comment.id}")
            return False
        
        message = match.group(1).strip()
        
        if not message:
            reply = "Please provide a message to emoji-fy!\n\n"
            reply += "Example: `WEREBOT K9 I love this game`"
            comment.reply(reply)
            time.sleep(2)
            return True
        
        # Emoji-fy the message K9 style - REPLACE words with emojis
        words = message.split()
        emojified_words = []
        
        for word in words:
            # Separate punctuation from word
            # Match: (leading punct)(word)(trailing punct)
            punct_match = re.match(r'^([^\w]*)(\w+)([^\w]*)$', word)
            
            if punct_match:
                leading_punct = punct_match.group(1)
                core_word = punct_match.group(2)
                trailing_punct = punct_match.group(3)
                
                # Check if word has an emoji mapping
                if core_word.lower() in K9_EMOJI_MAP:
                    emoji = K9_EMOJI_MAP[core_word.lower()]
                    # Replace word with emoji, keep punctuation
                    emojified_words.append(f"{leading_punct}{emoji}{trailing_punct}")
                else:
                    # No mapping, keep original
                    emojified_words.append(word)
            else:
                # Weird format, keep as-is
                emojified_words.append(word)
        
        emojified_message = ' '.join(emojified_words)
        
        # Build reply
        reply = f"## 🎨 K9-ified Message:\n\n"
        reply += f"{emojified_message}\n\n"
        reply += f"*K9-ified by Werebot in honor of /u/K9moonmoon* 🐕🌙"
        
        comment.reply(reply)
        logger.info(f"K9 emojify from u/{comment.author}: {len(words)} words processed")
        time.sleep(2)
        return True
        
    except Exception as e:
        logger.error(f"Failed to process K9 command: {e}")
        return False

def handle_easter_egg(comment, reddit):
    """Handle the Frrrrk easter egg"""
    try:
        reddit.subreddit('Fck__Frrrrk').contributor.add(str(comment.author))
        logger.info(f"Added u/{comment.author} to Fck__Frrrrk (easter egg)")
        return True
    except Exception as e:
        logger.error(f"Failed to add contributor to Fck__Frrrrk: {e}")
        return False

def handle_text_easter_egg(comment, trigger, response):
    """
    Handle simple text-based easter eggs (personality responses).
    These are just fun little replies that don't do anything functional.
    """
    try:
        comment.reply(response)
        logger.info(f"Easter egg response to u/{comment.author}: '{trigger}' → '{response}'")
        time.sleep(2)
        return True
    except Exception as e:
        logger.error(f"Failed to post easter egg response: {e}")
        return False

def run_bot(reddit, comments_replied_to, unsubscribed_users, checkpoint, snoozed_threads, vote_data, nickname_mapper=None):
    """
    Main bot logic - monitors comments and handles various commands
    
    Args:
        snoozed_threads: Dict of thread_id -> list of snoozed usernames
        vote_data: Dict of thread_id -> {voter: target}
        nickname_mapper: Optional NicknameMapper instance for resolving nicknames
    """
    bot_username = reddit.user.me().name
    processed_count = 0
    
    try:
        # Fetch recent comments
        comments = list(reddit.subreddit(SUBREDDITS).comments(limit=COMMENT_LIMIT))
        logger.debug(f"Fetched {len(comments)} recent comments")
        
        for comment in comments:
            # Skip if already processed
            if comment.id in comments_replied_to:
                continue
            
            # Skip own comments
            if comment.author and comment.author.name == bot_username:
                continue
            
            comment_body_upper = comment.body.upper()
            
            # Handle WEREBOT K9 (emojify) - must check before general commands
            if ("WEREBOT K9" in comment_body_upper or "WERE-BOT K9" in comment_body_upper or
                "WEREBOT! K9" in comment_body_upper or "WERE-BOT! K9" in comment_body_upper):
                logger.info(f"Processing K9 emojify from u/{comment.author}")
                
                if handle_k9_emojify(comment):
                    comments_replied_to.append(comment.id)
                    save_comment_id(comment.id)
                    processed_count += 1
            
            # Handle WEREBOT VOTE [username]
            elif ("WEREBOT VOTE" in comment_body_upper or "WERE-BOT VOTE" in comment_body_upper or
                  "WEREBOT! VOTE" in comment_body_upper or "WERE-BOT! VOTE" in comment_body_upper):
                logger.info(f"Processing vote declaration from u/{comment.author}")
                
                result = handle_vote_declaration(comment, vote_data, nickname_mapper)
                if result is not None:
                    vote_data = result
                    comments_replied_to.append(comment.id)
                    save_comment_id(comment.id)
                    processed_count += 1
            
            # Handle WEREBOT TALLY
            elif ("WEREBOT TALLY" in comment_body_upper or "WERE-BOT TALLY" in comment_body_upper or
                  "WEREBOT! TALLY" in comment_body_upper or "WERE-BOT! TALLY" in comment_body_upper):
                logger.info(f"Processing vote tally request from u/{comment.author}")
                
                if handle_vote_tally(comment, vote_data):
                    comments_replied_to.append(comment.id)
                    save_comment_id(comment.id)
                    processed_count += 1
            
            # Handle WEREBOT RANDOM (must check before regular WEREBOT)
            elif ("WEREBOT RANDOM" in comment_body_upper or "WERE-BOT RANDOM" in comment_body_upper or 
                "WEREBOT! RANDOM" in comment_body_upper or "WERE-BOT! RANDOM" in comment_body_upper):
                logger.info(f"Processing random choice from u/{comment.author}")
                
                if handle_random(comment):
                    comments_replied_to.append(comment.id)
                    save_comment_id(comment.id)
                    processed_count += 1
            
            # Handle WEREBOT SNOOZE (must check before regular WEREBOT)
            elif ("WEREBOT SNOOZE" in comment_body_upper or "WERE-BOT SNOOZE" in comment_body_upper):
                logger.info(f"Processing snooze from u/{comment.author} for thread {comment.submission.id}")
                
                result = handle_snooze(comment, snoozed_threads)
                if result is not None:
                    snoozed_threads = result
                    comments_replied_to.append(comment.id)
                    save_comment_id(comment.id)
                    processed_count += 1
            
            # Handle WEREBOT tagging
            elif ("WEREBOT" in comment_body_upper or "WERE-BOT" in comment_body_upper):
                # Resolve nicknames if mapper is available
                if nickname_mapper:
                    try:
                        comment_body_resolved = nickname_mapper.resolve_mentions(comment.body)
                        if comment_body_resolved != comment.body:
                            logger.info(f"Resolved nicknames in comment {comment.id}")
                            logger.debug(f"Original: {comment.body[:100]}...")
                            logger.debug(f"Resolved: {comment_body_resolved[:100]}...")
                    except Exception as e:
                        logger.warning(f"Failed to resolve nicknames: {e}")
                        comment_body_resolved = comment.body
                else:
                    comment_body_resolved = comment.body
                
                # Extract usernames (from resolved text if nicknames were used)
                usernames = extract_usernames(comment_body_resolved)
                
                # Filter out unsubscribed users
                subscribed_usernames = filter_subscribed_users(usernames, unsubscribed_users)
                
                # Filter out users who have snoozed this thread
                submission_id = comment.submission.id
                active_usernames = filter_snoozed_users(subscribed_usernames, submission_id, snoozed_threads)
                
                # Only tag if there are 4 or more users (>3 as per original logic)
                if len(active_usernames) > 3:
                    logger.info(f"Processing tag request from u/{comment.author} with {len(active_usernames)} users")
                    
                    if send_tags(comment, active_usernames, checkpoint):
                        comments_replied_to.append(comment.id)
                        save_comment_id(comment.id)
                        processed_count += 1
                    else:
                        logger.warning(f"Failed to send tags for comment {comment.id}")
                else:
                    logger.debug(f"Skipping tag request with only {len(active_usernames)} active users")
            
            # Handle unsubscribe
            if "WEREBOT!UNSUBSCRIBE" in comment_body_upper or "WERE-BOT!UNSUBSCRIBE" in comment_body_upper:
                logger.info(f"Processing unsubscribe from u/{comment.author}")
                
                if handle_unsubscribe(comment, unsubscribed_users, checkpoint):
                    comments_replied_to.append(comment.id)
                    save_comment_id(comment.id)
                    processed_count += 1
            
            # Handle subscribe
            elif "WEREBOT!SUBSCRIBE" in comment_body_upper or "WERE-BOT!SUBSCRIBE" in comment_body_upper:
                logger.info(f"Processing subscribe from u/{comment.author}")
                
                if handle_subscribe(comment, unsubscribed_users, checkpoint):
                    comments_replied_to.append(comment.id)
                    save_comment_id(comment.id)
                    processed_count += 1
            
            # Handle Frrrrk easter egg (functional - adds to subreddit)
            elif "I HATE FRRRRK" in comment_body_upper:
                logger.info(f"Processing Frrrrk easter egg for u/{comment.author}")
                
                if handle_easter_egg(comment, reddit):
                    comments_replied_to.append(comment.id)
                    save_comment_id(comment.id)
                    processed_count += 1
            
            # Handle text-based easter eggs (just fun personality responses)
            elif "FUCK WEREBOT" in comment_body_upper or "FUCK WERE-BOT" in comment_body_upper:
                logger.info(f"Processing 'rude' easter egg for u/{comment.author}")
                
                if handle_text_easter_egg(comment, "fuck werebot", "wow rude 😔"):
                    comments_replied_to.append(comment.id)
                    save_comment_id(comment.id)
                    processed_count += 1
            
            elif "THANKS WEREBOT" in comment_body_upper or "THANKS WERE-BOT" in comment_body_upper or \
                 "THANK YOU WEREBOT" in comment_body_upper or "THANK YOU WERE-BOT" in comment_body_upper:
                logger.info(f"Processing 'thanks' easter egg for u/{comment.author}")
                
                if handle_text_easter_egg(comment, "thanks", "😊"):
                    comments_replied_to.append(comment.id)
                    save_comment_id(comment.id)
                    processed_count += 1
            
            elif "GOOD BOT" in comment_body_upper:
                # Only respond if it seems directed at Werebot
                if "WEREBOT" in comment_body_upper or "WERE-BOT" in comment_body_upper:
                    logger.info(f"Processing 'good bot' easter egg for u/{comment.author}")
                    
                    if handle_text_easter_egg(comment, "good bot", "😊"):
                        comments_replied_to.append(comment.id)
                        save_comment_id(comment.id)
                        processed_count += 1
        
        if processed_count > 0:
            logger.info(f"Processed {processed_count} new comments this cycle")
            save_checkpoint(checkpoint)
        else:
            logger.debug("No new comments to process this cycle")
        
        return checkpoint, snoozed_threads, vote_data
        
    except Exception as e:
        logger.error(f"Error in run_bot: {e}", exc_info=True)
        raise

def main():
    """Main execution loop with error recovery"""
    logger.info("=" * 60)
    logger.info("Werebot starting up...")
    logger.info("=" * 60)
    
    # Load checkpoint
    checkpoint = load_checkpoint()
    if checkpoint['last_run']:
        logger.info(f"Last successful run: {checkpoint['last_run']}")
        logger.info(f"Stats - Tags: {checkpoint['total_tags']}, Unsubs: {checkpoint['total_unsubscribes']}, Subs: {checkpoint['total_subscribes']}")
    
    # Initialize
    try:
        reddit = bot_login()
        comments_replied_to = get_saved_comments()
        unsubscribed_users = get_unsubscribed_users()
        snoozed_threads = get_snoozed_threads()
        vote_data = get_vote_declarations()
        
        # Initialize nickname mapper if configured
        nickname_mapper = None
        if NICKNAME_MAPPER_AVAILABLE and NICKNAME_SPREADSHEET_URL:
            try:
                logger.info("Initializing nickname mapper...")
                nickname_mapper = NicknameMapper(
                    spreadsheet_url=NICKNAME_SPREADSHEET_URL,
                    credentials_file=NICKNAME_CREDENTIALS,
                    cache_duration=300  # Refresh every 5 minutes
                )
                if nickname_mapper.load_nicknames():
                    nickname_count = len(nickname_mapper.get_all_nicknames())
                    logger.info(f"Nickname mapper enabled with {nickname_count} nicknames")
                else:
                    logger.warning("Failed to load nicknames, mapper disabled")
                    nickname_mapper = None
            except Exception as e:
                logger.warning(f"Failed to initialize nickname mapper: {e}")
                logger.info("Continuing without nickname mapping")
                nickname_mapper = None
        else:
            if not NICKNAME_MAPPER_AVAILABLE:
                logger.info("Nickname mapper not available (nickname_mapper.py not found)")
            else:
                logger.info("Nickname mapping disabled (no spreadsheet URL configured)")
        
    except Exception as e:
        logger.critical(f"Failed to initialize: {e}")
        return
    
    logger.info(f"Bot initialized successfully. Monitoring r/{SUBREDDITS}")
    logger.info(f"Currently tracking {len(comments_replied_to)} processed comments")
    logger.info(f"Currently {len(unsubscribed_users)} unsubscribed users")
    logger.info(f"Currently {len(snoozed_threads)} threads with snoozed users")
    logger.info(f"Currently {len(vote_data)} threads with declared votes")
    logger.info("Starting main loop...")
    
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    while True:
        try:
            checkpoint, snoozed_threads, vote_data = run_bot(reddit, comments_replied_to, unsubscribed_users, checkpoint, snoozed_threads, vote_data, nickname_mapper)
            consecutive_errors = 0  # Reset error counter on success
            time.sleep(10)
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal. Saving checkpoint and exiting...")
            save_checkpoint(checkpoint)
            break
            
        except Exception as e:
            consecutive_errors += 1
            logger.error(f"Error in main loop (attempt {consecutive_errors}/{max_consecutive_errors}): {e}", exc_info=True)
            
            if consecutive_errors >= max_consecutive_errors:
                logger.critical(f"Too many consecutive errors ({max_consecutive_errors}). Exiting.")
                save_checkpoint(checkpoint)
                break
            
            # Exponential backoff
            wait_time = min(30 * (2 ** (consecutive_errors - 1)), 300)
            logger.info(f"Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)

if __name__ == "__main__":
    main()
