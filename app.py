from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime, timezone, date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

from dotenv import load_dotenv
import os
import pytz

from webforms import LoginForm, UserForm, PostForm, PasswordForm, NameForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid

load_dotenv()

# 日本のタイムゾーンを定義
japan_tz = pytz.timezone('Asia/Tokyo')

# Create a Flask Instance
app = Flask(__name__)

# CKEditorのグローバル設定
ckeditor = CKEditor(app)
app.config['CKEDITOR_HEIGHT'] = 400
# 警告を無効化
app.config['CKEDITOR_ENABLE_CODESNIPPET'] = True
app.config['CKEDITOR_CODE_THEME'] = 'monokai_sublime'
app.config['CKEDITOR_EXTRA_PLUGINS'] = ['codesnippet']
app.config['CKEDITOR_DISABLE_SECURITY_WARNING'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

UPLOAD_FOLDER = 'static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# routing(関数のアルファベット順)
@app.route('/add-post', methods=['GET', 'POST'])
# @login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, 
                    content=form.content.data,
                    poster_id=poster, 
                    slug=form.slug.data
                )
        form.title.data = ''
        form.content.data = ''
        # form.author.data = ''
        form.slug.data = ''

        # Add post data to database
        db.session.add(post)
        db.session.commit()

        flash('Blog Post Submitted Successfully!')
    
    return render_template('add_post.html', form=form)

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data)
            user = Users(name=form.name.data, 
                        username=form.username.data, 
                        email=form.email.data, 
                        favorite_color=form.favorite_color.data, password_hash=hashed_pw
                        )
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''
        flash('User Added Successfully!')
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    id = current_user.id
    if id == 1:
        name = None
        form = UserForm()
        if form.validate_on_submit():
            user = Users.query.filter_by(email=form.email.data).first()
            if user is None:
                # Hash the password
                hashed_pw = generate_password_hash(form.password_hash.data)
                user = Users(name=form.name.data, 
                            username=form.username.data, 
                            email=form.email.data, 
                            favorite_color=form.favorite_color.data, password_hash=hashed_pw
                            )
                db.session.add(user)
                db.session.commit()
            name = form.name.data
            form.name.data = ''
            form.username.data = ''
            form.email.data = ''
            form.favorite_color.data = ''
            form.password_hash.data = ''
            flash('User Added Successfully!')
        our_users = Users.query.order_by(Users.date_added)
        return render_template('admin.html', form=form, name=name, our_users=our_users)
    else:
        flash('Sorrt, You must be the Admin to access the Admin Page...')
        return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']
        name_to_update.profile_pic = request.files['profile_pic']

        # Grab Image Name
        pic_filename = secure_filename(name_to_update.profile_pic.filename)
        # Set UUID
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        # Save That Image
        saver = request.files['profile_pic']
        # Change it to a string to save to db
        name_to_update.profile_pic = pic_name
        try:
            db.session.commit()
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            flash('User Updated Successfully!')
            return render_template('dashboard.html', 
                                    form=form,
                                    name_to_update=name_to_update)
        except:
            flash('Error! Looks like there was a problem...try again!')
            return render_template('dashboard.html', 
                                    form=form,
                                    name_to_update=name_to_update)
    else:
        return render_template('dashboard.html', 
                                form=form,
                                name_to_update=name_to_update, 
                                id=id)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User Deleted Successfully!')
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, name=name, our_users=our_users)
    except:
        flash('Whoops! There was a problem deleting user, try again...')
        return render_template('add_user.html', form=form, name=name, our_users=our_users)

@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash('Post was Deleted!')
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
        except:
            flash('There was a problem deleting post, Try again...')
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
    else:
        flash("You Aren't Authorized To Delete this Post!")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)

@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash('Post Has Been Updated!')
        return redirect(url_for('post', id=post.id))
    
    if current_user.id == post.poster_id:
        form.title.data = post.title
        # form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You Arn't Authorized To Edit This Post!")
        post = Posts.query.get_or_404(id)
        return render_template('post.html', post=post)


# Json Thing
@app.route('/date')
def get_current_date():
    favorite_pizza = {
        "John": 'Pepperoni', 
        "Mary": 'Cheese',
        "Tim": 'Mushroom'
    }
    return favorite_pizza
    # return {"Date": date.today()}

@app.route('/')
def index():
    first_name = 'Jhon'
    stuff = 'This is bold Text'
    favorite_pizza = ['Pepperoni', 'Cheese', 'Mushrooms', 41]
    return render_template('index.html', 
                            first_name=first_name,
                            stuff = stuff,
                            favorite_pizza = favorite_pizza
                            )

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Login Successfully!')
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong Password - Try Again!')
        else:
            flash("That User Dosen't Exist! Try Again...")
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You Have Been Logged Out! Thanks For Stopping By...')
    return redirect(url_for('login'))

@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash('Successfully!')

    return render_template('name.html',
                            name=name, 
                            form=form
                            )

@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route('/posts')
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)

@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        # Get data from submitted form
        post.searched = form.searched.data
        # Query the Database
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template('search.html', 
                                form=form, 
                                searched=post.searched,
                                posts = posts
                                )

# テスト用
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data = ''
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template('test_pw.html',
                            email=email, 
                            password=password,
                            pw_to_check=pw_to_check,
                            passed=passed,
                            form=form
                            )

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash('User Updated Successfully!')
            return render_template('update.html', 
                                    form=form,
                                    name_to_update=name_to_update)
        except:
            flash('Error! Looks like there was a problem...try again!')
            return render_template('update.html', 
                                    form=form,
                                    name_to_update=name_to_update)
    else:
        return render_template('update.html', 
                                form=form,
                                name_to_update=name_to_update, 
                                id=id)

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)

# その他の関数
# Pass Stuff To Navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# Error Handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

# 日付フォーマット
@app.template_filter('format_date')
def format_date(value, format='%Y/%m/%d'):
    if value is None:
        return ""
    return value.strftime(format)

@app.template_filter('format_date_second')
def format_date_second(value, format='%Y/%m/%d %H:%M:%S'):
    if value is None:
        return ""
    return value.strftime(format)

# db.Model
# Create a Blog Post Model
class Posts(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    # author = db.Column(db.String(255)) ...poster_idの導入により不要
    # date_posted = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    date_posted = db.Column(db.DateTime(timezone=True), default=lambda:datetime.now(japan_tz))
    slug = db.Column(db.String(255))
    # Foreign Key To Link Users (refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id')) #usersはDBのTable名

class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(500), nullable=True)
    # date_added = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    date_added = db.Column(db.DateTime(timezone=True), default=lambda:datetime.now(japan_tz))
    profile_pic = db.Column(db.String(255), nullable=True)

    # Do some password stuff!
    password_hash = db.Column(db.String(255))
    # User Can Have Many Posts
    posts = db.relationship(Posts, backref='poster')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create A String
    def __repr__(self):
        return '<Name %r>' % self.name

if __name__ == '__main__':
    app.run(debug=True)