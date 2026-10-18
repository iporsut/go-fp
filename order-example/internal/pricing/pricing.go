package pricing

import "example.com/checkout-pricing-api/internal/order"

const taxRateBPS int64 = 725 // 7.25%, represented as basis points.

func Subtotal(items []order.OrderItem, products map[string]order.Product) (int64, error) {
	var subtotal int64
	for _, item := range items {
		product, ok := products[item.SKU]
		if !ok {
			return 0, ErrProductNotFound(item.SKU)
		}
		if item.Quantity <= 0 {
			return 0, ErrInvalidQuantity(item.SKU)
		}
		subtotal += product.UnitPriceCents * int64(item.Quantity)
	}
	return subtotal, nil
}

func Tax(subtotalCents, shippingCents int64) int64 {
	// Tax applies to merchandise and shipping, rounded half-up to cents.
	taxable := subtotalCents + shippingCents
	return (taxable*taxRateBPS + 5000) / 10000
}

func Total(subtotalCents, shippingCents, taxCents int64) int64 {
	return subtotalCents + shippingCents + taxCents
}
