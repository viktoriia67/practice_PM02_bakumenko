USE variant2_work;

-- Клиенты
INSERT INTO Clients (first_name, last_name, phone) VALUES
('Иван','Иванов','+7-900-111-11-11'),
('Пётр','Петров','+7-900-222-22-22'),
('Мария','Сидорова','+7-900-333-33-33'),
('Алексей','Кузнецов','+7-900-444-44-44');

-- Автомобили 
INSERT INTO Cars (clients_id, brand, model, year, license_plate) VALUES
(1,'Lada','Granta',2018,'A111AA77'),
(1,'Toyota','Camry',2015,'B222BB77'),
(2,'BMW','X5',2020,'C333CC77'),
(3,'Kia','Rio',2017,'D444DD77'),
(4,'Hyundai','Solaris',2019,'E555EE77');

-- Услуги
INSERT INTO Services (name, price, duration_hours) VALUES
('Замена масла', 2000.00, 1.00),
('Замена тормозных колодок', 5000.00, 2.50),
('Диагностика двигателя', 1500.00, 1.50),
('Шиномонтаж', 800.00, 0.75);

-- Запчасти
INSERT INTO SpareParts (name, price, stock_quantity) VALUES
('Моторное масло 5л', 2500.00, 10),
('Масляный фильтр', 400.00, 20),
('Воздушный фильтр', 600.00, 15),
('Сальник привода', 1200.00, 8),
('Тормозные колонки', 3500.00, 5);

-- Наряды (WorkOrders)
INSERT INTO WorkOrders (car_id, order_date, status) VALUES
(1, '2026-01-10', 'completed'),
(2, '2026-02-05', 'in_progress'),
(3, '2026-03-01', 'cancelled');

-- OrderServices (для наряда 1 - услуга 1 и 3; для наряда 2 - услуги 2 и 3)
INSERT INTO OrderServices (order_id, service_id) VALUES
(1,1),(1,3),
(2,2),(2,3);

-- OrderParts (например к наряду 1 масло и фильтр; к наряду 2 тормозные колодки)
INSERT INTO OrderParts (order_id, part_id, quantity) VALUES
(1,1,1),(1,2,1),
(2,3,1);
