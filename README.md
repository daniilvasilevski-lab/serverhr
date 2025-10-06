# 🎯 Python Interview Analyzer

Интеллектуальная система анализа видео-интервью с использованием ИИ для оценки кандидатов по 10 ключевым критериям. Система обеспечивает полный анализ видео и аудио данных, предоставляя детальную обратную связь о коммуникативных навыках, эмоциональном состоянии, языке тела и других важных аспектах.

## 🌟 Основные возможности

- **🎥 Анализ видео:** Определение эмоций, анализ позы, контроль взгляда, анализ жестов
- **🎵 Анализ аудио:** Транскрипция речи, анализ темпа, качества речи, словарного запаса
- **🧠 ИИ оценка:** GPT-4 анализ с детальной обратной связью по 10 критериям
- **📊 Мультимодальный анализ:** Интеграция видео и аудио данных
- **📈 Временной анализ:** Отслеживание изменений показателей во времени
- **🔄 API интеграция:** RESTful API для внешних систем
- **📝 Автоматические отчеты:** Экспорт в Google Sheets
- **🐳 Контейнеризация:** Docker поддержка для легкого развертывания

## 📋 Критерии оценки

1. **Коммуникативные навыки** - Ясность изложения, структурированность ответов
2. **Технические знания** - Демонстрация профессиональной экспертизы
3. **Решение проблем** - Аналитический подход к задачам
4. **Мотивация** - Энтузиазм и заинтересованность в позиции
5. **Культурная совместимость** - Соответствие ценностям компании
6. **Лидерские качества** - Способность к руководству и влиянию
7. **Адаптивность** - Гибкость и способность к изменениям
8. **Профессионализм** - Этика и деловые навыки
9. **Самопрезентация** - Уверенность и харизма
10. **Общее впечатление** - Итоговая оценка кандидата

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.11+
- Docker и Docker Compose (опционально)
- FFmpeg для обработки видео
- OpenAI API ключ

### Установка с Docker (рекомендуется)

1. **Клонирование репозитория:**
```bash
git clone <repository-url>
cd python-interview-analyzer
```

2. **Создание .env файла:**
```bash
cp .env.example .env
# Отредактируйте .env файл, добавив ваш OpenAI API ключ
```

3. **Запуск с Docker Compose:**
```bash
# Продакшн режим
docker-compose up --build

# Режим разработки
docker-compose --profile dev up --build
```

### Ручная установка

1. **Установка зависимостей:**
```bash
pip install -r requirements.txt
```

2. **Настройка переменных окружения:**
```bash
export OPENAI_API_KEY="your-openai-api-key"
export ENV="development"
```

3. **Запуск приложения:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📖 Использование API

### Базовый анализ интервью

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/interview.mp4",
    "candidate_id": "CAND-001",
    "candidate_name": "Иван Иванов",
    "preferences": "Python, FastAPI, Docker"
  }'
```

### Расширенный анализ

```bash
curl -X POST "http://localhost:8000/analyze-enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/interview.mp4",
    "candidate_id": "CAND-001",
    "candidate_name": "Иван Иванов",
    "preferences": "Python Developer",
    "questions_url": "https://example.com/questions.pdf",
    "cv_url": "https://example.com/cv.pdf",
    "use_temporal_analysis": true
  }'
```

### Временной анализ

```bash
curl -X POST "http://localhost:8000/analyze-temporal" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/interview.mp4",
    "candidate_id": "CAND-001",
    "candidate_name": "Иван Иванов",
    "preferences": "Senior Developer"
  }'
```

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Обязательная | Описание | По умолчанию |
|------------|--------------|----------|--------------|
| `OPENAI_API_KEY` | ✅ | OpenAI API ключ | - |
| `ENV` | ❌ | Окружение (development/production) | development |
| `PORT` | ❌ | Порт приложения | 8000 |
| `WHISPER_MODEL` | ❌ | Модель Whisper | base |
| `MAX_VIDEO_SIZE_MB` | ❌ | Максимальный размер видео | 100 |
| `GOOGLE_SERVICE_ACCOUNT_KEY` | ❌ | Google Sheets интеграция | - |
| `REDIS_URL` | ❌ | Redis для кеширования | - |
| `SENTRY_DSN` | ❌ | Sentry для мониторинга | - |

### Пример .env файла

```env
# Обязательные настройки
OPENAI_API_KEY=sk-your-openai-api-key-here

# Настройки приложения
ENV=production
PORT=8000
HOST=0.0.0.0

# Настройки анализа
DEFAULT_LANGUAGE=ru
WHISPER_MODEL=base
MAX_VIDEO_SIZE_MB=100

# Google Services (опционально)
GOOGLE_SERVICE_ACCOUNT_KEY=path/to/service-account.json
RESULTS_SHEET_ID=your-google-sheet-id

# Безопасность
SECRET_KEY=your-secret-key-for-production
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Мониторинг (опционально)
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=INFO
LOG_FILE=/app/logs/interview-analyzer.log
```

## 🏗️ Архитектура

```
app/
├── main.py                 # FastAPI приложение
├── models/                 # Модели данных
│   └── evaluation_criteria.py
├── services/               # Бизнес-логика
│   ├── video_processor.py      # Обработка видео
│   ├── audio_processor.py      # Обработка аудио
│   ├── integrated_analyzer.py  # Интегрированный анализ
│   ├── multimodal_analyzer_new.py  # Мультимодальный анализ
│   └── temporal_analyzer.py    # Временной анализ
├── config/                 # Конфигурация
│   └── settings.py
└── utils/                  # Утилиты
    ├── google_sheets.py        # Google Sheets интеграция
    └── video_downloader.py     # Загрузка видео

tests/                      # Тесты
├── test_api.py
├── test_processors.py
└── conftest.py

docker/                     # Docker конфигурация
├── Dockerfile
├── docker-compose.yml
└── nginx.conf
```

## 🔍 Технические детали

### Обработка видео
- **MediaPipe:** Анализ позы, жестов, лица
- **DeepFace:** Определение эмоций
- **OpenCV:** Обработка видеопотока
- **Eye Contact:** Отслеживание направления взгляда

### Обработка аудио
- **Whisper:** Транскрипция речи
- **LibROSA:** Анализ аудио характеристик
- **SpeechRecognition:** Альтернативная транскрипция
- **Анализ речи:** Темп, паузы, качество произношения

### ИИ анализ
- **GPT-4:** Холистический анализ интервью
- **Prompt Engineering:** Специализированные промпты для каждого критерия
- **Мультимодальная интеграция:** Объединение видео и аудио данных

## 🚀 Docker развертывание

### Продакшн

```bash
# Сборка и запуск продакшн версии
docker-compose up --build -d

# С мониторингом
docker-compose --profile monitoring up --build -d

# С базой данных
docker-compose --profile database up --build -d
```

### Разработка

```bash
# Режим разработки с hot reload
docker-compose --profile dev up --build

# Запуск тестов
docker-compose --profile testing up --build
```

### Мониторинг

Доступные сервисы:
- **Приложение:** http://localhost:8000
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3000 (admin/admin123)
- **Redis:** localhost:6379

## 🧪 Тестирование

```bash
# Запуск всех тестов
pytest tests/ -v

# С покрытием кода
pytest tests/ --cov=app --cov-report=html

# Только API тесты
pytest tests/test_api.py -v

# В Docker
docker-compose --profile testing up --build
```

## 📊 API Документация

После запуска приложения документация доступна по адресам:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

### Основные endpoints

- `GET /` - Информация о API
- `GET /health` - Проверка здоровья системы
- `GET /criteria` - Список критериев оценки
- `POST /analyze` - Базовый анализ интервью
- `POST /analyze-enhanced` - Расширенный анализ
- `POST /analyze-temporal` - Временной анализ
- `POST /analyze-and-save` - Анализ с сохранением

## 🛠️ Разработка

### Настройка окружения разработки

```bash
# Установка pre-commit hooks
pre-commit install

# Форматирование кода
black app/ tests/
isort app/ tests/

# Линтинг
flake8 app/ tests/
mypy app/

# Запуск в режиме разработки
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Добавление новых процессоров

1. Создайте новый файл в `app/services/`
2. Наследуйтесь от базового класса
3. Реализуйте методы обработки
4. Добавьте интеграцию в `integrated_analyzer.py`
5. Добавьте тесты

## 🔒 Безопасность

- Валидация входных данных с Pydantic
- Ограничение размера загружаемых файлов
- CORS настройки для продакшна
- Логирование всех операций
- Обработка ошибок без раскрытия внутренней информации

## 📈 Производительность

- Асинхронная обработка с asyncio
- Кеширование результатов в Redis
- Параллельная обработка видео и аудио
- Оптимизированные Docker образы
- Health checks для мониторинга

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Создайте Pull Request

## 📝 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для деталей.

## 🆘 Поддержка

- **Issues:** Создавайте issue в GitHub для багов и feature requests
- **Документация:** Полная документация доступна в `docs/`
- **Email:** support@interview-analyzer.com

## 🔄 Roadmap

- [ ] Поддержка веб-камеры в реальном времени
- [ ] Интеграция с HR системами (BambooHR, Workday)
- [ ] Мобильное приложение
- [ ] Многоязычная поддержка (English, Polish)
- [ ] Машинное обучение для персонализированных критериев
- [ ] Интеграция с видеоконференц-платформами (Zoom, Teams)
- [ ] Расширенная аналитика и дашборды
- [ ] API для интеграции с ATS системами

---

## 🎉 Благодарности

Спасибо всем контрибьюторам и сообществу за поддержку этого проекта!

**Сделано с ❤️ для улучшения процесса найма**
