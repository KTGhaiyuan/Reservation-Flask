from flask import Flask, redirect, url_for, render_template, jsonify, request, flash, get_flashed_messages, \
    make_response
import dotenv
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token, get_jwt_identity, jwt_optional)
from flask_pymongo import PyMongo, ObjectId
import pymongo.errors
import datetime
import utils

app = Flask(__name__)
allroom = ["101","111","105","108","201","202","204","205","208","212","301","302","304","305","308","310","312","第一电教室","第三电教室","第五电教室","第六电教室","第七电教室","第二电教室", "新平一","新平二","新平三","新平四","食品实验室","生物实验室一","生物实验室二","生物实验室三","生物实验室四","无机实验室","有机实验室","水化实验室","生化实验室","第三机房","第四机房","第五机房","第六机房","第一机房","第二机房","语音室02","第12机房", "第34机房","新语音室","旧语音室","电工电子实验室","金相实验室","发动机构造实验室","汽车维修实验室","发动机性能实验室","汽车电气实验室","电喷发动机试验室","汽车综合实习车间","基础实验室","冷库","空调实验室","制冷机械设备实验室","小型制冷实验室","旧平一","综合车间","绘图室","显微镜实验室"]


# change this config on product env
app.config["MONGO_URI"] = "mongodb://localhost:27017/reservation"

app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config["SECRET_KEY"] = "super secret key"
app.config["JWT_TOKEN_LOCATION"] = ['headers', 'cookies']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"]=False
# app.secret_key = "super secret key"
mongo = PyMongo(app)
jwt = JWTManager(app)

# print(mongo.db.course.find_one({"classroom": "111", "sunday": "4", "time": "九","date":3}))



"""
flash category:
https://getbootstrap.com/docs/4.0/components/alerts/
"""


@app.route("/testjwt")
def testjwt():
    aa = make_response(render_template("index.html"))
    aa.set_cookie("access_token_cookie", create_access_token(identity="a", expires_delta=False))
    return aa

@app.route('/hw')
def helloworld():
    if ("json" in request.headers and request.headers["json"] == "1"):
        return "asdf"
    else:
        return render_template("index.html")


@app.route("/test")
@jwt_required
def test():
    currentuser = get_jwt_identity()
    return currentuser
    # aa = make_response(redirect(url_for(endpoint="helloworld")))
    # aa.set_cookie('a', 'aa')
    # flash("asfas", "warning")
    # return aa

@app.route('/register', methods=["GET", "POST"])
def register():
    if (request.method == "GET"):
        return render_template("register.html")
    elif(request.method=="POST"):
        assert "actual_name" in request.form
        assert "username" in request.form
        assert "password" in request.form
        assert "identity" in request.form
        assert "repeat_password" in request.form

        if (request.form["password"] != request.form["repeat_password"]):
            return jsonify({"error": "1", "errmsg": "Inconsistent password"})
        else:
            actual_name = request.form["actual_name"]
            username = request.form["username"]
            identity = request.form["identity"]
            password = request.form["password"]
            try:
                user=mongo.db.user.find_one({"actual_name": str(actual_name),"username":str(username)})
                if user!=None:
                    return redirect(url_for("/"))
                else:
                    mongo.db.user.insert(
                        {"actual_name": actual_name, "username": username, "password": password, "identity": identity})
                    #return "注册成功"

                    if ("json" in request.headers and request.headers["json"] == "1"):
                        return jsonify({"msg": "register successful", "error": "0"})
                    else:
                        flash("注册成功", "success")
                        resp=make_response(redirect(url_for("index")))
                        resp.set_cookie("access_token_cookie",create_access_token(identity=username,expires_delta=False))
                        return resp
            except:
                if ("json" in request.headers and request.headers["json"] == "1"):
                    return jsonify({"error": "1", "errmsg": "Unknow error"})
                else:
                    flash("已经注册,去登陆", "danger")
                    return redirect(url_for("register"))




@app.route('/login', methods=["POST", "GET"])
def login():
    if (request.method == "GET"):
        return render_template("login.html")

    assert "username" in request.form
    assert "password" in request.form
    if "username" in request.form and "password" in request.form:
        username = request.form["username"]
        password = request.form["password"]
        user = mongo.db.user.find_one({"username": str(username), "password": str(password)})

        if (user == None):
            if ("json" in request.headers and request.headers["json"] == "1"):
                return jsonify({"error": "1", "errmsg": "Bad username or password,` failed"})
            else:
                flash("登录失败,请检查用户名或密码", "danger")
                return redirect(url_for("login"))
        else:

            access_token = create_access_token(identity=username, expires_delta=False)

            if ("json" in request.headers and request.headers["json"] == "1"):
                return jsonify({"error": 0, "access_token": access_token})
            else:
                resp = redirect(url_for("index"))
                resp.set_cookie("access_token_cookie", access_token)
                return resp

@app.route("/testprotected", methods=["GET"])
@jwt_required
def testprotected():
    currentuser = get_jwt_identity()

    return currentuser


@app.route("/testoptional", methods=["GET"])
@jwt_optional
def testoptional():
    currentuser = get_jwt_identity()
    if (currentuser):
        return jsonify({"currentuser": currentuser})
    else:
        return jsonify({"error": 1, "errmsg": "No access"})


@app.route('/reservation', methods=['POST','GET'])
@jwt_required
def reservation():
    if(request.method=="POST"):
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
                date = request.form['date']

                useroom = mongo.db.using.find_one({"classroom": classroom, "sunday": sunday, "time": time, "date": date})
                if useroom != None:
                    return jsonify({"error": 1, "msg": "Already scheduled"})
                else:
                    mongo.db.using.insert({"classroom": classroom, "sunday": sunday, "time": time, "date": date, 'user': currentuser})
                    return jsonify({"msg": "Reservation Successful!"})


            else:
                return jsonify({"error": "1", "msg": "Reaservation information should be completed"})

        else:
            return jsonify({"error": "please log in first"})
    elif(request.method=="GET"):
        return render_template("reservation.html")

@app.route("/",methods=['GET',"POST"])
@jwt_required
def index():
    currentuser = get_jwt_identity()
    if (currentuser):
        now = datetime.datetime.now()
        start = datetime.datetime(2018, 9, 3, 0, 0, 0, 000000)
        diff = (now - start).days * 24 * 60 * 60 + (now - start).seconds
        week = now.weekday() + 1

        dijizhou = int(diff / (7 * 24 * 60 * 60)) + 1
        hour = float(((diff % (7 * 24 * 60 * 60) % (24 * 60 * 60))) / (60.0 * 60))

        time = utils.numtozh(utils.hourtonlessons(hour))
        roomstats = {}
        for i in allroom:
            yes = mongo.db.course_new.find_one(
                {"classroom": str(i), "sunday": str(week), "time": str(time), "date": dijizhou})
            yuding = mongo.db.using.find_one(
                {"classroom": str(i), "sunday": str(week), "time": str(time), "date": dijizhou})
            if (yes != None):
                roomstats[i] = "youke"
            elif (yuding != None):
                roomstats[i] = "yijingyuding"
            else:
                roomstats[i] = "keyuding"

        return render_template("index.html", roomstatsitems=roomstats.items(),currentuser=currentuser)
    else:
        return redirect(url_for("login"))


@jwt.unauthorized_loader
def invalid_token_loaderr(a):
    flash("请先登陆")
    return redirect(url_for("login"))


@app.route('/cancel')
@jwt_required
def cancel():
    if(request.method=="POST"):
        assert "classroom" in request.form
        assert "sunday" in request.form
        assert "time" in request.form
        assert "date" in request.form
        currentuser = get_jwt_identity()
        if(currentuser):
            classroom = request.form['classroom']
            sunday = request.form['sunday']
            time = request.form['time']
            date = request.form['date']
            if (currentuser):
                try:
                    mongo.db.using.remove({"classroom": str(classroom), "sunday": str(sunday), "time": str(time), "date": date, 'user': str(currentuser)})
                    flash("取消成功!")
                    return redirect(url_for('/reservation'))
                except:
                    return jsonify({"error": "Please submit the correct room"})
        else:
            return jsonify({"error": "please login in first"})

@app.route('/find', methods=['POST', 'GET'])
@jwt_required
def find():
    currentuser = get_jwt_identity()
    if(request.method=="POST"):
        if (currentuser):
            assert "classroom" in request.form
            assert "sunday" in request.form
            assert "time" in request.form
            assert "date" in request.form

            # now = datetime.datetime.now()
            # start = datetime.datetime(2018, 9, 3, 0, 0, 0, 000000)
            # diff = (now - start).days * 24 * 60 * 60 + (now - start).seconds
            # week = int(diff / (7 * 24 * 60 * 60)) + 1
            # sunday=(int(diff%(7*24*60*60)/(24*60*60)))+1
            # hour=int(((diff%(7*24*60*60)%(24*60*60)))/(60*60))
            # minute=int((((diff%(7*24*60*60)%(24*60*60)))%(60*60))/60)-4

            if "classroom" in request.form and "sunday" in request.form and "time" in request.form:
                classroom = request.form['classroom']
                sunday = request.form['sunday']
                time = request.form['time']
                date = request.form['date']
                rooms = mongo.db.course_new.find_one({"classroom": str(classroom), "sunday": str(sunday), "time": str(time),"date":int(date)})
                print(rooms)
                if rooms==None:
                    use = mongo.db.using.find_one({"classroom": str(classroom), "sunday": str(sunday), "time": str(time), "date": date,"user":str(currentuser)})
                    if use==None:
                        return jsonify({"msg":"keyiyuding"})
                    else:
                        return jsonify({"msg":"yijingyuding"})
                else:
                    return jsonify({"msg":"youke"})
            else:
                return jsonify({"error": "1", "msg": "Information should be completed"})
        else:
            return jsonify({"error": "please login in first"})
    elif(request.method=="GET"):
        return render_template("find.html")


if __name__ == '__main__':
    app.run(debug=True)
