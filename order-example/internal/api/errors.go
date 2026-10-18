package api

import (
	"database/sql"
	"encoding/json"
	"errors"
	"log"
	"net/http"
)

type errorResponse struct {
	Error string `json:"error"`
}

// mapHTTPError is a pure mapping: it does not log or write to the response.
func mapHTTPError(err error, fallback string) (int, errorResponse) {
	if errors.Is(err, sql.ErrNoRows) {
		return http.StatusNotFound, errorResponse{
			Error: "order not found",
		}
	}
	return http.StatusInternalServerError, errorResponse{
		Error: fallback,
	}
}

// writeHTTPError handles the HTTP effects and keeps internal details in logs.
func writeHTTPError(w http.ResponseWriter, err error, fallback string) {
	status, response := mapHTTPError(err, fallback)
	log.Printf("%s: %v", fallback, err)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(response)
}
