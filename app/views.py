from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm
from models import User, ROLE_STUDENT, ROLE_INSTRUCTOR

############## Login ##############

@app.before_request
def before_request():
    g.user = current_user

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))
	
@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
	if g.user is not None and g.user.is_authenticated():
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		session['remember_me'] = form.remember_me.data
		return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
	return render_template('login.html',
		title = 'Sign In',
		form = form,
		providers = app.config['OPENID_PROVIDERS'])
		
@oid.after_login
def after_login(resp):
	if resp.email is None or resp.email == "":
		flash('Invalid login. Please try again.')
		return redirect(url_for('login'))
	user = User.query.filter_by(email = resp.email).first()
	if user is None:
		nickname = resp.nickname
		if nickname is None or nickname == "":
			nickname = resp.email.split('@')[0]
		user = User(nickname = nickname, email = resp.email, role = ROLE_STUDENT)
		db.session.add(user)
		db.session.commit()
	remember_me = False
	if 'remember_me' in session:
		remember_me = session['remember_me']
		session.pop('remember_me', None)
	login_user(user, remember = remember_me)
	return redirect(request.args.get('next') or url_for('index'))
	
@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))
	
############## Other Pages ##############

@app.route('/')
@app.route('/index')
@login_required
def index():
	return render_template("current-assignments.html", title = "Home")
	
@app.route('/classes')
@login_required
def classes():
	courses = [
		{
		"name":"English 101",
		"code":"123456",
		"numStudents":4
		},
		{
		"name":"Math 250",
		"code":"7891011",
		"numStudents":12
		}
	]
	return render_template("classes.html", title = "Classes", courseList=courses)

@app.route('/create-assignment')
@login_required
def create_assignment():
	courses = [
		{
		"name":"English 101",
		"code":"123456"
		},
		{
		"name":"Math 250",
		"code":"7891011"
		}
	]
	return render_template("create-assignment.html", title = "Create Assignment", courseList=courses)

@app.route('/create-class')
@login_required
def create_class():
	return render_template("create-class.html", title = "Create Class")

@app.route('/home')
@app.route('/current-assignments')
@login_required
def current_assignment():
	assignments = [
		{
		"name":"Journal Entry Week 4",
		"dueDate":"2014-04-20",
		"class":"English 101",
		"percentSubmitted":50
		},
		{
		"name":"Homework 10",
		"dueDate":"2014-04-20",
		"class":"Math 250",
		"percentSubmitted":100
		},
		{
		"name":"Homework 11",
		"dueDate":"2014-04-25",
		"class":"Math 250",
		"percentSubmitted":75
		},
		{
		"name":"Homework 12",
		"dueDate":"2014-04-30",
		"class":"Math 250",
		"percentSubmitted":0
		}
	]
	# Sort assignments by due date
	assignments.sort(key=lambda assignment:assignment["dueDate"]);
	return render_template("current-assignments.html", title = "Current Assignments", assignments=assignments)

@app.route('/home-not-logged-in')
def home_not_logged_in():
	return render_template("home-not-logged-in.html", title = "Sign Up")

@app.route('/home-student')
@login_required
def home_student():
	return render_template("home-student.html", title = "Home")


@app.route('/past-assignments')
@login_required
def past_assignments():
	assignments = [
		{
		"name":"Journal Entry Week 1",
		"dueDate":"2014-04-10",
		"class":"English 101",
		"percentSubmitted":100
		},
		{
		"name":"Homework 6",
		"dueDate":"2014-04-11",
		"class":"Math 250",
		"percentSubmitted":75
		},
		{
		"name":"Homework 7",
		"dueDate":"2014-04-12",
		"class":"Math 250",
		"percentSubmitted":100
		},
		{
		"name":"Homework 8",
		"dueDate":"2014-04-13",
		"class":"Math 250",
		"percentSubmitted":95
		},
		{
		"name":"Journal Entry Week 0",
		"dueDate":"2014-04-05",
		"class":"English 101",
		"percentSubmitted":0
		}
	]
	# Sort assignments by due date
	assignments.sort(key=lambda assignment:assignment["dueDate"]);
	return render_template("past-assignments.html", title = "Past Assignments",assignments=assignments)

@app.route('/student-signup')
def student_signup():
	return render_template("student-signup.html", title = "Sign Up")
	
@app.route('/submissions')
@login_required
def submissions():
	return render_template("submissions.html", title = "Submissions")

@app.route('/submit-assignment')
@login_required
def submit_assignment():
	return render_template("submit-assignment.html", title = "Submit Assignment")
