package main

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"os/signal"
	"syscall"
	"time"

	"example.com/checkout-pricing-api/internal/api"
	"example.com/checkout-pricing-api/internal/quote"
	"example.com/checkout-pricing-api/internal/shipping"
	"example.com/checkout-pricing-api/internal/store"
	_ "github.com/jackc/pgx/v5/stdlib"
)

func main() {
	if err := run(); err != nil {
		log.Fatal(err)
	}
}

func env(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}

func run() error {
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	shippingURL := env("SHIPPING_API_URL", "http://localhost:8081")
	u, err := url.Parse(shippingURL)
	if err != nil || (u.Scheme != "http" && u.Scheme != "https") || u.Host == "" {
		return fmt.Errorf("SHIPPING_API_URL must be an absolute HTTP(S) URL")
	}
	db, err := sql.Open("pgx", env("DATABASE_URL", "postgres://app:app@localhost:5432/checkout?sslmode=disable"))
	if err != nil {
		return fmt.Errorf("open database: %w", err)
	}
	defer db.Close()
	pingCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	if err := db.PingContext(pingCtx); err != nil {
		return fmt.Errorf("connect to PostgreSQL (start it with docker compose up -d postgres): %w", err)
	}
	orders := store.NewPostgresOrderRepository(db)
	handler := api.NewHandler(quote.CreateQuote{
		Orders:   orders,
		Shipping: shipping.DefaultHTTPShippingClient(shippingURL),
	}, orders)
	server := &http.Server{
		Addr:              env("HTTP_ADDR", ":8080"),
		Handler:           handler,
		ReadHeaderTimeout: 5 * time.Second,
		WriteTimeout:      10 * time.Second,
		IdleTimeout:       60 * time.Second,
	}
	done := make(chan error, 1)
	go func() {
		done <- server.ListenAndServe()
	}()
	log.Printf("checkout API listening on %s", server.Addr)
	select {
	case err := <-done:
		if !errors.Is(err, http.ErrServerClosed) {
			return err
		}
		return nil
	case <-ctx.Done():
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		return server.Shutdown(shutdownCtx)
	}
}
