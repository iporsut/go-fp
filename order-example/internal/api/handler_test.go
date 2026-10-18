package api

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"example.com/checkout-pricing-api/internal/order"
	"example.com/checkout-pricing-api/internal/quote"
	"example.com/checkout-pricing-api/internal/shipping"
)

type testOrders struct{}

func (testOrders) Get(_ context.Context, id string) (order.Order, error) {
	if id == "missing" {
		return order.Order{}, fmt.Errorf("load: %w", sql.ErrNoRows)
	}
	return order.Order{
		ID:             id,
		Currency:       "USD",
		DestinationZIP: "94107",
		Items: []order.OrderItem{
			{
				SKU:      "coffee",
				Quantity: 2,
			},
			{
				SKU:      "filter",
				Quantity: 1,
			},
		},
	}, nil
}
func (testOrders) ProductsBySKU(context.Context, []string) (map[string]order.Product, error) {
	return map[string]order.Product{
		"coffee": {
			UnitPriceCents: 1299,
			WeightGrams:    250,
		},
		"filter": {
			UnitPriceCents: 799,
			WeightGrams:    100,
		},
	}, nil
}
func TestQuoteHTTPFlow(t *testing.T) {
	provider := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/v1/quotes" || r.URL.Query().Get("weight_grams") != "600" || r.URL.Query().Get("destination_zip") != "94107" {
			t.Errorf("unexpected provider request: %s", r.URL)
		}
		fmt.Fprint(w, `{"provider":"ParcelPilot","service":"Ground","price_cents":500,"eta":"2026-10-23"}`)
	}))
	defer provider.Close()
	handler := NewHandler(quote.CreateQuote{
		Orders:   testOrders{},
		Shipping: shipping.DefaultHTTPShippingClient(provider.URL),
	}, testOrders{})
	t.Run("success", func(t *testing.T) {
		response := httptest.NewRecorder()
		handler.ServeHTTP(response, httptest.NewRequest(http.MethodPost, "/v1/orders/ord_demo_001/quote", nil))
		if response.Code != 200 {
			t.Fatalf("status %d: %s", response.Code, response.Body)
		}
		var result struct {
			Total    int64          `json:"total_cents"`
			Shipping map[string]any `json:"shipping"`
		}
		if err := json.Unmarshal(response.Body.Bytes(), &result); err != nil {
			t.Fatal(err)
		}
		if result.Total != 4180 || result.Shipping["cents"] != float64(500) || result.Shipping["provider"] != "ParcelPilot" {
			t.Fatalf("unexpected response: %s", response.Body)
		}
	})
	for _, tc := range []struct {
		method, path string
		status       int
	}{
		{
			"POST",
			"/v1/orders/missing/quote",
			404,
		},
		{
			"GET",
			"/v1/orders/ord_demo_001/quote",
			405,
		},
		{
			"POST",
			"/unknown",
			404,
		},
	} {
		t.Run(tc.method+tc.path, func(t *testing.T) {
			response := httptest.NewRecorder()
			handler.ServeHTTP(response, httptest.NewRequest(tc.method, tc.path, nil))
			if response.Code != tc.status {
				t.Fatalf("status %d, want %d", response.Code, tc.status)
			}
		})
	}
	t.Run("provider failure", func(t *testing.T) {
		provider.Close()
		response := httptest.NewRecorder()
		handler.ServeHTTP(response, httptest.NewRequest("POST", "/v1/orders/ord_demo_001/quote", nil))
		if response.Code != 500 {
			t.Fatalf("status %d", response.Code)
		}
	})
}

func TestGetOrder(t *testing.T) {
	handler := NewHandler(nil, testOrders{})
	response := httptest.NewRecorder()
	handler.ServeHTTP(response, httptest.NewRequest(http.MethodGet, "/v1/orders/ord_demo_001", nil))
	if response.Code != http.StatusOK {
		t.Fatalf("status %d: %s", response.Code, response.Body)
	}
	var result struct {
		ID    string            `json:"id"`
		Items []order.OrderItem `json:"items"`
	}
	if err := json.Unmarshal(response.Body.Bytes(), &result); err != nil {
		t.Fatal(err)
	}
	if result.ID != "ord_demo_001" || len(result.Items) != 2 {
		t.Fatalf("unexpected order: %+v", result)
	}
	response = httptest.NewRecorder()
	handler.ServeHTTP(response, httptest.NewRequest(http.MethodGet, "/v1/orders/missing", nil))
	if response.Code != http.StatusNotFound || response.Body.String() != "{\"error\":\"order not found\"}\n" {
		t.Fatalf("unexpected missing order response: %d %s", response.Code, response.Body)
	}
}
