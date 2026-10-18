package server

import "time"

type Server struct {
	Host    string
	Port    int
	Timeout time.Duration
}

type Option func(*Server)

func WithPort(port int) Option {
	return func(s *Server) {
		s.Port = port
	}
}

func WithTimeout(timeout time.Duration) Option {
	return func(s *Server) {
		s.Timeout = timeout
	}
}

// New สร้างค่าเริ่มต้นก่อนใช้ options ตามลำดับที่รับมา
func New(host string, opts ...Option) *Server {
	s := &Server{Host: host, Port: 8080, Timeout: 5 * time.Second}
	for _, opt := range opts {
		opt(s)
	}
	return s
}

func main() {
	New("localhost",
		WithTimeout(10*time.Second),
		WithPort(9090),
	)
}
