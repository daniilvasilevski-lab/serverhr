# 📚 ПОЛНАЯ ИНСТРУКЦИЯ ПО УСТАНОВКЕ
## Для тех, кто впервые работает с Linux

Эта инструкция написана максимально просто и подробно. Следуйте шаг за шагом.

---

## 🎯 ЧТО МЫ БУДЕМ ДЕЛАТЬ

1. Установим все необходимые программы
2. Скачаем проект
3. Настроим Google Sheets
4. Настроим OpenAI
5. Запустим систему
6. Проверим что все работает

**Время установки:** 30-40 минут

---

## 📋 ЧТО ВАМ ПОНАДОБИТСЯ

- ✅ Компьютер с Linux (Ubuntu, Debian, или другой дистрибутив)
- ✅ Интернет соединение
- ✅ Google аккаунт (для Google Sheets)
- ✅ OpenAI аккаунт с API ключом (мы покажем как получить)

---

# ЧАСТЬ 1: УСТАНОВКА ПРОГРАММ

## Шаг 1: Открываем терминал

**Терминал** - это черное окно где мы пишем команды.

**Как открыть:**
- **Ubuntu/Debian:** Нажмите `Ctrl + Alt + T`
- Или найдите в меню приложений "Terminal" / "Терминал"

Вы увидите что-то вроде:
```
username@computer:~$
```

---

## Шаг 2: Обновляем систему

**Что это значит:** Проверяем, что все программы в системе актуальные.

**Скопируйте и вставьте эту команду в терминал:**
```bash
sudo apt update && sudo apt upgrade -y
```

**Что происходит:**
- `sudo` = запускаем команду от имени администратора
- Может попросить пароль - введите пароль вашего пользователя
- Процесс может занять 5-10 минут

✅ **Готово, когда** увидите снова `username@computer:~$`

---

## Шаг 3: Устанавливаем Docker

**Docker** - программа для запуска нашего проекта в изолированном контейнере.

### 3.1. Установка Docker

```bash
# Устанавливаем необходимые пакеты
sudo apt install -y ca-certificates curl gnupg lsb-release

# Добавляем официальный репозиторий Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Устанавливаем Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

### 3.2. Проверяем что Docker установлен

```bash
docker --version
```

Вы должны увидеть что-то вроде:
```
Docker version 24.0.7, build afdd53b
```

### 3.3. Добавляем себя в группу docker

**Зачем:** Чтобы не писать `sudo` перед каждой командой docker.

```bash
sudo usermod -aG docker $USER
```

**ВАЖНО:** После этой команды нужно **выйти из системы и войти заново** или перезагрузить компьютер.

---

## Шаг 4: Устанавливаем Docker Compose

```bash
# Docker Compose обычно устанавливается вместе с Docker
docker compose version
```

Должны увидеть:
```
Docker Compose version v2.23.0
```

Если не установлен, установите:
```bash
sudo apt install docker-compose-plugin -y
```

---

## Шаг 5: Устанавливаем Git

**Git** - программа для скачивания кода с GitHub.

```bash
sudo apt install git -y
```

Проверяем:
```bash
git --version
```

Должны увидеть: `git version 2.x.x`

---

# ЧАСТЬ 2: СКАЧИВАЕМ ПРОЕКТ

## Шаг 6: Создаем папку для проектов

```bash
# Переходим в домашнюю папку
cd ~

# Создаем папку projects (можете назвать по-другому)
mkdir projects

# Переходим в эту папку
cd projects
```

**Где я сейчас:**
```bash
pwd
```
Увидите что-то вроде: `/home/username/projects`

---

## Шаг 7: Скачиваем проект

```bash
git clone https://github.com/daniilvasilevski-lab/serverhr.git
```

**Что происходит:**
- Скачивается весь код проекта
- Занимает 1-2 минуты

---

## Шаг 8: Переходим в папку проекта

```bash
cd serverhr/python-interview-analyzer
```

**Проверяем что мы в правильной папке:**
```bash
ls
```

Вы должны увидеть файлы проекта:
```
app/  docker-compose.yaml  Dockerfile  prompts.yaml  requirements.txt  ...
```

✅ **Отлично!** Проект скачан.

---

# ЧАСТЬ 3: НАСТРОЙКА GOOGLE SHEETS

Это самая важная часть! Следуйте внимательно.

## Шаг 9: Создаем Google Service Account

### 9.1. Переходим в Google Cloud Console

1. Откройте браузер
2. Перейдите на: https://console.cloud.google.com/
3. Войдите в свой Google аккаунт

### 9.2. Создаем новый проект

1. Нажмите на название проекта вверху (рядом с "Google Cloud")
2. Нажмите **"NEW PROJECT"** (Создать проект)
3. Название проекта: `interview-analyzer` (или любое другое)
4. Нажмите **"CREATE"** (Создать)
5. Подождите 10-20 секунд пока проект создается
6. Выберите этот проект в списке

### 9.3. Включаем Google Sheets API

1. В меню слева найдите **"APIs & Services"** (API и сервисы)
2. Нажмите **"Enable APIs and Services"** (Включить API и сервисы)
3. В поиске введите: `Google Sheets API`
4. Нажмите на **Google Sheets API**
5. Нажмите **"ENABLE"** (Включить)
6. Подождите пока включится

### 9.4. Включаем Google Drive API

Повторяем то же самое для Google Drive API:
1. Снова нажмите **"Enable APIs and Services"**
2. Ищем: `Google Drive API`
3. Нажимаем на **Google Drive API**
4. Нажимаем **"ENABLE"**

### 9.5. Создаем Service Account

1. В меню слева: **"IAM & Admin"** → **"Service Accounts"**
2. Нажмите **"CREATE SERVICE ACCOUNT"** (Создать сервисный аккаунт)
3. Заполняем:
   - **Service account name:** `interview-analyzer-service`
   - **Service account ID:** (заполнится автоматически)
   - **Description:** `Service account for interview analysis system`
4. Нажмите **"CREATE AND CONTINUE"** (Создать и продолжить)
5. **Grant this service account access to project:**
   - Роль: Выберите **"Editor"** (Редактор)
   - Нажмите **"CONTINUE"** (Продолжить)
6. Нажмите **"DONE"** (Готово)

### 9.6. Создаем JSON ключ

1. Найдите ваш Service Account в списке (email вроде `interview-analyzer-service@...`)
2. Нажмите на три точки справа → **"Manage keys"** (Управление ключами)
3. Нажмите **"ADD KEY"** → **"Create new key"** (Добавить ключ → Создать новый)
4. Выберите тип: **JSON**
5. Нажмите **"CREATE"** (Создать)

📥 **ВАЖНО:** Файл `service-account-xxxxxx.json` автоматически скачается на ваш компьютер!

**Запомните где он сохранился!** Обычно в папке "Загрузки" / "Downloads".

---

## Шаг 10: Создаем Google Таблицы

### 10.1. Создаем ВХОДНУЮ таблицу (где будут кандидаты)

1. Перейдите на: https://sheets.google.com/
2. Нажмите **"+"** (Создать новую таблицу)
3. Назовите таблицу: **"Interview Candidates"**

### 10.2. Создаем заголовки (первая строка)

Скопируйте эти заголовки **В ТОЧНОСТИ** в первую строку таблицы:

| A | B | C | D | E | F | G | H | I | J | K | L |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ID | Name | Email | Phone | Preferences | CV_gcs | video_gcs | CV_URL | Video_URL | created_at | Questions_URL | Processed |

**Как это сделать:**
- В ячейку A1 напишите: `ID`
- В ячейку B1 напишите: `Name`
- В ячейку C1 напишите: `Email`
- И так далее до колонки L1: `Processed`

### 10.3. Добавляем тестовые данные (необязательно)

Во вторую строку можете добавить тестового кандидата:

| A | B | C | D | E | I | L |
|---|---|---|---|---|---|---|
| CAND-001 | Тест Тестов | test@example.com | +79991234567 | Python Developer | https://example.com/video.mp4 | 0 |

**Важные колонки:**
- **I (Video_URL):** Обязательно! URL видео интервью
- **L (Processed):** Поставьте `0` (ноль) - значит не обработано

### 10.4. Копируем URL входной таблицы

1. Скопируйте URL из адресной строки браузера
2. Выглядит так: `https://docs.google.com/spreadsheets/d/ДЛИННЫЙ_ID/edit`
3. **СОХРАНИТЕ ЕГО!** Понадобится позже.

---

### 10.5. Создаем ВЫХОДНУЮ таблицу (куда будут результаты)

1. Создайте еще одну новую таблицу
2. Назовите: **"Interview Results"**

### 10.6. Создаем заголовки для результатов

Скопируйте эти заголовки в первую строку:

| A | B | C | D | E | F | G | H | I | J | K | L | M | N | O |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ID | Name | Email | Phone | Language | Communication | Motivation | Technical | Analytical | Creative | Teamwork | Stress_Resistance | Adaptability | Overall_Score | Recommendation |

### 10.7. Копируем URL выходной таблицы

1. Скопируйте URL этой таблицы тоже
2. **СОХРАНИТЕ ЕГО!**

---

## Шаг 11: Даем доступ Service Account к таблицам

**ЭТО ОЧЕНЬ ВАЖНО!** Без этого система не сможет читать/писать в таблицы.

### 11.1. Находим email Service Account

1. Откройте скачанный файл `service-account-xxxxxx.json` текстовым редактором
2. Найдите строку `"client_email"`
3. Скопируйте email (выглядит так: `interview-analyzer-service@project-id.iam.gserviceaccount.com`)

### 11.2. Даем доступ к ВХОДНОЙ таблице

1. Откройте входную таблицу **"Interview Candidates"**
2. Нажмите кнопку **"Share"** (Поделиться) справа вверху
3. Вставьте email Service Account
4. Права доступа: **Editor** (Редактор)
5. **ВАЖНО:** Снимите галочку **"Notify people"** (Уведомить людей)
6. Нажмите **"Share"** (Поделиться)

### 11.3. Даем доступ к ВЫХОДНОЙ таблице

Повторите то же самое для таблицы **"Interview Results"**:
1. Откройте таблицу результатов
2. **"Share"** → вставьте тот же email
3. Права: **Editor**
4. Снимите галочку уведомлений
5. **"Share"**

✅ **Готово!** Теперь система сможет работать с таблицами.

---

# ЧАСТЬ 4: ПОЛУЧАЕМ OPENAI API КЛЮЧ

## Шаг 12: Создаем OpenAI аккаунт и получаем API ключ

### 12.1. Регистрация

1. Перейдите на: https://platform.openai.com/
2. Нажмите **"Sign up"** если у вас нет аккаунта
3. Или **"Log in"** если аккаунт уже есть

### 12.2. Пополняем баланс

**ВАЖНО:** OpenAI API платный. Нужно пополнить баланс минимум на $5-10.

1. Перейдите в: **"Settings"** → **"Billing"**
2. Нажмите **"Add payment method"**
3. Добавьте карту и пополните баланс

**Примерная стоимость:**
- Анализ 1 интервью (10 минут видео): ~$0.50-1.00
- С $10 можно проанализировать ~10-20 интервью

### 12.3. Создаем API ключ

1. Перейдите на: https://platform.openai.com/api-keys
2. Нажмите **"Create new secret key"** (Создать новый секретный ключ)
3. Имя ключа: `interview-analyzer`
4. Нажмите **"Create secret key"**

📋 **КОПИРУЙТЕ КЛЮЧ НЕМЕДЛЕННО!**

Ключ выглядит так: `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**⚠️ ВНИМАНИЕ:** Ключ показывается только один раз! Если не скопировали - придется создавать новый.

**СОХРАНИТЕ ЕГО В БЕЗОПАСНОМ МЕСТЕ!**

---

# ЧАСТЬ 5: НАСТРОЙКА ПРОЕКТА

## Шаг 13: Копируем Service Account JSON в проект

Возвращаемся в терминал.

### 13.1. Проверяем где мы находимся

```bash
pwd
```

Должно показать: `/home/username/projects/serverhr/python-interview-analyzer`

Если нет, выполните:
```bash
cd ~/projects/serverhr/python-interview-analyzer
```

### 13.2. Создаем папку credentials

```bash
mkdir -p credentials
```

### 13.3. Копируем JSON файл

**Вариант 1: Если файл в Downloads**

```bash
cp ~/Downloads/service-account-*.json credentials/service-account.json
```

**Вариант 2: Если в другом месте**

Сначала найдите файл:
```bash
find ~ -name "service-account-*.json" -type f 2>/dev/null
```

Скопируйте путь который покажется, затем:
```bash
cp /полный/путь/к/файлу/service-account-xxxxx.json credentials/service-account.json
```

### 13.4. Проверяем что файл скопировался

```bash
ls -la credentials/
```

Должны увидеть файл `service-account.json`

---

## Шаг 14: Создаем .env файл

`.env` файл содержит все настройки проекта.

### 14.1. Копируем шаблон

```bash
cp .env.production.example .env
```

### 14.2. Открываем файл для редактирования

```bash
nano .env
```

**Что такое nano:** Это простой текстовый редактор в терминале.

### 14.3. Редактируем файл

Вы увидите много строк с настройками. Нужно изменить только эти:

**1. OpenAI API ключ (строка ~19):**

Найдите строку:
```env
OPENAI_API_KEY=sk-your-real-openai-api-key-here
```

Измените на (вставьте свой ключ):
```env
OPENAI_API_KEY=sk-proj-ваш-настоящий-ключ-здесь
```

**2. URL входной таблицы (строка ~27):**

Найдите:
```env
SOURCE_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_SOURCE_SHEET_ID_HERE/edit
```

Измените на (вставьте URL вашей входной таблицы):
```env
SOURCE_SHEET_URL=https://docs.google.com/spreadsheets/d/ваш_id_входной_таблицы/edit
```

**3. URL выходной таблицы (строка ~30):**

Найдите:
```env
RESULTS_SHEET_URL=https://docs.google.com/spreadsheets/d/YOUR_RESULTS_SHEET_ID_HERE/edit
```

Измените на (вставьте URL вашей выходной таблицы):
```env
RESULTS_SHEET_URL=https://docs.google.com/spreadsheets/d/ваш_id_выходной_таблицы/edit
```

### 14.4. Сохраняем файл

1. Нажмите `Ctrl + X` (выход)
2. Нажмите `Y` (да, сохранить)
3. Нажмите `Enter` (подтвердить имя файла)

### 14.5. Проверяем что сохранилось

```bash
cat .env | grep -E "OPENAI_API_KEY|SOURCE_SHEET_URL|RESULTS_SHEET_URL"
```

Должны увидеть ваши настройки (без sk-proj... в полном виде из соображений безопасности).

---

# ЧАСТЬ 6: ЗАПУСК СИСТЕМЫ

## Шаг 15: Запускаем Docker контейнеры

### 15.1. Первый запуск (с загрузкой образов)

**ВНИМАНИЕ:** Первый запуск занимает 10-15 минут, т.к. скачиваются все необходимые компоненты.

```bash
docker compose up --build
```

**Что происходит:**
- Скачиваются базовые образы (Python, Redis, и т.д.)
- Устанавливаются все Python библиотеки
- Запускается система

**Вы увидите много текста** - это нормально!

### 15.2. Что вы должны увидеть

После нескольких минут увидите:

```
================================================================================
🚀 ЗАПУСК INTERVIEW ANALYZER v2.0
================================================================================
📋 Конфигурация:
   • Среда: PRODUCTION
   • Порт: 8000
   ...

🔧 Инициализация сервисов...
   [1/6] OpenAI клиент... ✅ OpenAI клиент готов
   [2/6] Интегрированный анализатор... ✅ Анализатор готов
   ...
   [5/6] Google Sheets сервис...
         ✅ Google Sheets connection established
         ✅ Connected to source sheet: Interview Candidates
         ✅ Connected to results sheet: Interview Results

✅ ВСЕ СЕРВИСЫ ИНИЦИАЛИЗИРОВАНЫ УСПЕШНО!
🌐 Сервер доступен: http://0.0.0.0:8000
⏳ Ожидание запросов...
```

✅ **Если вы видите это - ВСЕ РАБОТАЕТ!**

---

## Шаг 16: Проверяем что система работает

### 16.1. Открываем второй терминал

Оставьте первый терминал открытым (там работает сервер).

Откройте **новый терминал** (Ctrl + Alt + T).

### 16.2. Проверяем health

```bash
curl http://localhost:8000/health
```

Должны увидеть:
```json
{"success":true,"status":"healthy","services_status":{...}}
```

### 16.3. Открываем документацию API в браузере

Откройте браузер и перейдите на:
```
http://localhost:8000/docs
```

Вы увидите интерактивную документацию API (Swagger UI).

---

# ЧАСТЬ 7: ТЕСТОВЫЙ ЗАПУСК

## Шаг 17: Добавляем тестовое интервью

### 17.1. Открываем входную таблицу

Откройте вашу таблицу **"Interview Candidates"** в браузере.

### 17.2. Добавляем тестовую запись

Если у вас еще нет записей, добавьте в строку 2:

| A | B | C | D | E | I | L |
|---|---|---|---|---|---|---|
| CAND-TEST | Тест Иванов | test@example.com | +79991234567 | Python Developer | https://www.youtube.com/watch?v=dQw4w9WgXcQ | 0 |

**ВАЖНО:**
- Колонка **I (Video_URL)**: Можете использовать любой публичный URL видео
- Колонка **L (Processed)**: Ставим `0` (ноль)

---

## Шаг 18: Запускаем обработку

### 18.1. Вариант A: Автоматическая обработка

Если в .env у вас `ENABLE_AUTO_PROCESSING=true` (по умолчанию), то:
- Просто подождите 5 минут
- Система автоматически обработает

### 18.2. Вариант B: Ручной запуск

Если хотите запустить сразу, во втором терминале выполните:

```bash
curl -X POST http://localhost:8000/api/v1/sheets/process-all
```

### 18.3. Смотрим логи в первом терминале

Переключитесь на первый терминал (где запущен сервер).

Вы увидите процесс обработки:

```
================================================================================
🎯 НАЧАЛО ОБРАБОТКИ КАНДИДАТА #1/1
👤 Имя: Тест Иванов
🆔 ID: CAND-TEST
📧 Email: test@example.com
================================================================================
⏳ Запуск анализа интервью для Тест Иванов...

🔬 НАЧАЛО ИНТЕГРИРОВАННОГО АНАЛИЗА для Тест Иванов
📋 Этап 1/4: Подготовка контекста интервью...
...
📊 Этап 3/4: Детальная оценка по 10 критериям...
   📌 Критерий 1/10: Коммуникативные навыки... ✓ Оценка: 8/10
   📌 Критерий 2/10: Мотивация к обучению... ✓ Оценка: 7/10
   ...
✅ АНАЛИЗ ЗАВЕРШЕН для Тест Иванов

📊 Итоговая оценка: 75/100
💡 Рекомендация: Рекомендуется к найму
🎉 УСПЕШНО ОБРАБОТАН: Тест Иванов (1/1)
```

---

## Шаг 19: Проверяем результаты

### 19.1. Открываем выходную таблицу

Откройте таблицу **"Interview Results"** в браузере.

### 19.2. Проверяем результат

Вы должны увидеть новую строку с результатами:

| A | B | C | F | G | H | N | O |
|---|---|---|---|---|---|---|---|
| CAND-TEST | Тест Иванов | test@example.com | 8/10 - Отличные... | 7/10 - Хорошая... | 6/10 - Базовый... | 75 | Рекомендуется к найму |

### 19.3. Проверяем входную таблицу

В таблице **"Interview Candidates"** в колонке **L (Processed)** должна стоять `1` (обработано).

---

# 🎉 ПОЗДРАВЛЯЕМ! СИСТЕМА РАБОТАЕТ!

---

# ЧАСТЬ 8: ЕЖЕДНЕВНОЕ ИСПОЛЬЗОВАНИЕ

## Как запускать систему каждый день

### Запуск

```bash
cd ~/projects/serverhr/python-interview-analyzer
docker compose up
```

### Остановка

В терминале где запущен сервер нажмите: `Ctrl + C`

Затем:
```bash
docker compose down
```

### Запуск в фоновом режиме

Если хотите чтобы система работала в фоне:

```bash
docker compose up -d
```

Проверить статус:
```bash
docker compose ps
```

Посмотреть логи:
```bash
docker compose logs -f app
```

Остановить:
```bash
docker compose down
```

---

# 🔧 РЕШЕНИЕ ПРОБЛЕМ

## Проблема 1: "Permission denied" при запуске Docker

**Решение:**
```bash
sudo usermod -aG docker $USER
```

Затем **выйдите из системы и войдите заново** или выполните:
```bash
newgrp docker
```

---

## Проблема 2: "Google Sheets not configured"

**Причина:** Service account не имеет доступа к таблицам.

**Решение:**
1. Откройте файл `credentials/service-account.json`
2. Найдите `client_email`
3. Скопируйте email
4. Откройте обе таблицы Google Sheets
5. Нажмите "Share" и добавьте этот email с правами **Editor**

---

## Проблема 3: "OpenAI API error"

**Причина:** Неправильный API ключ или нет денег на балансе.

**Решение:**
1. Проверьте баланс на: https://platform.openai.com/account/billing
2. Проверьте что в `.env` правильный ключ:
   ```bash
   cat .env | grep OPENAI_API_KEY
   ```
3. Ключ должен начинаться с `sk-proj-` или `sk-`

---

## Проблема 4: Порт 8000 занят

**Решение:**

Измените порт в `.env`:
```bash
nano .env
```

Найдите строку `PORT=8000` и измените на другой порт, например:
```env
PORT=8001
```

Сохраните и перезапустите:
```bash
docker compose down
docker compose up
```

---

## Проблема 5: Docker образ не собирается

**Решение:**

Очистите кеш Docker:
```bash
docker system prune -a
```

Затем соберите заново:
```bash
docker compose up --build
```

---

# 📚 ПОЛЕЗНЫЕ КОМАНДЫ

## Просмотр логов

```bash
# Все логи
docker compose logs

# Только приложение
docker compose logs app

# В реальном времени
docker compose logs -f app

# Последние 100 строк
docker compose logs --tail=100 app
```

## Проверка статуса

```bash
# Статус контейнеров
docker compose ps

# Использование ресурсов
docker stats

# Проверка здоровья API
curl http://localhost:8000/health
```

## Перезапуск

```bash
# Перезапуск всех сервисов
docker compose restart

# Перезапуск только приложения
docker compose restart app
```

---

# 🆘 НУЖНА ПОМОЩЬ?

## Где искать помощь

1. **Логи:** Всегда смотрите логи первым делом
   ```bash
   docker compose logs -f app
   ```

2. **Документация API:** http://localhost:8000/docs

3. **Health check:** http://localhost:8000/health

4. **Проверка настроек:**
   ```bash
   cat .env
   ls -la credentials/
   ```

---

# ✅ ЧЕКЛИСТ: ВСЕ ЛИ НАСТРОЕНО?

Перед первым запуском проверьте:

- [ ] Docker установлен и работает (`docker --version`)
- [ ] Docker Compose установлен (`docker compose version`)
- [ ] Git установлен (`git --version`)
- [ ] Проект скачан (`cd ~/projects/serverhr/python-interview-analyzer`)
- [ ] Google Service Account создан
- [ ] JSON ключ скачан и скопирован в `credentials/service-account.json`
- [ ] Две Google таблицы созданы (входная и выходная)
- [ ] Service Account имеет доступ **Editor** к обеим таблицам
- [ ] OpenAI API ключ получен
- [ ] OpenAI баланс пополнен (минимум $5)
- [ ] Файл `.env` создан и настроен
- [ ] В `.env` указаны: `OPENAI_API_KEY`, `SOURCE_SHEET_URL`, `RESULTS_SHEET_URL`
- [ ] Сервер запускается без ошибок (`docker compose up`)
- [ ] Health check возвращает success (`curl http://localhost:8000/health`)

---

# 🎯 ИТОГО

Теперь у вас есть полностью работающая система анализа интервью!

**Что она делает:**
- ✅ Автоматически сканирует Google Sheets каждые 5 минут
- ✅ Обрабатывает новые интервью (где Processed = 0)
- ✅ Анализирует видео, аудио, эмоции, речь
- ✅ Оценивает по 10 критериям через GPT-4
- ✅ Записывает результаты в выходную таблицу
- ✅ Отмечает обработанные интервью (Processed = 1)
- ✅ Показывает весь процесс в терминале в реальном времени

**Поздравляем!** 🎉

---

**Авторы:** Interview Analyzer Team
**Версия:** 2.0
**Дата:** 2025-10-24
