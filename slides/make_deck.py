# -*- coding: utf-8 -*-
"""สไลด์สำหรับผู้เรียน — เวิร์กชอป 'Explore Functional Programming in Go' (2 ชม.)
หลักการ: หน้าสไลด์สื่อคอนเซปต์ให้ผู้เรียน · ทุกอย่างที่เป็น meta ของผู้สอน
(เวลา, จุดตัด, การคุมห้อง) อยู่ใน speaker notes เท่านั้น"""
import re
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ---------- palette ----------
INK = RGBColor(0x0F, 0x17, 0x2A)
ACCENT = RGBColor(0x0D, 0x94, 0x88)
ACCENT_SOFT = RGBColor(0xCC, 0xFB, 0xF1)
CODE_BG = RGBColor(0x1E, 0x1E, 0x2E)
CODE_FG = RGBColor(0xE2, 0xE8, 0xF0)
CODE_COMMENT = RGBColor(0x94, 0xA3, 0xB8)
BAD = RGBColor(0xDC, 0x26, 0x26)
GOOD = RGBColor(0x16, 0xA3, 0x4A)
MUTED = RGBColor(0x64, 0x74, 0x8B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

TH = "Noto Sans Thai Looped"
DIGIT_FONT = "Ubuntu"
DIGIT_RE = re.compile(r"([0-9][0-9:.\-–/]*)")
MONO = "DejaVu Sans Mono"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


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


def title_bar(s, title, sub=None):
    tb, tf = textbox(s, 0.55, 0.32, 12.2, 1.0)
    put(tf, title, size=30, bold=True, first=True, space_after=2)
    if sub:
        put(tf, sub, size=15, color=MUTED)
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


def takeaway(s, text, y=6.55):
    """แถบสรุปด้านล่าง — ข้อความหลักที่ผู้เรียนต้องจับได้จากหน้านี้"""
    bar = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(y),
                             Inches(12.15), Inches(0.62))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT_SOFT
    bar.line.fill.background()
    bar.shadow.inherit = False
    tf = bar.text_frame
    tf.margin_top = Inches(0.06)
    tf.margin_bottom = Inches(0.04)
    tf.word_wrap = True
    put(tf, "จำไว้: " + text, size=15, bold=True, color=RGBColor(0x0F, 0x76, 0x6E),
        first=True, space_after=0)


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
        put(ltf, label, size=12, bold=True, color=WHITE, first=True, space_after=0)
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
            for li, ln in enumerate(val.split("\n")):
                p = tf.paragraphs[0] if li == 0 else tf.add_paragraph()
                for part in DIGIT_RE.split(ln):
                    if part == "":
                        continue
                    r = p.add_run()
                    r.text = part
                    r.font.size = Pt(size)
                    r.font.name = DIGIT_FONT if DIGIT_RE.fullmatch(part) else TH
                    r.font.bold = is_h
                    r.font.color.rgb = WHITE if is_h else INK
            if is_h:
                cell.fill.solid()
                cell.fill.fore_color.rgb = ACCENT
            elif ri % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(0xF1, 0xF5, 0xF9)
    return tbl


def notes(s, text):
    s.notes_slide.notes_text_frame.text = text


# ---------- โค้ดตัวอย่าง ----------
CODE_OPENER = '''func ProcessOrder(order *Order) {
    order.ProcessedAt = time.Now()
    fmt.Printf("processing %s ...", order.Email)
    order.Total = 0
    for _, it := range order.Items {
        order.Total += it.Price * it.Quantity
    }
    if order.Total >= 1000 {
        order.Total = order.Total * 90 / 100
    }
    orders[order.Email] = *order
    fmt.Printf("saved: total=%d", order.Total)
}'''

CODE_BAD = '''// ฟังก์ชันนี้ "คำนวณ" หรือ "ทำอะไรลงโลกภายนอก"?
func ApplyDiscount(cart Cart) Cart {
    fmt.Println("applying discount")
    cart.Total = cart.Total * 90 / 100
    return cart
}'''

CODE_GOOD = '''// คำนวณอย่างเดียว — input เดิม ได้ผลเดิมเสมอ
func Discounted(total int) int {
    return total * 90 / 100
}

// การ "ทำลงโลกภายนอก" แยกเป็นอีกฟังก์ชัน
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

CODE_HOF = '''// ฟังก์ชันคืนฟังก์ชันได้ — "เก็บครึ่งการคำนวณ" ไว้ก่อน
func Adder(a int) func(int) int {
    return func(b int) int { return a + b }
}

add10 := Adder(10)
add10(5) // == 15

// generic: curry ฟังก์ชัน 2 พารามิเตอร์
func Curry2[A, B, R any](f func(A, B) R) func(A) func(B) R {
    return func(a A) func(B) R {
        return func(b B) R { return f(a, b) }
    }
}'''

CODE_LOOPVAR = '''for i := 0; i < 3; i++ {
    go func() { fmt.Println(i) }()
}

// Go 1.22+: พิมพ์ 0..2 ไม่ซ้้า
//         (loop var แยกของตัวเองทุกรอบ)
// Go 1.21 ลงไป: ส่วนใหญ่พิมพ์ 3 3 3
//         (ทุก closure จับ "ตัวแปรตัวเดียวกัน")

// โค้ดเก่าจึงมีรอยแก้แบบนี้ทิ้งไว้:
for i := 0; i < 3; i++ {
    i := i // ทำสำเนาต่อรอบ
    go func() { fmt.Println(i) }()
}'''

CODE_GENERICS = '''func Map[T, R any](in []T, f func(T) R) []R {
    out := make([]R, 0, len(in))
    for _, v := range in { out = append(out, f(v)) }
    return out
}

func Filter[T any](in []T, keep func(T) bool) []T { ... }

// accumulator ต่าง type กับสมาชิกได้
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

srv := New("localhost", WithPort(9090))'''

CODE_MIDDLEWARE = '''type Middleware func(http.Handler) http.Handler

func Logger(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s (%s)", r.Method, r.URL, time.Since(start))
    })
}

// เอา middleware มาครอบซ้อนกัน = composition
func Chain(mw ...Middleware) Middleware {
    return func(final http.Handler) http.Handler {
        for i := len(mw) - 1; i >= 0; i-- {
            final = mw[i](final)
        }
        return final
    }
}'''

CODE_COUPON = '''// ทุกอย่างอยู่ในฟังก์ชันเดียว — มองแล้วเจออะไรบ้าง?
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

CODE_COUPON_SOL = '''// Calculation — pure: input เดิม ได้คูปองชุดเดิมเสมอ
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

// Action — เหลือแค่ "จุดที่โลกเปลี่ยน"
func SendCouponEmail(out io.Writer, email string,
    coupons []Coupon) error { ... }'''

CODE_ITER = '''// อนุกรมไม่รู้จบ — ไม่มีเงื่อนไขหยุดในตัว
func Fibonacci() iter.Seq[int] {
    return func(yield func(int) bool) {
        a, b := 0, 1
        for {
            if !yield(a) { return } // ผู้อ่านเป็นคนสั่งหยุด
            a, b = b, a+b
        }
    }
}

isEven := func(n int) bool { return n%2 == 0 }
even := Filter(Fibonacci(), isEven)
total := 0
for n := range Take(10, even) { // คำนวณเท่าที่ขอเท่านั้น
    total += n
} // sum แรก 10 ตัวเลขคู่ = 257114'''

# ═════════ สไลด์ (มุมผู้เรียน) ═════════

# 1 ปก
s = slide()
band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.35))
band.fill.solid(); band.fill.fore_color.rgb = ACCENT; band.line.fill.background()
tb, tf = textbox(s, 0.9, 2.3, 11.5, 3.0)
put(tf, "Explore Functional Programming in Go", size=44, bold=True, first=True, space_after=10)
put(tf, "มองโค้ดให้เห็น 3 อย่าง: Actions · Calculations · Data", size=22, color=ACCENT, space_after=6)
put(tf, "ทักษะที่ใช้กับโค้ด Go ที่ทำงานจริงได้ทันที — ไม่ต้องมีพื้น FP มาก่อน", size=16, color=MUTED)
notes(s, "[0:00] เปิดด้วยคำถาม: เคยแก้ bug ที่โค้ด 'รันครั้งที่สองผลไม่เหมือนครั้งแรก' ไหม? — นั่นคือ action ที่หลุดมาปน calculation ทั้งงานไม่พูด monad/functor เลย (ใครถามเรื่อง Haskell/monad เลื่อนไปตอบท้ายชั่วโมง)")

# 2 สิ่งที่จะได้
s = slide()
title_bar(s, "จบ 2 ชั่วโมงนี้ คุณจะได้", sub="เรียงจาก 'มองเป็น' → 'เขียนเป็น' → 'ใช้เป็น'")
bullets(s, [
    {"t": "ทักษะมองโค้ด — เห็นว่าบรรทัดไหนเป็น Action / Calculation / Data แล้วรู้ว่ามันแปลว่าอะไร", "level": 0, "size": 19, "space": 14},
    {"t": "วิธีดึง calculation ออกจาก action ให้โค้ดทดสอบง่ายขึ้น — ใช้กับ legacy Go ได้ทันที", "level": 0, "size": 19, "space": 14},
    {"t": "เครื่องมือของ Go สำหรับเขียนแบบ functional: closures, generics, iter.Seq", "level": 0, "size": 19, "space": 14},
    {"t": "สายตาใหม่กับ pattern ที่คุณใช้อยู่แล้ว (Functional Options, middleware) — ที่จริงมันคือ FP", "level": 0, "size": 19, "space": 14},
    {"t": "และมีการบ้าน 1 ชิ้น ให้ได้ลอง refactor ด้วยมือตัวเองต่อที่บ้าน", "level": 0, "size": 19, "space": 14, "bold": True, "color": ACCENT},
], y=1.75)
notes(s, "[0:02] ย้ำสัญญา: ออกจากห้องไปด้วยทักษะ ไม่ใช่ความรู้ลอย ๆ — เล่า flow วันนี้สั้น ๆ: ดูโค้ด เขียนโค้ด แล้วมีการบ้านไปต่อที่บ้าน (เวลาเริ่มเบี้ยว: middleware เป็นตัวตัดก่อน)")

# 3 ACD concept
s = slide()
title_bar(s, "แกนคิดของวันนี้: ทุกบรรทัดโค้ดคือ 1 ใน 3 อย่างนี้")
table(s, [
    ["", "คืออะไร", "ตัวอย่าง", "ชื่อ FP อื่นเรียก"],
    ["Data", "ข้อเท็จจริงของเหตุการณ์", "email ที่ user กรอก, ยอดเงินจาก API", "—"],
    ["Calculation", "input เดิม → output เดิม เสมอ", "หาส่วนลด, validate email", "pure function"],
    ["Action", "ผลขึ้นกับ 'รันกี่ครั้ง / เมื่อไหร่'", "ส่ง email, เขียน DB, อ่านเวลา", "side effect"],
], x=0.6, y=1.6, w=12.15, h=2.7, col_widths=[1.9, 3.6, 4.6, 2.0], size=14)
bullets(s, [
    {"t": "คำถามเดียวที่ต้องตอบเก่ง: \"บรรทัดนี้พึ่งโลกภายนอกไหม?\"", "level": 0, "size": 18, "bold": True, "color": ACCENT, "space": 12},
    {"t": "อ่านนาฬิกา, พิมพ์ log, เขียนไฟล์ → พึ่ง (ผลเปลี่ยนตามเวลา/จำนวนครั้ง)", "level": 0, "size": 16},
    {"t": "บวกเลข, ตรวจ format, หาคูปองที่ใช้ได้ → ไม่พึ่ง (input ชุดเดิม = คำตอบชุดเดิม)", "level": 0, "size": 16},
], y=4.7)
notes(s, "[0:05] ให้ผู้เรียนยกตัวอย่าง action/calculation จากงานตัวเองคนละ 1 อย่าง (30 วินาที) — ประเด็น: calculation มักแฝง 'ในหัว' เช่น กติกาส่วนลดที่อยู่ใน if ของ handler ใหญ่ ๆ จนไม่มีใครเห็นว่ามันคือ calculation แยกอยู่")

# 4 opener
s = slide()
title_bar(s, "ลองอ่านโค้ดนี้", "บรรทัดไหนคือ Data · Calculation · Action? — บรรทัดเดียวซ้อนหลายอย่างได้")
code_box(s, CODE_OPENER, 0.6, 1.75, 7.8, 4.6, size=14)
tb, tf = textbox(s, 8.75, 1.9, 4.0, 4.4)
put(tf, "ชวนคิด", size=18, bold=True, color=ACCENT, first=True, space_after=8)
for t in ["ทำไมฟังก์ชันนี้รัน 2 ครั้ง ผลอาจไม่เหมือนกัน?",
          "ถ้ากติกาส่วนลดเปลี่ยน ต้องรันระบบทั้งระบบเพื่อทดสอบไหม?",
          "ข้อมูล (Data) ที่ไหลผ่านฟังก์ชันนี้มีอะไรบ้าง?"]:
    put(tf, "• " + t, size=15, space_after=10)
notes(s, "[0:08] อย่าเฉลยเร็ว — จับคู่ชี้บรรทัด 3 นาที แล้วเฉลยบนกระดาน จุดที่ติง: order.Total ถูก mutate (action บน data), กติกา 1000→90% คือ calculation ที่ฝังอยู่, time.Now/print/save คือ action ชัด ๆ คำถามขวาคือสะพานไปหน้าถัดไป")

# 5 ปัญหา
s = slide()
title_bar(s, "โค้ดที่ปนกันทำให้ชีวิตยาก", sub="ตัวอย่างเดิม — มองผ่านกรอบ ACD แล้วปัญหาชัดขึ้นเอง")
bullets(s, [
    {"t": "Action แฝงใน calculation → ทดสอบยาก", "level": 0, "size": 20, "bold": True, "space": 6},
    {"t": "อยากทดสอบแค่กติกาส่วนลด ต้องรัน ProcessOrder ทั้งฟังก์ชัน — จับ stdout, ล้าง map, ปลอมเวลา", "level": 1, "size": 16, "space": 12},
    {"t": "Mutate input → ผู้เรียกไม่รู้ว่า order ของตัวเองถูกแก้ไปแล้ว", "level": 0, "size": 20, "bold": True, "space": 6},
    {"t": "bug ยอดฮิต: ผ่าน order เข้าไป 2 ครั้ง ยอดหายเพราะถูกลดสองรอบ", "level": 1, "size": 16, "space": 12},
    {"t": "กติกาธุรกิจ (ลด 10% เมื่อยอดถึง 1,000) ฝังอยู่ใน action → มองไม่เห็นเป็น 'ความรู้'", "level": 0, "size": 20, "bold": True, "space": 6},
    {"t": "กติกาพวกนี้คือ calculation ที่ควรรวมอยู่ด้วยกัน เทสต์ได้เอง และใช้ซ้ำได้", "level": 1, "size": 16, "space": 12},
], y=1.75)
takeaway(s, "โค้ดที่ปนกันยังทำงานได้ — แต่คุณจ่ายค่ามันตอนเทสต์ ตอนแก้ และตอนเจอ bug")
notes(s, "[0:13] อย่าเพิ่งโชว์วิธีแก้ — ให้เห็นปัญหาก่อน ถามว่าใครเคยเจอ bug 'ผ่านข้อมูลเข้าไปแล้วมันเปลี่ยน' (mutate input) แล้วสะพานไปหน้า refactor")

# 6 refactor
s = slide()
title_bar(s, "จาก Action สู่ Calculation", "หัวใจของวันนี้ — แยก 'การคำนวณ' ออกจาก 'การทำลงโลกภายนอก'")
code_box(s, CODE_BAD, 0.6, 1.85, 5.9, 2.5, size=12, label="ปนกัน", label_color=BAD)
code_box(s, CODE_GOOD, 6.85, 1.85, 5.9, 2.5, size=12, label="แยกแล้ว", label_color=GOOD)
bullets(s, [
    {"t": "Discounted เป็น calculation แท้: ไม่พิมพ์ ไม่แก้ input ไม่ถามเวลา", "level": 0, "size": 16, "space": 5},
    {"t": "action ไม่หายไปไหน — ถูก 'ย้ายไปไว้ที่ขอบ' ของระบบ ตรงที่ต้องเกิดจริงเท่านั้น", "level": 0, "size": 16, "space": 5},
], y=4.7)
takeaway(s, "แยกแล้วง่ายขึ้น: calculation เทสต์เองได้ · action เหลือบาง ๆ จุดเดียว")
notes(s, "[0:15] พิมพ์สดหรือสลับหน้าจอ go-fp/02 จุดสำคัญคือ 'ย้ายไปขอบ' — FP ไม่ได้แปลว่ากำจัด side effect แต่จัดที่อยู่ให้มัน ถามต่อ: LogDiscount ยังเทสต์ยากไหม? → ยาก แต่เล็กและไม่มีความรู้ธุรกิจอยู่ข้างในแล้ว")

# 7 test
s = slide()
title_bar(s, "ผลลัพธ์: ทดสอบได้โดยไม่ต้อง mock อะไรเลย")
code_box(s, CODE_TEST, 0.6, 1.8, 12.15, 3.5, size=14)
bullets(s, [
    {"t": "เทียบกับตอนก่อน: เทสต์ ApplyDiscount ต้องจับ stdout + เช็คว่า input โดนแก้ — เทสต์กลายเป็นงานโบราณคดี", "level": 0, "size": 16, "space": 5},
    {"t": "calculation ที่ pure = เทสต์เป็นตาราง input → output ได้เลย — กติกาธุรกิจทั้งหมดอยู่ตรงนี้", "level": 0, "size": 16, "space": 5},
], y=5.55)
takeaway(s, "อยากรู้ว่าโค้ดส่วนไหน 'ควรแยก' — ดูว่าการเทสต์มันต้อง mock อะไร ยิ่งเยอะ ยิ่งแปลว่า action ปนอยู่")
notes(s, "[0:25] รันเทสต์ให้เห็นเขียว ตาราง 3 แถวนี้คือ spec ของกติกาส่วนลด — QA/PM อ่านออกด้วย นี่คือเหตุผลที่ calculation คู่ควรกับการถูกแยกออกมา")

# 8 HOF
s = slide()
title_bar(s, "เครื่องมือ 1: ฟังก์ชันเป็นค่า (Higher-order Functions + Closures)",
          sub="Go ส่งฟังก์ชันเป็น argument / คืนฟังก์ชันได้เต็มรูปแบบ — std lib ใช้เยอะแล้ว: sort.Slice, http.HandleFunc")
code_box(s, CODE_HOF, 0.6, 2.05, 12.15, 4.0, size=14)
takeaway(s, "closure จำบริบทตอนถูกสร้าง → นี่คือวิธี Go ทำ partial application (verbose กว่าภาษา ML ชัดเจน — และนี่คือเหตุผลที่ Go ไม่มี pipe operator)")
notes(s, "[0:40] ให้ผู้เรียนเดาลายเซ็น Curry2 ก่อนเฉลย (โค้ดเต็ม + เทสต์: go-fp/04) ใครถาม 'ทำไม Go ไม่มี lambda สั้น ๆ' → ตอบตรง ๆ ว่า verbose by design และ (value, error) ทำ chain ยาก")

# 9 loop var
s = slide()
title_bar(s, "กับดักของ closure: loop variable", sub="closure จับ 'ตัวแปร' ไม่ใช่ 'ค่า' — เว้นแต่ Go 1.22 เป็นต้นไป")
code_box(s, CODE_LOOPVAR, 0.6, 1.75, 12.15, 4.3, size=14)
takeaway(s, "โค้ดเก่าก่อน 1.22 ยังมีรอยแก้ i := i ทิ้งไว้ — อ่านเจอแล้วอย่าลบทิ้งโดยไม่รู้ว่ามันกันอะไร")
notes(s, "[0:50] ถ้ามีเวลา รันสดเทียบ Go เก่า/ใหม่ (gotip) เชื่อมกลับกรอบ ACD: goroutine คือ action, ตัวแปรที่ถูกจับร่วมคือ data ที่แชร์โดยไม่ตั้งใจ")

# 10 generics
s = slide()
title_bar(s, "เครื่องมือ 2: Generics — เขียน Map / Filter / Reduce เองได้",
          sub="Go 1.18+ · โค้ดเต็ม + เทสต์แบบ TDD ใน go-fp/03-fp-toolkit")
code_box(s, CODE_GENERICS, 0.6, 2.05, 12.15, 3.7, size=14)
bullets(s, [
    {"t": "Go ไม่มี built-in map/filter — และ Go community ก็นิยม for loop ตรง ๆ", "level": 0, "size": 15, "space": 5},
    {"t": "โค้ดชุดนี้คือเครื่องมือ 'เรียนรู้ concept' — ในงานจริงใช้เมื่อมันทำให้เจตนาของโค้ดอ่านออกง่ายขึ้น", "level": 0, "size": 15, "space": 5},
], y=5.95)
takeaway(s, "Reduce ที่ accumulator ต่าง type กับสมาชิก (Reduce[Item, int]) คือจุดที่ generics ช่วยจริง")
notes(s, "[0:52] แนะให้เปิด fp_test.go เป็นตัวอย่าง TDD — เขียนเทสต์ก่อนแล้วเห็นลายเซ็น generic ทีละขั้น ใครถาม performance: for loop ตรง ๆ ชนะเสมอ ไม่มี magic")

# 11 options
s = slide()
title_bar(s, "Functional Options — pattern ที่คุณใช้อยู่แล้ว",
          sub="closure + higher-order function ในโค้ด production จริง: grpc-go, zap, aws-sdk-go-v2")
code_box(s, CODE_OPTIONS, 0.6, 2.05, 12.15, 3.7, size=14)
bullets(s, [
    {"t": "WithPort(9090) คือ 'ฟังก์ชันที่คืน action เล็ก ๆ' เอาไว้ยิงใส่ constructor ตอนหลัง", "level": 0, "size": 15, "space": 5},
    {"t": "ทำไมไม่ใช้ struct config? — options ขยายได้โดยไม่ทำ breaking change และ default ชัดเจน", "level": 0, "size": 15, "space": 5},
], y=5.95)
takeaway(s, "คุณเขียน FP อยู่แล้วโดยไม่รู้ตัว — งานวันนี้แค่ตั้งชื่อให้สิ่งที่ทำอยู่")
notes(s, "[1:05] aha moment ของวัน: คนที่ใช้ zap.New(...WithFields) มาตลอดจะเห็นว่ามันคือ pattern เดียวกับ Adder/Curry2 เพิ่งเรียน — เดินหน้านี้สั้น ๆ แล้วไป middleware")

# 12 middleware
s = slide()
title_bar(s, "Middleware = Function Composition",
          sub="http.Handler เป็น function เดียว → wrapper ครอบซ้อนกันคือ composition แบบ Go")
code_box(s, CODE_MIDDLEWARE, 0.6, 2.05, 12.15, 4.0, size=12)
takeaway(s, "ลำดับของ Chain(Logger, Recover) มีความหมาย — composition คือ 'ลำดับ = ความหมาย'")
notes(s, "[1:10] ถ้าเวลาเหลือน้อย ตัดหน้านี้ทั้งหน้าได้ (พูดประโยคเดียว: 'middleware คือการเอาฟังก์ชันมาคู่กัน ลำดับมีความหมาย') แล้วกระโดดไปของหวาน — ไม่กระทบเรื่องเล่า")

# 13 iter
s = slide()
title_bar(s, "ของหวาน: Lazy Sequence ด้วย iter.Seq (Go 1.23+)",
          sub="อนุกรมไม่รู้จบที่คำนวณเท่าที่ถูกขอ — range-over-func ในภาษา Go เอง")
code_box(s, CODE_ITER, 0.6, 1.85, 12.15, 4.35, size=13)
takeaway(s, "Fibonacci ไม่มีจุดจบ แต่ Take(10) คำนวณแค่ 10 ตัว — lazy คือคำนวณ 'เท่าที่จำเป็น' ไม่ใช่ 'ทั้งหมดก่อนแล้วค่อยตัด'")
notes(s, "[1:25] โชว์อย่างเดียว ไม่ลงลึก: yield คืน false = ผู้อ่านสั่งหยุด ทำให้ infinite sequence ปลอดภัย แถมขำ: int ยัง overflow ถ้าดันอ่านไกล — ของจริงไม่มีอะไร infinite หน้านี้ตัดได้ถ้าเวลาโดนตัด แต่เป็นของที่คนจำได้นาน พยายามรักษาไว้")

# 14 สรุป
s = slide()
title_bar(s, "สรุป: 3 คำถามกับโค้ดทุกบรรทัด")
table(s, [
    ["ถาม", "ถ้าคำตอบคือ...", "แล้วทำอะไร"],
    ["\"ผลขึ้นกับเวลา/จำนวนครั้งไหม?\"", "ใช่ → Action", "ย้ายไปไว้ขอบระบบ ทำให้บางที่สุด"],
    ["\"input เดิม ให้ผลเดิมเสมอไหม?\"", "ใช่ → Calculation", "ทำให้ pure + เขียน table-driven test"],
    ["\"เป็นแค่ข้อเท็จจริงที่ส่งต่อกันไหม?\"", "ใช่ → Data", "ใช้ immutable เท่าทำได้ (value semantics)"],
], x=0.6, y=1.6, w=12.15, h=2.7, col_widths=[4.2, 2.6, 5.35], size=14)
bullets(s, [
    {"t": "Go ทำได้ดี: HOF · closures · generics (1.18+) · iter.Seq (1.23+)", "level": 0, "size": 16},
    {"t": "Go ไม่มี: built-in map/filter · immutability guarantee · tail-call optimization — รู้ขีดจำกัด แล้วออกแบบรอบมัน", "level": 0, "size": 16},
], y=4.55)
takeaway(s, "ไม่ต้องเขียน FP ทั้งวัน — แค่หมั่นย้าย calculation ออกจาก action ทีละฟังก์ชัน")
notes(s, "[1:40] ปิดเนื้อหาด้วยกรอบเดียว: 3 คำถามนี้คือสิ่งที่อยากให้จำกลับบ้าน — การบ้านคือโอกาสฝึกใช้มันหน้าเดียว")

# 15 การบ้าน
s = slide()
title_bar(s, "การบ้าน: แยกคูปองออกจากการส่งอีเมล",
          sub="โจทย์จาก Grokking Simplicity บท 3–5 พอร์ตเป็น Go — repo: go-fp/07-coupon-email-exercise (มี EXERCISE.md ประกอบ)")
code_box(s, CODE_COUPON, 0.6, 2.05, 6.6, 4.5, size=12, label="starter/coupons.go — จุดตั้งต้น", label_color=BAD)
tb, tf = textbox(s, 7.5, 2.1, 5.3, 4.5)
put(tf, "โจทย์ของคุณ", size=18, bold=True, color=ACCENT, first=True, space_after=6)
for i, t in enumerate([
    "แยก Actions / Calculations / Data ให้ครบ",
    "ดึง FindApplicableCoupons ออกมา — เขียน table-driven test ก่อน implementation",
    "เหลือ SendCouponEmail เป็น action บาง ๆ",
    "ทำเสร็จค่อยเปิดดู solution/ ใน repo",
]):
    put(tf, f"{i+1}. {t}", size=15, space_after=8)
put(tf, "กติกาโจทย์: เงินเป็นบาทเต็มไม่ติดลบ · coupon ไม่มีหมวด = ใช้ได้ทุกหมวด · รักษาลำดับเดิม", size=13, color=MUTED, italic=True)
takeaway(s, "เป้าหมาย: กติกาธุรกิจทั้งหมดอยู่ใน calculation ที่เทสต์ได้ โดยไม่ต้องแตะ I/O")
notes(s, "[1:48] มอบการบ้าน: ใช้เวลา ~20 นาที ใบ้จุดพลาดบ่อยไว้ด้วย — (1) ลืมรักษาลำดับคูปองเดิม (2) return slice ใหม่แต่ mutate element ข้างใน (ยังไม่ pure) (3) แอบเอาการหา coupon กลับเข้าไปใน action ครั้งหน้าเปิดเฉลยพร้อมกัน")

# 16 อ่านต่อ
s = slide()
title_bar(s, "อ่านต่อ")
bullets(s, [
    {"t": "Grokking Simplicity — Eric Normand (Manning 2021) · โฟกัส ch.3–5 (ACD), ch.6–7 (immutability), ch.10–14 (first-class functions)", "level": 0, "size": 17},
    {"t": "Functional Programming in Go — Dylan Meeus (Packt 2023)", "level": 0, "size": 17},
    {"t": "Go blog: Range Over Function Types (Go 1.23) — go.dev/blog/range-functions", "level": 0, "size": 17},
    {"t": "Codewalk: First-Class Functions in Go — go.dev/doc/codewalk/functions", "level": 0, "size": 17},
    {"t": "โค้ดทั้งหมดในวันนี้ (พร้อมเทสต์): ~/src/go-fp — go test ./... ผ่านทุก package", "level": 0, "size": 17, "bold": True},
], y=1.8)
tb, tf = textbox(s, 0.6, 6.3, 12.1, 0.7)
put(tf, "ขอบคุณครับ 🙏 — คำถามได้ตลอด", size=20, bold=True, color=ACCENT, first=True)
notes(s, "เผื่อ Q&A: (1) ทำไม Go ไม่มี pipe operator → verbose by design + (value, error) ทำ chain ยาก (2) copy-on-write แพงไหม → benchmark ใน go-fp/08: struct เล็กต่างกัน ~0.05 ns/op (3) goroutine/channel เข้ากรอบไหน → channel คือ data, การส่ง/รับคือ action (4) ใครถาม monad → วันนี้ไม่จำเป็น แนะนำหนังสือต่อ")

out = "/home/weerasak/src/go-fp/slides/fp-in-go-workshop.pptx"
prs.save(out)
print("saved", out, "slides:", len(prs.slides._sldIdLst))
