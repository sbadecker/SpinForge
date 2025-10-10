import os
from flask import Flask, render_template, request, Response, jsonify
from core.generator import build_time_box_workout
from core.metrics import compute_if_tss
from core.nl_parser import NLParser
from core.export_zwo import export_zwo
from core.model import Workout, Step
import json

app = Flask(__name__)
# open_ai_key = os.getenv("OPENAI_API_KEY")
# nl_parser = NLParser(open_ai_key)
nl_parser = NLParser()


@app.get("/")
def index():
    return render_template("index.html")

@app.post("/preview")
def preview():
    duration = int(request.form.get("duration_min", "45"))
    focus = request.form.get("focus", "VO2")
    vary = request.form.get("vary") == "on"
    w = build_time_box_workout(duration, focus, vary=vary)
    IF, TSS = compute_if_tss(w)
    steps = [{"d": s.duration_s, "kind": s.kind, "pct": s.pct_ftp, "pct_end": s.pct_ftp_end, "note": s.note} for s in w.steps]
    return jsonify({"name": w.name, "focus": w.focus, "if": IF, "tss": TSS, "description": w.description, "steps": steps})

@app.post("/preview_nl")
def preview_nl():
    duration = int(request.form.get("duration_min", "45"))
    focus = request.form.get("focus", "VO2")
    prefs = request.form.get("prefs", "")
    w = nl_parser.generate(duration, focus, prefs=prefs)
    IF, TSS = compute_if_tss(w)
    steps = [{"d": s.duration_s, "kind": s.kind, "pct": s.pct_ftp, "pct_end": s.pct_ftp_end, "note": s.note} for s in w.steps]
    return jsonify({"name": w.name, "focus": w.focus, "if": IF, "tss": TSS, "description": w.description, "steps": steps})

def _preview_json_to_workout(s: str) -> Workout:
    # Parse the preview JSON shape back into a Workout
    obj = json.loads(s)
    steps = []
    for x in obj.get("steps", []):
        steps.append(Step(
            duration_s=int(x.get("d") or x.get("duration_s") or 0),
            pct_ftp=float(x.get("pct") or x.get("pct_ftp") or 0.6),
            kind=x.get("kind") or "steady",
            pct_ftp_end=(float(x.get("pct_end") or x.get("pct_ftp_end")) if (x.get("pct_end") is not None or x.get("pct_ftp_end") is not None) else None),
            note=x.get("note")
        ))
    return Workout(name=obj.get("name") or "Workout", focus=obj.get("focus") or "Endurance", steps=steps, description=obj.get("description"))

def _workout_to_preview_json(w: Workout, IF: float, TSS: float) -> dict:
    return {
        "name": w.name,
        "focus": w.focus,
        "if": IF,
        "tss": TSS,
        "description": w.description,
        "steps": [{"d": s.duration_s, "kind": s.kind, "pct": s.pct_ftp, "pct_end": s.pct_ftp_end, "note": s.note} for s in w.steps],
    }

@app.post("/preview_nl_refine")
def preview_nl_refine():
    duration = int(request.form.get("duration_min", "45"))
    focus = request.form.get("focus", "VO2")
    changes = request.form.get("changes", "")
    base_raw = request.form.get("base_raw", "")
    if not base_raw:
        return jsonify({"error": "base_raw required"}), 400
    try:
        prev = _preview_json_to_workout(base_raw)
    except Exception:
        return jsonify({"error": "invalid base_raw"}), 400
    w = nl_parser.refine(prev, changes)
    IF, TSS = compute_if_tss(w)
    return jsonify(_workout_to_preview_json(w, IF, TSS))

@app.get("/download")
def download():
    duration = int(request.args.get("duration_min", "45"))
    focus = request.args.get("focus", "VO2")
    vary = request.args.get("vary") == "1"
    w = build_time_box_workout(duration, focus, vary=vary)
    data = export_zwo(w, description=w.description)
    fname = f'{w.name.replace(" ","_")}.zwo'
    return Response(data, mimetype="application/xml",
                    headers={"Content-Disposition": f'attachment; filename="{fname}"'})

@app.get("/download_nl")
def download_nl():
    duration = int(request.args.get("duration_min", "45"))
    focus = request.args.get("focus", "VO2")
    prefs = request.args.get("prefs", "")
    base_raw = request.args.get("base_raw")
    if base_raw:
        try:
            w = _preview_json_to_workout(base_raw)
        except Exception:
            return Response("invalid base_raw", status=400)
    else:
        w = nl_parser.generate(duration, focus, prefs=prefs)
    data = export_zwo(w, description=w.description)
    fname = f'{w.name.replace(" ","_")}.zwo'
    return Response(data, mimetype="application/xml",
                    headers={"Content-Disposition": f'attachment; filename="{fname}"'})

if __name__ == "__main__":
    app.run(debug=True)
