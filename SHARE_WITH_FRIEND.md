# 🚀 Share This With Your Friend

Hey! I fixed the OAuth redirect URL issue. Now everyone can deploy their own bot on Railway and it works perfectly!

## What Changed?

The bot now **auto-detects** its own Railway URL, so OAuth works for every deployment.

## Send This to Your Friend:

---

# 🎯 How to Set Up ANAS Beast Bot (30 minutes)

## Quick Setup:

1. **Deploy on Railway:**
   - Go to: https://github.com/anasr4/beast-dashboard
   - Fork the repo (click Fork button)
   - Deploy on Railway: https://railway.app
   - Connect your forked repo
   - Wait 5 minutes for deployment

2. **Get Your Railway URL:**
   - In Railway dashboard, go to Settings → Domains → Generate Domain
   - You'll get: `https://beast-dashboard-production-xxxxx.up.railway.app`
   - **Copy this URL!**

3. **Create Snapchat App:**
   - Go to: https://business.snapchat.com/apps
   - Create new OAuth app
   - **IMPORTANT:** Set Redirect URL to:
     ```
     https://YOUR-RAILWAY-URL/api/oauth/callback
     ```
     Example: `https://beast-dashboard-production-12345.up.railway.app/api/oauth/callback`
   - Get your Client ID and Client Secret

4. **Get Snapchat Credentials:**
   - Follow this guide: https://github.com/anasr4/beast-dashboard/blob/main/QUICK_START_GUIDE.md
   - You need:
     - Client ID
     - Client Secret
     - Refresh Token
     - Ad Account ID

5. **Configure Bot:**
   - Open your Railway URL
   - Click "Token Manager"
   - Enter your credentials
   - Click "Authorize with Snapchat"
   - Done! ✅

## 📖 Full Guides:

- **Quick Start (0 to 100):** [QUICK_START_GUIDE.md](https://github.com/anasr4/beast-dashboard/blob/main/QUICK_START_GUIDE.md)
- **OAuth Setup:** [OAUTH_SETUP.md](https://github.com/anasr4/beast-dashboard/blob/main/OAUTH_SETUP.md)
- **Railway Deployment:** [RAILWAY_DEPLOYMENT.md](https://github.com/anasr4/beast-dashboard/blob/main/RAILWAY_DEPLOYMENT.md)

## ⚠️ Important:

**The redirect URL in Snapchat MUST match your Railway URL exactly:**

✅ Correct: `https://beast-dashboard-production-12345.up.railway.app/api/oauth/callback`
❌ Wrong: `https://web-production-95efb.up.railway.app/api/oauth/callback` (my URL)

Each Railway deployment gets its own unique URL. The bot auto-detects yours!

## 🆘 If OAuth Doesn't Work:

1. Check redirect URL in Snapchat matches your Railway URL exactly
2. Must include `/api/oauth/callback` at the end
3. No trailing slash
4. Use `https://` not `http://`

See [OAUTH_SETUP.md](https://github.com/anasr4/beast-dashboard/blob/main/OAUTH_SETUP.md) for troubleshooting.

## ✅ When It Works:

You'll be able to:
- Create 100s of ads in minutes
- Upload unlimited videos
- Exact ad count guarantee (request 100 = get 100)
- Auto-retry failed uploads
- Real-time progress tracking

Start here: https://github.com/anasr4/beast-dashboard

---

## 💡 Quick Answer to "What redirect URL do I use?"

**Use YOUR Railway URL, not mine!**

After you deploy on Railway, you'll get a URL like:
```
https://beast-dashboard-production-XXXXX.up.railway.app
```

Then set redirect URL in Snapchat to:
```
https://beast-dashboard-production-XXXXX.up.railway.app/api/oauth/callback
```

The bot auto-detects this URL, so OAuth will work perfectly for you!
