# coding: utf-8
from flask.views import MethodView
from flask import render_template
from flask import session
from flask import request
from flask import redirect
from flask import url_for

from ldapmanager.common import forms
from ldapmanager.common import modules
from ldapmanager.common import ldap


class IndexView(MethodView):
    def get(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if current_user.is_administrator:
            return render_template('admin_index.html')
        elif current_user.is_active and current_user.is_admin:
            return render_template('managers_index.html')
        return redirect(url_for('admin.userslist'))


class UsersList(MethodView):
    def get(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if 'username' in session:
            if current_user.is_administrator:
                users = ldap.list_users(current_user.admin_conn)
            elif current_user.is_authenticated and current_user.groups:
                users = ldap.get_all_managable_users(current_user.admin_conn,
                                                     current_user.username,
                                                     current_user.groups)
            users = [i.split(',')[0].split('=')[-1].encode('utf-8') for i in users]
            users = reduce(lambda x,y:x if y in x else x + [y], [[]]+users)
            if users:
                return render_template('userslist.html', users=sorted(users),
                                       is_administrator=current_user.is_administrator)
            return "DOCS"
        else:
            return redirect(url_for('admin.login'))


class DeleteUser(MethodView):
    def get(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if 'username' in session:
            target = request.args.get('uid')
            # Check if target is admin or user it self
            if not target:
                return redirect(url_for('admin.userslist'))
            if target == 'admin' or target == session['username']:
                return "CANNOT DELETE THIS USER"
            ldap.delete_user(current_user.admin_conn, target)
            return redirect(url_for('admin.userslist'))


class AddUser(MethodView):
    """Add user to the group of a admin user"""
    def get(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if 'username' in session:
            groups_choices = [(x,x) for x in \
                              [i.split(',')[0].split('=')[-1] \
                              for i in current_user.groups]]
            groups_choices += [('None', 'None')]
            add_user_form = forms.AddUserForm()
            add_user_form.groups.choices = groups_choices
        return render_template("adduser.html", form=add_user_form)

    def post(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        add_user_form = forms.AddUserForm()
        name = request.form.get('name')
        groups = request.form.get('groups')
        mail = request.form.get('email')

        if not groups:
            groups = None
        if not mail:
            mail = None

        ldap.add_user(current_user.admin_conn, name, groups, mail)

        return redirect(url_for('admin.userslist'))


class UserDetail(MethodView):
    """View a user's information."""
    def get(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if not 'username' in session:
            return redirect(url_for('admin.login'))
        username = request.args.get('user')
        detail = {'name': username}
        groups = ldap.get_groups_with_user(current_user.admin_conn,
                                           username=username)
        detail['groups'] = [i.split(',')[0].split('=')[-1] for i in groups]
        return render_template('userdetail.html', detail=detail)
