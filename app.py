from flask import Flask, request, render_template, redirect
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import os, shutil
import pymongo

client = pymongo.MongoClient("mongodb+srv://root:root1234@mycluster.csdveoq.mongodb.net/?retryWrites=true&w=majority")
db = client.Travel #選擇操作 test 資料庫
collection = db.travels # 選擇操作 users 集合


app = Flask(
    __name__,
    )


@app.route("/")
def Home():
    values = list(collection.find({}))

    return render_template("index.html", values=values)

@app.route("/Inc1st")
def Inc1st():
    return render_template("Increase.html")

@app.route("/Inc2nd", methods=["POST"])
def Inc2nd():
    
    personnm = request.form["personnm"]
    traveltime = request.form["traveltime"]
    travelnm = request.form["travelnm"]
    comment = request.form["comment"]

    Newtrip = collection.insert_one({
        "name":personnm,
        "time":traveltime,
        "travel":travelnm,
        "comment":comment,
        "photo":[]
        })


    tripnm = collection.find_one({'_id':ObjectId(Newtrip.inserted_id)})

    return render_template("PhotoInc.html", tripnm=tripnm)


@app.route("/List")
def Input():
    values = list(collection.find({}))

    return render_template("List.html", values=values)


@app.route("/Output")
def Output():
    trip_id = request.args.get("trip-id")
    values = list(collection.find({}))
    tripnm = collection.find_one({'_id':ObjectId(trip_id)})
    print(tripnm['photo'])

    return render_template("output.html", values=values, tripnm=tripnm)


@app.route("/Mod", methods=["POST"])
def Mod():
    trip_id = request.form["trip-id"]
    tripnm = collection.find_one({'_id':ObjectId(trip_id)})
    return render_template("Modify.html", tripnm=tripnm)

@app.route("/ModDel", methods=["GET","POST"])
def ModDel():

    if request.method == "POST":
        trip_id = request.form["trip-id"]
        personnm = request.form["personnm"]
        traveltime = request.form["traveltime"]
        travelnm = request.form["travelnm"]
        comment = request.form["comment"]

        collection.update_one({"_id":ObjectId(trip_id)},
        {"$set":{
        "name":personnm,
        "time":traveltime,
        "travel":travelnm,
        "comment":comment
        }})

    elif request.method == "GET":
        trip_id = request.args.get("trip-id")
        collection.delete_one({'_id':ObjectId(trip_id)})
        shutil.rmtree(os.path.join(os.getcwd(), 'static', 'img', trip_id), ignore_errors=True)

    values = list(collection.find({}))

    return render_template("List.html", values=values)


# 上傳圖片函式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/Upload", methods=['GET', 'POST'])
def Upload(): 
    if request.method == 'POST':
        trip_id = request.form["trip-id"]
        UPLOAD_FOLDER= os.path.join(os.getcwd(), 'static', 'img', trip_id)
        if not os.path.isdir(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        else:
            pass

        uploaded_files = request.files.getlist("file[]")

    filenames = []
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            filenames.append(filename)

    collection.update_one({"_id":ObjectId(trip_id)},
    {"$set":{"photo":filenames}})

    return redirect('/List')

app.run()