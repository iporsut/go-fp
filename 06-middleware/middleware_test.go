package middleware

import (
	"bytes"
	"log"
	"net/http"
	"net/http/httptest"
	"reflect"
	"strings"
	"testing"
)

func TestMiddleware(t *testing.T) {
	for _, tc := range []struct {
		name   string
		panic  bool
		status int
		body   string
	}{
		{"normal", false, 200, "ok"}, {"panic", true, 500, "internal server error\n"},
	} {
		t.Run(tc.name, func(t *testing.T) {
			var logs bytes.Buffer
			handler := Chain(Logger(log.New(&logs, "", 0)), Recover)(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				if tc.panic {
					panic("private detail")
				}
				_, _ = w.Write([]byte("ok"))
			}))
			response := httptest.NewRecorder()
			handler.ServeHTTP(response, httptest.NewRequest("GET", "/orders", nil))
			if response.Code != tc.status || response.Body.String() != tc.body {
				t.Fatalf("got %d %q", response.Code, response.Body.String())
			}
			if !strings.Contains(logs.String(), "GET /orders") {
				t.Fatal("missing log")
			}
		})
	}
}

func TestChainOrder(t *testing.T) {
	var calls []string
	wrap := func(name string) func(http.Handler) http.Handler {
		return func(next http.Handler) http.Handler {
			return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				calls = append(calls, name+" before")
				next.ServeHTTP(w, r)
				calls = append(calls, name+" after")
			})
		}
	}
	handler := Chain(wrap("a"), wrap("b"))(http.HandlerFunc(func(http.ResponseWriter, *http.Request) { calls = append(calls, "handler") }))
	handler.ServeHTTP(httptest.NewRecorder(), httptest.NewRequest("GET", "/", nil))
	want := []string{"a before", "b before", "handler", "b after", "a after"}
	if !reflect.DeepEqual(calls, want) {
		t.Fatalf("got %v", calls)
	}
}

func TestEmptyChain(t *testing.T) {
	response := httptest.NewRecorder()
	Chain()(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { w.WriteHeader(204) })).ServeHTTP(response, httptest.NewRequest("GET", "/", nil))
	if response.Code != 204 {
		t.Fatal(response.Code)
	}
}

func TestRecoverPreservesAbort(t *testing.T) {
	defer func() {
		if got := recover(); got != http.ErrAbortHandler {
			t.Fatalf("panic = %v", got)
		}
	}()
	Recover(http.HandlerFunc(func(http.ResponseWriter, *http.Request) { panic(http.ErrAbortHandler) })).ServeHTTP(httptest.NewRecorder(), httptest.NewRequest("GET", "/", nil))
}
