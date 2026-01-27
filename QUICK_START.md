# Quick Deployment Guide

## 🚀 Fastest Way: Deploy with Docker

### 1. Build and Run
```bash
docker build -t ip-detection .
docker run -d -p 5000:5000 --name ip-detection ip-detection
```

### 2. Or use Docker Compose
```bash
docker-compose up -d
```

Your app will be available at `http://localhost:5000`

---

## 🌐 Deploy to Cloud Platforms

### Railway (Easiest)
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Connect your repository
4. Add PostgreSQL service (or use your existing DB)
5. Set environment variables if needed
6. Deploy!

### Render (Free Tier Available)
1. Go to [render.com](https://render.com)
2. Create new "Web Service"
3. Connect GitHub repository
4. Build: `pip install -r requirements.txt`
5. Start: `gunicorn app:app`
6. Add PostgreSQL database
7. Deploy!

### Heroku
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

---

## 🖥️ Deploy to VPS/Server

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
pip install gunicorn
```

### Step 2: Run with Gunicorn
```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

### Step 3: Run as Background Service
```bash
nohup gunicorn --workers 4 --bind 0.0.0.0:5000 app:app > app.log 2>&1 &
```

### Step 4: Set up Nginx (Optional)
See `DEPLOYMENT.md` for Nginx configuration.

---

## 🔐 Environment Variables

For production, set these environment variables:

```bash
export DB_USER=hannan
export DB_PASSWORD=DigitalProwler(3088)
export DB_HOST=168.231.111.220
export DB_PORT=5432
export DB_NAME=ipcheck
```

Or create a `.env` file (copy from `.env.example`)

---

## ✅ Verify Deployment

1. Check if app is running:
   ```bash
   curl http://localhost:5000
   ```

2. Test database connection:
   ```bash
   curl http://localhost:5000/view-ips
   ```

3. Visit in browser:
   ```
   http://your-server-ip:5000
   ```

---

## 📝 Notes

- The app will automatically create database tables on first run
- Make sure PostgreSQL is accessible from your deployment server
- For production, use HTTPS (Let's Encrypt with Nginx)
- See `DEPLOYMENT.md` for detailed instructions
