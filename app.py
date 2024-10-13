from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    login_required,
    logout_user,
    current_user,
)
from sqlalchemy.exc import IntegrityError

import os
import pytz
import re

from webforms import LoginForm, UserForm, PostForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
from config import Config


# 日本のタイムゾーンを定義
japan_tz = pytz.timezone("Asia/Tokyo")

# Create a Flask Instance
app = Flask(__name__)
app.config.from_object(Config)
app.config["SQLALCHEMY_DATABASE_URI"] = Config.get_database_url()
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_recycle": 280}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.debug = Config.DEBUG

db = SQLAlchemy(app)
migrate = Migrate(app, db)

ckeditor = CKEditor(app)
app.config['CKEDITOR_CONFIG'] = {
    'extraPlugins': 'image2',
    'image2_alignClasses': ['image-left', 'image-center', 'image-right'],
    'image2_disableResizer': True,
    'removePlugins': 'image',
    'image2_prefillDimensions': False,
    'image2_maxSize': {'width': 100, 'height': 100},
    'contentsCss': ['static/css/style.css'],
    'allowedContent': True  # この行を追加
}

app.config['WTF_CSRF_TIME_LIMIT'] = None  # トークンの有効期限を無制限にする

# Flask_Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# routing(関数のアルファベット順)
@app.route("/add-post", methods=["GET", "POST"])
# @login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(
            title=form.title.data,
            content=form.content.data,
            poster_id=poster,
            keyword=form.keyword.data,
        )
        form.title.data = ""
        form.content.data = ""
        # form.author.data = ''
        form.keyword.data = ""

        # Add post data to database
        db.session.add(post)
        db.session.commit()

        flash("記事が投稿されました!")
        return redirect(url_for('post', id=post.id))  # postページへ

    return render_template("add_post.html", form=form)


@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        existing_user = Users.query.filter(
            (Users.email == form.email.data) | (Users.username == form.username.data)
        ).first()
        
        if existing_user:
            if existing_user.email == form.email.data:
                flash("このメールアドレスは既に登録されています。")
            else:
                flash("このユーザー名は既に使用されています。別のユーザー名で登録してください。")
        else:
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data)
            user = Users(
                name=form.name.data,
                username=form.username.data,
                email=form.email.data,
                favorite_color=form.favorite_color.data,
                password_hash=hashed_pw,
            )
            db.session.add(user)
            db.session.commit()
            
            name = form.name.data
            form.name.data = ""
            form.username.data = ""
            form.email.data = ""
            form.favorite_color.data = ""
            form.password_hash.data = ""
            flash("ユーザー情報が登録されました!")

    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    id = current_user.id
    if id == 3:  # Assuming 3 is the admin user ID
        name = None
        form = UserForm()
        if form.validate_on_submit():
            existing_user = Users.query.filter(
                (Users.email == form.email.data) | (Users.username == form.username.data)
            ).first()
            
            if existing_user:
                if existing_user.email == form.email.data:
                    flash("このメールアドレスは既に登録されています。")
                else:
                    flash("このユーザー名は既に使用されています。別のユーザー名で登録してください。")
            else:
                try:
                    # Hash the password
                    hashed_pw = generate_password_hash(form.password_hash.data)
                    user = Users(
                        name=form.name.data,
                        username=form.username.data,
                        email=form.email.data,
                        favorite_color=form.favorite_color.data,
                        password_hash=hashed_pw,
                    )
                    db.session.add(user)
                    db.session.commit()
                    
                    name = form.name.data
                    form.name.data = ""
                    form.username.data = ""
                    form.email.data = ""
                    form.favorite_color.data = ""
                    form.password_hash.data = ""
                    flash("ユーザー情報が更新されました!")
                except IntegrityError:
                    db.session.rollback()
                    flash("エラー! データベースの制約違反が発生しました。もう一度お試しください。")
                except Exception as e:
                    db.session.rollback()
                    flash(f"エラー! 問題が発生しました...: {str(e)}")

        our_users = Users.query.order_by(Users.date_added)
        return render_template("admin.html", form=form, name=name, our_users=our_users)
    else:
        flash("申し訳ありません。 管理者用の画面なので表示できません...")
        return redirect(url_for("dashboard"))

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        # Check if username or email already exists (excluding the current user)
        existing_user = Users.query.filter(
            (Users.username == request.form["username"]) | 
            (Users.email == request.form["email"])
        ).filter(Users.id != id).first()

        if existing_user:
            if existing_user.username == request.form["username"]:
                flash("このユーザー名は既に使用されています。別のユーザー名で登録してください。")
            else:
                flash("このメールアドレスは既に登録されています。")
            return render_template(
                "dashboard.html", form=form, name_to_update=name_to_update
            )

        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.favorite_color = request.form["favorite_color"]
        name_to_update.username = request.form["username"]
        name_to_update.about_author = request.form["about_author"]

        # Check for profile pic
        if request.files["profile_pic"]:
            name_to_update.profile_pic = request.files["profile_pic"]
            # Grab Image Name
            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            # Set UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            # Save That Image
            saver = request.files["profile_pic"]
            # Change it to a string to save to db
            name_to_update.profile_pic = pic_name

        try:
            db.session.commit()
            if request.files["profile_pic"]:
                saver.save(os.path.join(app.config["UPLOAD_FOLDER"], pic_name))
            flash("ユーザー情報が更新されました!")
        except IntegrityError:
            db.session.rollback()
            flash("エラー! データベースの制約違反が発生しました。もう一度お試しください。")
        except Exception as e:
            db.session.rollback()
            flash(f"エラー! 問題が発生しました...: {str(e)}")

        return render_template(
            "dashboard.html", form=form, name_to_update=name_to_update
        )
    else:
        return render_template(
            "dashboard.html", form=form, name_to_update=name_to_update, id=id
        )

@app.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete(id):
    if id == current_user.id or current_user.id == 3:
        user_to_delete = Users.query.get_or_404(id)
        name = None
        form = UserForm()
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("ユーザーを削除しました!")
            our_users = Users.query.order_by(Users.date_added)
            return render_template(
                "add_user.html", form=form, name=name, our_users=our_users
            )
        except:
            flash("ユーザー削除処理中に問題発生! もう一度お試しください...")
            return render_template(
                "add_user.html", form=form, name=name, our_users=our_users
            )
    else:
        flash("あなたはこのユーザーを削除する権限がありません!")
        return redirect(url_for("dashboard"))

@app.route("/posts/delete/<int:id>")
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id or id == 3:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("記事は削除されました!")
            posts = Posts.query.order_by(Posts.date_posted)
            # return render_template("posts.html", posts=posts)
            return redirect(url_for('dashboard'))
        except:
            flash("ユーザー削除処理中に問題発生! もう一度お試しください...")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
    else:
        flash("あなたはこの記事を削除する権限がありません!")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)


@app.route("/posts/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.keyword = form.keyword.data
        post.content = form.content.data
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("記事は更新されました!")
        return redirect(url_for("post", id=post.id))

    if current_user.id == post.poster_id or current_user.id == 3:
        form.title.data = post.title
        # form.author.data = post.author
        form.keyword.data = post.keyword
        form.content.data = post.content
        return render_template("edit_post.html", form=form)
    else:
        flash("あなたはこの記事を編集する権限がありません!")
        post = Posts.query.get_or_404(id)
        return render_template("post.html", post=post)

@app.route("/")
def index():
    return redirect(url_for("login"))

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("ログインに成功しました!")
                return redirect(url_for("dashboard"))
            else:
                flash("パスワードが間違っています...")
        else:
            flash("ユーザーが登録されていません...")
    return render_template("login.html", form=form)

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("ログアウトしました... お立ち寄りいただきありがとうございました！")
    return redirect(url_for("login"))

@app.route("/posts/<int:id>")
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

@app.route("/posts")
def posts():
    posts = Posts.query.order_by(Posts.date_posted.desc()).all()
    return render_template("posts.html", posts=posts)

@app.route("/privacypolicy")
def privacypolicy():
    return render_template("privacypolicy.html")

@app.route("/search", methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        # Get data from submitted form
        post.searched = form.searched.data
        # Query the Database
        # posts = posts.filter(Posts.content.like("%" + post.searched + "%"))
        posts = posts.filter(
            db.or_(
                Posts.content.like("%" + post.searched + "%"),
                Posts.title.like("%" + post.searched + "%"),
                Posts.keyword.like("%" + post.searched + "%"),
                Posts.poster_id.in_(
                    db.session.query(Users.id).filter(
                        Users.username.like("%" + post.searched + "%")
                    )
                ),
            )
        )
        posts = posts.order_by(Posts.date_posted.desc()).all()
        return render_template(
            "search.html", form=form, searched=post.searched, posts=posts
        )

@app.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        # Check if username or email already exists (excluding the current user)
        existing_user = Users.query.filter(
            (Users.username == request.form["username"]) | 
            (Users.email == request.form["email"])
        ).filter(Users.id != id).first()

        if existing_user:
            if existing_user.username == request.form["username"]:
                flash("このユーザー名は既に使用されています。別のユーザー名で登録してください。")
            else:
                flash("このメールアドレスは既に登録されています。")
            return render_template(
                "update.html", form=form, name_to_update=name_to_update
            )

        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.favorite_color = request.form["favorite_color"]
        name_to_update.username = request.form["username"]

        try:
            db.session.commit()
            flash("ユーザー情報が更新されました!")
        except IntegrityError:
            db.session.rollback()
            flash("エラー! データベースの制約違反が発生しました。もう一度お試しください。")
        except Exception as e:
            db.session.rollback()
            flash(f"エラー! 問題が発生しました...: {str(e)}")

        return render_template(
            "update.html", form=form, name_to_update=name_to_update
        )
    else:
        return render_template(
            "update.html", form=form, name_to_update=name_to_update, id=id
        )


# その他の関数
# Pass Stuff To Navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# Error Handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

# 日付フォーマット
@app.template_filter("format_date")
def format_date(value, format="%Y/%m/%d"):
    if value is None:
        return ""
    return value.strftime(format)

@app.template_filter("format_date_second")
def format_date_second(value, format="%Y/%m/%d %H:%M:%S"):
    if value is None:
        return ""
    return value.strftime(format)

# contet から最初の画像を特定する
@app.template_filter('get_first_image')
def get_first_image(html_content):
    # HTMLからimg タグを検索
    img_pattern = re.compile(r'<img[^>]+src=["\'](.*?)["\']', re.IGNORECASE)
    match = img_pattern.search(html_content)
    
    if match:
        # 最初の画像のURLを返す
        return match.group(1)
    else:
        # 画像が見つからない場合はNoneを返す
        return None


# db.Model
# Create a Blog Post Model
class Posts(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(japan_tz)
    )
    keyword = db.Column(db.String(255))
    # Foreign Key To Link Users (refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # usersはDBのTable名


class Users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(500), nullable=True)
    date_added = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(japan_tz)
    )
    profile_pic = db.Column(db.String(255), nullable=True)

    # Do some password stuff!
    password_hash = db.Column(db.String(255))
    # User Can Have Many Posts
    posts = db.relationship(Posts, backref="poster", lazy=True, cascade="all, delete-orphan")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create A String
    def __repr__(self):
        return "<Name %r>" % self.name


# print(os.getenv('SQLALCHEMY_DATABASE_URI'))

if __name__ == "__main__":
    app.run(debug=False)
