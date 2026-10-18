package pricing

import "fmt"

type productNotFoundError struct {
	sku string
}

func (e productNotFoundError) Error() string {
	return fmt.Sprintf("product %q not found", e.sku)
}
func ErrProductNotFound(sku string) error {
	return productNotFoundError{
		sku: sku,
	}
}

type invalidQuantityError struct {
	sku string
}

func (e invalidQuantityError) Error() string {
	return fmt.Sprintf("quantity for %q must be greater than zero", e.sku)
}
func ErrInvalidQuantity(sku string) error {
	return invalidQuantityError{
		sku: sku,
	}
}
