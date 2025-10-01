from flask import Flask, render_template, request, Response, jsonify
from core.generator import build_time_box_workout
from core.metrics import compute_if_tss
from core.export_zwo import export_zwo

app = Flask(__name__)

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
    steps = []
    for s in w.steps:
        steps.append({
            "d": s.duration_s,
            "kind": s.kind,
            "pct": s.pct_ftp,
            "pct_end": s.pct_ftp_end,
            "note": s.note
        })
    return jsonify({"name": w.name, "focus": w.focus, "if": IF, "tss": TSS, "steps": steps})

@app.get("/download")
def download():
    duration = int(request.args.get("duration_min", "45"))
    focus = request.args.get("focus", "VO2")
    vary = request.args.get("vary") == "1"
    w = build_time_box_workout(duration, focus, vary=vary)

    data = export_zwo(w)
    fname = f'{w.name.replace(" ", "_")}.zwo'
    return Response(data, mimetype="application/xml",
                    headers={"Content-Disposition": f'attachment; filename="{fname}"'})

if __name__ == "__main__":
    app.run(debug=True)
