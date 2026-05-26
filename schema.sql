-- =====================================
-- ZAYN RESORT DATABASE SCHEMA
-- =====================================


-- CUSTOMERS

CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR NOT NULL,
    date_of_birth DATE NOT NULL,
    cpf VARCHAR NOT NULL,
    newsletter_opt_in BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);


--RESERVATIONS

CREATE TABLE reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    room_id UUID NOT NULL REFERENCES rooms(id),
    check_in_at TIMESTAMP NOT NULL,
    check_out_at TIMESTAMP NOT NULL,
    status SMALLINT NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);


--ROOM CATEGORY

CREATE TABLE room_category (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    capacity INTEGER NOT NULL,
    daily_rate NUMERIC NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);


--ROOMS

CREATE TABLE rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    room_category_id UUID NOT NULL REFERENCES room_category(id),
    description VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);