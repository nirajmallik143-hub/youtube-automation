"""YouTube API Authentication Module

Handles OAuth 2.0 authentication with YouTube Data API
"""

import os
import json
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
          'https://www.googleapis.com/auth/youtube',
          'https://www.googleapis.com/auth/youtube.force-ssl']

class YouTubeAuth:
    """Handle YouTube API authentication"""
    
    def __init__(self, config_file='config/config.json', credentials_file='config/credentials.json'):
        """Initialize authentication
        
        Args:
            config_file: Path to config file with API credentials
            credentials_file: Path to OAuth token storage
        """
        self.config_file = config_file
        self.credentials_file = credentials_file
        self.credentials = None
        
    def authenticate(self):
        """Authenticate with YouTube API
        
        Returns:
            Credentials object for API access
        """
        try:
            # Try to load existing credentials
            if os.path.exists(self.credentials_file):
                logger.info(f"Loading existing credentials from {self.credentials_file}")
                self.credentials = self._load_credentials()
                
                # Refresh if expired
                if self.credentials and self.credentials.expired:
                    logger.info("Credentials expired, refreshing...")
                    self.credentials.refresh(Request())
                    self._save_credentials()
                    
            else:
                # Perform new authentication
                logger.info("Performing new OAuth authentication...")
                self._perform_oauth_flow()
                
            return self.credentials
            
        except RefreshError as e:
            logger.error(f"Authentication failed: {e}")
            logger.info("Please re-authenticate by deleting credentials file and running again")
            raise
            
    def _perform_oauth_flow(self):
        """Perform OAuth 2.0 authentication flow"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
            
        with open(self.config_file) as f:
            config = json.load(f)
            
        flow = InstalledAppFlow.from_client_config(
            config['youtube'],
            SCOPES
        )
        
        self.credentials = flow.run_local_server(port=0)
        self._save_credentials()
        logger.info("OAuth authentication successful")
        
    def _load_credentials(self):
        """Load credentials from file"""
        with open(self.credentials_file, 'rb') as f:
            credentials = pickle.load(f)
        return credentials
        
    def _save_credentials(self):
        """Save credentials to file"""
        with open(self.credentials_file, 'wb') as f:
            pickle.dump(self.credentials, f)
        logger.info(f"Credentials saved to {self.credentials_file}")
        
    def refresh_credentials(self):
        """Manually refresh credentials"""
        if self.credentials:
            self.credentials.refresh(Request())
            self._save_credentials()
            logger.info("Credentials refreshed successfully")


if __name__ == "__main__":
    # Test authentication
    auth = YouTubeAuth()
    credentials = auth.authenticate()
    print(f"✅ Authentication successful!")
    print(f"Token: {credentials.token[:20]}...")
