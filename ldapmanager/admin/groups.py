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


class GroupsList(MethodView):
    def get(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if not 'username' in session:
            return redirect(url_for('admin.login'))

        groups = [i.split(',')[0].split('=')[-1] for i in current_user.groups]
        return render_template('groups.html', groups=groups,
                               is_administrator=current_user.is_administrator)


class GrouopDetail(MethodView):
    """show all uesrs of a group"""

    def get(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if not 'username' in session:
            return redirect(url_for('admin.login'))

        group_name = request.args.get('group')

        users = ldap.get_group_users(current_user.admin_conn, group_name)
        admin = ldap.filter_admin_users(current_user.admin_conn, users)

        if users and admin:
            filter = lambda x: [i.split(',')[0].split('=')[-1] for i in x]
            group = {'name': group_name,
                     'users': filter(users),
                     'admin': filter(admin)}
        else:
            group = {'name': group_name, 'users': [], 'admin': []}
        return render_template('groupdetail.html', group=group)


class AddGroup(MethodView):
    """administrator only"""
    def get(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if not 'username' in session:
            return redirect(url_for('admin.login'))
        if not current_user.is_administrator:
            return "Only user admin is allowed for adding groups."
        return render_template('addgroup.html')

    def post(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if not 'username' in session:
            return redirect(url_for('admin.login'))
        if not current_user.is_administrator:
            return "Only user admin is allowed for adding groups."

        group = request.form.get('group')
        users = request.form.get('users')
        if not group:
            return redirect('admin.addgroup')
        if not users:
            return "At least one user is required for creating a group."
        users = users.split(",")
        ldap.add_group(current_user.admin_conn, group, users)

        current_user.get_groups()
        modules.Redis.set(current_user.username, current_user)

        return redirect('/admin/groupslist')

class DeleteGroup(MethodView):
    """administrator only"""
    def get(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if not 'username' in session:
            return redirect(url_for('admin.login'))
        if not current_user.is_administrator:
            return "Only user admin is allowed for adding groups."

        group = request.args.get('group')
        if group:
            ldap.delete_group(current_user.admin_conn, group)

        current_user.get_groups()
        modules.Redis.set(current_user.username, current_user)

        return redirect(url_for('admin.groupslist'))


class ChangeGroupName(MethodView):
    """Change groupname
       administrator only
    """
    def post(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if not 'username' in session:
            return redirect(url_for('admin.login'))
        if not current_user.is_administrator:
            return "Only user admin is allowed for adding groups."

        new_group_name = request.form.get('new')
        old_group_name = request.form.get('old')

        ldap.change_group_name(current_user.admin_conn, old=old_group_name,
                               new=new_group_name)

        current_user.get_groups()
        modules.Redis.set(current_user.username, current_user)

        return redirect('/admin/groupdetail?group=%s' % new_group_name)


class AddUserToGroup(MethodView):
    def get(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if not 'username' in session:
            return redirect(url_for('admin.login'))

        username = request.args.get('uid')
        if not username:
            return redirect(url_for('admin.userslist'))
        groups_choices = [(x,x) for x in \
                         [i.split(',')[0].split('=')[-1] \
                         for i in current_user.groups]]
        form = forms.AddUserForm()
        form.groups.choices = groups_choices
        return render_template("addusertogroup.html", form=form,
                               username=username)


class RemoveUserFromGroup(MethodView):
    def get(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if not 'username' in session:
            return redirect(url_for('admin.login'))

        username = request.args.get('user')
        group = request.args.get('group')
        if username and group:
            ldap.remove_user_from_group(current_user.admin_conn, username, group)
            return redirect('/admin/groupdetail?group=%s' % group)
        return "User name and group name could not be blank"
