from flask.views import MethodView
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from ldapmanager.common import ldap

class UsersList(MethodView):
    def get(self):
        users = ldap.list_users(ldap.get_admin_conn())
        return render_template('userslist.html', users=users)

    # def delete()

class DeleteUser(MethodView):
    def get(self):
        uid = request.args.get('uid')
        ldap.delete_user(ldap.get_admin_conn(), uid)
        return redirect(url_for('admin.userslist'))
