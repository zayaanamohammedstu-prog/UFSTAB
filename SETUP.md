# OratorHub Setup Guide

## Quick Start with Docker (Recommended)

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 5GB disk space

### Steps

1. **Clone the repository:**
```bash
git clone https://github.com/zayaanamohammedstu-prog/UFSTAB.git
cd UFSTAB
```

2. **Configure environment:**
```bash
cp .env.example .env
```

Edit `.env` and update at minimum:
- `SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- `JWT_SECRET_KEY` - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
- `STRIPE_SECRET_KEY` and `STRIPE_PUBLIC_KEY` (if using payments)
- `MAIL_USERNAME` and `MAIL_PASSWORD` (if using email)

3. **Start the application:**
```bash
docker-compose up -d
```

4. **Access the application:**
- Frontend: http://localhost
- API: http://localhost/api
- API Health: http://localhost/api/health

5. **Default admin login:**
- Email: `admin@oratorhub.com`
- Password: `admin123`
- **Change this immediately in production!**

### Stopping the Application

```bash
docker-compose down
```

To remove all data:
```bash
docker-compose down -v
```

## Local Development Setup

### Prerequisites
- Python 3.9+
- pip
- PostgreSQL 12+ (optional, SQLite works for dev)
- Redis (optional, for SSE features)

### Steps

1. **Clone repository:**
```bash
git clone https://github.com/zayaanamohammedstu-prog/UFSTAB.git
cd UFSTAB
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
```

Edit `.env` with your local settings. For development, these defaults work:
```env
FLASK_ENV=development
DATABASE_URL=sqlite:///oratorhub.db
SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=dev-jwt-secret
```

5. **Initialize database:**
```bash
chmod +x init_db.sh
./init_db.sh
```

Or manually:
```bash
export FLASK_APP=app.py
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. **Run the application:**
```bash
python app.py
```

The application will be available at http://localhost:5000

### Development Tools

```bash
# Run with auto-reload
FLASK_ENV=development python app.py

# Run tests
pytest

# Check code coverage
pytest --cov=app --cov-report=html

# Format code
black .

# Lint code
flake8 .
```

## Frontend-Only Mode

If you just want to use the basic tabulation features without the backend:

```bash
# Open directly in browser
open index.html

# Or use Python's HTTP server
python -m http.server 8000
# Visit http://localhost:8000
```

Note: Frontend-only mode uses localStorage and doesn't have:
- User authentication
- Payment processing
- Document uploads
- Real-time updates
- Multi-device sync

## Production Deployment

### Option 1: Docker Compose (Recommended)

1. **Update environment for production:**
```bash
# In .env file
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@db:5432/oratorhub
SECRET_KEY=<strong-random-key>
JWT_SECRET_KEY=<strong-random-key>
```

2. **Start services:**
```bash
docker-compose up -d
```

3. **Set up SSL (Let's Encrypt):**
```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d yourdomain.com
```

4. **Enable automatic backups:**
```bash
# Add to crontab
0 2 * * * docker exec oratorhub-db pg_dump -U oratorhub oratorhub > /backups/oratorhub_$(date +\%Y\%m\%d).sql
```

### Option 2: Manual Server Deployment

1. **Install system dependencies:**
```bash
sudo apt-get update
sudo apt-get install python3.9 python3-pip postgresql nginx redis
```

2. **Setup PostgreSQL:**
```bash
sudo -u postgres psql
CREATE DATABASE oratorhub;
CREATE USER oratorhub WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE oratorhub TO oratorhub;
\q
```

3. **Deploy application:**
```bash
# Clone and setup
git clone <repo>
cd UFSTAB
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with production settings

# Initialize database
./init_db.sh

# Install systemd service
sudo cp oratorhub.service /etc/systemd/system/
sudo systemctl enable oratorhub
sudo systemctl start oratorhub
```

4. **Configure Nginx:**
```bash
sudo cp nginx.conf /etc/nginx/sites-available/oratorhub
sudo ln -s /etc/nginx/sites-available/oratorhub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker ps  # or systemctl status postgresql

# Check connection
psql postgresql://oratorhub:password@localhost:5432/oratorhub

# Reset database
docker-compose down -v
docker-compose up -d
```

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or change port in .env
BACKEND_URL=http://localhost:5001
```

### Migration Errors

```bash
# Drop all tables and start fresh (DEV ONLY!)
flask db downgrade
flask db upgrade

# Or delete migrations and start over
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Docker Issues

```bash
# View logs
docker-compose logs -f

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d

# Clean everything
docker-compose down -v
docker system prune -a
```

## Performance Tuning

### For 50-100 Participants
- Default settings work fine
- SQLite is sufficient
- Single server

### For 100-500 Participants
- Use PostgreSQL
- Add Redis for caching
- Increase Gunicorn workers to 8

### For 500-2000 Participants
- PostgreSQL with connection pooling
- Redis cluster
- Multiple app servers with load balancer
- CDN for static assets

### For 2000-5000 Participants
- PostgreSQL with read replicas
- Redis Cluster
- Auto-scaling app servers
- CDN
- Database query optimization

## Security Checklist

- [ ] Change default admin credentials
- [ ] Use strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Set up firewall (ufw/iptables)
- [ ] Regular database backups
- [ ] Update dependencies regularly
- [ ] Monitor logs for suspicious activity
- [ ] Use environment-based configs
- [ ] Enable rate limiting
- [ ] Set up monitoring (Sentry, etc.)

## Support

- GitHub Issues: https://github.com/zayaanamohammedstu-prog/UFSTAB/issues
- Documentation: https://github.com/zayaanamohammedstu-prog/UFSTAB/wiki
- Email: support@oratorhub.com
