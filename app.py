import os
from flask import Flask, render_template, request, Response, jsonify
from core.generator import build_time_box_workout
from core.metrics import compute_if_tss
from core.nl_parser import NLParser
from core.export_zwo import export_zwo

app = Flask(__name__)
# open_ai_key = os.getenv("OPENAI_API_KEY")
# nl_parser = NLParser(open_ai_key)
anthropic_ai_key = os.getenv("ANTHROPIC_API_KEY")
nl_parser = NLParser(anthropic_ai_key)

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
    w = nl_parser.generate(duration, focus, prefs=prefs)
    data = export_zwo(w, description=w.description)
    fname = f'{w.name.replace(" ","_")}.zwo'
    return Response(data, mimetype="application/xml",
                    headers={"Content-Disposition": f'attachment; filename="{fname}"'})

if __name__ == "__main__":
    app.run(debug=True)
