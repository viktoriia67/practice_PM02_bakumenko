-- Автомобили клиента с фамилией «Иванов» 
SELECT c.*
FROM Cars c
JOIN Clients cl ON c.clients_id = cl.id
WHERE cl.last_name = 'Иванов';

-- Список нарядов с указанием автомобиля (модель, госномер) и даты
SELECT w.id AS workorder_id, c.brand, c.model, c.license_plate, w.order_date, w.status
FROM WorkOrders w
JOIN Cars c ON w.car_id = c.id
ORDER BY w.order_date;

-- Все услуги, выполненные в наряде №1, с ценой
SELECT s.id, s.name, s.price
FROM OrderServices os
JOIN Services s ON os.service_id = s.id
WHERE os.order_id = 1;

-- Общая стоимость запчастей, использованных в наряде №2
SELECT COALESCE(SUM(sp.price * op.quantity),0) AS total_parts_cost
FROM OrderParts op
JOIN SpareParts sp ON op.part_id = sp.id
WHERE op.order_id = 2;

-- Средняя продолжительность услуг
SELECT AVG(duration_hours) AS avg_duration_hours FROM Services;

-- Группировка услуг по названию и подсчёт, сколько раз они заказывались 
SELECT s.name, COUNT(os.id) AS times_ordered
FROM Services s
LEFT JOIN OrderServices os ON s.id = os.service_id
GROUP BY s.name
ORDER BY times_ordered DESC;

-- Клиенты, у которых больше одного автомобиля 
SELECT cl.id, cl.first_name, cl.last_name, COUNT(c.id) AS cars_count
FROM Clients cl
JOIN Cars c ON cl.id = c.clients_id
GROUP BY cl.id, cl.first_name, cl.last_name
HAVING COUNT(c.id) > 1;

-- Наряды, в которых не использовались запчасти 
SELECT w.*
FROM WorkOrders w
LEFT JOIN OrderParts op ON w.id = op.order_id
WHERE op.id IS NULL;

-- Увеличение цен всех запчастей на 10%
SET SQL_SAFE_UPDATES = 0;

UPDATE spareparts SET price = price * 1.10;

SET SQL_SAFE_UPDATES = 1;

-- Удаление наряда со статусом «отменён» 
SET SQL_SAFE_UPDATES = 0;

START TRANSACTION;
DELETE os FROM OrderServices os JOIN WorkOrders w ON os.order_id = w.id WHERE w.status = 'cancelled';
DELETE op FROM OrderParts op JOIN WorkOrders w2 ON op.order_id = w2.id WHERE w2.status = 'cancelled';
DELETE FROM WorkOrders WHERE status = 'cancelled';
COMMIT;

SET SQL_SAFE_UPDATES = 1;

-- Добавление в таблицу Clients столбец email
ALTER TABLE Clients ADD COLUMN email VARCHAR(255);

-- Представление CarServiceHistory, выводящее историю ремонтов для каждого автомобиля
CREATE OR REPLACE VIEW CarServiceHistory AS
SELECT c.id AS car_id, c.brand, c.model, c.license_plate,
w.id AS order_id, w.order_date, w.status,
s.id AS service_id, s.name AS service_name, s.price AS service_price,
op.part_id, sp.name AS part_name, sp.price AS part_price, op.quantity
FROM Cars c
LEFT JOIN WorkOrders w ON c.id = w.car_id
LEFT JOIN OrderServices os ON w.id = os.order_id
LEFT JOIN Services s ON os.service_id = s.id
LEFT JOIN OrderParts op ON w.id = op.order_id
LEFT JOIN SpareParts sp ON op.part_id = sp.id
ORDER BY c.id, w.order_date;

-- Для каждого клиента выводим количество его автомобилей, общее количество услуг во всех нарядах и общую стоимость 
SELECT cl.id, cl.first_name, cl.last_name,
COALESCE(t.num_cars,0) AS num_cars,
COALESCE(t.total_services,0) AS total_services_count,
COALESCE(t.total_cost,0) AS total_cost
FROM Clients cl
LEFT JOIN (
SELECT c.clients_id,
COUNT(DISTINCT c.id) AS num_cars,
COUNT(os.id) AS total_services,
COALESCE(SUM(s.price),0) + COALESCE(SUM(sp.price * op.quantity),0) AS total_cost
FROM Cars c
LEFT JOIN WorkOrders w ON c.id = w.car_id
LEFT JOIN OrderServices os ON w.id = os.order_id
LEFT JOIN Services s ON os.service_id = s.id
LEFT JOIN OrderParts op ON w.id = op.order_id
LEFT JOIN SpareParts sp ON op.part_id = sp.id
GROUP BY c.clients_id
) t ON cl.id = t.clients_id;
