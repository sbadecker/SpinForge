from .model import Workout

def compute_if_tss(w: Workout) -> tuple[float, float]:
    total = sum(s.duration_s for s in w.steps)
    if total <= 0: return 0.0, 0.0
    acc = sum((s.pct_ftp ** 2) * s.duration_s for s in w.steps)
    IF = (acc / total) ** 0.5
    TSS = (total * IF * IF) / 3600.0 * 100.0
    return round(IF, 3), round(TSS, 1)
