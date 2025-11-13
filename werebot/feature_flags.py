"""
Feature Flags Module for Werebot

This module allows features to be toggled on/off via Discord bot commands.
Features are stored in a JSON file that's shared between the Discord bot and Werebot.
"""

import json
import os
from typing import Dict

# Feature flags file path (shared with Discord bot)
FEATURES_FILE = os.environ.get('WEREBOT_FEATURES_FILE', 'feature_flags.json')

# Default feature states
DEFAULT_FEATURES = {
    'vote_system': True,
    'random': True,
    'k9_mode': True,
    'easter_eggs': True,
    'tagging': True
}


class FeatureFlags:
    """Manage feature flags for Werebot"""
    
    def __init__(self, features_file=FEATURES_FILE):
        self.features_file = features_file
        self._cached_features = None
        self._last_load_time = 0
        self.cache_duration = 10  # Reload every 10 seconds
    
    def _load_features(self) -> Dict[str, bool]:
        """Load features from file with caching"""
        import time
        
        current_time = time.time()
        
        # Use cache if still valid
        if self._cached_features and (current_time - self._last_load_time) < self.cache_duration:
            return self._cached_features
        
        # Load from file
        if not os.path.exists(self.features_file):
            self._cached_features = DEFAULT_FEATURES.copy()
            self._last_load_time = current_time
            return self._cached_features
        
        try:
            with open(self.features_file, 'r') as f:
                features = json.load(f)
                # Merge with defaults to ensure all features exist
                self._cached_features = {**DEFAULT_FEATURES, **features}
                self._last_load_time = current_time
                return self._cached_features
        except (json.JSONDecodeError, IOError):
            self._cached_features = DEFAULT_FEATURES.copy()
            self._last_load_time = current_time
            return self._cached_features
    
    def is_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled"""
        features = self._load_features()
        return features.get(feature_name, True)  # Default to True if not found
    
    def get_all(self) -> Dict[str, bool]:
        """Get all feature flags"""
        return self._load_features()


# Global instance
_feature_flags = FeatureFlags()


def is_enabled(feature_name: str) -> bool:
    """
    Check if a feature is enabled.
    
    Args:
        feature_name: Name of the feature to check
    
    Returns:
        bool: True if enabled, False if disabled
    
    Example:
        if is_enabled('vote_system'):
            handle_vote_declaration(comment, vote_data)
    """
    return _feature_flags.is_enabled(feature_name)


def get_all_features() -> Dict[str, bool]:
    """
    Get all feature flags.
    
    Returns:
        Dict mapping feature names to their enabled state
    """
    return _feature_flags.get_all()


# Convenience functions for checking specific features
def vote_system_enabled() -> bool:
    """Check if vote system (VOTE, UNVOTE, TALLY) is enabled"""
    return is_enabled('vote_system')


def random_enabled() -> bool:
    """Check if RANDOM command is enabled"""
    return is_enabled('random')


def k9_mode_enabled() -> bool:
    """Check if K9 emoji mode is enabled"""
    return is_enabled('k9_mode')


def easter_eggs_enabled() -> bool:
    """Check if easter eggs are enabled"""
    return is_enabled('easter_eggs')


def tagging_enabled() -> bool:
    """Check if user tagging is enabled"""
    return is_enabled('tagging')
