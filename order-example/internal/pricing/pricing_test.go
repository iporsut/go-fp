package pricing

import (
	"example.com/checkout-pricing-api/internal/order"
	"testing"
)

func TestSubtotalAndTaxForRealCheckout(t *testing.T) {
	products := map[string]order.Product{
		"coffee": {
			SKU:            "coffee",
			UnitPriceCents: 1299,
		},
		"filter": {
			SKU:            "filter",
			UnitPriceCents: 799,
		},
	}
	subtotal, err := Subtotal([]order.OrderItem{
		{
			SKU:      "coffee",
			Quantity: 2,
		},
		{
			SKU:      "filter",
			Quantity: 1,
		},
	}, products)
	if err != nil {
		t.Fatal(err)
	}
	if subtotal != 3397 {
		t.Fatalf("subtotal = %d, want 3397", subtotal)
	}
	if got := Tax(subtotal, 500); got != 283 {
		t.Fatalf("tax = %d, want 283", got)
	}
	if got := Total(subtotal, 500, 283); got != 4180 {
		t.Fatalf("total = %d, want 4180", got)
	}
}

func TestSubtotalRejectsUnknownProduct(t *testing.T) {
	_, err := Subtotal([]order.OrderItem{
		{
			SKU:      "missing",
			Quantity: 1,
		},
	}, map[string]order.Product{})
	if err == nil {
		t.Fatal("expected unknown product error")
	}
}
