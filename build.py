import subprocess
import sys
import os

# Change to the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Run pyinstaller
result = subprocess.run([sys.executable, '-m', 'pyinstaller', '--onefile', 'SO_analysis.py'], capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("STDERR:")
print(result.stderr)
print("Return code:", result.returncode)