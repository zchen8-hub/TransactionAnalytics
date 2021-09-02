from flask import Flask, request, redirect
import subprocess
import json
import os


app = Flask(__name__)

def start_streamlit_server():
    r =subprocess.call("streamlit run server.py --server.port 8091&>/dev/null&", shell=True)
    print('server started', r)


@app.route("/", methods=['GET', 'POST'])
def run_app():
    try:
        json_req = request.get_json()
        if json_req:
            with open('data.json', 'w') as f:
                json.dump(json_req,f)
            print("data.json is updated")
        else:
            print("no json passed.")
    except:
        print("No json passed. Using old data.json file")

    if not os.path.exists("data.json"):
        print("no data.json found. Quit...")
        return "No data.json found"
    start_streamlit_server()
    if request.method == 'GET':
        return redirect('http://localhost:8091')
    else:
        return "URL: http://localhost:8091"

if __name__ == '__main__':
    app.run('0.0.0.0', port=8090)