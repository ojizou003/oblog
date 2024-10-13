from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    PasswordField,
    TextAreaField,
    FileField,
)
from wtforms.validators import DataRequired, EqualTo, Length
from flask_ckeditor import CKEditorField


class LoginForm(FlaskForm):
    username = StringField("ユーザー名 : ", validators=[DataRequired()])
    password = PasswordField("パスワード : ", validators=[DataRequired()])
    submit = SubmitField("ログイン")


class PostForm(FlaskForm):
    title = StringField("タイトル", validators=[DataRequired()])
    keyword = StringField("キーワード", validators=[DataRequired()])
    content = CKEditorField("記事", validators=[DataRequired()])
    submit = SubmitField("投稿")


class SearchForm(FlaskForm):
    searched = StringField("検索 : ", validators=[DataRequired()])
    submit = SubmitField("検索")


class UserForm(FlaskForm):
    name = StringField("お名前 : ", validators=[DataRequired()])
    username = StringField("ユーザー名 : ", validators=[DataRequired()])
    email = StringField("Ｅメール : ", validators=[DataRequired()])
    favorite_color = StringField("好きな色 : ")
    about_author = TextAreaField("著者から一言 : ")
    password_hash = PasswordField(
        "パスワード : ",
        validators=[
            DataRequired(),
            EqualTo("password_hash2", message="パスワードが一致しません!"),
        ],
    )
    password_hash2 = PasswordField("パスワード(確認用) : ", validators=[DataRequired()])
    profile_pic = FileField("プロフィール画像 : ")
    submit = SubmitField("送信")
    update = SubmitField("更新")
    register = SubmitField("登録")
