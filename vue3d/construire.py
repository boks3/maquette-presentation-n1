"""Construit la vue 3D autonome à partir de vue3d/gabarit.html :
- ../index.html : page complète (GitHub Pages) ;
- artifact.html : même page sans <html>/<head>/<body>, pour une page Claude (artifact).
Les deux maquettes (sources/hub.glb = Présentation N°1, sources/armoire.glb = Armoire V 1800),
la texture du clavier (sources/clavier_tex.png) et les listes de pièces (vue3d/pieces.json,
vue3d/pieces-armoire.json) sont intégrées en base64 : la page ne charge que three.js (jsDelivr)."""
import base64, pathlib
d = pathlib.Path(__file__).resolve().parent
src = d.parent / "sources"
s = (d / "gabarit.html").read_text()
s = s.replace("__PIECES__", (d / "pieces.json").read_text())
s = s.replace("__TEX__", "data:image/png;base64," + base64.b64encode((src / "clavier_tex.png").read_bytes()).decode())
s = s.replace("__GLB__", base64.b64encode((src / "hub.glb").read_bytes()).decode())
s = s.replace("__PIECES_ARMOIRE__", (d / "pieces-armoire.json").read_text())
s = s.replace("__GLB_ARMOIRE__", base64.b64encode((src / "armoire.glb").read_bytes()).decode())
(d / "artifact.html").write_text(s)
tete = ('<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="robots" content="noindex, nofollow">\n'
        '<style>html{color-scheme:light}body{margin:0}[hidden]{display:none!important}'
        ':root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>\n')
i = s.index("<header")
(d.parent / "index.html").write_text(tete + s[:i] + "</head>\n<body>\n" + s[i:] + "\n</body>\n</html>\n")
print("index.html et artifact.html :", round(len(s) / 1e6, 2), "Mo")
