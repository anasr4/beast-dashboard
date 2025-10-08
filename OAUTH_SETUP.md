# OAuth Redirect URL Setup Guide

## Problem Solved
Each Railway deployment gets a unique URL. The bot now **auto-detects** its own URL, so OAuth works for everyone!

## What to Put in Snapchat App Settings

### Step 1: Find Your Railway URL
After deploying on Railway, you'll get a URL like:
```
https://web-production-xxxxx.up.railway.app
```

### Step 2: Set Redirect URL in Snapchat
1. Go to [Snapchat Developer Portal](https://business.snapchat.com/apps)
2. Click on your app
3. Go to **OAuth2 Settings** or **Redirect URIs**
4. Add this EXACT URL (replace with YOUR Railway URL):

```
https://YOUR-RAILWAY-URL.up.railway.app/api/oauth/callback
```

**Examples:**
- If your Railway URL is `https://web-production-12345.up.railway.app`
- Then set redirect URL to: `https://web-production-12345.up.railway.app/api/oauth/callback`

### Step 3: Save and Test
1. Click **Save** in Snapchat
2. Go to your bot's Token Manager page
3. Enter your credentials and click "Authorize"
4. You'll be redirected to Snapchat → Approve → Back to your bot ✅

## How It Works Now

### Before (Hardcoded - Didn't Work)
```javascript
// Old code - only worked for one Railway URL
const redirectUri = 'https://web-production-95efb.up.railway.app/api/oauth/callback'
```

### After (Auto-Detect - Works for Everyone!)
```javascript
// New code - auto-detects YOUR Railway URL
const currentUrl = window.location.origin; // Gets YOUR Railway URL automatically
const redirectUri = `${currentUrl}/api/oauth/callback`;
```

## For Your Friend

Tell your friend to:

1. **Deploy on Railway** - They get their own URL: `https://web-production-XXXXX.up.railway.app`

2. **Create Snapchat App** - Go to business.snapchat.com/apps

3. **Set Redirect URL** in Snapchat app to:
   ```
   https://web-production-XXXXX.up.railway.app/api/oauth/callback
   ```
   (Replace XXXXX with their actual Railway URL)

4. **Authorize** - Go to bot → Token Manager → Enter credentials → Click "Authorize with Snapchat"

5. **Done!** - OAuth will work with their Railway URL automatically

## Quick Copy-Paste Template

Send this to your friend:

```
Hey! Here's how to set up OAuth:

1. After you deploy on Railway, copy your URL (looks like: https://web-production-xxxxx.up.railway.app)

2. Go to your Snapchat App settings: https://business.snapchat.com/apps

3. Find "Redirect URIs" or "OAuth Settings"

4. Add this URL (replace with YOUR Railway URL):
   https://YOUR-RAILWAY-URL-HERE/api/oauth/callback

   Example: https://web-production-12345.up.railway.app/api/oauth/callback

5. Save in Snapchat

6. Go to your bot → Token Manager → Authorize

Done! The bot auto-detects your Railway URL so OAuth will work perfectly.
```

## Troubleshooting

### Error: "redirect_uri_mismatch"
**Cause:** URL in Snapchat doesn't match your Railway URL

**Fix:**
1. Check your Railway URL (it's at the top of your Railway dashboard)
2. Make sure Snapchat redirect URL is EXACTLY: `https://YOUR-RAILWAY-URL/api/oauth/callback`
3. Must include `/api/oauth/callback` at the end
4. Must use `https://` not `http://`
5. No trailing slash after `callback`

### Error: "invalid_client"
**Cause:** Client ID or Client Secret is wrong

**Fix:**
1. Double-check credentials in Snapchat Developer Portal
2. Copy-paste carefully (no extra spaces)
3. Make sure you're using the correct app

### Success Message
When it works, you'll see:
```
✅ Authorization successful!
✅ Tokens saved!
✅ Ready to create campaigns!
```

## Technical Details

The bot uses these endpoints:

1. **Authorization URL** (Snapchat):
   ```
   https://accounts.snapchat.com/login/oauth2/authorize
   ```

2. **Redirect URL** (Your Bot - Auto-detected):
   ```
   https://YOUR-RAILWAY-URL/api/oauth/callback
   ```

3. **Token Exchange URL** (Snapchat):
   ```
   https://accounts.snapchat.com/login/oauth2/access_token
   ```

The bot automatically uses YOUR Railway URL in steps 2 and 3, so OAuth works for every deployment!
