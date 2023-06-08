from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime #when addiing stuff to database, this keeps track of the time
from werkzeug.security import generate_password_hash, check_password_hash


# Create an instance of Flask that runs all the things
app = Flask(__name__) #helps flask find all the files in the directory
# adding our database

# old sqllite db below
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#MySql db     ex: 'mysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_DATABASE_URI'] = '#'

# the secret key
app.config['SECRET_KEY'] = "#"
# initializing the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Creating the database Model
class Users(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(200), nullable=False, unique=True)
	favorite_color = db.Column(db.String(100))
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	# password hash column
	password_hash = db.Column(db.String(128))

	@property
	def password(self):
		raise AttributeError('Password is not a readable attribute.')		

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)



	# create a String to designate what the model is
	def __repr__(self):
		return '<Name %r>' % self.name

with app.app_context():
	db.create_all()


@app.route('/delete/<int:id>')
def delete(id):
	user_to_delete = Users.query.get_or_404(id)
	name = None
	form = UserForm()

	try:
		db.session.delete(user_to_delete)
		db.session.commit()
		flash("User deleted successfully.")

		our_users = Users.query.order_by(Users.date_added) # users = the table | query = search | order_by = show data in a specific order
		return render_template("add_user.html",
		form=form, name=name, our_users=our_users)

	except:
		flash("Unexpected error when trying to delete user.")
		return render_template("add_user.html",
		form=form, name=name, our_users=our_users)



# Creating the user form class 
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	favorite_color = StringField("Favorite Color")
	password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash2', message="Passwords must match.")])
	password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
	submit = SubmitField("Submit")


# for updating the database records
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id) # if int:id = 3, looks for it. If no 3, then 404 error
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.favorite_color = request.form['favorite_color']
		try:
			db.session.commit()
			flash("User updated successfully.")
			return render_template("update.html",
				form=form,
				name_to_update = name_to_update)
		except:
			flash("Error: try again.")
			return render_template("update.html",
				form=form,
				name_to_update = name_to_update)
	else:
		return render_template("update.html",
				form=form,
				name_to_update = name_to_update,
				id = id)

# password form

class PasswordForm(FlaskForm):
	email = StringField("Enter email.", validators=[DataRequired()])
	password_hash = PasswordField("Enter password.", validators=[DataRequired()])
	submit = SubmitField("Submit")


# Creating a form class 
class NamerForm(FlaskForm):
	name = StringField("What's your Name?", validators=[DataRequired()])
	submit = SubmitField("Submit")


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first() # queries the database looking for whatever email address is just types in. If it exists, it will return first. This checks for duplicates.
		if user is None: # if there isn't a duplicate email. i.e., if the email in the submit form is unique. 
			# password hashing
			hashed_pw = generate_password_hash(form.password_hash.data, "#")		
			user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw) # the form data because the data for 'user'
			db.session.add(user) # adds the user to the database
			db.session.commit() # this is how you commit the addition
		name = form.name.data
		form.name.data = ''    # clearing out the data field
		form.email.data = ''   # clearing out the data field
		form.favorite_color.data = ''
		form.password_hash = ''
		flash("User successfully added.")


	# adding stuff to the database
	our_users = Users.query.order_by(Users.date_added) # users = the table | query = search | order_by = show data in a specific order
	return render_template("add_user.html",
	 form=form, name=name, our_users=our_users)


# Crate a route decorator (ex: "about.html" is a route)
@app.route('/')

#def index():
#	return "<h1>Hello World!<h1>"

#!! jinja filters !! 
#safe : allows to html to render when it's in a variable
#capitalize
#lower
#upper
#title
#trim : removes trailing spaces from the end
#striptags: this strips out html tags, and html isn't run by the browser


def index():
	first_name = "Connor"
	stuff = "This is <strong>Bold</strong> Text"

	# website version message
	flash("Welcome to Version 0.15.0 of my Blog!")
	favorite_pizza = ["Pepperoni", "Cheese", "Mushrooms", 21]

	return render_template("index.html",
		first_name=first_name,
	 	stuff=stuff,
	 	favorite_pizza=favorite_pizza)

@app.route('/user/<name>') # localhost:5000/user/con

def user(name):
	return render_template("user.html", user_name=name)

# Creating Custom Error Pages

# Invalid URL. File not found
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

# internal server error
@app.errorhandler(500)    
def page_not_found(e):
	return render_template("500.html"), 500

# creating a password test page

@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
	email = None
	password = None
	pw_to_check = None
	passed = None
	form = PasswordForm()

	# validation form
	if form.validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		form.email.data = ''
		form.password_hash.data = ''
		#lookup user by email
		pw_to_check = Users.query.filter_by(email=email).first()
		# check hashed password
		passed = check_password_hash(pw_to_check.password_hash, password)

	return render_template("test_pw.html", email=email, password=password, 
		pw_to_check = pw_to_check, passed = passed,	form=form)

# Creating the name page

@app.route('/name', methods=['GET', 'POST'])
def name():
	name = None
	form = NamerForm()

	# validate data in the form
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Form submitted Successfully.")

	return render_template("name.html", name = name, form = form)

