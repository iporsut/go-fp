package starter

import (
	"fmt"
	"io"
)

type Cart struct {
	Email, Category string
	Total           int
}
type Coupon struct {
	Code, Category string
	MinimumTotal   int
}

// EmailCoupons ใช้ writer จำลองระบบส่งอีเมล
func EmailCoupons(cart Cart, coupons []Coupon, out io.Writer) error {
	fmt.Printf("finding coupons for %s\n", cart.Email)
	var codes []string
	for _, coupon := range coupons {
		if cart.Total >= coupon.MinimumTotal && (coupon.Category == "" || coupon.Category == cart.Category) {
			codes = append(codes, coupon.Code)
		}
	}
	_, err := fmt.Fprintf(out, "To: %s\nCoupons: %v\n", cart.Email, codes)
	return err
}
