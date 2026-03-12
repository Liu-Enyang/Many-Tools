import sys
import os

# Add project root to Python path so runner module can be found
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from runner.runner import run_tests


results = run_tests()

# Calculate statistics (ignore case_summary records)
step_results = [r for r in results if r.get("type") != "case_summary"]

total_steps = len(step_results)
pass_count = sum(1 for r in step_results if r["result"] == "PASS")
fail_count = sum(1 for r in step_results if r["result"] == "FAIL")

cases = set(r.get("case", "") for r in step_results if r.get("case"))
total_cases = len(cases)

pass_rate = (pass_count / total_steps * 100) if total_steps else 0
# Calculate total duration from all step durations
total_duration = round(sum(r.get("duration", 0) for r in step_results), 3)

# Calculate case level results and duration
case_results = {}
case_durations = {}

for r in results:
    case_name = r.get("case", "")
    if not case_name:
        continue

    if r.get("type") == "case_summary":
        case_durations[case_name] = r.get("duration", "")
        continue

    if case_name not in case_results:
        case_results[case_name] = "PASS"

    if r["result"] == "FAIL":
        case_results[case_name] = "FAIL"

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
<b>Total Cases:</b> {total_cases} <br>
<b>Total Steps:</b> {total_steps} <br>
<b>PASS:</b> <span class="pass">{pass_count}</span> <br>
<b>FAIL:</b> <span class="fail">{fail_count}</span> <br>
<b>Pass Rate:</b> {pass_rate:.1f}% <br>
<b>Total Duration:</b> {total_duration}s
</div>

<br>

<h2>Case Summary</h2>
<table border=1 cellpadding=8>
<tr>
<th>Test Case</th>
<th>Result</th>
<th>Duration(s)</th>
</tr>
"""

for case_name, result in case_results.items():
    cls = "pass" if result == "PASS" else "fail"
    duration = case_durations.get(case_name, "")
    html += f"""
<tr>
<td>{case_name}</td>
<td class="{cls}">{result}</td>
<td>{duration}</td>
</tr>
"""
html += "</table><br><br>"

html += """
<table border=1 cellpadding=10>

<tr>
<th>No.</th>
<th>Test Case</th>
<th>Step</th>
<th>Result</th>
<th>Duration(s)</th>
<th>Screenshot</th>
</tr>
"""

step_index = 1
for r in results:

    if r.get("type") == "case_summary":
        continue

    cls = "pass" if r["result"] == "PASS" else "fail"
    duration = r.get("duration", "")

    html += f"""
<tr>
<td>{step_index}</td>
<td>{r.get('case', '')}</td>
<td>{r['step']}</td>
<td class="{cls}">{r['result']}</td>
<td>{duration}</td>
<td><a class="view" href="../{r['screenshot']}" target="_blank">View</a></td>
</tr>
"""
    step_index += 1

html += "</table></body></html>"

import os

os.makedirs("reports", exist_ok=True)

with open("reports/report.html", "w") as f:
    f.write(html)

print("Report generated: reports/report.html")