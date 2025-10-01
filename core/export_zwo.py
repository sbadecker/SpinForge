from xml.etree.ElementTree import Element, SubElement, tostring
from .model import Workout, Step

def export_zwo(w: Workout, author: str|None=None, description: str|None=None) -> bytes:
    root = Element("workout-file")
    SubElement(root, "name").text = w.name
    if author: SubElement(root, "author").text = author
    if description: SubElement(root, "description").text = description

    wo = SubElement(root, "workout")

    for s in w.steps:
        emit_step(wo, s)

    return tostring(root, encoding="utf-8", xml_declaration=True)

def emit_step(parent: Element, s: Step) -> None:
    dur = int(s.duration_s)
    a = float(s.pct_ftp)
    b = float(s.pct_ftp_end) if s.pct_ftp_end is not None else None

    if s.kind in ("warmup", "cooldown", "ramp") and b is not None and b != a:
        tag = "Warmup" if s.kind == "warmup" else ("Cooldown" if s.kind == "cooldown" else "Ramp")
        el = SubElement(parent, tag, {
            "Duration": str(dur),
            "PowerLow": f"{a:.3f}",
            "PowerHigh": f"{b:.3f}",
        })
    else:
        el = SubElement(parent, "SteadyState", {
            "Duration": str(dur),
            "Power": f"{a:.3f}",
        })

    if s.cadence is not None:
        el.set("Cadence", str(int(s.cadence)))

    if s.note:
        te = SubElement(el, "textevent", {"timeoffset": "0"})
        te.text = s.note
