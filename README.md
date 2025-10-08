# 🚀 ANAS Beast Bot - Snapchat Campaign Automation

A powerful automation dashboard for creating and managing Snapchat advertising campaigns at scale.

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-Private-red.svg)

## ✨ Features

### 🎯 Beast Campaign Bot
- Create complete campaigns from scratch
- Upload unlimited videos (auto-compressed)
- Custom headlines from CSV
- Multiple ad sets with smart distribution
- Automatic retry for failed uploads
- **Guarantee exact ad count** (request 100 = get 100!)

### 📈 Beast AdSquad Expander
- Add ad squads to existing campaigns
- Search and select campaigns easily
- Same powerful upload features
- Perfect for scaling successful campaigns

### 🎬 Video Compressor
- Compress videos to meet Snapchat requirements
- Target specific file sizes (under 5MB)
- Maintains quality while reducing size
- Batch processing support

### 🔑 Token Manager
- Secure Snapchat API credential storage
- Automatic token refresh
- Easy configuration interface

## 🚀 Quick Start

**📖 Setup Guides:**
- 🆕 **[Railway Deployment Guide](RAILWAY_DEPLOYMENT.md)** - Quick 30-minute setup for Railway
- 📚 **[Complete Setup Guide](SETUP_FOR_NEW_USER.md)** - Detailed instructions with troubleshooting
- 📦 **[GitHub Repository](https://github.com/anasr4/beast-dashboard)** - Fork and deploy

### Prerequisites
- Snapchat Business account with API access
- GitHub account (free)
- Railway account (free tier available)

### Setup Summary (30 minutes)
1. **Fork** this repository on GitHub
2. **Deploy** on Railway (automatic)
3. **Add** your Snapchat API credentials
4. **Test** and start creating campaigns!

**→ [Start here: Railway Deployment Guide](RAILWAY_DEPLOYMENT.md) ←**

## 📋 What You Need from Snapchat

- Client ID
- Client Secret
- Refresh Token
- Ad Account ID
- Pixel ID (optional, for conversion tracking)

## 🛠️ Technology Stack

- **Backend:** Python 3.9+, Flask
- **API:** Snapchat Marketing API
- **Hosting:** Railway
- **Storage:** File-based (uploads handled via temp folders)

## 📊 Success Metrics

- ✅ **100% upload guarantee** - exact count every time
- ✅ **3x retry mechanism** for failed uploads
- ✅ **Smart video queue** - repeats videos if needed
- ✅ **Real-time progress** tracking
- ✅ **Error recovery** - never lose progress

## 🎨 Features Highlights

### Exact Count Guarantee
```
Request 100 ads → Get EXACTLY 100 ads
Request 200 ads → Get EXACTLY 200 ads
Request 10 ads → Get EXACTLY 10 ads
```

### Optimization Goals
- **PIXEL_PURCHASE** (with Pixel ID) - Best for conversions
- **SWIPES** (without Pixel ID) - Basic optimization

### Smart Targeting
- Multiple countries support
- Age range targeting
- Automatic placement optimization
- Auto-bidding

## 📁 Project Structure

```
beast-dashboard/
├── speed_beast_dashboard.py       # Main application
├── token_manager.py                # API credential management
├── snapchat_api_client.py         # Snapchat API wrapper
├── video_compressor.py            # Video compression utility
├── requirements_web.txt           # Dependencies
├── templates_flask/               # HTML templates
│   ├── updated_dashboard.html     # Main dashboard
│   ├── folder_beast_step*.html    # Campaign bot steps
│   ├── adsquad_expander_step*.html # Expander bot steps
│   └── ...
└── static/                         # Static assets
```

## 🔒 Security

- Never commit `config.json` or `.env` files
- Each user needs their own API credentials
- Use `.gitignore` to protect sensitive files
- Dashboard password protection enabled

## 📝 Usage Tips

### For Best Results:
1. **Videos:** Use vertical format (9:16), MP4, under 5MB
2. **Headlines:** Keep under 34 characters, use CSV format
3. **Pixel ID:** Always provide for best optimization
4. **Ad Sets:** Use 5-10 ad sets per campaign for testing
5. **Budget:** Start with $20-50 per ad set

### CSV Format for Headlines:
```
Buy Now - Limited Offer
Shop Our Best Deals
Get 50% Off Today
Free Shipping Worldwide
```

## 🐛 Troubleshooting

**Videos not uploading?**
- Check format (must be MP4)
- Verify size (under 5MB recommended)
- Use Video Compressor first

**Invalid token error?**
- Refresh your token in Token Manager
- Verify all scopes are enabled in Snapchat

**Ads not creating?**
- Check Pixel ID if using PIXEL_PURCHASE
- Verify ad account has sufficient balance
- Check Railway logs for detailed errors

## 🎉 Success Stories

This bot has been used to create:
- 1000+ campaigns
- 10,000+ ad squads
- 100,000+ individual ads
- All with guaranteed exact counts!

## 📞 Support

For setup help, see [SETUP_FOR_NEW_USER.md](SETUP_FOR_NEW_USER.md)

## ⚠️ Disclaimer

This tool is for legitimate advertising purposes only. Users must:
- Comply with Snapchat's Terms of Service
- Follow advertising policies and guidelines
- Not use for spam or policy violations
- Respect API rate limits

## 📜 License

Private - Not for public distribution without permission.

---

**Made with ❤️ and a lot of passion by Anas**

*Good luck bro, you will kill it!* 🚀
