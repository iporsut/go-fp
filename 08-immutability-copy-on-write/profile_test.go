package immutability

import "testing"

func TestUpdates(t *testing.T) {
	original := Profile{Name: "Nok", Points: 10}
	updated := original.WithPoints(5)
	if original.Points != 10 || updated.Points != 15 || updated.Name != "Nok" {
		t.Fatalf("original=%+v updated=%+v", original, updated)
	}
	original.AddPoints(5)
	if original != updated {
		t.Fatalf("got %+v, want %+v", original, updated)
	}
}

var result Profile

func BenchmarkMutation(b *testing.B) {
	p := Profile{Name: "Nok"}
	b.ReportAllocs()
	for b.Loop() {
		p.AddPoints(1)
	}
	result = p
}

func BenchmarkCopyOnWrite(b *testing.B) {
	p := Profile{Name: "Nok"}
	b.ReportAllocs()
	for b.Loop() {
		p = p.WithPoints(1)
	}
	result = p
}
