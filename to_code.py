# /// script
# requires-python = ">=3.11"
# dependencies = [
# ]
# ///

import os

# Ensure the data directory exists
os.makedirs('./data/logs', exist_ok=True)

# Function to find log files and return the first line of the most recent 10 files
def extract_recent_log_lines():
    log_dir = './data/logs/'
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    # Extract numbers from filenames and sort
    log_files.sort(key=lambda x: int(x.split('-')[1].split('.')[0]))
    # Only keep the most recent 10 files
    recent_files = log_files[-10:]
    # Write the first line of each recent log file to the output file
    with open('./data/logs-recent.txt', 'w') as outfile:
        for log_file in recent_files:
            file_path = os.path.join(log_dir, log_file)
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        if line.strip():  # Skip empty lines
                            outfile.write(line.strip() + '\n')
                            break  # Only take the first non-empty line
            except Exception as e:
                print(f'Error reading {log_file}: {e}')  # Handle missing files or read errors

extract_recent_log_lines()