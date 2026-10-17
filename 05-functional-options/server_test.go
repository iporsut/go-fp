package server

import (
	"testing"
	"time"
)

func TestNew(t *testing.T) {
	for _, tc := range []struct {
		name    string
		opts    []Option
		port    int
		timeout time.Duration
	}{
		{"defaults", nil, 8080, 5 * time.Second},
		{"port", []Option{WithPort(9000)}, 9000, 5 * time.Second},
		{"timeout", []Option{WithTimeout(time.Second)}, 8080, time.Second},
		{"both", []Option{WithPort(443), WithTimeout(2 * time.Second)}, 443, 2 * time.Second},
		{"last wins", []Option{WithPort(80), WithPort(443)}, 443, 5 * time.Second},
	} {
		t.Run(tc.name, func(t *testing.T) {
			got := New("localhost", tc.opts...)
			if got.Host != "localhost" || got.Port != tc.port || got.Timeout != tc.timeout {
				t.Fatalf("got %+v", got)
			}
		})
	}
}
