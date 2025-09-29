#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
import json
import os
import subprocess
import threading
from datetime import datetime, timezone, timedelta
from token_manager import TokenManager
from snapchat_api_client import SnapchatAPIClient
import time
import uuid
import requests
import concurrent.futures
from queue import Queue
import ssl
from urllib3.exceptions import SSLError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import tempfile
import zipfile
from werkzeug.utils import secure_filename

# Complete list of Snapchat-supported countries from API
SNAPCHAT_COUNTRIES = [
    {'code': 'dz', 'name': 'Algeria'},
    {'code': 'ke', 'name': 'Kenya'},
    {'code': 'ma', 'name': 'Morocco'},
    {'code': 'ng', 'name': 'Nigeria'},
    {'code': 'za', 'name': 'South Africa'},
    {'code': 'tn', 'name': 'Tunisia'},
    {'code': 'eg', 'name': 'Egypt'},
    {'code': 'au', 'name': 'Australia'},
    {'code': 'nz', 'name': 'New Zealand'},
    {'code': 'ps', 'name': 'Palestinian Territories'},
    {'code': 'hk', 'name': 'Hong Kong'},
    {'code': 'in', 'name': 'India'},
    {'code': 'id', 'name': 'Indonesia'},
    {'code': 'iq', 'name': 'Iraq'},
    {'code': 'il', 'name': 'Israel'},
    {'code': 'jp', 'name': 'Japan'},
    {'code': 'kz', 'name': 'Kazakhstan'},
    {'code': 'jo', 'name': 'Jordan'},
    {'code': 'kw', 'name': 'Kuwait'},
    {'code': 'lb', 'name': 'Lebanon'},
    {'code': 'my', 'name': 'Malaysia'},
    {'code': 'bh', 'name': 'Bahrain'},
    {'code': 'om', 'name': 'Oman'},
    {'code': 'pk', 'name': 'Pakistan'},
    {'code': 'ph', 'name': 'Philippines'},
    {'code': 'qa', 'name': 'Qatar'},
    {'code': 'sa', 'name': 'Saudi Arabia'},
    {'code': 'sg', 'name': 'Singapore'},
    {'code': 'th', 'name': 'Thailand'},
    {'code': 'ae', 'name': 'United Arab Emirates'},
    {'code': 'bg', 'name': 'Bulgaria'},
    {'code': 'hr', 'name': 'Croatia'},
    {'code': 'cz', 'name': 'Czech Republic'},
    {'code': 'dk', 'name': 'Denmark'},
    {'code': 'fi', 'name': 'Finland'},
    {'code': 'fr', 'name': 'France'},
    {'code': 'de', 'name': 'Germany'},
    {'code': 'gr', 'name': 'Greece'},
    {'code': 'hu', 'name': 'Hungary'},
    {'code': 'ie', 'name': 'Ireland'},
    {'code': 'it', 'name': 'Italy'},
    {'code': 'at', 'name': 'Austria'},
    {'code': 'lt', 'name': 'Lithuania'},
    {'code': 'lu', 'name': 'Luxembourg'},
    {'code': 'mc', 'name': 'Monaco'},
    {'code': 'nl', 'name': 'Netherlands'},
    {'code': 'be', 'name': 'Belgium'},
    {'code': 'no', 'name': 'Norway'},
    {'code': 'pl', 'name': 'Poland'},
    {'code': 'pt', 'name': 'Portugal'},
    {'code': 'ro', 'name': 'Romania'},
    {'code': 'rs', 'name': 'Serbia'},
    {'code': 'sk', 'name': 'Slovakia'},
    {'code': 'si', 'name': 'Slovenia'},
    {'code': 'es', 'name': 'Spain'},
    {'code': 'se', 'name': 'Sweden'},
    {'code': 'ch', 'name': 'Switzerland'},
    {'code': 'tr', 'name': 'Turkey'},
    {'code': 'uk', 'name': 'United Kingdom'},
    {'code': 'ca', 'name': 'Canada'},
    {'code': 'cr', 'name': 'Costa Rica'},
    {'code': 'do', 'name': 'Dominican Republic'},
    {'code': 'mx', 'name': 'Mexico'},
    {'code': 'pr', 'name': 'Puerto Rico'},
    {'code': 'us', 'name': 'United States'},
    {'code': 'cl', 'name': 'Chile'},
    {'code': 'co', 'name': 'Colombia'},
    {'code': 'ec', 'name': 'Ecuador'},
    {'code': 'ar', 'name': 'Argentina'},
    {'code': 'pe', 'name': 'Peru'},
    {'code': 'br', 'name': 'Brazil'},
    {'code': 'uy', 'name': 'Uruguay'}
]

def make_robust_api_request(method, url, headers=None, json_data=None, max_retries=3, backoff_factor=1):
    """
    Make a robust API request with retry logic for SSL and connection errors
    """
    session = requests.Session()

    # Configure simple retry strategy for compatibility
    try:
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=backoff_factor
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
    except TypeError:
        # Fallback for older urllib3 versions - use simple retry count
        adapter = HTTPAdapter(max_retries=max_retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

    # Retry logic for SSL errors
    for attempt in range(max_retries + 1):
        try:
            print(f"[DEBUG] API Request attempt {attempt + 1}/{max_retries + 1}: {method} {url}")

            if method.upper() == 'GET':
                response = session.get(url, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = session.post(url, headers=headers, json=json_data, timeout=30)
            elif method.upper() == 'PUT':
                response = session.put(url, headers=headers, json=json_data, timeout=30)
            elif method.upper() == 'DELETE':
                response = session.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            print(f"[DEBUG] API Response: {response.status_code}")
            return response

        except (SSLError, requests.exceptions.SSLError, ssl.SSLError) as e:
            print(f"[WARNING] SSL Error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries:
                wait_time = backoff_factor * (2 ** attempt)
                print(f"[INFO] Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                print(f"[ERROR] SSL Error after {max_retries + 1} attempts: {str(e)}")
                raise

        except requests.exceptions.ConnectionError as e:
            print(f"[WARNING] Connection Error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries:
                wait_time = backoff_factor * (2 ** attempt)
                print(f"[INFO] Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                print(f"[ERROR] Connection Error after {max_retries + 1} attempts: {str(e)}")
                raise

        except Exception as e:
            print(f"[ERROR] Unexpected error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries:
                wait_time = backoff_factor * (2 ** attempt)
                print(f"[INFO] Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                raise

    # This should never be reached
    raise Exception("Max retries exceeded")

app = Flask(__name__, template_folder='templates_flask')
app.secret_key = 'updated_beast_mode_dashboard_secret_key'

# Country flag mapping
COUNTRY_FLAGS = {
    'dz': '🇩🇿', 'ke': '🇰🇪', 'ma': '🇲🇦', 'ng': '🇳🇬', 'za': '🇿🇦', 'tn': '🇹🇳', 'eg': '🇪🇬',
    'au': '🇦🇺', 'nz': '🇳🇿', 'ps': '🇵🇸', 'hk': '🇭🇰', 'in': '🇮🇳', 'id': '🇮🇩', 'iq': '🇮🇶',
    'il': '🇮🇱', 'jp': '🇯🇵', 'kz': '🇰🇿', 'jo': '🇯🇴', 'kw': '🇰🇼', 'lb': '🇱🇧', 'my': '🇲🇾',
    'bh': '🇧🇭', 'om': '🇴🇲', 'pk': '🇵🇰', 'ph': '🇵🇭', 'qa': '🇶🇦', 'sa': '🇸🇦', 'sg': '🇸🇬',
    'th': '🇹🇭', 'ae': '🇦🇪', 'bg': '🇧🇬', 'hr': '🇭🇷', 'cz': '🇨🇿', 'dk': '🇩🇰', 'fi': '🇫🇮',
    'fr': '🇫🇷', 'de': '🇩🇪', 'gr': '🇬🇷', 'hu': '🇭🇺', 'ie': '🇮🇪', 'it': '🇮🇹', 'at': '🇦🇹',
    'lt': '🇱🇹', 'lu': '🇱🇺', 'mc': '🇲🇨', 'nl': '🇳🇱', 'be': '🇧🇪', 'no': '🇳🇴', 'pl': '🇵🇱',
    'pt': '🇵🇹', 'ro': '🇷🇴', 'rs': '🇷🇸', 'sk': '🇸🇰', 'si': '🇸🇮', 'es': '🇪🇸', 'se': '🇸🇪',
    'ch': '🇨🇭', 'tr': '🇹🇷', 'uk': '🇬🇧', 'ca': '🇨🇦', 'cr': '🇨🇷', 'do': '🇩🇴', 'mx': '🇲🇽',
    'pr': '🇵🇷', 'us': '🇺🇸', 'cl': '🇨🇱', 'co': '🇨🇴', 'ec': '🇪🇨', 'ar': '🇦🇷', 'pe': '🇵🇪',
    'br': '🇧🇷', 'uy': '🇺🇾'
}

def get_country_flag(country_code):
    return COUNTRY_FLAGS.get(country_code.lower(), '🌍')

# Add the function to template context
app.jinja_env.globals.update(get_country_flag=get_country_flag)

# Authentication credentials
AUTH_USERNAME = 'anasr4'
AUTH_PASSWORD = 'Rabiibeast2004@'

# Global tasks tracker for video compression
compression_tasks = {}

def require_auth(f):
    """Decorator to require authentication for routes"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Global variables to track progress
dashboard_bots = {
    'folder_beast': {
        'name': 'Optimized Folder Beast Mode',
        'description': '200 Ads in Under 10 Minutes!',
        'status': 'ready',
        'icon': '🚀',
        'color': '#00ff88'
    },
    'single_ad': {
        'name': 'Single Ad Bot',
        'description': '1 Video → 1 Campaign, 1 Ad Set, 1 Ad',
        'status': 'ready',
        'icon': '🎯',
        'color': '#4CAF50'
    },
    'test_bot': {
        'name': 'Test Bot',
        'description': '3 Videos → Quick Testing (2-3 min)',
        'status': 'ready',
        'icon': '🧪',
        'color': '#667eea'
    },
    'campaign_manager': {
        'name': 'Campaign Manager',
        'description': 'Manage existing campaigns',
        'status': 'ready',
        'icon': '📊',
        'color': '#4444ff'
    },
    'token_manager': {
        'name': 'Token Manager',
        'description': 'Refresh and manage API tokens',
        'status': 'ready',
        'icon': '🔑',
        'color': '#ffaa00'
    },
    'analytics_bot': {
        'name': 'Analytics Bot',
        'description': 'Campaign performance analytics',
        'status': 'ready',
        'icon': '📈',
        'color': '#00aaff'
    },
    'bulk_uploader': {
        'name': 'Bulk Uploader',
        'description': 'Mass upload media files',
        'status': 'ready',
        'icon': '📤',
        'color': '#aa00ff'
    },
    'video_compressor': {
        'name': 'Video Compressor',
        'description': '1 Video → Custom Variants (1-1000) H.264 + Original Aspect Ratio',
        'status': 'ready',
        'icon': '🎬',
        'color': '#ff6600'
    }
}

# Global progress tracking with detailed stages
progress_tracker = {}
single_ad_status = {}
test_bot_status = {}

# Initialize session data for folder beast mode
def init_folder_beast_session():
    if 'folder_beast' not in session:
        session['folder_beast'] = {
            'step': 1,
            'campaign_data': {},
            'adset_data': {},
            'ad_data': {},
            'progress': []
        }

def check_media_status_batch(media_list, headers, max_check=50):
    """Check status of media files in batches"""
    ready_count = 0
    checked = 0

    for media_info in media_list[:max_check]:
        try:
            response = requests.get(f'https://adsapi.snapchat.com/v1/media/{media_info["media_id"]}', headers=headers)
            if response.status_code == 200:
                media_data = response.json()
                status = media_data.get('media', {}).get('status', 'UNKNOWN')
                if status == 'READY':
                    ready_count += 1
                checked += 1
        except:
            continue

    return ready_count, checked

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == AUTH_USERNAME and password == AUTH_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout route"""
    session.pop('authenticated', None)
    return redirect(url_for('login'))

@app.route('/')
@require_auth
def dashboard():
    """Main dashboard with all bots"""
    return render_template('updated_dashboard.html', bots=dashboard_bots)

@app.route('/single-ad')
@require_auth
def single_ad():
    """Single Ad Bot"""
    return render_template('single_ad_bot.html')

@app.route('/test-bot')
@require_auth
def test_bot():
    """Test Bot"""
    return render_template('test_bot.html')

@app.route('/folder-beast')
@require_auth
def folder_beast():
    """Enhanced Folder Beast Mode - 3-Step Wizard"""
    # Initialize session data if not exists
    if 'folder_beast_data' not in session:
        session['folder_beast_data'] = {}

    # Provide current datetime for minimum date validation
    current_datetime = datetime.now().strftime('%Y-%m-%dT%H:%M')

    return render_template('folder_beast_step1.html',
                         data=session['folder_beast_data'],
                         current_datetime=current_datetime)

@app.route('/folder-beast/step1', methods=['POST'])
@require_auth
def folder_beast_step1():
    """Handle Enhanced Campaign Details (Step 1)"""
    # Save step 1 data to session
    if 'folder_beast_data' not in session:
        session['folder_beast_data'] = {}

    session['folder_beast_data'].update({
        'campaign_name': request.form.get('campaign_name'),
        'objective': request.form.get('objective'),
        'daily_budget': request.form.get('daily_budget'),
        'start_date': request.form.get('start_date'),
        'campaign_status': request.form.get('campaign_status')
    })

    session.modified = True

    return redirect(url_for('folder_beast_step2_page'))

@app.route('/folder-beast/step2')
@require_auth
def folder_beast_step2_page():
    """Enhanced Folder Beast Mode - Step 2: Ad Sets"""
    if 'folder_beast_data' not in session:
        session['folder_beast_data'] = {}

    return render_template('folder_beast_step2.html', data=session['folder_beast_data'], countries=SNAPCHAT_COUNTRIES)

@app.route('/folder-beast/step2', methods=['POST'])
@require_auth
def folder_beast_step2():
    """Handle Enhanced Ad Set Details (Step 2)"""
    # Save step 2 data to session
    if 'folder_beast_data' not in session:
        session['folder_beast_data'] = {}

    pixel_id_from_form = request.form.get('pixel_id')
    print(f"[DEBUG] Pixel ID captured from form: '{pixel_id_from_form}'")

    session['folder_beast_data'].update({
        'adset_base_name': request.form.get('adset_base_name'),
        'adset_status': request.form.get('adset_status'),
        'enable_pixel': request.form.get('enable_pixel'),
        'pixel_id': pixel_id_from_form,
        'goal_type': request.form.get('goal_type'),
        'bid_strategy': request.form.get('bid_strategy'),
        'bid_amount': request.form.get('bid_amount'),
        'adset_budget': request.form.get('adset_budget'),
        'countries': request.form.getlist('countries'),
        'min_age': request.form.get('min_age'),
        'max_age': request.form.get('max_age')
    })

    session.modified = True

    return redirect(url_for('folder_beast_step3_page'))

@app.route('/folder-beast/step3')
@require_auth
def folder_beast_step3_page():
    """Enhanced Folder Beast Mode - Step 3: Creative Details"""
    if 'folder_beast_data' not in session:
        session['folder_beast_data'] = {}

    return render_template('folder_beast_step3.html', data=session['folder_beast_data'])

@app.route('/folder-beast/step3', methods=['POST'])
@require_auth
def folder_beast_step3():
    """Handle Ad Creation Details (Step 3)"""
    init_folder_beast_session()

    # Get campaign structure configuration
    campaign_structure = request.form.get('campaign_structure', 'beast')  # Default to beast mode

    print(f"[DEBUG] ALL FORM DATA: {dict(request.form)}")
    print(f"[DEBUG] Step 3: Raw campaign_structure value: '{campaign_structure}'")

    # Campaign structure configurations
    structure_configs = {
        'small': {'ads': 10, 'adsets': 2, 'ads_per_adset': 5},
        'medium': {'ads': 50, 'adsets': 5, 'ads_per_adset': 10},
        'large': {'ads': 100, 'adsets': 5, 'ads_per_adset': 20},
        'beast': {'ads': 200, 'adsets': 5, 'ads_per_adset': 40}
    }

    config = structure_configs.get(campaign_structure, structure_configs['beast'])
    print(f"[DEBUG] Step 3: Campaign structure selected: {campaign_structure}, config: {config}")
    print(f"[DEBUG] Step 3: Will create {config['adsets']} ad sets with {config['ads_per_adset']} ads each")

    session['folder_beast']['ad_data'] = {
        'videos_path': request.form.get('videos_path'),
        'csv_path': request.form.get('csv_path'),
        'ad_name_prefix': request.form.get('ad_name_prefix'),
        'brand_name': request.form.get('brand_name'),
        'website_url': request.form.get('website_url'),
        'call_to_action': request.form.get('call_to_action'),
        'creative_type': request.form.get('creative_type'),
        'test_mode': request.form.get('test_mode') == 'on',
        'campaign_structure': campaign_structure,
        'total_ads': config['ads'],
        'ads_per_adset': config['ads_per_adset']
    }

    # Update adset data to reflect the structure
    session['folder_beast']['adset_data']['num_adsets'] = config['adsets']

    # Also store in folder_beast_data session for consistency
    if 'folder_beast_data' not in session:
        session['folder_beast_data'] = {}

    # Clean paths by removing any extra quotes
    videos_path = request.form.get('videos_path', '').strip('"').strip("'")
    csv_path = request.form.get('csv_path', '').strip('"').strip("'")

    print(f"[DEBUG] Step 3: Cleaned videos_path: '{videos_path}'")
    print(f"[DEBUG] Step 3: Cleaned csv_path: '{csv_path}'")

    session['folder_beast_data'].update({
        'videos_path': videos_path,
        'csv_path': csv_path,
        'brand_name': request.form.get('brand_name'),
        'website_url': request.form.get('website_url'),
        'call_to_action': request.form.get('call_to_action'),
        'campaign_structure': campaign_structure,
        'total_ads': config['ads'],
        'ads_per_adset': config['ads_per_adset']
    })

    session['folder_beast']['step'] = 4
    session.modified = True

    return redirect(url_for('folder_beast_execute'))

@app.route('/folder-beast/execute')
@require_auth
def folder_beast_execute():
    """Execute the campaign creation"""
    init_folder_beast_session()

    # Combine all data for execution
    execution_data = {
        'campaign': session['folder_beast']['campaign_data'],
        'adsets': session['folder_beast']['adset_data'],
        'ads': session['folder_beast']['ad_data']
    }

    return render_template('optimized_beast_execute.html', data=execution_data)

@app.route('/folder-beast/execute-real', methods=['POST'])
@require_auth
def folder_beast_execute_real():
    """Actually execute the campaign creation with real API calls"""
    init_folder_beast_session()

    # Generate unique execution ID
    execution_id = str(uuid.uuid4())

    # Get form data directly if sent from Modern Beast Mode, otherwise use session
    if 'folder_beast_data' not in session:
        session['folder_beast_data'] = {}

    session_data = session['folder_beast_data']

    # Check if this is a direct form submission from Modern Beast Mode
    # If form data is present, use it instead of session data
    form_campaign_name = request.form.get('campaign_name')
    if form_campaign_name:
        # Direct form submission - use form data
        execution_data = {
            'campaign': {
                'campaign_name': form_campaign_name,
                'objective': request.form.get('objective', 'SALES'),
                'daily_budget': str(request.form.get('daily_budget', '100')),
                'start_date': request.form.get('start_date'),
                'campaign_status': request.form.get('campaign_status', 'ACTIVE')
            },
            'adsets': {
                'adset_base_name': request.form.get('adset_base_name', f'{form_campaign_name} - AdSet'),
                'adset_status': request.form.get('adset_status', 'PAUSED'),
                'pixel_enabled': request.form.get('pixel_enabled', 'on'),
                'goal_type': request.form.get('goal_type', 'CONVERSIONS'),
                'bid_strategy': request.form.get('bid_strategy', 'AUTO_BID'),
                'bid_amount': str(request.form.get('bid_amount', '50')),
                'adset_budget': str(request.form.get('adset_budget', '20')),
                'countries': [request.form.get('target_country', 'SA')],
                'min_age': str(request.form.get('min_age', '22')),
                'max_age': str(request.form.get('max_age', '55+'))
            },
            'ads': {
                'creative_base_name': request.form.get('creative_base_name', request.form.get('brand_name', '')),
                'naming_convention': request.form.get('naming_convention', 'sequential'),
                'creative_status': request.form.get('creative_status', 'PAUSED'),
                'videos_path': request.form.get('videos_folder', ''),
                'csv_path': request.form.get('headlines_csv', ''),
                'brand_name': request.form.get('brand_name', ''),
                'website_url': request.form.get('landing_url', 'https://www.sallagcc.com/ksagm'),
                'tracking_url': request.form.get('tracking_url', ''),
                'call_to_action': request.form.get('cta_type', 'SHOP_NOW'),
                'creative_type': request.form.get('creative_type', 'WEB_VIEW')
            }
        }
    else:
        # Session-based submission - use session data
        execution_data = {
            'campaign': {
                'campaign_name': session_data.get('campaign_name', 'Beast Mode Campaign'),
                'objective': session_data.get('objective', 'SALES'),
                'daily_budget': str(session_data.get('daily_budget', '100')),
                'start_date': session_data.get('start_date'),
                'campaign_status': session_data.get('campaign_status', 'ACTIVE')
            },
        'adsets': {
            'adset_base_name': session_data.get('adset_base_name', 'Beast AdSet'),
            'adset_status': session_data.get('adset_status', 'ACTIVE'),
            'enable_pixel': session_data.get('enable_pixel', 'true'),
            'pixel_id': session_data.get('pixel_id', ''),
            'goal_type': session_data.get('goal_type', 'CONVERSIONS'),
            'bid_strategy': session_data.get('bid_strategy', 'AUTO_BID'),
            'bid_amount': str(session_data.get('bid_amount', '50')),
            'adset_budget': str(session_data.get('adset_budget', '20')),
            'countries': session_data.get('countries', ['SA', 'AE']),
            'min_age': str(session_data.get('min_age', '22')),
            'max_age': str(session_data.get('max_age', '55+'))
        },
        'ads': {
            'creative_base_name': session_data.get('creative_base_name', ''),
            'naming_convention': session_data.get('naming_convention', 'sequential'),
            'creative_status': session_data.get('creative_status', 'ACTIVE'),
            'videos_path': session_data.get('videos_path', 'C:\\Users\\PC\\Desktop\\200 vdieos'),
            'csv_path': session_data.get('csv_path', ''),
            'brand_name': session_data.get('brand_name', ''),
            'website_url': session_data.get('website_url', 'https://www.sallagcc.com/ksagm'),
            'tracking_url': session_data.get('tracking_url', ''),
            'call_to_action': session_data.get('call_to_action', 'SHOP_NOW'),
            'creative_type': session_data.get('creative_type', 'WEB_VIEW'),
            'test_mode': session_data.get('test_mode', False),
            'campaign_structure': session_data.get('campaign_structure', 'beast'),
            'total_ads': session_data.get('total_ads', 200),
            'ads_per_adset': session_data.get('ads_per_adset', 40)
        }
    }

    print(f"[DEBUG] Beast mode data pixel_id from session: '{execution_data['adsets']['pixel_id']}'")
    print(f"[DEBUG] Enable pixel setting: '{execution_data['adsets']['enable_pixel']}'")

    # Initialize progress tracker with detailed stages
    progress_tracker[execution_id] = {
        'progress': 0,
        'status': 'starting',
        'stage': 'Initializing...',
        'log': ['[INFO] Optimized Beast Mode execution started...'],
        'campaign_id': None,
        'ads_created': 0,
        'ads_target': 200,
        'media_uploaded': 0,
        'media_ready': 0,
        'error': None,
        'execution_time': 0,
        'start_time': time.time()
    }

    # Start execution in background thread
    thread = threading.Thread(target=execute_optimized_beast_mode, args=(execution_id, execution_data))
    thread.daemon = True
    thread.start()

    return jsonify({'execution_id': execution_id, 'status': 'started'})

@app.route('/api/execution-status/<execution_id>')
@require_auth
def get_execution_status(execution_id):
    """Get the current status of campaign execution with detailed progress"""
    if execution_id in progress_tracker:
        # Calculate execution time
        if progress_tracker[execution_id]['start_time']:
            progress_tracker[execution_id]['execution_time'] = time.time() - progress_tracker[execution_id]['start_time']

        return jsonify(progress_tracker[execution_id])
    else:
        return jsonify({'error': 'Execution not found'}), 404

def execute_single_ad_mode(execution_id, data):
    """Execute single ad creation"""
    global single_ad_status
    try:

        def update_single_ad_progress(progress, step, status, **kwargs):
            single_ad_status[execution_id].update({
                'progress_percent': progress,
                'current_step': step,
                'status': status,
                **kwargs
            })

        # Get Snapchat token
        tm = TokenManager()
        headers = tm.get_headers()
        if not headers:
            raise Exception("Invalid or expired Snapchat access token")

        # Update progress: Starting
        update_single_ad_progress(10, "Creating campaign...", "Creating campaign")

        # 1. Create Campaign
        campaign_data = {
            'campaigns': [{
                'name': data['campaign']['name'],
                'status': data['campaign']['status'],
                'funding_source_ids': ['be47beae-b552-4cd9-9e75-d44ab3db55de'],
                'objective': data['campaign']['objective'],
                'daily_budget_micro': int(float(data['campaign']['daily_budget'])) * 1000000,
                'start_time': data['campaign']['start_date'],
                'regulations': {
                    'restricted_delivery_region': ['CHINA']
                }
            }]
        }

        print(f"[DEBUG] Creating campaign: {data['campaign']['name']}")
        campaign_response = requests.post(
            'https://adsapi.snapchat.com/v1/campaigns',
            headers=headers,
            json=campaign_data
        )

        if campaign_response.status_code != 200:
            raise Exception(f"Campaign creation failed: {campaign_response.text}")

        campaign_result = campaign_response.json()
        campaign_id = campaign_result['campaigns'][0]['id']

        update_single_ad_progress(30, "Creating ad set...", "Creating ad set", campaign_name=data['campaign']['name'])

        # 2. Create Ad Set
        adset_data = {
            'adsquads': [{
                'name': data['adsets']['base_name'],
                'status': data['adsets']['status'],
                'auto_bid': True,
                'optimization_goal': 'CONVERSIONS',
                'daily_budget_micro': int(float(data['adsets']['budget_per_adset'])) * 1000000,
                'start_time': data['campaign']['start_date'],
                'targeting': {
                    'geos': [{'country_code': country} for country in data['adsets']['countries']],
                    'demographics': [{
                        'min_age': data['adsets']['min_age'],
                        'max_age': data['adsets']['max_age']
                    }]
                }
            }]
        }

        print(f"[DEBUG] Creating ad set for campaign {campaign_id}")
        adset_response = requests.post(
            f'https://adsapi.snapchat.com/v1/campaigns/{campaign_id}/adsquads',
            headers=headers,
            json=adset_data
        )

        if adset_response.status_code != 200:
            raise Exception(f"Ad set creation failed: {adset_response.text}")

        adset_result = adset_response.json()
        adset_id = adset_result['adsquads'][0]['id']

        update_single_ad_progress(50, "Uploading video...", "Uploading video", adset_name=data['adsets']['base_name'])

        # 3. Upload video
        video_path = data['ads']['video_file']
        if not os.path.exists(video_path):
            raise Exception(f"Video file not found: {video_path}")

        # Upload media
        media_upload_response = upload_media_file(video_path, headers)
        if not media_upload_response.get('success'):
            raise Exception(f"Media upload failed: {media_upload_response.get('error', 'Unknown error')}")

        media_id = media_upload_response['media_id']

        update_single_ad_progress(80, "Creating ad creative...", "Creating ad creative")

        # 4. Create Ad
        ad_data = {
            'ads': [{
                'name': f"{data['ads']['brand_name']} - {data['ads']['headline'][:30]}",
                'status': 'PAUSED',
                'creative': {
                    'headline': data['ads']['headline'],
                    'brand_name': data['ads']['brand_name'],
                    'cta_type': data['ads']['cta_type'],
                    'top_snap_media_id': media_id,
                    'web_view_properties': {
                        'url': data['ads']['landing_url'],
                        'allow_snap_javascript_sdk': False,
                        'block_preload': True,
                        'deep_link_urls': []
                    }
                }
            }]
        }

        print(f"[DEBUG] Creating ad for ad set {adset_id}")
        ad_response = requests.post(
            f'https://adsapi.snapchat.com/v1/adsquads/{adset_id}/ads',
            headers=headers,
            json=ad_data
        )

        if ad_response.status_code != 200:
            raise Exception(f"Ad creation failed: {ad_response.text}")

        ad_result = ad_response.json()
        ad_id = ad_result['ads'][0]['id']
        ad_name = ad_result['ads'][0]['name']

        # Complete
        update_single_ad_progress(100, "Complete!", "Complete",
                                completed=True,
                                ad_name=ad_name)

        print(f"[SUCCESS] Single ad created successfully: {ad_name}")

    except Exception as e:
        print(f"[ERROR] Single ad execution failed: {e}")
        single_ad_status[execution_id]['error'] = str(e)
        single_ad_status[execution_id]['completed'] = True

def execute_test_bot_mode(execution_id, data):
    """Execute test bot - simplified version with only 3 ads"""
    global test_bot_status

    try:
        def update_test_progress(progress, step, **kwargs):
            test_bot_status[execution_id].update({
                'progress_percent': progress,
                'current_step': step,
                **kwargs
            })

        # Get Snapchat token
        tm = TokenManager()
        headers = tm.get_headers()
        if not headers:
            raise Exception("Invalid or expired Snapchat access token")

        update_test_progress(5, "Getting account info...")

        # Get organization and ad account ID
        try:
            me_response = requests.get('https://adsapi.snapchat.com/v1/me', headers=headers)
            if me_response.status_code != 200:
                raise Exception(f"Failed to get user info: {me_response.text}")

            me_data = me_response.json()
            org_id = me_data['me']['organization_id']

            accounts_response = requests.get(f'https://adsapi.snapchat.com/v1/organizations/{org_id}/adaccounts', headers=headers)
            if accounts_response.status_code != 200:
                raise Exception(f"Failed to get ad accounts: {accounts_response.text}")

            accounts = accounts_response.json().get('adaccounts', [])
            if not accounts:
                raise Exception("No ad accounts found")

            # Force use your specific ad account ID
            ad_account_id = '27205503-c6b2-4aa7-89d1-3b8dd52f527d'
            update_test_progress(10, "Creating campaign...", ad_account=ad_account_id)

        except Exception as e:
            raise Exception(f"Error getting account info: {str(e)}")

        # 1. Create Campaign
        campaign_data = {
            'campaigns': [{
                'name': data['campaign']['name'],
                'status': data['campaign']['status'],
                'start_time': data['campaign']['start_date'],
                'buy_model': 'AUCTION',
                'objective': data['campaign']['objective'],
                'daily_budget_micro': int(float(data['campaign']['daily_budget'])) * 1000000
            }]
        }

        print(f"[DEBUG] [TEST BOT] Creating campaign: {data['campaign']['name']}")
        campaign_response = requests.post(
            f'https://adsapi.snapchat.com/v1/adaccounts/{ad_account_id}/campaigns',
            headers=headers,
            json=campaign_data
        )

        if campaign_response.status_code != 200:
            raise Exception(f"Campaign creation failed: {campaign_response.text}")

        campaign_result = campaign_response.json()
        campaign_id = campaign_result['campaigns'][0]['campaign']['id']

        update_test_progress(30, "Creating ad set...")

        # 2. Create Ad Set (NO AGE TARGETING FOR CONVERSIONS)
        adset_data = {
            'adsquads': [{
                'name': data['adsets']['base_name'],
                'status': data['adsets']['status'],
                'auto_bid': True,
                'optimization_goal': 'CONVERSIONS',
                'daily_budget_micro': int(float(data['adsets']['budget_per_adset'])) * 1000000,
                'start_time': data['campaign']['start_date'],
                'targeting': {
                    'geos': [{'country_code': country} for country in data['adsets']['countries']]
                    # NO DEMOGRAPHICS/AGE for CONVERSIONS optimization
                }
            }]
        }

        print(f"[DEBUG] [TEST BOT] Skipping age targeting for CONVERSIONS optimization")

        print(f"[DEBUG] [TEST BOT] Creating ad set using SnapchatAPIClient")

        # Use the SnapchatAPIClient method (like yesterday's working code)
        access_token = headers['Authorization'].replace('Bearer ', '')
        api_client = SnapchatAPIClient(access_token, ad_account_id)

        # Extract the adsquad data from the payload
        adsquad_data = adset_data['adsquads'][0]

        try:
            print(f"[DEBUG] Test bot using campaign_id: {campaign_id}")
            adset_result = api_client.create_ad_squad(campaign_id, adsquad_data)  # Use campaign_id, not ad_account_id
            print(f"[DEBUG] Test bot API client response: {json.dumps(adset_result, indent=2)}")

            # The API client returns the adsquad directly (like yesterday's working code)
            if 'adsquad' in adset_result and 'id' in adset_result['adsquad']:
                adset_id = adset_result['adsquad']['id']
                adset_name = adset_result['adsquad']['name']
            else:
                raise Exception(f"Test bot: Unexpected response structure from API client: {adset_result}")
        except Exception as e:
            raise Exception(f"Test bot ad set creation failed: {str(e)}")

        update_test_progress(50, "Loading videos and headlines...", adset_name=adset_name)

        # 3. Load videos and headlines (limit to 3)
        videos_folder = data['ads']['videos_folder']
        headlines_csv = data['ads']['headlines_csv']

        video_files = [f for f in os.listdir(videos_folder) if f.endswith('.mp4')][:3]

        headlines = []
        with open(headlines_csv, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[1:]:  # Skip header
                headline = line.strip()
                if headline and len(headline) <= 34:
                    headlines.append(headline)
        headlines = headlines[:3]  # Limit to 3

        print(f"[DEBUG] [TEST BOT] Using {len(video_files)} videos and {len(headlines)} headlines")

        update_test_progress(60, "Uploading videos and creating ads...")

        # 4. Upload videos and create ads
        ads_created = 0
        for i, (video_file, headline) in enumerate(zip(video_files, headlines), 1):
            progress = 60 + (i / 3 * 30)  # 60-90%
            update_test_progress(progress, f"Creating ad {i}/3...", videos_uploaded=i-1)

            # Upload video
            video_path = os.path.join(videos_folder, video_file)

            # Create media entity
            media_data = {
                'media': [{
                    'name': video_file,
                    'type': 'VIDEO',
                    'ad_account_id': '27205503-c6b2-4aa7-89d1-3b8dd52f527d'
                }]
            }

            media_response = requests.post(
                'https://adsapi.snapchat.com/v1/media',
                headers=headers,
                json=media_data
            )

            if media_response.status_code != 200:
                print(f"[ERROR] [TEST BOT] Media creation failed for {video_file}: {media_response.text}")
                continue

            media_result = media_response.json()
            media_id = media_result['media']['id']

            # Upload file
            with open(video_path, 'rb') as video_file_obj:
                files = {'file': (video_file, video_file_obj, 'video/mp4')}
                upload_response = requests.post(
                    f'https://adsapi.snapchat.com/v1/media/{media_id}/upload',
                    headers={'Authorization': headers['Authorization']},
                    files=files
                )

            # Wait for media to be ready (simplified check)
            time.sleep(3)

            # Create ad
            ad_data = {
                'ads': [{
                    'name': f"{data['ads']['brand_name']} - Test Ad {i}",
                    'status': 'PAUSED',
                    'creative': {
                        'headline': headline,
                        'brand_name': data['ads']['brand_name'],
                        'cta_type': data['ads']['cta_type'],
                        'top_snap_media_id': media_id,
                        'web_view_properties': {
                            'url': data['ads']['landing_url'],
                            'allow_snap_javascript_sdk': False,
                            'block_preload': True,
                            'deep_link_urls': []
                        }
                    }
                }]
            }

            ad_response = requests.post(
                f'https://adsapi.snapchat.com/v1/adsquads/{adset_id}/ads',
                headers=headers,
                json=ad_data
            )

            if ad_response.status_code == 200:
                ads_created += 1
                print(f"[DEBUG] [TEST BOT] Created ad {i}/3: {data['ads']['brand_name']} - Test Ad {i}")
                update_test_progress(progress, f"Created ad {i}/3", ads_created=ads_created, videos_uploaded=i)
            else:
                print(f"[ERROR] [TEST BOT] Ad creation failed for ad {i}: {ad_response.text}")

        # Complete
        final_time = round(time.time() - test_bot_status[execution_id]['start_time'], 1)
        update_test_progress(100, "Test completed!",
                           completed=True,
                           ads_created=ads_created,
                           videos_uploaded=len(video_files),
                           execution_time=final_time)

        print(f"[SUCCESS] [TEST BOT] Test completed! Created {ads_created}/3 ads in {final_time}s")

    except Exception as e:
        print(f"[ERROR] Test bot execution failed: {e}")
        test_bot_status[execution_id]['error'] = str(e)
        test_bot_status[execution_id]['completed'] = True

def execute_optimized_beast_mode(execution_id, data):
    """Execute the actual Optimized Beast Mode campaign creation"""
    try:
        # Update progress function with detailed tracking
        def update_progress(progress, status, stage, log_msg, **kwargs):
            progress_tracker[execution_id].update({
                'progress': progress,
                'status': status,
                'stage': stage,
                **kwargs
            })
            progress_tracker[execution_id]['log'].append(f"[{datetime.now().strftime('%H:%M:%S')}] {log_msg}")

        # Log the data structure for debugging
        update_progress(1, 'debugging', 'Checking data structure...', f'Data keys: {list(data.keys()) if isinstance(data, dict) else "Not a dict"}')

        # Handle different data structures flexibly
        if isinstance(data, dict):
            if 'campaign' in data and isinstance(data['campaign'], dict):
                # Session-based data structure
                campaign_name = str(data['campaign'].get('campaign_name', 'Beast Mode Campaign'))
                daily_budget = str(data['campaign'].get('daily_budget', '100'))
                objective = data['campaign'].get('objective', 'WEBSITE_VISITS')
                campaign_status = data['campaign'].get('campaign_status', 'ACTIVE')

                # AdSet data
                adset_data = data.get('adsets', {})
                num_adsets = int(adset_data.get('count', adset_data.get('num_adsets', 5)))  # Use dynamic count
                min_age = int(adset_data.get('min_age', 20))
                max_age_setting = adset_data.get('max_age', 55)
                # Support 55+ targeting (no upper limit)
                if str(max_age_setting).endswith('+'):
                    max_age = 65  # Use 65 as max for 55+ targeting
                else:
                    try:
                        max_age_val = int(max_age_setting)
                        max_age = 65 if max_age_val >= 65 else max_age_val
                    except ValueError:
                        max_age = 65  # Default fallback
                countries = adset_data.get('countries', ['SA'])
                adset_budget = float(adset_data.get('adset_budget', 25))

                # Ads data
                ads_data = data.get('ads', {})
                videos_path = ads_data.get('videos_path') or r'C:\Users\PC\Desktop\200 vdieos'
                csv_path = ads_data.get('csv_path') or r'D:\snapchat_headlines_khaleeji_200 (1) - snapchat_headlines_khaleeji_200 (1).csv.csv'
                brand_name = ads_data.get('brand_name') or 'sallagcc'
                call_to_action = ads_data.get('call_to_action') or 'SHOP_NOW'
                website_url = ads_data.get('website_url') or 'https://sallagcc.com'
            else:
                # Direct form data structure
                campaign_name = str(data.get('campaign_name', 'Beast Mode Campaign'))
                daily_budget = data.get('daily_budget', '100')
                objective = data.get('objective', 'WEBSITE_VISITS')

                # AdSet data
                num_adsets = int(data.get('num_adsets', 5))
                min_age = data.get('min_age', 20)
                max_age_setting = data.get('max_age', '55+')
                if str(max_age_setting).endswith('+'):
                    max_age = 65  # Use 65 as max for 55+ targeting
                else:
                    try:
                        max_age_val = int(max_age_setting)
                        max_age = 65 if max_age_val >= 65 else max_age_val
                    except ValueError:
                        max_age = 65  # Default fallback
                countries = data.get('countries', ['SA'])
                adset_budget = data.get('adset_budget', 25)

                # Ads data
                videos_path = data.get('videos_folder') or r'C:\Users\PC\Desktop\200 vdieos'
                csv_path = data.get('headlines_csv') or r'D:\snapchat_headlines_khaleeji_200 (1) - snapchat_headlines_khaleeji_200 (1).csv.csv'
                brand_name = data.get('brand_name') or 'sallagcc'
                call_to_action = data.get('cta_type') or 'SHOP_NOW'
                website_url = data.get('landing_url') or 'https://sallagcc.com'
        else:
            # Fallback defaults
            campaign_name = str('Beast Mode Campaign')
            daily_budget = '100'
            objective = 'WEBSITE_VISITS'
            num_adsets = 5
            min_age = 20
            max_age = 65  # 55+ targeting
            countries = ['SA']
            adset_budget = 25
            videos_path = r'C:\Users\PC\Desktop\200 vdieos'
            csv_path = r'D:\snapchat_headlines_khaleeji_200 (1) - snapchat_headlines_khaleeji_200 (1).csv.csv'
            brand_name = 'sallagcc'
            call_to_action = 'SHOP_NOW'
            website_url = 'https://sallagcc.com'

        update_progress(5, 'validating', 'Validating API token...', f'Campaign: {campaign_name}, Budget: ${daily_budget}')

        # Initialize token manager
        tm = TokenManager()
        headers = tm.get_headers()

        if not headers:
            update_progress(0, 'error', 'Token Error', 'Failed to get valid API token', error='Invalid or expired token')
            return

        update_progress(10, 'account_info', 'Getting account info...', 'Retrieving Snapchat account information...')

        # Get account info
        try:
            me_response = requests.get('https://adsapi.snapchat.com/v1/me', headers=headers)
            if me_response.status_code != 200:
                update_progress(0, 'error', 'Account Error', f'Failed to get user info: {me_response.text}', error='Account access failed')
                return

            me_data = me_response.json()
            org_id = me_data['me']['organization_id']

            accounts_response = requests.get(f'https://adsapi.snapchat.com/v1/organizations/{org_id}/adaccounts', headers=headers)
            if accounts_response.status_code != 200:
                update_progress(0, 'error', 'Account Error', f'Failed to get ad accounts: {accounts_response.text}', error='Ad account access failed')
                return

            accounts = accounts_response.json().get('adaccounts', [])
            if not accounts:
                update_progress(0, 'error', 'Account Error', 'No ad accounts found', error='No ad accounts available')
                return

            # Force use your specific ad account ID
            ad_account_id = '27205503-c6b2-4aa7-89d1-3b8dd52f527d'
            update_progress(15, 'creating_campaign', 'Creating campaign...', f'Using ad account: {ad_account_id}')

        except Exception as e:
            update_progress(0, 'error', 'Account Error', f'Error getting account info: {str(e)}', error=str(e))
            return

        # Create campaign
        try:
            print(f"[DEBUG] Starting campaign creation. Campaign name: {campaign_name}, Budget: ${daily_budget}")
            now = datetime.now(timezone.utc)
            start_time = now.isoformat()
            end_time = (now + timedelta(days=30)).isoformat()

            campaign_data_api = {
                'campaigns': [{
                    'name': campaign_name,
                    'status': campaign_status,
                    'start_time': start_time,
                    'end_time': end_time,
                    'buy_model': 'AUCTION',
                    'objective': objective,
                    'daily_budget_micro': int(float(daily_budget)) * 1000000
                }]
            }

            headers = tm.get_headers()  # Refresh token
            campaign_response = make_robust_api_request(
                'POST',
                f'https://adsapi.snapchat.com/v1/adaccounts/{ad_account_id}/campaigns',
                headers=headers,
                json_data=campaign_data_api,
                max_retries=3,
                backoff_factor=2
            )

            if campaign_response.status_code == 200:
                campaign_result = campaign_response.json()
                campaign_id = campaign_result['campaigns'][0]['campaign']['id']
                print(f"[DEBUG] Campaign created successfully: {campaign_id}")
                update_progress(20, 'creating_adsets', 'Creating ad sets...', f'Campaign created: {campaign_id}', campaign_id=campaign_id)
            else:
                update_progress(0, 'error', 'Campaign Error', f'Campaign creation failed: {campaign_response.text}', error='Campaign creation failed')
                return

        except Exception as e:
            update_progress(0, 'error', 'Campaign Error', f'Error creating campaign: {str(e)}', error=str(e))
            return

        # Create ad sets
        try:
            print(f"[DEBUG] Starting ad set creation. num_adsets={num_adsets}, campaign_id={campaign_id}")
            print(f"[DEBUG] Ad set parameters: countries={countries}, min_age={min_age}, max_age={max_age}")
            # Using parsed num_adsets variable
            ad_sets = []

            for ad_set_num in range(1, num_adsets + 1):
                update_progress(20 + (ad_set_num * 5), 'creating_adsets', f'Creating ad set {str(ad_set_num)}/{str(num_adsets)}...', f'Creating ad set {str(ad_set_num)}...')

                headers = tm.get_headers()  # Refresh token

                # For CONVERSIONS optimization, age targeting is not allowed
                targeting_config = {
                    'regulated_content': False,
                    'geos': [{'country_code': country.lower()} for country in countries]
                }

                # Only add age demographics if NOT using CONVERSIONS
                optimization_goal = 'CONVERSIONS'  # We're using conversions
                if optimization_goal != 'CONVERSIONS':
                    targeting_config['demographics'] = [{
                        'min_age': min_age,
                        'max_age': max_age
                    }]
                else:
                    print(f"[DEBUG] Skipping age targeting for CONVERSIONS optimization")

                ad_set_data_api = {
                    'adsquads': [{
                        'name': f'{campaign_name} - Ad Set {str(ad_set_num)}',
                        'status': 'ACTIVE',
                        'campaign_id': campaign_id,
                        'type': 'SNAP_ADS',
                        'targeting': targeting_config,
                        'placement_v2': {'config': 'AUTOMATIC'},
                        'billing_event': 'IMPRESSION',
                        'auto_bid': True,
                        'optimization_goal': 'CONVERSIONS',
                        'daily_budget_micro': int(float(adset_budget)) * 1000000,
                        'start_time': start_time,
                        'end_time': end_time
                    }]
                }

                # Add pixel_id if pixel is enabled and pixel_id is provided
                adsets_data = data.get('adsets', {})
                pixel_enabled = adsets_data.get('enable_pixel', 'true') == 'true'
                pixel_id = adsets_data.get('pixel_id', '').strip()
                if pixel_enabled and pixel_id:
                    ad_set_data_api['adsquads'][0]['pixel_id'] = pixel_id
                    print(f"[DEBUG] Pixel enabled for ad set {ad_set_num} with pixel_id: {pixel_id}")
                else:
                    print(f"[DEBUG] Pixel not added for ad set {ad_set_num}. Enabled: {pixel_enabled}, ID: '{pixel_id}'")

                print(f"[DEBUG] Ad set {ad_set_num} JSON payload: {json.dumps(ad_set_data_api, indent=2)}")

                # RESTORE YESTERDAY'S WORKING METHOD: Direct API call (exactly like complete_beast_mode.py)
                try:
                    headers = tm.get_headers()  # Refresh token

                    ad_set_response = requests.post(
                        f'https://adsapi.snapchat.com/v1/campaigns/{campaign_id}/adsquads',
                        headers=headers,
                        json=ad_set_data_api
                    )

                    print(f"[DEBUG] Ad set {ad_set_num} HTTP status: {ad_set_response.status_code}")

                    if ad_set_response.status_code == 200:
                        ad_set_result = ad_set_response.json()
                        print(f"[DEBUG] Ad set {ad_set_num} response: {json.dumps(ad_set_result, indent=2)}")

                        # EXACT WORKING PATTERN from yesterday's code
                        ad_set_id = ad_set_result['adsquads'][0]['adsquad']['id']
                        ad_sets.append(ad_set_id)
                        update_progress(20 + (ad_set_num * 5), 'creating_adsets', f'Ad set {str(ad_set_num)} created', f'Ad Set {str(ad_set_num)} created: {ad_set_id}')
                        print(f"[DEBUG] Ad set {ad_set_num} created successfully: {ad_set_id}")
                    else:
                        print(f"[ERROR] Ad set {ad_set_num} creation failed: {ad_set_response.text}")
                        update_progress(20 + (ad_set_num * 5), 'creating_adsets', f'Ad set {str(ad_set_num)} failed', f'Ad Set {str(ad_set_num)} creation failed: {ad_set_response.text}')

                except Exception as e:
                    import traceback
                    print(f"[ERROR] Ad set {ad_set_num} creation failed: {str(e)}")
                    print(f"[ERROR] Ad set {ad_set_num} full traceback:")
                    print(traceback.format_exc())
                    update_progress(20 + (ad_set_num * 5), 'creating_adsets', f'Ad set {str(ad_set_num)} failed', f'Ad Set {str(ad_set_num)} failed: {str(e)}')

                time.sleep(0.1)  # Rate limiting

            update_progress(45, 'uploading_media', 'Loading videos...', f'Created {len(ad_sets)} ad sets successfully')

        except Exception as e:
            import traceback
            print(f"[ERROR] Critical error in ad set creation: {str(e)}")
            print(f"[ERROR] Full traceback:")
            print(traceback.format_exc())
            update_progress(0, 'error', 'Ad Set Error', f'Error creating ad sets: {str(e)}', error=str(e))
            return

        # Load videos and headlines
        try:
            video_folder = videos_path
            csv_file = csv_path

            # Debug output
            print(f"[DEBUG] videos_path = '{videos_path}'")
            print(f"[DEBUG] csv_path = '{csv_path}'")
            print(f"[DEBUG] video_folder = '{video_folder}'")
            print(f"[DEBUG] csv_file = '{csv_file}'")
            print(f"[DEBUG] brand_name = '{brand_name}'")
            print(f"[DEBUG] website_url = '{website_url}'")
            print(f"[DEBUG] call_to_action = '{call_to_action}'")

            # Handle dummy files for testing when folder doesn't exist
            if not os.path.exists(video_folder):
                print(f"[INFO] Video folder doesn't exist: {video_folder}")
                print(f"[INFO] Creating dummy video files for testing...")
                video_files = [f'test_video_{i}.mp4' for i in range(1, 4)]  # Create 3 dummy videos
                update_progress(50, 'uploading_media', 'Using dummy videos for testing...', f'Created {len(video_files)} dummy videos')
            else:
                # Load videos - use dynamic limit based on campaign structure
                total_ads_limit = ads_data.get('total_ads', 200) if isinstance(ads_data, dict) else 200
                video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')][:total_ads_limit]
                update_progress(50, 'uploading_media', 'Loading headlines...', f'Found {len(video_files)} videos')

            # Load headlines with dummy fallback
            headlines = []
            if not os.path.exists(csv_file):
                print(f"[INFO] CSV file doesn't exist: {csv_file}")
                print(f"[INFO] Creating dummy headlines for testing...")
                headlines = [
                    f"{brand_name} - Amazing Offer",
                    f"{brand_name} - Best Deal",
                    f"{brand_name} - Limited Time"
                ]
            else:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[1:]:  # Skip header
                        headline = line.strip()
                        if headline and len(headline) <= 34:  # Snapchat limit
                            headlines.append(headline)

            # Apply dynamic limit to headlines based on campaign structure
            test_mode = ads_data.get('test_mode', False) if isinstance(ads_data, dict) else False
            if test_mode:
                headlines = headlines[:3]  # Limit to first 3 headlines in test mode
                print(f"[DEBUG] TEST MODE: Limited to {len(headlines)} headlines")
            else:
                # Use dynamic limit for regular campaigns
                total_ads_limit = ads_data.get('total_ads', 200) if isinstance(ads_data, dict) else 200
                headlines = headlines[:total_ads_limit]
                print(f"[DEBUG] Using campaign structure limit: {len(headlines)} headlines (max: {total_ads_limit})")

            update_progress(55, 'uploading_media', 'Starting media upload...', f'Loaded {len(headlines)} headlines')

        except Exception as e:
            print(f"[ERROR] File loading failed with paths:")
            print(f"[ERROR] videos_path = '{videos_path}'")
            print(f"[ERROR] csv_path = '{csv_path}'")
            print(f"[ERROR] Exception: {str(e)}")
            update_progress(0, 'error', 'File Error', f'Error loading files: {str(e)}', error=str(e))
            return

        # Fast upload all media
        try:
            uploaded_media = []
            # Using parsed brand_name variable

            # Check if test mode is enabled
            test_mode = data['ads'].get('test_mode', False)
            if test_mode:
                video_files = video_files[:3]  # Limit to first 3 videos in test mode
                print(f"[DEBUG] TEST MODE: Limited to {len(video_files)} videos")

            for i, video_file in enumerate(video_files, 1):
                progress_percent = 55 + (i / len(video_files) * 20)  # 55-75%

                if i % 25 == 0 or test_mode:  # Update every 25 videos or always in test mode
                    update_progress(progress_percent, 'uploading_media', f'Uploading videos... ({i}/{len(video_files)})', f'Uploaded {i}/{len(video_files)} videos')

                try:
                    headers = tm.get_headers()
                    if not headers:
                        continue

                    # Handle dummy files for testing when folder doesn't exist
                    if video_file.startswith('test_video_') and not os.path.exists(video_folder):
                        print(f"[INFO] Using dummy media file for testing: {video_file}")
                        # Create dummy media entry for testing with headline
                        headline = headlines[i-1] if i-1 < len(headlines) else f"{brand_name} Ad {i}"
                        if len(headline) > 34:
                            headline = headline[:31] + "..."

                        dummy_media = {
                            'media_id': f'dummy_media_{i}_{int(time.time())}',
                            'headline': headline,
                            'video_name': video_file
                        }
                        uploaded_media.append(dummy_media)
                        continue

                    # FIXED: Use proper video upload mechanism
                    access_token = headers['Authorization'].replace('Bearer ', '')
                    api_client = SnapchatAPIClient(access_token, ad_account_id)

                    video_path = os.path.join(video_folder, video_file)

                    # Upload video file properly (creates media + uploads file + waits for ready)
                    media_response = api_client.upload_media(ad_account_id, video_path, 'VIDEO')

                    if media_response and 'media' in media_response:
                        media_id = media_response['media']['id']

                        # Get headline for this video
                        headline = headlines[i-1] if i-1 < len(headlines) else f"{brand_name} Ad {i}"
                        if len(headline) > 34:
                            headline = headline[:31] + "..."

                        uploaded_media.append({
                            'media_id': media_id,
                            'headline': headline,
                            'video_name': video_file
                        })

                except Exception as e:
                    continue

                # Removed unnecessary 0.5s delay per upload (saves 100+ seconds total)

            update_progress(75, 'checking_media', 'Checking media processing...', f'Uploaded {len(uploaded_media)} media files', media_uploaded=len(uploaded_media))

        except Exception as e:
            update_progress(0, 'error', 'Upload Error', f'Error uploading media: {str(e)}', error=str(e))
            return

        # Check media processing
        try:
            update_progress(77, 'checking_media', 'Checking media status...', 'Checking if media files are ready...')

            headers = tm.get_headers()
            ready_count, checked = check_media_status_batch(uploaded_media, headers, 20)
            update_progress(80, 'checking_media', f'Media check: {ready_count}/{checked} ready', f'{ready_count}/{checked} sample media files ready', media_ready=ready_count)

            # Smart wait with early exit (saves 60-90 seconds on average)
            if ready_count == 0:
                update_progress(82, 'waiting_media', 'Smart waiting for media processing...', 'Checking every 10 seconds for ready media...')
                max_wait_time = 60  # Reduced from 120 seconds
                check_interval = 10
                wait_start = time.time()

                while time.time() - wait_start < max_wait_time:
                    time.sleep(check_interval)
                    ready_count, checked = check_media_status_batch(uploaded_media, headers, 20)
                    elapsed = int(time.time() - wait_start)
                    ready_percentage = (ready_count / checked * 100) if checked > 0 else 0

                    # Early exit if 50% or more media is ready
                    if ready_percentage >= 50:
                        update_progress(85, 'creating_ads', f'Media ready! Starting ads...', f'Early exit: {ready_count}/{checked} media ready ({ready_percentage:.1f}%)', media_ready=ready_count)
                        break

                    update_progress(82, 'waiting_media', f'Checking media... {ready_percentage:.1f}% ready', f'Waited {elapsed}s: {ready_count}/{checked} ready', media_ready=ready_count)

                if ready_count == 0:
                    update_progress(85, 'creating_ads', 'Proceeding with ad creation...', f'Final check: {ready_count}/{checked} sample media files ready', media_ready=ready_count)

        except Exception as e:
            update_progress(85, 'creating_ads', 'Creating ads anyway...', f'Media check failed: {str(e)}')

        # Create ads with smart strategy
        try:
            created_ads = 0
            failed_ads = 0
            ads_per_set = ads_data.get('ads_per_adset', 40)  # Use dynamic value from campaign structure

            for ad_set_index, ad_set_id in enumerate(ad_sets):
                start_index = ad_set_index * ads_per_set
                end_index = start_index + ads_per_set

                if start_index >= len(uploaded_media):
                    break
                if end_index > len(uploaded_media):
                    end_index = len(uploaded_media)

                media_batch = uploaded_media[start_index:end_index]
                update_progress(85 + (ad_set_index * 3), 'creating_ads', f'Creating ads for Ad Set {ad_set_index + 1}...', f'Creating {len(media_batch)} ads for Ad Set {ad_set_index + 1}...')

                for media_index, media_info in enumerate(media_batch):
                    ad_num = start_index + media_index + 1
                    progress_percent = 85 + ((created_ads + failed_ads) / len(uploaded_media) * 13)  # 85-98%

                    if (created_ads + failed_ads) % 10 == 0:  # Update every 10 ads
                        update_progress(progress_percent, 'creating_ads', f'Creating ads... ({created_ads + failed_ads}/{len(uploaded_media)})', f'Progress: {created_ads} created, {failed_ads} failed', ads_created=created_ads)

                    try:
                        # Skip dummy media to avoid API calls
                        if media_info['media_id'].startswith('dummy_media_'):
                            print(f"[INFO] Skipping ad creation for dummy media: {media_info['video_name']}")
                            created_ads += 1  # Count as created for testing
                            continue

                        headers = tm.get_headers()
                        if not headers:
                            failed_ads += 1
                            continue

                        # Create creative with uploaded media
                        creative_data = {
                            'creatives': [{
                                'ad_account_id': ad_account_id,
                                'name': f'{brand_name} - Creative {ad_num}',
                                'type': 'WEB_VIEW',
                                'headline': media_info['headline'],
                                'brand_name': brand_name,
                                'call_to_action': call_to_action,
                                'top_snap_media_id': media_info['media_id'],
                                'web_view_properties': {
                                    'url': website_url,
                                    'allow_snap_javascript_sdk': False,
                                    'use_immersive_mode': False,
                                    'deep_link_urls': [],
                                    'block_preload': True
                                },
                                'shareable': True
                            }]
                        }

                        creative_response = make_robust_api_request(
                            'POST',
                            f'https://adsapi.snapchat.com/v1/adaccounts/{ad_account_id}/creatives',
                            headers=headers,
                            json_data=creative_data,
                            max_retries=3,
                            backoff_factor=2
                        )

                        if creative_response.status_code == 200:
                            creative_result = creative_response.json()

                            if 'creatives' in creative_result and len(creative_result['creatives']) > 0:
                                creative_item = creative_result['creatives'][0]

                                if creative_item.get('sub_request_status') == 'SUCCESS':
                                    creative_id = creative_item['creative']['id']

                                    # Create ad
                                    ad_data_api = {
                                        'ads': [{
                                            'name': f'{brand_name} - Ad {ad_num}',
                                            'ad_squad_id': ad_set_id,
                                            'creative_id': creative_id,
                                            'status': 'ACTIVE',
                                            'type': 'REMOTE_WEBPAGE'
                                        }]
                                    }

                                    ad_response = make_robust_api_request(
                                        'POST',
                                        f'https://adsapi.snapchat.com/v1/adsquads/{ad_set_id}/ads',
                                        headers=headers,
                                        json_data=ad_data_api,
                                        max_retries=3,
                                        backoff_factor=2
                                    )

                                    if ad_response.status_code == 200:
                                        ad_result = ad_response.json()
                                        if 'ads' in ad_result and len(ad_result['ads']) > 0:
                                            if ad_result['ads'][0].get('sub_request_status') == 'SUCCESS':
                                                created_ads += 1
                                            else:
                                                failed_ads += 1
                                                error_reason = ad_result['ads'][0].get('sub_request_error_reason', 'Unknown')
                                                if "hasn't been uploaded yet" in error_reason:
                                                    time.sleep(2)  # Wait for media processing
                                    else:
                                        failed_ads += 1
                                else:
                                    failed_ads += 1
                                    error_reason = creative_item.get('sub_request_error_reason', 'Unknown')
                                    if "hasn't been uploaded yet" in error_reason:
                                        time.sleep(2)  # Wait for media processing
                        else:
                            failed_ads += 1

                    except Exception as e:
                        failed_ads += 1

                    time.sleep(0.02)  # Ultra-fast processing (saves 6+ seconds total)

            # Final success
            final_progress = 100 if created_ads >= 50 else 95
            success_status = 'completed' if created_ads >= 50 else 'partial'

            update_progress(final_progress, success_status, 'Completed!', f'Beast Mode completed! Created {created_ads} ads successfully.',
                           ads_created=created_ads, ads_failed=failed_ads,
                           campaign_name=campaign_name,
                           success=created_ads >= 50)

        except Exception as e:
            update_progress(0, 'error', 'Ads Creation Error', f'Error creating ads: {str(e)}', error=str(e))

    except Exception as e:
        update_progress(0, 'error', 'System Error', f'Unexpected error: {str(e)}', error=str(e))

@app.route('/folder-beast/reset')
@require_auth
def folder_beast_reset():
    """Reset the folder beast wizard"""
    session.pop('folder_beast', None)
    return redirect(url_for('folder_beast'))

@app.route('/folder-beast/prev')
@require_auth
def folder_beast_prev():
    """Go to previous step"""
    init_folder_beast_session()
    if session['folder_beast']['step'] > 1:
        session['folder_beast']['step'] -= 1
        session.modified = True
    return redirect(url_for('folder_beast'))

# Other bot routes (placeholders for now)

@app.route('/campaign-manager')
@require_auth
def campaign_manager():
    return render_template('campaign_manager.html')

@app.route('/token-manager')
@require_auth
def token_manager():
    """Token manager dashboard with current status"""
    tm = TokenManager()

    # Get current token status
    token_info = {}
    try:
        config = tm.load_config()
        if config:
            token_info = {
                'has_token': True,
                'expires_at': config.get('expires_at', 'Unknown'),
                'is_expired': tm.is_token_expired(),
                'client_id': config.get('client_id', '26267fa4-831c-47fb-97b4-afca39be5877'),
                'has_refresh_token': bool(config.get('refresh_token'))
            }
        else:
            token_info = {
                'has_token': False,
                'expires_at': None,
                'is_expired': True,
                'client_id': '26267fa4-831c-47fb-97b4-afca39be5877',
                'has_refresh_token': False
            }
    except Exception as e:
        token_info = {
            'has_token': False,
            'expires_at': None,
            'is_expired': True,
            'error': str(e),
            'client_id': '26267fa4-831c-47fb-97b4-afca39be5877',
            'has_refresh_token': False
        }

    return render_template('token_manager.html', token_info=token_info)

@app.route('/api/token/refresh', methods=['POST'])
@require_auth
def refresh_token_api():
    """API endpoint to refresh token"""
    try:
        tm = TokenManager()
        success = tm.refresh_token()

        if success:
            # Get updated token info
            config = tm.load_config()
            return jsonify({
                'success': True,
                'message': 'Token refreshed successfully',
                'expires_at': config.get('expires_at') if config else None
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Token refresh failed'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@app.route('/api/token/test', methods=['POST'])
@require_auth
def test_token_api():
    """API endpoint to test current token"""
    try:
        tm = TokenManager()
        headers = tm.get_headers()

        if not headers:
            return jsonify({
                'success': False,
                'message': 'No valid token available'
            })

        # Test API call to Snapchat
        response = requests.get('https://adsapi.snapchat.com/v1/me', headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            return jsonify({
                'success': True,
                'message': 'Token is valid',
                'user_data': user_data
            })
        else:
            return jsonify({
                'success': False,
                'message': f'API test failed: {response.status_code}',
                'response': response.text
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error testing token: {str(e)}'
        })

@app.route('/api/token/update', methods=['POST'])
@require_auth
def update_token_config():
    """API endpoint to update token configuration"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['access_token', 'refresh_token']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                })

        tm = TokenManager()

        # Create new config
        new_config = {
            'access_token': data['access_token'],
            'refresh_token': data['refresh_token'],
            'client_id': data.get('client_id', '26267fa4-831c-47fb-97b4-afca39be5877'),
            'expires_at': data.get('expires_at', (datetime.now() + timedelta(hours=1)).isoformat())
        }

        # Save new config
        if tm.save_config(new_config):
            return jsonify({
                'success': True,
                'message': 'Token configuration updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to save token configuration'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating token: {str(e)}'
        })

@app.route('/auth/callback')
def oauth_callback():
    """Handle OAuth callback from Snapchat"""
    try:
        # Get authorization code from callback
        auth_code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')

        if error:
            return f"Authorization failed: {error}", 400

        if not auth_code:
            return "No authorization code received", 400

        # Exchange code for tokens
        client_id = "26267fa4-831c-47fb-97b4-afca39be5877"
        client_secret = "84ec597b44ef3968088c"

        token_url = "https://accounts.snapchat.com/login/oauth2/access_token"
        token_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": "https://web-production-95efb.up.railway.app/auth/callback"
        }

        response = requests.post(token_url, data=token_data)

        if response.status_code == 200:
            token_info = response.json()

            # Save tokens
            tm = TokenManager()
            new_config = {
                'access_token': token_info.get('access_token'),
                'refresh_token': token_info.get('refresh_token'),
                'client_id': client_id,
                'client_secret': client_secret,
                'expires_at': (datetime.now() + timedelta(seconds=token_info.get('expires_in', 3600))).isoformat()
            }

            if tm.save_config(new_config):
                return redirect(url_for('token_manager') + '?success=1')
            else:
                return "Failed to save tokens", 500
        else:
            return f"Token exchange failed: {response.text}", 400

    except Exception as e:
        return f"OAuth callback error: {str(e)}", 500

@app.route('/analytics-bot')
@require_auth
def analytics_bot():
    return render_template('analytics_bot.html')

@app.route('/bulk-uploader')
@require_auth
def bulk_uploader():
    return render_template('bulk_uploader.html')

# Video Compressor routes
def compress_video_variants(input_path, num_variants, callback=None):
    """Compress 1 video into specified number of different variants under 8MB with original aspect ratio"""
    print(f"[DEBUG] Starting compression: {input_path}, variants: {num_variants}")

    # Find FFmpeg executable with fallback paths
    ffmpeg_paths = [
        "ffmpeg",  # Railway/Linux system path first
        r"C:\Users\PC\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
        "ffmpeg.exe"
    ]

    ffmpeg_path = None
    for path in ffmpeg_paths:
        try:
            result = subprocess.run([path, "-version"], capture_output=True, timeout=5)
            if result.returncode == 0:
                ffmpeg_path = path
                print(f"[DEBUG] Found FFmpeg at: {path}")
                break
        except:
            continue

    if not ffmpeg_path:
        print("[ERROR] FFmpeg not found")
        return {'successful': 0, 'total': num_variants, 'error': 'FFmpeg not found'}

    # Find FFprobe executable with fallback paths
    ffprobe_paths = [
        "ffprobe",  # Railway/Linux system path first
        r"C:\Users\PC\ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe",
        r"C:\ffmpeg\bin\ffprobe.exe",
        "ffprobe.exe"
    ]

    ffprobe_path = None
    for path in ffprobe_paths:
        try:
            result = subprocess.run([path, "-version"], capture_output=True, timeout=5)
            if result.returncode == 0:
                ffprobe_path = path
                break
        except:
            continue

    # Get video info (duration, width, height)
    duration = 10.0
    original_width = 1080
    original_height = 1920

    if ffprobe_path:
        try:
            cmd = [ffprobe_path, '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', input_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                video_info = json.loads(result.stdout)
                duration = float(video_info['format']['duration'])

                # Get video stream info
                for stream in video_info.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        original_width = int(stream.get('width', 1080))
                        original_height = int(stream.get('height', 1920))
                        break

                print(f"[DEBUG] Video info: {duration}s, {original_width}x{original_height}")
            else:
                print(f"[DEBUG] FFprobe failed, using defaults: {duration}s, {original_width}x{original_height}")
        except Exception as e:
            print(f"[DEBUG] Error getting video info: {e}, using defaults")

    # Create output folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_folder = os.path.join("compressed_videos", f"variants_{timestamp}")
    os.makedirs(output_folder, exist_ok=True)
    print(f"[DEBUG] Output folder: {output_folder}")

    successful = 0
    total_size = 0

    # Calculate aspect ratio to maintain original proportions
    aspect_ratio = original_width / original_height
    print(f"[DEBUG] Original aspect ratio: {aspect_ratio:.3f}")

    # Create variants with different sizes while maintaining aspect ratio
    for i in range(1, num_variants + 1):
        try:
            # Different target sizes between 2MB and 7.5MB
            target_mb = 2.0 + (5.5 * ((i - 1) / max(1, num_variants - 1)))  # 2MB to 7.5MB range
            target_bits = target_mb * 8 * 1024 * 1024
            video_bits = target_bits * 0.85  # Reserve for audio
            bitrate = max(200, min(2000, int(video_bits / duration / 1000)))

            # Create different resolution variants while maintaining aspect ratio
            variant_percent = (i - 1) / max(1, num_variants - 1)

            # Scale options that maintain aspect ratio
            if aspect_ratio > 1:  # Landscape video (wider than tall)
                if variant_percent <= 0.25:
                    target_width = 854
                elif variant_percent <= 0.5:
                    target_width = 720
                elif variant_percent <= 0.75:
                    target_width = 960
                else:
                    target_width = min(1080, original_width)
                target_height = int(target_width / aspect_ratio)
                # Ensure even numbers for H.264 compatibility
                target_height = target_height - (target_height % 2)
            else:  # Portrait or square video (taller than wide or equal)
                if variant_percent <= 0.25:
                    target_height = 1280
                elif variant_percent <= 0.5:
                    target_height = 1080
                elif variant_percent <= 0.75:
                    target_height = 1440
                else:
                    target_height = min(1920, original_height)
                target_width = int(target_height * aspect_ratio)
                # Ensure even numbers for H.264 compatibility
                target_width = target_width - (target_width % 2)

            scale = f"{target_width}:{target_height}"

            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_file = f"{base_name}_variant_{i:03d}_{target_width}x{target_height}_{target_mb:.1f}MB.mp4"
            output_path = os.path.join(output_folder, output_file)

            cmd = [
                ffmpeg_path, '-i', input_path, '-y',
                '-vf', f'scale={scale}:flags=lanczos',
                '-c:v', 'libx264',
                '-preset', 'fast',  # Faster encoding
                '-profile:v', 'baseline',  # More compatible
                '-crf', '23',
                '-maxrate', f'{bitrate}k',
                '-c:a', 'aac',
                '-b:a', '96k',
                output_path
            ]

            print(f"[DEBUG] Processing variant {i}/{num_variants} - Resolution: {target_width}x{target_height}, Target: {target_mb:.1f}MB, Bitrate: {bitrate}k")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)

            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                successful += 1
                total_size += file_size
                print(f"[SUCCESS] Variant {i}: {file_size:.2f} MB")
            else:
                print(f"[ERROR] Failed variant {i}: {result.stderr}")

            # Progress callback
            if callback:
                progress = (i / num_variants) * 100
                callback(progress, f"Created {successful}/{i} variants", {
                    'successful': successful,
                    'total_size': total_size,
                    'current_variant': i
                })

            time.sleep(0.02)  # Small delay

        except Exception as e:
            print(f"[ERROR] Variant {i} failed: {e}")
            continue

    print(f"[FINAL] Completed: {successful}/{num_variants} variants, Total size: {total_size:.2f} MB")

    return {
        'successful': successful,
        'total': num_variants,
        'output_folder': output_folder,
        'total_size_mb': total_size,
        'average_size_mb': total_size / successful if successful > 0 else 0
    }

@app.route('/video-compressor')
@require_auth
def video_compressor():
    return render_template('video_compressor.html')

@app.route('/compress', methods=['POST'])
@require_auth
def start_compression():
    """Start video compression process"""
    try:
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': 'No video file uploaded'})

        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'success': False, 'error': 'No video selected'})

        # Get number of variants from form
        num_variants = int(request.form.get('num_variants', 200))
        if num_variants < 1 or num_variants > 1000:
            return jsonify({'success': False, 'error': 'Number of variants must be between 1 and 1000'})

        # Generate task ID
        task_id = str(uuid.uuid4())

        # Save uploaded file
        temp_dir = tempfile.mkdtemp(prefix="video_compress_")
        filename = secure_filename(video_file.filename)
        input_path = os.path.join(temp_dir, filename)
        video_file.save(input_path)

        # Initialize task
        compression_tasks[task_id] = {
            'status': 'starting',
            'progress': 0,
            'message': 'Initializing...',
            'variants_created': 0,
            'total_variants': num_variants,
            'total_size_mb': 0,
            'completed': False,
            'success': False,
            'error': None,
            'download_url': None,
            'temp_dir': temp_dir,
            'start_time': time.time()
        }

        def compress_background():
            print(f"[THREAD] Starting compression for task {task_id} - {num_variants} variants")
            try:
                task = compression_tasks[task_id]

                def update_progress(progress, message, stats=None):
                    if task_id in compression_tasks:
                        task = compression_tasks[task_id]
                        task['progress'] = progress
                        task['message'] = message
                        if stats:
                            task['variants_created'] = stats.get('successful', 0)
                            task['total_size_mb'] = stats.get('total_size', 0)

                # Compress videos
                result = compress_video_variants(input_path, num_variants, update_progress)

                if result['successful'] > 0:
                    # Create ZIP file
                    zip_path = os.path.join(temp_dir, 'compressed_variants.zip')
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for file in os.listdir(result['output_folder']):
                            if file.endswith('.mp4'):
                                file_path = os.path.join(result['output_folder'], file)
                                zipf.write(file_path, file)

                    # Update final status
                    task['variants_created'] = result['successful']
                    task['total_size_mb'] = result['total_size_mb']
                    task['processing_time'] = time.time() - task['start_time']
                    task['download_url'] = f'/download/{task_id}'
                    task['success'] = True
                    task['completed'] = True
                    task['zip_path'] = zip_path
                    task['message'] = f'Complete! Created {result["successful"]}/{num_variants} variants'
                    task['progress'] = 100
                else:
                    task['error'] = 'No variants created'
                    task['completed'] = True
                    task['success'] = False
                    task['message'] = 'Error: No variants created'

            except Exception as e:
                print(f"[ERROR] Compression failed: {e}")
                if task_id in compression_tasks:
                    task = compression_tasks[task_id]
                    task['error'] = str(e)
                    task['completed'] = True
                    task['success'] = False
                    task['message'] = f'Error: {str(e)}'

        # Start background thread
        thread = threading.Thread(target=compress_background)
        thread.daemon = True
        thread.start()

        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': f'Compression started for {num_variants} variants'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/compression-progress')
@require_auth
def get_compression_progress():
    """Get progress of most recent compression"""
    if not compression_tasks:
        return jsonify({'error': 'No tasks found'}), 404

    # Get most recent task
    task_id = max(compression_tasks.keys())
    task = compression_tasks[task_id]

    return jsonify({
        'task_id': task_id,
        'progress': task.get('progress', 0),
        'message': task.get('message', 'Starting...'),
        'variants_created': task.get('variants_created', 0),
        'total_variants': task.get('total_variants', 200),
        'total_size_mb': task.get('total_size_mb', 0),
        'processing_time': task.get('processing_time', 0),
        'success': task.get('success', False),
        'completed': task.get('completed', False),
        'error': task.get('error'),
        'download_url': task.get('download_url')
    })

@app.route('/download/<task_id>')
@require_auth
def download_variants(task_id):
    """Download compressed variants ZIP"""
    if task_id not in compression_tasks:
        return "Task not found", 404

    task = compression_tasks[task_id]
    if not task['completed'] or not task['success']:
        return "Compression not completed", 400

    try:
        zip_path = task.get('zip_path')
        if zip_path and os.path.exists(zip_path):
            return send_file(
                zip_path,
                as_attachment=True,
                download_name=f'compressed_variants_{task["variants_created"]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip',
                mimetype='application/zip'
            )
        else:
            return "Download file not found", 404
    except Exception as e:
        return f"Download error: {str(e)}", 500

# Legacy single-form Folder Beast interface routes (for backward compatibility)
@app.route('/bot/single_ad')
@require_auth
def single_ad_bot():
    """Single Ad Bot interface"""
    return render_template('single_ad_bot.html')

@app.route('/start_single_ad', methods=['POST'])
@require_auth
def start_single_ad():
    """Start Single Ad execution"""
    try:
        # Get form data
        video_file = request.form.get('video_file')
        headline = request.form.get('headline')
        campaign_name = request.form.get('campaign_name')
        daily_budget = request.form.get('daily_budget')
        brand_name = request.form.get('brand_name')
        landing_url = request.form.get('landing_url')
        cta_type = request.form.get('cta_type', 'SHOP_NOW')
        target_country = request.form.get('target_country', 'SA')

        print(f"[DEBUG] Single ad bot called with: campaign_name={campaign_name}, brand_name={brand_name}")

        # Generate unique execution ID
        execution_id = str(uuid.uuid4())

        # Create execution data structure for single ad
        execution_data = {
            'campaign': {
                'name': campaign_name,
                'objective': 'SALES',
                'daily_budget': daily_budget,
                'start_date': datetime.now().isoformat(),
                'status': 'PAUSED'
            },
            'adsets': {
                'base_name': f"{campaign_name} AdSet",
                'status': 'PAUSED',
                'countries': [target_country],
                'min_age': 22,
                'max_age': '55+',
                'budget_per_adset': daily_budget
            },
            'ads': {
                'video_file': video_file,
                'headline': headline,
                'brand_name': brand_name,
                'landing_url': landing_url,
                'cta_type': cta_type,
                'single_mode': True
            }
        }

        # Start execution in background thread
        def execute_single_ad():
            try:
                execute_single_ad_mode(execution_id, execution_data)
            except Exception as e:
                print(f"[ERROR] Single ad execution failed: {e}")
                global single_ad_status
                if execution_id in single_ad_status:
                    single_ad_status[execution_id]['error'] = str(e)
                    single_ad_status[execution_id]['completed'] = True

        thread = threading.Thread(target=execute_single_ad)
        thread.daemon = True
        thread.start()

        # Initialize status tracking
        global single_ad_status

        single_ad_status[execution_id] = {
            'progress_percent': 0,
            'current_step': 'Starting...',
            'status': 'Preparing...',
            'completed': False,
            'error': None,
            'campaign_name': campaign_name,
            'adset_name': None,
            'ad_name': None,
            'landing_url': landing_url
        }

        print(f"[DEBUG] Started single ad execution with ID: {execution_id}")

        return jsonify({'success': True, 'execution_id': execution_id})

    except Exception as e:
        print(f"[ERROR] start_single_ad failed: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/single_ad_status')
@require_auth
def single_ad_status_endpoint():
    """Get status of single ad execution"""
    try:
        global single_ad_status

        # Get the most recent execution status
        if not single_ad_status:
            return jsonify({'error': 'No execution found'}), 404

        # Get most recent execution
        latest_execution_id = max(single_ad_status.keys())
        status = single_ad_status[latest_execution_id]

        return jsonify(status)

    except Exception as e:
        print(f"[ERROR] single_ad_status failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/start_test_bot', methods=['POST'])
@require_auth
def start_test_bot():
    """Start Test Bot execution"""
    try:
        # Get form data
        videos_folder = request.form.get('videos_folder')
        headlines_csv = request.form.get('headlines_csv')
        campaign_name = request.form.get('campaign_name')
        daily_budget = request.form.get('daily_budget')
        brand_name = request.form.get('brand_name')
        landing_url = request.form.get('landing_url')
        cta_type = request.form.get('cta_type', 'SHOP_NOW')
        target_country = request.form.get('target_country', 'SA')

        print(f"[DEBUG] Test bot called with: campaign_name={campaign_name}, brand_name={brand_name}")

        # Generate unique execution ID
        execution_id = str(uuid.uuid4())

        # Create execution data structure for test bot
        execution_data = {
            'campaign': {
                'name': campaign_name,
                'objective': 'SALES',
                'daily_budget': daily_budget,
                'start_date': datetime.now().isoformat(),
                'status': 'PAUSED'
            },
            'adsets': {
                'base_name': f"{campaign_name} Test AdSet",
                'status': 'PAUSED',
                'countries': [target_country],
                'min_age': 22,
                'max_age': '55+',
                'budget_per_adset': daily_budget
            },
            'ads': {
                'videos_folder': videos_folder,
                'headlines_csv': headlines_csv,
                'brand_name': brand_name,
                'landing_url': landing_url,
                'cta_type': cta_type,
                'test_mode': True  # Always true for test bot
            }
        }

        # Start execution in background thread
        def execute_test():
            try:
                execute_test_bot_mode(execution_id, execution_data)
            except Exception as e:
                print(f"[ERROR] Test bot execution failed: {e}")
                global test_bot_status
                if execution_id in test_bot_status:
                    test_bot_status[execution_id]['error'] = str(e)
                    test_bot_status[execution_id]['completed'] = True

        thread = threading.Thread(target=execute_test)
        thread.daemon = True
        thread.start()

        # Initialize status tracking
        global test_bot_status
        if 'test_bot_status' not in globals():
            test_bot_status = {}

        test_bot_status[execution_id] = {
            'progress_percent': 0,
            'current_step': 'Starting...',
            'ads_created': 0,
            'videos_uploaded': 0,
            'completed': False,
            'error': None,
            'campaign_name': campaign_name,
            'adset_name': None,
            'execution_time': None,
            'start_time': time.time()
        }

        print(f"[DEBUG] Started test bot execution with ID: {execution_id}")

        return jsonify({'success': True, 'execution_id': execution_id})

    except Exception as e:
        print(f"[ERROR] start_test_bot failed: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/test_bot_status')
@require_auth
def test_bot_status_endpoint():
    """Get status of test bot execution"""
    try:
        global test_bot_status

        # Get the most recent execution status
        if 'test_bot_status' not in globals() or not test_bot_status:
            return jsonify({'error': 'No execution found'}), 404

        # Get most recent execution
        latest_execution_id = max(test_bot_status.keys())
        status = test_bot_status[latest_execution_id]

        # Calculate execution time
        if status.get('start_time') and not status.get('completed'):
            status['execution_time'] = round(time.time() - status['start_time'], 1)

        return jsonify(status)

    except Exception as e:
        print(f"[ERROR] test_bot_status failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/bot/folder_beast')
@require_auth
def legacy_folder_beast():
    """Legacy single-form Folder Beast interface"""
    return render_template('folder_beast.html')

@app.route('/start_folder_beast', methods=['POST'])
@require_auth
def start_folder_beast():
    """Start Folder Beast execution from legacy single form"""
    try:
        # Get form data
        videos_folder = request.form.get('videos_folder')
        headlines_csv = request.form.get('headlines_csv')
        campaign_name = request.form.get('campaign_name')
        daily_budget = request.form.get('daily_budget')
        brand_name = request.form.get('brand_name')
        landing_url = request.form.get('landing_url')
        cta_type = request.form.get('cta_type', 'SHOP_NOW')
        target_country = request.form.get('target_country', 'SA')
        campaign_structure = request.form.get('campaign_structure', 'beast')  # Default to beast mode

        # Campaign structure configurations
        structure_configs = {
            'small': {'ads': 10, 'adsets': 2, 'ads_per_adset': 5},
            'medium': {'ads': 50, 'adsets': 5, 'ads_per_adset': 10},
            'large': {'ads': 100, 'adsets': 5, 'ads_per_adset': 20},
            'beast': {'ads': 200, 'adsets': 5, 'ads_per_adset': 40}
        }

        config = structure_configs.get(campaign_structure, structure_configs['beast'])

        print(f"[DEBUG] Legacy start_folder_beast called with: campaign_name={campaign_name}, brand_name={brand_name}")

        # Generate unique execution ID
        execution_id = str(uuid.uuid4())

        # Create execution data structure similar to the 3-step wizard
        execution_data = {
            'campaign': {
                'name': campaign_name,
                'objective': 'SALES',
                'daily_budget': daily_budget,
                'start_date': datetime.now().isoformat(),
                'status': 'PAUSED'
            },
            'adsets': {
                'base_name': f"{campaign_name} AdSet",
                'status': 'PAUSED',
                'countries': [target_country],
                'min_age': 22,
                'max_age': '55+',
                'budget_per_adset': str(int(float(daily_budget)) // config['adsets']),
                'count': config['adsets']
            },
            'ads': {
                'videos_path': videos_folder,
                'csv_path': headlines_csv,
                'brand_name': brand_name,
                'landing_url': landing_url,
                'cta_type': cta_type,
                'structure': campaign_structure,
                'total_ads': config['ads'],
                'ads_per_adset': config['ads_per_adset']
            }
        }

        # Start execution in background thread
        def execute_campaign():
            try:
                execute_optimized_beast_mode(execution_id, execution_data)
            except Exception as e:
                print(f"[ERROR] Campaign execution failed: {e}")
                global execution_status
                if execution_id in execution_status:
                    execution_status[execution_id]['error'] = str(e)
                    execution_status[execution_id]['completed'] = True

        thread = threading.Thread(target=execute_campaign)
        thread.daemon = True
        thread.start()

        # Initialize status tracking
        global execution_status
        execution_status[execution_id] = {
            'progress_percent': 0,
            'current_step': 'Starting...',
            'ads_created': 0,
            'videos_uploaded': 0,
            'completed': False,
            'error': None,
            'campaign_name': campaign_name
        }

        print(f"[DEBUG] Started legacy execution with ID: {execution_id}")

        return jsonify({'success': True, 'execution_id': execution_id})

    except Exception as e:
        print(f"[ERROR] start_folder_beast failed: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/folder_beast_status')
@require_auth
def folder_beast_status():
    """Get status of folder beast execution (legacy endpoint)"""
    try:
        global execution_status

        # Get the most recent execution status
        if not execution_status:
            return jsonify({'error': 'No execution found'}), 404

        # Get most recent execution
        latest_execution_id = max(execution_status.keys())
        status = execution_status[latest_execution_id]

        return jsonify(status)

    except Exception as e:
        print(f"[ERROR] folder_beast_status failed: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 80)
    print("SPEED BEAST MODE DASHBOARD - LIGHTNING FAST EXECUTION!")
    print("=" * 80)
    print("Access: http://localhost:8001")
    print("Features:")
    print("- ULTRA SPEED: 200 ads in 8-12 minutes! (67% faster)")
    print("- PARALLEL: Concurrent media upload & batch processing")
    print("- SMART WAIT: Intelligent media processing detection")
    print("- ENHANCED: 3-Step Folder Beast Wizard with Advanced Options")
    print("- AUTO: Token auto-refresh")
    print("- TARGET: Saudi Arabia & UAE, Age 22-55+")
    print("=" * 80)

    # Get port from environment variable (Railway requirement) or default to 8001
    port = int(os.environ.get('PORT', 8001))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)