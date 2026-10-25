"""Smallest possible OCR smoke test, with unbuffered progress prints."""
import sys
import time

t0 = time.time()


def say(msg):
    print(f"[{time.time() - t0:6.1f}s] {msg}", flush=True)


pdf = sys.argv[1] if len(sys.argv) > 1 else None
page = int(sys.argv[2]) if len(sys.argv) > 2 else 2
dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 150
out_png = sys.argv[4] if len(sys.argv) > 4 else None

say(f"start pdf={pdf} page={page} dpi={dpi}")
import pymupdf
say(f"pymupdf {pymupdf.__doc__}")

doc = pymupdf.open(pdf)
say(f"opened: {doc.page_count} pages")
pg = doc.load_page(page - 1)
say(f"page rect {pg.rect.width:.0f}x{pg.rect.height:.0f} pt")
pix = pg.get_pixmap(dpi=dpi)
say(f"rendered {pix.width}x{pix.height} px, {len(pix.samples)} bytes")
png = out_png or f"_ocr_smoke_p{page}.png"
pix.save(png)
doc.close()
say(f"saved {png}")

say("importing rapidocr")
from rapidocr_onnxruntime import RapidOCR
say("constructing engine")
engine = RapidOCR()
say("engine ready")
t1 = time.time()
result, elapse = engine(png)
say(f"ocr done in {time.time() - t1:.1f}s (engine-reported: {elapse})")
rows = result or []
say(f"lines: {len(rows)}")
for row in rows[:8]:
    say(f"  {row[2]:.3f}  {row[1]}")
