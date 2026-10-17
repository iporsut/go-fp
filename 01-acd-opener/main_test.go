package main

import "testing"

func TestProcessOrder(t *testing.T) {
	previous := orders
	orders = map[string]Order{}
	t.Cleanup(func() { orders = previous })
	order := Order{Email: "test@example.com", Items: []Item{{600, 2}}}
	ProcessOrder(&order)
	if order.Total != 1080 || order.ProcessedAt.IsZero() {
		t.Fatalf("unexpected order: %+v", order)
	}
	if orders[order.Email].Total != 1080 {
		t.Fatal("order was not saved")
	}
}
