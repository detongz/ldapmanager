from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template
from flask.views import MethodView

from ldapmanager.common import form
from ldapmanager.common import ldap
from ldapmanager.common import modules


class Login(MethodView):
    def get(self):
        loginform = form.LoginForm()
        return render_template('login.html', form=loginform)

    def post(self):
        loginform = form.LoginForm()
        username = request.form.get('username')
        password = request.form.get('password', type=str)

        user = modules.User(username, password)
        if user.is_active:
            modules.Redis.set(username, user)
            session['username'] = username
            return redirect(url_for('admin.userslist'))
        return "NO SUCH USER OR PASSWORD INCORRECT"


class Logout(MethodView):
    def get(self):
        try:
            modules.Redis.delete(session['username'])
            session.clear()
        except Exception:
            pass
        return redirect(url_for('admin.login'))
