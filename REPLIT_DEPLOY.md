# Deploy on Replit (Easiest & Free!)

## Why Replit? 
✅ One-click deploy  
✅ No CLI needed  
✅ Works in browser  
✅ Completely free  
✅ Live URL in seconds  

---

## 🚀 Deploy in 3 Steps

### Step 1: Go to Replit
1. Open [replit.com](https://replit.com)
2. **Sign up** (free account, use GitHub)

### Step 2: Import Your GitHub Repo
1. Click **"Create"** → **"Import from GitHub"**
2. Paste your repo URL: `https://github.com/YOUR_USERNAME/UPI_Mule_Account_Detection`
3. Click **"Import"**
4. Wait for Replit to set up (~1 minute)

### Step 3: Run & Deploy
1. Click the **"Run"** button (green play button at top)
2. Replit starts your app automatically
3. **Your live URL appears** on the right side
4. Click the URL to see your app live! 🎉

---

## 🌐 Access Your App

After running:
- **Frontend URL**: `https://UPI-Mule-Account-Detection.YOUR_USERNAME.repl.co`
- **Backend available** at same domain with `/api` prefix
- Share this link with anyone!

---

## ⚙️ Environment Setup (If Needed)

If app doesn't start automatically:

1. Click **"Secrets"** (lock icon on left)
2. Add if needed:
   ```
   VITE_API_BASE_URL=https://UPI-Mule-Account-Detection.YOUR_USERNAME.repl.co
   NODE_ENV=production
   LOG_LEVEL=INFO
   ```

3. Click **"Run"** again

---

## 📝 Configure Replit to Run Your Stack

1. In Replit, click **".replit"** file (should appear)
2. If not, create it in root with:
   ```toml
   run = "bash start-all.sh"
   ```

3. Or manually run in **Shell**:
   ```bash
   # Terminal in Replit
   cd backend && python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 &
   cd frontend && npm install && npm run dev
   ```

---

## ✅ Your App is LIVE!

1. ✅ Repo imported on Replit
2. ✅ Click Run
3. ✅ Get shareable URL
4. ✅ Share with anyone

**No payment. No deployment config. Just click and run!** 🎉

---

## 💡 Tips

- **Keep Replit tab open** (free tier sleeps when you close browser)
- **Upgrade to Replit Pro** ($10/month) for always-on hosting
- **Share URL** with anyone - they can see your live demo
- **Edit code** directly in Replit and see changes instantly

---

## 🎯 Next Steps

1. Go to [replit.com](https://replit.com)
2. Sign up with GitHub
3. Import repo
4. Click **Run**
5. Done! 🚀

Questions? Let me know!
