#!/usr/bin/env python3
"""
archive_dicom_demo.py - ДЕМО-ВЕРСИЯ архивации DICOM-изображений
Для Windows: имитирует перенос файлов старше 1 года в холодное хранилище
"""

import os
import json
import shutil
import logging
from datetime import datetime, timedelta
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Настройки для Windows
HOT_STORAGE = "C:/dicom/hot_storage"      # "Горячее" хранилище (последние 2 месяца)
COLD_STORAGE = "C:/dicom/cold_archive"    # "Холодное" хранилище (архив)
DAYS_TO_KEEP_HOT = 365                     # Храним в горячем хранилище 365 дней

# Создаем необходимые папки
os.makedirs(HOT_STORAGE, exist_ok=True)
os.makedirs(COLD_STORAGE, exist_ok=True)

def create_test_dicom_files():
    """Создает тестовые DICOM-файлы с разными датами"""
    logger.info("📁 Создаем тестовые DICOM-файлы...")
    
    # Создаем файлы с разными датами
    test_files = [
        {"name": "patient_001_2025_01_15.dcm", "days_ago": 520},  # Старый файл (> 365 дней)
        {"name": "patient_002_2025_06_10.dcm", "days_ago": 370},  # Старый файл (> 365 дней)
        {"name": "patient_003_2026_01_05.dcm", "days_ago": 160},  # Новый файл (< 365 дней)
        {"name": "patient_004_2026_03_20.dcm", "days_ago": 90},   # Новый файл (< 365 дней)
        {"name": "patient_005_2026_05_15.dcm", "days_ago": 30},   # Новый файл (< 365 дней)
    ]
    
    for file_info in test_files:
        file_path = os.path.join(HOT_STORAGE, file_info["name"])
        
        # Создаем содержимое файла (имитация DICOM)
        content = {
            "patient_id": file_info["name"].split("_")[1],
            "study_date": (datetime.now() - timedelta(days=file_info["days_ago"])).strftime("%Y-%m-%d"),
            "modality": "MRI",
            "body_part": "Brain",
            "description": f"Test DICOM file created {file_info['days_ago']} days ago"
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2)
        
        # Устанавливаем дату создания файла (для имитации)
        create_time = datetime.now() - timedelta(days=file_info["days_ago"])
        os.utime(file_path, (create_time.timestamp(), create_time.timestamp()))
        
        logger.info(f"   ✅ Создан: {file_info['name']} (возраст: {file_info['days_ago']} дней)")
    
    return test_files

def check_file_age(file_path):
    """Проверяет возраст файла в днях"""
    # Берем дату изменения файла
    mtime = os.path.getmtime(file_path)
    file_date = datetime.fromtimestamp(mtime)
    age_days = (datetime.now() - file_date).days
    return age_days

def archive_old_files():
    """Архивирует файлы старше DAYS_TO_KEEP_HOT дней"""
    logger.info("=" * 60)
    logger.info("🚀 ЗАПУСК АРХИВАЦИИ DICOM-ФАЙЛОВ")
    logger.info("=" * 60)
    
    # Считаем файлы
    all_files = os.listdir(HOT_STORAGE)
    logger.info(f"📊 Найдено файлов в горячем хранилище: {len(all_files)}")
    
    archived_count = 0
    archived_size = 0
    skipped_count = 0
    
    for filename in all_files:
        file_path = os.path.join(HOT_STORAGE, filename)
        
        # Пропускаем папки
        if os.path.isdir(file_path):
            continue
        
        # Проверяем возраст файла
        age_days = check_file_age(file_path)
        file_size = os.path.getsize(file_path)
        
        if age_days > DAYS_TO_KEEP_HOT:
            # Файл старый - архивируем
            logger.info(f"📦 Архивация: {filename}")
            logger.info(f"   Возраст: {age_days} дней (превышает лимит {DAYS_TO_KEEP_HOT} дней)")
            logger.info(f"   Размер: {file_size:,} байт")
            
            # Копируем в холодное хранилище
            dest_path = os.path.join(COLD_STORAGE, filename)
            
            # Имитация загрузки в Glacier (создаем архивную копию)
            with open(file_path, 'r', encoding='utf-8') as src:
                content = json.load(src)
            
            # Добавляем метаданные архива
            content["archived"] = True
            content["archive_date"] = datetime.now().isoformat()
            content["original_path"] = file_path
            content["age_days"] = age_days
            content["archive_storage"] = "GLACIER (имитация)"
            
            with open(dest_path, 'w', encoding='utf-8') as dst:
                json.dump(content, dst, indent=2)
            
            # Удаляем из горячего хранилища
            os.remove(file_path)
            
            archived_count += 1
            archived_size += file_size
            
            logger.info(f"   ✅ Перемещен в холодное хранилище: {dest_path}")
        else:
            # Файл достаточно новый - оставляем
            logger.info(f"⏩ Пропуск: {filename} (возраст {age_days} дней, меньше лимита)")
            skipped_count += 1
    
    # Итоговый отчет
    logger.info("=" * 60)
    logger.info("📊 ИТОГОВЫЙ ОТЧЕТ АРХИВАЦИИ")
    logger.info("=" * 60)
    logger.info(f"✅ Заархивировано файлов: {archived_count}")
    logger.info(f"   Освобождено места: {archived_size:,} байт")
    logger.info(f"⏩ Пропущено файлов: {skipped_count}")
    
    # Показываем содержимое папок
    logger.info("=" * 60)
    logger.info("📁 Содержимое горячего хранилища:")
    for f in os.listdir(HOT_STORAGE):
        if os.path.isfile(os.path.join(HOT_STORAGE, f)):
            age = check_file_age(os.path.join(HOT_STORAGE, f))
            logger.info(f"   📄 {f} (возраст: {age} дней)")
    
    logger.info("=" * 60)
    logger.info("📁 Содержимое холодного хранилища (архив):")
    for f in os.listdir(COLD_STORAGE):
        if os.path.isfile(os.path.join(COLD_STORAGE, f)):
            size = os.path.getsize(os.path.join(COLD_STORAGE, f))
            logger.info(f"   📦 {f} (размер: {size:,} байт) 🧊")
    
    logger.info("=" * 60)
    logger.info("✅ АРХИВАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")
    logger.info("=" * 60)

def restore_from_archive(file_pattern=None):
    """Восстанавливает файлы из холодного хранилища (для демонстрации)"""
    logger.info("=" * 60)
    logger.info("🔄 ЗАПУСК ВОССТАНОВЛЕНИЯ ИЗ АРХИВА")
    logger.info("=" * 60)
    
    archive_files = os.listdir(COLD_STORAGE)
    
    if not archive_files:
        logger.warning("Архив пуст!")
        return
    
    # Ищем файлы для восстановления
    restored_count = 0
    for filename in archive_files:
        if file_pattern and file_pattern not in filename:
            continue
        
        archive_path = os.path.join(COLD_STORAGE, filename)
        restore_path = os.path.join(HOT_STORAGE, filename)
        
        # Читаем архив
        with open(archive_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # Убираем архивные метки
        content.pop("archived", None)
        content.pop("archive_date", None)
        content.pop("original_path", None)
        content.pop("age_days", None)
        content.pop("archive_storage", None)
        
        # Восстанавливаем
        with open(restore_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2)
        
        # Удаляем из архива
        os.remove(archive_path)
        
        restored_count += 1
        logger.info(f"   ✅ Восстановлен: {filename}")
    
    logger.info(f"📊 Восстановлено файлов: {restored_count}")

def show_storage_info():
    """Показывает информацию о хранилищах"""
    logger.info("=" * 60)
    logger.info("💾 ИНФОРМАЦИЯ О ХРАНИЛИЩАХ")
    logger.info("=" * 60)
    
    # Горячее хранилище
    hot_files = [f for f in os.listdir(HOT_STORAGE) if os.path.isfile(os.path.join(HOT_STORAGE, f))]
    hot_size = sum(os.path.getsize(os.path.join(HOT_STORAGE, f)) for f in hot_files)
    
    logger.info(f"🔥 Горячее хранилище:")
    logger.info(f"   Файлов: {len(hot_files)}")
    logger.info(f"   Размер: {hot_size:,} байт")
    
    # Холодное хранилище
    cold_files = [f for f in os.listdir(COLD_STORAGE) if os.path.isfile(os.path.join(COLD_STORAGE, f))]
    cold_size = sum(os.path.getsize(os.path.join(COLD_STORAGE, f)) for f in cold_files)
    
    logger.info(f"🧊 Холодное хранилище (архив):")
    logger.info(f"   Файлов: {len(cold_files)}")
    logger.info(f"   Размер: {cold_size:,} байт")
    
    logger.info(f"📊 Всего файлов: {len(hot_files) + len(cold_files)}")
    logger.info(f"📊 Общий размер: {hot_size + cold_size:,} байт")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🖥️  СИСТЕМА АРХИВАЦИИ DICOM-ИЗОБРАЖЕНИЙ")
    print("=" * 60)
    print("1. Создать тестовые DICOM-файлы")
    print("2. Запустить архивацию старых файлов")
    print("3. Показать информацию о хранилищах")
    print("4. Восстановить файлы из архива")
    print("5. Полный цикл (создать → архивировать → показать)")
    print("0. Выход")
    print("=" * 60)
    
    while True:
        choice = input("\nВыберите действие (0-5): ").strip()
        
        if choice == "0":
            print("👋 До свидания!")
            break
        elif choice == "1":
            create_test_dicom_files()
        elif choice == "2":
            archive_old_files()
        elif choice == "3":
            show_storage_info()
        elif choice == "4":
            pattern = input("Введите часть имени файла для восстановления (или Enter для всех): ").strip()
            restore_from_archive(pattern if pattern else None)
        elif choice == "5":
            logger.info("🚀 Запуск полного цикла...")
            create_test_dicom_files()
            archive_old_files()
            show_storage_info()
        else:
            print("❌ Неверный выбор. Попробуйте снова.")
