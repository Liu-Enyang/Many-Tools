import os
import json
import yaml
import glob
import imageio.v2 as imageio

# Paths
STATE_FILE = "state/cases_state.json"
CHECKLIST_DIR = "checklist"
GIF_DIR = "reports/gifs"
REPORT_PATH = "reports/report.html"

os.makedirs(GIF_DIR, exist_ok=True)

# Load case state
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        state = json.load(f)
else:
    state = {}

# Collect all case YAML files
case_files = glob.glob(f"{CHECKLIST_DIR}/*.yaml")

# Prepare GIFs mapping
case_gifs = {}
for file in case_files:
    case_name = os.path.splitext(os.path.basename(file))[0]
    gif_path = f"{GIF_DIR}/{case_name}.gif"
    if os.path.exists(gif_path):
        case_gifs[case_name] = gif_path

# Generate HTML
html = f"""
<html>
<head>
<title>Test Report</title>
<style>
body{{font-family:Arial}}
.pass{{color:green}}
.fail{{color:red}}
a.view{{color:#0066cc;text-decoration:none;font-weight:bold}}
a.view:hover{{text-decoration:underline}}
</style>
</head>
<body>

<h1>Automation Test Report</h1>

<div>
<b>Total Cases:</b> {len(case_files)} <br>
<b>PASS:</b> <span class="pass">{sum(1 for s in state.values() if s=='PASS')}</span> <br>
<b>FAIL:</b> <span class="fail">{sum(1 for s in state.values() if s=='FAIL')}</span> <br>
</div>

<br>

<h2>Case Summary</h2>
<table border=1 cellpadding=8>
<tr>
<th>Test Case</th>
<th>Result</th>
<th>Replay</th>
</tr>
"""

for file in case_files:
    case_name = os.path.splitext(os.path.basename(file))[0]
    result = state.get(case_name, "NOT RUN")
    cls = "pass" if result == "PASS" else "fail"
    gif = case_gifs.get(case_name, "")
    replay = f'<a class="view" href="../{gif}" target="_blank">Replay</a>' if gif else ""
    html += f"""
<tr>
<td>{case_name}</td>
<td class="{cls}">{result}</td>
<td>{replay}</td>
</tr>
"""

html += "</table><br><br>"

# Step details table with durations
html += """
<table border=1 cellpadding=10>
<tr>
<th>No.</th>
<th>Test Case</th>
<th>Step</th>
<th>Step Duration</th>
<th>Case Duration</th>
<th>Total Duration</th>
<th>Result</th>
<th>Screenshot</th>
</tr>
"""

step_index = 1
total_duration = 0.0

for file in case_files:
    case_name = os.path.splitext(os.path.basename(file))[0]
    with open(file) as f:
        case = yaml.safe_load(f)
    steps = case.get("steps", [])
    case_start = steps[0].get("start_time", 0) if steps else 0
    case_end = steps[-1].get("end_time", 0) if steps else 0
    case_duration = case_end - case_start
    total_duration += case_duration

    for step in steps:
        step_name = step.get("action", "")
        step_duration = step.get("duration", 0)
        result = state.get(case_name, "NOT RUN")
        cls = "pass" if result=="PASS" else "fail"
        screenshot = step.get("screenshot", "")
        # screenshot_link = f'<a class="view" href="../{screenshot}" target="_blank">View</a>' if screenshot else ""
        if screenshot:
            # Adjust path to be relative to reports/report.html in reports/screenshots/
            screenshot_path = f"screenshots/{os.path.basename(screenshot)}"
            screenshot_link = f'<a class="view" href="{screenshot_path}" target="_blank">View</a>'
        else:
            screenshot_link = ""
        html += f"""
<tr>
<td>{step_index}</td>
<td>{case_name}</td>
<td>{step_name}</td>
<td>{step_duration:.2f}s</td>
<td>{case_duration:.2f}s</td>
<td>{total_duration:.2f}s</td>
<td class="{cls}">{result}</td>
<td>{screenshot_link}</td>
</tr>
"""
        step_index += 1

html += "</table></body></html>"

os.makedirs("reports", exist_ok=True)
with open(REPORT_PATH, "w") as f:
    f.write(html)

print(f"Report generated: {REPORT_PATH}")