package shipping

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"

	"example.com/checkout-pricing-api/internal/order"
)

type ShippingClient interface {
	Quote(ctx context.Context, destinationZIP string, totalWeightGrams int64) (order.ShippingQuote, error)
}

type HTTPShippingClient struct {
	BaseURL string
	Client  *http.Client
}

type shippingResponse struct {
	Provider   string `json:"provider"`
	Service    string `json:"service"`
	PriceCents int64  `json:"price_cents"`
	ETA        string `json:"eta"`
}

func (c *HTTPShippingClient) Quote(ctx context.Context, destinationZIP string, totalWeightGrams int64) (order.ShippingQuote, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, strings.TrimRight(c.BaseURL, "/")+"/v1/quotes?"+url.Values{
		"destination_zip": {
			destinationZIP,
		},
		"weight_grams": {
			strconv.FormatInt(totalWeightGrams, 10),
		},
	}.Encode(), nil)
	if err != nil {
		return order.ShippingQuote{}, fmt.Errorf("build shipping request: %w", err)
	}
	resp, err := c.Client.Do(req)
	if err != nil {
		return order.ShippingQuote{}, fmt.Errorf("shipping provider request: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return order.ShippingQuote{}, fmt.Errorf("shipping provider returned %s", resp.Status)
	}
	var payload shippingResponse
	if err := json.NewDecoder(resp.Body).Decode(&payload); err != nil {
		return order.ShippingQuote{}, fmt.Errorf("decode shipping response: %w", err)
	}
	return order.ShippingQuote{
		Provider: payload.Provider,
		Service:  payload.Service,
		Cents:    payload.PriceCents,
		ETA:      payload.ETA,
	}, nil
}

func DefaultHTTPShippingClient(baseURL string) *HTTPShippingClient {
	return &HTTPShippingClient{
		BaseURL: baseURL,
		Client: &http.Client{
			Timeout: 2 * time.Second,
		},
	}
}
