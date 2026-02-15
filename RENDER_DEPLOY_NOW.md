# 🚀 Deploy on Render (FREE) - Step by Step

## ✅ Prerequisites
- GitHub account with your repo pushed
- Render.com account (free signup)

---

## 📋 STEP 1: Sign Up on Render (100% Free)

1. Go to **https://render.com**
2. Click **"Sign Up"**
3. Click **"Continue with GitHub"** (authorize Render)
4. **DO NOT add payment** - just skip/close that page
5. Go to Dashboard

---

## 🔧 STEP 2: Deploy Backend (Free Web Service)

### Create Backend Service:
1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Choose **"Existing Code"** → Connect your GitHub repo
4. Fill in details:
   - **Name**: `upi-mule-backend`
   - **Branch**: `main`
   - **Runtime**: `Docker`
   - **Build Command**: (leave empty)
   - **Start Command**: (leave empty)
   - **Instance Type**: **FREE** (scroll down to find this!)

5. Click **"Create Web Service"**
6. ⏳ **Wait 5-10 minutes** for deployment
7. Once deployed, copy your Backend URL (looks like: `https://upi-mule-backend.onrender.com`)
8. **SAVE THIS URL** 📌

---

## 🎨 STEP 3: Deploy Frontend (Free Web Service)

### Create Frontend Service:
1. Click **"New +"** button again
2. Select **"Web Service"**
3. Choose **"Existing Code"** → Same GitHub repo
4. Fill in details:
   - **Name**: `upi-mule-frontend`
   - **Branch**: `main`
   - **Runtime**: `Docker`
   - **Build Command**: (leave empty)
   - **Start Command**: (leave empty)
   - **Instance Type**: **FREE** ⭐

### Add Environment Variables:
5. Scroll to **"Environment"** section
6. Add these variables:
   ```
   VITE_API_BASE_URL=https://upi-mule-backend.onrender.com
   NODE_ENV=production
   ```
   (Use your actual backend URL from Step 2)

7. Click **"Create Web Service"**
8. ⏳ **Wait 5-10 minutes** for deployment

---

## ✨ STEP 4: Your App is LIVE!

### Access your app:
- **Frontend**: `https://upi-mule-frontend.onrender.com`
- **Backend API**: `https://upi-mule-backend.onrender.com`
- **Test Backend**: `https://upi-mule-backend.onrender.com/health`

---

## ⚠️ Important: Free Tier Behavior

| Behavior | What happens |
|----------|-------------|
| **Sleep** | After 15 min with no traffic, service sleeps |
| **Wake up** | First request after sleep takes ~30 sec |
| **After wake** | Super fast responses |
| **Usage limit** | 100 GB/month bandwidth (plenty for demo) |

**This is NORMAL and expected for free tier!**

---

## 🔄 STEP 5: Update Deployment (Automatic)

Every time you push to GitHub:
```bash
git add .
git commit -m "Update"
git push origin main
```

**Render auto-redeploys!** No manual steps needed.

---

## 🧪 Test Your Deployment

### Test Backend Health:
```bash
curl https://upi-mule-backend.onrender.com/health
```
Should return: `{"status": "healthy"}` (or similar)

### Test Frontend:
Open in browser: `https://upi-mule-frontend.onrender.com`

---

## 🐛 If Something Goes Wrong

### Issue: Frontend shows blank/error
**Fix**: 
1. Go to Frontend service → **Settings**
2. Scroll to **"Environment"**
3. Verify `VITE_API_BASE_URL` is exactly right (check spelling!)
4. Click **"Manual Deploy"** → **"Manual Deploy"** button
5. Wait for redeploy

### Issue: Backend not responding
**Fix**:
1. Click Backend service
2. Scroll to **"Logs"** (bottom)
3. Look for red error messages
4. Common issue: Check if `requirements.txt` exists in backend/

### Issue: Deployment stuck/fails
**Fix**:
1. Go to service → **Settings**
2. Click **"Clear Build Cache & Deploy"**
3. Wait again

---

## 💡 Pro Tips

✅ **Keep services awake** (Optional):
- Add external monitoring service to ping `/health` every 10 min
- Or upgrade to paid plan ($7+/month)

✅ **Track deployments**:
- Render Dashboard → Click service → **"Events"** tab

✅ **View logs in real-time**:
- Click service → **"Logs"** → See everything happening

✅ **Share your demo**:
- Send this URL: `https://upi-mule-frontend.onrender.com`
- Works great for presentations!

---

## ✅ Summary

| Step | Time | Action |
|------|------|--------|
| 1 | 2 min | Sign up on Render |
| 2 | 10 min | Deploy Backend |
| 3 | 10 min | Deploy Frontend |
| 4 | 1 min | Test URLs |
| **Total** | **~25 min** | **LIVE!** |

---

**You're ready to deploy! Start with STEP 1 now.** 🚀
