"""Prépare la texture du clavier : rogne l'ombre transparente de l'image d'origine,
pose la face sur un fond noir (le boîtier) et la met en 704 x 2048 px."""
from PIL import Image
im = Image.open("clavier-original.png").convert("RGBA")
boite = im.split()[3].point(lambda v: 255 if v > 200 else 0).getbbox()
face = im.crop(boite)
fond = Image.new("RGBA", face.size, (18, 19, 20, 255)); fond.alpha_composite(face)
fond.convert("RGB").resize((704, 2048), Image.LANCZOS).save("clavier_tex.png")
print("rognage", boite, "rapport", round(face.size[0] / face.size[1], 3), "(pièce SYSTEME_CLAVIER : 38 x 113 mm = 0,336)")
