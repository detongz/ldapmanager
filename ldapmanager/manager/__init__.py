from flask import Blueprint
from ldapmanager.manager import sign

managerblueprint = Blueprint('admin', __name__)
managerblueprint.add_url_rule('/admin/login', view_func=sign.Login.as_view('login'))
managerblueprint.add_url_rule('/admin/logout', view_func=sign.Logout.as_view('logout'))
