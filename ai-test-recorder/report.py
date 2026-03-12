import os
from jinja2 import Template
from runner import execute


results = execute()

html_template = """
<html>
<head>
<title>Test Report</title>
<style>

body{
font-family:Arial;
}

table{
border-collapse: collapse;
width: 80%;
}

th,td{
border:1px solid #ccc;
padding:8px;
}

.pass{
color:green;
}

.fail{
color:red;
}

</style>
</head>

<body>

<h1>Automation Test Report</h1>

<table>

<tr>
<th>Result</th>
<th>Action</th>
<th>Target</th>
</tr>

{% for r in results %}

<tr>

<td class="{{r.result|lower}}">{{r.result}}</td>

<td>{{r.step.action}}</td>

<td>{{r.step.get('target','')}}</td>

</tr>

{% endfor %}

</table>

</body>
</html>
"""

template = Template(html_template)

output = template.render(results=results)
os.makedirs("reports", exist_ok=True)
with open("reports/report.html", "w") as f:
    f.write(output)

print("Report generated: reports/report.html")