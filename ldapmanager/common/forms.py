from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms import RadioField
from wtforms import SelectField
from wtforms import StringField
from wtforms import validators


class LoginForm(FlaskForm):
    username = StringField('username', [validators.Length(min=3, max=20), validators.DataRequired()])
    password = PasswordField('password', [validators.Length(min=6, max=20), validators.DataRequired()])


class ChangePasswordForm(FlaskForm):
    """code here is google authenticator code"""
    username = StringField('username', [validators.Length(min=3, max=20), validators.DataRequired()])
    code = PasswordField('code', [validators.Length(min=12, max=12), validators.DataRequired()])
    password = PasswordField('New Password',
                             [validators.DataRequired(),
                              validators.Length(min=6, max=20, message='Password length must be 6-20'),
                              validators.EqualTo('confirm', message='Password must match')])
    confirm = PasswordField('Repeat Password')


class AddUserForm(FlaskForm):
    name = StringField('name', [validators.DataRequired()])
    groups = SelectField('groups', choices=[], option_widget='btn btn-success')
    email = StringField('email', [validators.DataRequired()])
