package order

import "time"

type OrderItem struct {
	SKU      string `json:"sku"`
	Quantity int    `json:"quantity"`
}

type Order struct {
	ID             string      `json:"id"`
	CustomerID     string      `json:"customer_id"`
	DestinationZIP string      `json:"destination_zip"`
	Currency       string      `json:"currency"`
	Items          []OrderItem `json:"items"`
	CreatedAt      time.Time   `json:"created_at"`
}

type Product struct {
	SKU            string
	UnitPriceCents int64
	WeightGrams    int64
}

type ShippingQuote struct {
	Provider string `json:"provider"`
	Service  string `json:"service"`
	Cents    int64  `json:"cents"`
	ETA      string `json:"eta"`
}

type Quote struct {
	OrderID       string        `json:"order_id"`
	SubtotalCents int64         `json:"subtotal_cents"`
	ShippingCents int64         `json:"shipping_cents"`
	TaxCents      int64         `json:"tax_cents"`
	TotalCents    int64         `json:"total_cents"`
	Currency      string        `json:"currency"`
	Shipping      ShippingQuote `json:"shipping"`
}
