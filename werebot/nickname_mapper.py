"""
Nickname Lookup System for Were-Bot
Allows users to use shorthand nicknames that map to Reddit usernames
"""

import gspread
from google.oauth2.service_account import Credentials
import logging
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class NicknameMapper:
    """
    Manages nickname-to-username mappings from Google Sheets.
    Caches results to minimize API calls.
    """
    
    def __init__(self, spreadsheet_url, credentials_file, cache_duration=300):
        """
        Initialize nickname mapper.
        
        Args:
            spreadsheet_url: URL of the Google Sheet
            credentials_file: Path to Google service account credentials JSON
            cache_duration: How long to cache nicknames (seconds, default 5 minutes)
        """
        self.spreadsheet_url = spreadsheet_url
        self.credentials_file = credentials_file
        self.cache_duration = cache_duration
        
        self.nickname_map = {}  # nickname (lowercase) -> username
        self.last_update = None
        self.client = None
        
        self._init_google_client()
    
    def _init_google_client(self):
        """Initialize Google Sheets client"""
        try:
            logger.info("Initializing Google Sheets client for nickname lookup...")
            
            scopes = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=scopes
            )
            
            self.client = gspread.authorize(creds)
            logger.info("Google Sheets client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {e}")
            self.client = None
    
    def _should_refresh_cache(self):
        """Check if cache should be refreshed"""
        if not self.last_update:
            return True
        
        age = datetime.now() - self.last_update
        return age.total_seconds() > self.cache_duration
    
    def load_nicknames(self):
        """
        Load nicknames from Google Sheet.
        
        Expected sheet format:
        Column A: Nickname (e.g., "Puff", "K9")
        Column B: Reddit Username (e.g., "Team-Hufflepuff", "K9moonmoon")
        
        First row is headers (will be skipped).
        """
        if not self.client:
            logger.warning("Google Sheets client not initialized, cannot load nicknames")
            return False
        
        try:
            logger.info("Loading nicknames from Google Sheet...")
            
            # Open spreadsheet
            sheet = self.client.open_by_url(self.spreadsheet_url)
            worksheet = sheet.get_worksheet(0)  # First worksheet
            
            # Get all values
            all_values = worksheet.get_all_values()
            
            if not all_values:
                logger.warning("Nickname sheet is empty")
                return False
            
            # Skip header row
            data_rows = all_values[1:]
            
            # Build nickname map
            new_map = {}
            for row in data_rows:
                if len(row) >= 2:
                    nickname = row[0].strip()
                    username = row[1].strip()
                    
                    if nickname and username:
                        # Store nickname in lowercase for case-insensitive lookup
                        nickname_lower = nickname.lower()
                        
                        # Remove /u/ prefix if present in sheet
                        if username.startswith('/u/'):
                            username = username[3:]
                        elif username.startswith('u/'):
                            username = username[2:]
                        
                        new_map[nickname_lower] = username
                        logger.debug(f"Loaded nickname: {nickname} -> {username}")
            
            self.nickname_map = new_map
            self.last_update = datetime.now()
            
            logger.info(f"Successfully loaded {len(self.nickname_map)} nicknames")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load nicknames: {e}")
            return False
    
    def get_username(self, nickname):
        """
        Get Reddit username for a nickname.
        
        Args:
            nickname: The nickname to look up (case-insensitive)
        
        Returns:
            Reddit username if found, None otherwise
        """
        # Refresh cache if needed
        if self._should_refresh_cache():
            self.load_nicknames()
        
        return self.nickname_map.get(nickname.lower())
    
    def resolve_mentions(self, text):
        """
        Resolve all nickname mentions in text to Reddit usernames.
        
        Looks for patterns like:
        - Puff
        - @Puff
        - #Puff
        
        And converts them to /u/Team-Hufflepuff
        
        Args:
            text: Text containing potential nicknames
        
        Returns:
            Text with nicknames replaced by /u/username mentions
        """
        if not self.nickname_map:
            return text
        
        # Refresh cache if needed
        if self._should_refresh_cache():
            self.load_nicknames()
        
        import re
        
        # Find all potential nickname mentions
        # Matches: word boundaries followed by alphanumeric (with optional @ or # prefix)
        pattern = r'\b[@#]?([A-Za-z0-9_-]+)\b'
        
        def replace_nickname(match):
            potential_nickname = match.group(1)
            username = self.get_username(potential_nickname)
            
            if username:
                logger.debug(f"Resolved nickname '{potential_nickname}' to '/u/{username}'")
                return f"/u/{username}"
            else:
                # Not a nickname, return original
                return match.group(0)
        
        resolved_text = re.sub(pattern, replace_nickname, text)
        return resolved_text
    
    def get_all_nicknames(self):
        """
        Get all available nicknames.
        
        Returns:
            Dictionary of nickname -> username mappings
        """
        # Refresh cache if needed
        if self._should_refresh_cache():
            self.load_nicknames()
        
        return self.nickname_map.copy()


# Example usage in Were-Bot:
"""
# At the top of werebot_updated.py
from nickname_mapper import NicknameMapper

# Initialize nickname mapper (optional - only if spreadsheet is configured)
NICKNAME_SPREADSHEET_URL = os.environ.get('NICKNAME_SPREADSHEET_URL', '')
if NICKNAME_SPREADSHEET_URL:
    nickname_mapper = NicknameMapper(
        spreadsheet_url=NICKNAME_SPREADSHEET_URL,
        credentials_file='creds2.json',
        cache_duration=300  # Refresh every 5 minutes
    )
    nickname_mapper.load_nicknames()
    logger.info("Nickname mapper enabled")
else:
    nickname_mapper = None
    logger.info("Nickname mapper disabled (no spreadsheet URL provided)")

# In the tagging logic, before extracting usernames:
if nickname_mapper:
    # Resolve nicknames to usernames
    comment_body_resolved = nickname_mapper.resolve_mentions(comment.body)
    logger.debug(f"Original: {comment.body}")
    logger.debug(f"Resolved: {comment_body_resolved}")
    
    # Extract usernames from resolved text
    usernames = extract_usernames(comment_body_resolved)
else:
    # No nickname mapping, use original text
    usernames = extract_usernames(comment.body)
"""
