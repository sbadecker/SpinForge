from core.generator import build_time_box_workout
from core.export_zwo import export_zwo
from core.export_mrc import export_mrc


def test_exports_exist():
    w = build_time_box_workout(30, "SweetSpot")
    zwo = export_zwo(w)
    mrc = export_mrc(w)
    assert zwo.startswith(b'<?xml')
    assert "[COURSE DATA]" in mrc
