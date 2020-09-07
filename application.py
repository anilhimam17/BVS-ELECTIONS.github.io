# All the dependencies required
from flask import Flask, render_template, request, redirect, send_file, session
from flask_session import Session
from helpers import login_required
from cs50 import SQL
import os

# Instantiating flask to run from this script
app = Flask(__name__)

# To disable permanent sessions
app.config["SESSIONS_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Security Key
secKey = "BVS2020"

# Acquiring the database
db = SQL("sqlite:///Elections.db")

# Positions the students are standing for
pos = ["HEAD BOY", "HEAD GIRL", "SPORTS CAPTIAN", "ASST. HEAD BOY", "ASST. HEAD GIRL", "SEASURFERS HOUSE CAPTAIN",
	   "STORMCHASERS HOUSE CAPTAIN", "TRAILBLAZERS HOUSE CAPTAIN", "TERRAFORMERS HOUSE CAPTAIN", "CULTURAL SECRETARY",
       "CREATIVE HEAD", "TECHNOLOGY HEAD", "COMMUNICATIONS HEAD", "COMMUNITY AFFAIRS HEAD"]

# Total no of candidates
nC = len(db.execute("select * from nominees"))

# ------------------------------------------------------------------------------------------------------------

# Home Route
@app.route("/")
def index():
	return render_template("index.html")

# ------------------------------------------------------------------------------------------------------------

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():

	# Incase of get request
	if request.method == "GET":
		return render_template("login.html")

	# Incase of post request
	else:
		# Forget any user_id
		session.clear()

		# Acaquiring the values that were entered by the user
		usrName = request.form.get("username")
		usrPasswd = request.form.get("passwd")

		if not usrName or not usrPasswd:
			return render_template("apology.html", message = "Username or Password was left blank")

		res = db.execute("select * from users where name == ? and password == ?", usrName, usrPasswd)
		if len(res) != 1:
			return render_template("apology.html", message = "Entered Username or Password was incorrect")

		# Remember which user has logged in
		session["user_id"] = res[0]["id"]

		return redirect("/admin")

# ------------------------------------------------------------------------------------------------------------

# Register Route
@app.route("/register", methods=["GET", "POST"])
def register():

	if request.method == "GET":
		return render_template("register.html")

	else:
		usrName = request.form.get("username")
		usrPasswd = request.form.get("passwd")
		usrConf = request.form.get("passwdConf")
		usrSecKey = request.form.get("secKey")

		res = db.execute("select * from users where name == ?", usrName)

		if not usrName or not usrPasswd or not usrConf or not usrSecKey:
			return render_template("apology.html", message = "Some of the credentials were left blank")

		elif usrPasswd != usrConf:
			return render_template("apology.html", message = "The passwords entered do not match")

		elif usrSecKey != secKey:
			return render_template("apology.html", message = "The security key dosent match")

		elif len(res) != 0:
			return render_template("apology.html", message = "The username was already taken")

		# Entering the user into the database
		db.execute("insert into users (name, password) values (?, ?)", usrName, usrPasswd)
		return redirect("/login")

# ------------------------------------------------------------------------------------------------------------

# List to keep track of the users that are changing their passwords
users = []

# Forgot Password Route
@app.route("/forgot", methods=["GET", "POST"])
def forgot():

	if request.method == "GET":
		return render_template("forgot.html")

	else:
		usrName = request.form.get("username")
		usrSecKey = request.form.get("secKey")

		res = db.execute("select * from users where name == ?", usrName)

		if not usrName or not usrSecKey:
			return render_template("apology.html", message = "Some of the credentials were left blank")

		elif usrSecKey != secKey:
			return render_template("apology.html", message = "The security key dosent match")

		elif len(res) != 1:
			return render_template("apology.html", message = "The username entered was incorrect")

		users.append(usrName)
		return render_template("newPassword.html")


# New password Route
@app.route("/newPasswd", methods=["GET", "POST"])
def newPasswd():

	if request.method == "GET":
		return render_template("newPassword.html")

	else:
		usrPasswd = request.form.get("passwd")
		usrConf = request.form.get("passwdConf")

		if not usrPasswd or not usrConf:
			return render_template("apology.html", message = "Some of the credentials were left blank")

		elif usrPasswd != usrConf:
			return render_template("apology.html", message = "The passwords entered do not match")

		# Updating the password
		db.execute("update users set password = ? where name == ?", usrPasswd, users[-1])
		return redirect("/login")

# ------------------------------------------------------------------------------------------------------------

# Admin Route
@app.route("/admin")
@login_required
def admin():

	# Displaying in the order of the office
	chOrder = []

	# Extracting all the nominees
	for i in pos:
		nominees = db.execute("select * from nominees where position == ?", i)

		# Appending all the values
		for j in nominees:
			chOrder.append(j)

	# The total no of candidates
	nC = len(db.execute("select * from nominees"))

	return render_template("admin.html", nominees = chOrder, nC = nC)

# ------------------------------------------------------------------------------------------------------------

# Setup Route
@app.route("/setup", methods=["GET", "POST"])
@login_required
def setup():

	if request.method == "GET":
		return render_template("setup.html", pos = pos)

	else:
		cPos = request.form.get("cPos")
		cName = request.form.get("cName")

		if not cName:
			return render_template("apology.html", message="Name was left blank")

		elif "Select" in cPos:
			return render_template("apology.html", message="Position was not selected")

		res = db.execute("select * from nominees where name == ?", cName)
		if len(res) != 0:
			return render_template("apology.html", message="Candidate cannot nominate himself for more than one position")

		# Entering the candidate into the database
		db.execute("insert into nominees (name, position, votes) values (?, ?, ?)", cName, cPos, 0)
		return redirect("/setup")

# ------------------------------------------------------------------------------------------------------------

@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():

	if request.method == "GET":
		return render_template("remove.html", pos = pos)

	else:
		cPos = request.form.get("cPos")
		cName = request.form.get("cName")

		if "Select" in cPos:
			return render_template("apology.html", message="Postion was not selected")

		elif not cName:
			return render_template("apology.html", message="Candidate name was left blank")

		# Extracting the ID for reordering the table
		cId = db.execute("select id from nominees where name == ? and position == ?", cName, cPos)

		if not cId:
			return render_template("apology.html", message="The candidate with the given credentials was not found")

		cId = cId[0]["id"]

		# Deleting the candidate
		db.execute("delete from nominees where name == ? and position == ?", cName, cPos)

		# Total no of candidates
		nC = len(db.execute("select * from nominees"))

		# Updating the ids of the records
		for i in range(cId, nC + 1):
			db.execute("update nominees set id = ? where id == ?", i, i + 1)

		return redirect("/remove")

# ------------------------------------------------------------------------------------------------------------

# Logout Route
@app.route("/logout")
def logout():

	# Clearing out the user
	session.clear()

	# Redirecting to the home page
	return redirect("/")

# ------------------------------------------------------------------------------------------------------------

# Student Route
@app.route("/vote", methods=["GET", "POST"])
def vote():

	# Extracting all the candidates for the elections based on their posts
	lhb = db.execute("select name from nominees where position == ?", pos[0])
	lhg = db.execute("select name from nominees where position == ?", pos[1])
	ls = db.execute("select name from nominees where position == ?", pos[2])
	lahb = db.execute("select name from nominees where position == ?", pos[3])
	lahg = db.execute("select name from nominees where position == ?", pos[4])
	lss = db.execute("select name from nominees where position == ?", pos[5])
	lsc = db.execute("select name from nominees where position == ?", pos[6])
	ltb = db.execute("select name from nominees where position == ?", pos[7])
	ltf = db.execute("select name from nominees where position == ?", pos[8])
	lcs = db.execute("select name from nominees where position == ?", pos[9])
	lch = db.execute("select name from nominees where position == ?", pos[10])
	lth = db.execute("select name from nominees where position == ?", pos[11])
	lcom = db.execute("select name from nominees where position == ?", pos[12])
	lcomaf = db.execute("select name from nominees where position == ?", pos[13])

	if request.method == "GET":
		return render_template("vote.html", lhb = lhb, lhg = lhg, ls = ls, lahb = lahb, lahg = lahg, lss = lss,
		ltb = ltb, ltf = ltf, lsc = lsc, lcs = lcs, lch = lch, lth = lth, lcom = lcom, lcomaf = lcomaf)

	else:
		# Check all the values
		posKeys = ["lhb", "lhg", "ls", "lahb", "lahg", "lss", "lsc", "ltf", "ltb", "lcs", "lth", "lch",
		"lcom", "lcomaf"]

		for i in posKeys:
			# Values
			name = request.form.get(i)

			if "Select" == name.split(" ")[0]:
				return render_template("apology.html", message="The ballot was not filled completely")

		for i in posKeys:
			# Values
			name = request.form.get(i)

			if name == "NOTA":
				continue

			# Extracting the current no of votes
			cVotes = db.execute("select votes from nominees where name == ?", name)[0]["votes"]
			cVotes += 1

			# Updating the no of votes
			db.execute("update nominees set votes = ? where name == ?", cVotes, name)

		else:
			return redirect("/vote")

# ------------------------------------------------------------------------------------------------------------

# Results Route
@app.route("/results")
@login_required
def results():
    # List of all the winners with accordance to the positions
    winners = []

    for i in pos:
        votes = db.execute("select max(votes) as votes from nominees where position == ?", i)[0]["votes"]
        name = db.execute("select name from nominees where votes == ? and position == ?", votes, i)

        if len(name) != 1:
            ls = [i["name"] for i in name]
            winners.append({"name": ls, "position": i, "votes": votes, "len": len(name)})

        else:
            winners.append({"name": name[0]["name"], "position": i, "votes": votes, "len": len(name)})

    return render_template("results.html", winners = winners)

# ------------------------------------------------------------------------------------------------------------

# Reset Elections
@app.route("/reset")
@login_required
def reset():

	# Deleting all the records
	db.execute("delete from nominees")

	return redirect("/admin")

# ------------------------------------------------------------------------------------------------------------

# ResetVotes Route
@app.route("/resetVotes")
def resetVotes():

	# Quesry to reset all the votes
	db.execute("update nominees set votes == ?", 0)

	return redirect("/admin")

# ------------------------------------------------------------------------------------------------------------

# Download Route
@app.route("/download")
@login_required
def download():

	# List of all the winners with accordance to the positions
    winners = []

    for i in pos:
        votes = db.execute("select max(votes) as votes from nominees where position == ?", i)[0]["votes"]
        name = db.execute("select name from nominees where votes == ? and position == ?", votes, i)

        if len(name) != 1:
            ls = [i["name"] for i in name]
            winners.append({"name": ls, "position": i, "votes": votes, "len": len(name)})

        else:
            winners.append({"name": name[0]["name"], "position": i, "votes": votes, "len": len(name)})

    # Removing File if already exists
    if os.path.exists("ELECTION RESULTS.csv"):
    	os.remove("ELECTION RESULTS.csv")

    # Creating the file if it dosent exist
    myfile = open("ELECTION RESULTS.csv", "a")

    # Enter the data into the file
    myfile.write("POSITION, STATUS, NAME, VOTES\n")
    for i in winners:

    	# Incases of ties
    	if i["len"] == 1:
    		myfile.write(f"{i['position']}, Winner, {i['name']}, {i['votes']}\n")

    	else:
    		for j in i["name"]:
    			myfile.write(f"{i['position']}, Tied, {j}, {i['votes']}\n")

    # Closing the file to avoid buffer storage
    myfile.close()

    return send_file("ELECTION RESULTS.csv", as_attachment=True)

# ------------------------------------------------------------------------------------------------------------

# Running the webapplication from the current script
if __name__ == "__main__":
	app.run()

else:
	quit()

# ------------------------------------------------------------------------------------------------------------
