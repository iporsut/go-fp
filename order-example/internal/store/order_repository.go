package store

import (
	"context"
	"database/sql"
	"fmt"

	"example.com/checkout-pricing-api/internal/order"
)

type OrderRepository interface {
	Get(ctx context.Context, id string) (order.Order, error)
	ProductsBySKU(ctx context.Context, skus []string) (map[string]order.Product, error)
}

type PostgresOrderRepository struct {
	db *sql.DB
}

func NewPostgresOrderRepository(db *sql.DB) *PostgresOrderRepository {
	return &PostgresOrderRepository{
		db: db,
	}
}

func (r *PostgresOrderRepository) Get(ctx context.Context, id string) (order.Order, error) {
	var ord order.Order
	err := r.db.QueryRowContext(ctx, `SELECT id, customer_id, destination_zip, currency, created_at FROM orders WHERE id = $1`, id).
		Scan(&ord.ID, &ord.CustomerID, &ord.DestinationZIP, &ord.Currency, &ord.CreatedAt)
	if err != nil {
		return order.Order{}, fmt.Errorf("get order: %w", err)
	}
	rows, err := r.db.QueryContext(ctx, `SELECT sku, quantity FROM order_items WHERE order_id = $1 ORDER BY sku`, id)
	if err != nil {
		return order.Order{}, fmt.Errorf("get order items: %w", err)
	}
	defer rows.Close()
	for rows.Next() {
		var item order.OrderItem
		if err := rows.Scan(&item.SKU, &item.Quantity); err != nil {
			return order.Order{}, fmt.Errorf("scan order item: %w", err)
		}
		ord.Items = append(ord.Items, item)
	}
	return ord, rows.Err()
}

func (r *PostgresOrderRepository) ProductsBySKU(ctx context.Context, skus []string) (map[string]order.Product, error) {
	products := make(map[string]order.Product, len(skus))
	for _, sku := range skus {
		var p order.Product
		if err := r.db.QueryRowContext(ctx, `SELECT sku, unit_price_cents, weight_grams FROM products WHERE sku = $1`, sku).
			Scan(&p.SKU, &p.UnitPriceCents, &p.WeightGrams); err != nil {
			if err == sql.ErrNoRows {
				continue
			}
			return nil, fmt.Errorf("get product %s: %w", sku, err)
		}
		products[p.SKU] = p
	}
	return products, nil
}
