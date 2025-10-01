# tests/test_exports.py
from core.generator import build_time_box_workout
from core.export_zwo import export_zwo

def test_zwo_has_warmup_cooldown_ramps():
    w = build_time_box_workout(45, "Endurance", vary=True)
    xml = export_zwo(w).decode()
    assert "<Warmup" in xml
    assert "<Cooldown" in xml
    assert "<?xml" in xml
