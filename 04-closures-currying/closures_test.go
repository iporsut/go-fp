package closures

import (
	"fmt"
	"reflect"
	"slices"
	"testing"
)

func TestAdder(t *testing.T) {
	for _, tc := range []struct{ a, b, want int }{{2, 3, 5}, {-2, 2, 0}, {0, 4, 4}} {
		if got := Adder(tc.a)(tc.b); got != tc.want {
			t.Errorf("Adder(%d)(%d)=%d", tc.a, tc.b, got)
		}
	}
}

func TestCurry2(t *testing.T) {
	label := Curry2(func(prefix string, n int) string { return fmt.Sprintf("%s:%d", prefix, n) })
	itemLabel := label("item")
	for _, tc := range []struct {
		n    int
		want string
	}{{1, "item:1"}, {2, "item:2"}} {
		if got := itemLabel(tc.n); got != tc.want {
			t.Errorf("got %q, want %q", got, tc.want)
		}
	}
	if got := label("cart")(3); got != "cart:3" {
		t.Fatal(got)
	}
}

func TestCapturedIndices(t *testing.T) {
	for _, n := range []int{0, 1, 10} {
		got := CapturedIndices(n)
		slices.Sort(got)
		want := make([]int, n)
		for i := range n {
			want[i] = i
		}
		if !reflect.DeepEqual(got, want) {
			t.Fatalf("got %v, want %v", got, want)
		}
	}
}
