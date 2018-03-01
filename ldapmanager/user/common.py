# coding: utf-8
from flask.views import MethodView
from flask import render_template
from flask import session
from flask import request
from flask import redirect
from flask import url_for
import radius

from ldapmanager.common import configs
from ldapmanager.common import forms
from ldapmanager.common import ldap
from ldapmanager.common import modules


class ChangePassword(MethodView):
    def get(self):
        password_form = forms.ChangePasswordForm()
        return render_template("changepassword.html", form=password_form)

    def post(self):
        password_form = forms.ChangePasswordForm()

        username = request.form.get('username')
        password = request.form.get('password')
        confirm_pwd = request.form.get('confirm')
        code = request.form.get('code')

        google_auth = configs.get_configs('google_auth')
        if not username:
            # TODO: Check username syntax.
            return "Username incorrect"
        elif not password or not confirm_pwd:
            return "Password cannot left blank"
        elif not code:
            return "Google Authenticator Code not found"
        elif password != confirm_pwd:
            return "Password not match"

        r = radius.Radius(google_auth['secret'], google_auth['host'])
        if r.authenticate(username, code):
            if not ldap.list_users(user=username):
                return "User Not Exist"
            ldap.change_passwd(username=username,
                               password=password.encode('utf-8'))
            return "Reset Password Success"
        return "Identify Authentication Failed"
