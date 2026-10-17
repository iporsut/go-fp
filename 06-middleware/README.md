# Middleware — ตัดได้เมื่อเวลาไม่พอ (cuttable)

แสดงการประกอบฟังก์ชันด้วย `Chain(Logger(logger), Recover)(handler)` ตัวแรกอยู่ชั้นนอกสุด ลองทำนายลำดับก่อนอ่านเทสต์

ส่วนนี้เป็น Actions: รับ request, เขียน response และ log การใช้ higher-order function ไม่ได้ทำให้โค้ดเป็น pure โดยอัตโนมัติ

`Recover` เป็นตัวอย่างสั้น: หากเขียน response ไปแล้ว จะเปลี่ยนสถานะเป็น 500 ไม่ได้ และจับ panic ได้เฉพาะ goroutine เดียวกัน
