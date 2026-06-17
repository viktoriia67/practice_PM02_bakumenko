# Система мониторинга бэкапов

## Дашборд "Health Backup Status"
Отображает:
1. **Статус последнего WAL-бэкапа** (Success/Fail).
2. **Возраст последнего бэкапа** (Age in seconds).
3. **Скорость заполнения DICOM-хранилища**.
4. **Количество ошибок шифрования** (если ключ невалиден).

## PromQL Алерты

### 1. Критический провал бэкапа (BackupJobFailed)
```promql
backup_job_status{job="postgres_wal"} == 0
Действие: Немедленный вызов дежурного инженера (PagerDuty).
2. Бэкап слишком старый (BackupTooOld)
promql
(time() - backup_last_success_timestamp) > 300  # Превышает RPO в 5 минут
Действие: Предупреждение в Slack. Требуется ручная проверка.
3. Недостаточно места для DICOM-архива (DiskSpaceCritical)
promql
(dicom_storage_used / dicom_storage_total) > 0.85
Действие: Запуск скрипта archive_dicom_to_cold.py для освобождения места.
JSON-схема отчета
json
{
  "job_name": "postgres_wal",
  "status": "success",  // success | failed | partial
  "size_bytes": 1024000000,
  "duration_seconds": 120.5,
  "timestamp": "2026-06-16T14:20:00Z",
  "checksum_sha256": "a1b2c3d4...",
  "encrypted": true
}
