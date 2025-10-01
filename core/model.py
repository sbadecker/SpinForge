from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Step:
    duration_s: int
    pct_ftp: float          # 0.50–1.20 (relativ)
    note: Optional[str] = None
    cadence: Optional[int] = None

@dataclass
class Workout:
    name: str
    focus: str              # "Endurance"|"SweetSpot"|"Threshold"|"VO2"
    steps: List[Step]       # flache Liste (einfachere Exporte/Preview)
