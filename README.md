# Maquettes 3D Boks

Cinq maquettes 3D interactives sur la même page, au choix en tête de page (lien direct : `#n1`, `#armoire`, `#casier`, `#pro`, `#one`) :

- **Bokspark** (Présentation N°1) : caisson **C0042-26091-D1100-00 « PRÉSENTATION N°1 »** (export SolidWorks 2025
  du 02/10/2026), avec ses photos de présentation ;
- **Boks taille XL** (Armoire V 1800) : ensemble **BOKS 1 D V1800 1250 « ARMOIRE V 1800 COMPLETE (rampe étroite) »**
  (export SolidWorks 2022 du 07/05/2023), une porte, serrure à barillet, rampe d'accès. Pas de photos ;
- **Boks taille L** (Casier V 1200) : **BOKS 1 D CASIER V1200 1050 COMPLET** (SolidWorks 2022, 07/05/2023), une porte,
  clavier Boks connecté, serrure à barillet ;
- **Boks taille M** (Armoire PRO) : **C0042-22101-D1060-00 ARMOIRE COMPLETE PRO** (SolidWorks 2022, 14/02/2023), une porte
  sur charnières à ressort, clavier Boks, serrure à barillet ;
- **boksONE taille S** (avec porte arrière) : **« V2 3D BOKS capuchon for rendering back door »**, export **Rhino 7**
  du 30/11/2023 (fichier de rendu, pas l'original SolidWorks), porte avant, porte arrière, clavier Boks connecté.

- **Page en ligne** : https://boks3.github.io/maquette-presentation-n1/ (GitHub Pages, branche `main`, racine).
- **Même page sur claude.ai** (privée) : https://claude.ai/artifact/ForGWMwGuv6tCGHkxbJ4kb

🔴 **Ce dépôt est public.** Tout ce qui est ici (maquette 3D, photos) est visible et téléchargeable
par n'importe qui. Le fichier **STEP d'origine n'y est pas** et ne doit pas y venir (`.gitignore`) :
ils restent sur les postes de l'équipe (vaut pour les deux STEP). Une fois les essais finis : Settings → General → passer en privé
ou supprimer le dépôt.

## Ce qu'il y a

| Chemin | Contenu |
|---|---|
| `index.html` | La page en ligne (~0,55 Mo : code, listes de pièces, texture du clavier). Elle télécharge la maquette du modèle choisi (`sources/*.glb`) et three.js 0.186.1 (jsDelivr). Générée, ne pas l'éditer à la main. Pour l'ouvrir en local, passer par un serveur (`python3 -m http.server`) : en `file://` le navigateur refuse le téléchargement. |
| `vue3d/gabarit.html` | Le code de la page (vue, portes, points de vue, teintes). Ce qui distingue les deux modèles est dans `PRODUITS`. C'est lui qu'on modifie. |
| `vue3d/construire.py` | Construit `index.html` (et `vue3d/artifact.html` pour claude.ai, à publier avec les `sources/*.glb` aux mêmes chemins) depuis le gabarit. |
| `vue3d/pieces.json`, `vue3d/pieces-armoire.json` | Pour chaque nœud : sa matière, ce qui le fait bouger (`g`, `d`, `b1`, `b2` ou rien) et, pour l'armoire, `1` s'il cadre la vue « Serrure ». |
| `photos/` | Les 9 photos en 2400 × 1600 : fermé, ouvert à 100° sous 4 angles, entrouvert à 45°, détail et gros plan du clavier. |
| `sources/lire.py` | Lit le STEP et liste les pièces avec leur encombrement (repérage). |
| `sources/maillage.py` | Convertit un STEP en glTF (mètres, Y vers le haut) + index des nœuds. Sans option : Présentation N°1 (`hub.glb`, `index.json`). Options pour l'armoire : `--z-haut`, maillage allégé, `--sans`. Bouche les perçages < 25 mm ; sépare la façade des portes (`[façade]`). |
| `sources/<modèle>.glb` (`hub`, `one`, `pro`, `casier`, `armoire`) + `*-index.json` | Les maquettes servies, **compressées meshopt** (gltfpack `-cc`, décodeur WebAssembly de three.js) : 4,4 Mo pour les cinq. |
| `sources/secours/<modèle>.glb` | Les mêmes sans compression meshopt (16 Mo) : la page les prend si le navigateur refuse WebAssembly. |
| `sources/pieces.py` | Refait `vue3d/pieces.json` depuis `index.json` ; `pieces.py armoire` (`casier`, `pro`) refait `vue3d/pieces-armoire.json` (…). |
| `sources/preparer_clavier.py` | Prépare la texture du clavier Boks (`clavier-original.png` → `clavier_tex.png`). |
| `sources/scene.html`, `photos.mjs`, `vues.json` | Rendu des photos dans Chrome sans interface (three.js) ; `vues.json` = les 9 points de vue. |
| `sources/reduire.py` | Réduit les rendus doubles (4800 × 3200) en photos 2400 × 1600. |

## Refaire sur un Mac

```sh
cd sources
python3 -m venv .venv && .venv/bin/pip install cadquery-ocp trimesh numpy pillow   # ~1,3 Go (OpenCascade)
npm ci                                                                            # three, playwright-core, gltfpack

# 1. STEP -> maquette 3D (le STEP reste hors du dépôt)
.venv/bin/python maillage.py ~/chemin/C0042-26091-D1100-00_PRESENTATION_N_1.STEP
.venv/bin/python pieces.py
# 1 bis. STEP de l'armoire -> sources/armoire.glb (Z vers le haut dans le fichier ; tôles à picots maillées grossièrement)
.venv/bin/python maillage.py ~/chemin/"BOKS 1 D V1800   1250 ARMOIRE V 1800 COMPLETE (rampe étroite).STEP" \
  --nom armoire-brut --z-haut --facade "^$" --angle 0.5 --petites 50 --normales --minuscules 20 \
  --grossier "PLANCHER|RAMPE P1$|RAMPE -2 P10" --sans "DALLE PRESENTATION"
# 1 ter. Casier V 1200 (déjà en Y vers le haut) et Armoire PRO (Z vers le haut, façade vers +Y)
.venv/bin/python maillage.py ~/chemin/"BOKS 1 D CASIER V1200   1050  COMPLET.STEP" --nom casier-brut \
  --facade "^$" --angle 0.5 --petites 50 --normales --minuscules 25 --sans "Export STEP - Boks  -|AAA Battery"
.venv/bin/python maillage.py ~/chemin/"C0042-22101-D1060-00-ARMOIRE COMPLETE PRO.STEP" --nom pro-brut --axes=-x,z,y \
  --facade "^$" --angle 0.5 --petites 50 --normales --minuscules 15
# 1 quater. boksONE (Rhino : pièces sans nom, découpées volume par volume ; la scène de rendu, à 40 m, est écartée)
.venv/bin/python maillage.py ~/chemin/"V2 3D BOKS capuchon for rendering back door.stp" --nom one-brut --decouper \
  --rapatrier SUOGOU --rap-axes=x,-z,y --rap-dec=-9792.0,-148.1,39330.8 \
  --boite=-260,-800,-60,260,600,800 --axes=x,z,-y --facade "^$" --angle 0.5 --petites 50 --normales --minuscules 15
for n in armoire casier pro one; do mv $n-brut-index.json $n-index.json
  npx gltfpack -i $n-brut.glb -o secours/$n.glb -kn -km && npx gltfpack -i $n-brut.glb -o $n.glb -kn -km -cc && rm $n-brut.glb
  .venv/bin/python pieces.py $n; done
# Bokspark (hub) : secours/hub.glb = sortie brute de maillage.py ; hub.glb = gltfpack -kn -km -cc -vpf (positions non quantifiées)
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

## Comportement de la page

- **Zoom à la molette** : ~25 % par cran, lissé sur quelques images, vers le point visé (celui d'OrbitControls
  avançait de 5 % par cran, d'un bloc). Le pincement sur téléphone reste celui d'OrbitControls.
- **Ombres** : recalculées seulement quand une pièce bouge (porte, changement de modèle), pas quand la caméra
  tourne ou zoome : c'était 75 à 95 % du coût d'une image.
- **« Ouvrir la porte »** : 100°, ou la limite du modèle si elle est plus basse.
- **Chargement** : la maquette compressée d'abord ; en cas d'échec du décodage (WebAssembly refusé), `sources/secours/`.
  Éprouvé dans Chrome avec WebAssembly bloqué exprès : les cinq modèles se chargent depuis `secours/`.

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

🔴 `hub.glb` n'a pas été refait sur le Mac : OpenCascade 8.0.1 (`cadquery-ocp` pour Python 3.14) maille trois
pièces du clavier un peu autrement (±1 % de triangles) que la version de la session cloud. Les noms et
l'ordre des 68 nœuds restent identiques.

## Choix faits pour l'Armoire V 1800

- **Repère** : le STEP est en Z vers le haut, façade vers −X ; `--z-haut` le tourne en Y vers le haut, façade vers +Z, comme la N°1.
- **Dalle de présentation** (4 000 × 2 000 × 100 mm) retirée de la maquette.
- **Volet de la poignée** : ouvert à 90°, tel que dessiné dans le fichier.
- **Porte** : pivote sur l'axe `PORTE GD AXE` (x = 3 007, y = 1 534 mm dans le STEP) ; ouverture limitée à 110° (le fichier ne donne pas la butée).
  Suivent la porte, bien qu'ils soient rangés hors de son assemblage : les deux supports de sérigraphie et, côté porte, la ferrure du compas (L1, son axe, ses écrous).
- **Compas d'arrêt de porte** : C1 pivote sur l'armoire (entretoise ENT 1), C2 sur la porte (axe de la ferrure L1) ; les deux restent alignés et coulissent l'un dans l'autre (`b1`, `b2`).
- **Matières** : panneaux, façade, visière et rivets laqués à la teinte choisie ; pièces zinguées et rampe en alu ; serrure JIEKAI et visserie inox en inox ; poignée noire.
- **Maillage allégé** : pièces de moins de 80 mm simplifiées à 240 triangles ; plancher et rampes (tôle à picots, ~400 bossages chacun) maillés grossièrement plutôt que simplifiés, la simplification les froissait. 397 000 triangles.

Encombrement de l'armoire : 1 459 mm (largeur) × 1 545 mm (profondeur, visière comprise, volet fermé) × 1 909 mm (hauteur sur vérins) ; rampe : 2 056 × 770 mm.

## Choix faits pour le Casier V 1200 et l'Armoire PRO

- **Clavier** : sur le montant droit, fixe (goujons de fixation sur le cadre). L'image du clavier Boks est plaquée
  sur le film du clavier connecté (casier, 34 × 109 mm) et sur `SYSTEME_CLAVIER` (PRO, même clavier que la N°1).
- **Porte** : pivote à gauche (casier : axe `AXE P2` ; PRO : paliers et charnières à ressort). Suivent la porte bien que
  rangés hors de son assemblage : casier, support de gâche, crochet de serrure (SUOGOU), ferrure U1 et 4 écrous M4 ;
  PRO, ferrure U1 et sa rondelle.
- **Tige d'arrêt Ø4** (`b2` + `guide`) : pivote sur la ferrure U1 de la porte et coulisse dans un guide fixé au cadre,
  juste derrière la ferrure (PRO : « FACE ARRET PT » ; casier : « ARRET PT3 ») ; son coude bute contre le guide.
  Ouverture maximale = cette butée : 106° (M), 107° (L). Corrigé le 02/10 sur l'indication de Ziad (« cette partie
  est fixe, la tige glisse ») : la 1re version faisait glisser le bout coudé dans le plafond.
- **Allègement** : pièces de moins de 80 mm à 240 triangles ; la carte électronique du clavier connecté (cachée dans
  son boîtier) simplifiée à 15 000 triangles. Casier 226 000 triangles, PRO 106 000.

Encombrements : casier 805 × 879 (visière comprise) × 1 256 mm (pieds compris) ; PRO 500 × 437 × 1 053 mm (pieds compris).

## Choix faits pour la boksONE

- **Fichier** : export Rhino de rendu, 248 volumes rangés dans 3 « COMPOUND » sans nom. `--decouper` en fait un nœud par
  volume et l'index garde l'encombrement de chacun (`boite`, mm) : `pieces.py one` décide matière et mouvement d'après
  la position. La serrure JIEKAI nommée, un cube de 3 m et quelques pièces sont placés à ~40 m (scène de rendu) : écartés par `--boite`.
- **Repère** : Z vers le haut, façade (clavier) vers −Y → `--axes=x,z,-y`.
- **Porte avant** : pivote à gauche (axe x = −180,9, y = −141,1 mm) ; vantail, renforts, plaque haute et charnière la suivent ;
  le montant droit (clavier, barillet) reste fixe. **Porte arrière** (`a`) : charnières à droite (axe x = 156,9, y = 228,3 mm),
  avec sa crémone et ses tringles. Les deux portes s'ouvrent ensemble, jusqu'à 110° (le fichier ne donne pas de butée).
- **Clavier** : l'image du clavier Boks est plaquée sur le film de 34 × 109 mm (le même que sur le casier).
- **Rendu** : `--normales` exporte l'orientation exacte des surfaces (la page ne la recalcule plus) : les triangles
  longs et fins des grandes faces planes, une fois les positions quantifiées, faisaient des traînées de reflet.
  Rien n'est simplifié, sauf les pièces de moins de 15 mm (`--minuscules`, 120 triangles, orientation recalculée).
  149 000 triangles.
- Encombrement mesuré : 408 × 400 (charnières arrière comprises) × 705 mm ; boks.app annonce H 70 × L 40 × P 37 cm.

## Rendu des tailles M, L, XL et de la boksONE (02/10/2026)

- **Orientation des surfaces** : `--normales` exporte la normale de la surface CAO à chaque nœud ; la page s'en sert au
  lieu de la recalculer. Un garde-fou (`normales_fiables`) la refuse pour une pièce quand elle contredit ses triangles
  (> 60° sur plus de 2 % d'entre eux : surface mal paramétrée) ; c'est arrivé pour 6 pièces de la boksONE, aucune ailleurs.
  La façade des portes n'est plus découpée (`--facade "^$"`) : c'était le correctif précédent du même défaut.
- **Simplification** : seulement les pièces de moins de 15 mm (20 mm pour XL, 25 mm pour L : rivets et vis du clavier).
- **Taille L** : la carte électronique et les piles du clavier, enfermées dans son boîtier, sont retirées (`--sans`).
- **Taille M** : la vitre du clavier affleure le montant ; matière `vitreAffleurante` (décalage de profondeur) pour
  qu'elle ne se dispute pas l'affichage avec lui. Pas sur la Bokspark, où la vitre est en retrait derrière la porte.
- **boksONE** : le crochet de la gâche (plaque à patte en Z et ses vis, cotes du « SUP GACHE » de la PRO) suit la porte
  avant ; le capot en U de la serrure (cotes du « CAPOT SERRURE » de la PRO) reste sur le montant.
- **boksONE, crochet JIEKAI** : le fichier range une copie de la serrure et de son crochet SUOGOU (les seules pièces
  nommées) à ~40 m, près de la scène de rendu ; le produit n'a que le corps de serrure. `--rapatrier SUOGOU` remet le
  crochet en place : rotation `x,-z,y` (la copie est en Y vers le haut), socle contre le support de gâche de la porte
  (y = −116,4 mm), centré sur lui. Contrôle : la même transformation pose le corps de serrure de la copie sur celui du
  produit à 0,3 mm près sur les trois axes.
- Poids : XL 6,8 Mo (391 000 triangles), L 3,1 Mo (192 000), M 2,2 Mo (133 000), boksONE 2,3 Mo (149 000).
