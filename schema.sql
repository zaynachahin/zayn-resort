-- =====================================
-- ZAYN RESORT DATABASE SCHEMA
-- =====================================


-- CUSTOMERS

CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    cpf VARCHAR(11) NOT NULL UNIQUE,
    newsletter_opt_in BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);


--ROOM CATEGORY

CREATE TABLE room_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    capacity INTEGER NOT NULL,
    daily_rate NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE UNIQUE INDEX room_categories_name_active_unique
ON room_categories (name)
WHERE deleted_at IS NULL;


--ROOMS

CREATE TABLE rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    room_category_id UUID NOT NULL REFERENCES room_categories(id),
    description VARCHAR(500) NOT NULL,
    number VARCHAR(10) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);


--RESERVATIONS

CREATE TABLE reservations(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    room_id UUID NOT NULL REFERENCES rooms(id),
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'confirmed',
    total_amount NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);