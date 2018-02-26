from flask.views import MethodView
from flask import render_template
from flask import session
from flask import request
from flask import redirect
from flask import url_for

from ldapmanager.common import ldap
from ldapmanager.common import modules


class UsersList(MethodView):
    def get(self):
        if 'username' in session:
            current_user = modules.Redis.get(session['username'])
            if current_user.is_administrator:
                users = ldap.list_users(current_user.admin_conn)
                return render_template('userslist.html', users=users)
            elif current_user.is_authenticated:
                return str(current_user.groups)
        else:
            return redirect(url_for('admin.login'))


class DeleteUser(MethodView):
    def get(self):
        uid = request.args.get('uid')
        # Check if target is admin or user it self
        ldap.delete_user(ldap.get_admin_conn(), uid)
        return redirect(url_for('admin.userslist'))
