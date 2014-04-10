from app import db

ROLE_STUDENT = 0
ROLE_INSTRUCTOR = 1

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	nickname = db.Column(db.String(64), unique = True)
	email = db.Column(db.String(120), unique = True)
	role = db.Column(db.SmallInteger, default = ROLE_STUDENT)
	courses = db.relationship('Course', backref = 'instructor', lazy = 'dynamic')
	
	def is_authenticated(self):
		return True
		
	def is_active(self):
		return True
	
	def is_anonymous(self):
		return False
	
	def get_id(self):
		return unicode(self.id)
	
	def __repr__(self):
		return '<User %r>' % (self.nickname)

class Course(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	title = db.Column(db.String(64), index = True, unique = True)
	code = db.Column(db.String(64), index = True, unique = True)
	assignments = db.relationship('Assignment', backref = 'course', lazy = 'dynamic')

	def __repr__(self):
		return '<Course %r>' % (self.title)

class Assignment(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(64), index = True, unique = True)
	description = db.Column(db.String(500))
	due_date = db.Column(db.DateTime)
	course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

	def __repr__(self):
		return '<Assignment %r>' % (self.title)