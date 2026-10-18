//go:build ignore

package main

import "fmt"

var operators = map[string]func(int, int) int{
	"+": func(a, b int) int { return a + b },
	"-": func(a, b int) int { return a - b },
	"*": func(a, b int) int { return a * b },
	"/": func(a, b int) int { return a / b },
}

func calculate(operator string, operator1, operator2 int) int {
	if op, exists := operators[operator]; exists {
		return op(operator1, operator2)
	}
	return 0
}

func main() {
	fmt.Println(calculate("+", 1, 2)) // 3
	fmt.Println(calculate("-", 1, 2)) // -1
	fmt.Println(calculate("*", 1, 2)) // 2
	fmt.Println(calculate("/", 1, 2)) // 0
}
