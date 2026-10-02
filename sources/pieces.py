"""Fabrique vue3d/pieces.json (rôle de matière et porte de chaque nœud) à partir de index.json."""
import json, re
idx = json.load(open("index.json"))
def role(ch):
    if "[façade]" in ch: return "porteFace"
    for motif, r in [(r"CHARNIERE", "inox"), (r"SYSTEME_CLAVIER", "facade"), (r"CORPS4_1", "vitre"), (r"CORPS(5|6|11|12)_1", "touche"),
                     (r"CLAVIER", "clavier"), (r"BOITIER", "boitier"), (r"PORTE|PORTILLON", "porte"), (r"PAN ", "panneau")]:
        if re.search(motif, ch): return r
    return "alu"
def porte(ch):
    return "g" if "PORTE GAUCHE" in ch else "d" if "PORTE DROITE ASS1" in ch else ""
json.dump({i["noeud"]: [role(i["chemin"]), porte(i["chemin"])] for i in idx}, open("../vue3d/pieces.json", "w"), separators=(",", ":"))
print(len(idx), "nœuds")
