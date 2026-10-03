"""Construit la vue 3D autonome à partir de vue3d/gabarit.html :
- ../index.html : page complète (GitHub Pages) ;
- artifact.html : même page sans <html>/<head>/<body>, pour une page Claude (artifact).
La texture du clavier (sources/clavier_tex.png, en base64) et les listes de pièces (vue3d/pieces*.json)
sont intégrées à la page. Les maquettes restent des fichiers à part (sources/hub.glb, armoire.glb,
casier.glb…), téléchargés par la page quand on choisit le modèle : on ne charge que ce qu'on regarde.
Pour claude.ai, publier artifact.html avec ces fichiers aux mêmes chemins."""
import base64, json, pathlib
d = pathlib.Path(__file__).resolve().parent
src = d.parent / "sources"
s = (d / "gabarit.html").read_text()
s = s.replace("__PIECES__", (d / "pieces.json").read_text())
s = s.replace("__TEX__", "data:image/png;base64," + base64.b64encode((src / "clavier_tex.png").read_bytes()).decode())
for f in sorted(d.glob("pieces-*.json")):  # pieces-armoire.json -> __PIECES_ARMOIRE__
    s = s.replace("__PIECES_" + f.stem[len("pieces-"):].upper() + "__", f.read_text())
assert "__" + "PIECES" not in s, "liste de pièces manquante"
# inspecteur.html : la même page, avec l'inspecteur et le nom de chaque pièce dans le fichier
noms = {cle: {x["noeud"]: x["chemin"].split(" / ")[-1] for x in json.loads((src / f).read_text())}
        for cle, f in {"n1": "index.json", "armoire": "armoire-index.json", "casier": "casier-index.json",
                       "pro": "pro-index.json", "one": "one-index.json"}.items()}
inspecteur = (s.replace("__INSPECTEUR__", "true").replace("__NOMS__", json.dumps(noms, ensure_ascii=False))
              .replace("<title>Maquettes 3D Boks</title>", "<title>Inspecteur des maquettes Boks</title>"))
s = s.replace("__INSPECTEUR__", "false").replace("__NOMS__", "{}")
(d / "artifact.html").write_text(s.replace("__GLB_EN_TEXTE__", "true"))
# claude.ai ne sert pas les .glb : les mêmes maquettes en base64, à publier aux chemins sources/<nom>.glb.txt
for g in sorted(src.glob("*.glb")) + sorted(src.glob("secours/*.glb")):  # compressées, puis leur secours
    cible = d / "artifact-fichiers" / g.relative_to(src.parent)
    cible.parent.mkdir(parents=True, exist_ok=True)
    cible.with_name(g.name + ".txt").write_text(base64.b64encode(g.read_bytes()).decode())
s = s.replace("__GLB_EN_TEXTE__", "false")
tete = ('<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="robots" content="noindex, nofollow">\n'
        '<style>html{color-scheme:light}body{margin:0}[hidden]{display:none!important}'
        ':root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>\n')
i = s.index("<header")
(d.parent / "index.html").write_text(tete + s[:i] + "</head>\n<body>\n" + s[i:] + "\n</body>\n</html>\n")
(d / "inspecteur-artifact.html").write_text(inspecteur.replace("__GLB_EN_TEXTE__", "true"))  # pour claude.ai, mêmes fichiers .glb.txt
inspecteur = inspecteur.replace("__GLB_EN_TEXTE__", "false"); j = inspecteur.index("<header")
(d.parent / "inspecteur.html").write_text(tete + inspecteur[:j] + "</head>\n<body>\n" + inspecteur[j:] + "\n</body>\n</html>\n")
print("index.html et artifact.html :", round(len(s) / 1e6, 2), "Mo")
