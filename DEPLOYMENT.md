# Deployment Guide for IP Detection Application

This guide covers multiple deployment options for your Flask IP Detection application.

## Prerequisites

- Python 3.7+
- PostgreSQL database (already configured)
- Git (for version control)

---

## Option 1: Deploy to VPS/Server (Recommended)

### Using Gunicorn (Production WSGI Server)

1. **Install dependencies on server:**
```bash
pip install -r requirements.txt
pip install gunicorn
```

2. **Create a systemd service file** (`/etc/systemd/system/ipdetection.service`):
```ini
[Unit]
Description=IP Detection Flask App
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/Ip Detection
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

3. **Start the service:**
```bash
sudo systemctl daemon-reload
sudo systemctl start ipdetection
sudo systemctl enable ipdetection
```

4. **Check status:**
```bash
sudo systemctl status ipdetection
```

### Using Nginx as Reverse Proxy

1. **Install Nginx:**
```bash
sudo apt update
sudo apt install nginx
```

2. **Create Nginx config** (`/etc/nginx/sites-available/ipdetection`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **Enable and restart:**
```bash
sudo ln -s /etc/nginx/sites-available/ipdetection /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Option 2: Deploy with Docker

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

### Deploy with Docker

```bash
docker build -t ip-detection .
docker run -d -p 5000:5000 --name ip-detection ip-detection
```

---

## Option 3: Deploy to Railway

1. **Install Railway CLI:**
```bash
npm i -g @railway/cli
```

2. **Login and initialize:**
```bash
railway login
railway init
```

3. **Add PostgreSQL service** (or use your existing one)

4. **Set environment variables** in Railway dashboard:
   - `DATABASE_URL` (Railway will auto-set if using their PostgreSQL)

5. **Deploy:**
```bash
railway up
```

---

## Option 4: Deploy to Render

1. **Create account** at [render.com](https://render.com)

2. **Create new Web Service**:
   - Connect your GitHub repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

3. **Add PostgreSQL database** in Render dashboard

4. **Set environment variables**:
   - `DATABASE_URL` (auto-set by Render)

5. **Deploy** - Render will automatically deploy on git push

---

## Option 5: Deploy to Heroku

1. **Install Heroku CLI** and login:
```bash
heroku login
```

2. **Create Procfile** (`Procfile`):
```
web: gunicorn app:app
```

3. **Create runtime.txt** (`runtime.txt`):
```
python-3.11.0
```

4. **Create Heroku app:**
```bash
heroku create your-app-name
```

5. **Add PostgreSQL addon:**
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

6. **Deploy:**
```bash
git push heroku main
```

---

## Security Improvements for Production

### 1. Use Environment Variables

Update `app.py` to use environment variables:

```python
import os
from urllib.parse import quote_plus

# Database configuration from environment
db_user = os.getenv('DB_USER', 'hannan')
db_password = os.getenv('DB_PASSWORD', 'DigitalProwler(3088)')
db_host = os.getenv('DB_HOST', '168.231.111.220')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', 'ipcheck')

encoded_password = quote_plus(db_password)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}'
```

### 2. Create .env file (for local development)

```env
DB_USER=hannan
DB_PASSWORD=DigitalProwler(3088)
DB_HOST=168.231.111.220
DB_PORT=5432
DB_NAME=ipcheck
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

### 3. Add python-dotenv to requirements.txt

```
python-dotenv==1.0.0
```

### 4. Update app.py to load .env

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Production Checklist

- [ ] Use environment variables for sensitive data
- [ ] Set `FLASK_ENV=production`
- [ ] Use Gunicorn or uWSGI (not Flask dev server)
- [ ] Set up SSL/HTTPS (Let's Encrypt)
- [ ] Configure firewall rules
- [ ] Set up logging
- [ ] Configure database backups
- [ ] Set up monitoring/health checks
- [ ] Use reverse proxy (Nginx/Apache)
- [ ] Enable rate limiting
- [ ] Set up error tracking (Sentry, etc.)

---

## Quick Deploy Script (VPS)

Save as `deploy.sh`:

```bash
#!/bin/bash
cd /path/to/Ip\ Detection
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart ipdetection
```

Make executable:
```bash
chmod +x deploy.sh
```

---

## Troubleshooting

### Check if app is running:
```bash
ps aux | grep gunicorn
```

### View logs:
```bash
sudo journalctl -u ipdetection -f
```

### Test database connection:
```bash
python -c "from app import db; db.create_all(); print('DB connected!')"
```

---

## Recommended: VPS with Docker

For easiest deployment and management, use Docker on a VPS:

1. Install Docker on your server
2. Use the Dockerfile provided above
3. Use docker-compose for easy management
4. Set up Nginx reverse proxy
5. Use Let's Encrypt for SSL

This gives you the best balance of control, performance, and ease of management.
