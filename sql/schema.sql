CREATE DATABASE IF NOT EXISTS pregnancy_tracker
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE pregnancy_tracker;

CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    phone VARCHAR(20) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_profiles (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL UNIQUE,
    name VARCHAR(100) NULL,
    email VARCHAR(120) NULL UNIQUE,
    age INT NULL,
    city VARCHAR(100) NULL,
    height_cm DECIMAL(5,2) NULL,
    preferred_language VARCHAR(10) DEFAULT 'fr',
    theme VARCHAR(20) DEFAULT 'light',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_profiles_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pregnancy_profiles (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL UNIQUE,
    lmp_date DATE NOT NULL,
    due_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_pregnancy_profiles_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS appointments (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    type ENUM('consultation', 'analyse', 'echographie') NOT NULL,
    title VARCHAR(150) NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NULL,
    location VARCHAR(150) NULL,
    doctor_name VARCHAR(120) NULL,
    notes TEXT NULL,
    source ENUM('auto', 'manual') NOT NULL DEFAULT 'manual',
    status ENUM('planned', 'done', 'missed', 'postponed', 'cancelled') NOT NULL DEFAULT 'planned',
    gestational_week_target INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_appointments_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alerts (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL,
    category ENUM('blood_pressure', 'glucose', 'weight', 'fetal_movement', 'followup', 'system') NOT NULL,
    severity ENUM('info', 'warning', 'urgent') NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL DEFAULT NULL,
    CONSTRAINT fk_alerts_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_settings (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT UNSIGNED NOT NULL UNIQUE,
    notifications_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    reminder_2h_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    reminder_same_day_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    privacy_consent BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_settings_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);
