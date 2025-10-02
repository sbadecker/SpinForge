from __future__ import annotations
from typing import Any, Dict, Optional
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from .model import Workout, Step
from .generator import build_time_box_workout
from .validator import sanitize_workout

SYSTEM = """You generate Zwift workouts as JSON:
{{
 "name": "string",
 "focus": "Recovery|Endurance|SweetSpot|Threshold|VO2",
 "description": "string",  # short explanation why the session makes sense
 "steps": [
   {{"duration_s": int, "pct_ftp": float, "kind":"steady|warmup|cooldown", "pct_ftp_end": float?, "note": str?}}
 ]
}}
Rules:
- JSON only. No markdown fences or commentary.
- Provide a concise "description" (2–3 sentences) explaining the session goal and why it suits the chosen focus for ambitious/elite cyclists.
- Total time ≈ {duration_min} min (±60s)
- Min. 5s per step
- Typical intensities 0.50–1.20 (sprints >1.2 ok); accept up to 3.00
- Ramps ONLY in warmup/cooldown (and set pct_ftp_end). Main steps are steady (no pct_ftp_end).
- Always include a progressive warmup (Z1→Z2/low Z3) and an easy cooldown (Z2→Z1). The cooldown should never start higher than the previous step.
- Use science-based structure suitable for elite and ambitious cyclists: steady, purposeful work; controlled recovery.
- Recoveries sit in Z1–low Z2 (≈0.50–0.65 FTP) and should not exceed work intensity.
- Keep intensity changes smooth; avoid abrupt jumps >0.30 FTP between adjacent steady steps.
- Keep high-intensity volume appropriate for session type (see focus-specific rules below).
- The guidance is not a strict template; adapt intelligently to fit the total duration and also to keep workouts interesting.
- Add a brief, helpful note to each step explaining intent and motivation.

Focus-specific guidance:
- Recovery: Easy aerobic spin at ≤0.60 FTP, mostly steady 0.50–0.60; no hard efforts; include gentle cadence focus in notes if useful.
- Endurance: Mostly continuous Z2 (≈0.60–0.75 FTP). Optional brief steady Z3 touches only if specified; no surges.
- SweetSpot: 2–5 blocks of 8–15 min at ≈0.88–0.94 FTP with 3–5 min Z1–Z2 recoveries.
- Threshold: 2–3 blocks of 10–20 min at ≈0.95–1.02 FTP with recoveries ≈25–50% of work duration in 0.55–0.65 FTP.
- VO2: 4–8 repeats of 2–4 min at ≈1.10–1.18 FTP with equal or slightly longer recoveries (2–4 min) at 0.50–0.60 FTP. If the user requests it, you can include short sprints >1.2 FTP, but keep total high-intensity volume sensible.
"""
USER = """Parameters:
- Duration: {duration_min} min
- Focus: {focus}
- Preferences: {prefs}"""

def _json_only(s: str) -> Dict[str, Any]:
    s = s.strip()
    if s.startswith("```"):
        s = s.strip("`").replace("json","",1).strip()
    first, last = s.find("{"), s.rfind("}")
    if first >= 0 and last > first:
        s = s[first:last+1]
    return json.loads(s)

class NLParser:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-5-mini"):
        self.llm = ChatOpenAI(model=model, temperature=1, api_key=api_key)
        self.prompt = ChatPromptTemplate.from_messages([("system", SYSTEM), ("user", USER)])

    def generate(self, duration_min:int, focus:str, prefs:str="") -> Workout:
        msg = self.prompt.format_messages(duration_min=duration_min, focus=focus, prefs=prefs or "—")
        raw = self.llm.invoke(msg)
        print(raw.content)
        try:
            j = _json_only(raw.content)
        except Exception:
            raw = self.llm.invoke(msg)
            j = _json_only(raw.content)

        steps = []
        for s in j.get("steps", []):
            steps.append(Step(
                duration_s=int(s["duration_s"]),
                pct_ftp=float(s["pct_ftp"]),
                kind=s.get("kind","steady"),
                pct_ftp_end=(float(s["pct_ftp_end"]) if "pct_ftp_end" in s and s["pct_ftp_end"] is not None else None),
                note=s.get("note")
            ))
        w = Workout(name=j.get("name", f"{focus} {duration_min}m"), focus=j.get("focus", focus), steps=steps, description=j.get("description"))
        return sanitize_workout(w)
