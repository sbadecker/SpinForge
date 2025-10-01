from __future__ import annotations
from .model import Workout, Step

def sanitize_workout(w: Workout) -> Workout:
    # Dauer min. 5s; pFTP clamp 0.50–3.00
    for s in w.steps:
        if s.duration_s < 5:
            s.duration_s = 5
        s.pct_ftp = max(0.50, min(3.00, float(s.pct_ftp)))
        if s.pct_ftp_end is not None:
            s.pct_ftp_end = max(0.50, min(3.00, float(s.pct_ftp_end)))
    # keine künstliche Sprungbegrenzung zwischen Steps (Zwift erlaubt große Sprünge)
    return w
