from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
	return render_template("home.html", title = "Home")
	
@app.route('/classes')
def classes():
	return render_template("classes.html", title = "Classes")

@app.route('/create-assignment')
def create_assignment():
	return render_template("create-assignment.html", title = "Create Assignment")

@app.route('/create-class')
def create_class():
	return render_template("create-class.html", title = "Create Class")
	
@app.route('/current-assignments')
def current_assignment():
	return render_template("current-assignments.html", title = "Current Assignments")

@app.route('/home-not-logged-in')
def home_not_logged_in():
	return render_template("home-not-logged-in.html", title = "Sign Up")

@app.route('/home-student')
def home_student():
	return render_template("home-student.html", title = "Home")

@app.route('/past-assignments')
def past_assignments():
	return render_template("past-assignments.html", title = "Past Assignments")

@app.route('/student-signup')
def student_signup():
	return render_template("student-signup.html", title = "Sign Up")
	
@app.route('/submissions')
def submissions():
	return render_template("submissions.html", title = "Submissions")

@app.route('/submit-assignment')
def submit_assignment():
	return render_template("submit-assignment.html", title = "Submit Assignment")
