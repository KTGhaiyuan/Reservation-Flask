from flask import Flask,redirect,url_for,render_template,jsonify,request
from flask_jwt_extended import (JWTManager,jwt_required,create_access_token,get_jwt_identity,jwt_optional)
from flask_pymongo import PyMongo,ObjectId
import pymongo.errors
import datetime
app = Flask(__name__)

#change this config on product env
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config["MONGO_URI"] = "mongodb://localhost:27017/reservation"
mongo = PyMongo(app)
jwt=JWTManager(app)



@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/register/',methods=["POST"])
def register():
    assert "actual_name" in request.form
    assert "username" in request.form
    assert "password" in request.form
    assert "repeat_password" in request.form

    if(request.form["password"]!=request.form["repeat_password"]):
        return jsonify({"error":"1","errmsg":"Inconsistent password"})
    else:
        actual_name=request.form["actual_name"]
        username=request.form["username"]
        password=request.form["password"]
        try:
            mongo.db.user.insert({"actual_name":actual_name,"username":username,"password":password})
            return jsonify({ "errmsg": "register successful","error": "0"})

        except:
            return jsonify({"error": "1", "errmsg": "Unknow error"})






@app.route('/login/',methods=["POST"])
def login():
    # a=request
    assert "username" in request.form
    assert "password" in request.form
    if "username" in request.form and "password" in request.form:
        username=request.form["username"]
        password=request.form["password"]
        user=mongo.db.user.find_one({"username":username,"password":password})

        if(user==None):
            return jsonify({"error":"1","errmsg":"Bad username or password,login failed"})
        else:
            access_token = create_access_token(identity=username)
            return jsonify({"error":0,"access_token":access_token})

@app.route("/testprotected/",methods=["GET"])
@jwt_required
def testprotected():
    currentuser=get_jwt_identity()

    return currentuser


@app.route("/testoptional/",methods=["GET"])
@jwt_optional
def testoptional():
    currentuser=get_jwt_identity()
    if(currentuser):
        return jsonify({"currentuser":currentuser})
    else:
        return jsonify({"error":1,"errmsg":"No access"})






@app.route("/test/")
def test():
    a=mongo.db.user.insert({"_id" : ObjectId("5bbff2bd24d12bc3d8b518f4"),"username" : "a", "password" : "aa"})
    return "sdf"


@app.route('/reservation/',methods=['POST'])
@jwt_required
def reservation():
    currentuser = get_jwt_identity()
    if (currentuser):
        assert "classroom" in request.form
        assert "sunday" in request.form
        assert "time" in request.form
        assert "date" in request.form

        if "classroom" in request.form and "sunday" in request.form and "time" in request.form:
            classroom = request.form['classroom']
            sunday = request.form['sunday']
            time = request.form['time']
            date=request.form['date']

            useroom=mongo.db.using.find({"classroom":classroom,"sunday":sunday,"time":time,"date":date})
            if useroom!=None:
                return jsonify({"error":1,"msg":"Already scheduled"})
            else:
                mongo.db.using.insert({"classroom":classroom,"sunday":sunday,"time":time,"date":date})
                return  jsonify({"msg":"Scheduled Successful!"})


        else:
            return jsonify({"error":"1","msg":"Reaservation information should be completed"})

    else:
        return jsonify({"error":"please log in first"})



@app.route('/room/',methods=['POST','GET'])
@jwt_required
def room():
    currentuser=get_jwt_identity()
    if(currentuser):
        assert "classroom" in request.form
        assert "sunday" in request.form
        assert "time" in request.form
        assert "date" in request.form

        now=datetime.datetime.now()
        start=datetime.datetime(2018,9,3,0,0,0,000000)
        diff=(now-start).days*24*60*60+(now-start).seconds
        week=int(diff/(7*24*60*60))+1
        # sunday=(int(diff%(7*24*60*60)/(24*60*60)))+1
        # hour=int(((diff%(7*24*60*60)%(24*60*60)))/(60*60))
        # minute=int((((diff%(7*24*60*60)%(24*60*60)))%(60*60))/60)-4

        if "classroom" in request.form and  "sunday" in request.form  and  "time" in request.form:
            classroom=request.form['classroom']
            sunday = request.form['sunday']
            time = request.form['time']
            date=request.form['date']
            rooms=mongo.db.course.find({"classroom":classroom,"sunday":sunday,"time":time})
            for  room  in rooms:
                if  week  in  room['date']:
                    return jsonify({"result":"1","msg":"youke"})

            use=mongo.db.using.find({"classroom":classroom,"sunday":sunday,"time":time,"date":date})
            if use!=None:
                return jsonify({"msg":"Already scheduled"})
            else:
                return jsonify({"msg":"Can be booked"})



        else:
            return jsonify({"error":"1","msg":"Information should be completed"})



    else:
        return jsonify({"error":"please login in first"})




if __name__ == '__main__':
    app.run(debug=True)
