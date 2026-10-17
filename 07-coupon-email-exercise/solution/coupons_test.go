package solution

import (
	"reflect"
	"slices"
	"testing"
)

func TestFindApplicableCoupons(t *testing.T) {
	book := Coupon{"BOOK", "books", 1000}
	all := Coupon{"ALL", "", 500}
	food := Coupon{"FOOD", "food", 0}
	for _, tc := range []struct {
		name          string
		cart          Cart
		coupons, want []Coupon
	}{
		{"nil", Cart{}, nil, []Coupon{}},
		{"empty", Cart{}, []Coupon{}, []Coupon{}},
		{"below threshold", Cart{Total: 499}, []Coupon{all}, []Coupon{}},
		{"exact threshold", Cart{Category: "books", Total: 1000}, []Coupon{book}, []Coupon{book}},
		{"above threshold", Cart{Category: "books", Total: 1001}, []Coupon{book}, []Coupon{book}},
		{"wrong category", Cart{Category: "books", Total: 1000}, []Coupon{food}, []Coupon{}},
		{"all categories", Cart{Category: "books", Total: 500}, []Coupon{all}, []Coupon{all}},
		{"empty cart category", Cart{Total: 1000}, []Coupon{book, all}, []Coupon{all}},
		{"order and duplicates", Cart{Category: "books", Total: 1000}, []Coupon{book, food, all, book}, []Coupon{book, all, book}},
	} {
		t.Run(tc.name, func(t *testing.T) {
			before := slices.Clone(tc.coupons)
			got := FindApplicableCoupons(tc.cart, tc.coupons)
			if !reflect.DeepEqual(got, tc.want) {
				t.Fatalf("got %v, want %v", got, tc.want)
			}
			if again := FindApplicableCoupons(tc.cart, tc.coupons); !reflect.DeepEqual(got, again) {
				t.Fatal("result changed")
			}
			if !reflect.DeepEqual(tc.coupons, before) {
				t.Fatal("input changed")
			}
			if len(got) > 0 {
				got[0].Code = "CHANGED"
				if !reflect.DeepEqual(tc.coupons, before) {
					t.Fatal("result shares input storage")
				}
			}
		})
	}
}
