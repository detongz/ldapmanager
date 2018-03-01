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

        if 'username' in session:
            if not current_user.is_administrator:
                return redirect(url_for('admin.userslist'))


class AddGroup(MethodView):
    """administrator only"""
    def get(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if 'username' in session:
            if not current_user.is_administrator:
                return redirect(url_for('admin.userslist'))


class DeleteGroup(MethodView):
    """administrator only"""
    def get(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if 'username' in session:
            if not current_user.is_administrator:
                return redirect(url_for('admin.userslist'))


class ChangeGroup(MethodView):
    """Change groupname
       administrator only
    """
    def get(self):
        try:
            current_user = modules.Redis.get(session['username'])
        except Exception:
            return redirect(url_for('admin.login'))

        if 'username' in session:
            if not current_user.is_administrator:
                return redirect(url_for('admin.userslist'))
