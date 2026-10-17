# -*- coding: utf-8 -*-
"""ดึง speaker notes จากเด็ค แล้วทำเป็น PDF (ผ่าน HTML → LibreOffice)"""
import html
import subprocess
from pptx import Presentation

DECK = "/home/weerasak/src/go-fp/slides/fp-in-go-workshop.pptx"
HTML = "/home/weerasak/src/go-fp/slides/speaker-notes.html"
PDF = "/home/weerasak/src/go-fp/slides/speaker-notes.pdf"

prs = Presentation(DECK)
rows = []
for i, s in enumerate(prs.slides, 1):
    title = ""
    notes = ""
    for sh in s.shapes:
        if sh.has_text_frame and not title:
            t = sh.text_frame.text.strip()
            if t:
                title = t.split("\n")[0]
    if s.has_notes_slide:
        notes = s.notes_slide.notes_text_frame.text.strip()
    rows.append((i, title or "—", notes))

parts = ["""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
@page { size: A4; margin: 1.8cm; }
body { font-family: "Ubuntu", "Noto Sans Thai Looped", sans-serif; font-size: 10.5pt; color: #0f172a; }
h1 { font-size: 17pt; border-bottom: 2.5pt solid #0d9488; padding-bottom: 4pt; }
.meta { color: #64748b; font-size: 9pt; margin-bottom: 14pt; }
.slide { margin-bottom: 12pt; page-break-inside: avoid; }
.num { display: inline-block; background: #0d9488; color: white; font-weight: bold;
       padding: 1pt 7pt; border-radius: 4pt; font-size: 9.5pt; }
.title { font-weight: bold; font-size: 11.5pt; margin-left: 5pt; }
.notes { margin: 3pt 0 0 30pt; color: #334155; line-height: 1.45; }
</style></head><body>
<h1>Speaker Notes — Explore Functional Programming in Go</h1>
<div class="meta">เวิร์กชอป 2 ชม. · 16 สไลด์ · ตัวเลขใน [วงเล็บ] = นาทีบน timeline (0:00–2:00) · เด็ค: ~/src/go-fp/slides/fp-in-go-workshop.pptx</div>
"""]
for i, title, notes in rows:
    parts.append(f'<div class="slide"><span class="num">{i}</span>'
                 f'<span class="title">{html.escape(title)}</span>'
                 f'<div class="notes">{html.escape(notes) if notes else "<i>(ไม่มีโน้ต)</i>"}</div></div>')
parts.append("</body></html>")

with open(HTML, "w", encoding="utf-8") as f:
    f.write("\n".join(parts))

subprocess.run(["soffice", "--headless", "--convert-to", "pdf",
                "--outdir", "/home/weerasak/src/go-fp/slides", HTML],
               check=True, capture_output=True)
print("pages:", len(rows), "->", PDF)
