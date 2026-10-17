package solution

import (
	"fmt"
	"io"
)

// SendCouponEmail เป็น action บาง ๆ ใช้ writer แทนระบบส่งอีเมลจริง
// ผู้เรียกคำนวณคูปองก่อน แล้วค่อยส่งเข้ามาที่ขอบเขตนี้
func SendCouponEmail(out io.Writer, email string, coupons []Coupon) error {
	codes := make([]string, 0, len(coupons))
	for _, coupon := range coupons {
		codes = append(codes, coupon.Code)
	}
	_, err := fmt.Fprintf(out, "To: %s\nCoupons: %v\n", email, codes)
	return err
}
