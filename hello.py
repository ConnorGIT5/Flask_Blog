from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime #when addiing stuff to database, this keeps track of the time



# Create an instance of Flask that runs all the things
app = Flask(__name__) #helps flask find all the files in the directory
# adding our database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# the secret key
app.config['SECRET_KEY'] = "secret key "
# initializing the database
db = SQLAlchemy(app)

# Creating the database Model
class Users(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(200), nullable=False, unique=True)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)

	# create a String to designate what the model is
	def __repr__(self):
		return '<Name %r>' % self.name

with app.app_context():
	db.create_all()


# Creating the user form class 
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
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
			user = Users(name=form.name.data, email=form.email.data) # the form data because the data for 'user'
			db.session.add(user) # adds the user to the database
			db.session.commit() # this is how you commit the addition
		name = form.name.data
		form.name.data = ''    # clearing out the data field
		form.email.data = ''   # clearing out the data field
		flash("User successfully added.")

	# adding stuff to the database
	our_users = Users.query.order_by(Users.date_added) # users = the table | query = search | order_by = show data in a specific order
	return render_template("add_user.html",
	 form=form,
	 name=name,
	 our_users=our_users)


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
	flash("Welcome to Version 0.08 of my Blog!")
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

# Creating the name page

@app.route('/name', methods=['GET', 'POST'])
def name():
	name = None
	form = NamerForm()

	# validate data in the form
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Form Submitted Successfully!")

	return render_template("name.html", name = name, form = form)

