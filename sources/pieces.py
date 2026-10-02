"""Fabrique le rôle de matière et la porte de chaque nœud à partir de l'index des nœuds :
`python pieces.py` (Présentation N°1 : index.json -> vue3d/pieces.json) ou
`python pieces.py armoire` (armoire-index.json -> vue3d/pieces-armoire.json) ou
`python pieces.py casier` (casier-index.json -> vue3d/pieces-casier.json) ou
`python pieces.py pro` (pro-index.json -> vue3d/pieces-pro.json)."""
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

# Casier V 1200 : clavier connecté Boks (pièces FIEVEL, film du clavier texturé) sur le montant droit, fixe.
# Boulonnés sur la porte hors de son assemblage : support de gâche, crochet de serrure (SUOGOU), ferrure U1
# de la tige d'arrêt et les 4 écrous M4 de premier niveau. b2 = tige d'arrêt Ø4 et son écrou borgne.
def role_casier(ch):
    if "[façade]" in ch: return "porteFace"
    piece = ch.split(" / ")[-1]
    for motif, r in [(r"KEYPAD FOIL", "facade"), (r"FIEVEL|Fievel|Battery|AAA|Export STEP|BAYONET", "clavier"),
                     (r"PORTE P1|PORTE RENF|PT OMEG|ZED", "porte"),
                     (r"CT (DROIT|GAUCHE)|TOIT|COTE RENF|PAN |FOND|MT (DROIT|GAUCHE)|TRAV|FACE P|P7|VISIERE|PIED", "panneau"),
                     (r"INOX|SERRURE|^0\d-|GB8\d\d|^S0-|M3X6|SCREW|ARRET|AXE|PALIER|PENNE|PT L1|Ø", "inox")]:
        if re.search(motif, piece): return r
    return "alu"
def porte_casier(ch):
    piece = ch.split(" / ")[-1]
    if re.search(r"ARRET PT Ø4|M4 BORGNE", piece): return "b2"
    if "1021 PORTE ASS2" in ch or "SUOGOU" in ch or "SUP GACHE" in piece or "ARRET  PT U1" in piece: return "g"
    if ch == "ECROU M4  A COLERETTE INOX A2": return "g"
    return ""

# Armoire PRO : même clavier que la N°1 (CLAVIER COMPLET, sur le montant droit, fixe) ; la ferrure U1 de la
# tige d'arrêt et sa rondelle sont sur la porte ; b2 = tige d'arrêt Ø4, dont le bout coulisse dans le plafond.
def role_pro(ch):
    if "[façade]" in ch: return "porteFace"
    if "CLAVIER COMPLET" in ch: return role(ch)
    piece = ch.split(" / ")[-1]
    for motif, r in [(r"ARTI|RESSORT|PALIER|A2", "inox"), (r"PORTE (P\d|OMEGA)", "porte"),
                     (r"CORPS P|PAN |FACE|PIED|PLAT  PRO", "panneau"),
                     (r"SERRURE JIEKAI|^0\d-|GB8\d\d|^S0-|M3X6|ARRET|ECROU M4 SP", "inox")]:
        if re.search(motif, piece): return r
    return "alu"
def porte_pro(ch):
    piece = ch.split(" / ")[-1]
    if "ARRET PT Ø4" in piece: return "b2"
    if "D1021-00-PORTE ASS2" in ch or ("ARRET PORTE ASS1" in ch and re.search(r"U1|RONDELLE", piece)): return "g"
    return ""

if nom == "hub":
    idx = json.load(open("index.json"))
    sortie = {i["noeud"]: [role(i["chemin"]), porte(i["chemin"])] for i in idx}
    chemin = "../vue3d/pieces.json"
elif nom == "armoire":
    idx = json.load(open(f"{nom}-index.json"))
    sortie = {i["noeud"]: [role_armoire(i["chemin"]), porte_armoire(i["chemin"])] + ([1] if detail_armoire(i["chemin"]) else []) for i in idx}
    chemin = f"../vue3d/pieces-{nom}.json"
elif nom == "pro":
    idx = json.load(open(f"{nom}-index.json"))
    sortie = {i["noeud"]: [role_pro(i["chemin"]), porte_pro(i["chemin"])] for i in idx}
    chemin = f"../vue3d/pieces-{nom}.json"
else:
    idx = json.load(open(f"{nom}-index.json"))
    sortie = {i["noeud"]: [role_casier(i["chemin"]), porte_casier(i["chemin"])] for i in idx}
    chemin = f"../vue3d/pieces-{nom}.json"
json.dump(sortie, open(chemin, "w"), separators=(",", ":"))
print(len(idx), "nœuds ->", chemin)
