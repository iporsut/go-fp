package fp

import (
	"reflect"
	"strconv"
	"testing"
)

func TestMap(t *testing.T) {
	for _, tc := range []struct {
		name  string
		input []int
		want  []string
	}{
		{"nil", nil, []string{}}, {"empty", []int{}, []string{}},
		{"values", []int{2, -1, 2}, []string{"2", "-1", "2"}},
	} {
		t.Run(tc.name, func(t *testing.T) {
			if got := Map(tc.input, strconv.Itoa); !reflect.DeepEqual(got, tc.want) {
				t.Fatalf("got %v, want %v", got, tc.want)
			}
		})
	}
}

func TestFilter(t *testing.T) {
	for _, tc := range []struct {
		name        string
		input, want []int
	}{
		{"nil", nil, []int{}}, {"empty", []int{}, []int{}},
		{"none", []int{1, 3}, []int{}}, {"all", []int{2, 4}, []int{2, 4}},
		{"mixed", []int{3, 2, 4, 2}, []int{2, 4, 2}},
	} {
		t.Run(tc.name, func(t *testing.T) {
			got := Filter(tc.input, func(n int) bool { return n%2 == 0 })
			if !reflect.DeepEqual(got, tc.want) {
				t.Fatalf("got %v, want %v", got, tc.want)
			}
		})
	}
}

func TestReduce(t *testing.T) {
	for _, tc := range []struct {
		name          string
		input         []int
		initial, want string
	}{
		{"nil", nil, "start", "start"}, {"empty", []int{}, "", ""},
		{"ordered", []int{1, 2, 3}, "numbers:", "numbers:123"},
	} {
		t.Run(tc.name, func(t *testing.T) {
			got := Reduce(tc.input, tc.initial, func(acc string, n int) string { return acc + strconv.Itoa(n) })
			if got != tc.want {
				t.Fatalf("got %q, want %q", got, tc.want)
			}
		})
	}
}

func TestFind(t *testing.T) {
	for _, tc := range []struct {
		name  string
		input []int
		want  int
		ok    bool
	}{
		{"nil", nil, 0, false}, {"empty", []int{}, 0, false},
		{"missing", []int{1, 3}, 0, false}, {"first match", []int{1, 4, 2}, 4, true},
		{"zero is a match", []int{0, 2}, 0, true},
	} {
		t.Run(tc.name, func(t *testing.T) {
			got, ok := Find(tc.input, func(n int) bool { return n%2 == 0 })
			if got != tc.want || ok != tc.ok {
				t.Fatalf("got (%d, %v), want (%d, %v)", got, ok, tc.want, tc.ok)
			}
		})
	}
}

func TestGroupBy(t *testing.T) {
	for _, tc := range []struct {
		name  string
		input []string
		want  map[int][]string
	}{
		{"nil", nil, map[int][]string{}}, {"empty", []string{}, map[int][]string{}},
		{"groups preserve order", []string{"a", "go", "b", "a"}, map[int][]string{1: {"a", "b", "a"}, 2: {"go"}}},
	} {
		t.Run(tc.name, func(t *testing.T) {
			got := GroupBy(tc.input, func(s string) int { return len(s) })
			if !reflect.DeepEqual(got, tc.want) {
				t.Fatalf("got %v, want %v", got, tc.want)
			}
		})
	}
}

func TestResultsDoNotShareSliceStorage(t *testing.T) {
	input := []int{2, 4}
	mapped := Map(input, func(n int) int { return n })
	filtered := Filter(input, func(int) bool { return true })
	grouped := GroupBy(input, func(int) string { return "all" })
	mapped[0], filtered[0], grouped["all"][0] = 99, 99, 99
	if !reflect.DeepEqual(input, []int{2, 4}) {
		t.Fatal("input changed")
	}
	// สมาชิกที่เป็น pointer หรือมี slice ภายในยังต้องจัดการสำเนาเอง
}
