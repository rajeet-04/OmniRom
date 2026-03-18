# -*- coding: utf-8 -*-
import sys

sys.path.insert(0, "R:/Code/OmniRom")

# Direct test of the romanizer
import importlib.util

spec = importlib.util.spec_from_file_location(
    "arabic_urdu_romanizer", "app/engines/arabic_urdu_romanizer.py"
)
module = importlib.util.module_from_spec(spec)

# Read and execute the module
with open("app/engines/arabic_urdu_romanizer.py", "r", encoding="utf-8") as f:
    code = f.read()
    exec(code, globals())

text = "زخم دل پہ ہیں، دوا کرو"
result = romanize_arabic_urdu(text)

with open("test_output.json", "w", encoding="utf-8") as f:
    import json

    json.dump({"input": text, "output": result}, f, indent=2, ensure_ascii=False)
