from flask import Flask, redirect, url_for, render_template, jsonify, request, flash, get_flashed_messages, \
    make_response
import dotenv
from flask_jwt_extended import (JWTManager, jwt_required, create_access_token, get_jwt_identity, jwt_optional)
from flask_pymongo import PyMongo, ObjectId
import pymongo.errors
import datetime
import utils
import data

app = Flask(__name__)

allroom =data.allroom

# change this config on product env
app.config["MONGO_URI"] = "mongodb://localhost:27017/reservation"

app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config["SECRET_KEY"] = "super secret key"
app.config["JWT_TOKEN_LOCATION"] = ['headers', 'cookies']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = False

mongo = PyMongo(app)
jwt = JWTManager(app)


if(app.config['DEBUG']==True):
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)


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
    elif (request.method == "POST"):
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
                user = mongo.db.user.find_one({"actual_name": str(actual_name), "username": str(username)})
                if user != None:
                    return redirect(url_for("/"))
                else:
                    mongo.db.user.insert(
                        {"actual_name": actual_name, "username": username, "password": password, "identity": identity})
                    # return "注册成功"

                    if ("json" in request.headers and request.headers["json"] == "1"):
                        return jsonify({"msg": "register successful", "error": "0"})
                    else:
                        flash("注册成功", "success")
                        resp = make_response(redirect(url_for("index")))
                        resp.set_cookie("access_token_cookie",
                                        create_access_token(identity=username, expires_delta=False))
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


@app.route("/room/<string:roomname>")
def roomstatus(roomname):
    room = mongo.db.course.find({"classroom":str(roomname)})

    now = datetime.datetime.now()  # 当前时间
    start = datetime.datetime(2018, 9, 3, 0, 0, 0, 000000)  # 开始时间
    diff = (now - start).days * 24 * 60 * 60 + (now - start).seconds  # 距离开学已经过了多长时间
    week = now.weekday() + 1  # 星期几

    dijizhou = int(diff / (7 * 24 * 60 * 60)) + 1  # 当前第几周
    hour = float(((diff % (7 * 24 * 60 * 60) % (24 * 60 * 60))) / (60.0 * 60))  # 今天的第几个小时

    time = utils.numtozh(utils.hourtonlessons(hour))  # 使用今天第几个小时转换成现在第几节课








    for i in room:
        print(i)


    return render_template("roomstatus.html", roomname=roomname)


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


@app.route('/reservation', methods=['POST', 'GET'])
@jwt_required
def reservation():
    if (request.method == "GET"):
        return render_template("reservation.html")

    elif (request.method == "POST"):
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

                timetemp = time[1:-2].replace('"', "").split(",")
                time = []

                for i in timetemp:
                    if (i in ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"] and i not in time):
                        time.append(i)
                reservation_status = []
                status = 0
                for i in time:
                    useroom = mongo.db.using.find_one(
                        {"classroom": str(classroom), "sunday": str(sunday), "time": str(i), "date": str(date)})

                    if useroom != None:
                        status += 0
                    else:
                        mongo.db.using.insert(
                            {"classroom": classroom, "sunday": sunday, "time": str(i), "date": date,
                             'user': currentuser})
                        status += 1
                        reservation_status.append(
                            {"classroom": classroom, "sunday": sunday, "time": str(i), "date": date})
                if (status == 0):
                    return jsonify({"msg": "已经预定"})
                else:
                    return jsonify({"msg": reservation_status})
                    # return jsonify({"msg": "预定成功!"})


            else:
                return jsonify({"error": "1", "msg": "Reaservation information should be completed"})

        else:
            return jsonify({"error": "please log in first"})


@app.route("/", methods=['GET', "POST"])
@jwt_optional
def index():
    currentuser = get_jwt_identity()

    now = datetime.datetime.now()#当前时间
    start = datetime.datetime(2018, 9, 3, 0, 0, 0, 000000)#开始时间
    diff = (now - start).days * 24 * 60 * 60 + (now - start).seconds#距离开学已经过了多长时间
    week = now.weekday() + 1#星期几

    dijizhou = int(diff / (7 * 24 * 60 * 60)) + 1 #当前第几周
    hour = float(((diff % (7 * 24 * 60 * 60) % (24 * 60 * 60))) / (60.0 * 60)) #今天的第几个小时

    time = utils.numtozh(utils.hourtonlessons(hour)) #使用今天第几个小时转换成现在第几节课

    roomstats = {}
    for i in allroom:
        yes = mongo.db.course.find_one(
            {"classroom": str(i), "sunday": str(week), "time": str(time), "date": dijizhou})
        yuding = mongo.db.using.find_one(
            {"classroom": str(i), "sunday": str(week), "time": str(time), "date": dijizhou})
        if (yes != None):
            roomstats[i] = "youke"
        elif (yuding != None):
            roomstats[i] = "yijingyuding"
        else:
            roomstats[i] = "keyuding"

    return render_template("index.html", roomstatsitems=roomstats.items(), currentuser=currentuser)

    # return redirect(url_for("login"))


@jwt.unauthorized_loader
def invalid_token_loaderr(a):
    return redirect(url_for("login"))


@app.route('/cancel', methods=["GET", "POST"])
@jwt_required
def cancel():
    a = request
    if (request.method == "POST"):
        assert "classroom" in request.form
        assert "sunday" in request.form
        # assert "time" in request.form
        assert "date" in request.form
        currentuser = get_jwt_identity()
        if (currentuser):
            classroom = request.form['classroom']
            sunday = request.form['sunday']
            time = request.form['time']
            date = request.form['date']

            timetemp = time[1:-2].replace('"', "").split(",")
            time = []
            for i in timetemp:
                if (i in ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二"] and i not in time):
                    time.append(i)

            # TODO 添加循环time
            try:
                reservation_status = []
                status = 0
                for i in time:
                    useroom = mongo.db.using.find_one(
                        {"classroom": str(classroom), "sunday": str(sunday), "time": str(i), "date": date})
                    if useroom == None:
                        status += 0
                    else:
                        mongo.db.using.remove(
                            {"classroom": str(classroom), "sunday": str(sunday), "time": str(i), "date": date})
                        status += 1
                        reservation_status.append(
                            {"classroom": str(classroom), "sunday": str(sunday), "time": str(i), "date": date})
                if (status == 0):
                    return jsonify({"msg": "没有预定,不能取消!"})
                else:
                    return jsonify({"msg": "取消成功!"})
            except:
                return jsonify({"error": "Please submit the correct room"})

        else:
            return jsonify({"error": "please login in first"})


@app.route('/find', methods=['POST', 'GET'])
@jwt_required
def find():
    currentuser = get_jwt_identity()
    if (request.method == "POST"):
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

                rooms = mongo.db.course.find_one(
                    {"classroom": str(classroom), "sunday": str(sunday), "time": str(time), "date": int(date)})
                if rooms == None:
                    use = mongo.db.using.find_one(
                        {"classroom": str(classroom), "sunday": str(sunday), "time": str(time), "date": date})
                    if use == None:
                        return jsonify({"msg": "可以预定"})
                    else:
                        return jsonify({"msg": "已经被预定!"})
                else:
                    return jsonify({"msg": "有课"})
            else:
                return jsonify({"error": "1", "msg": "Information should be completed"})
        else:
            return jsonify({"error": "please login in first"})
    elif (request.method == "GET"):
        return render_template("find.html")


if __name__ == '__main__':
    app.run()
