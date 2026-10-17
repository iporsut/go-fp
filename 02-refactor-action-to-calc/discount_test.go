package discount

import (
	"errors"
	"reflect"
	"testing"
)

func TestDiscounted(t *testing.T) {
	for _, tc := range []struct {
		name        string
		total, want int
	}{
		{"empty", 0, 0}, {"below threshold", 999, 999},
		{"threshold", 1000, 900}, {"round down", 1001, 900}, {"large", 2000, 1800},
	} {
		t.Run(tc.name, func(t *testing.T) {
			if got := Discounted(tc.total); got != tc.want {
				t.Fatalf("got %d, want %d", got, tc.want)
			}
		})
	}
}

func TestApplyDiscountChangesCaller(t *testing.T) {
	cart := Cart{Prices: []int{600, 600}}
	ApplyDiscount(cart)
	// ต้องรู้เรื่องข้อมูลร่วมกัน และการเรียกยังพิมพ์ log ระหว่างทดสอบ
	if cart.Prices[0] != 540 {
		t.Fatal("expected caller's slice to change")
	}
	ApplyDiscount(cart)
	if cart.Prices[0] != 486 {
		t.Fatal("repeating the action changes the result again")
	}
}

func TestProcessOrder(t *testing.T) {
	cart := Cart{Prices: []int{600, 600}}
	wantErr := errors.New("storage unavailable")
	calls := 0
	err := ProcessOrder(cart, func(total int) error {
		calls++
		if total != 1080 {
			t.Errorf("total = %d", total)
		}
		return wantErr
	})
	if !errors.Is(err, wantErr) || calls != 1 {
		t.Fatalf("calls=%d, err=%v", calls, err)
	}
	if !reflect.DeepEqual(cart.Prices, []int{600, 600}) {
		t.Fatal("input changed")
	}
}
