package lazy

import "iter"

// Fibonacci ไม่มีเงื่อนไขหยุดเอง ผู้บริโภคเป็นคนหยุด
// int มีขอบเขตและจะ overflow หากอ่านไกลเกินไป ตัวอย่างนี้ใช้เพียงช่วงต้น
func Fibonacci() iter.Seq[int] {
	return func(yield func(int) bool) {
		a, b := 0, 1
		for {
			if !yield(a) {
				return
			}
			a, b = b, a+b
		}
	}
}

func Filter[T any](seq iter.Seq[T], keep func(T) bool) iter.Seq[T] {
	return func(yield func(T) bool) {
		for value := range seq {
			if keep(value) && !yield(value) {
				return
			}
		}
	}
}

// Take ไม่อ่านต้นทางเลยเมื่อ n <= 0 และไม่อ่านเกินจำนวนที่ขอ
func Take[T any](n int, seq iter.Seq[T]) iter.Seq[T] {
	return func(yield func(T) bool) {
		if n <= 0 {
			return
		}
		count := 0
		for value := range seq {
			if !yield(value) {
				return
			}
			count++
			if count == n {
				return
			}
		}
	}
}

func SumEvenFibonacci() int {
	even := Filter(Fibonacci(), func(n int) bool { return n%2 == 0 })
	total := 0
	for n := range Take(10, even) {
		total += n
	}
	return total
}
