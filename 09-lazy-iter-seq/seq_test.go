package lazy

import (
	"iter"
	"slices"
	"testing"
)

func TestFibonacci(t *testing.T) {
	seq := Take(8, Fibonacci())
	want := []int{0, 1, 1, 2, 3, 5, 8, 13}
	for range 2 {
		if got := slices.Collect(seq); !slices.Equal(got, want) {
			t.Fatalf("got %v", got)
		}
	}
}

func TestFilter(t *testing.T) {
	for _, tc := range []struct {
		name        string
		input, want []int
	}{
		{"empty", nil, nil}, {"none", []int{1, 3}, nil},
		{"all", []int{2, 4}, []int{2, 4}}, {"mixed", []int{1, 2, 3, 4}, []int{2, 4}},
	} {
		t.Run(tc.name, func(t *testing.T) {
			got := slices.Collect(Filter(slices.Values(tc.input), func(n int) bool { return n%2 == 0 }))
			if !slices.Equal(got, tc.want) {
				t.Fatalf("got %v, want %v", got, tc.want)
			}
		})
	}
}

func TestTake(t *testing.T) {
	for _, tc := range []struct {
		n    int
		want []int
	}{
		{-1, nil}, {0, nil}, {1, []int{1}}, {3, []int{1, 2, 3}}, {5, []int{1, 2, 3}},
	} {
		got := slices.Collect(Take(tc.n, slices.Values([]int{1, 2, 3})))
		if !slices.Equal(got, tc.want) {
			t.Fatalf("n=%d: got %v, want %v", tc.n, got, tc.want)
		}
	}
}

func TestLazyAndEarlyStop(t *testing.T) {
	for _, tc := range []struct {
		name      string
		limit     int
		stopEarly bool
		reads     int
	}{
		{"negative", -1, false, 0}, {"zero", 0, false, 0},
		{"take two", 2, false, 4}, {"consumer breaks", 10, true, 2},
	} {
		t.Run(tc.name, func(t *testing.T) {
			reads := 0
			source := iter.Seq[int](func(yield func(int) bool) {
				for n := 1; ; n++ {
					reads++
					if !yield(n) {
						return
					}
				}
			})
			seq := Take(tc.limit, Filter(source, func(n int) bool { return n%2 == 0 }))
			if reads != 0 {
				t.Fatal("source read before iteration")
			}
			for range seq {
				if tc.stopEarly {
					break
				}
			}
			if reads != tc.reads {
				t.Fatalf("reads=%d, want %d", reads, tc.reads)
			}
		})
	}
}

func TestSumEvenFibonacci(t *testing.T) {
	// นับศูนย์เป็นเลขคู่ตัวแรก: 0, 2, 8, 34, 144, 610, 2584, 10946, 46368, 196418
	if got := SumEvenFibonacci(); got != 257114 {
		t.Fatalf("got %d", got)
	}
}
