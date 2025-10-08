# 🚂 Railway Deployment Guide - Quick Setup

**For:** Friends who want to run ANAS Beast Bot on their own Railway account

## 📦 Prerequisites

Before starting, make sure you have:
- ✅ GitHub account
- ✅ Railway account ([sign up here](https://railway.app))
- ✅ Snapchat Business account
- ✅ Snapchat API credentials (Client ID, Secret, Refresh Token, Ad Account ID)

---

## 🚀 Step-by-Step Railway Deployment

### Step 1: Fork the Repository on GitHub

1. Go to the original repository: `https://github.com/anasr4/beast-dashboard`
2. Click the **"Fork"** button (top right corner)
3. This creates your own copy: `https://github.com/YOUR_USERNAME/beast-dashboard`
4. ✅ Your fork is ready!

### Step 2: Connect Railway to GitHub

1. Go to [Railway.app](https://railway.app)
2. Click **"Login"** → Sign in with GitHub
3. Grant Railway access to your GitHub repositories
4. ✅ Railway is connected!

### Step 3: Deploy Your Bot

1. On Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your forked repository: `YOUR_USERNAME/beast-dashboard`
4. Railway will automatically:
   - Detect it's a Python app
   - Install dependencies from `requirements_web.txt`
   - Start the Flask server
5. Wait 2-5 minutes for deployment
6. ✅ Your bot is deploying!

### Step 4: Configure Railway Settings

1. In Railway project, go to **Settings** tab
2. Click **"Generate Domain"** to get a public URL
3. Your URL will be: `https://beast-dashboard-production-xxxxx.up.railway.app`
4. Copy this URL - you'll need it!
5. ✅ URL is ready!

### Step 5: Add Your Snapchat Credentials

1. Open your Railway URL in browser
2. You'll see the login page
3. **Default password:** Ask the person who shared the bot with you
4. After login, click **"Token Manager"** (🔑 icon)
5. Click **"Refresh Token"** button
6. Enter your Snapchat API credentials:
   ```
   Client ID: YOUR_CLIENT_ID
   Client Secret: YOUR_CLIENT_SECRET
   Refresh Token: YOUR_REFRESH_TOKEN
   Ad Account ID: YOUR_AD_ACCOUNT_ID
   ```
7. Click **"Save Configuration"**
8. Click **"Test Token"** to verify it works
9. ✅ Credentials saved!

---

## 🎯 Testing Your Bot

### Test the Beast Campaign Bot:

1. Click **"Beast Campaign Bot"** on dashboard
2. Fill in campaign details:
   - Campaign name: `Test Campaign`
   - Daily budget: `$50`
   - Number of ad sets: `2`
3. Upload a folder with 10 videos
4. Upload a CSV file with headlines (one per line)
5. Add your Pixel ID from Snapchat Events Manager
6. Click **"Execute"**
7. Watch the real-time progress!
8. ✅ If you see ads being created in Snapchat - it works!

### Test the AdSquad Expander Bot:

1. Click **"Beast AdSquad Expander"** on dashboard
2. Search for an existing campaign
3. Configure ad squads (2-5 for testing)
4. Upload videos and CSV
5. Add Pixel ID
6. Click **"Execute"**
7. Check Snapchat - new ad squads should appear!
8. ✅ Success!

---

## ⚙️ Railway Project Management

### View Logs:
1. Railway Dashboard → Your Project
2. Click **"Deployments"** tab
3. Click latest deployment
4. Click **"View Logs"**
5. You'll see all debug output and errors

### Redeploy (if needed):
1. Make changes in your GitHub repository
2. Push changes: `git push origin main`
3. Railway automatically redeploys
4. Wait 2-3 minutes
5. ✅ New version is live!

### Check Status:
1. Railway Dashboard → Your Project
2. Green = Running ✅
3. Red = Error ❌
4. Yellow = Deploying ⚠️

---

## 💰 Railway Pricing

**Free Tier:**
- $5 worth of usage per month (free credit)
- Enough for moderate usage
- Auto-sleeps after 30 minutes of inactivity

**Hobby Plan:** $5/month
- 500 hours of runtime
- No auto-sleep
- Perfect for production use

**Pro Plan:** $20/month
- Unlimited runtime
- Higher resource limits
- For heavy usage

---

## 🔒 Security Best Practices

### DO:
✅ Use your own Snapchat credentials
✅ Change the dashboard password
✅ Keep your Railway project private
✅ Never share your refresh token
✅ Use `.gitignore` to protect `config.json`

### DON'T:
❌ Share your API credentials
❌ Commit secrets to GitHub
❌ Use someone else's tokens
❌ Share your Railway project URL publicly

---

## 🐛 Common Railway Issues

**Issue: "Application failed to start"**
- Check Railway logs for errors
- Verify `requirements_web.txt` exists
- Make sure you pushed latest code to GitHub

**Issue: "Port binding failed"**
- Railway uses `PORT` environment variable
- Bot automatically uses Railway's assigned port
- No action needed - already configured!

**Issue: "Out of memory"**
- Railway free tier has 512MB RAM limit
- Reduce number of concurrent uploads
- Consider upgrading to Hobby plan

**Issue: "Deployment timeout"**
- Large repositories take longer to deploy
- Wait up to 10 minutes
- Check Railway status page for outages

---

## 📊 Monitoring Your Bot

### Check Deployment Status:
```bash
# Your bot is working if you see:
✅ "Deployment successful"
✅ Green status indicator
✅ Can access dashboard URL
✅ Login page loads
```

### Check Bot Health:
```bash
# Test these after deployment:
1. Open Railway URL → Should load login page
2. Login → Should show dashboard
3. Click Token Manager → Should show form
4. Test token → Should show "Token valid"
5. Create test campaign → Should start execution
```

---

## 🔄 Updating Your Bot

When the original bot gets updates:

### Method 1: Sync Your Fork (Recommended)
1. Go to your fork on GitHub
2. Click **"Sync fork"** button
3. Click **"Update branch"**
4. Railway auto-redeploys with new code
5. ✅ Updated!

### Method 2: Manual Pull
```bash
# In your local copy:
git remote add upstream https://github.com/anasr4/beast-dashboard.git
git fetch upstream
git merge upstream/main
git push origin main
```

---

## 📝 Environment Variables (Optional)

Railway automatically sets:
- `PORT` - Assigned by Railway
- `PYTHONUNBUFFERED` - For better logging

You can add custom variables:
1. Railway Dashboard → Settings → Variables
2. Click **"New Variable"**
3. Add key-value pairs
4. Redeploy for changes to take effect

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] Railway project shows "Running" status
- [ ] Dashboard URL loads without errors
- [ ] Can login with password
- [ ] Token Manager accepts credentials
- [ ] Test token shows "Valid"
- [ ] Beast Campaign Bot creates campaigns
- [ ] AdSquad Expander adds ad squads
- [ ] Videos upload successfully
- [ ] Ads appear in Snapchat Ads Manager
- [ ] Real-time progress updates work
- [ ] Railway logs show no critical errors

---

## 💬 Getting Help

**Railway Issues:**
- [Railway Docs](https://docs.railway.app/)
- [Railway Discord](https://discord.gg/railway)
- [Railway Status](https://status.railway.app/)

**Snapchat API Issues:**
- [Snapchat Developer Docs](https://developers.snap.com/api/)
- [Snapchat Business Help](https://businesshelp.snapchat.com/)

**Bot Issues:**
- Check Railway logs first
- Review `SETUP_FOR_NEW_USER.md`
- Check troubleshooting section in README

---

## ⏱️ Deployment Timeline

**Total time: ~30 minutes**

- Step 1 (Fork): 2 minutes
- Step 2 (Connect Railway): 3 minutes
- Step 3 (Deploy): 5 minutes
- Step 4 (Configure): 2 minutes
- Step 5 (Add credentials): 5 minutes
- Testing: 10 minutes
- Verification: 3 minutes

---

**🎊 Congratulations!**

Your ANAS Beast Bot is now running on Railway!

You can now:
- Create unlimited Snapchat campaigns
- Upload and compress videos
- Expand existing campaigns
- Manage everything from one dashboard

**Made with ❤️ by Anas**

*Good luck with your campaigns!* 🚀
