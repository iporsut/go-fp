package solution

type Cart struct {
	Email, Category string
	Total           int
}
type Coupon struct {
	Code, Category string
	MinimumTotal   int
}

// FindApplicableCoupons คืนคูปองตามลำดับเดิม หมวดว่างใช้ได้ทุกหมวด
func FindApplicableCoupons(cart Cart, coupons []Coupon) []Coupon {
	result := make([]Coupon, 0)
	for _, coupon := range coupons {
		if cart.Total >= coupon.MinimumTotal && (coupon.Category == "" || coupon.Category == cart.Category) {
			result = append(result, coupon)
		}
	}
	return result
}
