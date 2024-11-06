from flask import Flask,render_template,request,jsonify
from pymongo import MongoClient
from os import environ
from dotenv import load_dotenv
from icecream import ic
import pytz
from datetime import datetime
load_dotenv()
app = Flask(__name__)
ic("first")
client = MongoClient(environ.get("mongodb"))
db = client["favourites"]   

favourites_collection = db["favourites"]
devices_collection = db['devices']

favourites = (list(favourites_collection.find({})))
ic("connected.")
ic(favourites)


def time_now():
    saudi_tz = pytz.timezone('Asia/Riyadh')
    current_time = datetime.now(saudi_tz).strftime("%A, %dth of %B, %I:%M %p")
    ic(current_time)
    return current_time



@app.route("/")
def home():
    return render_template("home.html")


@app.route("/favourites",methods=["GET","POST"])
def show_favourites():

    favourites = (list(favourites_collection.find({})))
    found_mariem = any(note['created_by'] == 'Mariem' for note in favourites)
    ic("Finding mariem")
    ic(found_mariem)



    if request.method == "POST":
        headers = dict(request.headers)
        ic(headers)
        user_ip = headers['X-Forwarded-For'] if headers['Host'] == "elyas-notes-production.up.railway.app" else request.remote_addr
        user_agent = headers['User-Agent']
        content = request.form.get("content")
        ic(content)

        device = {
            "user_ip":user_ip,
            "user_agent":user_agent
        }


    return render_template("favourites.html",favourites=favourites,found_mariem=found_mariem)

@app.route('/collect_device_info', methods=['POST'])
def collect_device_info():
    data = request.get_json()
    headers = dict(request.headers)
    ic("DEVICE INFO RECIEVED")
    # Extract and print each data point
    screen_res = data.get('screen_resolution')
    browser = data.get('browser')
    platform = data.get('platform')
    cpu_cores = data.get('cpu_cores')
    memory = data.get('memory')
    user_ip = headers['X-Forwarded-For'] if headers['Host'] == "elyas-notes-production.up.railway.app" else request.remote_addr
    
    devices = list(devices_collection.find({}))
    # ic(list(devices))
    device = {
        "screen_res":screen_res,
        "browser":browser,
        "platform":platform,
        "cpu_cores":cpu_cores,
        "memory":memory,
        "user_ip":user_ip

    }
    for empty_device in [{k:v for k,v in device_without_id.items() if k!= '_id'} for device_without_id in devices]:
        ic(device,empty_device)
        ic("__________________________________________________________")
        ic("__________________________________________________________")
        ic("__________________________________________________________")
        ic("__________________________________________________________")

 


    if device not in [{k:v for k,v in device_without_id.items() if k!= '_id' and k!='times_visited' and k!= 'first_time_visited'} for device_without_id in devices]:
        device["times_visited"] = "first timer"
        device["first_time_visited"] = time_now()
        devices_collection.insert_one(device)
    else:
        # devices_collection.update_one({})
        pass
    
    ic("DEVICE INFO SAVED SUCCESSFULLY")
    # You can save the data to a database or process it here
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    ic("Here")
    app.run(debug=True,host='0.0.0.0',port=8080)
    