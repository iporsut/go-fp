package discount

import "fmt"

// จำนวนเงินทั้งหมดใช้หน่วยบาทเต็มเพื่อให้ตัวอย่างสั้น
// slice ใน struct ยังอ้างถึงข้อมูลร่วมกันแม้ส่ง struct แบบ value
type Cart struct{ Prices []int }

func ApplyDiscount(cart Cart) Cart {
	total := Total(cart)
	fmt.Printf("cart total: %d\n", total)
	if total >= 1000 {
		for i := range cart.Prices {
			cart.Prices[i] = cart.Prices[i] * 90 / 100
		}
	}
	return cart
}

func Total(cart Cart) int {
	total := 0
	for _, price := range cart.Prices {
		total += price
	}
	return total
}

// Discounted คำนวณส่วนลดสิบเปอร์เซ็นต์และปัดเศษลงครั้งเดียวที่ยอดรวม
func Discounted(total int) int {
	if total >= 1000 {
		return total * 90 / 100
	}
	return total
}

// ProcessOrder เป็นขอบเขตของงานที่สื่อสารกับภายนอก
func ProcessOrder(cart Cart, save func(int) error) error {
	total := Discounted(Total(cart))
	fmt.Printf("discounted total: %d\n", total)
	return save(total)
}
