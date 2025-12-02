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

### Если `docker` или `docker compose` не найдены
```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release ffmpeg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/$(. /etc/os-release && echo "$ID")/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$(. /etc/os-release && echo \"$ID\") $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"  # выйдите и зайдите в терминал заново
docker --version && docker compose version && ffmpeg -version
```
> После `usermod` обязательно перезайдите в систему/терминал, иначе команда `docker` всё ещё может быть недоступна.

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

codex/analyze-project-readiness-and-setup-g70f2j
=======
HEAD
=======
codex/analyze-project-readiness-and-setup-ilokil
origin/main
main
## 7. Автозапуск без Docker в одном терминале (всё включено)
Если нужно, чтобы установка зависимостей и запуск сервера шли в **одном терминале и без Docker**, используйте новый скрипт:
```bash
# 1) Установите модуль для виртуальных окружений (иначе будет ошибка
#    "externally-managed-environment" при pip install)
sudo apt update && sudo apt install -y python3-venv

# 2) Запустите установку + автозапуск (создаст venv, проверит PyPI, поставит пакеты,
#    запустит сервер и покажет все логи в этом же терминале)
bash scripts/install_and_run_local.sh
```
Что делает скрипт:
- создаёт/активирует `.venv` и ставит зависимости через `scripts/setup_local.sh`;
- проверяет окружение (`check_system.py`);
- запускает FastAPI/uvicorn в **этом** терминале, оставляя все логи и статус здесь (Ctrl+C — остановка).

codex/analyze-project-readiness-and-setup-g70f2j
> Если при запуске вместо логов появляется большая справка `curl` (строки про `--basic/--ntlm/...`), команда была исполнена через
> `curl ... | bash` или скопирована не полностью. Откройте терминал в корне репозитория и выполните напрямую: `bash
> scripts/install_and_run_local.sh`.

=======
main
Если хотите раздельно: сначала поставить зависимости, потом запускать вручную — используйте прежний короткий путь:
```bash
bash scripts/setup_local.sh
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Если скрипт пишет, что не может достучаться до PyPI:
- Проверьте, нужны ли вам прокси-переменные `http_proxy`/`https_proxy` (или наоборот — удалите их `unset http_proxy https_proxy`).
- Если у вас корпоративное зеркало PyPI, задайте его: `export PIP_INDEX_URL=https://<ваш-миррор>/simple` и повторите запуск скрипта.
- Скрипт прекращает работу при недоступности индекса, чтобы вы сразу увидели сетевую проблему, а не падение `pip install` в конце.

> Если видите предупреждение про *externally-managed-environment*, значит вы не в активированном `.venv`. Выполните `source .venv/bin/activate` и повторите `pip install -r requirements.txt` или `bash scripts/install_and_run_local.sh`.
codex/analyze-project-readiness-and-setup-g70f2j
=======
HEAD
=======
=======
## 7. Альтернативный запуск без Docker
Только если Docker недоступен:
```bash
# 1) Установите модуль для виртуальных окружений (иначе получите ошибку
#    "externally-managed-environment" при pip install)
sudo apt update && sudo apt install -y python3-venv

# 2) Создайте и активируйте окружение рядом с проектом
python3 -m venv .venv
source .venv/bin/activate

# 3) Установите зависимости и запустите сервер
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
> Если всё же видите предупреждение про *externally-managed-environment*, значит вы не в активированном `.venv`. Выполните `source .venv/bin/activate` и повторите `pip install -r requirements.txt`.
 main
origin/main
main

## 8. Частые проблемы
- **Нет доступа к таблицам** — проверьте, что сервисный аккаунт добавлен в Google Sheets с правами Editor.
- **FFmpeg not found** — установите FFmpeg (`sudo apt install ffmpeg`).
- **OPENAI_API_KEY пустой** — без ключа запросы к модели не будут работать.
- **Permission denied к `/var/run/docker.sock`** — либо не запущен Docker, либо нет прав на сокет. Исправление:
  - запустите демон: `sudo systemctl start docker` (или `sudo service docker start` на старых системах);
  - добавьте пользователя в группу docker и **перезайдите в терминал/сессию**: `sudo usermod -aG docker "$USER"`;
  - для единичного запуска можно выполнить команду с sudo: `sudo docker compose up --build`.
codex/analyze-project-readiness-and-setup-g70f2j
=======
HEAD
 main
- **Конфликты после `git pull`** — сделайте копию `.env` и `credentials/`, затем либо сбросьте репозиторий к последней версии (`git fetch origin && git reset --hard origin/main && git clean -fd`), либо вручную разрешите конфликт в файлах, удалив маркеры `<<<<<<<`/`=======`/`>>>>>>>` и зафиксировав правку `git add . && git commit -m "Resolve merge conflicts"`.
- **`pip install` не может скачать пакеты (PyPI недоступен)** — запустите `./scripts/setup_local.sh`, он проверит доступ к индексу и подскажет: добавить прокси-переменные или, наоборот, убрать их. При наличии корпоративного зеркала задайте `PIP_INDEX_URL=https://<mirror>/simple`.
- **AttributeError: platform.freedesktop_os_release / pip падает на старом Python** — вы запускаете скрипты через Python < 3.11, который не поддерживает новую версию pip. Решение: `sudo apt install -y python3.11 python3.11-venv`, затем запустите скрипт так: `PYTHON=python3.11 bash scripts/install_and_run_local.sh` (или `scripts/setup_local.sh`) и удалите старое окружение `.venv`, если оно было создано другой версией Python.
- **Сборка dlib падает при `pip install -r requirements.txt`** (вручную, без Docker) — установите системные библиотеки и повторите (на свежих Debian/Ubuntu используйте `libblas-dev` вместо устаревшего `libatlas-base-dev`):
codex/analyze-project-readiness-and-setup-g70f2j
=======
=======
codex/analyze-project-readiness-and-setup-ilokil
- **Конфликты после `git pull`** — сделайте копию `.env` и `credentials/`, затем либо сбросьте репозиторий к последней версии (`git fetch origin && git reset --hard origin/main && git clean -fd`), либо вручную разрешите конфликт в файлах, удалив маркеры `<<<<<<<`/`=======`/`>>>>>>>` и зафиксировав правку `git add . && git commit -m "Resolve merge conflicts"`.
- **`pip install` не может скачать пакеты (PyPI недоступен)** — запустите `./scripts/setup_local.sh`, он проверит доступ к индексу и подскажет: добавить прокси-переменные или, наоборот, убрать их. При наличии корпоративного зеркала задайте `PIP_INDEX_URL=https://<mirror>/simple`.
- **Сборка dlib падает при `pip install -r requirements.txt`** (вручную, без Docker) — установите системные библиотеки и повторите (на свежих Debian/Ubuntu используйте `libblas-dev` вместо устаревшего `libatlas-base-dev`):

- **Сборка dlib падает при `pip install -r requirements.txt`** (вручную, без Docker) — установите системные библиотеки и повторите:
 main
origin/main
main
  ```bash
  sudo apt update
  sudo apt install -y \
    cmake \
    libopenblas-dev \
    liblapack-dev \
codex/analyze-project-readiness-and-setup-g70f2j
    libblas-dev \
=======
HEAD
    libblas-dev \
=======
 codex/analyze-project-readiness-and-setup-ilokil
    libblas-dev \
=======
    libatlas-base-dev \
 main
origin/main
main
    libboost-all-dev \
    gfortran \
    pkg-config \
    libx11-dev \
    libgtk-3-dev \
    libgl1-mesa-dev
  pip install -r requirements.txt
  ```
- **externally-managed-environment при `pip install`** — вы ставите пакеты в системный Python. Решение: `sudo apt install -y python3-venv`, затем `python3 -m venv .venv && source .venv/bin/activate` и повторите `pip install -r requirements.txt`.
