from bson import ObjectId
from flask import Flask,render_template,request,jsonify, session
from pymongo import MongoClient
from os import environ
from dotenv import load_dotenv
from icecream import ic
import pytz
from datetime import datetime
load_dotenv()

app = Flask(__name__)
app.secret_key = "UHEFUEHFSUSUPERDUPERNIGGA"


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
    ic(session.get('_id'))
    return render_template("home.html")


@app.route("/favourites",methods=["GET","POST"])
def show_favourites():

    favourites = (list(favourites_collection.find({})))
    found_mariem = any(note['created_by'] == 'Mariem' for note in favourites)
    ic("Finding mariem")
    ic(found_mariem)



    if request.method == "POST":

        
        user_id = session.get("_id")
        content = request.form.get("content")

        post = {
            "content":content,
            "date_created":time_now(),
            "created_by":"Mariem"
        }

        if user_id:
            ic("USER EXISTS")
            user = devices_collection.find({"_id":ObjectId(user_id)})
            ic(user)
            devices_collection.update_one({"_id":ObjectId(user_id)},{"$push":{"posts":post}})
            ic("SUCCESSFULLY ADDED POST TO USER")
        favourites_collection.insert_one(post)


        ic(content)

     


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
    user_ip = headers['X-Forwarded-For'] if headers['Host'] == "farouk.up.railway.app" else request.remote_addr
    
    devices = list(devices_collection.find({}))
    ic(list(devices))
   
   

    device_query = {
        "device.screen_res": screen_res,
        "device.browser": browser,
        "device.platform": platform,
        "device.cpu_cores": cpu_cores,
        "device.memory": memory,
        "device.user_ip": user_ip
    }

    existing_device = devices_collection.find_one(device_query)

    if existing_device:
        devices_collection.update_one(device_query,{"$inc":{"device.times_visited":1}})
        devices_collection.update_one(device_query,{"$set":{"device.last_time_visited":time_now()}})
    else: 
        device = {
        "posts":[],
        "screen_res":screen_res,
        "browser":browser,
        "platform":platform,
        "cpu_cores":cpu_cores,
        "memory":memory,
        "user_ip":user_ip,
        "times_visited":1,
        "first_time_visited":time_now(),
        "last_time_visited":time_now()

    }
        
        devices_collection.insert_one({"device":device})
        existing_device = devices_collection.find_one(device_query)

   
    try:
        session['_id'] = str(existing_device['_id'])
    except Exception as e:
        print(f"Error found: {e}")
        ic( f"{existing_device}")
    
    
    ic("DEVICE INFO SAVED SUCCESSFULLY")
 
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    ic("Here")
    app.run(debug=True,host='0.0.0.0',port=8080)
    