import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import praw
import time
import logging
import json
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hwwbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Checkpoint file for resuming
CHECKPOINT_FILE = 'hwwbot_checkpoint.json'

def load_checkpoint():
    """Load checkpoint data if it exists"""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load checkpoint: {e}")
    return {'last_run': None, 'run_count': 0}

def save_checkpoint(data):
    """Save checkpoint data"""
    try:
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.debug("Checkpoint saved")
    except Exception as e:
        logger.error(f"Could not save checkpoint: {e}")

def bot_login():
    """
    Initialize Reddit connection with proper OAuth2 authentication.
    Uses password flow for script-type application.
    """
    try:
        logger.info("Attempting to log in to Reddit...")
        reddit = praw.Reddit(
            client_id="eDn-z1FX_U4P7Q",
            client_secret="2eFqcAKGpdWSR8ecOmeD0rDCiN0",
            username="HWWBot",
            password="yrEtx&l_g0/4ldf(sh",
            user_agent="HWWBot:3.0 (by /u/Penultima)"
        )
        
        # Verify authentication
        user = reddit.user.me()
        logger.info(f"Successfully logged in as: {user.name}")
        return reddit
        
    except Exception as e:
        logger.error(f"Failed to log in to Reddit: {e}")
        raise

def init_google_sheets():
    """Initialize Google Sheets connection using service account"""
    try:
        logger.info("Connecting to Google Sheets...")
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Use the credentials file from project
        creds_path = '/mnt/project/creds2.json' if os.path.exists('/mnt/project/creds2.json') else 'creds2.json'
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
        client = gspread.authorize(creds)
        logger.info("Successfully connected to Google Sheets")
        return client
        
    except Exception as e:
        logger.error(f"Failed to connect to Google Sheets: {e}")
        raise

def update_automod_config(reddit, subreddit_name, automod_config):
    """
    Update AutoModerator configuration for a subreddit
    
    Args:
        reddit: PRAW Reddit instance
        subreddit_name: Name of the subreddit
        automod_config: AutoModerator configuration string
    """
    try:
        logger.info(f"Updating AutoMod config for r/{subreddit_name}")
        page = reddit.subreddit(subreddit_name).wiki['config/AutoModerator']
        page.edit(content=automod_config)
        logger.info(f"Successfully updated r/{subreddit_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to update r/{subreddit_name}: {e}")
        return False

def run_bot(reddit, client, checkpoint):
    """
    Main bot logic - checks spreadsheet and updates subreddit AutoMod configs
    """
    try:
        # Get the control sheet
        logger.info("Checking spreadsheet for updates...")
        sheet_two = client.open('Hidden Werewolves - Game Sign Ups (Responses)').worksheet("HWWbot")
        status = sheet_two.cell(2, 5).value
        
        if status != "Updating...":
            logger.info(f"Status is '{status}', skipping this cycle")
            return checkpoint
        
        logger.info("Status is 'Updating...', proceeding with update")
        
        # Get the backend sheet with player lists
        sheet_one = client.open('Hidden Werewolves - Game Sign Ups (Responses)').worksheet("Backend")
        
        # Fetch all necessary data
        logger.info("Fetching configuration from spreadsheet...")
        status1 = sheet_one.cell(2, 1).value
        status2 = sheet_one.cell(2, 2).value
        status3 = sheet_one.cell(2, 3).value
        list1 = sheet_one.cell(1, 1).value
        list2 = sheet_one.cell(1, 2).value
        list3 = sheet_one.cell(1, 3).value
        new_users = sheet_one.cell(1, 4).value
        
        # Subreddit names
        subreddits = [
            ("HiddenWerewolves", status1, list1),
            ("HiddenWerewolvesA", status2, list2),
            ("HiddenWerewolvesB", status3, list3)
        ]
        
        # Common AutoMod components
        flair = '"Meta"'
        lynch_message = """type: comment
body+title (includes, regex): ['lynch']
moderators_exempt: false
comment: |
    As a community, we're making a conscious shift away from using the word 'lynch' in the light-hearted context of our games. The word has historically been used to describe the murders of marginalized groups, and as such, has some loaded meaning. You can view [our community discussion thread on the topic](https://redd.it/hdumj4) for more insight into why we're trying to discourage the casual use of the word 'lynch' going forward. In short, we don't want to make a game out of historical trauma.

    We understand that this has been in our vernacular for a while, it'll take time for this change to feel natural, and mistakes will happen. We encourage you to keep working at it and look for alternative ways to get your point across!

---

"""
        
        on_comment = '''comment: "This comment was removed because only players may comment in the game ([Rule 6](https://www.reddit.com/r/hogwartswerewolves/wiki/rules#wiki_6._non-players_may_not_post_in_the_main_game_subs.)). If a game is in-progress and you believe your comment was removed in error, please message the game hosts directly.  If there is no game in-progress, please message the mods via modmail."'''
        
        off_comment = '''comment: "This comment was removed as you currently do not meet the account requirements to participate in /r/HiddenWerewolves. Please see [this thread](https://redd.it/8t428a) for details. **If a game is in-progress and you believe your comment was removed in error, please message the game hosts directly.**  If there is no game in-progress, please message the mods via modmail."'''
        
        # Update each subreddit
        results = []
        logger.info(f"Updating {len(subreddits)} subreddits...")
        for sub_name, status, player_list in subreddits:
            logger.info(f"Processing r/{sub_name} (Status: {status})")
            
            if status == "ON":
                automod = f"""{lynch_message}# HWWBOT IS ON
type: any
is_edited: false
author:
    ~name: {player_list}
parent_submission:
    ~flair_css_class: [{flair}]
action: remove
{on_comment}"""
            else:
                automod = f"""{lynch_message}# HWWBOT IS OFF
type: any
is_edited: false
author:
    account_age: < 1 month
    ~name: {new_users}
parent_submission:
    ~flair_css_class: [{flair}]
action: remove
{off_comment}"""
            
            # Update the subreddit
            success = update_automod_config(reddit, sub_name, automod)
            results.append((sub_name, success))
            
            # Small delay between updates
            time.sleep(1)
        
        # Update checkpoint
        checkpoint['last_run'] = datetime.now().isoformat()
        checkpoint['run_count'] += 1
        save_checkpoint(checkpoint)
        
        # Update timestamp in spreadsheet
        now = datetime.now() + timedelta(seconds=1300)
        time_now = "Last updated: " + now.strftime("%d/%m/%Y %H:%M:%S") + " EDT"
        logger.info(f"Update complete: {time_now}")
        
        sheet_two.update_cell(3, 5, time_now)
        sheet_two.update_cell(2, 5, "Done")
        
        # Log results
        successful = sum(1 for _, success in results if success)
        logger.info(f"Updated {successful}/{len(results)} subreddits successfully")
        
        return checkpoint
        
    except Exception as e:
        logger.error(f"Error in run_bot: {e}", exc_info=True)
        raise

def main():
    """Main execution loop with error recovery"""
    logger.info("=" * 60)
    logger.info("HWWBot starting up...")
    logger.info("=" * 60)
    
    # Load checkpoint
    checkpoint = load_checkpoint()
    if checkpoint['last_run']:
        logger.info(f"Last successful run: {checkpoint['last_run']}")
        logger.info(f"Total runs: {checkpoint['run_count']}")
    
    # Initialize connections
    try:
        reddit = bot_login()
        client = init_google_sheets()
    except Exception as e:
        logger.critical(f"Failed to initialize connections: {e}")
        return
    
    logger.info("Bot initialized successfully. Starting main loop...")
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    while True:
        try:
            checkpoint = run_bot(reddit, client, checkpoint)
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
