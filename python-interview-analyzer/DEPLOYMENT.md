# 🚀 Deployment Guide - Interview Analyzer

Полное руководство по развертыванию Interview Analyzer API в production.

## 📋 Содержание

- [Требования](#требования)
- [Локальное развертывание](#локальное-развертывание)
- [Production развертывание](#production-развертывание)
- [Docker Compose](#docker-compose)
- [Kubernetes](#kubernetes)
- [Мониторинг и логи](#мониторинг-и-логи)
- [Безопасность](#безопасность)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Требования

### Минимальные требования

- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disk**: 50 GB SSD
- **OS**: Linux (Ubuntu 20.04+, Debian 10+, CentOS 8+)

### Рекомендуемые требования (Production)

- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Disk**: 100+ GB SSD
- **OS**: Linux (Ubuntu 22.04 LTS)

### Программное обеспечение

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+ (для локальной разработки)
- PostgreSQL 14+ (опционально, для production)

---

## 🏠 Локальное развертывание

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-org/interview-analyzer.git
cd interview-analyzer/python-interview-analyzer
```

### 2. Настройка переменных окружения

Скопируйте `.env.example` в `.env`:

```bash
cp .env.example .env
```

Отредактируйте `.env` и добавьте необходимые ключи:

```env
# Обязательные
OPENAI_API_KEY=sk-your-openai-api-key-here

# Окружение
ENV=development
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=DEBUG

# Database (опционально)
DATABASE_URL=postgresql://interview_user:interview_pass@localhost:5432/interview_db

# Google Sheets (опционально)
GOOGLE_SERVICE_ACCOUNT_KEY=/path/to/service-account.json
SOURCE_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
RESULTS_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_RESULTS_SHEET_ID/edit
```

### 3. Запуск с Docker Compose

```bash
# Базовый запуск (App + Redis)
docker-compose up -d

# С PostgreSQL
docker-compose --profile database up -d

# С мониторингом (Prometheus + Grafana)
docker-compose --profile monitoring up -d

# Production режим
docker-compose --profile production up -d
```

### 4. Проверка работоспособности

```bash
# Проверка статуса контейнеров
docker-compose ps

# Проверка health endpoint
curl http://localhost:8000/health

# Просмотр логов
docker-compose logs -f app
```

### 5. Доступ к сервисам

- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Prometheus** (если включен): http://localhost:9090
- **Grafana** (если включен): http://localhost:3000 (admin/admin)

---

## 🏭 Production развертывание

### Вариант 1: Docker Compose на одном сервере

#### 1.1 Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker
```

#### 1.2 Настройка приложения

```bash
# Создание рабочей директории
sudo mkdir -p /opt/interview-analyzer
cd /opt/interview-analyzer

# Клонирование репозитория
git clone https://github.com/your-org/interview-analyzer.git .

# Настройка переменных окружения
cp .env.example .env
nano .env  # Отредактируйте конфигурацию
```

**Важные настройки для production в `.env`:**

```env
# Production окружение
ENV=production
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO

# Безопасность
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
API_KEYS_ENABLED=true
RATE_LIMIT_ENABLED=true

# Database
DATABASE_URL=postgresql://interview_user:STRONG_PASSWORD@postgres:5432/interview_db

# OpenAI
OPENAI_API_KEY=sk-prod-your-api-key

# Workers
MAX_CONCURRENT_ANALYSES=5
WORKER_COUNT=4

# Monitoring
SENTRY_DSN=https://your-sentry-dsn
PROMETHEUS_ENABLED=true
```

#### 1.3 Настройка SSL/TLS с Nginx

Создайте файл `nginx/prod.conf`:

```nginx
upstream interview_api {
    server app:8000;
}

# HTTP -> HTTPS redirect
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 100M;

    location / {
        proxy_pass http://interview_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /health {
        proxy_pass http://interview_api/health;
        access_log off;
    }
}
```

#### 1.4 Получение SSL сертификата

```bash
# Установка certbot
sudo apt install certbot python3-certbot-nginx -y

# Получение сертификата
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Автоматическое обновление
sudo crontab -e
# Добавьте: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 1.5 Запуск в production

```bash
# Сборка и запуск
docker-compose --profile production up -d --build

# Проверка логов
docker-compose logs -f app

# Проверка работоспособности
curl https://yourdomain.com/health
```

#### 1.6 Настройка автозапуска

Создайте systemd service файл `/etc/systemd/system/interview-analyzer.service`:

```ini
[Unit]
Description=Interview Analyzer API
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/interview-analyzer
ExecStart=/usr/local/bin/docker-compose --profile production up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Активируйте сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable interview-analyzer
sudo systemctl start interview-analyzer
sudo systemctl status interview-analyzer
```

---

### Вариант 2: Kubernetes Deployment

#### 2.1 Создание Namespace

```yaml
# kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: interview-analyzer
```

#### 2.2 ConfigMap и Secrets

```yaml
# kubernetes/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: interview-analyzer-config
  namespace: interview-analyzer
data:
  ENV: "production"
  PORT: "8000"
  HOST: "0.0.0.0"
  LOG_LEVEL: "INFO"
  DEFAULT_LANGUAGE: "ru"
---
# kubernetes/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: interview-analyzer-secrets
  namespace: interview-analyzer
type: Opaque
stringData:
  OPENAI_API_KEY: "sk-your-api-key-here"
  DATABASE_URL: "postgresql://user:pass@postgres:5432/interview_db"
```

#### 2.3 Deployment

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: interview-analyzer
  namespace: interview-analyzer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: interview-analyzer
  template:
    metadata:
      labels:
        app: interview-analyzer
    spec:
      containers:
      - name: interview-analyzer
        image: your-registry/interview-analyzer:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: interview-analyzer-config
        - secretRef:
            name: interview-analyzer-secrets
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

#### 2.4 Service и Ingress

```yaml
# kubernetes/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: interview-analyzer-service
  namespace: interview-analyzer
spec:
  selector:
    app: interview-analyzer
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
---
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: interview-analyzer-ingress
  namespace: interview-analyzer
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: interview-analyzer-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: interview-analyzer-service
            port:
              number: 80
```

#### 2.5 Применение конфигурации

```bash
# Применение всех манифестов
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secrets.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
kubectl apply -f kubernetes/ingress.yaml

# Проверка статуса
kubectl get pods -n interview-analyzer
kubectl get services -n interview-analyzer
kubectl get ingress -n interview-analyzer

# Просмотр логов
kubectl logs -f deployment/interview-analyzer -n interview-analyzer
```

---

## 📊 Мониторинг и логи

### Prometheus метрики

Эндпоинт метрик доступен на `/metrics`:

```bash
curl http://localhost:8000/metrics
```

**Основные метрики:**

- `http_requests_total` - Общее количество HTTP запросов
- `http_request_duration_seconds` - Длительность обработки запросов
- `analysis_processing_time_seconds` - Время обработки анализа
- `analysis_total_count` - Общее количество анализов
- `analysis_errors_total` - Количество ошибок анализа

### Grafana Dashboards

Импортируйте готовый dashboard из `monitoring/grafana-dashboard.json`:

1. Откройте Grafana: http://localhost:3000
2. Login: admin/admin
3. Import dashboard
4. Загрузите `grafana-dashboard.json`

### Логирование

**Структура логов:**

```json
{
  "timestamp": "2024-01-15T14:30:00Z",
  "level": "INFO",
  "message": "Analysis completed",
  "candidate_id": "CAND-001",
  "duration_ms": 45000,
  "total_score": 78
}
```

**Просмотр логов:**

```bash
# Docker Compose
docker-compose logs -f app

# Kubernetes
kubectl logs -f deployment/interview-analyzer -n interview-analyzer

# Фильтрация по уровню
docker-compose logs app | grep ERROR
```

---

## 🔒 Безопасность

### 1. API Keys (рекомендуется для production)

Создайте middleware для проверки API ключей:

```python
# app/middleware/api_key.py
from fastapi import Header, HTTPException
from typing import Optional

API_KEYS = set(os.getenv("API_KEYS", "").split(","))

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key or x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key
```

### 2. Rate Limiting

Установите и настройте slowapi:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/analyze")
@limiter.limit("10/minute")
async def analyze_interview(...):
    ...
```

### 3. HTTPS только

В production всегда используйте HTTPS:

```nginx
# Редирект HTTP -> HTTPS
server {
    listen 80;
    return 301 https://$server_name$request_uri;
}
```

### 4. Секреты

**НИКОГДА** не коммитьте `.env` файл в Git!

```bash
# .gitignore
.env
*.key
*.pem
service-account.json
```

Используйте secret management:
- **AWS**: AWS Secrets Manager
- **GCP**: Google Secret Manager
- **Azure**: Azure Key Vault
- **K8s**: Kubernetes Secrets

---

## 🐛 Troubleshooting

### Проблема: API не отвечает

**Симптомы:** Timeout при запросах к API

**Решение:**

```bash
# Проверка статуса контейнера
docker-compose ps

# Проверка логов
docker-compose logs -f app

# Проверка health endpoint
curl http://localhost:8000/health

# Рестарт сервиса
docker-compose restart app
```

### Проблема: Ошибка "OpenAI API key not valid"

**Решение:**

```bash
# Проверьте .env файл
cat .env | grep OPENAI_API_KEY

# Убедитесь, что ключ начинается с sk-
# Перезапустите контейнер
docker-compose restart app
```

### Проблема: Медленная обработка видео

**Решение:**

1. Увеличьте ресурсы контейнера в `docker-compose.yaml`:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
```

2. Увеличьте количество воркеров в `.env`:

```env
WORKER_COUNT=8
MAX_CONCURRENT_ANALYSES=3
```

### Проблема: Нехватка места на диске

**Решение:**

```bash
# Очистка неиспользуемых образов
docker system prune -a

# Очистка логов
sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log

# Настройка ротации логов в docker-compose.yaml
services:
  app:
    logging:
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 📦 Backup и восстановление

### Backup базы данных

```bash
# PostgreSQL backup
docker exec interview-analyzer-postgres pg_dump -U interview_user interview_db > backup_$(date +%Y%m%d).sql

# Автоматический backup (добавьте в cron)
0 2 * * * /path/to/backup-script.sh
```

### Восстановление

```bash
# Восстановление из backup
docker exec -i interview-analyzer-postgres psql -U interview_user interview_db < backup_20240115.sql
```

---

## 🔄 Updates и миграции

### Обновление приложения

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose --profile production down
docker-compose --profile production up -d --build

# Проверка новой версии
curl http://localhost:8000/ | jq '.version'
```

### Database миграции

```bash
# Использование Alembic (если настроено)
docker-compose exec app alembic upgrade head

# Откат миграции
docker-compose exec app alembic downgrade -1
```

---

## ✅ Checklist перед production

- [ ] Все API ключи настроены и в безопасности
- [ ] SSL сертификаты установлены
- [ ] CORS настроен правильно
- [ ] Rate limiting включен
- [ ] Логирование настроено
- [ ] Мониторинг (Prometheus + Grafana) работает
- [ ] Backup настроен
- [ ] Health checks проходят
- [ ] Load testing выполнен
- [ ] Документация обновлена
- [ ] Error tracking (Sentry) настроен

---

## 📞 Поддержка

Если возникли проблемы:

1. Проверьте логи: `docker-compose logs -f`
2. Проверьте health endpoint: `curl /health`
3. Создайте issue на GitHub
4. Свяжитесь с командой: support@yourdomain.com
