import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///training.db")


@app.route("/login", methods=["GET", "POST"])       ## From CS50 Finance
def login():
    """Log user in."""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")               ## From CS50 Finance
def logout():
    """Log user out."""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user for an account."""

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("username"):
            return apology("Missing username")
        elif not request.form.get("clas"):
            return apology("Missing clas")
        elif not request.form.get("password"):
            return apology("Missing password")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match")
        hash=generate_password_hash(request.form.get("password"))
        username=request.form.get("username")
        clas=request.form.get("clas")
        id = db.execute("INSERT INTO users (username, hash, clas) VALUES(:username, :hash, :clas)", username=username, hash=hash, clas=clas)
        if not id:
            return apology("username taken")
        session["user_id"] = id
        return redirect("/")

    # GET
    else:
        return render_template("register.html")


@app.route("/password_change", methods=["GET", "POST"])
@login_required
def password_change():

    if request.method == "POST":
        if not request.form.get("current_password"):
            return apology("provide current password")
        rows = db.execute("SELECT hash FROM users WHERE id = :user_id", user_id=session["user_id"])
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("current_password")):
            return apology("invalid password")
        if not request.form.get("new_password"):
            return apology("provide new password")
        elif not request.form.get("new_confirmation"):
            return apology("provide new password confirmation")
        elif request.form.get("new_password") != request.form.get("new_confirmation"):
            return apology("new password and confirmation don't match")
        hash = generate_password_hash(request.form.get("new_password"))
        rows = db.execute("UPDATE users SET hash = :hash WHERE id = :user_id", user_id=session["user_id"], hash=hash)
        return redirect("/")
    else:
        return render_template("password_change.html")

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():

    if request.method == "GET":
        return render_template("add.html")
    else:
        if not request.form.get("time"):
            return apology("provide an amount of time")
        time = int(request.form.get("time"))
        if time <= 0:
            return apology("provide an amount of time")
        type = request.form.get("type")
        db.execute("INSERT INTO log (user_id, time, type) VALUES(:user_id, :time, :type)", user_id=session["user_id"], time=time, type=type)
        return redirect("/")

@app.route("/my_log")
@login_required
def my_log():
    # takes all current users informtaion and puts into a table
    history = db.execute("SELECT time, type, date_created FROM log WHERE user_id = :user_id ORDER BY date_created", user_id=session["user_id"])
    total_time = 0
    # list for recall using flask in html page
    numbers = []
    for i in range(len(history)):
        numbers.append(i)
        total_time = total_time + int(history[i]['time'])
    return render_template("my_log.html", numbers=numbers, history=history, total_time=total_time)

@app.route("/my_class")
@login_required
def my_class():
    rows = db.execute("SELECT clas FROM users WHERE id = :user_id", user_id=session["user_id"])
    # class seems to be a function so spelling wierd
    claz = rows[0]['clas']
    history = db.execute("SELECT SUM(time) AS time, username, clas FROM log JOIN users ON log.user_id = users.id  GROUP BY username")
    # initiate counters for totals
    total_time = 0
    count = 0
    numbers = []
    for i in range(len(history)):
        if history[i]['clas'] == claz:
            numbers.append(i)
            total_time = total_time + int(history[i]['time'])
            count += 1
    if count != 0:
        avg_time = total_time / count
    else:
        avg_time = 0
    return render_template("my_class.html", numbers=numbers, history=history, avg_time=avg_time)


@app.route("/recent")
@login_required
def recent():
    history = db.execute("SELECT time, type, date_created, username FROM log JOIN users ON log.user_id = users.id ORDER BY date_created DESC")
    numbers = []
    for i in range(len(history)):
        numbers.append(i)
    return render_template("recent.html", numbers=numbers, history=history)

@app.route("/rank")
@login_required
def rank():
    history = db.execute("SELECT SUM(time) AS time, username FROM log JOIN users ON log.user_id = users.id GROUP BY username ORDER BY time DESC")
    numbers = []
    for i in range(len(history)):
        numbers.append(i)
    return render_template("rank.html", numbers=numbers, history=history)

@app.route("/")
@login_required
def home():

    # not using for loop like all previuous as I think easier to do maually as sums etc in python code
    clas20 = db.execute("SELECT SUM(time) AS time, clas FROM log JOIN users ON log.user_id = users.id WHERE clas='2020'")
    time20 = clas20[0]['time']
    clas21 = db.execute("SELECT SUM(time) AS time, clas FROM log JOIN users ON log.user_id = users.id WHERE clas='2021'")
    time21 = clas21[0]['time']
    clas22 = db.execute("SELECT SUM(time) AS time, clas FROM log JOIN users ON log.user_id = users.id WHERE clas='2022'")
    time22 = clas22[0]['time']
    clas23 = db.execute("SELECT SUM(time) AS time, clas FROM log JOIN users ON log.user_id = users.id WHERE clas='2023'")
    time23 = clas23[0]['time']

    # count memebers in each class
    fog20 = db.execute("SELECT clas, username FROM users WHERE clas='2020' GROUP BY username")
    count20 = 0
    for i in range(len(fog20)):
        count20 += 1
    fog21 = db.execute("SELECT clas, username FROM users WHERE clas='2021' GROUP BY username")
    count21 = 0
    for i in range(len(fog21)):
        count21 += 1
    fog22 = db.execute("SELECT clas, username FROM users WHERE clas='2022' GROUP BY username")
    count22 = 0
    for i in range(len(fog22)):
        count22 += 1
    fog23 = db.execute("SELECT clas, username FROM users WHERE clas='2023' GROUP BY username")
    count23 = 0
    for i in range(len(fog23)):
        count23 += 1

    # some maths for minutes per person statistic
    if time20 == None:
        time20 = 0

    if count20 == 0:
        mpp20 = 0
    else:
        mpp20 = time20 / count20

    if time21 == None:
        time21 = 0

    if count21 == 0:
        mpp21 = 0
    else:
        mpp21 = time21 / count21

    if time22 == None:
        time22 = 0

    if count22 == 0:
        mpp22 = 0
    else:
        mpp22 = time22 / count22

    if time23 == None:
        time23 = 0

    if count23 == 0:
        mpp23 = 0
    else:
        mpp23 = time23 / count23

    return render_template("home.html", time20=time20, time21=time21, time22=time22, time23=time23, count20=count20, count21=count21, count22=count22, count23=count23, mpp20=mpp20, mpp21=mpp21, mpp22= mpp22, mpp23=mpp23)

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
