# /// script
# requires-python = ">=3.11"
# dependencies = [
# ]
# ///

import os
import glob

# Ensure the data directory exists
os.makedirs('./data/', exist_ok=True)

# Path to log files
log_path = './data/logs/*.log'
# Get the list of log files and sort them by modification time, most recent first
log_files = sorted(glob.glob(log_path), key=os.path.getmtime, reverse=True)

# Open the output file to write recent log file lines
with open('./data/logs-recent.txt', 'w') as recent_log:
    for log_file in log_files[:10]:  # Get the 10 most recent log files
        with open(log_file, 'r') as f:
            first_line = f.readline().strip()  # Read the first line
            recent_log.write(f'{log_file}: {first_line}\n')  # Write filename and first line
