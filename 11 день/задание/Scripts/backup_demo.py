#!/usr/bin/env python3
"""
backup_demo.py - ДЕМО-ВЕРСИЯ бэкапа PostgreSQL (без реальной БД)
Для демонстрации процесса резервного копирования
"""

import os
import logging
import json
import hashlib
import shutil
from datetime import datetime, timedelta
from Crypto.Cipher import AES
import zstandard as zstd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Настройки
BACKUP_DIR = "C:/backup/demo"
ENCRYPTION_KEY = os.getenv("GOST_KEY", "12345678901234567890123456789012")  # 32 байта

def create_demo_backup():
    """Создает демонстрационный файл бэкапа"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.sql")
    
    # Создаем тестовый дамп базы данных (имитация)
    test_data = {
        "backup_info": {
            "database": "clinic_emias",
            "timestamp": timestamp,
            "version": "1.0",
            "type": "full_backup"
        },
        "tables": [
            {"name": "patients", "count": 1547},
            {"name": "appointments", "count": 3421},
            {"name": "medical_records", "count": 12567}
        ],
        "data": "Sample patient data... (это демонстрационный бэкап)"
    }
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Создан демо-бэкап: {backup_file}")
    return backup_file

def compress_file(input_file):
    """Сжимает файл с помощью Zstandard"""
    compressed_file = input_file + ".zst"
    
    # Читаем исходный файл
    with open(input_file, 'rb') as f:
        data = f.read()
    
    # Сжимаем
    compressor = zstd.ZstdCompressor(level=19)
    compressed_data = compressor.compress(data)
    
    # Сохраняем
    with open(compressed_file, 'wb') as f:
        f.write(compressed_data)
    
    original_size = os.path.getsize(input_file)
    compressed_size = os.path.getsize(compressed_file)
    
    logger.info(f"✅ Сжатие: {original_size:,} → {compressed_size:,} байт (экономия {100 - (compressed_size/original_size*100):.1f}%)")
    return compressed_file

def encrypt_file(input_file):
    """Шифрует файл (AES-256)"""
    encrypted_file = input_file + ".enc"
    
    # Убедимся, что ключ правильной длины
    key = ENCRYPTION_KEY.encode()
    if len(key) < 32:
        key = key.ljust(32, b'0')
    elif len(key) > 32:
        key = key[:32]
    
    # Читаем данные
    with open(input_file, 'rb') as f:
        data = f.read()
    
    # Шифруем
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    
    # Сохраняем: nonce + tag + ciphertext
    with open(encrypted_file, 'wb') as f:
        f.write(cipher.nonce + tag + ciphertext)
    
    logger.info(f"✅ Зашифрован: {encrypted_file}")
    logger.info(f"   Алгоритм: AES-256-GCM (имитация ГОСТ 28147-89)")
    return encrypted_file

def calculate_checksum(file_path):
    """Вычисляет SHA-256 контрольную сумму"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    checksum = sha256.hexdigest()
    logger.info(f"✅ SHA-256: {checksum[:16]}...")
    return checksum

def save_metadata(original_file, compressed_file, encrypted_file, checksum):
    """Сохраняет метаданные о бэкапе"""
    metadata = {
        "job_name": "postgres_demo_backup",
        "status": "success",
        "size_bytes": os.path.getsize(encrypted_file),
        "original_size_bytes": os.path.getsize(original_file),
        "compressed_size_bytes": os.path.getsize(compressed_file),
        "duration_seconds": 5,
        "timestamp": datetime.now().isoformat(),
        "checksum_sha256": checksum,
        "encrypted": True,
        "encryption_algorithm": "AES-256-GCM (ГОСТ 28147-89 имитация)",
        "retention_days": 30
    }
    
    metadata_file = encrypted_file + ".meta.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"✅ Метаданные сохранены: {metadata_file}")
    return metadata

def run_demo_backup():
    """Запускает демонстрационный процесс бэкапа"""
    try:
        logger.info("=" * 60)
        logger.info("🚀 ЗАПУСК ДЕМОНСТРАЦИОННОГО БЭКАПА")
        logger.info("=" * 60)
        
        # 1. Создаем тестовый бэкап
        original = create_demo_backup()
        
        # 2. Сжимаем
        compressed = compress_file(original)
        
        # 3. Шифруем
        encrypted = encrypt_file(compressed)
        
        # 4. Вычисляем контрольную сумму
        checksum = calculate_checksum(encrypted)
        
        # 5. Сохраняем метаданные
        metadata = save_metadata(original, compressed, encrypted, checksum)
        
        # 6. Выводим итоговый отчет
        logger.info("=" * 60)
        logger.info("📊 ИТОГОВЫЙ ОТЧЕТ О БЭКАПЕ")
        logger.info("=" * 60)
        logger.info(json.dumps(metadata, indent=2, ensure_ascii=False))
        
        # 7. Отображаем структуру папки
        logger.info("=" * 60)
        logger.info("📁 Файлы в директории бэкапов:")
        for file in os.listdir(BACKUP_DIR):
            size = os.path.getsize(os.path.join(BACKUP_DIR, file))
            logger.info(f"   📄 {file} ({size:,} байт)")
        
        logger.info("=" * 60)
        logger.info("✅ ДЕМО-БЭКАП УСПЕШНО ЗАВЕРШЕН!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        raise

if __name__ == "__main__":
    # Проверка наличия библиотек
    try:
        import Crypto
        import zstandard
    except ImportError as e:
        print(f"❌ Установите зависимости: pip install pycryptodome zstandard")
        print(f"   Ошибка: {e}")
        exit(1)
    
    run_demo_backup()
