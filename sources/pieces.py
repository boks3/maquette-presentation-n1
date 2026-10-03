"""Fabrique le rôle de matière et la porte de chaque nœud à partir de l'index des nœuds :
`python pieces.py` (Présentation N°1 : index.json -> vue3d/pieces.json) ou
`python pieces.py armoire` (armoire-index.json -> vue3d/pieces-armoire.json) ou
`python pieces.py casier` (casier-index.json -> vue3d/pieces-casier.json) ou
`python pieces.py pro` (pro-index.json -> vue3d/pieces-pro.json) ou
`python pieces.py one` (one-index.json -> vue3d/pieces-one.json)."""
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
    if "MT DROIT ASS1" in ch and "GOUGEON A SERTIR M 4X10" in ch: return "panneau"  # goujons autour du clavier, à la teinte du montant
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
    if "FACE MT DROIT ASS1" in ch and "GOUG-SER-AC-A2-M4X10" in ch: return "panneau"  # goujons autour du clavier, à la teinte du montant (Ziad : « retire les trous »)
    if "CLAVIER COMPLET" in ch:  # vitre au ras du montant : matière qui passe devant (la page)
        r = role(ch); return "vitreAffleurante" if r == "vitre" else r
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

# boksONE S + porte arrière : export Rhino sans noms (« COMPOUND nnn ») -> tout se décide sur l'encombrement
# (`boite`, mm, repère du STEP : Z en haut, façade vers -Y). g = porte avant (pivot à gauche), a = porte arrière
# (charnières à droite). Restent fixes : le montant droit avec le clavier et le barillet, le cadre, la caisse.
def crochet_one(i):  # support de gâche et pièces vissées dessus, après le décalage de 18 mm (maillage.py --deplacer)
    x0, y0, z0, x1, y1, z1 = i["boite"]
    return x0 >= 127 and x1 <= 149 and y0 >= -147 and y1 <= -110 and z0 >= 340 and z1 <= 432
def role_one(i):
    x0, y0, z0, x1, y1, z1 = i["boite"]; dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
    if crochet_one(i): return "panneau" if max(dx, dy, dz) > 50 else "inox"
    if x0 > 115 and x1 < 175 and 495 < z0 < 630 and y0 < -137 and max(dx, dy, dz) < 9: return "cache"  # goujons et écrous autour du clavier
    if 33 < dx < 35 and dy < 2 and 108 < dz < 110: return "facade"                     # film du clavier, 34 x 109
    if x0 > 110 and y0 > -153 and y1 < 10 and 340 < z0 and z1 < 640 and max(dx, dy, dz) > 40: return "clavier"
    if max(dx, dy, dz) < 80: return "inox"                                              # visserie, charnières, barillet
    if 230 < dz < 330 and dx < 10: return "inox"                                        # tringles de la crémone
    if dy < 25 and dx > 200 and dz > 500: return "porte"                                # les deux vantaux
    if porte_one(i) and max(dx, dz) > 150: return "porte"                               # renforts et plaque des portes
    return "panneau"
def porte_one(i):
    x0, y0, z0, x1, y1, z1 = i["boite"]
    if "SUOGOU" in i["chemin"]: return "g"  # crochet JIEKAI rapatrié (maillage.py --rapatrier), vissé sur la porte
    # lèvre de la traverse haute, découpée par maillage.py --couper : sur le produit elle est sur la porte (photo de Ziad)
    if "[coupe]" in i["chemin"]: return "g"
    barillet = x0 > 130 and 455 < z0 and z1 < 490
    clavier = x0 > 110 and 490 < z0 and z1 < 640
    # crochet de la gâche, vissé dans la porte (cotes du « SUP GACHE » de l'armoire PRO) ; le capot de serrure
    # en U juste derrière (cotes du « CAPOT SERRURE » de la PRO) reste sur le montant
    if crochet_one(i): return "g"
    # renfort vertical 73 x 15 x 645 derrière la porte : sur la caisse (Ziad, inspecteur : p243 « ne doit pas suivre la porte »)
    if 70 < x1 - x0 < 76 and z1 - z0 > 600 and y1 - y0 < 20: return ""
    if y0 >= -153 and y1 <= -125.5 and x0 >= -190 and x1 <= 165 and z0 >= 19 and not (barillet or clavier): return "g"
    if y0 >= 212 and y1 <= 249 and x0 >= -187 and x1 <= 160 and z0 >= 19: return "a"
    return ""

if nom == "hub":
    idx = json.load(open("index.json"))
    sortie = {i["noeud"]: [role(i["chemin"]), porte(i["chemin"])] for i in idx}
    chemin = "../vue3d/pieces.json"
elif nom == "armoire":
    idx = json.load(open(f"{nom}-index.json"))
    sortie = {i["noeud"]: [role_armoire(i["chemin"]), porte_armoire(i["chemin"])] + ([1] if detail_armoire(i["chemin"]) else []) for i in idx}
    chemin = f"../vue3d/pieces-{nom}.json"
elif nom == "one":
    idx = json.load(open(f"{nom}-index.json"))
    sortie = {i["noeud"]: [role_one(i), porte_one(i)] for i in idx}
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
