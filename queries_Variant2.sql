-- =============================
-- Все записи клиентов.
SELECT * FROM clients;

-- =============================
-- Услугм больше 1500 рублей.
SELECT * FROM services WHERE price > 1500.00;

-- =============================
-- Заказы по убыванию даты.
SELECT * FROM order_names ORDER BY date DESC;

-- =============================
-- Клиенты, чьё имя начинается на букву "А".
SELECT * FROM clients WHERE name LIKE 'А%';

-- =============================
-- Первые 5 записей из таблицы запчасти.
SELECT * FROM parts LIMIT 5;

-- =============================
-- Связанные две таблицы.
SELECT clients.id_clients, cars.brand, clients.phone
FROM clients
JOIN cars ON clients.id_clients = cars.id_cars;

-- =============================
-- Данные из трёх таблиц.
SELECT clients.surname, cars.brand, cars.Model, order_names.Date
FROM clients
JOIN cars ON clients.id_Clients = cars.id_Clients
JOIN order_names ON clients.id_Clients = order_names.id_Clients; 

-- =============================
-- Левое соединение.
SELECT clients.surname, clients.name, order_names.id_Order_Names, order_names.Date
FROM clients
LEFT JOIN order_names ON clients.id_Clients = order_names.id_Clients;

-- =============================
-- Список сущностей и количество свызанных записей.
SELECT clients.surname, COUNT(order_names.id_Order_Names) AS count_orders
FROM clients
LEFT JOIN order_names ON clients.id_clients = order_names.id_clients
GROUP BY clients.surname;

-- =============================
-- Записи, у которых нет связанных данных.
SELECT clients.surname, clients.name, clients.Phone
FROM clients
LEFT JOIN order_names ON clients.id_Clients = order_names.id_clients
WHERE order_names.id_Order_Names IS NULL;

-- =============================
-- Общее количество заказов.
SELECT COUNT(*) AS Total_orders FROM order_names;

-- =============================
-- Сумма, минимум, максимум, средннее по числовому полю.
SELECT SUM(price) AS Total_amount FROM services;
SELECT MIN(price) AS Min FROM services;
SELECT MAX(price) AS Max FROM services;
SELECT AVG(price) AS Average FROM services;

-- =============================
-- Группировка данных по олному полю и количетсво.
SELECT status, COUNT(*) AS quantity FROM order_names GROUP BY status;

-- =============================
-- Клиенты, у которых более 1 заказа.
SELECT id_clients, COUNT(*) AS quantity_orders
FROM order_names
GROUP BY id_clients
HAVING COUNT(*) > 1

UNION ALL

SELECT 0 AS id_clients, 0 AS count_orders
FROM (SELECT 1) AS dummy
WHERE NOT EXISTS (
SELECT 1
FROM order_names
GROUP BY id_clients
HAVING COUNT(*) > 1
);

-- =========================
-- Значение поля равно максимульному.
SELECT title, price
FROM services
WHERE price > (SELECT AVG(price) FROM services);

-- =========================
-- Клиенты, у которых нет автомобилей.
SELECT surname, name FROM clients
WHERE id_clients NOT IN (SELECT id_clients FROM cars);

-- =========================
-- Запчасти, которые использовались хотя бы в одном заказе.
SELECT title FROM parts
WHERE EXISTS (SELECT * FROM parts_in_orders WHERE parts_in_orders.id_Parts = parts.id_Parts);

-- =========================
-- Повышение цены на все запчасти на 10%.
SET SQL_SAFE_UPDATES = 0;

UPDATE parts SET price = price * 1.10; 

SET SQL_SAFE_UPDATES = 1;

-- ==========================
-- Изменение статуса.
UPDATE order_names SET status = 'Выполнен' WHERE id_order_names = 3;

-- ==========================
-- Удаление устаревших записей.
SET SQL_SAFE_UPDATES = 0;

DELETE FROM order_names WHERE date < '09.06.2025';

SET SQL_SAFE_UPDATES = 1;