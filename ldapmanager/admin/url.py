from flask import Blueprint
from ldapmanager.admin import sign
from ldapmanager.admin import users

adminblueprint = Blueprint("admin", __name__)
adminblueprint.add_url_rule('/admin/login', view_func=sign.Login.as_view('login'))
adminblueprint.add_url_rule('/admin/logout', view_func=sign.Logout.as_view('logout'))
adminblueprint.add_url_rule('/admin/userslist', view_func=users.UsersList.as_view('userslist'))
adminblueprint.add_url_rule('/admin/deleteuser', view_func=users.DeleteUser.as_view('delete'))
