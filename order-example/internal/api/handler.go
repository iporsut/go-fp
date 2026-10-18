package api

import (
	"context"
	"encoding/json"
	"net/http"

	"example.com/checkout-pricing-api/internal/order"
)

type QuoteCreator interface {
	Execute(context.Context, string) (order.Quote, error)
}

type OrderReader interface {
	Get(context.Context, string) (order.Order, error)
}

func NewHandler(creator QuoteCreator, orders OrderReader) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("POST /v1/orders/{order_id}/quote", func(w http.ResponseWriter, r *http.Request) {
		result, err := creator.Execute(r.Context(), r.PathValue("order_id"))
		if err != nil {
			writeHTTPError(w, err, "could not create quote")
			return
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(result)
	})
	mux.HandleFunc("GET /v1/orders/{order_id}", func(w http.ResponseWriter, r *http.Request) {
		result, err := orders.Get(r.Context(), r.PathValue("order_id"))
		if err != nil {
			writeHTTPError(w, err, "could not load order")
			return
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(result)
	})
	return mux
}
