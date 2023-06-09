from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea 
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField



# search form
class SearchForm(FlaskForm):
	searched = StringField("searched", validators=[DataRequired()])
	submit = SubmitField('Submit')



# creates the 'login' form
class LoginForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired()])
	password = PasswordField("Password", validators=[DataRequired()])
	submit = SubmitField('Submit') 

	# creates the post form
class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()]) 
	# content = StringField("Content", validators=[DataRequired()], widget=TextArea())
	content = CKEditorField('Content', validators=[DataRequired()])
	author = StringField("Author")
	slug = StringField("Slug", validators=[DataRequired()])
	submit = SubmitField("Submit")

# Creating the user form class 
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	username = StringField("Username", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	favorite_color = StringField("Favorite Color")
	about_author = TextAreaField("About The Author")
	password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash2', message="Passwords must match.")])
	password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
	profile_pic = FileField("Profile Pic")
	submit = SubmitField("Submit")

# password form
class PasswordForm(FlaskForm):
	email = StringField("Enter email.", validators=[DataRequired()])
	password_hash = PasswordField("Enter password.", validators=[DataRequired()])
	submit = SubmitField("Submit")


# Creating a form class 
class NamerForm(FlaskForm):
	name = StringField("What's your Name?", validators=[DataRequired()])
	submit = SubmitField("Submit")

