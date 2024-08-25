import pandas as pd

# import json
panda_file = pd.read_json("input.json")
# panda = pd.json_normalize(panda_file)
panda_file.to_excel("output.xlsx", index=False)
