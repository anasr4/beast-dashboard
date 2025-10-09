# 🚀 ANAS Beast Bot - Complete Step-by-Step Guide (0 to 100)

**Total Time:** 30-45 minutes
**Difficulty:** Easy (No coding required!)
**Last Updated:** October 8, 2025

---

## 📋 What You'll Need Before Starting

- [ ] A computer with internet
- [ ] Email address (for sign-ups)
- [ ] Snapchat Business account with ads
- [ ] Credit card (for Snapchat API - no charges for setup)

---

# 🎯 PART 1: CREATE ACCOUNTS (10 minutes)

## Step 1: Create GitHub Account (2 minutes)

**What is GitHub?** A website to store code. You need it to get the bot.

1. Go to: https://github.com/join
2. Enter:
   - Username: `yourname` (choose any)
   - Email: your email
   - Password: create a strong password
3. Click **"Create account"**
4. Verify your email (check inbox)
5. ✅ GitHub account ready!

---

## Step 2: Create Railway Account (3 minutes)

**What is Railway?** A hosting service that runs your bot 24/7 in the cloud.

1. Go to: https://railway.app
2. Click **"Login"** (top right)
3. Click **"Login with GitHub"**
4. Click **"Authorize Railway"**
5. ✅ Railway account ready!

**Note:** Railway gives you $5 free credit per month - enough for testing!

---

## Step 3: Prepare Snapchat Business Account (5 minutes)

**What you need:** Access to Snapchat Ads Manager

1. Go to: https://ads.snapchat.com/
2. Login with your Snapchat Business account
3. Make sure you see your ad account dashboard
4. Keep this tab open - you'll need it later
5. ✅ Snapchat account ready!

---

# 🔑 PART 2: GET SNAPCHAT API CREDENTIALS (15 minutes)

**Important:** These credentials let the bot access your Snapchat account.

## Step 4: Create Snapchat App (5 minutes)

1. Go to: https://business.snapchat.com/
2. Login with your Snapchat Business account
3. Click **"My Apps"** or **"Business Details"** → **"API Credentials"**
4. Click **"+ Create App"** or **"New OAuth App"**
5. Fill in:
   - **App Name:** `My Beast Bot` (or any name you like)
   - **Redirect URI:** `https://localhost:8000/callback` (temporary - you'll update this later)
   - **App Description:** `Campaign automation bot`
6. Select **ALL** OAuth Scopes (especially `snapchat-marketing-api`)
7. Click **"Create App"** or **"Save"**

8. **SAVE THESE IMMEDIATELY:**
   - ✅ **Client ID** (looks like: `abc123-def456-ghi789`)
   - ✅ **Client Secret** (looks like: `xyz789-abc123-def456`)

**⚠️ Important:** Save these in a text file! You'll need them soon.

**📝 Note:** After you deploy on Railway (Step 8), you'll update the Redirect URI to your Railway URL. See `OAUTH_SETUP.md` for details.

---

## Step 5: Get Refresh Token (7 minutes)

**This is the most technical step - follow carefully:**

### A. Get Authorization Code

1. Copy this URL (replace `YOUR_CLIENT_ID` with your actual Client ID from Step 4):
   ```
   https://accounts.snapchat.com/login/oauth2/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=https://localhost:8000/callback&scope=snapchat-marketing-api&state=test
   ```

2. Replace `YOUR_CLIENT_ID` in the URL with your real Client ID
   - Example: If your Client ID is `abc123`, the URL becomes:
   ```
   https://accounts.snapchat.com/login/oauth2/authorize?response_type=code&client_id=abc123&redirect_uri=https://localhost:8000/callback&scope=snapchat-marketing-api&state=test
   ```

3. Paste the URL in your browser and press Enter

4. Login to Snapchat if asked

5. Click **"Continue"** or **"Authorize"**

6. You'll be redirected to a page that says "Can't reach this page" - **THIS IS NORMAL!**

7. Look at the URL in your browser's address bar. It will look like:
   ```
   https://localhost:8000/callback?code=LONG_CODE_HERE&state=test
   ```

8. Copy the part after `code=` and before `&state`
   - Example: If URL is `...?code=abc123xyz&state=...`, copy `abc123xyz`
   - ✅ **Save this code** - this is your Authorization Code

### B. Exchange Code for Refresh Token

**You need to make an API call. Use one of these methods:**

#### Method 1: Use Postman (Recommended)

1. Download Postman: https://www.postman.com/downloads/
2. Install and open Postman
3. Click **"New"** → **"HTTP Request"**
4. Set request type to **POST**
5. Enter URL: `https://accounts.snapchat.com/login/oauth2/access_token`
6. Click **"Body"** tab
7. Select **"x-www-form-urlencoded"**
8. Add these fields:

   | Key | Value |
   |-----|-------|
   | `grant_type` | `authorization_code` |
   | `client_id` | Your Client ID from Step 4 |
   | `client_secret` | Your Client Secret from Step 4 |
   | `code` | Authorization Code from Step 5A |
   | `redirect_uri` | `https://localhost:8000/callback` |

9. Click **"Send"**
10. You'll get a response with `refresh_token`
11. ✅ **Copy and save the `refresh_token`** - this is what you need!

#### Method 2: Use curl (Terminal/Command Prompt)

```bash
curl -X POST https://accounts.snapchat.com/login/oauth2/access_token \
  -d "grant_type=authorization_code" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "code=YOUR_AUTH_CODE" \
  -d "redirect_uri=https://localhost:8000/callback"
```

Replace YOUR_CLIENT_ID, YOUR_CLIENT_SECRET, and YOUR_AUTH_CODE with your values.

---

## Step 6: Get Ad Account ID (3 minutes)

1. Go to: https://ads.snapchat.com/
2. Look at the URL in your browser
3. You'll see something like:
   ```
   https://ads.snapchat.com/ads/accounts/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/dashboard
   ```
4. The long string after `/accounts/` is your Ad Account ID (format: UUID)
5. ✅ **Copy and save your Ad Account ID**

---

## ✅ Credentials Checklist

Before continuing, make sure you have saved:

- [ ] Client ID (from Step 4)
- [ ] Client Secret (from Step 4)
- [ ] Refresh Token (from Step 5)
- [ ] Ad Account ID (from Step 6)

**Save these in a text file - you'll need them in Part 3!**

---

# 🚂 PART 3: DEPLOY BOT ON RAILWAY (10 minutes)

## Step 7: Fork the Repository (2 minutes)

**What is forking?** Making your own copy of the bot code.

1. Go to: https://github.com/anasr4/beast-dashboard
2. Click the **"Fork"** button (top right corner)
3. Click **"Create fork"**
4. Wait 10 seconds - your copy is being created
5. You'll be redirected to `https://github.com/YOUR_USERNAME/beast-dashboard`
6. ✅ Your own copy is ready!

---

## Step 8: Deploy on Railway (5 minutes)

1. Go to: https://railway.app
2. Click **"New Project"**
3. Click **"Deploy from GitHub repo"**
4. Click **"Configure GitHub App"** (if asked)
5. Select **"Only select repositories"**
6. Choose your forked repository: `YOUR_USERNAME/beast-dashboard`
7. Click **"Save"**
8. Click **"Deploy from GitHub repo"** again
9. Select your repository: `YOUR_USERNAME/beast-dashboard`
10. Railway will automatically start deploying
11. Wait 2-5 minutes - you'll see logs scrolling
12. When you see **"Deployment successful"** with a green checkmark - done!
13. ✅ Bot is deployed!

---

## Step 9: Get Your Bot URL (1 minute)

1. In Railway, click on your project
2. Click **"Settings"** tab
3. Scroll to **"Domains"** section
4. Click **"Generate Domain"**
5. Railway creates a URL like: `https://beast-dashboard-production-xxxxx.up.railway.app`
6. ✅ **Copy this URL** - this is your bot's address!

---

## Step 9.5: Update Snapchat Redirect URL (2 minutes)

**IMPORTANT:** Now that you have your Railway URL, update Snapchat app settings:

1. Go to: https://business.snapchat.com/apps
2. Click on your app (created in Step 4)
3. Find **"Redirect URIs"** or **"OAuth Settings"**
4. **Remove** the old URL (`https://localhost:8000/callback`)
5. **Add** your new Railway URL with `/api/oauth/callback`:
   ```
   https://YOUR-RAILWAY-URL-HERE/api/oauth/callback
   ```
   Example: `https://beast-dashboard-production-xxxxx.up.railway.app/api/oauth/callback`
6. Click **"Save"**
7. ✅ OAuth is now configured!

**💡 Why?** The bot auto-detects your Railway URL for OAuth. This ensures authorization works perfectly!

See `OAUTH_SETUP.md` for detailed troubleshooting.

---

## Step 10: Test Your Bot (2 minutes)

1. Open your Railway URL in a new browser tab
2. You should see the **"ANAS Beast Bot"** dashboard
3. You'll see two bots:
   - 🚀 Beast Campaign Bot
   - 📈 Beast AdSquad Expander
4. If you see this - **SUCCESS!** Your bot is running!
5. ✅ Bot is live!

---

# ⚙️ PART 4: CONFIGURE YOUR BOT (5 minutes)

## Step 11: Add Snapchat Credentials (5 minutes)

1. On your bot dashboard, click **"Token Manager"** (🔑 icon in navbar)
2. You'll see a form titled **"Snapchat API Configuration"**
3. Click the **"Refresh Token"** button
4. Enter your credentials (from Part 2):
   - **Client ID:** Paste from Step 4
   - **Client Secret:** Paste from Step 4
   - **Refresh Token:** Paste from Step 5
   - **Ad Account ID:** Paste from Step 6
5. Click **"Save Configuration"**
6. You'll see: **"Configuration saved successfully!"**
7. Click **"Test Token"**
8. If you see **"Token is valid! ✅"** - perfect!
9. If you see an error - double-check your credentials and try again
10. ✅ Bot is configured!

---

# 🎯 PART 5: CREATE YOUR FIRST CAMPAIGN (10-15 minutes)

## Step 12: Prepare Your Assets (5 minutes)

Before creating a campaign, you need:

### A. Videos (10 videos minimum)

1. Prepare 10-100 MP4 videos
2. Requirements:
   - Format: MP4
   - Size: Under 5MB each (use bot's Video Compressor if needed)
   - Dimensions: Vertical (9:16 ratio recommended)
   - Length: 3-60 seconds
3. Put all videos in one folder on your computer

### B. Headlines CSV File

1. Create a text file with headlines (one per line)
2. Requirements:
   - Each headline: Maximum 34 characters
   - One headline per line
   - No header row
3. Save as `.csv` or `.txt`

Example `headlines.csv`:
```
Buy Now - Limited Offer
Shop Our Best Deals
Get 50% Off Today
Free Shipping Worldwide
New Arrivals Just In
```

### C. Snapchat Pixel ID (Optional but Recommended)

1. Go to: https://ads.snapchat.com/
2. Click **"Events Manager"** (left sidebar)
3. Click on your Pixel
4. Copy the Pixel ID (looks like: `6dd29628-0d34-4e10-ad54-8697f81dd40a`)
5. ✅ Save this - you'll enter it in the bot

**Note:** Pixel ID gives better ad performance (PIXEL_PURCHASE optimization)

---

## Step 13: Create Campaign with Beast Campaign Bot (5-10 minutes)

1. Go to your bot dashboard
2. Click **"Beast Campaign Bot"** (🚀 icon)

### Step 1: Campaign Details

1. **Campaign Name:** Enter a name (e.g., `My First Campaign`)
2. **Daily Budget:** Enter budget in USD (e.g., `100`)
3. **Campaign Objective:** Keep as `WEBSITE_VISITS` or `WEB_CONVERSIONS`
4. Click **"Next"**

### Step 2: Ad Set Configuration

1. **Number of Ad Sets:** Enter `5` (for testing)
2. **Budget Per Ad Set:** Enter `20` (USD per day)
3. **Status:** Keep as `ACTIVE`
4. **Target Countries:** Select `SA` (Saudi Arabia) or your country
5. **Age Range:** Pre-set to `22-55` (good for most campaigns)
6. **Enable Pixel Tracking:** Select `✅ Enable`
7. **Snapchat Pixel ID:** Paste your Pixel ID (from Step 12C)
8. Click **"Next"**

### Step 3: Upload Media & Content

1. **Upload Videos:**
   - Click **"Browse"** button
   - Select your video folder
   - Wait for upload (shows progress)

2. **Upload Headlines CSV:**
   - Click **"Browse"** for CSV
   - Select your headlines file
   - Wait for upload

3. **Brand Name:** Enter your brand name (e.g., `MyBrand`)
4. **Website URL:** Enter your landing page (e.g., `https://example.com/product`)
5. **Call to Action:** Select `SHOP_NOW` or relevant CTA
6. Click **"Next"**

### Step 4: Review & Execute

1. Review all your settings
2. Check:
   - Campaign name ✓
   - Budget ✓
   - Ad sets count ✓
   - Videos uploaded ✓
   - Headlines uploaded ✓
   - Pixel ID added ✓
3. Click **"Execute Campaign"**
4. **Watch the magic happen!** 🎉

---

## Step 14: Monitor Progress (Real-Time)

You'll see a real-time progress page showing:

1. **Campaign Creation** (5%)
2. **Creating Ad Sets** (20-40%)
3. **Uploading Videos** (55-75%)
   - Shows: "Uploaded 45/100 videos..."
4. **Creating Ads** (85-98%)
   - Shows: "Creating ads... (78/100)"
5. **Completion** (100%)

**Time:** 5-10 minutes for 100 ads

---

## Step 15: Verify in Snapchat Ads Manager

1. Go to: https://ads.snapchat.com/
2. Click **"Campaigns"** (left sidebar)
3. You should see your new campaign!
4. Click on the campaign to see:
   - ✅ Ad sets created
   - ✅ Ads published
   - ✅ Videos uploaded
5. Click **"Preview"** on any ad to see how it looks
6. ✅ **CONGRATULATIONS!** Your first campaign is live! 🎊

---

# 🎉 SUCCESS! YOU'RE DONE!

## What You've Accomplished:

✅ Created GitHub & Railway accounts
✅ Got Snapchat API credentials
✅ Deployed your own bot on Railway
✅ Configured Snapchat integration
✅ Created your first automated campaign
✅ Published ads to Snapchat

---

# 🚀 NEXT STEPS

## Create More Campaigns

Now you can:

1. **Scale Up:**
   - Create 200 ad campaigns
   - Upload 100 videos at once
   - Bot guarantees exact count (request 100 = get 100!)

2. **Use AdSquad Expander:**
   - Add more ad squads to successful campaigns
   - Scale winners without creating new campaigns
   - Search and select existing campaigns

3. **Optimize:**
   - Use Video Compressor to compress large videos
   - Test different headlines
   - Experiment with budgets and targeting

---

# 📊 Usage Tips

## Best Practices:

1. **Videos:**
   - Use vertical format (9:16)
   - Keep under 5MB
   - 3-10 seconds work best for attention

2. **Headlines:**
   - Keep under 34 characters
   - Be clear and direct
   - Include call-to-action words

3. **Budget:**
   - Start with $50-100 daily budget
   - Use 5-10 ad sets for testing
   - Scale winners after 2-3 days

4. **Pixel ID:**
   - ALWAYS use Pixel ID for best results
   - Enables PIXEL_PURCHASE optimization
   - Tracks conversions accurately

5. **Age Targeting:**
   - Bot uses 22-55 (Snapchat's optimal range)
   - Targets everyone 22 years old and older
   - Already optimized - no changes needed

---

# 🐛 Troubleshooting

## Common Issues & Solutions:

### "Token is invalid"
- **Cause:** Expired or wrong credentials
- **Fix:** Go back to Step 5 and get a new Refresh Token

### "Videos not uploading"
- **Cause:** Videos too large or wrong format
- **Fix:** Use bot's Video Compressor to compress to under 5MB

### "AdSquad creation failed"
- **Cause:** Missing Pixel ID when using PIXEL_PURCHASE
- **Fix:** Add your Pixel ID in Step 2 of campaign creation

### "Railway deployment failed"
- **Cause:** Repository not forked correctly
- **Fix:** Delete and re-fork the repository (Step 7)

### "Can't access dashboard"
- **Cause:** Railway URL not generated
- **Fix:** Go to Railway Settings → Domains → Generate Domain

---

# 💰 Costs

## What You'll Pay:

1. **GitHub:** FREE ✅
2. **Railway:** $5/month free credit (enough for testing) ✅
3. **Snapchat API:** FREE to use ✅
4. **Snapchat Ads:** Only pay for actual ads running (your budget)

**Total Setup Cost:** $0
**Monthly Cost:** $0-5 (depending on Railway usage)

---

# 📞 Need Help?

## Resources:

1. **Setup Issues:** Re-read this guide carefully
2. **Snapchat API:** https://developers.snap.com/api/
3. **Railway Help:** https://docs.railway.app/
4. **Bot Documentation:**
   - [Complete Setup Guide](SETUP_FOR_NEW_USER.md)
   - [Railway Guide](RAILWAY_DEPLOYMENT.md)
   - [README](README.md)

---

# ✅ Final Checklist

Before you're done, verify:

- [ ] Railway shows "Running" status (green)
- [ ] Bot dashboard loads at your Railway URL
- [ ] Token Manager shows "Token is valid ✅"
- [ ] Test campaign created successfully
- [ ] Ads visible in Snapchat Ads Manager
- [ ] Real-time progress tracking worked
- [ ] All videos uploaded (exact count)

---

**🎊 CONGRATULATIONS!**

You now have your own fully automated Snapchat campaign bot!

You can create:
- ✅ Unlimited campaigns
- ✅ 100+ ads in under 10 minutes
- ✅ Automatic video uploads
- ✅ Perfect ad count every time
- ✅ Real-time progress tracking

**Time to scale your Snapchat ads!** 🚀

---

**Made with ❤️ by Anas**

*Good luck with your campaigns - you will kill it!* 💪
