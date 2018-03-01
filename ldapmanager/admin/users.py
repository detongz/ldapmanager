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


class UsersList(MethodView):
    def get(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if 'username' in session:
            if current_user.is_administrator:
                users = ldap.list_users(current_user.admin_conn)
                return render_template('userslist.html', users=users)
            elif current_user.is_authenticated and current_user.groups:
                users = ldap.get_all_managable_users(current_user.admin_conn,
                                                     current_user.username)
                # TODO: 用户去重
                if users:
                    return render_template('userslist.html', users=users)
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
            if current_user.is_administrator:
                groups = [i['dn'] for i in ldap.get_group(current_user.admin_conn)]
            elif current_user.is_active:
                groups = ldap.get_administrated_groups(current_user.admin_conn,
                                                       session['username'])
            groups_choices = [(x,x) for x in \
                              [i.split(',')[0].split('=')[-1] \
                              for i in groups]]
            # groups_choices = [i.split(',')[0].split('=')[-1] for i in groups]
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

        if not groups:
            groups = None

        ldap.add_user(current_user.admin_conn, name, groups)

        return redirect(url_for('admin.userslist'))


class RemoveUserFromGroup(MethodView):
    def get(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if 'username' in session:
            if current_user.is_administrator:
                pass
