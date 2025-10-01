# RoadForge (SpinForge)

**Custom Cycling Workouts in Seconds – Ready to Ride in Zwift**

RoadForge (working title: *SpinForge*) is a small web application that lets cyclists generate personalized training workouts in seconds.  
The workouts can be downloaded as **.zwo** files and imported straight into Zwift.

---

## 🎯 Features

- **Workout Generator**
  - Input total duration (minutes) and training focus (Endurance, SweetSpot, Threshold, VO₂).
  - Optional: variation toggle to add randomness.
  - Automatic structure: Warm-up (ramp), Main (steady intervals), Cool-down (ramp).

- **Zwift-Compatible Export**
  - Workouts are saved as `.zwo` files (XML).
  - Supports `<SteadyState>`, `<Warmup>`, `<Cooldown>` blocks.
  - Ramps are used only in Warm-up and Cool-down.

- **Workout Preview**
  - In-browser chart (SVG), inspired by [whatsonzwift.com/workouts](https://whatsonzwift.com/workouts).
  - Color-coded by training zone.
  - Tooltips showing duration, %FTP, and notes.
  - Grid lines for FTP zones (70%, 88%, 95%, 105%, 120%).
  - Time markers every 5–10 minutes.
  - Summary with Name, IF (Intensity Factor), TSS (Training Stress Score).

- **Direct Download**
  - One-click download as `.zwo`.

- **Code Structure**
  - Backend in **Flask (Python)**.
  - Frontend in **Tailwind + HTMX**.
  - Core logic separated into `core/` modules.

---

## 📂 Project Structure

```

SpinForge/
│
├── app.py                  # Flask server: routes for preview & download
│
├── core/
│   ├── model.py            # Step & Workout datamodel (with ramps)
│   ├── generator.py        # Workout generator (Warmup, Main, Cooldown)
│   ├── export_zwo.py       # Export to Zwift (.zwo XML)
│   ├── metrics.py          # Compute IF & TSS
│   ├── validator.py        # Sanity checks (min. 5s, 50–300% FTP, ramps only warm/cool)
│   └── nl_parser.py        # (optional) LLM-based free text parser
│
├── templates/
│   └── index.html          # Frontend form, preview & chart (SVG)
│
├── tests/                  # Basic unit tests for generator & export
│
├── requirements.txt        # Python dependencies
└── README.md               # This file

````

---

## ⚙️ Setup

### 1. Clone & install
```bash
git clone https://github.com/sbadecker/SpinForge.git
cd SpinForge
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
````

### 2. Run

```bash
flask run
# or python app.py
```

### 3. Open

[http://localhost:5000](http://localhost:5000)

---

## 🔢 Data Model

**Step**:

* `duration_s`: duration in seconds
* `pct_ftp`: start intensity relative to FTP (e.g., 0.65)
* `pct_ftp_end`: target intensity (only for warmup/cooldown ramps)
* `kind`: `"steady" | "warmup" | "cooldown"`
* `note`: optional description (e.g. “Work”, “Recover”)
* `cadence`: optional cadence target

**Workout**:

* `name`
* `focus` (e.g. “VO2”)
* `steps: List[Step]`

---

## 🖼️ Visualization

* **SVG-based chart**
* Colors per zone:

  * `<70%` Recovery → Green
  * `70–88%` Tempo → Lime
  * `88–95%` SweetSpot → Amber
  * `95–105%` Threshold → Orange
  * `105–120%` VO₂ → Red
  * `>120%` Sprint → Purple
* Warmup & cooldown ramps rendered as multiple sub-steps to simulate slope.

---

## 📈 Metrics

* **IF** = sqrt( (1/T) ∫ p(t)² dt )
* **TSS** = (duration * IF² / 3600) * 100
* For ramps:
  ∫ (linear a→b)² dt = T * (a² + ab + b²) / 3

---

## 🔮 Roadmap

* Free-text workout generator using OpenAI API (LangChain + nl_parser).
* Export to Garmin/TrainerRoad (currently Zwift only).
* User accounts & saved workouts.
* Extended form inputs (interval length, sprint peaks, cadence).

---

## 👨‍💻 Developer Notes

* **Workout logic** → `core/generator.py`
* **Export logic** → `core/export_zwo.py`
* **Preview chart** → `templates/index.html`
* **Validation** → `core/validator.py`
* Run tests with `pytest`.

---

## 📜 License

MIT License
