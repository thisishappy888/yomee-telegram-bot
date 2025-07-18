### **Yomee Telegram Bot**


#### 📦 Используемые технологии

- **Python 3**
- **Aiogram** — асинхронный фреймворк для Telegram-ботов
- **SQLite** — простая встроенная база данных
- **Scikit-learn** — для TF-IDF и cosine similarity

---

### 💡 Возможности бота

- Создание и редактирование анкеты
- Лайки / дизлайки анкет
- Подбор подходящих анкет на основе описания
- Диалог через Telegram
- Простая локальная база данных

---

#### 🔍 Как работает система рекомендаций

- При поиске пары бот анализирует поле `about` текущего пользователя
- Все описания преобразуются в векторы с помощью `TfidfVectorizer`
- Затем вычисляется косинусное сходство между текущим пользователем и другими
- Самое похожее описание (если его оценка сходства ≥ 0.1) возвращается в качестве совпадения
- Если анкет с похожим описанием (если его оценка сходства < 0.1) возвращается случайная анкета

> Это позволяет находить людей с похожими интересами и стилем общения, даже если они не указывали явные предпочтения

---

#### 🔧 Установка

1. Склонируйте репозиторий:
 ```bash
   git clone https://github.com/thisishappy888/yomee-telegram-bot.git
   cd yomee-telegram-bot
 ```

2. Создайте виртуальное окружение и активируйте его:
```bash
    python3 -m venv venv
    source venv/bin/activate
   ```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте .env или файл конфигураций, заполните следующие параметры:
```env
BOT_TOKEN = ВАШ ТОКЕН TELEGRAM БОТА
```

5. Запуск
```bash
python bot.py
```

   
