# Functional Programming in Go — เวิร์กช็อป 2 ชั่วโมง

สำหรับนักพัฒนา Go ที่ทำงานจริง ใช้กรอบ **Actions / Calculations / Data** จาก *Grokking Simplicity* โดย Eric Normand เน้นแยกงานที่มีผลกับภายนอกออกจากการคำนวณ ไม่เน้นทฤษฎีชนิดข้อมูล

- **Actions**: ผลขึ้นกับเวลาหรือจำนวนครั้งที่เรียก เช่น อ่านนาฬิกา ส่งอีเมล เขียน log และเปลี่ยนข้อมูลที่แชร์
- **Calculations**: input เดิมให้ output เดิม ไม่มีผลข้างเคียงที่สังเกตได้
- **Data**: ข้อเท็จจริงที่ส่งเข้าและคืนออก เช่น ตะกร้า คูปอง และยอดเงิน

| เวลา | โฟลเดอร์ | กิจกรรม |
| --- | --- | --- |
| 0:00–0:15 | [01-acd-opener](01-acd-opener/) | อ่านโค้ดที่ปนกัน แล้วจัดประเภทบนไวท์บอร์ด |
| 0:15–0:40 | [02-refactor-action-to-calc](02-refactor-action-to-calc/) | live refactor แยกส่วนลดและทดสอบด้วยตาราง |
| 0:40–1:05 | [03-fp-toolkit](03-fp-toolkit/), [04-closures-currying](04-closures-currying/) | HOF, generics, closures และ partial application |
| 1:05–1:25 | [05-functional-options](05-functional-options/), [06-middleware](06-middleware/) | ประกอบพฤติกรรมด้วยฟังก์ชัน; **middleware ตัดได้เมื่อเวลาไม่พอ** |
| 1:25–1:45 | [07-coupon-email-exercise](07-coupon-email-exercise/EXERCISE.md) | จับคู่แยกการเลือกคูปองออกจากการส่งอีเมล |
| 1:45–2:00 | [09-lazy-iter-seq](09-lazy-iter-seq/) | ปิดท้าย Fibonacci → Filter(even) → Take(10) → sum |
| Q&A สำรอง | [08-immutability-copy-on-write](08-immutability-copy-on-write/) | mutation, สำเนา struct และ benchmark |

ช่วง closing ใช้ 1:45–2:00 เพื่อไม่ทับกับ exercise ช่วง 1:25–1:45 และให้จบภายในสองชั่วโมง

## เตรียมเครื่องและตรวจสอบ

module ชื่อ `go-fp` ตั้ง Go **1.27.2** ใน `go.mod` ใช้ Go 1.27.2 ขึ้นไปสำหรับรันทั้ง repo โดย `iter` และ range-over-func ต้องใช้ **Go 1.23+** ส่วน benchmark ใช้ `testing.B.Loop` จาก Go 1.24

```sh
go version
go vet ./...
go test ./...
go run ./01-acd-opener
go test ./08-immutability-copy-on-write -run '^$' -bench . -benchmem
```

ทุกตัวอย่างใช้ standard library และไม่ต้องมีฐานข้อมูลหรือบริการอีเมลจริง โฟลเดอร์ 01 เป็น executable ที่มีไฟล์ตัวอย่าง Go หนึ่งไฟล์พร้อมไฟล์เทสต์ ส่วนอื่นเป็น package สำหรับอ่านและทดลองผ่านเทสต์

## แนวทางสอน

ให้ผู้เรียนทำนายผลก่อนรัน เริ่มจากเทสต์ของ 03 แล้วเขียนฟังก์ชันทีละตัว ชี้ว่า `Reduce[T, R]` ใช้ชนิดตัวสะสมต่างจากสมาชิกได้ และการมี closure หรือ generic ไม่ได้ทำให้ฟังก์ชัน pure โดยอัตโนมัติ callback เองก็อาจมีผลข้างเคียง

02 และ 07 ใช้เงินหน่วยบาทเต็มที่ไม่ติดลบเพื่อให้เห็นแนวคิดชัด 03 สร้าง slice ใหม่แต่ไม่ได้ deep copy สมาชิก 04 ใช้ loop variable ที่ประกาศด้วย `:=` ซึ่งแยกแต่ละรอบตั้งแต่ Go 1.22

09 สร้างลำดับเมื่อมีผู้เรียกอ่านเท่านั้น `Take` ส่งสัญญาณหยุดย้อนกลับถึงต้นทาง ผลรวมเลขคู่สิบตัวแรกนับศูนย์ด้วยคือ **257114** ตัวสร้างไม่มีจุดหยุดเอง แต่ `int` ยังมีขอบเขต จึงไม่ใช่เลข Fibonacci ขนาดไม่จำกัด
