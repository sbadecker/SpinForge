from dataclasses import dataclass
from typing import List, Optional, Literal

StepKind = Literal["steady", "ramp", "warmup", "cooldown"]

@dataclass
class Step:
    duration_s: int
    pct_ftp: float                     # Start-Intensität (bei ramp/warmup/cooldown = low)
    note: Optional[str] = None
    cadence: Optional[int] = None
    kind: StepKind = "steady"
    pct_ftp_end: Optional[float] = None  # Nur für ramp/warmup/cooldown: End-Intensität

@dataclass
class Workout:
    name: str
    focus: str              # "Recovery"|"Endurance"|"SweetSpot"|"Threshold"|"VO2"
    steps: List[Step]
    description: Optional[str] = None
