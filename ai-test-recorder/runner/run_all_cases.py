import os
import json
import glob
from runner.run_single_case import run_case

CHECKLIST_DIR = "checklist"
STATE_FILE = "state/cases_state.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE) as f:
        return json.load(f)


def save_state(state):
    os.makedirs("state", exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def run_all():
    state = load_state()
    case_files = glob.glob(f"{CHECKLIST_DIR}/*.yaml")

    for case_file in case_files:
        case_name = os.path.splitext(os.path.basename(case_file))[0]

        # Skip cases already marked as PASS
        if state.get(case_name) == "PASS":
            print(f"Skipping already PASS case: {case_name}")
            continue

        print("Running case:", case_name)
        try:
            run_case(case_file)
            state[case_name] = "PASS"
            print(f"{case_name} PASS")
        except SystemExit as e:
            # run_case calls sys.exit(1) on failure
            state[case_name] = "FAIL"
            print(f"{case_name} FAIL")
        except Exception as e:
            state[case_name] = "FAIL"
            print(f"{case_name} FAIL:", e)

        # Save state after each case
        save_state(state)


if __name__ == "__main__":
    run_all()