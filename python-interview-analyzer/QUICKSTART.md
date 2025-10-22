# ⚡ Quick Start Guide - Interview Analyzer

Быстрый старт для начала работы с Interview Analyzer API за 5 минут.

## 🎯 Что вы получите

После выполнения этого руководства у вас будет:
- ✅ Работающий AI-анализатор интервью
- ✅ REST API на порту 8000
- ✅ Автоматическая Swagger документация
- ✅ Redis для кэширования
- ✅ Готовность к интеграции с Google Sheets

---

## 🚀 Запуск за 3 шага

### Шаг 1: Клонирование и настройка

```bash
# Клонируйте репозиторий
git clone https://github.com/your-org/interview-analyzer.git
cd interview-analyzer/python-interview-analyzer

# Скопируйте файл конфигурации
cp .env.example .env
```

### Шаг 2: Добавьте OpenAI API ключ

Откройте файл `.env` и добавьте ваш OpenAI API ключ:

```bash
nano .env  # или любой другой редактор
```

**Минимальная конфигурация:**

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

Получить API ключ: https://platform.openai.com/api-keys

### Шаг 3: Запустите Docker Compose

```bash
docker-compose up -d
```

Готово! 🎉

---

## ✅ Проверка работоспособности

### 1. Проверьте статус контейнеров

```bash
docker-compose ps
```

Вы должны увидеть 2 запущенных контейнера:
- `interview-analyzer-app` (port 8000)
- `interview-analyzer-redis` (port 6379)

### 2. Проверьте health endpoint

```bash
curl http://localhost:8000/health
```

**Ожидаемый ответ:**

```json
{
  "success": true,
  "status": "healthy",
  "services_status": {
    "analyzer": "ok",
    "sheets_service": "ok",
    "openai_api": "ok",
    "settings": "ok"
  }
}
```

### 3. Откройте Swagger UI

Откройте в браузере: http://localhost:8000/docs

Вы увидите интерактивную документацию API.

---

## 🎓 Первый анализ интервью

### Пример 1: Базовый анализ (curl)

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/interview.mp4",
    "candidate_id": "DEMO-001",
    "candidate_name": "Иван Иванов",
    "preferences": "Python, FastAPI"
  }'
```

### Пример 2: Анализ с Python

Создайте файл `test_api.py`:

```python
import requests
import json

# Отправка запроса на анализ
response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "video_url": "https://storage.googleapis.com/your-bucket/interview.mp4",
        "candidate_id": "CAND-001",
        "candidate_name": "Иван Иванов",
        "preferences": "Python, Machine Learning"
    },
    timeout=300  # 5 минут
)

# Проверка результата
if response.status_code == 200:
    result = response.json()

    if result['success']:
        analysis = result['analysis']
        print(f"✅ Анализ завершен!")
        print(f"Кандидат: {analysis['candidate_name']}")
        print(f"Общий балл: {analysis['total_score']}/100")
        print(f"Рекомендация: {analysis['recommendation']}")

        # Топ критерии
        print("\nОценки по критериям:")
        for criterion, data in analysis['scores'].items():
            print(f"  {criterion}: {data['score']}/10")
    else:
        print(f"❌ Ошибка: {result['error']}")
else:
    print(f"❌ HTTP Error: {response.status_code}")
```

Запустите:

```bash
python test_api.py
```

---

## 📊 Основные эндпоинты

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/` | GET | Информация о API |
| `/health` | GET | Проверка здоровья системы |
| `/criteria` | GET | Получение всех критериев оценки |
| `/analyze` | POST | Базовый анализ интервью |
| `/analyze-temporal` | POST | Временной анализ (30-сек сегменты) |
| `/analyze-enhanced` | POST | Расширенный анализ с CV и вопросами |
| `/docs` | GET | Swagger UI документация |

---

## 🎯 Что делать дальше?

### Интеграция с Google Sheets (опционально)

1. Создайте Google Service Account:
   - Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
   - Создайте новый проект или используйте существующий
   - Включите Google Sheets API
   - Создайте Service Account и скачайте JSON ключ

2. Добавьте в `.env`:

```env
GOOGLE_SERVICE_ACCOUNT_KEY=/path/to/service-account.json
SOURCE_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
RESULTS_SHEET_URL=https://docs.google.com/spreadsheets/d/RESULTS_SHEET_ID/edit
```

3. Перезапустите:

```bash
docker-compose restart app
```

### Включение PostgreSQL (опционально)

Для хранения результатов в базе данных:

```bash
# Запуск с PostgreSQL
docker-compose --profile database up -d

# Инициализация базы данных
docker-compose exec app python -c "from app.db import init_db; init_db()"
```

### Мониторинг (опционально)

Для включения Prometheus и Grafana:

```bash
docker-compose --profile monitoring up -d
```

Доступ:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

---

## 🔧 Настройка производительности

### Для более быстрого анализа

В `.env` настройте:

```env
# Увеличьте количество воркеров
WORKER_COUNT=4

# Разрешите больше одновременных анализов
MAX_CONCURRENT_ANALYSES=3

# Используйте меньшую модель Whisper (быстрее, но менее точно)
WHISPER_MODEL_SIZE=tiny  # tiny, base, small, medium, large
```

### Для лучшего качества

```env
# Больше воркеров и памяти
WORKER_COUNT=8

# Большая модель Whisper
WHISPER_MODEL_SIZE=medium  # или large

# Увеличьте лимит видео
MAX_VIDEO_SIZE_MB=200
```

---

## 📝 Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Только логи приложения
docker-compose logs -f app

# Последние 100 строк
docker-compose logs --tail=100 app

# Поиск ошибок
docker-compose logs app | grep ERROR
```

---

## 🛑 Остановка

```bash
# Остановить все контейнеры
docker-compose down

# Остановить и удалить volumes (данные будут потеряны!)
docker-compose down -v
```

---

## 🐛 Troubleshooting

### Проблема: "Connection refused"

**Решение:**

```bash
# Проверьте статус
docker-compose ps

# Перезапустите
docker-compose restart

# Проверьте логи
docker-compose logs app
```

### Проблема: "OpenAI API key invalid"

**Решение:**

1. Проверьте ключ в `.env`
2. Убедитесь, что ключ начинается с `sk-`
3. Проверьте, что у вас есть кредиты на OpenAI
4. Перезапустите: `docker-compose restart app`

### Проблема: Медленная обработка

**Решение:**

1. Увеличьте ресурсы в `docker-compose.yaml`:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
```

2. Используйте меньшую модель Whisper:

```env
WHISPER_MODEL_SIZE=base  # вместо medium или large
```

---

## 📚 Дополнительная документация

- **API Guide**: [API_GUIDE.md](./API_GUIDE.md) - Полная документация API
- **Deployment**: [DEPLOYMENT.md](./DEPLOYMENT.md) - Развертывание в production
- **README**: [README.md](./README.md) - Общая информация о проекте

---

## 💡 Советы

1. **Размер видео**: Для быстрого тестирования используйте видео до 5 минут
2. **Качество**: Минимум 720p для лучших результатов анализа лица
3. **Формат**: MP4 рекомендуется для лучшей совместимости
4. **Язык**: Система поддерживает русский, английский и польский

---

## 🎉 Готово!

Теперь вы готовы использовать Interview Analyzer API!

**Следующие шаги:**

1. ✅ Попробуйте анализ тестового интервью
2. ✅ Изучите [API_GUIDE.md](./API_GUIDE.md) для продвинутых функций
3. ✅ Настройте интеграцию с вашей системой
4. ✅ Разверните в production (см. [DEPLOYMENT.md](./DEPLOYMENT.md))

---

## 🆘 Нужна помощь?

- **Документация**: http://localhost:8000/docs
- **GitHub Issues**: https://github.com/your-org/interview-analyzer/issues
- **Email**: support@example.com

---

**Приятного использования! 🚀**
