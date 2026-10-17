package immutability

// Profile ใช้ฟิลด์แบบค่า จึงคัดลอกด้วย assignment ได้ครบ
// ถ้ามี slice, map หรือ pointer ต้องพิจารณาคัดลอกข้อมูลภายในด้วย
type Profile struct {
	Name   string
	Points int
}

func (p *Profile) AddPoints(points int) { p.Points += points }

// WithPoints คืนค่าใหม่โดยไม่เปลี่ยนผู้รับเดิม
func (p Profile) WithPoints(points int) Profile {
	p.Points += points
	return p
}
