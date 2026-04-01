import subprocess
import sys

if len(sys.argv) < 2:
    print("Usage: python recorder.py <url>")
    sys.exit(1)

url = sys.argv[1]

print("Starting browser recorder...")
print("Close the browser window when finished recording.")

subprocess.run([
    sys.executable,
    "-m",
    "playwright",
    "codegen",
    url,
    "--target",
    "python",
    "-o",
    "recorded_script.py"
])

print("Recording saved to recorded_script.py")