import json
import sys

def write(doc, fp=sys.stdout):
    json.dump(doc, fp, sort_keys=True, indent=4)
