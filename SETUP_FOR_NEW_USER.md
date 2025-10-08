# 🚀 ANAS Beast Bot - Complete Setup Guide for New Users

This guide will help you set up your own copy of the ANAS Beast Bot with your own Snapchat API credentials.

**📅 Last Updated:** October 8, 2025
**✅ Latest Features:**
- Exact ad count guarantee (request 100 = get 100!)
- Age targeting: 22-55+ (optimized for Snapchat API)
- Video retry mechanism (3 attempts per video)
- PIXEL_PURCHASE optimization with fallback to SWIPES

## 📋 What You'll Need

1. **GitHub Account** (free) - [Sign up here](https://github.com/join)
2. **Railway Account** (free tier available) - [Sign up here](https://railway.app/)
3. **Snapchat Business Account** with API access
4. **Your Snapchat API Credentials:**
   - Client ID
   - Client Secret
   - Refresh Token
   - Ad Account ID

---

## 🔑 Step 1: Get Your Snapchat API Credentials

### A. Create Snapchat Business Account
1. Go to [Snapchat Ads Manager](https://ads.snapchat.com/)
2. Create a Business account if you don't have one

### B. Create an App in Snapchat
1. Go to [Snapchat Business Portal](https://business.snapchat.com/)
2. Navigate to **"My Apps"** or **"Developer Portal"**
3. Click **"Create App"**
4. Fill in app details:
   - App Name: `Beast Bot` (or any name)
   - Redirect URI: `https://localhost:8000/callback`
   - OAuth Scopes: Select **ALL** scopes (especially `snapchat-marketing-api`)
5. Save and note down:
   - ✅ **Client ID** (looks like: `abc123-def456-ghi789`)
   - ✅ **Client Secret** (looks like: `xyz789-abc123-def456`)

### C. Get Your Refresh Token
1. Use this OAuth URL (replace `YOUR_CLIENT_ID` with your actual Client ID):
```
https://accounts.snapchat.com/login/oauth2/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=https://localhost:8000/callback&scope=snapchat-marketing-api&state=test
```
2. Paste in browser and authorize the app
3. You'll be redirected to a URL that contains a **code** parameter
4. Use that code to get refresh token (you can use Postman or ask the bot creator for help with this step)
5. ✅ Save your **Refresh Token**

### D. Get Your Ad Account ID
1. Go to [Snapchat Ads Manager](https://ads.snapchat.com/)
2. Look at the URL, it will contain your Ad Account ID
3. Format: `27205503-c6b2-4aa7-89d1-3b8dd52f527d`
4. ✅ Save your **Ad Account ID**

---

## 📦 Step 2: Fork the Repository

You have TWO options:

### Option A: Fork from Original Repository (Recommended)

**What the bot creator needs to share with you:**
- The GitHub repository URL (example: `https://github.com/anasr4/beast-dashboard`)

**Steps:**
1. Go to the GitHub repository URL
2. Click the **"Fork"** button (top right)
3. This creates YOUR OWN copy under your GitHub account
4. Your fork URL will be: `https://github.com/YOUR_USERNAME/beast-dashboard`

### Option B: Create New Repository from Zip

**What the bot creator needs to share with you:**
- A ZIP file of the entire `beast-dashboard` folder

**Steps:**
1. Download and extract the ZIP file
2. Go to [GitHub](https://github.com/new)
3. Create a new repository:
   - Name: `beast-dashboard` (or any name)
   - Privacy: Private (recommended)
4. Upload all files from the extracted folder
5. Click **"Commit changes"**

---

## ☁️ Step 3: Deploy on Railway

### A. Connect Railway to GitHub
1. Go to [Railway.app](https://railway.app/)
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your forked repository: `YOUR_USERNAME/beast-dashboard`

### B. Configure Environment Variables
In Railway dashboard, go to **Variables** tab and add:

```
PORT=8080
```

That's it! Railway will automatically detect it's a Python app.

### C. Wait for Deployment
- Railway will automatically build and deploy your app
- This takes 2-5 minutes
- You'll get a URL like: `https://beast-dashboard-production-abc123.up.railway.app`

---

## 🔐 Step 4: Add Your Snapchat Credentials

### A. Access Your Bot
1. Open your Railway URL in browser
2. **Dashboard loads directly** - no login required! 🎉

### B. Add Your API Credentials
1. Click **"Token Manager"** (🔑 icon in navbar)
2. Click **"Refresh Token"** button
3. Enter your Snapchat credentials:
   - Client ID
   - Client Secret
   - Refresh Token
   - Ad Account ID
4. Click **"Save Configuration"**
5. Test the token by clicking **"Test Token"**

---

## ✅ Step 5: Test Your Bot

### A. Test Video Compressor (Optional)
1. Go to **Video Compressor** bot
2. Upload a video
3. Compress it to verify everything works

### B. Test Campaign Bot
1. Go to **Beast Campaign Bot**
2. Fill in:
   - Campaign name
   - Budget
   - Number of ad sets
   - Upload videos folder
   - Upload CSV with headlines
   - Add your Pixel ID (from Snapchat Events Manager)
3. Click **"Execute"**
4. Watch the progress!

### C. Test AdSquad Expander Bot
1. Go to **Beast AdSquad Expander**
2. Select an existing campaign
3. Configure ad squads
4. Upload videos and headlines
5. Execute and verify ads are created

---

## 📁 What Files to Share

### Minimum Files Needed (for new user):
```
beast-dashboard/
├── speed_beast_dashboard.py       # Main bot code
├── token_manager.py                # Token management
├── snapchat_api_client.py         # Snapchat API wrapper
├── video_compressor.py            # Video compression
├── requirements_web.txt           # Python dependencies
├── templates_flask/               # All HTML templates
│   ├── updated_dashboard.html
│   ├── folder_beast_step1.html
│   ├── folder_beast_step2.html
│   ├── folder_beast_step3.html
│   ├── optimized_beast_execute.html
│   ├── adsquad_expander_step1.html
│   ├── adsquad_expander_step2.html
│   ├── adsquad_expander_step3.html
│   ├── adsquad_expander_execute.html
│   ├── token_manager.html
│   └── video_compressor.html
├── static/                         # Static files (if any)
├── SETUP_FOR_NEW_USER.md          # This guide!
└── README.md                       # Project info
```

### Files to EXCLUDE (don't share these):
```
❌ config.json                     # Contains YOUR credentials
❌ .env                            # Environment variables
❌ __pycache__/                    # Python cache
❌ *.pyc                           # Compiled Python files
❌ uploads/                        # Uploaded files
❌ tmp/                            # Temporary files
❌ .git/                           # Git history (if sharing ZIP)
```

---

## 🔒 Security Best Practices

### For Bot Creator (You):
1. **Never share your `config.json`** - it has your API credentials
2. **Share only the code**, not your tokens
3. Create a `.gitignore` file to prevent committing secrets:
```
config.json
.env
*.pyc
__pycache__/
uploads/
tmp/
*.log
```

### For New User:
1. **Use your own Snapchat account** - don't share credentials
2. **Set your own dashboard password**
3. **Keep your Railway project private**
4. **Don't commit credentials to GitHub**

---

## 🛠️ Customization Options

The new user can customize:

### 1. Dashboard Branding
Edit `templates_flask/updated_dashboard.html`:
- Line 267: Change title from "ANAS Beast Bot" to their name
- Lines 340-341: Change footer messages

### 2. Bot Names
Edit `speed_beast_dashboard.py` around line 219:
```python
dashboard_bots = {
    'folder_beast': {
        'name': 'Your Bot Name Here',  # Change this
        # ...
    }
}
```

### 3. Default Settings
Edit `speed_beast_dashboard.py`:
- Default budget amounts
- Default ad set counts
- Default targeting countries

---

## 📞 Support & Troubleshooting

### Common Issues:

**Issue: "Invalid Token" error**
- Solution: Regenerate refresh token from Snapchat Developer Portal
- Make sure all scopes are enabled

**Issue: Railway deployment fails**
- Solution: Check Railway logs
- Make sure `requirements_web.txt` is present
- Verify Python version compatibility

**Issue: Videos not uploading**
- Solution: Check video format (must be MP4)
- Verify file size (under 5MB recommended)
- Check video dimensions (vertical format works best)

**Issue: Dashboard not loading**
- Check Railway deployment status (should be green)
- Check Railway logs for errors
- Verify your Railway URL is correct

**Issue: "min_age value must be between 13 and 45" error**
- This is NORMAL! The bot automatically sets min_age=22
- Snapchat limit: min_age can only be 13-45
- The bot uses min_age=22, max_age=55 (targets 22-55+)
- No action needed - this is already fixed!

**Issue: Not all videos uploading**
- The bot now retries failed videos 3 times
- If video fails 3 times, it moves to next video
- Bot keeps going until exact count is reached
- Example: Request 100 ads = exactly 100 ads created

---

## 🆕 October 2025 Updates

### Latest Improvements:
1. **Exact Ad Count Guarantee**
   - Bot now guarantees exact number of ads requested
   - Retries failed videos up to 3 times
   - Repeats videos if needed to reach target count

2. **Age Targeting Fixed**
   - Hardcoded to 22-55 (Snapchat's optimal range)
   - min_age: 22 (won't target under 22)
   - max_age: 55 (targets up to 55+, including 60, 70, etc.)

3. **Pixel Optimization**
   - PIXEL_PURCHASE when Pixel ID provided (best results)
   - SWIPES optimization when no Pixel ID (fallback)
   - Clear instructions in UI for Pixel ID location

4. **Video Retry System**
   - Each video gets 3 upload attempts
   - 1 second wait between retries
   - Continues with next video after 3 failures
   - Logs all retry attempts for debugging

5. **UI Improvements**
   - Pixel ID field always visible with cyan highlight
   - Clear instructions: "Snapchat Ads Manager → Events Manager → Pixel ID"
   - Better error messages and progress tracking

---

## 🎉 You're All Set!

Your bot is now ready to use! You can:
- ✅ Create unlimited campaigns
- ✅ Upload videos and compress them
- ✅ Expand existing campaigns with new ad squads
- ✅ Manage everything from one dashboard

**Important:** Each person needs their own:
- Snapchat Business account
- API credentials (Client ID, Secret, Refresh Token)
- Railway project (for hosting)
- GitHub repository (for code)

---

## 📚 Additional Resources

- [Snapchat Marketing API Docs](https://marketingapi.snapchat.com/docs/)
- [Railway Documentation](https://docs.railway.app/)
- [GitHub Guides](https://guides.github.com/)

---

## ⚠️ Legal Notice

This bot is for legitimate advertising purposes only. Users must:
- Comply with Snapchat's Terms of Service
- Follow advertising policies
- Not use for spam or abuse
- Respect rate limits

---

**Created with ❤️ by Anas**

Good luck with your Snapchat campaigns! 🚀
