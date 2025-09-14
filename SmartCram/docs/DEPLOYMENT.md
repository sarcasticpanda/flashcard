# SMARTCRAM Deployment Guide

## Overview

This guide covers deploying SMARTCRAM in various environments, from local development to production. The application supports multiple deployment methods including Docker, cloud platforms, and traditional server deployments.

## Prerequisites

- Python 3.8+
- MySQL 8.0+
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key
- Git

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Database Configuration
DATABASE_URL=mysql+mysqlconnector://username:password@host:port/database_name

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# JWT Configuration
JWT_SECRET_KEY=your_secure_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=720

# Application Configuration
API_BASE_URL=http://your-domain.com
DEBUG=False
ENVIRONMENT=production

# CORS Configuration
ALLOWED_ORIGINS=["http://your-domain.com", "https://your-domain.com"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

## Deployment Methods

### 1. Docker Deployment (Recommended)

#### Using Docker Compose

1. **Clone the repository:**
```bash
git clone <repository-url>
cd SMARTCRAM
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your production values
```PS C:\Users\USER\Desktop\HACKATHON-4-3-2> cp .env.example .env

3. **Build and start services:**
```bash
docker-compose up -d
```

4. **Run database migrations:**
```bash
docker-compose exec backend alembic upgrade head
```

5. **Verify deployment:**
```bash
# Check if services are running
docker-compose ps

# Test the API
curl http://localhost:8000/health
```

#### Using Docker Swarm

1. **Initialize Docker Swarm:**
```bash
docker swarm init
```

2. **Deploy the stack:**
```bash
docker stack deploy -c docker-compose.yml smartcram
```

3. **Check service status:**
```bash
docker service ls
```

### 2. Cloud Platform Deployment

#### AWS Deployment

##### Using AWS ECS

1. **Create ECR repository:**
```bash
aws ecr create-repository --repository-name smartcram-backend
aws ecr create-repository --repository-name smartcram-frontend
```

2. **Build and push images:**
```bash
# Backend
docker build -t smartcram-backend ./backend
docker tag smartcram-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/smartcram-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/smartcram-backend:latest

# Frontend
docker build -t smartcram-frontend ./frontend
docker tag smartcram-frontend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/smartcram-frontend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/smartcram-frontend:latest
```

3. **Create ECS cluster and services using AWS Console or CLI**

##### Using AWS EC2

1. **Launch EC2 instance:**
```bash
# Launch Ubuntu 20.04 instance
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --count 1 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxxx
```

2. **SSH into instance and install dependencies:**
```bash
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

3. **Deploy application:**
```bash
# Clone repository
git clone <repository-url>
cd SMARTCRAM

# Configure environment
cp .env.example .env
# Edit .env file

# Start services
docker-compose up -d
```

#### Google Cloud Platform (GCP)

##### Using Google Cloud Run

1. **Enable required APIs:**
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

2. **Build and deploy:**
```bash
# Backend
gcloud builds submit --tag gcr.io/PROJECT_ID/smartcram-backend ./backend
gcloud run deploy smartcram-backend \
  --image gcr.io/PROJECT_ID/smartcram-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Frontend
gcloud builds submit --tag gcr.io/PROJECT_ID/smartcram-frontend ./frontend
gcloud run deploy smartcram-frontend \
  --image gcr.io/PROJECT_ID/smartcram-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Microsoft Azure

##### Using Azure Container Instances

1. **Build and push to Azure Container Registry:**
```bash
# Login to Azure
az login

# Create container registry
az acr create --name smartcramregistry --resource-group myResourceGroup --sku Basic

# Build and push images
az acr build --registry smartcramregistry --image smartcram-backend:latest ./backend
az acr build --registry smartcramregistry --image smartcram-frontend:latest ./frontend
```

2. **Deploy containers:**
```bash
# Backend
az container create \
  --resource-group myResourceGroup \
  --name smartcram-backend \
  --image smartcramregistry.azurecr.io/smartcram-backend:latest \
  --dns-name-label smartcram-backend \
  --ports 8000

# Frontend
az container create \
  --resource-group myResourceGroup \
  --name smartcram-frontend \
  --image smartcramregistry.azurecr.io/smartcram-frontend:latest \
  --dns-name-label smartcram-frontend \
  --ports 80
```

### 3. Traditional Server Deployment

#### Ubuntu/Debian Server

1. **Install system dependencies:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv mysql-server nginx git
```

2. **Setup MySQL:**
```bash
sudo mysql_secure_installation
sudo mysql -u root -p
```

```sql
CREATE DATABASE smartcram;
CREATE USER 'smartcram'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON smartcram.* TO 'smartcram'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

3. **Deploy application:**
```bash
# Clone repository
git clone <repository-url>
cd SMARTCRAM

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env file

# Run migrations
cd backend
alembic upgrade head
```

4. **Setup systemd service:**
```bash
sudo nano /etc/systemd/system/smartcram.service
```

```ini
[Unit]
Description=SMARTCRAM Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/SMARTCRAM/backend
Environment=PATH=/path/to/SMARTCRAM/venv/bin
ExecStart=/path/to/SMARTCRAM/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable smartcram
sudo systemctl start smartcram
```

6. **Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/smartcram
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /path/to/SMARTCRAM/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/smartcram /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Database Setup

### MySQL Configuration

1. **Create database and user:**
```sql
CREATE DATABASE smartcram CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'smartcram'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON smartcram.* TO 'smartcram'@'localhost';
FLUSH PRIVILEGES;
```

2. **Run migrations:**
```bash
cd backend
alembic upgrade head
```

### Database Backup and Recovery

#### Backup
```bash
# Create backup
mysqldump -u smartcram -p smartcram > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u smartcram -p smartcram > $BACKUP_DIR/backup_$DATE.sql
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

#### Recovery
```bash
mysql -u smartcram -p smartcram < backup_20240101_120000.sql
```

## SSL/TLS Configuration

### Using Let's Encrypt

1. **Install Certbot:**
```bash
sudo apt install certbot python3-certbot-nginx
```

2. **Obtain certificate:**
```bash
sudo certbot --nginx -d your-domain.com
```

3. **Auto-renewal:**
```bash
sudo crontab -e
# Add line: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring and Logging

### Application Logs

```bash
# View application logs
docker-compose logs -f backend

# View system logs
sudo journalctl -u smartcram -f
```

### Health Checks

```bash
# API health check
curl http://your-domain.com/api/v1/health

# Database connectivity
docker-compose exec backend python -c "from app.db.database import engine; print(engine.execute('SELECT 1').scalar())"
```

### Performance Monitoring

1. **Install monitoring tools:**
```bash
# Prometheus and Grafana
docker-compose -f docker-compose.monitoring.yml up -d
```

2. **Setup alerts:**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'smartcram'
    static_configs:
      - targets: ['localhost:8000']
```

## Security Considerations

### Firewall Configuration

```bash
# UFW firewall setup
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Environment Security

1. **Secure environment variables:**
```bash
# Use secrets management
docker secret create jwt_secret_key /path/to/jwt_secret
docker secret create openai_api_key /path/to/openai_key
```

2. **Database security:**
```sql
-- Limit database access
REVOKE ALL PRIVILEGES ON smartcram.* FROM 'smartcram'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON smartcram.* TO 'smartcram'@'localhost';
```

### Regular Security Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d

# Update Python dependencies
pip install --upgrade -r requirements.txt
```

## Scaling

### Horizontal Scaling

1. **Load Balancer Configuration:**
```nginx
upstream smartcram_backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /api/ {
        proxy_pass http://smartcram_backend;
    }
}
```

2. **Database Scaling:**
```yaml
# docker-compose.scale.yml
services:
  backend:
    deploy:
      replicas: 3
    environment:
      - DATABASE_URL=mysql+mysqlconnector://smartcram:password@mysql:3306/smartcram
```

### Vertical Scaling

1. **Resource limits:**
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

## Troubleshooting

### Common Issues

1. **Database connection errors:**
```bash
# Check database status
docker-compose exec mysql mysql -u root -p -e "SHOW PROCESSLIST;"

# Check connection string
docker-compose exec backend python -c "from app.core.config import settings; print(settings.database_url)"
```

2. **OpenAI API errors:**
```bash
# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

3. **CORS issues:**
```bash
# Check CORS configuration
curl -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: X-Requested-With" -X OPTIONS http://localhost:8000/api/v1/auth/login
```

### Performance Issues

1. **Database optimization:**
```sql
-- Add indexes for better performance
CREATE INDEX idx_flashcards_user_id ON flashcards(user_id);
CREATE INDEX idx_quiz_user_id ON quiz(user_id);
```

2. **Application optimization:**
```python
# Enable connection pooling
DATABASE_URL = "mysql+mysqlconnector://user:pass@host/db?pool_size=20&max_overflow=30"
```

## Backup and Disaster Recovery

### Backup Strategy

1. **Database backups:**
```bash
# Daily automated backups
0 2 * * * /usr/local/bin/backup_database.sh
```

2. **Application backups:**
```bash
# Backup application files
tar -czf smartcram_backup_$(date +%Y%m%d).tar.gz /path/to/SMARTCRAM
```

### Disaster Recovery Plan

1. **Recovery procedures:**
```bash
# Restore from backup
./scripts/restore.sh backup_20240101_120000.sql
```

2. **Failover procedures:**
```bash
# Switch to backup server
./scripts/failover.sh backup_server_ip
```

## Support

For deployment issues and support:
- Check the troubleshooting section above
- Review application logs
- Create an issue in the project repository
- Contact the development team

## Additional Resources

- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Docker Documentation](https://docs.docker.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Nginx Documentation](https://nginx.org/en/docs/)
