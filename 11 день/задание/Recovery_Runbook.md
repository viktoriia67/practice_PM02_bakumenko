# Runbook восстановления (Recovery Runbook)
**Версия:** 1.0
**Сценарий:** Кибератака (шифровальщик) или коррупция данных в основном ЦОД.
**Цель:** Восстановить работу клиники в течение **RTO = 4 часа** (для DICOM) и **RTO = 1 час** (для приема пациентов).

## Предварительные условия
- Доступ к резервному ЦОД (Екатеринбург) с чистыми серверами.
- Ключи расшифровки для бэкапов (хранятся в HSM-модуле).

---

## Сценарий 1. Восстановление PostgreSQL (ЭМИС + LIS) — Критично!
**Время:** 0–60 минут.

1.  **Подготовка инфраструктуры:**
    ```bash
    # Поднимаем чистый кластер PostgreSQL на резервных мощностях
    ansible-playbook -i inventory/dr.yml site.yml --tags postgresql
2.	Восстановление из бэкапа (Point-in-Time Recovery — PITR):
o	Целевое время восстановления: За 5 минут до обнаружения атаки (чтобы исключить зараженные данные).
o	Скачиваем последний Full бэкап из защищенного хранилища (не зашифрованного вирусом):
bash
aws s3 cp s3://backup-clinic/postgres/emias/full/latest.dump.zst.enc /tmp/
o	Расшифровываем (ГОСТ) и распаковываем:
bash
# Декриптор (плагин)
openssl enc -d -gost89 -in /tmp/latest.dump.zst.enc -out /tmp/latest.dump.zst -pass file:/keys/gost.key
zstd -d /tmp/latest.dump.zst
3.	Применение WAL-логов:
bash
# Восстанавливаем схему
pg_restore -h dr-postgres.internal -U admin -d clinic /tmp/latest.dump

# Скачиваем WAL файлы (логи за последние часы)
aws s3 cp s3://backup-clinic/postgres/wal/ /tmp/wal_recovery/ --recursive

# Создаем recovery.conf для автоматического наката логов
echo "restore_command = 'cp /tmp/wal_recovery/%f %p'" > /var/lib/postgresql/recovery.conf
echo "recovery_target_time = '2026-06-16 14:20:00'" >> recovery.conf
echo "recovery_target_action = 'promote'" >> recovery.conf

systemctl restart postgresql
4.	Проверка консистентности:
sql
-- Сверяем количество активных пациентов за сегодня с контрольной суммой в отдельном независимом отчете
SELECT COUNT(*) FROM patients WHERE updated_at > CURRENT_DATE;
-- Ожидаемое значение: 1560

________________________________________
Сценарий 2. Восстановление DICOM-изображений (Холодный архив)
Время: 2–4 часа (параллельно с БД).
1.	Извлечение из Deep Archive:
o	Так как RTO для DICOM = 4 часа, мы не можем ждать 5 часов извлечения из Glacier.
o	Решение: У нас есть "горячий" S3-бакет с изображениями за последние 2 месяца.
bash
# Монтируем "горячий" бакет обратно в систему PACS
s3fs pacs-hot-dr /mnt/dicom_images -o passwd_file=/etc/passwd-s3fs
2.	Восстановление глубокого архива:
o	Для файлов старше 2 месяцев (в Deep Archive) инициируем массовый запрос на извлечение, но приоритезируем пациентов, которые записаны на прием сегодня:
bash
# Получаем список ID пациентов за сегодня из восстановленной БД
psql -h dr-postgres -c "SELECT dicom_id FROM appointments_today" > /tmp/dicom_ids.txt

# Инициируем извлечение только этих файлов с экспресс-доставкой (ускоряем)
aws glacier initiate-job --vault-name pacs-archive --job-parameters file://restore-params.json
________________________________________
Проверка целостности
После восстановления всех систем запускается скрипт validate_anonymization.py, который проверяет, что персональные данные пациентов из тестового окружения не попали в продакшн (см. скрипты).

