from jinja2 import Template
from runner import run_tests
import os

os.makedirs("reports", exist_ok=True)

results = run_tests()

html = """
<html>
<head>
<title>Automation Report</title>

<style>

body{
font-family:Arial;
background:#f5f5f5;
}

table{
border-collapse: collapse;
width:90%;
background:white;
}

th,td{
border:1px solid #ddd;
padding:10px;
}

.pass{
color:green;
font-weight:bold;
}

.fail{
color:red;
font-weight:bold;
}

</style>

</head>

<body>

<h1>Automation Test Report</h1>

<table>

<tr>
<th>Test</th>
<th>Step</th>
<th>Result</th>
<th>Error</th>
<th>Screenshot</th>
</tr>

{% for r in results %}

<tr>

<td>{{r.test}}</td>

<td>{{r.step}}</td>

<td class="{{r.result|lower}}">{{r.result}}</td>

<td>{{r.get("error","")}}</td>

<td>
{% if r.get("screenshot") %}
<a href="../{{r.screenshot}}">view</a>
{% endif %}
</td>

</tr>

{% endfor %}

</table>

</body>
</html>
"""

template = Template(html)

output = template.render(results=results)

with open("reports/report.html","w") as f:
    f.write(output)

print("Report generated: reports/report.html")