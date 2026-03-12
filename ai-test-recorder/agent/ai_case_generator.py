import os
import yaml
from openai import OpenAI

CHECKLIST_DIR = "checklist"

client = OpenAI()

def save_cases(yaml_text):

    data = yaml.safe_load(yaml_text)

    os.makedirs(CHECKLIST_DIR, exist_ok=True)

    for case in data["tests"]:

        name = case["name"]

        path = f"{CHECKLIST_DIR}/{name}.yaml"

        with open(path, "w") as f:
            yaml.dump(case, f)

        print("Saved case:", name)