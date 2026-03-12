import subprocess
import sys

def start_record(url):

    print("Starting browser recorder...")

    cmd = [
        sys.executable,
        "-m",
        "playwright",
        "codegen",
        url,
        "--target",
        "python",
        "-o",
        "recorded_script.py"
    ]

    subprocess.run(cmd)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python recorder.py <url>")
        exit()

    start_record(sys.argv[1])