import requests
import json


json_content = json.load(open('input.json'))
req = requests.post("http://localhost:8090",json=json_content)
print(req.text)
