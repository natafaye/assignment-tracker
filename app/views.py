from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask import jsonify
from app import app, db, lm, oid
from forms import LoginForm
from models import User, Assignment, Submission, ROLE_STUDENT, ROLE_INSTRUCTOR, Course
import string, random, datetime

# Make one date format to be consistent throughout the pages
dateFMT = "%a. %B %d, %Y"

############### Home and Unauthenticated Pages ##############

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
	if not g.user.is_authenticated():
		return home_not_logged_in()
	elif g.user.role == ROLE_INSTRUCTOR:
		return current_assignments()
	else: # g.user.role == ROLE_STUDENT
		return home_student()

@app.route('/home-not-logged-in')
def home_not_logged_in():
	return render_template("home-not-logged-in.html", title = "Sign Up")
	
@app.route('/student-signup')
def student_signup():
	return render_template("student-signup.html", title = "Sign Up")
	
@app.route('/instructor-signup')
def instructor_signup():
	return render_template("instructor-signup.html", title = "Instructor Signup")


##################### Instructor Pages ######################

@app.route('/current-assignments')
@login_required
def current_assignments():
	# Redirect student to student homepage
	if not g.user.role == ROLE_INSTRUCTOR:
		return redirect(url_for('index'))
		
	assignments = get_assignments_for_instructor()
	# Sort assignments by due date
	assignments.sort(key=lambda assignment:assignment["dueDate"]);
	
	return render_template("current-assignments.html", title = "Current Assignments", user=g.user,assignments=assignments,dateFMT=dateFMT)
	
@app.route('/past-assignments')
@login_required
def past_assignments():
	# Redirect student to student homepage
	if not g.user.role == ROLE_INSTRUCTOR:
		return redirect(url_for('index'))
		
	assignments = get_assignments_for_instructor()
	# Sort assignments by due date
	assignments.sort(key=lambda assignment:assignment["dueDate"]);
	
	return render_template("past-assignments.html", title = "Past Assignments", user=g.user, assignments=assignments,dateFMT=dateFMT)
	
@app.route('/classes')
@login_required
def classes():
	# Redirect student to student homepage
	if not g.user.role == ROLE_INSTRUCTOR:
		return redirect(url_for('index'))
		
	courses = get_courses_for_instructor()
	
	return render_template("classes.html", title = "Classes", user=g.user, courseList=courses)
	
@app.route('/submissions/<assignment_id>')
@login_required
def submissions(assignment_id):
	# Redirect student to student homepage
	if not g.user.role == ROLE_INSTRUCTOR:
		return redirect(url_for('index'))
	
	assignment = get_assignment(assignment_id)
	print(assignment)
	# Sort students by last name
	assignment["students"].sort(key=lambda student:student["lastname"]);
	
	return render_template("submissions.html", title = assignment["name"], user=g.user, assignment=assignment)

@app.route('/create-assignment')
@login_required
def create_assignment():
	# Redirect student to student homepage
	if not g.user.role == ROLE_INSTRUCTOR:
		return redirect(url_for('index'))
		
	courses = get_courses_for_instructor()
	
	return render_template("create-assignment.html", title = "Create Assignment", user=g.user, courseList=courses)

@app.route('/create-class')
@login_required
def create_class():
	# Redirect student to student homepage
	if not g.user.role == ROLE_INSTRUCTOR:
		return redirect(url_for('index'))
	
	return render_template("create-class.html", title = "Create Class", user=g.user)

############## Front-end Database requests ##################
@app.route('/create-class-post', methods = ['POST'])
@login_required
def add_class_to_db():
	# Set up course code generator & retrieve form data
	course_code = generate_course_code()
	course_name = request.form['name']
	
	# Add to database
	add_course_for_instructor(course_name,course_code)
	
	# Send response
	return jsonify({
		'name':course_name,
		'code':course_code })

@app.route('/create-assignment-post', methods = ['POST'])
@login_required
def add_assignment_to_db():
	# Retrieve form data
	course_code = request.form['class_code']
	assign_name = request.form['name']
	instructions = request.form['instr']
	datestr = request.form['dueDate']
	
	# Format Date
	dueDate = datetime.datetime.strptime(datestr, "%Y-%m-%d")
	returnDate = dueDate.strftime(dateFMT)

	# Add to database
	add_assignment_for_course(assign_name,course_code,instructions,dueDate)
	
	# Send response
	return jsonify({
		'course':course_code,
		'name':assign_name,
		'instr':instructions,
		'due': returnDate})


####################### Student Pages #######################

@app.route('/home-student')
@login_required
def home_student():
	if not g.user.role == ROLE_STUDENT:
		return redirect(url_for('index'))
		
	course = get_course_for_student()
	
	return render_template("home-student.html", title = course["name"], user=g.user, course=course,dateFMT=dateFMT)

@app.route('/submit-assignment/<assignment_id>')
@login_required
def submit_assignment(assignment_id):
	if not g.user.role == ROLE_STUDENT:
		return redirect(url_for('index'))
		
	assignment = {
		"name":"Journal Entry Week 4",
		"description": "Write down your thoughts and feelings about the Little Red Riding Hood. Also, explain why it was unwise for Red to wander alone in the forest.",
		"dueDate":"2014-04-25"
	}
	
	return render_template("submit-assignment.html", title = assignment["name"], user=g.user, assignment=assignment)


######################## Login ########################

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

################## Database Functions #################
		
def add_course_for_instructor(name,course_code):
	# Create the new course
	newCourse = Course(title=name,code=course_code)
	db.session.add(newCourse)
	db.session.commit()
	
	# Add the course the instructor's list of courses
	g.user.courses.append(newCourse)
	db.session.commit()
	return

def delete_course(course_code):
	delCourse = Course.query.filter_by(code=course_code).first()
	db.session.delete(delCourse)
	db.session.commit()
	return

def add_assignment_for_course(name,course_code,descr,dueDate):
	theCourse = Course.query.filter_by(code=course_code).first()
	newAssignment = Assignment(title=name,description=descr,due_date=dueDate,course=theCourse)
	db.session.add(newAssignment)
	db.session.commit()
	return
	
def get_courses_for_instructor():
	# Check permissions
	if not g.user.is_authenticated():
		return courses
		
	courses = []
	for c in g.user.courses:
		courses.append({
				"name":c.title,
				"code":c.code,
				"numStudents":len(c.students)
			})
			
	return courses
	
def get_course_for_student():
	# Check permissions
	if g.user.course is None:
		return {"name":"None", "assignments": []}
		
	course = {
		"name": g.user.course.title,
		"assignments": []
	}
	for a in g.user.course.assignments:
		course['assignments'].append({
			"name": a.title,
			"dueDate": a.due_date,
			"submitted": get_date_submitted(a, g.user)
		})
		
	return course
		
def get_assignments_for_instructor():
	# Check permissions
	if not g.user.is_authenticated():
		return []
		
	assignments = []
	for c in g.user.courses:
		for a in c.assignments:
			assignments.append({
				'name':a.title,
				'dueDate':a.due_date,
				'class':c.title,
				'percentSubmitted': get_percentage(a)
			})
	
	return assignments
	
def get_assignments_for_student():
	# Check permissions
	if not g.user.is_authenticated() or g.user.course is None:
		return []
		
	assignments = []
	for a in g.user.course.assignments:
		assignments.append({
				'name':a.title,
				'description':a.description,
				'dueDate':a.due_date
		})
		
	return assignments
	
def get_assignment(assignment_id):
	a = Assignment.query.get(assignment_id)
	
	# Check permissions
	if a is None or (a.course.instructor != g.user and not g.user in a.course.students):
		return {"name":"", "description":"", "dueDate":""}
		
	assignment = {
		"name": a.title,
		"description": a.description,
		"dueDate": a.due_date,
		"students": [],
		"percent": get_percentage(a)
	}
	for s in a.course.students:
		assignment['students'].append({
			"firstname": s.nickname,
			"lastname" : s.nickname,
			"id": s.id,
			"date": get_date_submitted(a, s)
		})
	
	print(assignment)
	return assignment
	
################## Utility Functions ##################

def get_date_submitted(a, u):
	# Get the date submitted for a particular assignment and user
	s = a.submissions.filter(Submission.user == u).first()
	if s is not None:
		return str(s.time)
	else:
		return ""
		
def get_percentage(a):
	return safe_division(a.submissions.count(), len(a.course.students)) * 100

def safe_division(dividend, divisor):
	if divisor == 0:
		return 0
	return dividend / divisor

def generate_course_code():
	size = 7
	chars = string.ascii_uppercase + string.digits
	newCode = ''.join(random.choice(chars) for _ in range(size))
	
	# Require all IDs to have at least one digit
	while(any(char.isdigit() for char in newCode) != True):
		newCode = ''.join(random.choice(chars) for _ in range(size))

	return newCode
