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
from OCP.BRepBndLib import BRepBndLib
import re
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
assert r.ReadFile(sys.argv[1]) == IFSelect_RetDone
r.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
def nom(lab):
    a = TDataStd_Name()
    return a.Get().ToExtString() if lab.FindAttribute(TDataStd_Name.GetID_s(), a) else "?"

def maille(shape, combler=False):
    BRepMesh_IncrementalMesh(shape, 0.4, False, 0.25, True)
    V, F, off = [], [], 0
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        f = TopoDS.Face(ex.Current()); loc = TopLoc_Location()
        if combler:
            g = sans_petits_trous(f)
            if g is not f:
                BRepMesh_IncrementalMesh(g, 0.4, False, 0.25, True); f = g
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
        V, F = maille(st.GetShape_s(cible).Moved(loc), combler=bool(re.search(r'PORTE|PORTILLON|BOITIER', ' / '.join(chemin))))
        if len(F): pieces.append((chemin[1:], V, F))

roots = Seq(); st.GetFreeShapes(roots)
for i in range(1, roots.Length()+1): parcours(roots.Value(i), TopLoc_Location(), [])

scene = trimesh.Scene()
index = []
for k, (chemin, V, F) in enumerate(pieces):
    V = V / 1000.0  # mm -> m
    m = trimesh.Trimesh(V, F, process=True)
    ch = ' / '.join(chemin)
    if re.search(r'PORTE GAUCHE P1|PORTE DROITE P1|PORTILLON', ch):
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
    index.append({"noeud": nomnoeud, "chemin": " / ".join(chemin), "triangles": int(len(m.faces))})
scene.export("hub.glb")
json.dump(index, open("index.json", "w"), ensure_ascii=False, indent=1)
print("trous bouchés :", BOUCHES[0]); print(len(pieces), "pièces,", sum(i["triangles"] for i in index), "triangles")
