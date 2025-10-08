import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import time

class SnapchatAPIClient:
    def __init__(self, access_token: str, ad_account_id: str = None):
        self.access_token = access_token
        self.ad_account_id = ad_account_id
        self.base_url = "https://adsapi.snapchat.com/v1"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        url = f"{self.base_url}/{endpoint}"

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, params=data)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            raise Exception(f"API request failed: {error_msg}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def get_organizations(self) -> List[Dict]:
        response = self._make_request('GET', 'organizations')
        return response.get('organizations', [])

    def get_ad_accounts(self, organization_id: str) -> List[Dict]:
        response = self._make_request('GET', f'organizations/{organization_id}/adaccounts')
        return response.get('adaccounts', [])

    def get_campaigns(self, ad_account_id: str) -> List[Dict]:
        response = self._make_request('GET', f'adaccounts/{ad_account_id}/campaigns')
        return response.get('campaigns', [])

    def get_campaign_stats(self, campaign_id: str) -> Dict:
        try:
            response = self._make_request('GET', f'campaigns/{campaign_id}/stats')
            return response.get('total_stats', [{}])[0] if response.get('total_stats') else {}
        except:
            return {}

    def create_campaign(self, ad_account_id: str, campaign_data: Dict) -> Dict:
        campaign_payload = {
            'campaigns': [campaign_data]
        }
        print(f"Campaign payload: {campaign_payload}")
        response = self._make_request('POST', f'adaccounts/{ad_account_id}/campaigns', campaign_payload)
        print(f"Campaign response: {response}")

        # Check for API errors
        if response.get('request_status') == 'ERROR':
            error_msg = "Campaign creation failed"
            if 'campaigns' in response and response['campaigns']:
                campaign_error = response['campaigns'][0]
                if 'sub_request_error_reason' in campaign_error:
                    error_msg = campaign_error['sub_request_error_reason']
            raise Exception(error_msg)

        campaigns = response.get('campaigns', [])
        if not campaigns:
            raise Exception(f"No campaigns in response: {response}")
        return campaigns[0]

    def create_ad_squad(self, campaign_id: str, ad_squad_data: Dict) -> Dict:
        ad_squad_payload = {
            'adsquads': [ad_squad_data]
        }
        print(f"Ad Squad payload: {ad_squad_payload}")
        # Using the CORRECT endpoint from official documentation
        response = self._make_request('POST', f'campaigns/{campaign_id}/adsquads', ad_squad_payload)
        print(f"Ad Squad response: {response}")

        # Check for API errors
        if response.get('request_status') == 'ERROR':
            error_msg = "Ad Squad creation failed"
            if 'adsquads' in response and response['adsquads']:
                ad_squad_error = response['adsquads'][0]
                if 'sub_request_error_reason' in ad_squad_error:
                    error_msg = ad_squad_error['sub_request_error_reason']
            raise Exception(error_msg)

        adsquads = response.get('adsquads', [])
        if not adsquads:
            raise Exception(f"No adsquads in response: {response}")
        return adsquads[0]

    def create_media(self, ad_account_id: str, media_name: str, media_type: str = 'IMAGE') -> Dict:
        media_payload = {
            'media': [{
                'name': media_name,
                'type': media_type,
                'ad_account_id': ad_account_id
            }]
        }
        print(f"Media creation payload: {media_payload}")
        response = self._make_request('POST', f'adaccounts/{ad_account_id}/media', media_payload)

        # Check for API errors in media creation
        if response.get('request_status') == 'ERROR':
            error_msg = "Media creation failed"
            if 'media' in response and response['media']:
                media_error = response['media'][0]
                if 'sub_request_error_reason' in media_error:
                    error_msg = media_error['sub_request_error_reason']
            raise Exception(error_msg)

        media_list = response.get('media', [])
        if not media_list:
            raise Exception(f"No media in response: {response}")
        return media_list[0]

    def upload_media_file(self, media_id: str, media_file_path: str) -> Dict:
        upload_url = f"{self.base_url}/media/{media_id}/upload"

        import os
        import mimetypes

        filename = os.path.basename(media_file_path)
        content_type, _ = mimetypes.guess_type(media_file_path)
        if not content_type:
            content_type = 'image/jpeg'  # default fallback

        print(f"Uploading media file: {filename}, content_type: {content_type}")

        with open(media_file_path, 'rb') as f:
            files = {
                'file': (filename, f, content_type)
            }
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }

            response = requests.post(upload_url, headers=headers, files=files)

            if response.status_code != 200:
                print(f"Upload error: {response.status_code} - {response.text}")
                raise Exception(f"Media upload failed: {response.status_code} - {response.text}")

        # Return empty dict since upload endpoint might not return JSON
        try:
            return response.json()
        except:
            return {'status': 'uploaded'}

    def get_media_status(self, media_id: str) -> Dict:
        try:
            response = self._make_request('GET', f'media/{media_id}')
            print(f"Media status response: {response}")

            # Handle different response formats - updated for correct nested structure
            if isinstance(response, dict):
                if 'media' in response:
                    if isinstance(response['media'], list) and response['media']:
                        # Handle nested structure: response['media'][0]['media']
                        media_item = response['media'][0]
                        if isinstance(media_item, dict) and 'media' in media_item:
                            return media_item['media']
                        return media_item
                    elif isinstance(response['media'], dict):
                        return response['media']
                # Handle direct media object response
                return response
            return {}
        except Exception as e:
            print(f"Failed to get media status: {e}")
            return {}

    def wait_for_media_ready(self, media_id: str, timeout: int = 120) -> bool:
        print(f"Waiting for media {media_id} to be ready...")
        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            media_status = self.get_media_status(media_id)
            status = media_status.get('media_status', 'UNKNOWN')

            if status == 'READY':
                print(f"Media {media_id} is ready!")
                return True
            elif status in ['FAILED', 'ERROR']:
                print(f"Media {media_id} failed processing: {media_status}")
                return False
            elif status == 'PENDING_UPLOAD':
                print(f"Media {media_id} still pending upload, continuing to wait...")
            elif status == 'PROCESSING':
                print(f"Media {media_id} is processing...")
            else:
                print(f"Media status: {status}, waiting...")

            time.sleep(10)  # Wait 10 seconds for better stability

        print(f"Timeout waiting for media {media_id} to be ready after {timeout}s")
        return False

    def upload_media(self, ad_account_id: str, media_file_path: str, media_type: str = 'IMAGE', wait_for_ready: bool = False) -> Dict:
        import os
        media_name = os.path.basename(media_file_path)

        # Determine media type from file extension
        file_ext = os.path.splitext(media_file_path)[1].lower()
        if file_ext in ['.mp4', '.mov']:
            media_type = 'VIDEO'
        else:
            media_type = 'IMAGE'

        print(f"Creating media entity: {media_name}, type: {media_type}")

        # First create media entity
        media = self.create_media(ad_account_id, media_name, media_type)
        print(f"Media creation response: {media}")

        if 'media' not in media or 'id' not in media['media']:
            raise Exception(f"Failed to create media entity: {media}")

        media_id = media['media']['id']

        # Then upload the file to that media ID
        self.upload_media_file(media_id, media_file_path)

        # FAST MODE: Skip waiting for each video (batch wait later instead)
        # Only wait if explicitly requested
        if wait_for_ready:
            if not self.wait_for_media_ready(media_id):
                print(f"Warning: Media {media_id} may not be ready, continuing anyway...")

        return media

    def create_creative(self, ad_account_id: str, creative_data: Dict) -> Dict:
        creative_payload = {
            'creatives': [creative_data]
        }
        print(f"Creative payload: {creative_payload}")
        response = self._make_request('POST', f'adaccounts/{ad_account_id}/creatives', creative_payload)
        print(f"Creative response: {response}")

        # Check for API errors
        if response.get('request_status') == 'ERROR':
            error_msg = "Creative creation failed"
            if 'creatives' in response and response['creatives']:
                creative_error = response['creatives'][0]
                if 'sub_request_error_reason' in creative_error:
                    error_msg = creative_error['sub_request_error_reason']
            raise Exception(error_msg)

        creatives = response.get('creatives', [])
        if not creatives:
            raise Exception(f"No creatives in response: {response}")
        return creatives[0]

    def create_ad(self, ad_squad_id: str, ad_data: Dict) -> Dict:
        ad_payload = {
            'ads': [ad_data]
        }
        print(f"Ad payload: {ad_payload}")
        response = self._make_request('POST', f'adsquads/{ad_squad_id}/ads', ad_payload)
        print(f"Ad response: {response}")

        # Check for API errors
        if response.get('request_status') == 'ERROR':
            error_msg = "Ad creation failed"
            if 'ads' in response and response['ads']:
                ad_error = response['ads'][0]
                if 'sub_request_error_reason' in ad_error:
                    error_msg = ad_error['sub_request_error_reason']
            raise Exception(error_msg)

        ads = response.get('ads', [])
        if not ads:
            raise Exception(f"No ads in response: {response}")
        return ads[0]

    def get_pixels(self, ad_account_id: str) -> List[Dict]:
        try:
            response = self._make_request('GET', f'adaccounts/{ad_account_id}/pixels')
            return response.get('pixels', [])
        except Exception as e:
            print(f"Failed to get pixels: {e}")
            return []

    def get_public_profiles(self, organization_id: str) -> List[Dict]:
        try:
            url = f"https://businessapi.snapchat.com/v1/organizations/{organization_id}/public_profiles"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get('public_profiles', [])
        except Exception as e:
            print(f"Failed to get public profiles: {e}")
            return []

    def get_my_profile(self) -> Dict:
        try:
            url = "https://businessapi.snapchat.com/v1/public_profiles/my_profile"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to get my profile: {e}")
            return {}

    def get_profile_info(self, ad_account_id: str) -> Dict:
        # Try to get proper public profile first
        try:
            my_profile = self.get_my_profile()
            if my_profile and 'public_profile' in my_profile:
                profile_id = my_profile['public_profile']['id']
                return {
                    'profile': {
                        'id': profile_id,
                        'name': my_profile['public_profile'].get('display_name', 'My Profile')
                    }
                }
        except Exception as e:
            print(f"My profile fetch failed: {e}")

        # Fallback: try organization profiles
        try:
            organizations = self.get_organizations()
            if organizations:
                org_id = organizations[0]['organization']['id']
                public_profiles = self.get_public_profiles(org_id)
                if public_profiles:
                    profile = public_profiles[0]['public_profile']
                    return {
                        'profile': {
                            'id': profile['id'],
                            'name': profile.get('display_name', 'Organization Profile')
                        }
                    }
        except Exception as e:
            print(f"Organization profiles fetch failed: {e}")

        # Last fallback: use the ad account as profile
        print("Warning: Using ad account as profile fallback - may cause creative creation issues")
        return {
            'profile': {
                'id': ad_account_id,
                'name': 'Ad Account Profile'
            }
        }

class SnapchatCampaignBuilder:
    def __init__(self, api_client: SnapchatAPIClient):
        self.api = api_client

    def build_campaign_data(self, name: str, budget: int, objective: str = None) -> Dict:
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)

        campaign_data = {
            'name': name,
            'status': 'PAUSED',
            'start_time': now.isoformat(),
            'end_time': (now + timedelta(days=30)).isoformat(),
            'buy_model': 'AUCTION',
            'objective': 'SALES'  # Use SALES objective for conversions
        }

        if budget:
            campaign_data['daily_budget_micro'] = budget * 1000000

        return campaign_data

    def build_ad_squad_data(self, name: str, campaign_id: str, targeting: Dict,
                           bid_micro: int = None, billing_event: str = 'IMPRESSION', pixel_id: str = None) -> Dict:
        # Simplified ad squad matching successful formats
        ad_squad_data = {
            'name': name,
            'status': 'PAUSED',
            'campaign_id': campaign_id,
            'type': 'SNAP_ADS',
            'targeting': targeting,
            'placement_v2': {
                'config': 'AUTOMATIC'
            },
            'billing_event': billing_event,  # Use IMPRESSION for now
            'auto_bid': True,  # Auto bid
            'optimization_goal': 'PIXEL_PURCHASE' if pixel_id else 'IMPRESSIONS',
            'daily_budget_micro': 25000000
        }

        # Fix timing
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)
        start_time = now
        end_time = start_time + timedelta(days=30)

        ad_squad_data['start_time'] = start_time.isoformat()
        ad_squad_data['end_time'] = end_time.isoformat()

        # Add pixel_id if provided for conversion tracking
        if pixel_id:
            ad_squad_data['pixel_id'] = pixel_id
            print(f"Using pixel ID for conversion tracking: {pixel_id}")

        return ad_squad_data

    def build_targeting_spec(self, geo_locations: List[str] = None,
                           age_groups: List[str] = None,
                           genders: List[str] = None,
                           interests: List[str] = None) -> Dict:
        # Saudi Arabia targeting like manual process
        targeting = {
            'regulated_content': False,
            'demographics': [
                {
                    'min_age': '20',  # Age 20 to 55+
                    'max_age': '55'
                }
            ],
            'geos': [
                {
                    'country_code': 'sa'  # Saudi Arabia
                }
            ]
        }

        # Override with provided values if any
        if geo_locations:
            targeting['geos'] = [
                {'country_code': geo.lower()} for geo in geo_locations
            ]

        # Handle age groups properly
        if age_groups:
            demographics = []
            for age_group in age_groups:
                if '-' in age_group:
                    min_age, max_age = age_group.split('-')
                    demographics.append({
                        'min_age': min_age,
                        'max_age': max_age
                    })
            if demographics:
                targeting['demographics'] = demographics

        # All genders by default (no gender restriction)
        return targeting

    def build_creative_data(self, name: str, headline: str, media_id: str,
                          cta_type: str, landing_page_url: str,
                          profile_id: str, brand_name: str = None, ad_account_id: str = None) -> Dict:
        # Build creative exactly like manual process
        creative_data = {
            'ad_account_id': ad_account_id,
            'name': name,
            'type': 'WEB_VIEW',
            'headline': headline,
            'brand_name': brand_name or 'anas',  # Use brand name from manual
            'top_snap_media_id': media_id,
            'shareable': False,
            'call_to_action': cta_type.upper(),
            'web_view_properties': {
                'url': landing_page_url,
                'allow_snap_javascript_sdk': False,
                'use_immersive_mode': False,
                'deep_link_urls': [],
                'block_preload': True,
                'web_browser_type': 'SNAP'
            }
        }

        # Try with profile_properties only if we have a real profile_id
        if profile_id != ad_account_id:
            creative_data['profile_properties'] = {
                'profile_id': profile_id
            }
        else:
            print(f"Skipping profile_properties due to invalid profile_id - will test creative creation without it")

        return creative_data

    def build_ad_data(self, name: str, ad_squad_id: str, creative_id: str) -> Dict:
        # BREAKTHROUGH: WEB_VIEW creatives need REMOTE_WEBPAGE ad type!
        return {
            'name': name,
            'ad_squad_id': ad_squad_id,
            'creative_id': creative_id,
            'status': 'PAUSED',
            'type': 'REMOTE_WEBPAGE'  # Correct type for WEB_VIEW creatives
        }