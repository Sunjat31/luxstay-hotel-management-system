-- ============================================================
-- LuxStay Hotel Management System — MySQL Database Schema
-- ============================================================
DROP DATABASE IF EXISTS hotel_db;
CREATE DATABASE hotel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hotel_db;
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    phone VARCHAR(20),
    role ENUM('admin','guest') DEFAULT 'guest',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB;
CREATE TABLE IF NOT EXISTS room_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    base_price DECIMAL(10,2) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(10) NOT NULL UNIQUE,
    floor INT NOT NULL,
    room_type_id INT NOT NULL,
    status ENUM('available','occupied','maintenance','reserved') DEFAULT 'available',
    capacity INT DEFAULT 2,
    amenities TEXT,
    FOREIGN KEY (room_type_id) REFERENCES room_types(id) ON DELETE RESTRICT,
    INDEX idx_status (status),
    INDEX idx_floor (floor)
) ENGINE=InnoDB;


CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    room_id INT NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    guests INT DEFAULT 1,
    status ENUM('confirmed','checked_in','checked_out','cancelled') DEFAULT 'confirmed',
    total_amount DECIMAL(10,2),
    special_requests TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE RESTRICT,
    INDEX idx_user (user_id),
    INDEX idx_room (room_id),
    INDEX idx_dates (check_in, check_out),
    INDEX idx_status (status),
    CONSTRAINT chk_dates CHECK (check_out > check_in)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL UNIQUE,
    amount DECIMAL(10,2) NOT NULL,
    method ENUM('cash','card','bkash','nagad','bank_transfer') DEFAULT 'cash',
    status ENUM('pending','paid','refunded') DEFAULT 'pending',
    transaction_id VARCHAR(100),
    paid_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    position VARCHAR(100),
    department VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(120),
    salary DECIMAL(10,2),
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_department (department)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image_path VARCHAR(200),
    category VARCHAR(50) DEFAULT 'health',
    features TEXT,
    icon_class VARCHAR(50),
    INDEX idx_category (category)
) ENGINE=InnoDB;
INSERT IGNORE INTO room_types (name, description, base_price) VALUES
('Standard',     'Comfortable standard room with essential amenities',           2500.00),
('Deluxe',       'Spacious deluxe room with city view and premium facilities',   4500.00),
('Suite',        'Luxury suite with separate living area and premium amenities', 8000.00),
('Presidential', 'The pinnacle of luxury with private pool and butler service',  15000.00);

INSERT IGNORE INTO services (name, description, image_path, category, features, icon_class) VALUES
('Swimming Pool', 'Relax in our temperature-controlled outdoor pool with stunning views and comfortable lounging areas.', NULL, 'health', 'Temperature controlled,Outdoor pool,Lifeguard on duty,Poolside service', 'fas fa-swimmer'),
('Sauna & Steam Bath', 'Detoxify and relax in our traditional sauna and modern steam bath facilities.', NULL, 'health', 'Finnish sauna,Steam bath,Aromatherapy,Relaxation areas', 'fas fa-hot-tub'),
('Gym', 'Stay fit with our fully equipped fitness center featuring modern equipment and personal training options.', NULL, 'health', 'Cardio equipment,Free weights,Personal training,Group classes', 'fas fa-dumbbell'),
('Billiard', 'Enjoy recreational games in our billiard room with professional tables and a relaxed atmosphere.', NULL, 'health', 'Professional tables,Game instruction,Tournament hosting,Refreshment service', 'fas fa-table-tennis');

INSERT IGNORE INTO users (username, email, password_hash, full_name, phone, role) VALUES
('admin', 'admin@hotel.com', 
 'scrypt:32768:8:1$placeholder$hash_replace_with_generate_password_hash_admin123', 
 'Hotel Administrator', '01700000000', 'admin');

CREATE OR REPLACE VIEW v_booking_summary AS
SELECT 
    b.id AS booking_id, 
    u.full_name AS guest_name, 
    u.email AS guest_email, 
    r.room_number, 
    rt.name AS room_type, 
    b.check_in, b.check_out, 
    DATEDIFF(b.check_out, b.check_in) AS nights,
    b.guests, b.status, b.total_amount, 
    b.created_at
FROM bookings b
JOIN users u ON b.user_id = u.id
JOIN rooms r ON b.room_id = r.id
JOIN room_types rt ON r.room_type_id = rt.id;

CREATE OR REPLACE VIEW v_room_availability AS
SELECT 
    r.id, r.room_number, r.floor, r.status, r.capacity, 
    rt.name AS room_type, rt.base_price
FROM rooms r
JOIN room_types rt ON r.room_type_id = rt.id
ORDER BY r.floor, r.room_number;
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS GetAvailableRooms(
    IN p_check_in DATE,
    IN p_check_out DATE,
    IN p_guests INT
)
BEGIN
    SELECT r.id, r.room_number, r.floor, r.capacity, rt.name AS type, rt.base_price
    FROM rooms r
    JOIN room_types rt ON r.room_type_id = rt.id
    WHERE r.status = 'available'
      AND r.capacity >= p_guests
      AND r.id NOT IN (
          SELECT DISTINCT room_id FROM bookings
          WHERE status NOT IN ('cancelled', 'checked_out')
            AND check_in < p_check_out
            AND check_out > p_check_in
      )
    ORDER BY rt.base_price;
END //
DELIMITER ;