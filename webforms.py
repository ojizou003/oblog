from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, FileField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField


class LoginForm(FlaskForm):
    username = StringField("Username : ", validators=[DataRequired()])
    password = PasswordField("Password : ", validators=[DataRequired()])
    submit = SubmitField("Login")

class NameForm(FlaskForm):
    name = StringField("Enter Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    # content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Content', validators=[DataRequired()])
    # author = StringField("Author")
    slug = StringField('Slug', validators=[DataRequired()])
    submit = SubmitField('Post')

class SearchForm(FlaskForm):
    searched = StringField("Searchd : ", validators=[DataRequired()])
    submit = SubmitField("Search")

class UserForm(FlaskForm):
    name = StringField("Name : ", validators=[DataRequired()])
    username = StringField("Username : ", validators=[DataRequired()])
    email = StringField("Email : ", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color : ")
    about_author = TextAreaField("About Author : ")
    password_hash = PasswordField("password : ", validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField('Confirm Password : ', validators=[DataRequired()])
    profile_pic = FileField("Profile pic : ")
    submit = SubmitField("Submit")
    update = SubmitField("Update")
    register = SubmitField("Register")


