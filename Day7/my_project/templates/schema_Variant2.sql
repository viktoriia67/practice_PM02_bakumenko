USE variant2_work;

CREATE TABLE IF NOT EXISTS Пользователи (
    id_пользователя INT PRIMARY KEY AUTO_INCREMENT,
    логин VARCHAR(50) UNIQUE NOT NULL,
    пароль_hash VARCHAR(255) NOT NULL,
    роль ENUM('admin', 'worker') DEFAULT 'worker',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Добавляем тестовых пользователей (пароли будут добавлены через Python-скрипт)
INSERT INTO Пользователи (логин, пароль_hash, роль) VALUES
('admin', 'temp', 'admin'),
('worker', 'temp', 'worker');
