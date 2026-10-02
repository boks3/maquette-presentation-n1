"""Réduit les rendus de hd/ (4800 x 3200) en photos/ (2400 x 1600) : suréchantillonnage."""
from PIL import Image
import glob, os, sys
src, dst = (sys.argv[1:3] + ["hd", "../photos"])[:2] if len(sys.argv) > 1 else ("hd", "../photos")
os.makedirs(dst, exist_ok=True)
for f in sorted(glob.glob(f"{src}/*.png")):
    Image.open(f).convert("RGB").resize((2400, 1600), Image.LANCZOS).save(f"{dst}/{os.path.basename(f)}", optimize=True)
    print(os.path.basename(f))
