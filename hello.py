from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# Create an instance of Flask that runs all the things
app = Flask(__name__) #helps flask find all the files in the directory
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"


# Creating a form class 
class NamerForm(FlaskForm):
	name = StringField("What's your Name?", validators=[DataRequired()])
	submit = SubmitField("Submit")




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

	return render_template("name.html", name = name, form = form)