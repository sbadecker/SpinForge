from .model import Workout

def sanitize_workout(w: Workout) -> Workout:
    for s in w.steps:
        if s.duration_s < 5: s.duration_s = 5
        # 0.50–3.00 als „sinnvoller“ Rahmen (Zwift kann hohe Sprints)
        s.pct_ftp = max(0.50, min(3.00, float(s.pct_ftp)))
        if s.kind not in ("warmup","cooldown"):
            s.pct_ftp_end = None
        elif s.pct_ftp_end is not None:
            s.pct_ftp_end = max(0.50, min(3.00, float(s.pct_ftp_end)))
    return w
