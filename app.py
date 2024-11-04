from flask import Flask,render_template,request
from pymongo import MongoClient
from os import environ
from dotenv import load_dotenv
from icecream import ic
load_dotenv()
app = Flask(__name__)
ic("first")
client = MongoClient(environ.get("mongodb"))
db = client["favourites"]   

favourites_collection = db["favourites"]

favourites = (list(favourites_collection.find({})))
ic("connected.")
ic(favourites)
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/favourites",methods=["GET","POST"])
def show_favourites():
    favourites = (list(favourites_collection.find({})))
    found_mariem = any(note['created_by'] == 'Mariem' for note in favourites)
    ic("Finding mariem")
    ic(found_mariem)
    return render_template("favourites.html",favourites=favourites,found_mariem=found_mariem)



if __name__ == '__main__':
    ic("Here")
    app.run(debug=True,host='0.0.0.0',port=8080)
    