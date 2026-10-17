package closures

func Adder(a int) func(int) int {
	return func(b int) int { return a + b }
}

func Curry2[A, B, R any](f func(A, B) R) func(A) func(B) R {
	return func(a A) func(B) R {
		return func(b B) R { return f(a, b) }
	}
}

// CapturedIndices คืนค่าตามลำดับที่ goroutine ส่งมา จึงไม่รับประกันลำดับ
func CapturedIndices(n int) []int {
	values := make(chan int, n)
	for i := 0; i < n; i++ {
		// ตั้งแต่ Go 1.22 ตัวแปรที่ประกาศด้วย := ใน loop แยกแต่ละรอบ
		// ก่อน 1.22 ต้องทำสำเนา i หรือส่งเป็น argument เพื่อเลี่ยงการจับตัวแปรร่วม
		go func() { values <- i }()
	}
	result := make([]int, 0, n)
	for range n {
		result = append(result, <-values)
	}
	return result
}
