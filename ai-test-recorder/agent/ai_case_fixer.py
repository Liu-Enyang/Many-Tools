import yaml
from openai import OpenAI

client = OpenAI()

def fix_case(dom, error, case_yaml):

    prompt = f"""
Test case failed.

DOM:
{dom}

Error:
{error}

Case YAML:
{case_yaml}

Fix selector or step.

Return YAML only.
"""

    resp = client.chat.completions.create(
        model="qwen3-max",
        messages=[{"role":"user","content":prompt}]
    )

    return resp.choices[0].message.content