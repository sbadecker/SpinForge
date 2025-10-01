from __future__ import annotations
import math, random
from .model import Workout, Step

def build_time_box_workout(duration_min: int, focus: str, vary: bool=False, seed: int|None=None) -> Workout:
    if duration_min < 20:
        raise ValueError("duration_min muss >= 20 sein.")
    if seed is not None:
        random.seed(seed)

    total = max(20*60, int(duration_min)*60)
    wu = max(5*60, int(0.12*total))
    cd = max(5*60, int(0.08*total))
    work = max(0, total - wu - cd)

    steps: list[Step] = []
    # Warmup 60→75%
    steps.append(Step(int(wu*0.4), 0.60, "Easy"))
    steps.append(Step(int(wu*0.3), 0.68 if not vary else 0.66 + randj(0.02), "Build"))
    steps.append(Step(wu - int(wu*0.4) - int(wu*0.3), 0.75 if not vary else 0.73 + randj(0.03), "Prime"))

    # Main nach Fokus
    f = focus.strip().lower()
    if f == "endurance":
        steps.append(Step(work, 0.65 if not vary else 0.63 + randj(0.03), "Endurance steady"))
    elif f == "sweetspot":
        steps += repeat_intervals(work, 8*60, 12*60, (0.88,0.94), 2*60, 4*60, vary)
    elif f == "threshold":
        steps += repeat_intervals(work, 12*60, 20*60, (0.95,1.02), 3*60, 5*60, vary)
    else:  # VO2 (default)
        steps += repeat_intervals(work, 2*60, 4*60, (1.10,1.18), 2*60, 4*60, vary)

    # Cooldown 60→50%
    steps.append(Step(int(cd*0.5), 0.60, "Spin down"))
    steps.append(Step(cd - int(cd*0.5), 0.50, "Easy"))

    # leichte Guardrails
    snap_total(steps, total)
    cap_pct(steps, 0.50, 1.20)
    smooth_deltas(steps, 0.60)

    return Workout(name=f"{focus} {duration_min}m", focus=focus, steps=steps)

def repeat_intervals(total_s:int, w_lo:int, w_hi:int, w_pct:tuple[float,float], r_lo:int, r_hi:int, vary:bool)->list[Step]:
    out: list[Step] = []
    t = 0
    while True:
        w = pick_int(w_lo, w_hi, vary)
        r = pick_int(r_lo, r_hi, vary)
        if t + w + r > total_s: break
        p = pick_pct(w_pct[0], w_pct[1], vary)
        out.append(Step(w, p, "Work"))
        out.append(Step(r, 0.55 if not vary else 0.53 + randj(0.03), "Recover"))
        t += w + r
    left = total_s - t
    if left > 0:
        out.append(Step(left, 0.65, "Steady fill"))
    return out

def pick_int(lo:int, hi:int, vary:bool)->int:
    if not vary or lo==hi: return lo
    v = random.randint(lo, hi)
    return (v//30)*30  # auf 30s runden

def pick_pct(lo:float, hi:float, vary:bool)->float:
    if not vary or math.isclose(lo, hi): return round((lo+hi)/2,3)
    return round(lo + random.random()*(hi-lo), 3)

def snap_total(steps:list[Step], target:int)->None:
    cur = sum(s.duration_s for s in steps)
    diff = target - cur
    if abs(diff) <= 60 and steps:
        steps[-1].duration_s = max(30, steps[-1].duration_s + diff)

def cap_pct(steps:list[Step], lo:float, hi:float)->None:
    for s in steps:
        s.pct_ftp = round(min(hi, max(lo, s.pct_ftp)), 3)

def smooth_deltas(steps:list[Step], max_delta:float)->None:
    for i in range(1, len(steps)):
        d = steps[i].pct_ftp - steps[i-1].pct_ftp
        if abs(d) > max_delta:
            steps[i].pct_ftp = round(steps[i-1].pct_ftp + (max_delta if d>0 else -max_delta), 3)

def randj(amp:float)->float:
    return (random.random()*2-1)*amp
