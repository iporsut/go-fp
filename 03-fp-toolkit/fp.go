// Package fp รวมเครื่องมือแปลงข้อมูลแบบ eager โดยไม่แก้ slice ต้นฉบับ
package fp

func Map[T, R any](items []T, transform func(T) R) []R {
	result := make([]R, 0, len(items))
	for _, item := range items {
		result = append(result, transform(item))
	}
	return result
}

func Filter[T any](items []T, keep func(T) bool) []T {
	result := make([]T, 0)
	for _, item := range items {
		if keep(item) {
			result = append(result, item)
		}
	}
	return result
}

// Reduce ใช้ชนิดของตัวสะสมต่างจากชนิดของสมาชิกได้
func Reduce[T, R any](items []T, initial R, combine func(R, T) R) R {
	result := initial
	for _, item := range items {
		result = combine(result, item)
	}
	return result
}

func Find[T any](items []T, match func(T) bool) (T, bool) {
	for _, item := range items {
		if match(item) {
			return item, true
		}
	}
	var zero T
	return zero, false
}

func GroupBy[T any, K comparable](items []T, key func(T) K) map[K][]T {
	result := make(map[K][]T)
	for _, item := range items {
		k := key(item)
		result[k] = append(result[k], item)
	}
	return result
}
