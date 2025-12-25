-- Создание таблиц для SQLAlchemy ORM
DROP TABLE IF EXISTS goods CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS tokens CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE tokens (
    id SERIAL PRIMARY KEY,
    value TEXT NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    is_valid BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE goods (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    count INTEGER NOT NULL,
    price NUMERIC(10, 2) NOT NULL
);

-- Индексы
CREATE INDEX idx_tokens_value ON tokens(value);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_goods_order_id ON goods(order_id);
