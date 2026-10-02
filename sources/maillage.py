import sys, json, numpy as np, trimesh
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_Label
from OCP.OCP.collections import Sequence_TDF_Label as Seq
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.BRep import BRep_Tool
from OCP.TopoDS import TopoDS
from OCP.IFSelect import IFSelect_RetDone
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
from OCP.BRepTools import BRepTools
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.TopAbs import TopAbs_WIRE
from OCP.Bnd import Bnd_Box
from OCP.TopoDS import TopoDS_Iterator
from OCP.TopAbs import TopAbs_COMPOUND
from OCP.BRepBndLib import BRepBndLib
import re, argparse
ap = argparse.ArgumentParser(description="STEP -> maquette glTF (mètres, Y vers le haut) + index des nœuds")
ap.add_argument("step")
ap.add_argument("--nom", default="hub", help="sortie <nom>.glb et index ; hub = Présentation N°1 (index.json)")
ap.add_argument("--z-haut", action="store_true", help="STEP en Z vers le haut, façade vers -X : (x, y, z) -> (-y, z, -x)")
ap.add_argument("--axes", default="", help="repère du STEP vers celui de la page, ex. \"-x,z,y\" (Z vers le haut, façade vers +Y) ; rotation propre seulement")
ap.add_argument("--combler", default=r"PORTE|PORTILLON|BOITIER", help="chemins dont on bouche les perçages < 25 mm")
ap.add_argument("--facade", default=r"PORTE GAUCHE P1|PORTE DROITE P1|PORTILLON", help="chemins dont la façade devient un nœud [façade]")
ap.add_argument("--angle", type=float, default=0.25, help="déflexion angulaire du maillage (rad)")
ap.add_argument("--petites", type=float, default=0, help="pièces de diagonale < N mm : maillage grossier (1 mm, 0,8 rad) ; 0 = non")
ap.add_argument("--plafond", type=int, default=0, help="triangles au plus par pièce, au-delà : simplification quadrique ; 0 = non")
ap.add_argument("--plafond-petites", type=int, default=0, help="idem pour les pièces de --petites ; 0 = non")
ap.add_argument("--sans", default="", help="chemins laissés de côté (ex. la dalle de présentation)")
ap.add_argument("--decouper", action="store_true", help="un nœud par élément des COMPOUND (exports Rhino sans arbre nommé)")
ap.add_argument("--boite", default="", help="xmin,ymin,zmin,xmax,ymax,zmax en mm (repère du STEP) : on écarte ce dont le centre est dehors")
ap.add_argument("--grossier", default="", help="chemins maillés grossièrement (1 mm, 0,8 rad) et jamais simplifiés (tôles à picots)")
A = ap.parse_args()
BOUCHES = [0]
def taille_fil(w):
    b = Bnd_Box(); BRepBndLib.Add_s(w, b)
    p0, p1 = b.CornerMin(), b.CornerMax()
    return max(p1.X()-p0.X(), p1.Y()-p0.Y(), p1.Z()-p0.Z())
def sans_petits_trous(f, seuil=25.0):
    if BRepAdaptor_Surface(f).GetType() != GeomAbs_Plane: return f
    ext = BRepTools.OuterWire_s(f)
    fils = []; e = TopExp_Explorer(f, TopAbs_WIRE)
    while e.More(): fils.append(TopoDS.Wire(e.Current())); e.Next()
    if len(fils) < 2: return f
    gardes = [w for w in fils if not w.IsSame(ext) and taille_fil(w) >= seuil]
    if len(gardes) == len(fils) - 1: return f
    mf = BRepBuilderAPI_MakeFace(BRep_Tool.Surface_s(f), ext)
    for w in gardes: mf.Add(w)
    if not mf.IsDone(): return f
    nf = mf.Face(); nf.Orientation(f.Orientation())
    BOUCHES[0] += len(fils) - 1 - len(gardes)
    return nf

doc = TDocStd_Document(TCollection_ExtendedString("doc"))
r = STEPCAFControl_Reader(); r.SetNameMode(True)
assert r.ReadFile(A.step) == IFSelect_RetDone
r.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
def nom(lab):
    a = TDataStd_Name()
    return a.Get().ToExtString() if lab.FindAttribute(TDataStd_Name.GetID_s(), a) else "?"

def petite(shape):
    if not A.petites: return False
    b = Bnd_Box(); BRepBndLib.Add_s(shape, b)
    return b.SquareExtent() ** 0.5 < A.petites

def maille(shape, combler=False, grossier=False):
    lin, ang = (1.0, 0.8) if grossier or petite(shape) else (0.4, A.angle)
    BRepMesh_IncrementalMesh(shape, lin, False, ang, True)
    V, F, off = [], [], 0
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        f = TopoDS.Face(ex.Current()); loc = TopLoc_Location()
        if combler:
            g = sans_petits_trous(f)
            if g is not f:
                BRepMesh_IncrementalMesh(g, lin, False, ang, True); f = g
        tri = BRep_Tool.Triangulation_s(f, loc)
        if tri is not None:
            tr = loc.Transformation()
            pts = []
            for i in range(1, tri.NbNodes()+1):
                p = tri.Node(i).Transformed(tr); pts.append((p.X(), p.Y(), p.Z()))
            inv = f.Orientation() == TopAbs_REVERSED
            for i in range(1, tri.NbTriangles()+1):
                a, b, c = tri.Triangle(i).Get()
                F.append((off+a-1, off+c-1, off+b-1) if inv else (off+a-1, off+b-1, off+c-1))
            V += pts; off += len(pts)
        ex.Next()
    return np.array(V, float), np.array(F, int)

pieces = []
def parcours(lab, loc, chemin):
    ref = TDF_Label()
    if st.IsReference_s(lab):
        st.GetReferredShape_s(lab, ref); loc = loc.Multiplied(st.GetLocation_s(lab)); cible = ref
    else:
        cible = lab
    chemin = chemin + [nom(cible)]
    if st.IsAssembly_s(cible):
        enf = Seq(); st.GetComponents_s(cible, enf)
        for i in range(1, enf.Length()+1): parcours(enf.Value(i), loc, chemin)
    else:
        forme = st.GetShape_s(cible).Moved(loc); ch = ' / '.join(chemin)
        if A.sans and re.search(A.sans, ch): return
        if A.decouper and forme.ShapeType() == TopAbs_COMPOUND:
            elements = []
            def ouvrir(f):
                it = TopoDS_Iterator(f)
                while it.More():
                    e = it.Value()
                    if e.ShapeType() == TopAbs_COMPOUND: ouvrir(e)
                    else: elements.append(e)
                    it.Next()
            ouvrir(forme)
            for i, e in enumerate(elements): ajouter(chemin + [f"{chemin[-1]} {i:03d}"], e)
            return
        ajouter(chemin, forme)

def ajouter(chemin, forme):
        ch = ' / '.join(chemin)
        if A.boite:
            b = Bnd_Box(); BRepBndLib.Add_s(forme, b); p0, p1 = b.CornerMin(), b.CornerMax()
            x0, y0, z0, x1, y1, z1 = map(float, A.boite.split(","))
            cx, cy, cz = (p0.X() + p1.X()) / 2, (p0.Y() + p1.Y()) / 2, (p0.Z() + p1.Z()) / 2
            if not (x0 <= cx <= x1 and y0 <= cy <= y1 and z0 <= cz <= z1): return
        grossier = bool(A.grossier and re.search(A.grossier, ch))
        V, F = maille(forme, combler=bool(re.search(A.combler, ch)), grossier=grossier)
        if len(F): pieces.append((chemin[1:], V, F, petite(forme), grossier))

roots = Seq(); st.GetFreeShapes(roots)
for i in range(1, roots.Length()+1): parcours(roots.Value(i), TopLoc_Location(), [])

scene = trimesh.Scene()
index = []
for k, (chemin, V, F, est_petite, grossier) in enumerate(pieces):
    boite = [round(float(v), 1) for v in list(V.min(0)) + list(V.max(0))]  # mm, repère du STEP
    axes = A.axes or ("-y,z,-x" if A.z_haut else "")
    if axes:  # chaque composante de la page = ± un axe du STEP ; rotation propre : l'enroulement des triangles ne change pas
        cols = [(-1 if c.strip().startswith("-") else 1) * V[:, "xyz".index(c.strip()[-1])] for c in axes.split(",")]
        M = np.array([[(-1 if c.strip().startswith("-") else 1) * (j == "xyz".index(c.strip()[-1])) for j in range(3)] for c in axes.split(",")])
        assert round(np.linalg.det(M)) == 1, "--axes doit être une rotation (déterminant +1)"
        V = np.column_stack(cols)
    V = V / 1000.0  # mm -> m
    m = trimesh.Trimesh(V, F, process=True)
    plafond = A.plafond_petites if est_petite and A.plafond_petites else A.plafond
    if plafond and len(m.faces) > plafond and not grossier:
        m = m.simplify_quadric_decimation(face_count=plafond)
    ch = ' / '.join(chemin)
    if re.search(A.facade, ch):
        n = m.face_normals; c = m.triangles_center
        face = (n[:, 2] > 0.99) & (c[:, 2] > m.bounds[1][2] - 0.0002)
        if face.any() and (~face).any():
            mf = m.submesh([np.where(face)[0]], append=True)
            m = m.submesh([np.where(~face)[0]], append=True)
            nf = f"p{k:02d}f"
            scene.add_geometry(mf, node_name=nf, geom_name=nf)
            index.append({"noeud": nf, "chemin": ch + " [façade]", "triangles": int(len(mf.faces))})
    nomnoeud = f"p{k:02d}"
    scene.add_geometry(m, node_name=nomnoeud, geom_name=nomnoeud)
    index.append({"noeud": nomnoeud, "chemin": " / ".join(chemin), "triangles": int(len(m.faces))} | ({"boite": boite} if A.decouper else {}))
scene.export(f"{A.nom}.glb")
json.dump(index, open("index.json" if A.nom == "hub" else f"{A.nom}-index.json", "w"), ensure_ascii=False, indent=1)
print("trous bouchés :", BOUCHES[0]); print(len(pieces), "pièces,", sum(i["triangles"] for i in index), "triangles")
