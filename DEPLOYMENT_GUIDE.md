# PECS Learning System - Deployment Guide

## Deploy Anywhere, Access from Mobile/Desktop

This guide shows you how to deploy the PECS Learning System as a **Progressive Web App (PWA)** that works on any device.

---

## Quick Start (Local Testing)

### 1. Build and run with Docker

```bash
cd /home/user/PECS-learner

# Build and start
docker-compose -f docker-compose.nicegui.yml up --build

# Access from:
# - Your computer: http://localhost:8080
# - Your phone (same WiFi): http://<your-local-ip>:8080
```

### 2. Find your local IP

**On Linux/Mac:**
```bash
ip addr show | grep "inet " | grep -v 127.0.0.1
# or
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**On Windows:**
```bash
ipconfig | findstr IPv4
```

### 3. Access from mobile

1. Make sure your phone is on the **same WiFi network**
2. Open browser on phone: `http://192.168.x.x:8080` (use your IP from step 2)
3. Tap "Install" to add to home screen (becomes a PWA!)

---

## Production Deployment (Access from Anywhere)

### Option 1: Railway (Easiest - Free Tier Available) ⭐ RECOMMENDED

**Why Railway?**
- ✅ Free tier: 500 hours/month
- ✅ Automatic HTTPS
- ✅ One-click deploy
- ✅ Git integration
- ✅ Custom domains

**Steps:**

1. **Prepare your code**
```bash
# Create Procfile for Railway
echo "web: python nicegui_app_pwa.py" > Procfile

# Make sure Dockerfile.nicegui exists (already created)
# Railway will auto-detect it
```

2. **Deploy to Railway**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Get your URL
railway open
```

3. **Configure environment variables** (in Railway dashboard)
```
PORT=8080
OPENAI_API_KEY=your-key-here
NICEGUI_STORAGE_PATH=/app/data/nicegui_storage
```

4. **Access your app**
- Railway will give you a URL like: `https://pecs-learning-production.up.railway.app`
- Share this URL with anyone!
- Works on mobile, tablet, desktop

**Cost:** Free tier (500 hours/month), then ~$5/month

---

### Option 2: Render (Free Tier)

**Why Render?**
- ✅ Free tier with no credit card
- ✅ Automatic HTTPS
- ✅ Easy database backups
- ✅ Custom domains

**Steps:**

1. **Create `render.yaml`**
```yaml
services:
  - type: web
    name: pecs-learning
    env: docker
    plan: free
    healthCheckPath: /
    envVars:
      - key: PORT
        value: 8080
      - key: OPENAI_API_KEY
        sync: false
    disk:
      name: pecs-data
      mountPath: /app/data
      sizeGB: 1
```

2. **Deploy**
   - Go to https://render.com
   - Connect your GitHub repo
   - Select `render.yaml` blueprint
   - Click "Create"
   - Wait ~5 minutes for deployment

3. **Access**
   - Render URL: `https://pecs-learning.onrender.com`

**Limitations:**
- Free tier sleeps after 15 minutes of inactivity (wakes up in ~30 seconds on first visit)
- Perfect for personal use or testing

**Cost:** Free tier, then $7/month for always-on

---

### Option 3: DigitalOcean App Platform ($5/month)

**Why DigitalOcean?**
- ✅ Reliable, always-on
- ✅ Easy scaling
- ✅ Good performance

**Steps:**

1. **Push code to GitHub/GitLab**

2. **Create App on DigitalOcean**
   - Go to https://cloud.digitalocean.com/apps
   - Click "Create App"
   - Connect GitHub repo
   - Select `Dockerfile.nicegui`
   - Set environment variables:
     ```
     PORT=8080
     OPENAI_API_KEY=your-key
     ```

3. **Deploy**
   - Click "Create Resources"
   - Wait ~5 minutes

4. **Access**
   - DigitalOcean URL: `https://pecs-learning-xxxxx.ondigitalocean.app`
   - Add custom domain (optional)

**Cost:** $5/month (Basic plan)

---

### Option 4: Google Cloud Run (Pay-per-use)

**Why Cloud Run?**
- ✅ Only pay when in use
- ✅ Auto-scaling
- ✅ Very cheap for low traffic

**Steps:**

1. **Install Google Cloud SDK**
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

2. **Build and deploy**
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/pecs-learning

# Deploy
gcloud run deploy pecs-learning \
  --image gcr.io/YOUR_PROJECT_ID/pecs-learning \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars OPENAI_API_KEY=your-key
```

3. **Access**
   - Google will give you: `https://pecs-learning-xxxxx-uc.a.run.app`

**Cost:** Free tier: 2 million requests/month, then ~$0.10 per million requests

---

### Option 5: Self-Hosted (Your Own Server/VPS)

**Why self-host?**
- ✅ Full control
- ✅ No monthly fees (after VPS cost)
- ✅ Can use cheap VPS ($5/month)

**Providers:**
- Linode: $5/month (1GB RAM)
- DigitalOcean Droplet: $6/month
- Vultr: $5/month
- Hetzner: €4.5/month

**Steps:**

1. **Setup VPS** (Ubuntu 22.04 recommended)

2. **Install Docker**
```bash
# SSH into your VPS
ssh root@your-vps-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y
```

3. **Clone and deploy**
```bash
# Clone your repo
git clone https://github.com/your-username/PECS-learner.git
cd PECS-learner

# Create .env file
echo "OPENAI_API_KEY=your-key-here" > .env

# Start app
docker-compose -f docker-compose.nicegui.yml up -d
```

4. **Setup HTTPS with Caddy (automatic SSL)**

Create `Caddyfile`:
```
your-domain.com {
    reverse_proxy localhost:8080
}
```

Install and run Caddy:
```bash
# Install Caddy
apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install caddy

# Copy Caddyfile
cp Caddyfile /etc/caddy/Caddyfile

# Start Caddy
systemctl restart caddy
```

5. **Access**
   - Your domain: `https://your-domain.com`
   - Direct IP: `http://your-vps-ip:8080`

**Cost:** $5/month VPS + domain name (~$12/year)

---

## Making it a PWA (Progressive Web App)

The app is already configured as a PWA! Here's what users should do:

### On iPhone/iPad (Safari)

1. Open `https://your-app-url.com`
2. Tap the **Share** button (box with arrow)
3. Scroll down and tap **"Add to Home Screen"**
4. Tap **"Add"**
5. App icon appears on home screen!
6. Opens in fullscreen mode (looks like native app)

### On Android (Chrome)

1. Open `https://your-app-url.com`
2. Tap the menu button (3 dots)
3. Tap **"Install app"** or **"Add to Home Screen"**
4. Tap **"Install"**
5. App appears in app drawer!
6. Can be launched like any native app

### On Desktop (Chrome/Edge)

1. Visit `https://your-app-url.com`
2. Click the **install icon** in address bar (or ⋮ menu → "Install...")
3. Click **"Install"**
4. App opens in its own window!

---

## PWA Features Included

✅ **Installable** - Add to home screen on any device
✅ **Offline-capable** - Service worker caches key resources
✅ **App-like experience** - Fullscreen mode, no browser UI
✅ **Fast loading** - Cached assets load instantly
✅ **Responsive** - Works on phone, tablet, desktop
✅ **Push notifications** - Can be added later
✅ **Background sync** - Can be added later

---

## Custom Domain Setup

### For Railway/Render/DigitalOcean

1. **Buy a domain** (Namecheap, Google Domains, Cloudflare)

2. **Add domain in platform dashboard**
   - Railway: Settings → Domains → Add Custom Domain
   - Render: Settings → Custom Domains → Add
   - DigitalOcean: Settings → Domains → Add

3. **Update DNS records** (at your domain registrar)
   - Add CNAME record:
     - Name: `@` or `www`
     - Value: provided by platform (e.g., `pecs-learning.up.railway.app`)

4. **Wait for SSL** (~5-15 minutes for automatic HTTPS)

5. **Done!** Access at `https://yourdomain.com`

---

## Environment Variables

Create `.env` file for local development:

```bash
# .env
OPENAI_API_KEY=sk-your-key-here
NICEGUI_STORAGE_PATH=/app/data/nicegui_storage
PORT=8080
```

**For production**, set these in your platform:
- Railway: Dashboard → Variables
- Render: Dashboard → Environment
- DigitalOcean: App Settings → Environment Variables
- Google Cloud Run: `gcloud run deploy --set-env-vars KEY=value`

---

## Database Persistence

The app uses SQLite database stored in `/app/data/pecs.db`.

### Backup database

**Local (Docker):**
```bash
# Database is in ./data directory (mounted volume)
cp ./data/pecs.db ./data/pecs.db.backup
```

**Production (most platforms):**
- Railway: Automatic persistent disk
- Render: Persistent disk (configured in render.yaml)
- DigitalOcean: Persistent volume
- Cloud Run: Need to use Cloud SQL or external storage

### Restore database

```bash
# Stop app
docker-compose -f docker-compose.nicegui.yml down

# Replace database
cp pecs.db.backup ./data/pecs.db

# Restart
docker-compose -f docker-compose.nicegui.yml up -d
```

---

## Monitoring & Logs

### Railway
```bash
railway logs
```

### Render
- Dashboard → Logs tab

### DigitalOcean
- App → Runtime Logs

### Docker (self-hosted)
```bash
docker-compose -f docker-compose.nicegui.yml logs -f
```

---

## Cost Comparison

| Platform | Free Tier | Paid | Best For |
|----------|-----------|------|----------|
| **Railway** | 500 hrs/month | ~$5/month | Easy setup, great DX |
| **Render** | Yes (sleeps) | $7/month | Free testing, low traffic |
| **DigitalOcean** | No | $5/month | Reliable, always-on |
| **Google Cloud Run** | 2M req/month | Pay-per-use | Variable traffic |
| **Self-hosted VPS** | No | $5/month + domain | Full control, learning |

---

## Recommended Setup for Different Use Cases

### Personal Use (Just You)
→ **Render Free Tier** or **Railway Free Tier**
- Cost: $0
- Sleeps when inactive (wakes in 30s)
- Perfect for solo learning

### Small Team (2-10 people)
→ **Railway** or **DigitalOcean**
- Cost: $5-7/month
- Always on, fast
- Easy management

### Public/Commercial
→ **Google Cloud Run** or **DigitalOcean App Platform**
- Cost: Scales with usage
- Auto-scaling
- Better performance

### Learning/Experimenting
→ **Self-hosted VPS**
- Cost: $5/month
- Full control
- Learn DevOps skills

---

## Troubleshooting

### App won't install as PWA

**Check:**
1. Must be served over HTTPS (not `http://`)
2. Must have valid `manifest.json`
3. Must have service worker
4. Icons must be present in `/static/icons/`

**Solution:**
```bash
# Generate icons from a single 512x512 image
# Use https://www.pwabuilder.com/imageGenerator
# Download and place in static/icons/
```

### Database not persisting

**Check Docker volumes:**
```bash
docker-compose -f docker-compose.nicegui.yml down
docker volume ls
# Make sure ./data is mounted correctly
```

### Can't access from other devices

**Check firewall:**
```bash
# On Linux, allow port 8080
sudo ufw allow 8080

# Make sure Docker is running with host 0.0.0.0
# Edit nicegui_app_pwa.py line ~500: host='0.0.0.0'
```

### Slow performance

**Enable production mode:**
```python
# In nicegui_app_pwa.py
ui.run(
    port=8080,
    host='0.0.0.0',
    reload=False,  # Disable in production!
    show=False,
    storage_secret='your-secret-key'  # Add for production!
)
```

---

## Next Steps

1. **Test locally** with Docker
2. **Deploy to Railway/Render** (easiest)
3. **Share URL** with users
4. **Install as PWA** on your phone
5. **Add custom domain** (optional)
6. **Setup backups** (important!)

---

## Security Checklist for Production

- [ ] Change `storage_secret` in `nicegui_app_pwa.py`
- [ ] Use environment variables for API keys (never commit)
- [ ] Enable HTTPS (automatic on most platforms)
- [ ] Setup regular database backups
- [ ] Add authentication if needed (NiceGUI supports OAuth)
- [ ] Review CORS settings if adding mobile app later

---

## Resources

- **NiceGUI Docs:** https://nicegui.io
- **Railway Docs:** https://docs.railway.app
- **Render Docs:** https://render.com/docs
- **PWA Builder:** https://www.pwabuilder.com
- **Icon Generator:** https://www.pwabuilder.com/imageGenerator

---

## Questions?

Check the documentation or open an issue in the GitHub repo!
