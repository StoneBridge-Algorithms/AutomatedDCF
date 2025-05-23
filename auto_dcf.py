import subprocess
import sys
import re
from dotenv import load_dotenv
load_dotenv()
import os

if len(sys.argv) != 2:
    print("Usage: python3 run_all.py <TICKER>")
    sys.exit(1)

ticker = sys.argv[1].upper()
API_KEY = os.getenv("FMP_API_KEY")

try:
    output = subprocess.check_output(["python3", "work.py", ticker], text=True)
except subprocess.CalledProcessError as e:
    print("Error running work.py:", e)
    sys.exit(1)

lines = output.strip().splitlines()
if not lines:
    print("No output from work.py")
    sys.exit(1)

last_line = lines[-1]  # should be like "12.00%"
match = re.search(r'([0-9.]+)%', last_line)
if not match:
    print("No percentage found in work.py output")
    sys.exit(1)

percent = float(match.group(1))
eg_value = round(percent / 100, 3)

try:
    subprocess.run([
        "python3", "main.py",
        "--t", ticker,
        "--i", "annual",
        "--y", "3",
        "--eg", str(eg_value),
        "--steps", "2",
        "--s", "0.1",
        "--v", "eg",
        "--apikey", API_KEY
    ], check=True)
except subprocess.CalledProcessError as e:
    print("Error running main.py:", e)
    sys.exit(1)
