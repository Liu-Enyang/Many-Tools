import yaml
import re

INPUT_FILE = "recorded_script.py"
OUTPUT_FILE = "checklist/test.yaml"

steps = []

with open(INPUT_FILE) as f:
    lines = f.readlines()

for line in lines:

    if "page.goto" in line:

        url = re.search(r'"(.*?)"', line).group(1)

        steps.append({
            "action": "goto",
            "url": url
        })

    if ".fill(" in line:

        parts = re.findall(r'"(.*?)"', line)

        if len(parts) >= 2:

            steps.append({
                "action": "fill",
                "target": parts[0],
                "value": parts[1]
            })

    if ".click(" in line:

        parts = re.findall(r'"(.*?)"', line)

        if len(parts) >= 1:

            steps.append({
                "action": "click",
                "target": parts[0]
            })


data = {
    "case": "recorded_test",
    "steps": steps
}

with open(OUTPUT_FILE, "w") as f:
    yaml.dump(data, f)

print("Checklist generated:", OUTPUT_FILE)