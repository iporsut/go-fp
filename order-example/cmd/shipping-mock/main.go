package main

import (
	"encoding/json"
	"log"
	"net/http"
	"strconv"
)

type quote struct {
	Provider   string `json:"provider"`
	Service    string `json:"service"`
	PriceCents int64  `json:"price_cents"`
	ETA        string `json:"eta"`
}

func main() {
	http.HandleFunc("/v1/quotes", func(w http.ResponseWriter, r *http.Request) {
		weight, _ := strconv.ParseInt(r.URL.Query().Get("weight_grams"), 10, 64)
		price := int64(500)
		if weight > 1000 {
			price += 250
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(quote{
			Provider:   "ParcelPilot",
			Service:    "Ground",
			PriceCents: price,
			ETA:        "2026-10-23",
		})
	})
	log.Println("mock shipping provider listening on :8081")
	log.Fatal(http.ListenAndServe(":8081", nil))
}
