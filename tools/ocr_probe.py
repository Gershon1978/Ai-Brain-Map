"""Probe what OCR capability exists on this machine. Read-only."""
import importlib.util as u
import shutil
import sys

print("python:", sys.version.split()[0], sys.executable)

for m in ["fitz", "rapidocr_onnxruntime", "easyocr", "pytesseract", "PIL", "numpy", "onnxruntime", "cv2"]:
    print(f"  {m:22s} {bool(u.find_spec(m))}")

for exe in ["tesseract", "pdftotext", "pdftoppm", "magick", "ollama"]:
    print(f"  {exe:22s} {shutil.which(exe)}")

try:
    import fitz
    print("pymupdf:", fitz.version)
except Exception as exc:  # pragma: no cover
    print("pymupdf: MISSING", exc)
