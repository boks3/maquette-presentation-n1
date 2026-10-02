"""Fabrique le rôle de matière et la porte de chaque nœud à partir de l'index des nœuds :
`python pieces.py` (Présentation N°1 : index.json -> vue3d/pieces.json) ou
`python pieces.py armoire` (armoire-index.json -> vue3d/pieces-armoire.json)."""
import json, re, sys
nom = sys.argv[1] if len(sys.argv) > 1 else "hub"

def role(ch):
    if "[façade]" in ch: return "porteFace"
    for motif, r in [(r"CHARNIERE", "inox"), (r"SYSTEME_CLAVIER", "facade"), (r"CORPS4_1", "vitre"), (r"CORPS(5|6|11|12)_1", "touche"),
                     (r"CLAVIER", "clavier"), (r"BOITIER", "boitier"), (r"PORTE|PORTILLON", "porte"), (r"PAN ", "panneau")]:
        if re.search(motif, ch): return r
    return "alu"
def porte(ch):
    return "g" if "PORTE GAUCHE" in ch else "d" if "PORTE DROITE ASS1" in ch else ""

# Armoire V 1800 : le nom de la pièce (dernier maillon du chemin) suffit. Rivets laqués = teinte des panneaux ;
# zingué = alu ; serrure JIEKAI (pièces 0x-…, GB…, S0-…) et visserie inox = inox ; galets PA6 = touche (plastique).
def role_armoire(ch):
    if "[façade]" in ch: return "porteFace"
    piece = ch.split(" / ")[-1]
    for motif, r in [(r"DALLE", "dalle"), (r"LAQUE", "panneau"), (r"POIGNET", "noir"), (r"PA6", "touche"),
                     (r"PORTE (P1|RENF|BOITIER|VISIERE)|PORTE CREMONE", "porte"),
                     (r"PAN |FACE |VISIERE|SERIGRAPH", "panneau"),
                     (r"INOX|SERRURE|^0\d-|GB8\d\d|^S0-|ARRET PT|GUIDE|PALIER|AXE|CAME|GACHE|PÊNE|CREMONE|BUTEE", "inox")]:
        if re.search(motif, piece): return r
    return "alu"
# Ce qui tourne avec la porte sans être rangé dans son assemblage : les supports de sérigraphie et,
# côté porte, le compas d'arrêt (ferrure L1, son axe et les écrous des goujons de la porte).
# Le compas lui-même : b1 = bras C1 (pivote sur l'armoire), b2 = bras C2 (pivote sur la porte).
def porte_armoire(ch):
    piece = ch.split(" / ")[-1]
    if "1070 PORTE ASS2" in ch or "SERIGRAPH" in piece: return "g"
    if ch == "BOKS 1 D V1800   1200 ARMOIRE V 1800  ASS1 / ECROU M6 INOX A2 NYLSTOP": return "g"
    if "1069 ARRET DE PORTE" in ch:
        if re.search(r"ARRET PT L1|SIX PANS INOX  6X10|M6 BORGNE", piece): return "g"
        if "ARRET PT C2" in piece: return "b2"
        return "b1"
    return ""
def detail_armoire(ch):  # vue « Serrure » : poignée et barillet
    return 1 if re.search(r"POIGNET|SERRURE JIEKAI    010", ch) else 0

if nom == "hub":
    idx = json.load(open("index.json"))
    sortie = {i["noeud"]: [role(i["chemin"]), porte(i["chemin"])] for i in idx}
    chemin = "../vue3d/pieces.json"
else:
    idx = json.load(open(f"{nom}-index.json"))
    sortie = {i["noeud"]: [role_armoire(i["chemin"]), porte_armoire(i["chemin"])] + ([1] if detail_armoire(i["chemin"]) else []) for i in idx}
    chemin = f"../vue3d/pieces-{nom}.json"
json.dump(sortie, open(chemin, "w"), separators=(",", ":"))
print(len(idx), "nœuds ->", chemin)
