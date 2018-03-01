from flask import Blueprint
from ldapmanager.user.common import ChangePassword

commonblueprint = Blueprint("common", __name__)
commonblueprint.add_url_rule('/change_password', view_func=ChangePassword.as_view('change_passwd'))
