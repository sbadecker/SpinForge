from .model import Workout

def export_mrc(w: Workout) -> str:
    header = [
        "[COURSE HEADER]",
        "VERSION = 2",
        "UNITS = ENGLISH",
        f"DESCRIPTION = {w.name}",
        "",
        "[COURSE DATA]"
    ]
    t = 0
    lines = []
    for s in w.steps:
        pct = 100.0 * float(s.pct_ftp)
        lines.append(f"{t}\t{pct:.1f}")
        t += int(s.duration_s)
        lines.append(f"{t}\t{pct:.1f}")
    return "\n".join(header + lines)
