import os
import json
import brotli
import fastlz
import requests
import time

def path_to_dict(path):
    d = {'name': os.path.basename(path)}
    # path
    if os.path.isdir(path):
        d['type'] = "directory"
        d['children'] = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
    else:
		d['type'] = "file"
		d["mtime"] = time.ctime(os.path.getmtime(path))
    return d

# applications =  brotli.compress(json.dumps(path_to_dict('/Applications/')))
user = fastlz.compress(json.dumps(path_to_dict("/Users/rafalstapinski/")))

url = "http://localhost:8080/structure/new"

f = {"structure": ("structure.bro", user)}

r = requests.post(url, files=f)
