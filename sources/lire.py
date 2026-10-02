import sys, json
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_Label
from OCP.OCP.collections import Sequence_TDF_Label as TDF_LabelSequence
from OCP.TDataStd import TDataStd_Name
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.TopLoc import TopLoc_Location
from OCP.IFSelect import IFSelect_RetDone

src = sys.argv[1]
doc = TDocStd_Document(TCollection_ExtendedString("doc"))
r = STEPCAFControl_Reader(); r.SetNameMode(True)
assert r.ReadFile(src) == IFSelect_RetDone
r.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())

def nom(lab):
    a = TDataStd_Name()
    if lab.FindAttribute(TDataStd_Name.GetID_s(), a):
        return a.Get().ToExtString()
    return "?"

feuilles = []
def parcours(lab, loc, chemin, prof):
    ref = TDF_Label()
    if st.IsReference_s(lab):
        st.GetReferredShape_s(lab, ref)
        loc = loc.Multiplied(st.GetLocation_s(lab))
        cible = ref
    else:
        cible = lab
    n = nom(cible)
    chemin = chemin + [n]
    if st.IsAssembly_s(cible):
        enf = TDF_LabelSequence(); st.GetComponents_s(cible, enf)
        for i in range(1, enf.Length()+1):
            parcours(enf.Value(i), loc, chemin, prof+1)
    else:
        s = st.GetShape_s(cible).Moved(loc)
        b = Bnd_Box(); BRepBndLib.Add_s(s, b)
        p0,p1 = b.CornerMin(), b.CornerMax(); x0,y0,z0,x1,y1,z1 = p0.X(),p0.Y(),p0.Z(),p1.X(),p1.Y(),p1.Z()
        feuilles.append({"chemin": chemin, "bbox": [round(v,1) for v in (x0,y0,z0,x1,y1,z1)]})

roots = TDF_LabelSequence(); st.GetFreeShapes(roots)
for i in range(1, roots.Length()+1):
    parcours(roots.Value(i), TopLoc_Location(), [], 0)
json.dump(feuilles, open("feuilles.json","w"), ensure_ascii=False, indent=0)
for f in feuilles:
    print(" / ".join(f["chemin"][1:]), f["bbox"])
