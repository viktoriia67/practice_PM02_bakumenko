#!/usr/bin/env python3
"""
validate_anonymization_demo.py - ДЕМО-ВЕРСИЯ проверки анонимизации
Проверяет, что тестовые данные не попали в продакшн
Для Windows: использует SQLite вместо PostgreSQL
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
import shutil

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Настройки
DB_PATH = "C:/backup/demo_clinic.db"  # SQLite база данных
DICOM_DIR = "C:/dicom/hot_storage"    # Папка с DICOM-файлами
TEST_DICOM_DIR = "C:/dicom/test_storage"  # Папка с тестовыми DICOM

# Создаем папки
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(DICOM_DIR, exist_ok=True)
os.makedirs(TEST_DICOM_DIR, exist_ok=True)

def create_test_database():
    """Создает тестовую базу данных с пациентами"""
    logger.info("=" * 60)
    logger.info("📊 СОЗДАНИЕ ТЕСТОВОЙ БАЗЫ ДАННЫХ")
    logger.info("=" * 60)
    
    # Удаляем старую БД, если есть
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    # Создаем подключение
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Создаем таблицу пациентов
    cursor.execute('''
        CREATE TABLE patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            birth_date TEXT,
            phone TEXT,
            email TEXT,
            updated_at TEXT
        )
    ''')
    
    # Вставляем тестовые данные
    test_patients = [
        # Реальные пациенты (нормальные имена)
        ("Иванова Мария Петровна", "1985-03-15", "+7(999)123-45-67", "maria@mail.ru", datetime.now().isoformat()),
        ("Петров Сергей Иванович", "1990-07-22", "+7(999)234-56-78", "sergey@mail.ru", datetime.now().isoformat()),
        ("Сидорова Анна Владимировна", "1978-11-01", "+7(999)345-67-89", "anna@mail.ru", datetime.now().isoformat()),
        
        # ТЕСТОВЫЕ пациенты (должны быть обнаружены!)
        ("Test User", "2000-01-01", "+7(999)000-00-00", "test@test.ru", datetime.now().isoformat()),
        ("Тестовый Пациент", "1995-05-05", "+7(999)111-11-11", "test2@test.ru", datetime.now().isoformat()),
        ("John Doe Test", "1980-12-12", "+7(999)222-22-22", "john@test.com", datetime.now().isoformat()),
        
        # Еще реальные пациенты
        ("Козлов Дмитрий Алексеевич", "1982-09-30", "+7(999)456-78-90", "dmitry@mail.ru", datetime.now().isoformat()),
        ("Новикова Елена Сергеевна", "1992-04-18", "+7(999)567-89-01", "elena@mail.ru", datetime.now().isoformat()),
    ]
    
    for patient in test_patients:
        cursor.execute('''
            INSERT INTO patients (full_name, birth_date, phone, email, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', patient)
    
    conn.commit()
    
    # Проверяем количество
    cursor.execute("SELECT COUNT(*) FROM patients")
    count = cursor.fetchone()[0]
    logger.info(f"✅ Создана БД с {count} записями")
    
    # Показываем список пациентов
    cursor.execute("SELECT id, full_name FROM patients")
    all_patients = cursor.fetchall()
    logger.info("📋 Список пациентов:")
    for patient_id, name in all_patients:
        is_test = "🔴 ТЕСТОВЫЙ" if any(word in name.lower() for word in ["test", "тест", "john"]) else "🟢"
        logger.info(f"   {patient_id}. {name} {is_test}")
    
    conn.close()
    return DB_PATH

def create_test_dicom_files():
    """Создает тестовые DICOM-файлы с метаданными"""
    logger.info("=" * 60)
    logger.info("📁 СОЗДАНИЕ ТЕСТОВЫХ DICOM-ФАЙЛОВ")
    logger.info("=" * 60)
    
    # Очищаем папки
    for folder in [DICOM_DIR, TEST_DICOM_DIR]:
        for f in os.listdir(folder):
            os.remove(os.path.join(folder, f))
    
    # Создаем файлы в основной папке (продакшн)
    production_files = [
        {"name": "patient_001_mri_brain.dcm", "patient_name": "Иванова Мария"},
        {"name": "patient_002_ct_chest.dcm", "patient_name": "Петров Сергей"},
        {"name": "patient_003_mri_spine.dcm", "patient_name": "Сидорова Анна"},
        {"name": "patient_004_xray_hand.dcm", "patient_name": "Козлов Дмитрий"},
        {"name": "patient_005_ultrasound.dcm", "patient_name": "Новикова Елена"},
    ]
    
    for file_info in production_files:
        file_path = os.path.join(DICOM_DIR, file_info["name"])
        content = {
            "patient_name": file_info["patient_name"],
            "study_date": "2026-06-15",
            "modality": file_info["name"].split("_")[1].upper() if len(file_info["name"].split("_")) > 1 else "MRI",
            "body_part": file_info["name"].split("_")[2].split(".")[0] if len(file_info["name"].split("_")) > 2 else "Unknown",
            "file_size": 1024 * 1024,  # 1 MB
            "is_test": False
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2)
        logger.info(f"   ✅ Создан: {file_info['name']} (пациент: {file_info['patient_name']})")
    
    # Создаем ТЕСТОВЫЕ файлы (должны быть обнаружены!)
    test_files = [
        {"name": "test_patient_001.dcm", "patient_name": "Test Patient"},
        {"name": "тестовый_пациент_002.dcm", "patient_name": "Тестовый Пациент"},
        {"name": "test_mri_003.dcm", "patient_name": "John Doe"},
    ]
    
    for file_info in test_files:
        file_path = os.path.join(DICOM_DIR, file_info["name"])
        content = {
            "patient_name": file_info["patient_name"],
            "study_date": "2026-06-10",
            "modality": "TEST",
            "body_part": "Test",
            "file_size": 1024 * 512,  # 512 KB
            "is_test": True
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2)
        logger.info(f"   🔴 Создан ТЕСТОВЫЙ: {file_info['name']} (пациент: {file_info['patient_name']})")
    
    # Также создаем файл с теговым именем в отдельной папке (для демонстрации)
    test_file_path = os.path.join(TEST_DICOM_DIR, "test_backup_001.dcm")
    with open(test_file_path, 'w', encoding='utf-8') as f:
        json.dump({"test": True, "name": "Test backup file"}, f)
    logger.info(f"   🔴 Создан тестовый файл в отдельной папке: {test_file_path}")

def check_test_data_in_database():
    """Проверяет наличие тестовых данных в БД"""
    logger.info("=" * 60)
    logger.info("🔍 ПРОВЕРКА БАЗЫ ДАННЫХ НА ТЕСТОВЫЕ ЗАПИСИ")
    logger.info("=" * 60)
    
    if not os.path.exists(DB_PATH):
        logger.error("❌ База данных не найдена!")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Проверяем на явные тестовые данные
    test_keywords = ["test", "тест", "Test", "Тест", "John", "Doe"]
    
    found_test_patients = []
    for keyword in test_keywords:
        cursor.execute('''
            SELECT id, full_name, email, phone FROM patients 
            WHERE full_name LIKE ? OR email LIKE ? OR phone LIKE ?
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        
        results = cursor.fetchall()
        for row in results:
            found_test_patients.append(row)
    
    conn.close()
    
    if found_test_patients:
        logger.error(f"❌ НАЙДЕНО {len(found_test_patients)} ТЕСТОВЫХ ЗАПИСЕЙ:")
        for patient_id, name, email, phone in found_test_patients:
            logger.error(f"   ID: {patient_id}, Имя: {name}, Email: {email}, Телефон: {phone}")
        return False
    else:
        logger.info("✅ Тестовых записей в БД не найдено")
        return True

def check_test_dicom_files():
    """Проверяет DICOM-файлы на наличие тестовых данных"""
    logger.info("=" * 60)
    logger.info("🔍 ПРОВЕРКА DICOM-ФАЙЛОВ НА ТЕСТОВЫЕ ДАННЫЕ")
    logger.info("=" * 60)
    
    if not os.path.exists(DICOM_DIR):
        logger.error("❌ Папка DICOM не найдена!")
        return False
    
    test_files_found = []
    
    for filename in os.listdir(DICOM_DIR):
        file_path = os.path.join(DICOM_DIR, filename)
        
        if os.path.isdir(file_path):
            continue
        
        # Проверяем имя файла
        is_test_by_name = False
        test_keywords = ["test", "тест", "Test", "Тест"]
        for keyword in test_keywords:
            if keyword in filename:
                is_test_by_name = True
                break
        
        # Проверяем содержимое файла
        is_test_by_content = False
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                if content.get("is_test", False):
                    is_test_by_content = True
                if "patient_name" in content:
                    for keyword in ["test", "тест", "Test", "Тест", "John"]:
                        if keyword in content["patient_name"]:
                            is_test_by_content = True
                            break
        except:
            pass
        
        if is_test_by_name or is_test_by_content:
            test_files_found.append(filename)
            logger.error(f"   🔴 ТЕСТОВЫЙ ФАЙЛ: {filename}")
        else:
            logger.info(f"   ✅ OK: {filename}")
    
    # Проверяем отдельную папку с тестовыми файлами
    if os.path.exists(TEST_DICOM_DIR):
        for filename in os.listdir(TEST_DICOM_DIR):
            if filename.startswith("test_"):
                test_files_found.append(f"TEST_DICOM_DIR/{filename}")
                logger.error(f"   🔴 ТЕСТОВЫЙ ФАЙЛ в отдельной папке: {filename}")
    
    if test_files_found:
        logger.error(f"❌ НАЙДЕНО {len(test_files_found)} ТЕСТОВЫХ DICOM-ФАЙЛОВ")
        return False
    else:
        logger.info("✅ Тестовых DICOM-файлов не найдено")
        return True

def run_full_validation():
    """Запускает полную проверку анонимизации"""
    logger.info("=" * 60)
    logger.info("🔐 ЗАПУСК ПОЛНОЙ ПРОВЕРКИ АНОНИМИЗАЦИИ")
    logger.info("=" * 60)
    logger.info(f"📅 Дата проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # Сначала создаем тестовые данные (для демонстрации)
    create_test_database()
    create_test_dicom_files()
    
    print("\n" + "=" * 60)
    print("🔍 НАЧАЛО ПРОВЕРКИ")
    print("=" * 60 + "\n")
    
    # Проверка БД
    db_ok = check_test_data_in_database()
    
    print("\n" + "-" * 60 + "\n")
    
    # Проверка DICOM
    dicom_ok = check_test_dicom_files()
    
    # Итоговый результат
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ ПРОВЕРКИ")
    print("=" * 60)
    logger.info(f"База данных: {'✅ OK' if db_ok else '❌ НАЙДЕНЫ ТЕСТОВЫЕ ДАННЫЕ'}")
    logger.info(f"DICOM-файлы: {'✅ OK' if dicom_ok else '❌ НАЙДЕНЫ ТЕСТОВЫЕ ФАЙЛЫ'}")
    
    if db_ok and dicom_ok:
        logger.info("=" * 60)
        logger.info("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! АНОНИМИЗАЦИЯ КОРРЕКТНА")
        logger.info("=" * 60)
        return True
    else:
        logger.error("=" * 60)
        logger.error("❌ ОБНАРУЖЕНЫ НАРУШЕНИЯ АНОНИМИЗАЦИИ!")
        logger.error("   Требуется исправление перед выкаткой в продакшн")
        logger.error("=" * 60)
        return False

def fix_test_data():
    """Автоматически исправляет найденные тестовые данные"""
    logger.info("=" * 60)
    logger.info("🔧 ИСПРАВЛЕНИЕ ТЕСТОВЫХ ДАННЫХ")
    logger.info("=" * 60)
    
    # Исправляем БД
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        test_keywords = ["test", "тест", "Test", "Тест", "John", "Doe"]
        deleted_count = 0
        
        for keyword in test_keywords:
            cursor.execute('''
                DELETE FROM patients 
                WHERE full_name LIKE ? OR email LIKE ? OR phone LIKE ?
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
            deleted_count += cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Удалено {deleted_count} тестовых записей из БД")
    
    # Исправляем DICOM
    if os.path.exists(DICOM_DIR):
        for filename in os.listdir(DICOM_DIR):
            file_path = os.path.join(DICOM_DIR, filename)
            if os.path.isfile(file_path):
                is_test = False
                for keyword in ["test", "тест", "Test", "Тест"]:
                    if keyword in filename:
                        is_test = True
                        break
                
                if is_test:
                    os.remove(file_path)
                    logger.info(f"✅ Удален тестовый DICOM-файл: {filename}")
    
    logger.info("✅ Тестовые данные успешно удалены!")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔐 СИСТЕМА ПРОВЕРКИ АНОНИМИЗАЦИИ")
    print("=" * 60)
    print("1. Запустить полную проверку (создать тестовые данные → проверить)")
    print("2. Проверить только базу данных")
    print("3. Проверить только DICOM-файлы")
    print("4. Исправить найденные тестовые данные")
    print("0. Выход")
    print("=" * 60)
    
    # Создаем тестовую БД при первом запуске
    if not os.path.exists(DB_PATH):
        create_test_database()
        create_test_dicom_files()
    
    while True:
        choice = input("\nВыберите действие (0-4): ").strip()
        
        if choice == "0":
            print("👋 До свидания!")
            break
        elif choice == "1":
            run_full_validation()
        elif choice == "2":
            print("\n" + "-" * 60)
            check_test_data_in_database()
            print("-" * 60)
        elif choice == "3":
            print("\n" + "-" * 60)
            check_test_dicom_files()
            print("-" * 60)
        elif choice == "4":
            fix_test_data()
        else:
            print("❌ Неверный выбор. Попробуйте снова.")
