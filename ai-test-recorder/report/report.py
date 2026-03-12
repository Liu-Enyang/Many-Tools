import sys
import os

# Add project root to Python path so runner module can be found
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from runner.runner import run_tests

results = run_tests()

html = """
<html>
<head>
<title>Test Report</title>
<style>
body{font-family:Arial}
.pass{color:green}
.fail{color:red}
a.view{color:#0066cc;text-decoration:none;font-weight:bold}
a.view:hover{text-decoration:underline}
</style>
</head>
<body>

<h1>Automation Test Report</h1>

<table border=1 cellpadding=10>

<tr>
<th>No.</th>
<th>Test Case</th>
<th>Step</th>
<th>Result</th>
<th>Screenshot</th>
</tr>
"""

for i, r in enumerate(results, start=1):

    cls = "pass" if r["result"] == "PASS" else "fail"

    html += f"""
<tr>
<td>{i}</td>
<td>{r.get('case', '')}</td>
<td>{r['step']}</td>
<td class="{cls}">{r['result']}</td>
<td><a class="view" href="../{r['screenshot']}" target="_blank">View</a></td>
</tr>
"""

html += "</table></body></html>"

import os

os.makedirs("reports", exist_ok=True)

with open("reports/report.html", "w") as f:
    f.write(html)

print("Report generated: reports/report.html")