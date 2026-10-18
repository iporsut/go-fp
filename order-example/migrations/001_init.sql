CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    destination_zip TEXT NOT NULL,
    currency CHAR(3) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id TEXT NOT NULL REFERENCES orders(id),
    sku TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (order_id, sku)
);

CREATE TABLE IF NOT EXISTS products (
    sku TEXT PRIMARY KEY,
    unit_price_cents BIGINT NOT NULL CHECK (unit_price_cents >= 0),
    weight_grams BIGINT NOT NULL CHECK (weight_grams >= 0)
);

INSERT INTO products (sku, unit_price_cents, weight_grams) VALUES
('coffee', 1299, 250), ('filter', 799, 100)
ON CONFLICT (sku) DO NOTHING;

INSERT INTO orders (id, customer_id, destination_zip, currency) VALUES
('ord_demo_001', 'cus_42', '94107', 'USD') ON CONFLICT (id) DO NOTHING;
INSERT INTO order_items (order_id, sku, quantity) VALUES
('ord_demo_001', 'coffee', 2), ('ord_demo_001', 'filter', 1)
ON CONFLICT (order_id, sku) DO NOTHING;
