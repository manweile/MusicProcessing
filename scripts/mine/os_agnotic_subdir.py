# import os
import platform
# import sys
from pathlib import Path

os_name = platform.system()
if os_name == "Windows":
    tld = r"C:\Music\3 Doors Down\3 Doors Down\3 Doors Down-It's Not My Time.mp3"
elif os_name == "Linux":
    tld = r"/home/gerald/Music/3 Doors Down/3 Doors Down/3 Doors Down-It's Not My Time.mp3"

tld_path = Path(tld)
drive = tld_path.drive
root = tld_path.root
anchor = tld_path.anchor
name = tld_path.name
parent = tld_path.parent
parts = tld_path.parts
relative_to = tld_path.relative_to(anchor)

print(f"Drive: {drive}")
print(f"Root: {root}")
print(f"Anchor: {anchor}")
print(f"Name: {name}")
print(f"parent: {parent}")
print(f"Parts: {parts}")
print(f"Relative to: {relative_to}")
