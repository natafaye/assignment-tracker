from app import db
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine('sqlite://', echo=True)
Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)

ROLE_STUDENT = 0
ROLE_INSTRUCTOR = 1

class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	nickname = db.Column(db.String(64), unique = True)
	email = db.Column(db.String(120), unique = True)
	role = db.Column(db.SmallInteger, default = ROLE_STUDENT)
	course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
	course = db.relationship('Course', backref = 'students', foreign_keys=[course_id])
	submissions = db.relationship('Submission', backref = 'user')
	
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
	title = db.Column(db.String(64), index = True, unique = True)
	code = db.Column(db.String(64), index = True, unique = True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	instructor = db.relationship('User', backref = 'courses', foreign_keys=[user_id])
	assignments = db.relationship('Assignment', backref = 'course')

	def __repr__(self):
		return '<Course %r>' % (self.title)

class Assignment(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	title = db.Column(db.String(64), index = True, unique = True)
	description = db.Column(db.String(500))
	due_date = db.Column(db.DateTime)
	course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
	submissions = db.relationship('Submission', backref='assignment', lazy='dynamic')

	def __repr__(self):
		return '<Assignment %r>' % (self.title)
		
class Submission(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	time = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
	content = db.Column(db.String(2500))
	
	def __repr__(self):
		return '<Submission %r>' % (self.time)
		
Base.metadata.create_all()