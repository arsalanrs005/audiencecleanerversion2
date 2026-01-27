# Render Configuration Guide

## Required Settings (Main Configuration Page)

### Basic Settings
- **Name**: `audience-cleaner` (or any name you like)
- **Environment**: `Python 3`
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `main`

### Build & Deploy
- **Build Command**: `pip install -r requirements_web.txt`
- **Start Command**: `python app.py`

## Advanced Settings (What You're Looking At)

### Secret Files
- **Leave empty** - No secrets needed for this app
- (You can add `.env` file here later if needed)

### Health Check Path
- **Set to**: `/health` ✅
- This is already correct!

### Registry Credential
- **Leave as**: `No credential`
- Not needed (we're not using private Docker images)

### Docker Settings (Skip These)
These only apply if you're using Docker. Since we're using Python build:
- **Docker Build Context Directory**: Leave empty (not used)
- **Dockerfile Path**: Leave empty (not used)
- **Docker Command**: Leave empty (not used)

### Pre-Deploy Command
- **Leave empty** - No migrations or setup needed

### Auto-Deploy
- **Keep enabled** ✅
- This automatically deploys when you push to GitHub

### Build Filters
- **Leave default** (empty)
- Or add if you want to ignore certain files:
  ```
  *.csv
  test_*.csv
  ```

## Summary

**Only configure these:**
- ✅ Health Check Path: `/health`
- ✅ Auto-Deploy: Enabled
- Everything else: Leave as default/empty

## After Configuration

1. Click **"Create Web Service"**
2. Wait for build to complete (2-3 minutes)
3. Your API will be live at: `https://your-app-name.onrender.com`

## Test Your Deployment

Once deployed, test with:
```bash
curl https://your-app-name.onrender.com/health
```

Should return: `{"status":"healthy","service":"audience-cleaner-api"}`


