#!/usr/bin/env python3

import requests
import json
import time
from datetime import datetime, timedelta

class TokenManager:
    def __init__(self):
        self.config_file = 'snapchat_tokens.json'
        self.config = self.load_config()

    def load_config(self):
        """Load current token configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load config: {e}")
            return None

    def save_config(self, config):
        """Save updated token configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save config: {e}")
            return False

    def is_token_expired(self):
        """Check if current token is expired or will expire soon"""
        if not self.config or 'expires_at' not in self.config:
            return True

        try:
            expires_at = datetime.fromisoformat(self.config['expires_at'])
            # Consider token expired if it expires within 5 minutes
            buffer_time = datetime.now() + timedelta(minutes=5)
            return expires_at <= buffer_time
        except:
            return True

    def refresh_token(self):
        """Refresh the access token using refresh token"""
        if not self.config or 'refresh_token' not in self.config:
            print("[ERROR] No refresh token available")
            return False

        # Get credentials from saved config
        if 'client_id' not in self.config or 'client_secret' not in self.config:
            print("[ERROR] No client credentials found in config")
            return False

        print("[INFO] Refreshing access token...")

        client_id = self.config['client_id']
        client_secret = self.config['client_secret']

        token_url = "https://accounts.snapchat.com/login/oauth2/access_token"
        token_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": self.config['refresh_token'],
            "grant_type": "refresh_token"
        }

        try:
            response = requests.post(token_url, data=token_data)

            if response.status_code == 200:
                token_info = response.json()

                # Update config with new tokens
                self.config['access_token'] = token_info.get('access_token')
                if 'refresh_token' in token_info:
                    self.config['refresh_token'] = token_info.get('refresh_token')

                # Calculate expiration time
                expires_in = token_info.get('expires_in', 3600)
                expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # 5 min buffer
                self.config['expires_at'] = expires_at.isoformat()

                # Save updated config
                if self.save_config(self.config):
                    print(f"[SUCCESS] Token refreshed! Expires at: {expires_at}")
                    return True
                else:
                    print("[ERROR] Failed to save refreshed token")
                    return False
            else:
                print(f"[ERROR] Token refresh failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"[ERROR] Token refresh request failed: {e}")
            return False

    def get_valid_token(self):
        """Get a valid access token, refreshing if necessary"""
        if self.is_token_expired():
            print("[INFO] Token expired or expiring soon, refreshing...")
            if not self.refresh_token():
                print("[ERROR] Failed to refresh token")
                return None
            # Reload config after refresh
            self.config = self.load_config()

        return self.config.get('access_token') if self.config else None

    def get_headers(self):
        """Get authorization headers with valid token"""
        token = self.get_valid_token()
        if not token:
            return None

        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

def test_token_manager():
    """Test the token manager"""
    print("=== TESTING TOKEN MANAGER ===")

    tm = TokenManager()

    # Check if token is expired
    expired = tm.is_token_expired()
    print(f"Token expired: {expired}")

    # Get valid token
    token = tm.get_valid_token()
    if token:
        print("[SUCCESS] Got valid token")

        # Test API call
        headers = tm.get_headers()
        try:
            response = requests.get('https://adsapi.snapchat.com/v1/me', headers=headers)
            if response.status_code == 200:
                print("[SUCCESS] API test successful!")
                me_data = response.json()
                print(f"User: {me_data}")
            else:
                print(f"[ERROR] API test failed: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] API test failed: {e}")
    else:
        print("[ERROR] Failed to get valid token")

if __name__ == "__main__":
    test_token_manager()