# Review: Action / Calculation / Data (ACD)

เอกสารนี้อธิบายว่าโปรเจกต์ Checkout Pricing API ได้ประโยชน์จาก ACD ตรงไหน และหลักปฏิบัติที่ใช้แยก ACD ให้ดีในงานจริง

### โครงสร้าง package ที่ใช้จริง

ชื่อ package ถูกเลือกตาม responsibility/domain ไม่ได้ตั้งชื่อว่า `action`, `calculation` หรือ `data` โดยตรง เพราะ ACD เป็นวิธีมองพฤติกรรมของโค้ด ไม่ใช่ข้อบังคับเรื่องชื่อ package:

```text
internal/order     = domain data types
internal/quote     = quote use case / Action orchestration
internal/pricing   = pure pricing rules / Calculation
internal/store     = PostgreSQL data access
internal/shipping  = external shipping effect
internal/api       = HTTP transport effect
```

ดังนั้น ACD ในโปรเจกต์นี้เป็นการจับคู่แบบนี้:

- **Data**: ค่า `Order`, `Product`, `ShippingQuote`, `Quote` และค่าที่ไหลผ่านระบบ ไม่ว่ามาจาก DB, HTTP หรือ calculation
- **Calculation**: pure functions ใน `internal/pricing` ที่รับ Data แล้วคืน Data ใหม่
- **Action**: `internal/quote` ที่เรียงลำดับการทำงาน รวมถึง method ที่อ่าน DB, เรียก HTTP หรือเขียน response
- **Effect boundary**: `internal/store`, `internal/shipping`, `internal/api` เป็นบริเวณที่ Action เชื่อมโลกภายนอก ไม่ใช่ชนิดของ Data

`internal/quote` ไม่ได้ชื่อว่า `action` แต่ยังทำหน้าที่เป็น Action เพราะชื่อ package ควรบอกว่า package นี้ทำอะไรกับระบบธุรกิจ มากกว่าบอกว่าอยู่ layer ไหน

### Data — ข้อเท็จจริง

Data คือข้อมูลที่มีอยู่แล้ว ไม่ควรแอบทำงานกับโลกภายนอกหรือซ่อน business decision ไว้ข้างใน

ตัวอย่าง:

```go
type Product struct {
    SKU            string
    UnitPriceCents int64
    WeightGrams    int64
}
```

`Product` เป็นข้อมูล ไม่ใช่ object ที่ไป query database หรือคำนวณราคาเอง

ในโปรเจกต์นี้:

- `internal/order` เก็บ `Order`, `Product`, `ShippingQuote`, `Quote`
- `internal/store` อ่านข้อเท็จจริงจาก PostgreSQL แล้วแปลงเป็น domain data
- Calculation ไม่จำเป็นต้องรู้ว่าข้อมูลมาจาก PostgreSQL, cache หรือ API

### Calculation — กฎที่คำนวณได้

Calculation คือกฎที่รับ input แล้วคืน output โดยไม่มี side effect:

```go
func Tax(subtotalCents, shippingCents int64) int64 {
    taxable := subtotalCents + shippingCents
    return (taxable*taxRateBPS + 5000) / 10000
}
```

Calculation ที่ดีควรมีคุณสมบัติ:

- input เดิมให้ผลลัพธ์เดิม
- ไม่อ่าน DB
- ไม่เรียก HTTP
- ไม่อ่านเวลาเอง
- ไม่สร้าง random เอง
- ทดสอบได้โดยไม่ต้องเปิด infrastructure

ในโปรเจกต์นี้ `Subtotal`, `Tax` และ `Total` อยู่ใน `internal/pricing` และทดสอบแยกได้ด้วย `go test ./internal/pricing`

### Action — งานที่ทำกับโลกภายนอก

Action คือสิ่งที่ผลลัพธ์หรือผลกระทบขึ้นกับว่าเรียกเมื่อไหร่และเรียกกี่ครั้ง:

```go
orders.Get(ctx, orderID)
shipping.Quote(ctx, zip, weight)
db.Exec(...)
http.ListenAndServe(...)
```

`CreateQuote.Execute` จึงเป็น Action ที่ทำหน้าที่ orchestrate:

```text
โหลด Order
  ↓
โหลด Product
  ↓
คำนวณ Subtotal
  ↓
คำนวณน้ำหนัก
  ↓
เรียก Shipping API
  ↓
คำนวณ Tax และ Total
  ↓
ประกอบ Quote
```

Action ไม่ควรกลายเป็นถังรวม SQL, JSON parsing และ business formula ทั้งหมดในที่เดียว

## 2. จุดที่ ACD ให้ประโยชน์กับโค้ดนี้

### 2.1 ดัน business rule จาก Action ไปเป็น Calculation

ถ้าสูตรราคาอยู่ใน `CreateQuote.Execute` การเปลี่ยนสูตรจะต้องแตะ code ที่มี database และ HTTP dependency อยู่ด้วย

การแยกเป็น:

```go
subtotal, err := pricing.Subtotal(order.Items, products)
tax := pricing.Tax(subtotal, shipping.Cents)
total := pricing.Total(subtotal, shipping.Cents, tax)
```

ทำให้เปลี่ยน business rule และทดสอบได้โดยไม่ต้องเปิด PostgreSQL หรือ Shipping Provider

### 2.2 ทำให้ business workflow อ่านได้

Action เหลือหน้าที่เรียงลำดับงานและส่งข้อมูลระหว่างส่วนต่าง ๆ ส่วนรายละเอียด implementation ถูกซ่อนไว้หลัง abstraction:

- Action รู้ว่า “โหลด order”
- Action รู้ว่า “ขอ shipping quote”
- Action ไม่ต้องรู้ SQL
- Action ไม่ต้องรู้ JSON field ของ provider
- Action ไม่ต้องรู้สูตร tax ภายใน

### 2.3 แยก test ตามสิ่งที่ต้องการพิสูจน์

```text
Calculation test = กฎคำนวณถูกไหม
Action test      = workflow และการประกอบถูกไหม
Adapter test     = SQL/HTTP mapping ถูกไหม
```

ในโปรเจกต์นี้:

- `internal/pricing/pricing_test.go` ทดสอบ subtotal, tax, total และ unknown product
- `internal/quote/create_quote_test.go` ใช้ fake repository กับ fake shipping เพื่อทดสอบ orchestration

### 2.4 ลด coupling กับ infrastructure

`ShippingClient` และ `OrderRepository` เป็น interface ที่ขอบของ Action ทำให้ use case ไม่ผูกกับ PostgreSQL หรือ provider รายใดรายหนึ่ง:

```go
type ShippingClient interface {
    Quote(ctx context.Context, destinationZIP string, totalWeightGrams int64) (order.ShippingQuote, error)
}
```

Interface ควรอยู่ตรงจุดที่มี effect หรือมี dependency ที่เปลี่ยนได้ ไม่จำเป็นต้องสร้าง interface ให้ pure calculation ทุกตัว

## 3. Best practices ในการแยก ACD

### 3.1 แยกตามพฤติกรรม ไม่ใช่แยกตามชื่อไฟล์

ถามว่า:

- สิ่งนี้เป็นข้อมูลที่มีอยู่แล้วหรือไม่? → Data
- input เดิมควรได้ output เดิมหรือไม่? → Calculation
- การเรียกซ้ำหรือเวลาเรียกมีผลไหม? → Action

การมีโฟลเดอร์ชื่อ `pricing` ไม่ได้ทำให้โค้ดเป็น Calculation ถ้าข้างในยังเรียก DB หรือ HTTP — ต้องดูพฤติกรรมจริงของ function ด้วย

### 3.2 ใช้ลำดับ Data > Calculation > Action

ยิ่งโค้ดอยู่ทางซ้ายยิ่งคาดเดาและทดสอบง่าย จึงควรดันโค้ดจาก Action ไปเป็น Calculation หรือ Data ให้มากที่สุดเท่าที่ความหมายยังถูกต้อง

ไม่ได้หมายความว่า Action ต้องหายไป แต่หมายถึงให้เหลือ Action เฉพาะจุดที่ต้องคุยกับโลกจริง

### 3.3 Decision และ planning มักเป็น Calculation ที่ซ่อนอยู่

ตัวอย่างที่มักดึงออกมาเป็น Calculation ได้:

- ลูกค้าได้ส่วนลดหรือไม่
- order เข้าเกณฑ์ free shipping หรือไม่
- ควรเลือก shipping service ใด
- ควรแบ่ง order เป็นกี่ shipment
- สินค้าไหนควรเติม stock ก่อน

```go
func ChooseShippingService(destination string, weight int64, subtotal int64) Service {
    if subtotal >= 5000 {
        return FreeShipping
    }
    if weight > 3000 {
        return Freight
    }
    return Ground
}
```

ถ้า function นี้ไม่อ่าน DB, ไม่เรียก API และไม่อ่านเวลาปัจจุบัน มันมีแนวโน้มเป็น Calculation แม้ชื่อจะเป็น `Choose...`

### 3.4 Calculation ต้องไม่ไปหา input เอง

ไม่ควรเขียน:

```go
func CalculateTax(orderID string) int64 {
    order := database.Load(orderID)
    rate := taxAPI.GetRate(order.Destination)
    return calculate(order, rate)
}
```

ควรแยกเป็น:

```go
order := orderRepo.Get(ctx, orderID)
rate := taxClient.GetRate(ctx, order.Destination)
tax := pricing.Tax(order.Subtotal, rate)
```

Action เตรียมข้อมูล ส่วน Calculation ใช้ข้อมูลที่ได้รับมา

### 3.5 ดึงเวลา, random และ UUID ออกจาก Calculation

ไม่ควรให้ Calculation อ่านเวลาปัจจุบันเอง:

```go
func IsExpired(expireAt time.Time) bool {
    return time.Now().After(expireAt)
}
```

ควรส่งเวลาเข้าไป:

```go
func IsExpired(now, expireAt time.Time) bool {
    return now.After(expireAt)
}
```

Action เป็นผู้จัดหา `now` จาก clock แล้วส่งเข้า Calculation วิธีเดียวกันใช้กับ random, UUID, environment variable และผลจาก external API

### 3.6 Action ควรเป็น business workflow ที่อ่านได้

Action ที่ดีควรตอบคำถาม:

- ทำอะไรก่อน
- ทำอะไรต่อ
- ถ้าพังตรงไหนต้องหยุด
- ผลลัพธ์จากขั้นหนึ่งส่งให้ขั้นต่อไปอย่างไร

แต่ไม่ควรลงรายละเอียดว่า SQL เขียนอย่างไร, JSON field ชื่ออะไร หรือสูตรภาษีคูณอย่างไร

### 3.7 ใช้ interface เฉพาะตรง effect boundary

เหมาะกับ:

- repository
- HTTP client
- clock
- message publisher
- payment gateway
- file system

ไม่จำเป็นต้องสร้าง interface ให้ทุก Calculation:

```go
// มักไม่จำเป็น ถ้ามี pure function เพียงตัวเดียว
type TaxCalculator interface {
    Calculate(...)
}
```

ใช้ function ตรง ๆ ได้:

```go
tax := pricing.Tax(subtotal, shipping)
```

### 3.8 ทิศทาง dependency ควรไหลเข้าหา core

รูปแบบ dependency ที่อ่านได้จากโครงสร้างปัจจุบัน:

```text
cmd/api (composition root)
  ↓
internal/api ───────→ internal/quote ───────→ internal/pricing
                           │   │                    ↓
                           │   └──────────────→ internal/order
                           ├──────────────────→ internal/store
                           └──────────────────→ internal/shipping

internal/store ──────→ internal/order
internal/shipping ───→ internal/order
```

`cmd/api` เป็นจุด wire dependency ทั้งหมด, `internal/api` แปลง HTTP เป็นการเรียก use case, `internal/quote` เป็น Action orchestration, `internal/pricing` เป็น Calculation และ `internal/order` เป็น domain data ส่วน `store`/`shipping` เป็น effect adapters

Repository และ shipping client ถูก inject เข้า `quote.CreateQuote` ทำให้ use case ไม่ต้องสร้าง infrastructure เอง และ Calculation ไม่ต้องรู้จัก database หรือ HTTP client

## 4. จุดที่ควร refactor ต่อในตัวอย่างนี้

ส่วนนี้ใน `CreateQuote.Execute` เป็น Calculation ที่ยังอยู่ใน Action:

```go
var weight int64
for _, item := range order.Items {
    weight += products[item.SKU].WeightGrams * int64(item.Quantity)
}
```

ควรย้ายไปเป็น:

```go
func TotalWeight(
    items []order.OrderItem,
    products map[string]order.Product,
) (int64, error)
```

แล้ว Action จะเหลือ:

```go
weight, err := pricing.TotalWeight(order.Items, products)
shipping, err := a.Shipping.Quote(ctx, order.DestinationZIP, weight)
```

ผลคือ Action เป็น orchestration มากขึ้น และ Calculation ทั้งหมดอยู่ใน Functional Core

ACD ไม่ได้แก้ทุกปัญหาเอง ยังต้องพิจารณาเรื่องเหล่านี้แยกต่างหาก:

- `ProductsBySKU` ปัจจุบัน query ทีละ SKU เป็น N+1 query
- HTTP handler ยัง map error ทุกชนิดเป็น `500`
- การประกอบ URL ควรใช้ `url.Values`
- tax rate ยัง hard-code
- third-party ยังไม่มี retry หรือ circuit breaker
- ยังไม่มี transaction/consistency policy

## 5. Review checklist สำหรับใช้กับ PR

1. Function นี้อ่าน DB, HTTP, clock หรือ random ไหม? ถ้าใช่ มีแนวโน้มเป็น Action
2. ถ้า input เหมือนเดิม ผลลัพธ์เหมือนเดิมไหม? ถ้าใช่ มีแนวโน้มเป็น Calculation
3. สิ่งนี้เป็นเพียงข้อเท็จจริงหรือไม่? ถ้าใช่ คือ Data
4. มี decision หรือ planning ซ่อนอยู่ใน Action ไหม? ถ้ามี ดึงออกเป็น Calculation
5. Calculation มีการไปหา input เองไหม? ถ้ามี ให้ Action เตรียม input แล้วส่งเข้าไป
6. Action มีสูตรธุรกิจยาว ๆ ไหม? ถ้ามี ดึงสูตรออก
7. Data object มี method ที่ไปแตะโลกภายนอกไหม? ถ้ามี แยกเป็น Action/Repository
8. Interface นี้จำเป็นเพราะมี effect หรือ variation จริงไหม?
9. ต้องเปิด DB/API เพื่อทดสอบสูตรหรือไม่? ถ้าต้องเปิด Calculation ยังปนกับ Action
10. อ่านชื่อ use case แล้วเห็น business flow ไหม?

## ประโยคจำ

> Data บอกว่าโลกเป็นอย่างไร, Calculation บอกว่าควรตัดสินใจอย่างไร, Action ทำให้โลกเปลี่ยนไปตามการตัดสินใจนั้น

## คำถามทบทวน

1. ฟังก์ชัน `ChooseDeliveryMethod(weight, destination, subtotal)` ควรเป็น Action, Calculation หรือ Data เพราะอะไร?
2. `TaxCalculator` ที่เรียก database เพื่อโหลด tax rate แล้วยังคำนวณ tax ต่อใน function เดียว ถือเป็น Calculation แท้หรือไม่?
3. โค้ดนี้ควรแยกอย่างไร?

```go
func ProcessOrder(id string) error {
    order := db.Load(id)
    if order.Total > 5000 {
        order.Discount = 500
    }
    payment.Charge(order.Total - order.Discount)
    db.Save(order)
    email.Send(order.CustomerEmail)
    return nil
}
```

คำตอบที่ควรได้คือ: โหลดข้อมูลและทำ side effect อยู่ใน Action, การตัดสินใจส่วนลดควรเป็น Calculation, ส่วน `order` และผลลัพธ์จากการตัดสินใจเป็น Data
