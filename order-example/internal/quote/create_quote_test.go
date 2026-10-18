package quote

import (
	"context"
	"example.com/checkout-pricing-api/internal/order"
	"testing"
)

type fakeOrders struct{}

func (fakeOrders) Get(context.Context, string) (order.Order, error) {
	return order.Order{
		ID:             "ord_123",
		Currency:       "USD",
		DestinationZIP: "94107",
		Items: []order.OrderItem{
			{
				SKU:      "coffee",
				Quantity: 2,
			},
		},
	}, nil
}
func (fakeOrders) ProductsBySKU(context.Context, []string) (map[string]order.Product, error) {
	return map[string]order.Product{
		"coffee": {
			SKU:            "coffee",
			UnitPriceCents: 1299,
			WeightGrams:    250,
		},
	}, nil
}

type fakeShipping struct{}

func (fakeShipping) Quote(context.Context, string, int64) (order.ShippingQuote, error) {
	return order.ShippingQuote{
		Provider: "ParcelPilot",
		Service:  "Ground",
		Cents:    500,
		ETA:      "2026-10-23",
	}, nil
}

func TestCreateQuoteOrchestratesDataCalculationAndThirdParty(t *testing.T) {
	quote, err := (CreateQuote{
		Orders:   fakeOrders{},
		Shipping: fakeShipping{},
	}).Execute(context.Background(), "ord_123")
	if err != nil {
		t.Fatal(err)
	}
	if quote.SubtotalCents != 2598 || quote.ShippingCents != 500 || quote.TaxCents != 225 || quote.TotalCents != 3323 {
		t.Fatalf("unexpected quote: %+v", quote)
	}
}
