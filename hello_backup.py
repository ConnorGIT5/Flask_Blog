from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date #when addiing stuff to database, this keeps track of the time
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea 
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

# Create an instance of Flask that runs all the things
app = Flask(__name__) #helps flask find all the files in the directory
# adding our database

# old sqllite db below
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#MySql db     ex: 'mysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:jc999wLd@localhost/our_users'

# the secret key
app.config['SECRET_KEY'] = "secret key "
# initializing the database
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# flask login 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))


# creates the 'login' form
class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField('Submit') 


# creates the 'login' page
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user: # if there is a user
			# checking the hash
			if check_password_hash(user.password_hash, form.password.data): # will return true if both statements match
				login_user(user)
				flash('Login successful.')
				return redirect(url_for('dashboard'))
			else:
				flash('Wrong password - try again!')
		else:
			flash("User doesn't exist.")

	return render_template('login.html', form=form)

# logging out
@app.route('/logout', methods=['GET', 'POST'])
@login_required # you can't log out unless you're already logged in
def logout():
	logout_user()
	flash("You've been logged out.")
	return redirect(url_for('login'))


# creates the login dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
	form = UserForm()
	id = current_user.id
	name_to_update = Users.query.get_or_404(id) # if int:id = 3, looks for it. If no 3, then 404 error
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.favorite_color = request.form['favorite_color']
		name_to_update.username = request.form['username']
		try:
			db.session.commit()
			flash("User updated successfully.")
			return render_template("dashboard.html",
				form=form,
				name_to_update = name_to_update)
		except:
			flash("Error: try again.")
			return render_template("dashboard.html",
				form=form,
				name_to_update = name_to_update)
	else:
		return render_template("dashboard.html",
				form=form,
				name_to_update = name_to_update,
				id = id)
	return render_template('dashboard.html')


# creates the blog post model
class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(200))
	content = db.Column(db.Text)
	author = db.Column(db.String(100))
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(200))

# creates the post form
class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()]) 
	content = StringField("Content", validators=[DataRequired()], widget=TextArea())
	author = StringField("Author", validators=[DataRequired()])
	slug = StringField("Slug", validators=[DataRequired()])
	submit = SubmitField("Submit")

# route to delete posts
@app.route('/posts/delete/<int:id>')
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)
	try:
		db.session.delete(post_to_delete)
		db.session.commit()
		flash("Blog post deleted successfully.")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template('posts.html', posts=posts)

	except:
		flash('There was a problem deleting the post. Try again.')
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template('posts.html', posts=posts)


# the blog post page
@app.route('/posts')
def posts():
	# selecting all the posts in the database
	posts = Posts.query.order_by(Posts.date_posted.desc())
	return render_template("posts.html", posts=posts)

@app.route('/posts/<int:id>')
def post(id):
	post = Posts.query.get_or_404(id)
	return render_template('post.html', post=post)

# edit a post
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data # form.title.data: what was already filled out. post.title = what will be new
		post.author = form.author.data
		post.slug = form.slug.data
		post.content = form.content.data
		# update database
		db.session.add(post)
		db.session.commit()
		# return a message fr successful change
		flash("Post has been updated.")
		return redirect(url_for('post', id=post.id))
	form.title.data = post.title
	form.author.data = post.author
	form.slug.data = post.slug
	form.content.data = post.content
	return render_template('edit_post.html', form=form)


# adding the post page
@app.route('/add-post', methods=['GET', 'POST'])
# @login_required
def add_post():
	form = PostForm()

	if form.validate_on_submit():
		post = Posts(title=form.title.data, content=form.content.data, 
			author=form.author.data, slug=form.slug.data)
		# clears form
		form.title.data = ''
		form.content.data = ''
		form.author.data = ''
		form.slug.data = ''
		# posts data to the database
		db.session.add(post)
		db.session.commit()
		flash('Blog post submitted successfully.')
		# redirects to the "add_post" web page
	return render_template("add_post.html", form=form)


# quick json
@app.route('/date')
def get_current_date():
	favorite_pizza = {
	'Connor': 'Pepperoni',
	'Tim': 'Supreme',
	'Claire': 'Pineapple'
	}
	return favorite_pizza
	# return {"Date": date.today()}



# Creating the database Model
class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(25), nullable=False, unique=True)
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
@login_required
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
	username = StringField("Username", validators=[DataRequired()])
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
		name_to_update.username = request.form['username']
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
			hashed_pw = generate_password_hash(form.password_hash.data, "sha256")		
			user = Users(username=form.username.data, name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw) # the form data because the data for 'user'
			db.session.add(user) # adds the user to the database
			db.session.commit() # this is how you commit the addition
		name = form.name.data
		form.name.data = ''    # clearing out the data field
		form.username.data = ''
		form.email.data = ''  
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
	flash("Welcome to Version 0.25.0 of my Blog!")
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

