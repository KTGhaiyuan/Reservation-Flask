from flask import Flask,redirect,url_for,render_template
# import config

app = Flask(__name__)
# app.config.from_object(config)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/login/')
def login():
    return  render_template('login.html')

@app.route('/register/')
def register():
    return  "jcsausao"

@app.route('/reservation/')
def reservation():
    return  "sfsafsaf"
@app.route('/room_info/')
def room_info():
    return  "fsaf"



if __name__ == '__main__':
    app.run(debug=True)
