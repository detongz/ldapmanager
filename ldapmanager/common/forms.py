from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms import validators


class LoginForm(FlaskForm):
    username = StringField('username', [validators.Length(min=3, max=20), validators.DataRequired()])
    password = PasswordField('password', [validators.Length(min=6, max=20), validators.DataRequired()])
