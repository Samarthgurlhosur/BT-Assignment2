# Deployment Guide

## Production Deployment Instructions

### 1. Pre-Deployment Checklist

- [ ] Review all security settings
- [ ] Update SECRET_KEY in production
- [ ] Set FLASK_ENV=production
- [ ] Update DATABASE_URI to PostgreSQL
- [ ] Enable HTTPS
- [ ] Set up email service
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Create backup strategy
- [ ] Test all features
- [ ] Performance testing completed

---

## Option A: Heroku Deployment

### Step 1: Install Heroku CLI
```bash
# Windows
choco install heroku-cli

# macOS
brew install heroku/brew/heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

### Step 2: Create Procfile
```bash
# Create Procfile in project root
echo "web: gunicorn app:app" > Procfile
```

### Step 3: Create runtime.txt
```bash
# Specify Python version
echo "python-3.10.12" > runtime.txt
```

### Step 4: Add Production Dependencies
```bash
pip install gunicorn
pip freeze > requirements.txt
```

### Step 5: Login to Heroku
```bash
heroku login
```

### Step 6: Create Heroku App
```bash
heroku create land-registry-app
```

### Step 7: Set Environment Variables
```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set SQLALCHEMY_DATABASE_URI=postgresql://user:pass@host/db
```

### Step 8: Deploy
```bash
git push heroku main
```

### Step 9: Initialize Database
```bash
heroku run flask init_db
heroku run flask seed_data
```

---

## Option B: AWS Deployment

### Step 1: Create EC2 Instance
1. Launch EC2 instance (Ubuntu 20.04 or later)
2. Install Python 3.10+
3. Install dependencies:
```bash
sudo apt update
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx
```

### Step 2: Setup Project
```bash
git clone <your-repo>
cd land-registry
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Setup PostgreSQL Database
```bash
sudo -u postgres psql
CREATE DATABASE land_registry;
CREATE USER lr_user WITH PASSWORD 'strong-password-here';
ALTER ROLE lr_user SET client_encoding TO 'utf8';
ALTER ROLE lr_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE lr_user SET default_transaction_deferrable TO on;
ALTER ROLE lr_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE land_registry TO lr_user;
\q
```

### Step 4: Create Systemd Service File
```bash
sudo nano /etc/systemd/system/land-registry.service
```

Add:
```
[Unit]
Description=Land Registry Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/land-registry
Environment="PATH=/home/ubuntu/land-registry/venv/bin"
ExecStart=/home/ubuntu/land-registry/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

### Step 5: Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable land-registry
sudo systemctl start land-registry
```

### Step 6: Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/land-registry
```

Add:
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

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/land-registry /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 7: Setup HTTPS with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## Option C: Docker Deployment

### Step 1: Create Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "app.py"]
```

### Step 2: Create docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_USER: lr_user
      POSTGRES_PASSWORD: secure-password
      POSTGRES_DB: land_registry
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      FLASK_ENV: production
      SECRET_KEY: your-secret-key
      SQLALCHEMY_DATABASE_URI: postgresql://lr_user:secure-password@db:5432/land_registry
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads

volumes:
  postgres_data:
```

### Step 3: Build and Run
```bash
docker-compose up -d
docker-compose exec web flask init_db
docker-compose exec web flask seed_data
```

---

## Environment Configuration

### Production .env File
```bash
# Flask
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-very-long-secret-key-min-32-chars

# Database
SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost/land_registry
SQLALCHEMY_TRACK_MODIFICATIONS=False

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Strict

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Blockchain
BLOCKCHAIN_DIFFICULTY=3

# File Upload
MAX_CONTENT_LENGTH=52428800

# Server
HOST=0.0.0.0
PORT=5000
```

---

## Database Migration

### From SQLite to PostgreSQL
```bash
# Export from SQLite
sqlite3 land_registry.db .dump > data.sql

# Create PostgreSQL database
createdb -U postgres land_registry

# Import data
psql -U postgres land_registry < data.sql
```

---

## SSL/TLS Certificate Setup

### Using Let's Encrypt with Certbot
```bash
sudo certbot certonly --standalone -d your-domain.com

# Renew automatically
sudo apt install certbot
echo "0 0,12 * * * /opt/certbot/bin/python -c 'import random; import subprocess; subprocess.check_call(\"sudo /usr/bin/certbot renew -q\".split())' 2>&1 | logger -t certbot" | sudo tee -a /etc/crontab > /dev/null
```

---

## Monitoring & Logging

### Setup Application Logging
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/land_registry.log', 
                                      maxBytes=10240000, 
                                      backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
```

### Monitor with PM2
```bash
npm install -g pm2

# Create ecosystem.config.js
pm2 start "python app.py" --name land-registry
pm2 save
pm2 startup
pm2 logs
```

---

## Performance Optimization

### 1. Enable Caching
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/api/lands')
@cache.cached(timeout=300)
def get_lands():
    # ...
```

### 2. Database Connection Pooling
```python
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

### 3. Image Optimization
```python
from PIL import Image

def optimize_image(file_path, max_width=1200):
    img = Image.open(file_path)
    img.thumbnail((max_width, max_width))
    img.save(file_path, optimize=True, quality=85)
```

---

## Backup Strategy

### Daily Backups
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/land_registry"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_BACKUP="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Backup database
pg_dump -U lr_user land_registry > $DB_BACKUP

# Backup uploads
tar -czf "$BACKUP_DIR/uploads_$TIMESTAMP.tar.gz" /home/ubuntu/land-registry/uploads

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete
```

Schedule with cron:
```bash
0 2 * * * /home/ubuntu/land-registry/backup.sh
```

---

## Security Hardening

### 1. Disable Debug Mode
```python
app.config['DEBUG'] = False
```

### 2. Add Rate Limiting
```bash
pip install Flask-Limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

### 3. Add CORS Headers
```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-domain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})
```

### 4. Add Security Headers
```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

---

## Monitoring Checklist

- [ ] Application logs monitored
- [ ] Database performance tracked
- [ ] Uptime monitoring (UptimeRobot, etc)
- [ ] Error tracking (Sentry, etc)
- [ ] Security scanning enabled
- [ ] SSL certificate renewal automated
- [ ] Backups running daily
- [ ] Disk space monitored
- [ ] Memory usage tracked
- [ ] CPU usage monitored

---

## Rollback Plan

### If issues occur:
```bash
# Check application status
systemctl status land-registry

# View logs
journalctl -u land-registry -n 50

# Rollback to previous build
git revert <commit-hash>
git push

# Restart application
systemctl restart land-registry
```

---

**Deployment Complete!**

Your application is now running in production. 

Monitor it regularly and keep backups updated.
