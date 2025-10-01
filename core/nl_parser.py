from __future__ import annotations
from typing import Any, Dict, Optional
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from .model import Workout, Step
from .generator import build_time_box_workout
from .validator import sanitize_workout

SYSTEM = """Du erzeugst Zwift-Workouts als JSON:
{
 "name": "string",
 "focus": "Endurance|SweetSpot|Threshold|VO2",
 "steps": [
   {"duration_s": int, "pct_ftp": float, "kind":"steady|ramp|warmup|cooldown", "pct_ftp_end": float?, "note": str?}
 ]
}
Regeln:
- Min. 5s je Step
- Intensitäten typ. 0.50–1.20 (Sprints >1.2 ok), Warmup/Cooldown als Ramp
- Gesamtzeit ≈ {duration_min} min (±60s)
Nur JSON, keine Erklärungen.
"""
USER = """Parameter:
- Dauer: {duration_min} min
- Fokus: {focus}
- Präferenzen: {prefs}"""

def _json_only(s: str) -> Dict[str, Any]:
    s = s.strip()
    if s.startswith("```"):
        s = s.strip("`")
        s = s.replace("json", "", 1).strip()
    first, last = s.find("{"), s.rfind("}")
    if first >= 0 and last > first:
        s = s[first:last+1]
    return json.loads(s)

class NLParser:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model, temperature=0.2, api_key=api_key)
        self.prompt = ChatPromptTemplate.from_messages([("system", SYSTEM), ("user", USER)])

    def generate(self, duration_min:int, focus:str, prefs:str="") -> Workout:
        msg = self.prompt.format_messages(duration_min=duration_min, focus=focus, prefs=prefs or "—")
        raw = self.llm.invoke(msg)
        try:
            j = _json_only(raw.content)
        except Exception:
            # Retry 1x
            raw = self.llm.invoke(msg)
            j = _json_only(raw.content)
        # Parse in dataclasses
        steps = []
        for s in j.get("steps", []):
            steps.append(Step(
                duration_s=int(s["duration_s"]),
                pct_ftp=float(s["pct_ftp"]),
                kind=s.get("kind","steady"),
                pct_ftp_end=(float(s["pct_ftp_end"]) if "pct_ftp_end" in s and s["pct_ftp_end"] is not None else None),
                note=s.get("note")
            ))
        w = Workout(name=j.get("name", f"{focus} {duration_min}m"), focus=j.get("focus", focus), steps=steps)
        return sanitize_workout(w)
