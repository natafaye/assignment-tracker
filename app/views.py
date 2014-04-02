from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
	return render_template("home.html", title = "Home")
	
@app.route('/student-signup')
def studentsignup():
	return render_template("home.html", title = "Sign Up")
	
@app.route('/submissions')
def submissions():
	return render_template("home.html", title = "Submissions")
	
@app.route('/past-assignments')
def past_assignments():
	return render_template("home.html", title = "Past Assignments")

@app.route('/current-assignments')
def current_assignment():
	return render_template("home.html", title = "Current Assignments")
	
