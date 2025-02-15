# /// script
# requires-python = ">=3.11"
# dependencies = [
# ]
# ///

import os
import glob

# Create the data directory if it doesn't exist
os.makedirs('./data/', exist_ok=True)

# Path to the log files
dir_path = './data/logs/'
# Get the 10 most recent log files
log_files = sorted(glob.glob(os.path.join(dir_path, '*.log')), key=os.path.getmtime, reverse=True)[:10]

# Collect the first line of each log file
recent_lines = []
for log_file in log_files:
    with open(log_file, 'r') as file:
        first_line = file.readline().strip()  # Read the first line
        recent_lines.append(first_line)

# Write the collected lines to a new file
with open('./data/logs-recent.txt', 'w') as output:
    for line in recent_lines:
        output.write(line + '\n')