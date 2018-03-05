from flask import Blueprint
from ldapmanager.admin import sign
from ldapmanager.admin import users
from ldapmanager.admin import groups

adminblueprint = Blueprint("admin", __name__)
adminblueprint.add_url_rule('/', view_func=sign.Login.as_view('login_repl'))
adminblueprint.add_url_rule('/admin/', view_func=users.IndexView.as_view('index'))
adminblueprint.add_url_rule('/admin/index', view_func=users.IndexView.as_view('index_repl'))
adminblueprint.add_url_rule('/admin/login', view_func=sign.Login.as_view('login'))
adminblueprint.add_url_rule('/admin/logout', view_func=sign.Logout.as_view('logout'))
adminblueprint.add_url_rule('/admin/userslist', view_func=users.UsersList.as_view('userslist'))
adminblueprint.add_url_rule('/admin/userdetail', view_func=users.UserDetail.as_view('userdetail'))
adminblueprint.add_url_rule('/admin/deleteuser', view_func=users.DeleteUser.as_view('delete'))
adminblueprint.add_url_rule('/admin/adduser', view_func=users.AddUser.as_view('adduser'))


adminblueprint.add_url_rule('/admin/groupslist', view_func=groups.GroupsList.as_view('groupslist'))
adminblueprint.add_url_rule('/admin/groupdetail', view_func=groups.GrouopDetail.as_view('groupdetail'))
adminblueprint.add_url_rule('/admin/removeuserfromgroup', view_func=groups.RemoveUserFromGroup.as_view('removeuserfromgroup'))
adminblueprint.add_url_rule('/admin/addgroup', view_func=groups.AddGroup.as_view('addgroup'))
adminblueprint.add_url_rule('/admin/changegroupname', view_func=groups.ChangeGroupName.as_view('changegroupname'))
adminblueprint.add_url_rule('/admin/deletegroup', view_func=groups.DeleteGroup.as_view('deletegroup'))
adminblueprint.add_url_rule('/admin/addusertogroup', view_func=groups.AddUserToGroup.as_view('addusertogroup'))
