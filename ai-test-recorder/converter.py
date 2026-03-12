import yaml
import re

INPUT_FILE = "recorded_script.py"
OUTPUT_FILE = "checklist/tests.yaml"

steps = []

with open(INPUT_FILE) as f:
    lines = f.readlines()

for line in lines:

    line = line.strip()

    # goto
    if "page.goto" in line:
        url_match = re.search(r'"(.*?)"', line)
        if url_match:
            steps.append({
                "action": "goto",
                "url": url_match.group(1)
            })

    # fill
    if ".fill(" in line:

        role_name_match = re.search(r'get_by_role\("(.*?)",\s*name="(.*?)"\)', line)
        role_match = re.search(r'get_by_role\("(.*?)"\)', line)
        placeholder_match = re.search(r'get_by_placeholder\("(.*?)"\)', line)
        label_match = re.search(r'get_by_label\("(.*?)"\)', line)

        value_match = re.search(r'\.fill\("(.*?)"\)', line)

        if value_match:
            value = value_match.group(1)

            if role_name_match:
                target = f'role={role_name_match.group(1)}[name="{role_name_match.group(2)}"]'
            elif role_match:
                target = f"role={role_match.group(1)}"
            elif placeholder_match:
                target = f"placeholder={placeholder_match.group(1)}"
            elif label_match:
                target = f"label={label_match.group(1)}"
            else:
                parts = re.findall(r'"(.*?)"', line)
                if len(parts) >= 2:
                    target = parts[0]
                else:
                    continue

            steps.append({
                "action": "fill",
                "target": target,
                "value": value
            })

    # click
    if ".click(" in line:

        role_name_match = re.search(r'get_by_role\("(.*?)",\s*name="(.*?)"\)', line)
        role_match = re.search(r'get_by_role\("(.*?)"\)', line)
        text_match = re.search(r'get_by_text\("(.*?)"\)', line)
        label_match = re.search(r'get_by_label\("(.*?)"\)', line)

        if role_name_match:
            target = f'role={role_name_match.group(1)}[name="{role_name_match.group(2)}"]'
        elif role_match:
            target = f"role={role_match.group(1)}"
        elif text_match:
            target = f"text={text_match.group(1)}"
        elif label_match:
            target = f"label={label_match.group(1)}"
        else:
            parts = re.findall(r'"(.*?)"', line)
            if len(parts) >= 1:
                target = parts[0]
            else:
                continue

        steps.append({
            "action": "click",
            "target": target
        })

    # select dropdown
    if ".select_option(" in line:
        label_match = re.search(r'get_by_label\("(.*?)"\)', line)
        value_match = re.search(r'select_option\("(.*?)"\)', line)

        if label_match and value_match:
            steps.append({
                "action": "select",
                "target": f"label={label_match.group(1)}",
                "value": value_match.group(1)
            })

    # assertions (text visible)
    if "expect(" in line and "to_be_visible" in line:
        text_match = re.search(r'get_by_text\("(.*?)"\)', line)
        if text_match:
            steps.append({
                "action": "assert_text",
                "text": text_match.group(1)
            })


data = {
    "tests": [
        {
            "name": "recorded_test",
            "steps": steps
        }
    ]
}

with open(OUTPUT_FILE, "w") as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False)

print("Checklist generated:", OUTPUT_FILE)