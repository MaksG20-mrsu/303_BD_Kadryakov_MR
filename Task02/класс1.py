#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ETL Utility for Task02.
Reads raw dataset files and generates db_init.sql for SQLite database creation.
"""

import os
import re
import csv

# Определение путей к каталогам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, '..', 'dataset')
OUTPUT_SQL = os.path.join(BASE_DIR, 'db_init.sql')

# Если папка dataset лежит прямо внутри Task02
if not os.path.exists(DATASET_DIR) and os.path.exists(os.path.join(BASE_DIR, 'dataset')):
    DATASET_DIR = os.path.join(BASE_DIR, 'dataset')


def escape_sql_string(value: str) -> str:
    """Экранирует одинарные кавычки для SQL-запросов."""
    if value is None:
        return 'NULL'
    clean_val = str(value).replace("'", "''")
    return f"'{clean_val}'"


def find_dataset_file(base_name: str) -> str:
    """Находит файл датасета с расширениями .csv, .txt, .dat или без расширения."""
    extensions = ['.csv', '.txt', '.dat', '']
    for ext in extensions:
        file_path = os.path.join(DATASET_DIR, f"{base_name}{ext}")
        if os.path.exists(file_path):
            return file_path
    raise FileNotFoundError(f"Файл для таблицы '{base_name}' не найден в {DATASET_DIR}")


def detect_delimiter(file_path: str) -> str:
    """Определяет разделитель в текстовом файле."""
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        first_line = f.readline()
        if '::' in first_line:
            return '::'
        elif ';' in first_line:
            return ';'
        elif '\t' in first_line:
            return '\t'
        elif '|' in first_line:
            return '|'
        return ','


def process_movies(sql_file):
    """Генерация DD/DML для таблицы movies."""
    file_path = find_dataset_file('movies')
    delimiter = detect_delimiter(file_path)

    sql_file.write("-- Table: movies\n")
    sql_file.write("DROP TABLE IF EXISTS movies;\n")
    sql_file.write("""CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    year INTEGER,
    genres TEXT
);\n\n""")

    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f, delimiter=delimiter)
        # Пропуск заголовка, если он присутствует
        first_row = next(reader, None)
        if first_row and not first_row[0].isdigit():
            pass  # Header skipped
        elif first_row:
            rows = [first_row] + list(reader)
            reader = rows

        for row in reader:
            if not row or len(row) < 2:
                continue
            movie_id = row[0].strip()
            title = row[1].strip()
            
            # Извлечение года выпуска из названия или из отдельной колонки (если есть)
            year = 'NULL'
            year_match = re.search(r'\((\d{4})\)', title)
            if year_match:
                year = year_match.group(1)
            elif len(row) >= 4 and row[2].strip().isdigit():
                year = row[2].strip()

            genres = row[-1].strip() if len(row) >= 3 else ''
            
            sql_file.write(
                f"INSERT INTO movies (id, title, year, genres) VALUES ("
                f"{movie_id}, {escape_sql_string(title)}, {year}, {escape_sql_string(genres)});\n"
            )
    sql_file.write("\n")


def process_ratings(sql_file):
    """Генерация DD/DML для таблицы ratings."""
    file_path = find_dataset_file('ratings')
    delimiter = detect_delimiter(file_path)

    sql_file.write("-- Table: ratings\n")
    sql_file.write("DROP TABLE IF EXISTS ratings;\n")
    sql_file.write("""CREATE TABLE ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    rating REAL NOT NULL,
    timestamp INTEGER NOT NULL
);\n\n""")

    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f, delimiter=delimiter)
        first_row = next(reader, None)
        if first_row and not first_row[0].isdigit():
            pass
        elif first_row:
            reader = [first_row] + list(reader)

        for row in reader:
            if not row or len(row) < 4:
                continue
            # Обработка ситуаций, когда id присутствует или отсутствует в файле
            if len(row) >= 5 and row[0].strip().isdigit():
                r_id, user_id, movie_id, rating, ts = [x.strip() for x in row[:5]]
                sql_file.write(
                    f"INSERT INTO ratings (id, user_id, movie_id, rating, timestamp) VALUES ("
                    f"{r_id}, {user_id}, {movie_id}, {rating}, {ts});\n"
                )
            else:
                user_id, movie_id, rating, ts = [x.strip() for x in row[:4]]
                sql_file.write(
                    f"INSERT INTO ratings (user_id, movie_id, rating, timestamp) VALUES ("
                    f"{user_id}, {movie_id}, {rating}, {ts});\n"
                )
    sql_file.write("\n")


def process_tags(sql_file):
    """Генерация DD/DML для таблицы tags."""
    file_path = find_dataset_file('tags')
    delimiter = detect_delimiter(file_path)

    sql_file.write("-- Table: tags\n")
    sql_file.write("DROP TABLE IF EXISTS tags;\n")
    sql_file.write("""CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    timestamp INTEGER NOT NULL
);\n\n""")

    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f, delimiter=delimiter)
        first_row = next(reader, None)
        if first_row and not first_row[0].isdigit():
            pass
        elif first_row:
            reader = [first_row] + list(reader)

        for row in reader:
            if not row or len(row) < 4:
                continue
            if len(row) >= 5 and row[0].strip().isdigit():
                t_id, user_id, movie_id, tag, ts = [x.strip() for x in row[:5]]
                sql_file.write(
                    f"INSERT INTO tags (id, user_id, movie_id, tag, timestamp) VALUES ("
                    f"{t_id}, {user_id}, {movie_id}, {escape_sql_string(tag)}, {ts});\n"
                )
            else:
                user_id, movie_id, tag, ts = [x.strip() for x in row[:4]]
                sql_file.write(
                    f"INSERT INTO tags (user_id, movie_id, tag, timestamp) VALUES ("
                    f"{user_id}, {movie_id}, {escape_sql_string(tag)}, {ts});\n"
                )
    sql_file.write("\n")


def process_users(sql_file):
    """Генерация DD/DML для таблицы users."""
    file_path = find_dataset_file('users')
    delimiter = detect_delimiter(file_path)

    sql_file.write("-- Table: users\n")
    sql_file.write("DROP TABLE IF EXISTS users;\n")
    sql_file.write("""CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    gender TEXT,
    register_date TEXT,
    occupation TEXT
);\n\n""")

    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f, delimiter=delimiter)
        first_row = next(reader, None)
        if first_row and not first_row[0].isdigit():
            pass
        elif first_row:
            reader = [first_row] + list(reader)

        for row in reader:
            if not row or len(row) < 2:
                continue
            user_id = row[0].strip()
            name = row[1].strip() if len(row) > 1 else ''
            email = row[2].strip() if len(row) > 2 else ''
            gender = row[3].strip() if len(row) > 3 else ''
            reg_date = row[4].strip() if len(row) > 4 else ''
            occupation = row[5].strip() if len(row) > 5 else ''

            sql_file.write(
                f"INSERT INTO users (id, name, email, gender, register_date, occupation) VALUES ("
                f"{user_id}, {escape_sql_string(name)}, {escape_sql_string(email)}, "
                f"{escape_sql_string(gender)}, {escape_sql_string(reg_date)}, "
                f"{escape_sql_string(occupation)});\n"
            )
    sql_file.write("\n")


def main():
    print("Generating db_init.sql...")
    with open(OUTPUT_SQL, 'w', encoding='utf-8') as sql_file:
        sql_file.write("PRAGMA foreign_keys = ON;\n\n")
        process_movies(sql_file)
        process_ratings(sql_file)
        process_tags(sql_file)
        process_users(sql_file)
    print(f"Successfully generated: {OUTPUT_SQL}")


if __name__ == '__main__':
    main()