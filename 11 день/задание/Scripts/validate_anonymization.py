#!/usr/bin/env python3
"""
validate_anonymization.py - Проверка утечки персональных данных после восстановления
"""
import psycopg2
import os

DB_URL = os.getenv("DB_DR_URL")

def check_test_data_in_prod():
    """Проверяет, не осталось ли в продакшн БД тестовых пациентов (ФИО == 'Test')"""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    # Проверка на явные тестовые данные
    cur.execute("SELECT COUNT(*) FROM patients WHERE full_name LIKE '%Test%' OR full_name LIKE '%Тест%';")
    count = cur.fetchone()[0]
    
    if count > 0:
        raise Exception(f"Найдено {count} тестовых записей в основной БД! Анонимизация нарушена.")
    else:
        print("OK: Тестовых данных в продакшн нет.")

    # Проверка структуры DICOM-директорий (нет ли файлов с теговыми именами)
    # Здесь может быть логика проверки файловой системы

if __name__ == "__main__":
    check_test_data_in_prod()
