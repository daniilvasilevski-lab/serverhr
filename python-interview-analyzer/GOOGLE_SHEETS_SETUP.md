# 📊 Настройка Google Sheets Integration

Пошаговое руководство по настройке интеграции с Google Sheets для автоматической обработки интервью.

---

## 📋 Содержание

1. [Создание Google Service Account](#1-создание-google-service-account)
2. [Настройка Google Sheets](#2-настройка-google-sheets)
3. [Конфигурация проекта](#3-конфигурация-проекта)
4. [Запуск автоматической обработки](#4-запуск-автоматической-обработки)
5. [Troubleshooting](#5-troubleshooting)

---

## 1. Создание Google Service Account

### Шаг 1.1: Создание проекта в Google Cloud Console

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Запомните **Project ID**

### Шаг 1.2: Включение Google Sheets API

1. В навигационном меню выберите **APIs & Services** → **Library**
2. Найдите и включите:
   - **Google Sheets API**
   - **Google Drive API**

### Шаг 1.3: Создание Service Account

1. Перейдите в **APIs & Services** → **Credentials**
2. Нажмите **Create Credentials** → **Service Account**
3. Заполните форму:
   - **Service account name**: `interview-analyzer-service`
   - **Service account ID**: `interview-analyzer`
   - **Description**: `Service account for Interview Analyzer`
4. Нажмите **Create and Continue**
5. Выберите роль: **Project** → **Editor**
6. Нажмите **Continue** → **Done**

### Шаг 1.4: Создание ключа

1. В списке Service Accounts найдите созданный аккаунт
2. Нажмите на него и перейдите на вкладку **Keys**
3. Нажмите **Add Key** → **Create new key**
4. Выберите тип **JSON**
5. Нажмите **Create**
6. Файл `interview-analyzer-service-xxxxx.json` будет скачан

**⚠️ ВАЖНО: Сохраните этот файл в безопасном месте!**

---

## 2. Настройка Google Sheets

### Шаг 2.1: Создание входной таблицы (Source Sheet)

1. Создайте новую Google Таблицу
2. Назовите её: `Interview Analyzer - Source`
3. В первой строке создайте заголовки:

```
| A    | B    | C     | D     | E           | F      | G         | H      | I         | J          | K             | L         |
|------|------|-------|-------|-------------|--------|-----------|--------|-----------|------------|---------------|-----------|
| ID   | Name | Email | Phone | Preferences | CV_gcs | video_gcs | CV_URL | Video_URL | created_at | Questions_URL | Processed |
```

4. Скопируйте URL таблицы (например: `https://docs.google.com/spreadsheets/d/XXXXXXXX/edit`)

### Шаг 2.2: Создание выходной таблицы (Results Sheet)

1. Создайте новую Google Таблицу
2. Назовите её: `Interview Analyzer - Results`
3. В первой строке создайте заголовки:

```
| A  | B    | C     | D     | E        | F             | G          | H         | I          | J        | K        | L                 | M            | N             | O              |
|----|------|-------|-------|----------|---------------|------------|-----------|------------|----------|----------|-------------------|--------------|---------------|----------------|
| ID | Name | Email | Phone | Language | Communication | Motivation | Technical | Analytical | Creative | Teamwork | Stress_Resistance | Adaptability | Overall_Score | Recommendation |
```

4. Скопируйте URL таблицы

### Шаг 2.3: Предоставление доступа Service Account

1. Откройте Service Account key JSON файл
2. Найдите поле `client_email` (например: `interview-analyzer@project-id.iam.gserviceaccount.com`)
3. Скопируйте этот email
4. В обеих таблицах (Source и Results):
   - Нажмите **Share**
   - Вставьте скопированный email
   - Выберите роль: **Editor**
   - Нажмите **Send** (снимите галочку "Notify people")

---

## 3. Конфигурация проекта

### Шаг 3.1: Размещение Service Account ключа

```bash
# Создайте директорию для credentials
mkdir -p /home/user/serverhr/python-interview-analyzer/credentials

# Скопируйте JSON файл в эту директорию
cp /path/to/your/interview-analyzer-service-xxxxx.json \
   /home/user/serverhr/python-interview-analyzer/credentials/service-account.json
```

### Шаг 3.2: Настройка .env файла

Создайте или отредактируйте файл `.env`:

```bash
cd /home/user/serverhr/python-interview-analyzer
cp .env.example .env
nano .env
```

Добавьте следующие настройки:

```env
# === ОБЯЗАТЕЛЬНЫЕ НАСТРОЙКИ ===

# OpenAI API ключ
OPENAI_API_KEY=sk-your-openai-api-key-here

# === GOOGLE SHEETS INTEGRATION ===

# Путь к Service Account JSON ключу
GOOGLE_SERVICE_ACCOUNT_KEY=/app/credentials/service-account.json

# URL входной таблицы (откуда берутся интервью)
SOURCE_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SOURCE_SHEET_ID/edit

# URL выходной таблицы (куда сохраняются результаты)
RESULTS_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_RESULTS_SHEET_ID/edit

# === НАСТРОЙКИ ПРИЛОЖЕНИЯ ===

ENV=production
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO

# === АНАЛИЗ ===

DEFAULT_LANGUAGE=ru
WHISPER_MODEL=base
MAX_VIDEO_SIZE_MB=100

# === АВТОМАТИЧЕСКАЯ ОБРАБОТКА ===

# Включить автоматическое сканирование и обработку
ENABLE_AUTO_PROCESSING=true

# Интервал сканирования в минутах
SCAN_INTERVAL_MINUTES=5

# Максимум одновременных анализов
MAX_CONCURRENT_ANALYSES=2
```

### Шаг 3.3: Обновление docker-compose.yaml

Убедитесь, что в `docker-compose.yaml` смонтирована директория credentials:

```yaml
services:
  app:
    volumes:
      - ./credentials:/app/credentials:ro
      - ./logs:/app/logs
      - ./temp:/app/temp
```

---

## 4. Запуск автоматической обработки

### Шаг 4.1: Запуск проекта

```bash
cd /home/user/serverhr/python-interview-analyzer

# Запуск с Docker Compose
docker-compose up -d

# Проверка логов
docker-compose logs -f app
```

### Шаг 4.2: Проверка подключения к Google Sheets

Откройте в браузере: http://localhost:8000/docs

Найдите endpoint `/health` и выполните:

```bash
curl http://localhost:8000/health
```

Ответ должен содержать:

```json
{
  "success": true,
  "status": "healthy",
  "services_status": {
    "analyzer": "ok",
    "sheets_service": "ok",
    "openai_api": "ok"
  }
}
```

### Шаг 4.3: Добавление тестовых данных

В входную таблицу добавьте строку:

```
| ID       | Name          | Email               | Phone        | Preferences | CV_gcs | video_gcs | CV_URL | Video_URL                           | created_at | Questions_URL | Processed |
|----------|---------------|---------------------|--------------|-------------|--------|-----------|--------|-------------------------------------|------------|---------------|-----------|
| CAND-001 | Иван Иванов   | ivan@example.com    | +79991234567 | Python, ML  |        |           |        | https://example.com/interview.mp4   | 2024-01-15 |               | 0         |
```

### Шаг 4.4: Запуск ручной обработки

Через API:

```bash
curl -X POST "http://localhost:8000/api/v1/process-sheets" \
  -H "Content-Type: application/json"
```

Или через Swagger UI:
- Откройте http://localhost:8000/docs
- Найдите `/api/v1/process-sheets`
- Нажмите **Try it out** → **Execute**

### Шаг 4.5: Проверка результатов

1. Откройте выходную таблицу (Results Sheet)
2. Вы должны увидеть новую строку с результатами анализа
3. Во входной таблице (Source Sheet) колонка `Processed` должна стать `1`

---

## 5. Автоматический режим (опционально)

### Включение планировщика задач

Если вы хотите автоматическое сканирование каждые N минут:

```env
ENABLE_AUTO_PROCESSING=true
SCAN_INTERVAL_MINUTES=5
```

После перезапуска:

```bash
docker-compose restart app
```

Система будет автоматически сканировать входную таблицу каждые 5 минут и обрабатывать новые интервью.

### Проверка статуса планировщика

```bash
curl http://localhost:8000/api/v1/tasks/stats
```

---

## 6. Troubleshooting

### Проблема: "Google Sheets not configured"

**Решение:**

1. Проверьте наличие файла service-account.json
2. Убедитесь, что путь в .env правильный
3. Проверьте права доступа к файлу:

```bash
ls -la credentials/service-account.json
chmod 644 credentials/service-account.json
```

### Проблема: "Permission denied" при доступе к таблице

**Решение:**

1. Убедитесь, что Service Account email имеет доступ к таблицам
2. Проверьте, что в таблицах выдан доступ **Editor**
3. Попробуйте переоткрыть доступ:
   - Удалите текущий доступ
   - Добавьте снова с ролью Editor

### Проблема: "Invalid sheet URL"

**Решение:**

Убедитесь, что URL в формате:

```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
```

А не:

```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0
```

### Проблема: Обработка не начинается

**Проверьте:**

```bash
# Логи приложения
docker-compose logs -f app

# Статус сервисов
curl http://localhost:8000/health

# Список необработанных интервью
# (добавьте этот endpoint, см. ниже)
```

---

## 7. Пример работы

### 7.1. Подготовка данных

Добавьте в входную таблицу несколько интервью:

```
| ID       | Name            | Email                | Phone        | Video_URL                           | Processed |
|----------|-----------------|----------------------|--------------|-------------------------------------|-----------|
| CAND-001 | Иван Иванов     | ivan@example.com     | +79991111111 | https://example.com/ivan.mp4        | 0         |
| CAND-002 | Мария Петрова   | maria@example.com    | +79992222222 | https://example.com/maria.mp4       | 0         |
| CAND-003 | Алексей Сидоров | alexey@example.com   | +79993333333 | https://example.com/alexey.mp4      | 0         |
```

### 7.2. Запуск обработки

```bash
curl -X POST "http://localhost:8000/api/v1/process-sheets"
```

### 7.3. Мониторинг процесса

```bash
# Следите за логами в реальном времени
docker-compose logs -f app

# Вы увидите:
# 📋 Found unprocessed interview: Иван Иванов (Row 2)
# 🔄 Processing 1/3: Иван Иванов
# ✅ Successfully processed: Иван Иванов (1/3)
# ...
```

### 7.4. Результаты

В выходной таблице появятся строки:

```
| ID       | Name          | Email            | Language | Communication | Motivation | Technical | ... | Overall_Score | Recommendation        |
|----------|---------------|------------------|----------|---------------|------------|-----------|-----|---------------|-----------------------|
| CAND-001 | Иван Иванов   | ivan@example.com | RU       | 8             | 7          | 9         | ... | 82            | Сильный кандидат      |
| CAND-002 | Мария Петрова | maria@...        | RU       | 9             | 8          | 7         | ... | 78            | Рекомендуется к найму |
```

---

## 8. API Endpoints для Google Sheets

### POST /api/v1/process-sheets

Запуск ручной обработки всех необработанных интервью.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/process-sheets"
```

**Response:**
```json
{
  "success": true,
  "message": "Processing completed",
  "stats": {
    "found": 5,
    "processed": 5,
    "failed": 0,
    "saved": 5
  }
}
```

### GET /api/v1/sheets/unprocessed

Получение списка необработанных интервью.

**Response:**
```json
{
  "success": true,
  "count": 3,
  "interviews": [
    {
      "id": "CAND-001",
      "name": "Иван Иванов",
      "video_url": "https://example.com/ivan.mp4",
      "row_number": 2
    }
  ]
}
```

---

## 9. Best Practices

### Безопасность

1. **НИКОГДА** не коммитьте `service-account.json` в Git
2. Храните credentials в `.gitignore`
3. Используйте переменные окружения для чувствительных данных
4. Регулярно ротируйте Service Account ключи

### Производительность

1. Не обрабатывайте более 5-10 интервью одновременно
2. Используйте `MAX_CONCURRENT_ANALYSES=2` для начала
3. Мониторьте использование памяти Docker контейнера

### Организация данных

1. Используйте понятные ID для кандидатов (CAND-001, CAND-002)
2. Сохраняйте резервные копии таблиц
3. Периодически архивируйте старые данные

---

## 10. Дополнительные возможности

### Мультиязычность

Система автоматически определяет язык интервью и сохраняет его в колонку `Language`:
- `RU` - Русский
- `EN` - Английский
- `PL` - Польский

### Интеграция с CV и вопросами

Если заполнены колонки `CV_URL` и `Questions_URL`, система использует расширенный анализ:

```
| CV_URL                        | Questions_URL                  |
|-------------------------------|--------------------------------|
| https://example.com/cv.pdf    | https://example.com/q.pdf      |
```

---

## ✅ Checklist готовности

Перед запуском убедитесь:

- [ ] Google Service Account создан
- [ ] Google Sheets API включен
- [ ] Service Account ключ скачан
- [ ] Входная таблица создана с правильными колонками
- [ ] Выходная таблица создана с правильными колонками
- [ ] Service Account имеет доступ к обеим таблицам (Editor)
- [ ] Файл .env настроен с правильными URL и путем к ключу
- [ ] Credentials смонтированы в Docker контейнер
- [ ] OpenAI API ключ настроен
- [ ] Проект запущен и health check проходит
- [ ] Тестовый запуск обработки выполнен успешно

---

## 🆘 Поддержка

Если возникли проблемы:

1. Проверьте логи: `docker-compose logs -f app`
2. Проверьте health check: `curl http://localhost:8000/health`
3. Откройте issue на GitHub
4. Проверьте [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

---

**Готово! Ваша система автоматической обработки интервью настроена! 🎉**
