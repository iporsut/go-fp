package api

import (
	"database/sql"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestWriteHTTPError(t *testing.T) {
	for _, tc := range []struct {
		name   string
		err    error
		status int
		body   string
	}{
		{
			name:   "wrapped missing order",
			err:    fmt.Errorf("load order: %w", sql.ErrNoRows),
			status: http.StatusNotFound,
			body:   "{\"error\":\"order not found\"}\n",
		},
		{
			name:   "internal details stay private",
			err:    errors.New("database password=secret"),
			status: http.StatusInternalServerError,
			body:   "{\"error\":\"could not load order\"}\n",
		},
	} {
		t.Run(tc.name, func(t *testing.T) {
			response := httptest.NewRecorder()
			writeHTTPError(response, tc.err, "could not load order")
			if response.Code != tc.status || response.Body.String() != tc.body {
				t.Fatalf("unexpected response: %d %s", response.Code, response.Body)
			}
			if response.Header().Get("Content-Type") != "application/json" {
				t.Fatal("expected JSON content type")
			}
		})
	}
}
