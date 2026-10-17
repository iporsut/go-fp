# -*- coding: utf-8 -*-
"""สร้างสไลด์เวิร์กชอป 'Explore Functional Programming in Go' (2 ชม.) ตามโครงแบบ D"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import re

# ---------- palette ----------
INK = RGBColor(0x0F, 0x17, 0x2A)      # ตัวหนังสือหลัก
ACCENT = RGBColor(0x0D, 0x94, 0x88)   # เขียวอมฟ้า
ACCENT_SOFT = RGBColor(0xCC, 0xFB, 0xF1)
CODE_BG = RGBColor(0x1E, 0x1E, 0x2E)
CODE_FG = RGBColor(0xE2, 0xE8, 0xF0)
CODE_COMMENT = RGBColor(0x94, 0xA3, 0xB8)
BAD = RGBColor(0xDC, 0x26, 0x26)
GOOD = RGBColor(0x16, 0xA3, 0x4A)
MUTED = RGBColor(0x64, 0x74, 0x8B)

TH = "Noto Sans Thai Looped"
DIGIT_FONT = "Ubuntu"
DIGIT_RE = re.compile(r"([0-9][0-9:.\-–/]*)")
MONO = "DejaVu Sans Mono"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = 13.333, 7.5


def slide():
    return prs.slides.add_slide(BLANK)


def textbox(s, x, y, w, h):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    return tb, tf


def put(tf, text, size=18, bold=False, color=INK, font=TH, align=PP_ALIGN.LEFT,
        italic=False, first=False, space_after=6):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    for part in DIGIT_RE.split(text):
        if part == "":
            continue
        r = p.add_run()
        r.text = part
        f = r.font
        f.size = Pt(size)
        f.bold = bold
        f.italic = italic
        # LibreOffice/CTL เว้นวรรคตัวเลขในฟอนต์ไทย — แยกเป็น run ละติน
        f.name = DIGIT_FONT if DIGIT_RE.fullmatch(part) else font
        f.color.rgb = color
    return p


def title_bar(s, title, timing=None, sub=None):
    tb, tf = textbox(s, 0.55, 0.32, 9.6, 1.0)
    put(tf, title, size=30, bold=True, first=True, space_after=2)
    if sub:
        put(tf, sub, size=14, color=MUTED)
    if timing:
        badge = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   Inches(11.05), Inches(0.42), Inches(1.75), Inches(0.55))
        badge.fill.solid()
        badge.fill.fore_color.rgb = ACCENT
        badge.line.fill.background()
        btf = badge.text_frame
        btf.word_wrap = False
        put(btf, timing, size=14, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF),
            align=PP_ALIGN.CENTER, first=True, space_after=0)
    line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.55), Inches(1.32),
                              Inches(12.25), Pt(2.2))
    line.fill.solid()
    line.fill.fore_color.rgb = ACCENT
    line.line.fill.background()


def bullets(s, items, x=0.6, y=1.6, w=12.1, h=5.4, size=17):
    tb, tf = textbox(s, x, y, w, h)
    for i, it in enumerate(items):
        lvl = it.get("level", 0)
        p = put(tf, ("• " if lvl == 0 else "– ") + it["t"],
                size=it.get("size", size if lvl == 0 else size - 2),
                bold=it.get("bold", False),
                color=it.get("color", INK),
                italic=it.get("italic", False),
                first=(i == 0), space_after=it.get("space", 8))
        p.level = lvl
    return tf


def code_box(s, code, x, y, w, h, size=12, label=None, label_color=None):
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y),
                             Inches(w), Inches(h))
    box.fill.solid()
    box.fill.fore_color.rgb = CODE_BG
    box.line.fill.background()
    box.shadow.inherit = False
    tf = box.text_frame
    tf.word_wrap = False
    tf.margin_left = Inches(0.18)
    tf.margin_right = Inches(0.12)
    tf.margin_top = Inches(0.12)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    first = True
    for ln in code.rstrip("\n").split("\n"):
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(0)
        p.alignment = PP_ALIGN.LEFT
        # comment สีหม่น
        idx = ln.find("//")
        parts = [(ln, CODE_FG, False)] if idx < 0 else [
            (ln[:idx], CODE_FG, False), (ln[idx:], CODE_COMMENT, True)]
        for text, col, is_c in parts:
            if text == "":
                continue
            r = p.add_run()
            r.text = text
            r.font.size = Pt(size)
            r.font.name = MONO
            r.font.color.rgb = col
            r.font.italic = is_c
    if label:
        lab = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y - 0.34),
                                 Inches(min(len(label) * 0.11 + 0.4, w)), Inches(0.3))
        lab.fill.solid()
        lab.fill.fore_color.rgb = label_color or ACCENT
        lab.line.fill.background()
        lab.shadow.inherit = False
        ltf = lab.text_frame
        ltf.margin_top = 0
        ltf.margin_bottom = 0
        put(ltf, label, size=12, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF),
            first=True, space_after=0)
    return box


def table(s, rows, x, y, w, h, col_widths=None, header=True, size=14):
    n_r, n_c = len(rows), len(rows[0])
    gf = s.shapes.add_table(n_r, n_c, Inches(x), Inches(y), Inches(w), Inches(h))
    tbl = gf.table
    if col_widths:
        total = sum(col_widths)
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = Emu(int(Inches(w) * cw / total))
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = tbl.cell(ri, ci)
            cell.text = ""
            tf = cell.text_frame
            tf.word_wrap = True
            cell.margin_top = Inches(0.04)
            cell.margin_bottom = Inches(0.04)
            is_h = header and ri == 0
            lines = val.split("\n")
            for li, ln in enumerate(lines):
                p = tf.paragraphs[0] if li == 0 else tf.add_paragraph()
                for part in DIGIT_RE.split(ln):
                    if part == "":
                        continue
                    r = p.add_run()
                    r.text = part
                    r.font.size = Pt(size)
                    r.font.name = DIGIT_FONT if DIGIT_RE.fullmatch(part) else TH
                    r.font.bold = is_h
                    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if is_h else INK
            if is_h:
                cell.fill.solid()
                cell.fill.fore_color.rgb = ACCENT
            elif ri % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(0xF1, 0xF5, 0xF9)
    return tbl


def notes(s, text):
    s.notes_slide.notes_text_frame.text = text


CODE_OPENER = '''func ProcessOrder(order *Order) {
    order.ProcessedAt = time.Now()          // ????
    fmt.Printf("processing %s ...", order.Email)
    order.Total = 0                          // ????
    for _, it := range order.Items {
        order.Total += it.Price * it.Quantity
    }
    if order.Total >= 1000 {
        order.Total = order.Total * 90 / 100 // ????
    }
    orders[order.Email] = *order             // ????
    fmt.Printf("saved: total=%d", order.Total)
}'''

CODE_BAD = '''// ❌ Action ปน Calculation
func ApplyDiscount(cart Cart) Cart {
    fmt.Println("applying discount")   // side effect
    cart.Total = cart.Total * 90 / 100 // mutate input
    return cart
}'''

CODE_GOOD = '''// ✅ Calculation — pure, ทดสอบง่าย
func Discounted(total int) int {
    return total * 90 / 100
}

// action บาง ๆ ทำหน้าที่แค่ "เกิดขึ้น"
func LogDiscount(total int) {
    fmt.Println("discount", Discounted(total))
}'''

CODE_TEST = '''func TestDiscounted(t *testing.T) {
    tests := []struct{ in, want int }{
        {1000, 900}, {999, 999}, {0, 0},
    }
    for _, tt := range tests {
        if got := Discounted(tt.in); got != tt.want {
            t.Errorf("Discounted(%d) = %d; want %d",
                tt.in, got, tt.want)
        }
    }
}'''

CODE_HOF = '''// currying ด้วย closure
func Adder(a int) func(int) int {
    return func(b int) int { return a + b }
}

add10 := Adder(10)        // เก็บ "ครึ่งการคำนวณ" ไว้ก่อน
add10(5)                  // == 15

// generic curry 2 พารามิเตอร์
func Curry2[A, B, R any](f func(A, B) R) func(A) func(B) R {
    return func(a A) func(B) R {
        return func(b B) R { return f(a, b) }
    }
}'''

CODE_LOOPVAR = '''for i := 0; i < 3; i++ {
    go func() { fmt.Println(i) }()
}
// Go 1.22+: พิมพ์ 0..2 ไม่ซ้้า (loop var แยกต่อรอบ)
// Go 1.21-:  ส่วนใหญ่พิมพ์ 3 3 3 (ตัวแปรตัวเดียวถูกจับร่วม)
//
// วิธีเดิมก่อน 1.22:
for i := 0; i < 3; i++ {
    i := i // สำเนาต่อรอบ
    go func() { fmt.Println(i) }()
}'''

CODE_GENERICS = '''func Map[T, R any](in []T, f func(T) R) []R {
    out := make([]R, 0, len(in))
    for _, v := range in { out = append(out, f(v)) }
    return out
}

func Filter[T any](in []T, keep func(T) bool) []T { ... }

// accumulator ต่าง type กับสมาชิกได้ — จุดที่คนถามแน่
func Reduce[T, R any](in []T, init R,
    combine func(R, T) R) R { ... }

total := Reduce(items, 0, func(acc int, it Item) int {
    return acc + it.Price*it.Quantity
})'''

CODE_OPTIONS = '''type Option func(*Server)

func WithPort(p int) Option {
    return func(s *Server) { s.port = p }
}

func New(host string, opts ...Option) *Server {
    s := &Server{host: host, port: 8080} // default ก่อน
    for _, o := range opts { o(s) }      // แล้ว override
    return s
}

srv := New("localhost", WithPort(9090))
// grpc-go, zap, aws-sdk-go-v2 ล้วนใช้ pattern นี้'''

CODE_MIDDLEWARE = '''type Middleware func(http.Handler) http.Handler

func Logger(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s (%s)", r.Method, r.URL, time.Since(start))
    })
}

func Chain(mw ...Middleware) Middleware {
    return func(final http.Handler) http.Handler {
        for i := len(mw) - 1; i >= 0; i-- {
            final = mw[i](final)
        }
        return final
    }
}'''

CODE_COUPON = '''// จุดเริ่ม: ทุกอย่างอยู่ในฟังก์ชันเดียว
func EmailCoupons(cart Cart, coupons []Coupon,
    out io.Writer) error {
    fmt.Printf("finding coupons for %s\\n", cart.Email)
    var codes []string
    for _, c := range coupons {
        if cart.Total >= c.MinimumTotal &&
            (c.Category == "" || c.Category == cart.Category) {
            codes = append(codes, c.Code)
        }
    }
    _, err := fmt.Fprintf(out,
        "To: %s\\nCoupons: %v\\n", cart.Email, codes)
    return err
}'''

CODE_COUPON_SOL = '''// Calculation — pure ทดสอบได้โดยไม่ต้อง mock อะไร
func FindApplicableCoupons(cart Cart,
    coupons []Coupon) []Coupon {
    result := make([]Coupon, 0)
    for _, c := range coupons {
        if cart.Total >= c.MinimumTotal &&
            (c.Category == "" || c.Category == cart.Category) {
            result = append(result, c)
        }
    }
    return result
}

// Action — บาง ๆ ทำหน้าที่เดียว
func SendCouponEmail(out io.Writer, email string,
    coupons []Coupon) error { ... }'''

CODE_ITER = '''// infinite sequence — ไม่มีเงื่อนไขหยุดในตัว
func Fibonacci() iter.Seq[int] {
    return func(yield func(int) bool) {
        a, b := 0, 1
        for {
            if !yield(a) { return } // ผู้บริโภคเป็นคนหยุด
            a, b = b, a+b
        }
    }
}

isEven := func(n int) bool { return n%2 == 0 }
even := Filter(Fibonacci(), isEven)
total := 0
for n := range Take(10, even) { // lazy คำนวณเท่าที่จำเป็น
    total += n
} // sum แรก 10 ตัวเลขคู่ = 257114'''

# ═════════ สไลด์ ═════════

# 1 ปก
s = slide()
band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.35))
band.fill.solid(); band.fill.fore_color.rgb = ACCENT; band.line.fill.background()
tb, tf = textbox(s, 0.9, 2.3, 11.5, 3.0)
put(tf, "Explore Functional Programming in Go", size=44, bold=True, first=True, space_after=10)
put(tf, "เวิร์กชอป 2 ชั่วโมง · กรอบ Actions / Calculations / Data", size=22, color=ACCENT, space_after=6)
put(tf, "แนวคิดจาก Grokking Simplicity (Eric Normand) — แบบ pragmatic สำหรับ Go developer", size=16, color=MUTED)
tb2, tf2 = textbox(s, 0.9, 6.4, 11.5, 0.6)
put(tf2, "อาทิตย์ที่ 18 ตุลาคม 2026 · โค้ดตัวอย่าง: ~/src/go-fp", size=14, color=MUTED, first=True)
notes(s, "เปิดด้วยคำถาม: เคยแก้ bug ที่โค้ด 'รันครั้งที่สองผลไม่เหมือนครั้งแรก' ไหม? — นั่นคือ action ที่หลุดมาปน calculation ทั้งงานนี้ไม่พูด monad/functor เลย โค้ดทั้งหมดอยู่ที่ ~/src/go-fp รัน go test ./... ได้หมด")

# 2 Agenda
s = slide()
title_bar(s, "แผนวันนี้ (2 ชม.)", sub="มองโค้ด → เขียนโค้ด → ใช้จริง → ลงมือทำ")
table(s, [
    ["เวลา", "เรื่อง", "วิธี"],
    ["0:00–0:15", "เปิด: โค้ดปนเปื้อน 1 หน้า", "แยก Action/Calculation/Data ร่วมกันบนกระดาน"],
    ["0:15–0:40", "Refactor live", "ดึง calculation ออกจาก action → test ง่ายขึ้น"],
    ["0:40–1:05", "เครื่องมือของ Go", "HOF, closures (+ pitfall), generics Map/Filter/Reduce"],
    ["1:05–1:25", "FP ในโค้ดจริง", "Functional Options + middleware (= composition)"],
    ["1:25–1:45", "เวิร์กชอป", "แยก coupon ออกจาก sending email ด้วยมือตัวเอง"],
    ["1:45–2:00", "ของหวาน + สรุป", "iter.Seq lazy pipeline + cheat sheet"],
], x=0.6, y=1.55, w=12.15, h=5.3, col_widths=[1.6, 3.4, 7.1], size=14)
notes(s, "ย้ำสัญญากับผู้เรียน: จบ 2 ชม. จะได้ 'ทักษะมองโค้ด' ที่ใช้กับ legacy Go ได้ทันที ไม่ใช่ type theory ถ้าเวลาเริ่มเบี้ยว middleware เป็นตัวตัดก่อน (ข้ามได้ ไม่กระทบเรื่องเล่า)")

# 3 ACD concept
s = slide()
title_bar(s, "แกนคิดของวันนี้: Actions / Calculations / Data")
table(s, [
    ["ประเภท", "คืออะไร", "ตัวอย่าง", "ชื่อ FP อื่นเรียก"],
    ["Data", "ข้อเท็จจริงของเหตุการณ์", "email ที่ user กรอก, ยอดเงินจาก API", "—"],
    ["Calculation", "input เดิม → output เดิม เสมอ", "หาส่วนลด, validate email", "pure function"],
    ["Action", "ผลขึ้นกับ 'รันกี่ครั้ง / เมื่อไหร่'", "ส่ง email, เขียน DB, อ่านเวลา", "side effect"],
], x=0.6, y=1.6, w=12.15, h=2.6, col_widths=[1.9, 3.6, 4.6, 2.0], size=14)
bullets(s, [
    {"t": "ทักษะที่ต้องการคือ \"การมองโค้ด\" (spotting) ก่อนเทคนิค — ใช้กับ legacy Go ได้ทันที", "level": 0},
    {"t": "Go เป็นภาษาที่ action หลุดมาง่าย: mutation, goroutine, I/O อยู่ใกล้มือเสมอ", "level": 0},
    {"t": "วันนี้ไม่มี monad / functor / type theory — มีแต่คำถามเดียว: โค้ดบรรทัดนี้ \"พึ่งโลกภายนอก\" ไหม?", "level": 0, "bold": True, "color": ACCENT},
], y=4.5)
notes(s, "ให้ผู้เรียนลองยกตัวอย่าง action/calculation จากงานตัวเองคนละ 1 อย่าง (30 วินาที) ก่อนไปสไลด์ถัดไป — คำถามชี้ว่า calculation มักแฝง 'ในหัว' เช่น กติกาส่วนลดที่อยู่ใน if ของ handler ใหญ่ ๆ")

# 4 opener
s = slide()
title_bar(s, "เปิด: โค้ดนี้ทำอะไรบ้าง?", "0:00–0:15",
          sub="จาก go-fp/01-acd-opener — ลองตีเส้นแยก: บรรทัดไหน Data / Calculation / Action?")
code_box(s, CODE_OPENER, 0.6, 1.85, 8.1, 4.9, size=13)
tb, tf = textbox(s, 9.0, 1.9, 3.8, 4.6)
put(tf, "กติกา", size=18, bold=True, color=ACCENT, first=True, space_after=8)
for t in ["อ่านเงียบ ๆ 1 นาที", "จับคู่ชี้บรรทัด 3 นาที", "เฉลยบนกระดานร่วมกัน"]:
    put(tf, "• " + t, size=15, space_after=6)
put(tf, "", size=6, space_after=0)
put(tf, "คำใบ้: บรรทัดเดียวอาจมีมากกว่า 1 ประเภทซ้อนกัน", size=13, color=MUTED, italic=True)
notes(s, "อย่าเฉลยเร็ว — ปล่อยให้เถียงกันก่อน จุดที่ควรติง: order.Total ถูก mutate (action บน data), กติกา 1000→90% คือ calculation ที่ฝังอยู่, time.Now/print/save คือ action ชัด ๆ ปิดท้าย: 'ถ้ากติกาส่วนลดเปลี่ยน เราต้องรันระบบทั้งระบบเพื่อ test ไหม?' → ทำไมต้องแยก")

# 5 refactor live
s = slide()
title_bar(s, "Refactor live: ดึง Calculation ออกจาก Action", "0:15–0:40")
code_box(s, CODE_BAD, 0.6, 1.85, 5.9, 2.5, size=12, label="❌ ก่อน", label_color=BAD)
code_box(s, CODE_GOOD, 6.85, 1.85, 5.9, 2.5, size=12, label="✅ หลัง", label_color=GOOD)
code_box(s, CODE_TEST, 0.6, 4.85, 12.15, 2.45, size=11, label="table-driven test — ไม่ต้อง mock, ไม่ต้อง capture stdout", label_color=MUTED)
notes(s, "พิมพ์สดให้เห็น (หรือสลับหน้าจอ go-fp/02) ประเด็นสำคัญ: การ test ตัว ❌ ต้องจับ stdout + ระวัง input ถูก mutate — ตัว ✅ test ด้วยตาราง 3 บรรทัด ถามต่อ: แล้ว LogDiscount ยัง test ยากไหม? → action ไม่หายไป แต่ถูก 'ย้ายไปขอบ'")

# 6 HOF/closures
s = slide()
title_bar(s, "เครื่องมือของ Go (1): Higher-order + Closures", "0:40–1:05",
          sub="ฟังก์ชันเป็นค่าได้ — std lib ใช้เยอะแล้ว: sort.Slice, http.HandleFunc, context.WithCancel")
code_box(s, CODE_HOF, 0.6, 1.95, 12.15, 4.1, size=14)
bullets(s, [
    {"t": "closure = ฟังก์ชันที่จำบริบทตอนถูกสร้าง → นี่คือวิธี Go ทำ partial application", "level": 0, "size": 15},
    {"t": "แต่ระวัง: closure จับ 'ตัวแปร' ไม่ใช่ 'ค่า' → เจอเรื่องในสไลด์ถัดไป", "level": 0, "size": 15},
], y=6.2)
notes(s, "โค้ดเต็มใน go-fp/04-closures-currying มี test ของ Adder/Curry2 ให้ผู้เรียนลองเดาลายเซ็น Curry2 ก่อนเฉลย — ย้ำว่า Go verbose กว่า ML-family ชัดเจน นี่คือเหตุผลที่ Go ไม่มี pipe operator (ตอบคำถามที่มักโผล่)")

# 7 loop var pitfall
s = slide()
title_bar(s, "Pitfall ที่ต้องรู้: loop variable (ก่อน Go 1.22)", "0:40–1:05")
code_box(s, CODE_LOOPVAR, 0.6, 1.75, 12.15, 4.3, size=14)
bullets(s, [
    {"t": "จุดสอน: closure จับตัวแปรเดียวกัน ไม่ใช่สำเนา — ยกเว้น Go 1.22+ ที่ loop var แยกต่อรอบแล้ว", "level": 0, "size": 15},
    {"t": "โค้ดเก่าในทีม (ก่อน 1.22) ยังมีรอยแก้ i := i ทิ้งไว้ให้เห็นได้", "level": 0, "size": 15},
], y=6.25)
notes(s, "ถ้ามีเวลา ให้รันสดบน Go เวอร์ชันเก่า/ใหม่เทียบกัน (gotip) คนที่เคยโดน bug นี้จะตื่นเต้นเอง — เชื่อมกลับ ACD: goroutine คือ action การจับตัวแปรร่วมคือ data ที่แชร์กันโดยไม่ตั้งใจ")

# 8 generics
s = slide()
title_bar(s, "เครื่องมือของ Go (2): Generics — Map / Filter / Reduce", "0:40–1:05",
          sub="Go 1.18+ · โค้ดเต็ม + TDD ใน go-fp/03-fp-toolkit")
code_box(s, CODE_GENERICS, 0.6, 2.05, 12.15, 3.7, size=14)
bullets(s, [
    {"t": "Go ไม่มี built-in map/filter — เขียนเองได้ใน 5 บรรทัด แต่ Go community นิยม for loop ตรง ๆ: โค้ดชุดนี้คือเครื่องมือ 'เรียนรู้' ไม่ใช่แนวปฏิบัติ", "level": 0, "size": 15},
    {"t": "Reduce ที่ accumulator ต่าง type กับ element คือจุดที่ generics ช่วยจริง (Reduce[Item, int])", "level": 0, "size": 15},
], y=5.95)
notes(s, "แนะให้ผู้เรียนเปิด fp_test.go เป็นตัวอย่าง TDD: เขียน test ก่อน implementation เห็นลายเซ็น generic ทีละขั้น (แนวบทความ bitfieldconsulting) ถ้ามีคนถาม performance — for loop ตรง ๆ ชนะเสมอ ไม่มี magic")

# 9 functional options
s = slide()
title_bar(s, "FP ในโค้ดจริง: Functional Options", "1:05–1:25",
          sub="closure + higher-order function ที่คุณใช้อยู่แล้วโดยไม่รู้ตัว")
code_box(s, CODE_OPTIONS, 0.6, 2.05, 12.15, 3.7, size=14)
bullets(s, [
    {"t": "อ่านได้ว่า: WithPort(9090) คือ 'calculation ที่ผลิต action เล็ก ๆ' เอาไว้ยิงใส่ constructor ตอนหลัง", "level": 0, "size": 15},
    {"t": "เห็นใน production จริง: grpc-go, uber-go/zap, aws-sdk-go-v2", "level": 0, "size": 15, "bold": True},
], y=5.95)
notes(s, "นี่คือ aha moment ของวัน: หลายคนใช้ zap.New(...WithFields) มาตลอดแต่ไม่เคยมองว่ามันคือ FP pattern ถาม: ทำไมไม่ใช้ struct config ธรรมดา? → options ขยายได้ไม่ทำ breaking change + default ชัด")

# 10 middleware (cuttable)
s = slide()
title_bar(s, "Middleware = Function Composition", "1:05–1:25",
          sub="⚠️ สไลด์ 'ตัดได้' ตัวแรก — เวลาไม่พอให้ข้ามไปเวิร์กชอปได้เลย")
code_box(s, CODE_MIDDLEWARE, 0.6, 2.05, 12.15, 4.0, size=12)
bullets(s, [
    {"t": "http.Handler เป็น function เดียว → wrapper ครอบซ้อน ๆ = composition แบบ Go", "level": 0, "size": 15},
    {"t": "อ่าน Chain(Logger, Recover) จากในออกนอก: ลำดับ = ความหมายทางธุรกิจ", "level": 0, "size": 15},
], y=6.25)
notes(s, "โค้ดเต็ม + httptest อยู่ go-fp/06-middleware ถ้าเวลาเหลือน้อยกว่า 15 นาที ณ จุดนี้ ให้ตัดเลย — พูดประโยคเดียว: 'middleware ก็คือการเอาฟังก์ชันมาคู่กัน แล้วลำดับมีความหมาย' แล้วข้าม")

# 11 workshop
s = slide()
title_bar(s, "เวิร์กชอป: Coupon Email", "1:25–1:45",
          sub="โจทย์จริงจาก Grokking Simplicity บท 3–5 (พอร์ตเป็น Go แล้ว: go-fp/07-coupon-email-exercise)")
code_box(s, CODE_COUPON, 0.6, 2.05, 6.6, 4.5, size=12, label="starter/coupons.go", label_color=BAD)
tb, tf = textbox(s, 7.5, 2.1, 5.3, 4.5)
put(tf, "โจทย์", size=18, bold=True, color=ACCENT, first=True, space_after=6)
for i, t in enumerate([
    "จับคู่ — แยก A/C/D ให้ครบ (3 น.)",
    "ดึง FindApplicableCoupons ออกมา + เขียน table-driven test ก่อน implementation (10 น.)",
    "เหลือ SendCouponEmail เป็น action บาง ๆ (5 น.)",
    "เทียบกับ solution/ (2 น.)",
]):
    put(tf, f"{i+1}. {t}", size=15, space_after=8)
put(tf, "กติกา: เงินเป็นบาทเต็มไม่ติดลบ · coupon ไม่มีหมวด = ใช้ได้ทุกหมวด · รักษาลำดับเดิม", size=13, color=MUTED, italic=True)
notes(s, "เดินดูรอบห้อง จุดพลาดที่เจอบ่อย: (1) ลืมรักษาลำดับคูปองเดิม (2) คนที่ return slice ใหม่แต่ mutate element ข้างใน — ถามว่า pure จริงไหม (3) ฝั่ง action บางคนยังเอาการหา coupon ไปแอบใส่ ย้ำ: exercise เวอร์ชันเต็มอยู่ใน EXERCISE.md ให้ผู้เรียนเปิดตามได้")

# 12 solution + iter
s = slide()
title_bar(s, "เฉลย + ของหวานปิดท้าย: Lazy Pipeline (Go 1.23+)", "1:45–2:00")
code_box(s, CODE_COUPON_SOL, 0.6, 1.75, 5.9, 3.45, size=10.5, label="solution/", label_color=GOOD)
code_box(s, CODE_ITER, 6.85, 1.75, 5.9, 3.45, size=10.5, label="09-lazy-iter-seq", label_color=ACCENT)
bullets(s, [
    {"t": "calculation ที่ pure เต็มตัว = test ไม่ต้อง mock / action ที่บาง = เหลือแค่ 'จุดที่โลกเปลี่ยน'", "level": 0, "size": 14},
    {"t": "iter.Seq = lazy sequence ใน std lib: Fibonacci เป็นอนุกรมไม่รู้จบ แต่ Take(10) คำนวณแค่ที่จำเป็น", "level": 0, "size": 14},
], y=5.4)
notes(s, "เฉลยสั้น ๆ แล้วโชว์ iter.Seq เป็นของหวาน: range-over-func ทำให้ infinite sequence เขียนได้ปลอดภัยเพราะ yield คืน false ได้ (ผู้บริโภคสั่งหยุด) อย่าลืมบอกว่า int overflow ถ้าดันอ่านไกล — ของจริงไม่มีอะไร infinite")

# 13 cheat sheet
s = slide()
title_bar(s, "Cheat Sheet: ถาม–ตอบ 3 คำถามกับโค้ดทุกบรรทัด")
table(s, [
    ["ถาม", "ถ้าคำตอบคือ...", "แล้วทำอะไร"],
    ["\"ผลลัพธ์ขึ้นกับเวลา/จำนวนครั้งไหม?\"", "ใช่ → Action", "ดันไปไว้ขอบระบบ ทำให้บางที่สุด ไม่ test ก็ได้"],
    ["\"input เดิม ให้ผลเดิมเสมอไหม?\"", "ใช่ → Calculation", "ทำให้ pure + เขียน table-driven test"],
    ["\"เป็นแค่ข้อเท็จจริงที่ส่งต่อกันไหม?\"", "ใช่ → Data", "ใช้ immutable เท่าทำได้ (value semantics)"],
], x=0.6, y=1.6, w=12.15, h=2.7, col_widths=[4.2, 2.6, 5.35], size=14)
bullets(s, [
    {"t": "Go ทำได้ดี: HOF, closures, generics (1.18+), iter.Seq (1.23+)", "level": 0, "size": 15},
    {"t": "Go ไม่มี: built-in map/filter, immutability guarantee, tail-call optimization — รู้ขีดจำกัด แล้วออกแบบรอบมัน", "level": 0, "size": 15},
    {"t": "คำโปรย: 'คุณไม่ต้องเขียน FP ทั้งวัน — แค่หมั่นย้าย calculation ออกจาก action ทีละฟังก์ชัน'", "level": 0, "size": 15, "bold": True, "color": ACCENT},
], y=4.6)
notes(s, "ปิดด้วย call to action: สัปดาห์หน้าลองหยิบ handler ใน service ตัวเองมา 1 ตัว แยก ACD แล้วดึง calculation ออกมา 1 ชิ้น — ทำ 15 นาทีก็คุ้ม")

# 14 อ่านต่อ
s = slide()
title_bar(s, "อ่านต่อ")
bullets(s, [
    {"t": "Grokking Simplicity — Eric Normand (Manning 2021) · โฟกัส ch.3–5 (ACD), ch.6–7 (immutability), ch.10–14 (first-class functions)", "level": 0, "size": 17},
    {"t": "Functional Programming in Go — Dylan Meeus (Packt 2023)", "level": 0, "size": 17},
    {"t": "Go blog: Range Over Function Types (Go 1.23) — go.dev/blog/range-functions", "level": 0, "size": 17},
    {"t": "Codewalk: First-Class Functions in Go — go.dev/doc/codewalk/functions", "level": 0, "size": 17},
    {"t": "Eli Bendersky: Higher-order functions in Go — eli.thegreenplace.net", "level": 0, "size": 17},
    {"t": "โค้ดทั้งหมดวันนี้: github.com/…/go-fp (หรือ ~/src/go-fp) — go test ./... ผ่านทุก package", "level": 0, "size": 17, "bold": True},
], y=1.8)
tb, tf = textbox(s, 0.6, 6.3, 12.1, 0.7)
put(tf, "ขอบคุณครับ 🙏 — คำถามได้ตลอด", size=20, bold=True, color=ACCENT, first=True)
notes(s, "เผื่อ Q&A: คำถามที่น่าจะโผล่ — (1) ทำไม Go ไม่มี pipe operator → verbose by design + error ทำ chain ยาก (2) copy-on-write แพงไหม → benchmark ใน go-fp/08: struct เล็กต่างกัน ~0.05 ns/op (3) goroutine/channel เข้ากรอบไหน → channel คือ data, การส่ง/รับคือ action")

out = "/home/weerasak/src/go-fp/slides/fp-in-go-workshop.pptx"
prs.save(out)
print("saved", out, "slides:", len(prs.slides._sldIdLst))
