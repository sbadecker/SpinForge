from xml.etree.ElementTree import Element, SubElement, tostring
from .model import Workout

def export_zwo(w: Workout, author: str|None=None, description: str|None=None) -> bytes:
    root = Element("workout-file")
    SubElement(root, "name").text = w.name
    if author: SubElement(root, "author").text = author
    if description: SubElement(root, "description").text = description
    wo = SubElement(root, "workout")
    for s in w.steps:
        el = SubElement(wo, "SteadyState", {
            "Duration": str(int(s.duration_s)),
            "Power": f"{float(s.pct_ftp):.3f}",
        })
        if s.cadence is not None:
            el.set("Cadence", str(int(s.cadence)))
        if s.note:
            te = SubElement(el, "textevent", {"timeoffset": "0"})
            te.text = s.note
    return tostring(root, encoding="utf-8", xml_declaration=True)
