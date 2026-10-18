//go:build ignore

package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type Handler struct {
	srv *Service
}

func NewHandler(srv *Service) *Handler {
	return &Handler{srv: srv}
}

func (h *Handler) CreateOrder(c *gin.Context) {
}

func main() {
	e := gin.Default()
	srv := NewService()

	e.POST("/orders", createOrderHandler(srv))
	e.Run(":8080")
}

type Handler struct {
	srv *Service
}

func (h *Handler) handler(c *gin.Context) {
	// bind Order
	var order Order
	if err := c.ShouldBindJSON(&order); err != nil {
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}

	order, err := h.srv.CreateOrder(order)
	if err != nil {
		c.JSON(500, gin.H{"error": err.Error()})
		return
	}

	c.JSON(200, order)
}

func createOrderHandler(srv *Service) func(*gin.Context) {
	return func(c *gin.Context) {
		// bind Order
		var order Order
		if err := c.ShouldBindJSON(&order); err != nil {
			c.JSON(400, gin.H{"error": err.Error()})
			return
		}

		order, err := srv.CreateOrder(order)
		if err != nil {
			c.JSON(500, gin.H{"error": err.Error()})
			return
		}

		c.JSON(200, order)
	}

	// client := clintCallWithRetry(3, &http.Client{})
	// if err := client(func(d *Data) error {
	// 	// do something with d
	// 	return nil
	// }); err != nil {
	// 	// handle error
	// }
}

func clientCallWithRetry(times int, httpClient *http.Client) func(func(d *Data) error) error {
	return func(fn func(d *Data) error) error {
		var err error
		var resp *http.Response
		for i := 0; i < times; i++ {
			resp, err := httpClient.Do(nil) // call API
			if err != nil {
				continue
			}
			if resp.StatusCode == 200 {
				return nil
			}

			// unmarshal response body to Data
			var d Data
			// json.NewDecoder(resp.Body).Decode(&d) --- IGNORE ---
			err = fn(&d)
			if err == nil {
				return nil
			}
		}

		return err
	}
}
