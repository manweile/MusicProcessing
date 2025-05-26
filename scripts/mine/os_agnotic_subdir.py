import os
import sys
from pathlib import Path

tld = r"C:\Music\3 Doors Down\3 Doors Down\3 Doors Down-It's Not My Time.mp3"

tld_path = Path(tld)
root = tld_path.root
anchor = tld_path.anchor
name = tld_path.name
parent = tld_path.parent
parts = tld_path.parent.parts
is_relative = tld_path.is_relative_to(anchor)

print(f"Root: {root}")
print(f"Anchor: {anchor}")
print(f"Name: {name}")
print(f"parent: {parent}")
print(f"Parts: {parts}")
print(f"is relative to: {anchor} {is_relative}")
