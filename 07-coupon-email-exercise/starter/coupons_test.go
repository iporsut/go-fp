package starter

import (
	"bytes"
	"errors"
	"testing"
)

func TestEmailCoupons(t *testing.T) {
	var out bytes.Buffer
	err := EmailCoupons(Cart{"test@example.com", "books", 1000}, []Coupon{
		{"BOOK", "books", 1000}, {"FOOD", "food", 0}, {"VIP", "", 2000},
	}, &out)
	if err != nil {
		t.Fatal(err)
	}
	if got, want := out.String(), "To: test@example.com\nCoupons: [BOOK]\n"; got != want {
		t.Fatalf("got %q, want %q", got, want)
	}
}

type failingWriter struct{ err error }

func (w failingWriter) Write([]byte) (int, error) { return 0, w.err }

func TestEmailFailure(t *testing.T) {
	want := errors.New("mail unavailable")
	if err := EmailCoupons(Cart{}, nil, failingWriter{want}); !errors.Is(err, want) {
		t.Fatal(err)
	}
}
