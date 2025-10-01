from .model import Workout, Step

def _acc_power_sq_for_step(s: Step) -> float:
    """
    Liefert ∫ p(t)^2 dt über die Step-Dauer, mit p in %FTP (0.0–n).
    steady: p(t)=a → a^2 * T
    ramp:   p(t) linear a→b → Integral = T * (a*a + a*b + b*b) / 3
    """
    T = float(s.duration_s)
    a = float(s.pct_ftp)
    b = float(s.pct_ftp_end) if s.pct_ftp_end is not None else a
    return T * ((a*a + a*b + b*b) / 3.0)

def compute_if_tss(w: Workout) -> tuple[float, float]:
    total = sum(s.duration_s for s in w.steps)
    if total <= 0:
        return 0.0, 0.0
    acc = sum(_acc_power_sq_for_step(s) for s in w.steps)
    IF = (acc / total) ** 0.5
    TSS = (total * IF * IF) / 3600.0 * 100.0
    return round(IF, 3), round(TSS, 1)
