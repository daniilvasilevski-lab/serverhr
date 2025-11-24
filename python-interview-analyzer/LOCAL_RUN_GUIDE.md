# Локальный запуск из уже скачанного репозитория

Эта инструкция рассчитана на ситуацию, когда репозиторий уже скачан (как на скриншоте) и вам нужно просто запустить сервис.

## 🏃 TL;DR (5 команд)
```bash
cd python-interview-analyzer
cp .env.production.example .env
echo "OPENAI_API_KEY=sk-..." >> .env  # вставьте свой ключ
docker compose up --build
curl http://localhost:8000/health
```
Если нужен Google Sheets — добавьте URL таблиц в `.env` и положите JSON ключ в `credentials/service-account.json` (см. шаги ниже).

## 1. Предварительные требования
- Docker и Docker Compose установлены (`docker --version`, `docker compose version`).
- Python 3.11+ только если хотите запускать без Docker.
- FFmpeg установлен в системе (нужен для аудио/видео обработки).

### 1.1 Как установить Docker и FFmpeg (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release ffmpeg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/$(. /etc/os-release && echo "$ID")/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/$(. /etc/os-release && echo "$ID") \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"  # выйдите и зайдите в сессию снова
```
Проверьте версии после повторного входа: `docker --version`, `docker compose version`, `ffmpeg -version`.

## 2. Подготовьте переменные окружения
1. Перейдите в папку проекта:
   ```bash
   cd python-interview-analyzer
   ```
2. Скопируйте пример настроек и откройте файл для редактирования:
   ```bash
   cp .env.production.example .env
   nano .env  # можно любой редактор
   ```
3. Заполните как минимум:
   - `OPENAI_API_KEY` — ваш ключ OpenAI.
   - `SOURCE_SHEET_URL` и `RESULTS_SHEET_URL` — ссылки на входную и выходную Google-таблицы (если используете Sheets).
   - `GOOGLE_SERVICE_ACCOUNT_KEY=/app/credentials/service-account.json` — путь внутри контейнера до JSON ключа сервисного аккаунта.
   - `ENABLE_AUTO_PROCESSING=true` если хотите авто-сканирование таблицы; иначе можно оставить `false` и запускать вручную через API.

Пример минимального `.env` без Google Sheets (анализ через API):
```env
OPENAI_API_KEY=sk-ваш-ключ
ENV=development
ENABLE_AUTO_PROCESSING=false
```

## 3. Поместите ключ сервисного аккаунта
- Файл JSON положите в `credentials/` (например, `credentials/google-credentials.json`).
- Если имя отличное от `service-account.json`, либо переименуйте файл, либо поправьте путь в `.env` переменной `GOOGLE_SERVICE_ACCOUNT_KEY`.
- Убедитесь, что сервисный аккаунт имеет права **Editor** на обе ваши таблицы.

## 4. Запуск через Docker (рекомендуется)
```bash
docker compose up --build
```
- Первый запуск скачает образы и соберёт контейнеры; это нормально, если занимает время.
- Логи приложения: `docker compose logs -f app`.

## 5. Проверка работоспособности
1. Откройте health-check:
   ```bash
   curl http://localhost:8000/health
   ```
   Ожидается `{ "success": true, "status": "healthy" }`.
2. Документация API: http://localhost:8000/docs
3. ReDoc: http://localhost:8000/redoc

## 6. Обработка тестовой строки в таблице
1. В **входной** таблице добавьте строку (пример):
   - `ID=CAND-001`, `Name=Иван Иванов`, `Video_URL=https://.../interview.mp4`, `Processed=0`.
2. Если `ENABLE_AUTO_PROCESSING=true`, дождитесь интервала `SCAN_INTERVAL_MINUTES`.
3. Для ручного запуска:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/sheets/process-all"
   ```

## 7. Альтернативный запуск без Docker
Только если Docker недоступен:
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 8. Частые проблемы
- **Нет доступа к таблицам** — проверьте, что сервисный аккаунт добавлен в Google Sheets с правами Editor.
- **FFmpeg not found** — установите FFmpeg (`sudo apt install ffmpeg`).
- **OPENAI_API_KEY пустой** — без ключа запросы к модели не будут работать.
