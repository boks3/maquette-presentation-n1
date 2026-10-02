# Maquette Présentation N°1

Maquette 3D interactive du caisson **C0042-26091-D1100-00 « PRÉSENTATION N°1 »** (export
SolidWorks 2025 du 02/10/2026), avec ses photos de présentation.

- **Page en ligne** : https://boks3.github.io/maquette-presentation-n1/ (GitHub Pages, branche `main`, racine).
- **Même page sur claude.ai** (privée) : https://claude.ai/artifact/ForGWMwGuv6tCGHkxbJ4kb

🔴 **Ce dépôt est public.** Tout ce qui est ici (maquette 3D, photos) est visible et téléchargeable
par n'importe qui. Le fichier **STEP d'origine n'y est pas** et ne doit pas y venir (`.gitignore`) :
il reste sur les postes de l'équipe. Une fois les essais finis : Settings → General → passer en privé
ou supprimer le dépôt.

## Ce qu'il y a

| Chemin | Contenu |
|---|---|
| `index.html` | La page en ligne : autonome (maquette, texture et pièces intégrées en base64), seul three.js 0.186.1 vient de jsDelivr. Générée, ne pas l'éditer à la main. |
| `vue3d/gabarit.html` | Le code de la page (vue, portes, points de vue, teintes). C'est lui qu'on modifie. |
| `vue3d/construire.py` | Construit `index.html` (et `vue3d/artifact.html` pour claude.ai) depuis le gabarit. |
| `vue3d/pieces.json` | Pour chaque nœud de la maquette : sa matière et sa porte (`g`, `d` ou rien). |
| `photos/` | Les 9 photos en 2400 × 1600 : fermé, ouvert à 100° sous 4 angles, entrouvert à 45°, détail et gros plan du clavier. |
| `sources/lire.py` | Lit le STEP et liste les pièces avec leur encombrement (repérage). |
| `sources/maillage.py` | Convertit le STEP en `hub.glb` (mètres, Y vers le haut) + `index.json` (nom de chaque nœud). Bouche les perçages < 25 mm des portes, du portillon et du boîtier ; sépare la façade des portes (`[façade]`). |
| `sources/pieces.py` | Refait `vue3d/pieces.json` depuis `index.json`. |
| `sources/preparer_clavier.py` | Prépare la texture du clavier Boks (`clavier-original.png` → `clavier_tex.png`). |
| `sources/scene.html`, `photos.mjs`, `vues.json` | Rendu des photos dans Chrome sans interface (three.js) ; `vues.json` = les 9 points de vue. |
| `sources/reduire.py` | Réduit les rendus doubles (4800 × 3200) en photos 2400 × 1600. |

## Refaire sur un Mac

```sh
cd sources
python3 -m venv .venv && .venv/bin/pip install cadquery-ocp trimesh numpy pillow   # ~1,3 Go (OpenCascade)
npm ci                                                                            # three + playwright-core

# 1. STEP -> maquette 3D (le STEP reste hors du dépôt)
.venv/bin/python maillage.py ~/chemin/C0042-26091-D1100-00_PRESENTATION_N_1.STEP
.venv/bin/python pieces.py
# 2. (si l'image du clavier change) texture
.venv/bin/python preparer_clavier.py
# 3. photos
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" node photos.mjs "$(cat vues.json)" 2400x1600
#    -> sources/photos/*.png (à copier dans ../photos si elles conviennent)
# 4. page 3D
cd .. && python3 vue3d/construire.py && git add -A && git commit && git push   # Pages republie tout seul
```

Sous Linux sans carte graphique (conteneur cloud), Chrome rend en logiciel (SwiftShader) et son
anticrénelage laisse des pointillés sur les portes : rendre en double sans anticrénelage puis réduire :
`AA=0 DOS=hd node photos.mjs "$(cat vues.json)" 4800x3200 && .venv/bin/python reduire.py hd ../photos`.

## Choix faits (le fichier ne les donne pas)

- **Teintes** : le STEP n'a aucune couleur. Panneaux et portes anthracite RAL 7016, structure alu,
  charnières inox, clavier noir ; la page propose aussi RAL 7035, 9016 et 9005. Teintes d'illustration.
- **Toit** : ajouré (lattes), tel que dessiné : la moitié de sa surface est ouverte dans la maquette.
- **Portes** : elles pivotent sur l'axe des charnières tiré des cotes (gauche x = −2 090 mm, droite
  x = −18 mm, z = 3 086,9 mm), vers l'extérieur ; les charnières restent fixes.
- **Clavier** : l'image du clavier Boks est plaquée sur la pièce `SYSTEME_CLAVIER` (38 × 113 mm).
- **Trous** : 205 perçages de fixation (< 25 mm) bouchés sur les portes, le portillon et le boîtier ;
  la découpe du clavier et l'ouverture du portillon restent.
- **Façade des portes** : ses triangles très fins ont des normales penchées jusqu'à 7° ; la page et le
  rendu les forcent planes (nœuds `[façade]`).

Encombrement : 2 170 mm (largeur) × 2 170 mm (profondeur, hors charnières) × 2 106 mm (hauteur).
