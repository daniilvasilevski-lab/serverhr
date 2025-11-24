# 🚀 БЫСТРЫЙ СТАРТ - Interview Analyzer

## ✅ Проект готов на 100% к запуску!

Следуйте этим простым шагам для запуска системы автоматического анализа интервью.

---

## 📋 Что вы получите

✅ Автоматический анализ видео-интервью с AI
✅ Интеграция с Google Sheets (вход/выход)
✅ 10 критериев оценки кандидатов
✅ Мультиязычность (RU/EN/PL)
✅ Легкое редактирование промптов без изменения кода
✅ Production-ready Docker setup

> Уже скачали репозиторий и хотите быстро запустить? Смотрите краткое пошаговое руководство: [LOCAL_RUN_GUIDE.md](LOCAL_RUN_GUIDE.md).

### 🔄 Как обновить уже скачанный репозиторий до последней версии

Если у вас есть локальные правки, сохраните их (commit или `git stash`) перед обновлением.

```bash
cd python-interview-analyzer
# Посмотреть, нет ли несохранённых файлов
git status

# Скачать свежие изменения из основной ветки
git pull origin main

# Пересобрать контейнеры с учётом обновлений
docker-compose down
docker-compose up --build -d

# Проверить, что всё поднялось
docker-compose ps
curl http://localhost:8000/health
```

Если используете dev-профиль: замените команды на `docker-compose --profile dev ...`.

#### Если при `git pull` появились конфликты (как на скриншоте GitHub)

1. Сохраните важные локальные файлы (обычно `.env` и ключи из `credentials/`).
2. Если хотите просто взять последнее состояние из основной ветки и у вас нет нужных правок:
   ```bash
   git fetch origin
   git reset --hard origin/main
   git clean -fd  # удалит лишние неотслеживаемые файлы
   ```
   Затем пересоберите контейнеры:
   ```bash
   docker compose down
   docker compose up --build
   ```
3. Если есть нужные локальные изменения, откройте помеченные файлы (обычно `LOCAL_RUN_GUIDE.md`, `START_HERE.md`, `dockerfile`) и вручную выберите нужные версии в редакторе, удалив маркеры `<<<<<<<`, `=======`, `>>>>>>>`, после чего завершите merge:
   ```bash
   git add .
   git commit -m "Resolve merge conflicts"
   ```
   И снова пересоберите контейнеры как в шаге выше.

> При сбросе через `git reset --hard` все несохранённые изменения удаляются, поэтому заранее сделайте копию `.env` и ключей.

---

## 🎯 Шаг 1: Подготовка Google Sheets

### 1.1 Создайте Service Account

1. Перейдите: https://console.cloud.google.com/
2. Создайте проект (или используйте существующий)
3. Включите Google Sheets API и Google Drive API
4. Создайте Service Account:
   - IAM & Admin → Service Accounts → Create
   - Название: `interview-analyzer-service`
   - Роль: Editor
5. Создайте JSON ключ:
   - Keys → Add Key → Create new key → JSON
   - Сохраните файл как `credentials/service-account.json`

### 1.2 Создайте Google Таблицы

**Входная таблица (Source):**

| A  | B    | C     | D     | E           | F      | G         | H      | I         | J          | K             | L         |
|----|------|-------|-------|-------------|--------|-----------|--------|-----------|------------|---------------|-----------|
| ID | Name | Email | Phone | Preferences | CV_gcs | video_gcs | CV_URL | Video_URL | created_at | Questions_URL | Processed |

**Выходная таблица (Results):**

| A  | B    | C     | D     | E        | F             | G          | H         | I          | J        | K        | L                 | M            | N             | O              |
|----|------|-------|-------|----------|---------------|------------|-----------|------------|----------|----------|-------------------|--------------|---------------|----------------|
| ID | Name | Email | Phone | Language | Communication | Motivation | Technical | Analytical | Creative | Teamwork | Stress_Resistance | Adaptability | Overall_Score | Recommendation |

### 1.3 Дайте доступ Service Account

1. Откройте JSON ключ, найдите поле `client_email`
2. Скопируйте этот email (например: `interview-analyzer@project.iam.gserviceaccount.com`)
3. В обеих таблицах нажмите **Share**
4. Вставьте email, выберите **Editor**, нажмите Send
5. Скопируйте URL обеих таблиц

---

## 🔑 Шаг 2: Настройка Environment

### 2.1 Создайте .env файл

```bash
cd python-interview-analyzer
cp .env.production.example .env
nano .env  # или любой редактор
```

### 2.2 Заполните ОБЯЗАТЕЛЬНЫЕ параметры

```env
# OpenAI API Key (получить: https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-ваш-настоящий-ключ-здесь

# Google Service Account
GOOGLE_SERVICE_ACCOUNT_KEY=/app/credentials/service-account.json

# URL Google Sheets
SOURCE_SHEET_URL=https://docs.google.com/spreadsheets/d/ВАШ_ID_ВХОДНОЙ_ТАБЛИЦЫ/edit
RESULTS_SHEET_URL=https://docs.google.com/spreadsheets/d/ВАШ_ID_ВЫХОДНОЙ_ТАБЛИЦЫ/edit

# Автоматическая обработка
ENABLE_AUTO_PROCESSING=true
SCAN_INTERVAL_MINUTES=5
```

### 2.3 Разместите credentials

```bash
mkdir -p credentials
# Скопируйте ваш service-account.json в credentials/
cp /path/to/your/service-account.json credentials/service-account.json
```

---

## 🐳 Шаг 3: Запуск с Docker

### 3.1 Запустите контейнеры

```bash
docker-compose up -d
```

### 3.2 Проверьте логи

```bash
docker-compose logs -f app
```

Вы должны увидеть:
```
✅ Google Sheets connection established
✅ Connected to source sheet: ...
✅ Connected to results sheet: ...
✅ Prompts loaded from: prompts.yaml
```

### 3.3 Проверьте health

```bash
curl http://localhost:8000/health
```

Ответ должен быть:
```json
{
  "success": true,
  "status": "healthy"
}
```

---

## 📝 Шаг 4: Тестовый запуск

### 4.1 Добавьте тестовое интервью

В **входную таблицу** добавьте строку:

| ID       | Name        | Email            | Phone   | Video_URL                         | Processed |
|----------|-------------|------------------|---------|-----------------------------------|-----------|
| CAND-001 | Иван Иванов | ivan@example.com | +79991  | https://example.com/interview.mp4 | 0         |

### 4.2 Запустите обработку

**Вариант A: Автоматически** (если ENABLE_AUTO_PROCESSING=true)
- Подождите 5 минут (или SCAN_INTERVAL_MINUTES)
- Система автоматически обработает

**Вариант B: Вручную через API**

```bash
curl -X POST "http://localhost:8000/api/v1/sheets/process-all"
```

**Вариант C: Через Swagger UI**

1. Откройте: http://localhost:8000/docs
2. Найдите endpoint `POST /api/v1/sheets/process-all`
3. Нажмите **Try it out** → **Execute**

### 4.3 Проверьте результаты

1. Откройте **выходную таблицу** (Results)
2. Вы увидите новую строку с результатами анализа
3. Во **входной таблице** колонка `Processed` станет `1`

---

## 🎨 Шаг 5: Настройка промптов (опционально)

### 5.1 Редактирование промптов

```bash
nano prompts.yaml
```

В этом файле вы можете:
- Изменить системные промпты для анализаторов
- Настроить критерии оценки
- Изменить строгость оценок
- Добавить свои инструкции

### 5.2 Применение изменений

**Вариант A: Перезапуск**
```bash
docker-compose restart app
```

**Вариант B: Hot-reload (без перезапуска)**
```bash
curl -X POST "http://localhost:8000/api/v1/sheets/reload-prompts"
```

---

## 📊 API Endpoints

### Основные endpoints

```bash
# Health check
GET /health

# Информация о критериях
GET /criteria

# Анализ одного интервью
POST /analyze

# Обработка всех из Google Sheets
POST /api/v1/sheets/process-all

# Список необработанных
GET /api/v1/sheets/unprocessed

# Перезагрузка промптов
POST /api/v1/sheets/reload-prompts
```

### Swagger UI

Полная документация API: **http://localhost:8000/docs**

---

## 🔍 Мониторинг

### Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Только приложение
docker-compose logs -f app

# Последние 100 строк
docker-compose logs --tail=100 app

# Поиск ошибок
docker-compose logs app | grep ERROR
```

### Статистика обработки

```bash
curl http://localhost:8000/api/v1/sheets/unprocessed
```

---

## 🛠️ Troubleshooting

### Проблема: "Google Sheets not configured"

**Решение:**
```bash
# Проверьте наличие файла
ls -la credentials/service-account.json

# Проверьте .env
grep GOOGLE credentials/service-account.json

# Проверьте логи
docker-compose logs app | grep "Google Sheets"
```

### Проблема: "Permission denied" для таблицы

**Решение:**
1. Откройте service-account.json
2. Найдите `client_email`
3. Убедитесь, что этот email имеет доступ **Editor** к обеим таблицам
4. Переоткройте доступ если нужно

### Проблема: Интервью не обрабатываются

**Проверьте:**
```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Список необработанных
curl http://localhost:8000/api/v1/sheets/unprocessed

# 3. Запустите вручную
curl -X POST http://localhost:8000/api/v1/sheets/process-all

# 4. Проверьте логи
docker-compose logs -f app
```

---

## 📚 Дополнительная документация

- **API_GUIDE.md** - Полная документация API с примерами
- **DEPLOYMENT.md** - Развертывание в production
- **GOOGLE_SHEETS_SETUP.md** - Детальная настройка Google Sheets
- **QUICKSTART.md** - Альтернативный quick start

---

## ✅ Checklist готовности

Перед production использованием убедитесь:

- [ ] Google Service Account создан
- [ ] Обе таблицы созданы с правильными колонками
- [ ] Service Account имеет доступ **Editor** к таблицам
- [ ] Файл `.env` настроен
- [ ] Credentials находятся в `credentials/service-account.json`
- [ ] OpenAI API ключ валидный и имеет кредиты
- [ ] Docker контейнеры запущены
- [ ] Health check проходит успешно
- [ ] Тестовый анализ выполнен
- [ ] Промпты настроены под вашу специфику

---

## 🎉 Готово!

Ваша система автоматического анализа интервью готова к работе!

**Что дальше:**

1. Добавьте реальные интервью во входную таблицу
2. Настройте промпты под вашу специфику
3. Включите автоматическую обработку (ENABLE_AUTO_PROCESSING=true)
4. Мониторьте результаты в выходной таблице

---

## 🆘 Поддержка

- **Issues**: https://github.com/your-repo/issues
- **Documentation**: http://localhost:8000/docs
- **Email**: support@example.com

---

**Приятного использования! 🚀**
