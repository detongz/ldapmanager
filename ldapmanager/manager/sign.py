from flask import request
from flask import session
from flask import redirect
from flask import url_for
from flask import render_template
from flask.views import MethodView

from ldapmanager.common import form
from ldapmanager.common import ldap

class Login(MethodView):
    def get(self):
        loginform = form.LoginForm()
        return render_template('login.html', form=loginform)
    def post(self):
        loginform = form.LoginForm()
        username = request.form.get('username')
        password = request.form.get('password', type=str)
        if username and password:
            ldapconn = ldap.authlogin(username, password)
            if ldapconn:
                session['password'] = password
                session['username'] = username
                return "haha"
        return "hehes"


class Logout(MethodView):
    def get(self):
        session.clear()
        return redirect(url_for('admin.login'))
