//go:build ignore

package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func main() {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {

	})
}

func CreateAuthenticateMiddleware(authClient AuthClient) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Authentication logic here
		authHeader := c.GetHeader("Authorization")

		if authHeader == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "missing authorization header"})
			return
		}

		user, err := authClient.Authenticate(authHeader)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid token"})
			return
		}

		c.Set("user", user)
		c.Next()
	}
}
