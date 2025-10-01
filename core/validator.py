from __future__ import annotations
from .model import Workout, Step

def sanitize_workout(w: Workout) -> Workout:
    for s in w.steps:
        # Dauer min. 5s
        if s.duration_s < 5:
            s.duration_s = 5
        # Clamp 50–300 % FTP (Zwift-Workouts nutzen teils sehr hohe Sprints)
        s.pct_ftp = float(s.pct_ftp)
        if s.pct_ftp < 0.50: s.pct_ftp = 0.50
        if s.pct_ftp > 3.00: s.pct_ftp = 3.00
        if s.pct_ftp_end is not None:
            s.pct_ftp_end = float(s.pct_ftp_end)
            if s.pct_ftp_end < 0.50: s.pct_ftp_end = 0.50
            if s.pct_ftp_end > 3.00: s.pct_ftp_end = 3.00
    # keine künstlichen Sprunglimits
    return w
