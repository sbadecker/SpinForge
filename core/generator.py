from __future__ import annotations
import math, random
from .model import Workout, Step

def build_time_box_workout(duration_min: int, focus: str, vary: bool=False, seed: int|None=None) -> Workout:
    if duration_min < 20:
        raise ValueError("duration_min muss >= 20 sein.")
    if seed is not None:
        random.seed(seed)

    total = max(20*60, int(duration_min)*60)

    # Warmup/Cooldown als echte Ramps
    min_warmup_duration = 5
    min_cooldown_duration = 5
    warum_up_ratio = 0.12
    cool_down_ration = 0.08
    wu = max(5*60, int(warum_up_ratio*total))
    cd = max(5*60, int(cool_down_ration*total))
    work = max(0, total - wu - cd)

    steps: list[Step] = []

    # Warmup 60% → 75%
    wu_low = 0.60
    wu_high = 0.73 + randj(0.03) if vary else 0.75
    steps.append(Step(duration_s=wu, pct_ftp=round(wu_low,3), pct_ftp_end=round(wu_high,3), kind="warmup", note="Warmup"))

    # Main nach Fokus
    f = focus.strip().lower()
    # ToDo: vary should change the duration and intensity of all steps in repeated intervals, not each step individually
    if f == "endurance":
        # leichte wellenförmige Ramp im Main-Teil (optional)
        if vary and work >= 10*60:
            half = work // 2
            steps.append(Step(half, 0.65, 0.72, kind="ramp", note="Endurance ramp up"))
            steps.append(Step(work - half, 0.72, 0.64, kind="ramp", note="Endurance ramp down"))
        else:
            steps.append(Step(work, 0.65 if not vary else 0.63+randj(0.03), kind="steady", note="Endurance steady"))
    elif f == "sweetspot":
        steps += repeat_intervals(work, 8*60, 12*60, (0.88,0.94), 2*60, 4*60, vary)
    elif f == "threshold":
        steps += repeat_intervals(work, 12*60, 20*60, (0.95,1.02), 3*60, 5*60, vary)
    else:  # VO2
        steps += repeat_intervals(work, 2*60, 4*60, (1.10,1.18), 2*60, 4*60, vary)

    # Cooldown 60% → 50%
    steps.append(Step(duration_s=cd, pct_ftp=0.60, pct_ftp_end=0.50, kind="cooldown", note="Cooldown"))

    # leichte Guardrails
    snap_total(steps, total)
    clamp_pct(steps, 0.50, 3.00)  # Zwift erlaubt sehr hohe Sprints; 3.00 (=300%) als sinnvolle Obergrenze
    ensure_min_duration(steps, 5) # 5s Minimum, Zwift-Realität

    return Workout(name=f"{focus} {duration_min}m", focus=focus, steps=steps)

def repeat_intervals(total_s:int, w_lo:int, w_hi:int, w_pct:tuple[float,float], r_lo:int, r_hi:int, vary:bool)->list[Step]:
    out: list[Step] = []
    t = 0
    while True:
        w = pick_int(w_lo, w_hi, vary)
        r = pick_int(r_lo, r_hi, vary)
        if t + w + r > total_s: break
        p = pick_pct(w_pct[0], w_pct[1], vary)
        out.append(Step(w, p, kind="steady", note="Work"))
        out.append(Step(r, 0.55 if not vary else 0.53 + randj(0.03), kind="steady", note="Recover"))
        t += w + r
    left = total_s - t
    if left > 0:
        out.append(Step(left, 0.65, kind="steady", note="Steady fill"))
    return out

def pick_int(lo:int, hi:int, vary:bool)->int:
    if not vary or lo==hi: return lo
    v = random.randint(lo, hi)
    return (v//5)*5  # auf 5s runden (Zwift kann 5s)

def pick_pct(lo:float, hi:float, vary:bool)->float:
    if not vary or math.isclose(lo, hi): return round((lo+hi)/2,3)
    return round(lo + random.random()*(hi-lo), 3)

def snap_total(steps:list[Step], target:int)->None:
    cur = sum(s.duration_s for s in steps)
    diff = target - cur
    if abs(diff) <= 60 and steps:
        steps[-1].duration_s = max(5, steps[-1].duration_s + diff)

def clamp_pct(steps:list[Step], lo:float, hi:float)->None:
    for s in steps:
        s.pct_ftp = round(min(hi, max(lo, s.pct_ftp)), 3)
        if s.pct_ftp_end is not None:
            s.pct_ftp_end = round(min(hi, max(lo, s.pct_ftp_end)), 3)

def ensure_min_duration(steps:list[Step], min_s:int)->None:
    for s in steps:
        if s.duration_s < min_s:
            s.duration_s = min_s

def randj(amp:float)->float:
    return (random.random()*2-1)*amp
