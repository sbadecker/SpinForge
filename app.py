from flask import Flask, render_template, request, Response, jsonify
from core.generator import build_time_box_workout
from core.metrics import compute_if_tss
from core.export_zwo import export_zwo
from core.export_mrc import export_mrc

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
    steps = [{"d": s.duration_s, "pct": s.pct_ftp, "note": s.note} for s in w.steps]
    return jsonify({"name": w.name, "if": IF, "tss": TSS, "steps": steps})

@app.get("/download")
def download():
    duration = int(request.args.get("duration_min", "45"))
    focus = request.args.get("focus", "VO2")
    vary = request.args.get("vary") == "1"
    fmt = request.args.get("fmt", "zwo")
    w = build_time_box_workout(duration, focus, vary=vary)

    if fmt == "zwo":
        data = export_zwo(w)
        mt, ext = "application/xml", "zwo"
    elif fmt == "mrc":
        data = export_mrc(w).encode()
        mt, ext = "text/plain", "mrc"
    else:
        return jsonify({"error":"unknown fmt"}), 400

    fname = f'{w.name.replace(" ", "_")}.{ext}'
    return Response(data, mimetype=mt, headers={"Content-Disposition": f'attachment; filename="{fname}"'})

if __name__ == "__main__":
    app.run(debug=True)
