# 📚 Interview Analyzer API - Руководство разработчика

Полное руководство по использованию API анализа интервью с искусственным интеллектом.

## 🚀 Быстрый старт

### Запуск сервера

```bash
# Development mode
docker-compose up

# Production mode
docker-compose --profile production up

# С мониторингом
docker-compose --profile monitoring up
```

API будет доступен по адресу: `http://localhost:8000`

Документация Swagger: `http://localhost:8000/docs`

---

## 🔐 Аутентификация

В текущей версии API не требует аутентификации. Для production рекомендуется добавить:
- API ключи
- OAuth 2.0
- Rate limiting

---

## 📋 Основные эндпоинты

### 1. Информация о API

```http
GET /
```

**Ответ:**

```json
{
  "message": "🤖 Interview Analyzer API v2.0",
  "description": "Многомодальный анализ интервью с ИИ",
  "features": [
    "10 критериев оценки",
    "Анализ аудио, видео и текста",
    "Невербальный анализ",
    "Интеграция с Google Sheets"
  ],
  "docs": "/docs"
}
```

---

### 2. Проверка здоровья системы

```http
GET /health
```

**Ответ:**

```json
{
  "success": true,
  "status": "healthy",
  "unprocessed_count": 0,
  "services_status": {
    "analyzer": "ok",
    "sheets_service": "ok",
    "openai_api": "ok",
    "settings": "ok"
  }
}
```

**Статус коды:**
- `200`: Все сервисы работают
- `503`: Один или несколько сервисов недоступны

---

### 3. Получение критериев оценки

```http
GET /criteria
```

**Ответ:**

```json
{
  "success": true,
  "criteria": {
    "communication_skills": {
      "name": "Коммуникативные навыки",
      "description": "Способность ясно и эффективно общаться",
      "key_indicators": ["Четкость речи", "Структурированность", "Активное слушание"],
      "verbal_aspects": ["Словарный запас", "Грамматика", "Артикуляция"],
      "non_verbal_aspects": ["Жесты", "Зрительный контакт", "Мимика"]
    },
    // ... остальные 9 критериев
  }
}
```

---

### 4. Базовый анализ интервью

```http
POST /analyze
Content-Type: application/json
```

**Тело запроса:**

```json
{
  "video_url": "https://storage.googleapis.com/my-bucket/interview-video.mp4",
  "candidate_id": "CAND-2024-001",
  "candidate_name": "Иван Иванов",
  "preferences": "Python, FastAPI, Machine Learning"
}
```

**Пример запроса (curl):**

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/interview.mp4",
    "candidate_id": "CAND-001",
    "candidate_name": "Иван Иванов",
    "preferences": "Python, ML"
  }'
```

**Пример запроса (Python):**

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "video_url": "https://example.com/interview.mp4",
        "candidate_id": "CAND-001",
        "candidate_name": "Иван Иванов",
        "preferences": "Python, ML"
    }
)

result = response.json()
print(f"Total Score: {result['analysis']['total_score']}")
```

**Пример запроса (JavaScript):**

```javascript
const response = await fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    video_url: 'https://example.com/interview.mp4',
    candidate_id: 'CAND-001',
    candidate_name: 'Иван Иванов',
    preferences: 'Python, ML'
  })
});

const result = await response.json();
console.log('Analysis:', result.analysis);
```

**Ответ:**

```json
{
  "success": true,
  "analysis": {
    "candidate_id": "CAND-2024-001",
    "candidate_name": "Иван Иванов",
    "interview_duration": 1800,
    "scores": {
      "communication_skills": {
        "score": 8,
        "verbal_score": 4,
        "non_verbal_score": 4,
        "explanation": "Отличные коммуникативные навыки, четкая речь",
        "key_observations": [
          "Хорошая структура ответов",
          "Активный зрительный контакт",
          "Уверенная речь"
        ],
        "specific_examples": [
          "При ответе на вопрос о проекте использовал четкую структуру: проблема - решение - результат",
          "Поддерживал зрительный контакт 80% времени",
          "Речь без слов-паразитов"
        ]
      },
      // ... остальные критерии
    },
    "audio_quality": 8,
    "video_quality": 9,
    "emotion_analysis": {
      "confident": 45.0,
      "happy": 30.0,
      "neutral": 20.0,
      "nervous": 5.0
    },
    "eye_contact_percentage": 75.5,
    "gesture_frequency": 12,
    "posture_confidence": 8,
    "speech_pace": "нормальный",
    "vocabulary_richness": 7,
    "grammar_quality": 8,
    "answer_structure": 7,
    "total_score": 78,
    "weighted_score": 78.5,
    "recommendation": "Сильный кандидат. Рекомендуется к найму.",
    "detailed_feedback": "Кандидат продемонстрировал отличные коммуникативные навыки...",
    "analysis_timestamp": "2024-01-15T14:30:00",
    "ai_model_version": "integrated-v1.0"
  },
  "error": null
}
```

---

### 5. Анализ с сохранением в Google Sheets

```http
POST /analyze-and-save
Content-Type: application/json
```

**Тело запроса:** (то же, что и для `/analyze`)

**Особенности:**
- Автоматически сохраняет результаты в Google Sheets
- Работает в фоновом режиме
- Не блокирует ответ API

**Пример:**

```bash
curl -X POST "http://localhost:8000/analyze-and-save" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/interview.mp4",
    "candidate_id": "CAND-001",
    "candidate_name": "Иван Иванов",
    "preferences": "Python"
  }'
```

---

### 6. 🕒 Временной анализ (30-секундная сегментация)

```http
POST /analyze-temporal
Content-Type: application/json
```

**Описание:**
Анализ интервью с разбивкой на 30-секундные сегменты для отслеживания динамики поведения.

**Тело запроса:**

```json
{
  "video_url": "https://example.com/interview.mp4",
  "candidate_id": "CAND-002",
  "candidate_name": "Мария Петрова",
  "preferences": "Frontend, React"
}
```

**Что анализируется по сегментам:**
- Уверенность кандидата
- Уровень стресса
- Качество коммуникации
- Вовлеченность
- Адаптивность к разным типам вопросов

**Пример ответа (дополнительные данные):**

```json
{
  "success": true,
  "analysis": {
    // ... стандартные поля ...
    "detailed_feedback": "ВРЕМЕННЫЕ ИНСАЙТЫ:\n• Тренд уверенности: растущий (6.2 → 7.8)\n• Стрессоустойчивость: пики в 2 сегментах, средний уровень 4.2/10\n\nПОВЕДЕНИЕ ПО ТИПАМ ВОПРОСОВ:\n• знакомство: уверенность 8.5/10, коммуникация 8.0/10\n• технические: уверенность 6.5/10, коммуникация 7.0/10\n• проблемные: уверенность 5.8/10, коммуникация 6.5/10\n\nКРИТИЧЕСКИЕ МОМЕНТЫ: 3 значительных изменений в поведении\nАДАПТИВНОСТЬ: 4 успешных адаптаций к новым типам вопросов"
  }
}
```

---

### 7. 🚀 Расширенный анализ с CV и вопросами

```http
POST /analyze-enhanced
Content-Type: application/json
```

**Тело запроса:**

```json
{
  "video_url": "https://example.com/interview.mp4",
  "candidate_id": "CAND-003",
  "candidate_name": "Алексей Сидоров",
  "preferences": "DevOps, Kubernetes",
  "questions_url": "https://example.com/questions.pdf",
  "cv_url": "https://example.com/cv.pdf",
  "use_temporal_analysis": true
}
```

**Параметры:**
- `questions_url` (optional): URL файла с вопросами интервью (PDF/DOCX)
- `cv_url` (optional): URL резюме кандидата (PDF/DOCX)
- `use_temporal_analysis` (optional): Использовать временной анализ (default: true)

**Пример с Python:**

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze-enhanced",
    json={
        "video_url": "https://storage.googleapis.com/bucket/interview.mp4",
        "candidate_id": "CAND-003",
        "candidate_name": "Алексей Сидоров",
        "preferences": "DevOps, Kubernetes",
        "questions_url": "https://storage.googleapis.com/bucket/questions.pdf",
        "cv_url": "https://storage.googleapis.com/bucket/cv.pdf",
        "use_temporal_analysis": True
    }
)

result = response.json()

# Извлечение конкретных оценок
scores = result['analysis']['scores']
communication_score = scores['communication_skills']['score']
technical_score = scores['professional_skills']['score']

print(f"Коммуникация: {communication_score}/10")
print(f"Технические навыки: {technical_score}/10")
print(f"Рекомендация: {result['analysis']['recommendation']}")
```

**Дополнительная информация в ответе:**

```json
{
  "detailed_feedback": "...\n\n📋 CV АНАЛИЗ:\n• Оценка CV: 8/10\n• Релевантный опыт: 3 года работы с Docker и Kubernetes\n• Технические навыки: Docker, Kubernetes, CI/CD, AWS, Terraform\n\n❓ СТРУКТУРА ИНТЕРВЬЮ:\n• Количество вопросов: 15\n• Структура: знакомство (3), технические (8), поведенческие (4)\n• Ожидаемая длительность: 45 минут\n\n✅ CV СООТВЕТСТВИЕ: Высококачественное CV подтверждается уверенным поведением в интервью"
}
```

---

## 🔄 Управление задачами (Task Scheduler)

### Получение статистики планировщика

```http
GET /api/v1/tasks/stats
```

**Ответ:**

```json
{
  "status": "running",
  "total_scans": 45,
  "last_scan": "2024-01-15T14:25:00",
  "total_processed": 120,
  "total_failed": 3,
  "is_running": true
}
```

### Запуск сканирования вручную

```http
POST /api/v1/tasks/trigger
```

**Ответ:**

```json
{
  "message": "Scan triggered successfully",
  "timestamp": "2024-01-15T14:30:00"
}
```

### Остановка планировщика

```http
POST /api/v1/tasks/stop
```

### Запуск планировщика

```http
POST /api/v1/tasks/start
```

---

## 📊 Примеры использования

### Пример 1: Простой анализ одного кандидата

```python
import requests

# Конфигурация
API_URL = "http://localhost:8000"
VIDEO_URL = "https://storage.googleapis.com/my-bucket/interview-john-doe.mp4"

# Отправка запроса
response = requests.post(
    f"{API_URL}/analyze",
    json={
        "video_url": VIDEO_URL,
        "candidate_id": "2024-JAN-001",
        "candidate_name": "John Doe",
        "preferences": "Python, Data Science"
    },
    timeout=300  # 5 минут таймаут
)

# Проверка ответа
if response.status_code == 200:
    result = response.json()

    if result['success']:
        analysis = result['analysis']
        print(f"✅ Анализ завершен для {analysis['candidate_name']}")
        print(f"Общий балл: {analysis['total_score']}/100")
        print(f"Рекомендация: {analysis['recommendation']}")

        # Топ-3 критерия
        scores = analysis['scores']
        sorted_scores = sorted(
            scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )[:3]

        print("\nТоп-3 навыка:")
        for criterion, data in sorted_scores:
            print(f"  • {criterion}: {data['score']}/10")
    else:
        print(f"❌ Ошибка: {result['error']}")
else:
    print(f"❌ HTTP Error: {response.status_code}")
```

### Пример 2: Массовый анализ нескольких кандидатов

```python
import requests
import time
from typing import List, Dict

def analyze_batch(candidates: List[Dict]) -> List[Dict]:
    """Анализ нескольких кандидатов"""
    results = []

    for candidate in candidates:
        print(f"Анализ: {candidate['name']}...")

        response = requests.post(
            "http://localhost:8000/analyze-and-save",
            json={
                "video_url": candidate['video_url'],
                "candidate_id": candidate['id'],
                "candidate_name": candidate['name'],
                "preferences": candidate.get('preferences', '')
            },
            timeout=300
        )

        if response.status_code == 200:
            result = response.json()
            if result['success']:
                results.append({
                    'name': candidate['name'],
                    'score': result['analysis']['total_score'],
                    'recommendation': result['analysis']['recommendation']
                })
            else:
                results.append({
                    'name': candidate['name'],
                    'error': result['error']
                })

        # Пауза между запросами
        time.sleep(2)

    return results

# Использование
candidates = [
    {
        'id': 'CAND-001',
        'name': 'Иван Иванов',
        'video_url': 'https://example.com/ivan.mp4',
        'preferences': 'Python, ML'
    },
    {
        'id': 'CAND-002',
        'name': 'Мария Петрова',
        'video_url': 'https://example.com/maria.mp4',
        'preferences': 'React, TypeScript'
    }
]

batch_results = analyze_batch(candidates)

# Вывод результатов
for result in batch_results:
    if 'error' in result:
        print(f"❌ {result['name']}: {result['error']}")
    else:
        print(f"✅ {result['name']}: {result['score']}/100 - {result['recommendation']}")
```

### Пример 3: Интеграция с Google Sheets

```python
import requests
import gspread
from google.oauth2.service_account import Credentials

# Подключение к Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file('service-account.json', scopes=scope)
client = gspread.authorize(creds)

# Открытие таблицы
sheet = client.open("Кандидаты на интервью").sheet1

# Получение необработанных строк
all_rows = sheet.get_all_values()

for row_idx, row in enumerate(all_rows[1:], start=2):  # Пропускаем заголовки
    # row = [ID, Name, Video_URL, Processed, ...]
    if row[3] == "0":  # Не обработано
        candidate_id = row[0]
        candidate_name = row[1]
        video_url = row[2]

        print(f"Обработка: {candidate_name}")

        # Анализ через API
        response = requests.post(
            "http://localhost:8000/analyze",
            json={
                "video_url": video_url,
                "candidate_id": candidate_id,
                "candidate_name": candidate_name,
                "preferences": ""
            }
        )

        if response.status_code == 200 and response.json()['success']:
            analysis = response.json()['analysis']

            # Обновление строки в таблице
            sheet.update_cell(row_idx, 4, "1")  # Отмечаем как обработано
            sheet.update_cell(row_idx, 5, analysis['total_score'])  # Общий балл
            sheet.update_cell(row_idx, 6, analysis['recommendation'])  # Рекомендация

            print(f"✅ Обработано: {candidate_name} - {analysis['total_score']}/100")
        else:
            print(f"❌ Ошибка обработки: {candidate_name}")
```

### Пример 4: Сравнение кандидатов

```python
import requests
import pandas as pd

def compare_candidates(candidate_urls: Dict[str, str]) -> pd.DataFrame:
    """Сравнение нескольких кандидатов"""
    results = []

    for name, video_url in candidate_urls.items():
        response = requests.post(
            "http://localhost:8000/analyze",
            json={
                "video_url": video_url,
                "candidate_id": name,
                "candidate_name": name,
                "preferences": ""
            }
        )

        if response.status_code == 200 and response.json()['success']:
            analysis = response.json()['analysis']
            scores = analysis['scores']

            results.append({
                'Candidate': name,
                'Total Score': analysis['total_score'],
                'Communication': scores['communication_skills']['score'],
                'Technical': scores['professional_skills']['score'],
                'Analytical': scores['analytical_thinking']['score'],
                'Stress Resistance': scores['stress_resistance']['score'],
                'Recommendation': analysis['recommendation']
            })

    return pd.DataFrame(results).sort_values('Total Score', ascending=False)

# Использование
candidates = {
    'Иван Иванов': 'https://example.com/ivan.mp4',
    'Мария Петрова': 'https://example.com/maria.mp4',
    'Алексей Сидоров': 'https://example.com/alexey.mp4'
}

comparison = compare_candidates(candidates)
print(comparison.to_string(index=False))

# Вывод лучшего кандидата
best_candidate = comparison.iloc[0]
print(f"\n🏆 Лучший кандидат: {best_candidate['Candidate']} ({best_candidate['Total Score']}/100)")
```

---

## ⚠️ Обработка ошибок

### Коды ошибок

| Код | Описание | Решение |
|-----|----------|---------|
| 200 | Успешно | - |
| 400 | Неверный запрос | Проверьте формат запроса |
| 422 | Ошибка валидации | Проверьте обязательные поля |
| 500 | Внутренняя ошибка сервера | Проверьте логи, повторите запрос |
| 503 | Сервис недоступен | Проверьте статус сервисов через `/health` |

### Пример обработки ошибок

```python
import requests
from requests.exceptions import Timeout, ConnectionError

def safe_analyze(video_url: str, candidate_info: dict, max_retries: int = 3):
    """Безопасный анализ с retry логикой"""

    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8000/analyze",
                json={
                    "video_url": video_url,
                    **candidate_info
                },
                timeout=300
            )

            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    return result['analysis']
                else:
                    print(f"Ошибка анализа: {result['error']}")
                    return None

            elif response.status_code == 503:
                print("Сервис недоступен. Повторная попытка...")
                time.sleep(5 * (attempt + 1))  # Exponential backoff
                continue

            else:
                print(f"HTTP Error {response.status_code}")
                return None

        except Timeout:
            print(f"Timeout на попытке {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(10)
                continue
            return None

        except ConnectionError:
            print("Ошибка подключения к API")
            return None

    print("Превышено количество попыток")
    return None
```

---

## 🔧 Настройка и конфигурация

### Переменные окружения

Создайте файл `.env`:

```env
# Обязательные
OPENAI_API_KEY=sk-your-api-key-here

# Опциональные
ENV=production
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO

# Google Sheets
GOOGLE_SERVICE_ACCOUNT_KEY=/path/to/service-account.json
SOURCE_SHEET_URL=https://docs.google.com/spreadsheets/d/.../edit
RESULTS_SHEET_URL=https://docs.google.com/spreadsheets/d/.../edit

# Analysis
DEFAULT_LANGUAGE=ru
WHISPER_MODEL_SIZE=base
MAX_VIDEO_SIZE_MB=100

# Task Scheduler
AUTO_PROCESSING_ENABLED=true
SCAN_INTERVAL_MINUTES=30
MAX_CONCURRENT_ANALYSES=3
```

---

## 📈 Мониторинг и логи

### Просмотр логов

```bash
# Логи приложения
docker-compose logs -f app

# Логи всех сервисов
docker-compose logs -f

# Последние 100 строк
docker-compose logs --tail=100 app
```

### Метрики (Prometheus)

Если запущен с профилем monitoring:

```bash
# Prometheus UI
http://localhost:9090

# Grafana dashboards
http://localhost:3000
```

---

## 🎯 Best Practices

### 1. Таймауты

Всегда указывайте таймаут для запросов:

```python
response = requests.post(url, json=data, timeout=300)  # 5 минут
```

### 2. Retry логика

Используйте retry для сетевых ошибок:

```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
```

### 3. Асинхронная обработка

Для массовых анализов используйте асинхронность:

```python
import asyncio
import aiohttp

async def analyze_async(session, candidate):
    async with session.post(
        "http://localhost:8000/analyze",
        json=candidate
    ) as response:
        return await response.json()

async def batch_analyze(candidates):
    async with aiohttp.ClientSession() as session:
        tasks = [analyze_async(session, c) for c in candidates]
        return await asyncio.gather(*tasks)

# Использование
results = asyncio.run(batch_analyze(candidates))
```

### 4. Кэширование

Кэшируйте результаты для повторных запросов:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def get_cached_analysis(video_url_hash: str):
    # Проверка в базе/кэше
    pass
```

---

## 💡 Советы и подсказки

1. **Размер видео**: Рекомендуется до 100MB для оптимальной скорости
2. **Формат видео**: MP4, AVI, MOV поддерживаются
3. **Качество видео**: Минимум 720p для лучшего анализа лиц
4. **Длительность**: Оптимально 15-45 минут
5. **Язык**: Поддерживается русский, английский, польский

---

## 🆘 Поддержка

- **Документация**: http://localhost:8000/docs
- **GitHub Issues**: https://github.com/your-repo/issues
- **Email**: support@example.com

---

## 📝 Лицензия

MIT License - см. LICENSE file
