from flask import Blueprint
from ldapmanager.manager import sign
from ldapmanager.manager import users

managerblueprint = Blueprint('admin', __name__)
managerblueprint.add_url_rule('/admin/login', view_func=sign.Login.as_view('login'))
managerblueprint.add_url_rule('/admin/logout', view_func=sign.Logout.as_view('logout'))
managerblueprint.add_url_rule('/admin/userslist', view_func=users.UsersList.as_view('userslist'))
managerblueprint.add_url_rule('/admin/deleteuser', view_func=users.DeleteUser.as_view('delete'))
