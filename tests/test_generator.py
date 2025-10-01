from core.generator import build_time_box_workout


def test_total_duration_snap():
    w = build_time_box_workout(45, "VO2")
    total = sum(s.duration_s for s in w.steps)
    assert abs(total - 45*60) <= 60


def test_focus_names():
    for f in ["Endurance","SweetSpot","Threshold","VO2"]:
        w = build_time_box_workout(45, f)
        assert w.focus == f
        assert len(w.steps) > 0
