# Checkout Pricing API — Action / Calculation / Data

ตัวอย่างงานจริงของทีม commerce: ลูกค้ากด checkout แล้วระบบต้องอ่าน order จาก PostgreSQL, คำนวณราคาอย่าง deterministic และไปขอค่าส่งจากผู้ให้บริการภายนอก ก่อนตอบยอดรวมกลับไป

## โครงสร้าง

ตั้งใจไม่ใช้ package แบบ generic ตาม layer เช่น `action`, `calculation`, `data`, `domain` เพราะชื่อเหล่านี้บอกโครงสร้างมากกว่าความหมายของโค้ด จึงใช้ชื่อ package แบบ idiomatic Go ที่สื่อ responsibility/domain แทน:

- `internal/order` — domain types: `Order`, `Product`, `Quote`
- `internal/quote` — use case ที่สร้าง checkout quote และเป็นจุด orchestration
- `internal/pricing` — pure pricing rules: subtotal/tax/total ทดสอบง่าย ไม่มี I/O
- `internal/store` — PostgreSQL repository และการ mapping จาก DB เป็น domain data
- `internal/shipping` — shipping client และ HTTP adapter สำหรับ ParcelPilot
- `internal/api` — HTTP transport: path/status/JSON เท่านั้น
- `migrations` — schema และ demo data

ชื่อ package ไม่ได้บอกว่าเป็น ACD ตรง ๆ แต่ responsibility ยังเป็น ACD เหมือนเดิม: `quote` คือ Action/use case, `pricing` คือ Calculation, `order` คือรูปแบบของ Data, ส่วน method ใน `store`, `shipping` และ `api` คือ Actions ที่เชื่อมกับโลกภายนอกและรับส่ง Data

## Run tests

```bash
go test ./...
```

## Run locally

ต้องมี Docker และ Docker Compose โดยเปิด Docker daemon ก่อน จากนั้นรันทั้ง PostgreSQL, shipping mock และ API:

```bash
docker compose up --build -d
curl --fail -X POST http://localhost:8080/v1/orders/ord_demo_001/quote
```

Compose จะรอให้ PostgreSQL และ shipping mock พร้อมก่อนเริ่ม API โดยโหลด schema และ demo data จาก `migrations/001_init.sql` อัตโนมัติเมื่อสร้างฐานข้อมูลครั้งแรก

ดู log และหยุดระบบ:

```bash
docker compose logs -f api
docker compose down
```

หากต้องการรัน Go บนเครื่อง (Go 1.22 ขึ้นไป):

```bash
docker compose up -d --wait postgres
go run ./cmd/shipping-mock        # terminal 1
go run ./cmd/api                  # terminal 2
curl --fail -X POST http://localhost:8080/v1/orders/ord_demo_001/quote
```

ค่าตั้งต้นสำหรับ local development (เปลี่ยนผ่าน environment variables ได้):

| Variable | Default |
| --- | --- |
| `DATABASE_URL` | `postgres://app:app@localhost:5432/checkout?sslmode=disable` |
| `SHIPPING_API_URL` | `http://localhost:8081` |
| `HTTP_ADDR` | `:8080` |

`cmd/shipping-mock` เป็น provider จำลอง ไม่ต้องมีบัญชีผู้ให้บริการจริง และฟังที่ port 8081 ส่วน API ตรวจสอบการเชื่อมต่อฐานข้อมูลก่อนเริ่มรับคำขอ

```text
POST /v1/orders/{order_id}/quote
```

สำเร็จตอบ `200` พร้อม JSON, ไม่พบ order ตอบ `404`, dependency ล้มเหลวตอบ `500` โดยไม่เปิดเผยรายละเอียดภายใน และใช้ method ผิดตอบ `405`

ตัวอย่าง response:

```json
{
  "order_id": "ord_demo_001",
  "subtotal_cents": 3397,
  "shipping_cents": 500,
  "tax_cents": 283,
  "total_cents": 4180,
  "currency": "USD",
  "shipping": {"provider":"ParcelPilot", "service":"Ground", "cents":500, "eta":"2026-10-23"}
}
```

จุดสำคัญของตัวอย่างนี้คือ Action ไม่คำนวณเองและไม่เขียน SQL เอง: มัน compose Data + Calculation + 3rd party ให้เป็น business use case เดียว ทำให้ policy เปลี่ยนได้โดยไม่ลาก I/O เข้าไปใน pure pricing.

## ตัวอย่าง endpoint อ่าน order และ HTTP error helper

```bash
curl --fail http://localhost:8080/v1/orders/ord_demo_001
curl -i http://localhost:8080/v1/orders/missing
```

`GET /v1/orders/{order_id}` อ่าน order พร้อมรายการสินค้า ตอบ JSON ด้วยฟิลด์ `id`, `customer_id`, `destination_zip`, `currency`, `items` และ `created_at` โดยไม่เรียก shipping provider

ทั้ง GET order และ POST quote ใช้ helper ใน `internal/api/errors.go` ร่วมกัน:

- `mapHTTPError` เป็น pure function แปลง error เป็น status และ response data โดยใช้ `errors.Is` เพื่อรองรับ error ที่ถูก wrap: `sql.ErrNoRows` → `404` พร้อม `{"error":"order not found"}`, error อื่น → `500` พร้อมข้อความทั่วไปของแต่ละ endpoint
- `writeHTTPError` ทำ HTTP I/O: บันทึก error ภายในลง log, ตั้ง Content-Type, เขียน status และ encode JSON

Handler จึงเรียกเพียง `writeHTTPError(w, err, "could not load order")` แล้ว return โดยไม่ต้องเขียน mapping ซ้ำ และไม่ส่งรายละเอียด error ภายในกลับให้ client
