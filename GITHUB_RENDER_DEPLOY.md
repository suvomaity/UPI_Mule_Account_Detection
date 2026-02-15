# 🚀 GitHub Pages + Render Deployment Guide

## Overview
- **Frontend**: Deployed on GitHub Pages (free, auto-deploy on push)
- **Backend**: Deployed on Render (free tier, no payment)

---

## 📋 STEP 1: Deploy Backend on Render (5-10 minutes)

### Create Backend Service:
1. Go to **https://render.com** → Sign in
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub → Select your repo
4. Fill in:
   - **Name**: `upi-mule-backend`
   - **Branch**: `master`
   - **Runtime**: Docker
   - **Instance Type**: **FREE**
5. **Add Environment Variables**:
   ```
   LOG_LEVEL=INFO
   ENVIRONMENT=production
   PORT=8000
   ```
6. Click **"Deploy Web Service"**
7. ⏳ Wait for deployment (5-10 minutes)

### Get Backend URL:
Once deployed, you'll see a URL like:
```
https://upi-mule-backend.onrender.com
```
**Save this URL!** 📌

---

## 🌐 STEP 2: Enable GitHub Pages

### Prepare Repository:
1. Go to your GitHub repo
2. Go to **Settings** → **Pages**
3. Under **"Build and deployment"**:
   - **Source**: Select **"GitHub Actions"**
   - Click **"Save"**

---

## ⚡ STEP 3: Auto-Deploy with Workflow

The GitHub Actions workflow is already set up (`.github/workflows/deploy.yml`).

### How it works:
- **Every time you push to `master`**, GitHub automatically:
  1. Builds the frontend
  2. Sets `VITE_API_BASE_URL` to your backend
  3. Deploys to GitHub Pages

### Trigger deployment:
```bash
git add .
git commit -m "Deploy to GitHub Pages"
git push origin master
```

### Check deployment:
1. Go to your repo → **Actions** tab
2. Watch the workflow run
3. When green ✅, your app is live!

---

## 🌍 STEP 4: Access Your Live App

### Frontend URL:
```
https://username.github.io/UPI_Mule_Account_Detection/
```
*(Replace `username` with your GitHub username)*

### Backend URL:
```
https://upi-mule-backend.onrender.com
```

---

## 🔧 Updating Backend URL (If needed)

If your Render backend URL changes, update it in GitHub:

### Option A: Edit Workflow (Manual)
1. Go to repo → `.github/workflows/deploy.yml`
2. Find: `${{ secrets.BACKEND_URL || 'https://upi-mule-backend.onrender.com' }}`
3. Replace with your new backend URL
4. Commit & push

### Option B: Use GitHub Secrets (Better)
1. Go to repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Name: `BACKEND_URL`
4. Value: `https://upi-mule-backend.onrender.com` (or your actual URL)
5. Workflow automatically uses it!

---

## ✅ Summary

| Component | Platform | URL | Cost |
|-----------|----------|-----|------|
| Frontend | GitHub Pages | `github.io/project` | Free ✅ |
| Backend | Render | `onrender.com` | Free ($5 credit) ✅ |
| CI/CD | GitHub Actions | Auto-deploy | Free ✅ |

---

## 🧪 Test Your Deployment

1. Open frontend: `https://username.github.io/UPI_Mule_Account_Detection/`
2. Should see your UI
3. Should communicate with backend
4. Check browser console (F12) for API errors

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| Frontend loads but blank | Check browser console (F12) for API errors |
| "Cannot connect to backend" | Ensure Render backend is running (visit its URL) |
| GitHub Actions fails | Go to **Actions** → Click workflow → View logs |
| Build fails: "Type definition not found" | Already fixed in `tsconfig.json` |

---

## 🔄 Auto-Deploy on Push

Every git push automatically:
```
master push → GitHub Actions triggers → Build & Deploy → Live! ✨
```

No manual deployment needed! 🎉

---

## 💡 Pro Tips

✅ **Monitor frontend deployment**: Actions tab shows build status  
✅ **Monitor backend**: Render dashboard shows logs  
✅ **Update backend URL**: Use GitHub Secrets (easier to maintain)  
✅ **Rollback**: Just undo last commit & push

---

**You're ready! Push to GitHub now:** 🚀
```bash
git push origin master
```
