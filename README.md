# hillel_hw_10 — Django: книгарня

Навчальний Django-проєкт (Hillel, ДЗ №10): каталог книг із категоріями,
налаштована адмінка та management-команди для наповнення бази й статистики
через Django ORM (`filter`, `Q`, `annotate`, `aggregate`).

## Стек

- Python 3, Django 6.1
- SQLite
- python-dotenv — налаштування з `.env`

## Структура

```
config/                 # налаштування проєкту (settings, urls, wsgi/asgi)
books/
├── models.py           # Category, Book, BookCategory
├── admin.py            # адмінка: inlines, фільтри, пошук
└── management/commands/
    ├── seed_books.py   # тестові дані
    └── book_stats.py   # статистика через ORM
```

## Моделі

| Модель | Поля | Примітки |
|---|---|---|
| `Category` | `name`, `slug` | обидва унікальні |
| `Book` | `title`, `author`, `price`, `description`, `stock`, `categories`, `created_at`, `updated_at` | `price ≥ 0`, M2M до категорій через `BookCategory` |
| `BookCategory` | `book`, `category` | проміжна модель; `on_delete=PROTECT` не дає видалити категорію, у якій є книги; пара `book + category` унікальна |

## Адмінка

- **Книги:** колонки з категоріями та ознакою наявності, редагування ціни й
  кількості прямо у списку, фільтр за наявністю (є / мало ≤ 5 / немає),
  фільтр за категоріями й датою, пошук за назвою, автором, описом і категорією,
  `date_hierarchy`, `fieldsets`, inline для категорій.
- **Категорії:** кількість книг (із сортуванням), автозаповнення `slug`,
  inline зі списком книг.
- Запити оптимізовано через `select_related` / `prefetch_related` та `annotate`.

## Встановлення та запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# згенерувати SECRET_KEY і вставити в .env:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

python manage.py migrate
python manage.py createsuperuser
python manage.py seed_books
python manage.py runserver
```

Адмінка: http://127.0.0.1:8000/admin/

### Змінні оточення (`.env`)

| Змінна | Опис | Приклад |
|---|---|---|
| `DJANGO_SECRET_KEY` | секретний ключ (обов'язковий) | `change-me` |
| `DJANGO_DEBUG` | режим налагодження | `True` |
| `DJANGO_ALLOWED_HOSTS` | хости через кому | `127.0.0.1,localhost` |

## Management-команди

### `seed_books`

Створює 5 категорій і набір книг. Команду можна запускати повторно — дублікати
не створюються.

```bash
python manage.py seed_books
```

### `book_stats`

Виводить статистику книгарні та демонструє можливості ORM:

1. **filter** — у наявності й дешевші за задану ціну, мало на складі, немає на складі,
   книги певної категорії, книги без категорії;
2. **Q-об'єкти** — пошук за назвою / автором / категорією (OR), «у наявності, але не
   в категорії» (AND + NOT), складна умова для акції;
3. **annotate** — статистика по категоріях, топ-5 книг за вартістю запасу
   (`F("price") * F("stock")`), категорії з понад 2 книгами (HAVING);
4. **aggregate** — підсумок по всьому магазину.

```bash
python manage.py book_stats
python manage.py book_stats --max-price 200 --search Кінг --category fentezi
python manage.py book_stats --sql   # також показати згенерований SQL
```

| Параметр | За замовчуванням | Опис |
|---|---|---|
| `--max-price` | `300` | максимальна ціна для фільтра |
| `--search` | `Кінг` | рядок пошуку для Q-запиту |
| `--category` | `fentezi` | slug категорії |
| `--sql` | — | друкувати SQL кожного запиту |

> На SQLite `icontains` ігнорує регістр лише для латиниці, тому «кінг» не знайде «Кінг».
