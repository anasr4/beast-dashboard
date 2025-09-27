#!/usr/bin/env python3

import requests
import json
import time
import webbrowser
import urllib.parse
from datetime import datetime, timedelta

class TokenManager:
    def __init__(self):
        self.config_file = 'snapchat_tokens.json'

        # Default credentials - set before loading config
        self.default_client_id = "26267fa4-831c-47fb-97b4-afca39be5877"
        self.default_client_secret = "84ec597b44ef3968088c"
        self.default_redirect_uri = "https://localhost:8000/auth/callback"

        self.config = self.load_config()

    def load_config(self):
        """Load current token configuration"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Ensure all required fields exist
                if 'client_id' not in config:
                    config['client_id'] = self.default_client_id
                if 'client_secret' not in config:
                    config['client_secret'] = self.default_client_secret
                if 'redirect_uri' not in config:
                    config['redirect_uri'] = self.default_redirect_uri
                return config
        except Exception as e:
            print(f"[ERROR] Failed to load config: {e}")
            # Return default config
            return {
                'client_id': self.default_client_id,
                'client_secret': self.default_client_secret,
                'redirect_uri': self.default_redirect_uri,
                'ad_account_id': None,
                'access_token': None,
                'refresh_token': None,
                'expires_at': None
            }

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

    def generate_auth_url(self):
        """Generate authorization URL for OAuth flow"""
        client_id = self.config.get('client_id', self.default_client_id)
        redirect_uri = self.config.get('redirect_uri', self.default_redirect_uri)

        auth_url = "https://accounts.snapchat.com/login/oauth2/authorize"
        scope = "snapchat-marketing-api"

        params = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'state': 'authentication'
        }

        return f"{auth_url}?{urllib.parse.urlencode(params)}"

    def authorize_with_code(self, authorization_code):
        """Exchange authorization code for access token"""
        client_id = self.config.get('client_id', self.default_client_id)
        client_secret = self.config.get('client_secret', self.default_client_secret)
        redirect_uri = self.config.get('redirect_uri', self.default_redirect_uri)

        token_url = "https://accounts.snapchat.com/login/oauth2/access_token"
        token_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }

        try:
            response = requests.post(token_url, data=token_data)

            if response.status_code == 200:
                token_info = response.json()

                # Update config with new tokens (clean them)
                access_token = token_info.get('access_token', '')
                refresh_token = token_info.get('refresh_token', '')

                # Clean tokens by removing whitespace and newlines
                self.config['access_token'] = ''.join(access_token.split()) if access_token else None
                self.config['refresh_token'] = ''.join(refresh_token.split()) if refresh_token else None

                # Calculate expiration time
                expires_in = token_info.get('expires_in', 3600)
                expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # 5 min buffer
                self.config['expires_at'] = expires_at.isoformat()

                # Get and store ad account info
                if self.fetch_ad_account_info():
                    # Save updated config
                    if self.save_config(self.config):
                        print(f"[SUCCESS] Authorization complete! Token expires at: {expires_at}")
                        return True
                    else:
                        print("[ERROR] Failed to save authorization data")
                        return False
                else:
                    print("[ERROR] Failed to fetch ad account info")
                    return False
            else:
                print(f"[ERROR] Token exchange failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"[ERROR] Authorization failed: {e}")
            return False

    def fetch_ad_account_info(self):
        """Fetch and store ad account information"""
        if not self.config.get('access_token'):
            print("[ERROR] No access token available")
            return False

        headers = {
            'Authorization': f'Bearer {self.config["access_token"]}',
            'Content-Type': 'application/json'
        }

        try:
            # Get user info first
            me_response = requests.get('https://adsapi.snapchat.com/v1/me', headers=headers)
            if me_response.status_code != 200:
                print(f"[ERROR] Failed to get user info: {me_response.text}")
                return False

            me_data = me_response.json()
            org_id = me_data['me']['organization_id']

            # Get ad accounts
            accounts_response = requests.get(
                f'https://adsapi.snapchat.com/v1/organizations/{org_id}/adaccounts',
                headers=headers
            )
            if accounts_response.status_code != 200:
                print(f"[ERROR] Failed to get ad accounts: {accounts_response.text}")
                return False

            accounts = accounts_response.json().get('adaccounts', [])
            if not accounts:
                print("[ERROR] No ad accounts found")
                return False

            # Store the first ad account
            ad_account = accounts[0]['adaccount']
            self.config['ad_account_id'] = ad_account['id']
            self.config['ad_account_name'] = ad_account.get('name', 'Unknown')
            self.config['organization_id'] = org_id

            print(f"[SUCCESS] Found ad account: {ad_account['id']} ({ad_account.get('name', 'Unknown')})")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to fetch ad account info: {e}")
            return False

    def refresh_token(self):
        """Refresh the access token using refresh token"""
        if not self.config or 'refresh_token' not in self.config:
            print("[ERROR] No refresh token available")
            return False

        print("[INFO] Refreshing access token...")

        client_id = self.config.get('client_id', self.default_client_id)
        client_secret = self.config.get('client_secret', self.default_client_secret)

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

                # Update config with new tokens (clean them)
                access_token = token_info.get('access_token', '')
                refresh_token = token_info.get('refresh_token', '')

                # Clean tokens by removing whitespace and newlines
                self.config['access_token'] = ''.join(access_token.split()) if access_token else None
                if 'refresh_token' in token_info and refresh_token:
                    self.config['refresh_token'] = ''.join(refresh_token.split())

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

        # Clean the token - remove any whitespace, newlines, or invalid characters
        clean_token = ''.join(token.split())

        return {
            'Authorization': f'Bearer {clean_token}',
            'Content-Type': 'application/json'
        }

    def get_ad_account_id(self):
        """Get the stored ad account ID"""
        return self.config.get('ad_account_id') if self.config else None

    def start_authorization(self):
        """Start the OAuth authorization flow"""
        auth_url = self.generate_auth_url()
        print("=" * 80)
        print("SNAPCHAT AUTHORIZATION REQUIRED")
        print("=" * 80)
        print("1. Opening browser for authorization...")
        print(f"2. If browser doesn't open, visit: {auth_url}")
        print("3. After authorization, copy the 'code' parameter from the callback URL")
        print("4. Paste the code when prompted")
        print("=" * 80)

        try:
            webbrowser.open(auth_url)
        except:
            print("[WARNING] Could not open browser automatically")

        return input("Enter the authorization code from the callback URL: ").strip()

    def setup_credentials(self, client_id=None, client_secret=None, redirect_uri=None):
        """Setup or update API credentials"""
        if client_id:
            self.config['client_id'] = client_id
        if client_secret:
            self.config['client_secret'] = client_secret
        if redirect_uri:
            self.config['redirect_uri'] = redirect_uri

        return self.save_config(self.config)

    def is_authorized(self):
        """Check if we have valid authorization"""
        return (self.config and
                self.config.get('access_token') and
                self.config.get('ad_account_id') and
                not self.is_token_expired())

    def get_account_info(self):
        """Get stored account information"""
        if not self.config:
            return None

        return {
            'ad_account_id': self.config.get('ad_account_id'),
            'ad_account_name': self.config.get('ad_account_name'),
            'organization_id': self.config.get('organization_id'),
            'client_id': self.config.get('client_id'),
            'expires_at': self.config.get('expires_at')
        }

def test_token_manager():
    """Test the token manager"""
    print("=== TESTING ENHANCED TOKEN MANAGER ===")

    tm = TokenManager()

    # Check current authorization status
    if tm.is_authorized():
        print("[SUCCESS] Already authorized!")
        account_info = tm.get_account_info()
        print(f"Ad Account: {account_info['ad_account_id']} ({account_info['ad_account_name']})")
        print(f"Expires: {account_info['expires_at']}")

        # Test API call
        headers = tm.get_headers()
        try:
            response = requests.get('https://adsapi.snapchat.com/v1/me', headers=headers)
            if response.status_code == 200:
                print("[SUCCESS] API test successful!")
                me_data = response.json()
                print(f"User: {me_data['me']['display_name']} ({me_data['me']['email']})")
            else:
                print(f"[ERROR] API test failed: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] API test failed: {e}")

    else:
        print("[INFO] Authorization required")
        print("Choose an option:")
        print("1. Start OAuth authorization flow")
        print("2. Enter authorization code manually")
        print("3. Setup custom credentials")

        choice = input("Enter choice (1-3): ").strip()

        if choice == "1":
            # Start full OAuth flow
            try:
                auth_code = tm.start_authorization()
                if auth_code and tm.authorize_with_code(auth_code):
                    print("[SUCCESS] Authorization complete!")
                    account_info = tm.get_account_info()
                    print(f"Ad Account: {account_info['ad_account_id']} ({account_info['ad_account_name']})")
                else:
                    print("[ERROR] Authorization failed")
            except KeyboardInterrupt:
                print("\n[INFO] Authorization cancelled")

        elif choice == "2":
            # Manual code entry
            auth_code = input("Enter authorization code: ").strip()
            if auth_code and tm.authorize_with_code(auth_code):
                print("[SUCCESS] Authorization complete!")
                account_info = tm.get_account_info()
                print(f"Ad Account: {account_info['ad_account_id']} ({account_info['ad_account_name']})")
            else:
                print("[ERROR] Authorization failed")

        elif choice == "3":
            # Custom credentials setup
            print("Current credentials:")
            account_info = tm.get_account_info()
            print(f"Client ID: {account_info['client_id']}")

            client_id = input("Enter Client ID (press enter to keep current): ").strip()
            client_secret = input("Enter Client Secret (press enter to keep current): ").strip()
            redirect_uri = input("Enter Redirect URI (press enter to keep current): ").strip()

            if tm.setup_credentials(
                client_id=client_id if client_id else None,
                client_secret=client_secret if client_secret else None,
                redirect_uri=redirect_uri if redirect_uri else None
            ):
                print("[SUCCESS] Credentials updated!")
            else:
                print("[ERROR] Failed to update credentials")

if __name__ == "__main__":
    test_token_manager()