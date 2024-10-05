from flask import Flask, render_template

# Create a Flask Instance
app = Flask(__name__)

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


if __name__ == '__main__':
    app.run(debug=True)