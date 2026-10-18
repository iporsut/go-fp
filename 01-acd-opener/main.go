package main

import (
	"time"
)

type Item struct{ Price, Quantity int }
type Order struct {
	Email       string
	Items       []Item
	Total       int
	ProcessedAt time.Time
}

var orders = map[string]Order{}

func ProcessOrder(order Order, processedAt time.Time) Order {
	order.ProcessedAt = processedAt
	order.Total = ApplyDiscount(SubTotal(order.Items))
	return order
}

func SubTotal(items []Item) int {
	total := 0
	for _, item := range items {
		total += item.Price * item.Quantity
	}
	return total
}

func ApplyDiscount(total int) int {
	if total >= 1000 {
		return total * 90 / 100
	}
	return total
}

func main() {
	order := Order{Email: "learner@example.com", Items: []Item{{Price: 600, Quantity: 2}}}
	order = ProcessOrder(order, time.Now())
	orders[order.Email] = order
}
