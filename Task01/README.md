# Task01

## Структура файлов

- `ratings.csv` — оценки пользователей. Колонки: `userId`, `movieId`, `rating`, `timestamp`.
- `movies.csv`  — информация о фильмах. Колонки: `movieId`, `title`, `genres`.
- `tags.csv`    — теги пользователей. Колонки: `userId`, `movieId`, `tag`, `timestamp`.
- `links.csv`   — ссылки на IMDb и TMDb. Колонки: `movieId`, `imdbId`, `tmdbId`.

## Файлы, созданные в рамках задания

- `ratings_count.txt` — минимальный и максимальный `userId` из `ratings.csv`
  и количество строк с этими идентификаторами.
- `sqlite.txt` — версия установленного SQLite и список режимов вывода утилиты `sqlite3`.

## Как воспроизвести

1. Положить файлы `ratings.csv`, `movies.csv`, `tags.csv`, `links.csv` в папку `Task01`.
2. Скомпилировать программу: