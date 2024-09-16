from pathlib import Path

import camelot

dir = Path("./input/pdf/").glob("*.pdf")
for file in dir.iterdir():
    print(file)
