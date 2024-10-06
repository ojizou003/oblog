from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from dotenv import load_dotenv
import os

load_dotenv()

# Create a Flask Instance
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Create a Form Class
class NameForm(FlaskForm):
    name = StringField("Enter Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a route decorator
@app.route('/')
def index():
    first_name = 'Jhon'
    stuff = 'This is bold Text'
    favarite_pizza = ['Pepperoni', 'Cheese', 'Mushrooms', 41]
    return render_template('index.html', 
                            first_name=first_name,
                            stuff = stuff,
                            favarite_pizza = favarite_pizza
                            )

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''

    return render_template('name.html',
                            name=name, 
                            form=form
                            )

if __name__ == '__main__':
    app.run(debug=True)