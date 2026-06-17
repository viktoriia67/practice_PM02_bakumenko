#!/usr/bin/env python3
"""
archive_dicom_to_cold.py - Перенос файлов старше 1 года в Deep Archive
"""
import boto3
import os
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HOT_BUCKET = "pacs-hot-storage"
COLD_VAULT = "pacs-glacier-archive"
DAYS_TO_KEEP_HOT = 365  # 1 год

def move_old_files():
    s3 = boto3.client('s3')
    glacier = boto3.client('glacier')
    
    # 1. Сканируем горячий бакет
    objects = s3.list_objects(Bucket=HOT_BUCKET)
    cutoff_date = datetime.now() - timedelta(days=DAYS_TO_KEEP_HOT)
    
    for obj in objects.get('Contents', []):
        last_modified = obj['LastModified'].replace(tzinfo=None)
        if last_modified < cutoff_date:
            key = obj['Key']
            logger.info(f"Архивация файла: {key}")
            
            # 2. Загружаем в Glacier (имитация)
            # В реальности используется S3 Lifecycle Policy,
            # но тут мы демонстрируем логику
            archive_id = glacier.upload_archive(
                vaultName=COLD_VAULT,
                body=s3.get_object(Bucket=HOT_BUCKET, Key=key)['Body'].read()
            )
            logger.info(f"Загружено в Glacier: {archive_id}")
            
            # 3. Удаляем из горячего бакета (экономия места)
            s3.delete_object(Bucket=HOT_BUCKET, Key=key)

if __name__ == "__main__":
    move_old_files()
