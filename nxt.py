import requests

# Files and URL
local_file = "Aki.m3u"
source_url = "https://raw.githubusercontent.com/alex4528y/m3u/refs/heads/main/jtv.m3u"

# Line number where replacement should start
start_line = 1027

# Read existing local file
with open(local_file, "r", encoding="utf-8") as f:
    local_lines = f.readlines()

# Keep everything before line 1027
keep_lines = local_lines[:start_line - 1]

# Fetch remote content
response = requests.get(source_url)
response.raise_for_status()

remote_content = response.text.splitlines(keepends=True)

# Write updated content back
with open(local_file, "w", encoding="utf-8") as f:
    f.writelines(keep_lines)
    f.writelines(remote_content)

print(f"{local_file} updated successfully from line {start_line}")
