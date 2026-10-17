# สำรองสำหรับ Q&A: mutation กับ copy-on-write

`AddPoints` เปลี่ยนผู้รับเดิม ส่วน `WithPoints` ใช้ value receiver และคืน struct ใหม่ ทำให้ผู้เรียกเก็บค่าเดิมได้ ทั้งสองแบบเพิ่มแต้มเท่ากัน

```sh
go test ./08-immutability-copy-on-write -run '^$' -bench . -benchmem
```

struct เล็กที่มีแต่ฟิลด์แบบค่าอาจคัดลอกได้ถูกมาก และ compiler อาจลดต้นทุนได้ จึงควรวัดจริงแทนการเดา benchmark นี้วัดเฉพาะ struct เล็ก ไม่ใช่ข้อสรุปสำหรับระบบทั้งหมด

ข้อมูลใหญ่หรือ nested slice/map อาจมีต้นทุนคัดลอกและ allocation เพิ่ม สำเนา struct เป็น shallow copy: slice/map/pointer ยังแชร์ข้อมูลภายใน string แชร์หน่วยความจำได้เพราะแก้เนื้อหาไม่ได้ เลือก mutation ภายในขอบเขตที่ควบคุมได้ แล้วคืนข้อมูลที่ผู้เรียกใช้ได้อย่างปลอดภัย

benchmark ใช้ `testing.B.Loop` ซึ่งเริ่มมีใน Go 1.24; repo นี้ใช้ Go 1.27.2
