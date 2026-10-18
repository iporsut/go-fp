package quote

import (
	"context"
	"fmt"

	"example.com/checkout-pricing-api/internal/order"
	"example.com/checkout-pricing-api/internal/pricing"
	"example.com/checkout-pricing-api/internal/shipping"
	"example.com/checkout-pricing-api/internal/store"
)

type CreateQuote struct {
	Orders   store.OrderRepository
	Shipping shipping.ShippingClient
}

func (a CreateQuote) Execute(ctx context.Context, orderID string) (order.Quote, error) {
	ord, err := a.Orders.Get(ctx, orderID)
	if err != nil {
		return order.Quote{}, fmt.Errorf("load order: %w", err)
	}
	skus := make([]string, 0, len(ord.Items))
	for _, item := range ord.Items {
		skus = append(skus, item.SKU)
	}
	products, err := a.Orders.ProductsBySKU(ctx, skus)
	if err != nil {
		return order.Quote{}, fmt.Errorf("load products: %w", err)
	}
	subtotal, err := pricing.Subtotal(ord.Items, products)
	if err != nil {
		return order.Quote{}, err
	}
	var weight int64
	for _, item := range ord.Items {
		weight += products[item.SKU].WeightGrams * int64(item.Quantity)
	}
	shipping, err := a.Shipping.Quote(ctx, ord.DestinationZIP, weight)
	if err != nil {
		return order.Quote{}, fmt.Errorf("get shipping quote: %w", err)
	}
	tax := pricing.Tax(subtotal, shipping.Cents)
	return order.Quote{
		OrderID:       ord.ID,
		SubtotalCents: subtotal,
		ShippingCents: shipping.Cents,
		TaxCents:      tax,
		TotalCents:    pricing.Total(subtotal, shipping.Cents, tax),
		Currency:      ord.Currency,
		Shipping:      shipping,
	}, nil
}
