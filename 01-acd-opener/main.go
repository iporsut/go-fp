// ให้ผู้สอนอ่านโค้ดร่วมกับผู้เรียน แล้วจัดประเภทแต่ละบรรทัดบนไวท์บอร์ดก่อนเฉลย
package main

import (
	"fmt"
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

func ProcessOrder(order *Order) {
	order.ProcessedAt = time.Now()
	fmt.Printf("processing order for %s at %s\n", order.Email, order.ProcessedAt)
	order.Total = 0
	for _, item := range order.Items {
		order.Total += item.Price * item.Quantity
	}
	if order.Total >= 1000 {
		order.Total = order.Total * 90 / 100
	}
	orders[order.Email] = *order
	fmt.Printf("saved order: %s, total=%d\n", order.Email, order.Total)
}

func main() {
	order := Order{Email: "learner@example.com", Items: []Item{{Price: 600, Quantity: 2}}}
	ProcessOrder(&order)
}
