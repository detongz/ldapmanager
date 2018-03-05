# coding: utf-8
from ldap3 import ALL
from ldap3 import Connection
from ldap3 import Server
from ldap3 import SUBTREE
from ldap3 import BASE
from ldap3 import MODIFY_ADD
from ldap3 import MODIFY_DELETE
from ldap3 import MODIFY_REPLACE
from ldap3 import HASHED_SALTED_SHA

from ldap3.utils.hashed import hashed

from configs import get_configs

# authenticating all ldap users
def auth_login(username, password):
    conf = get_configs('ldap')
    user = 'uid=%s,%s' % (username, conf['account_base'])
    try:
        return Connection(Server(conf['ldap_server']), user, password,
                          auto_bind=True)
    except Exception:
        return False

def get_admin_conn():
    conf = get_configs('ldap')
    try:
        return Connection(Server(conf['ldap_server']), conf['admin_dn'],
                          conf['admin_password'])
    except Exception:
        return False

def list_users(conn=None, user=None):
    if not conn:
        conn = get_admin_conn()
    conn.bind()
    if user:
        filter = '(uid=%s)' % user
    else:
        filter = '(objectClass=inetOrgPerson)'
    entry_generator = conn.extend.standard.paged_search(
                search_base=get_configs('ldap')['account_base'],
                search_filter=filter,
                search_scope = SUBTREE,
                paged_size=5,
                generator=True)
    # for (entry, counter) in zip(entry_generator, range(5)):
    #     print(entry['dn'])
    # return entry_generator ### unbind connectin causes generator error if any operation caused.
    entry = [item['dn'] for item in entry_generator]
    conn.unbind()
    return entry

def get_group(conn, group=None):
    conn.bind()
    conf = get_configs('ldap')
    if group:
        filter = '(cn=%s)' % group
    else:
        filter = '(objectClass=*)'
    entry = conn.extend.standard.paged_search(conf['group_base'],
                                              filter,
                                              search_scope=SUBTREE)
    if entry:
        group_result = [item['dn'] for item in entry]
    else:
        group_result = []
    conn.unbind()
    return group_result

def add_user(conn, username, groupname, mail=None):
    # TODO: Either modify groups from objectClass: groupOfUniqueNames to
    # objectClass: posixGroup with a gidNumber: 10000
    # or move all groups to groupOfUniqueNames and manage users
    # with uniqueMember: uid=...
    # gidNumber: 1 is a fake one.

    # param username: str name of a user.
    # param groupname: str name of a group.

    conn.bind()
    user = 'uid=%s,%s' % (username, get_configs('ldap')['account_base'])
    group = get_group(conn, groupname)
    conn.bind()
    conn.add(user,
             ['inetOrgPerson', 'posixAccount', 'shadowAccount', 'top'],
             {'sn': username, 'displayName': username, 'cn': username,
             'uidNumber': 1, 'gidNumber': 1, 'givenName': username,
             'homeDirectory': '/home/' + username, 'uid': username})
    print(conn.result)
    # Add user to group:
    if group:
        # TODO: add support for user modify gidNumber for
        # none groupOfUniqueNames groups:
        # conn.modify(user, {'gidNumber': (MODIFY_ADD, [item['']])})
        # conn.extend.microsoft.add_members_to_groups([user],[group]) ##invalid
        conn.modify(group,
                    {'uniqueMember': ('MODIFY_ADD', [user])})
        print(conn.result)
    if mail:
        conn.modify(user, {'mail': ('MODIFY_REPLACE', mail)})
    conn.unbind()

def add_group(conn, groupname, users):
    group = 'cn=%s,%s' % (groupname, get_configs('ldap')['group_base'])
    users_dn = map(lambda x: 'uid=%s,%s' %
                  (x, get_configs('ldap')['account_base']),
                  users)
    conn.bind()
    conn.add(group, ['groupOfUniqueNames', 'top'],
             {'uniqueMember': users_dn, 'cn': groupname})
    print conn.result
    conn.unbind()

def change_passwd(username, password, conn=None):
    if not conn:
        conn = get_admin_conn()
    conn.bind()
    user = 'uid=%s,%s' % (username, get_configs('ldap')['account_base'])
    conn.modify(user,
                {'userPassword': ('MODIFY_REPLACE',
                                  [hashed(HASHED_SALTED_SHA, password)])})
    print conn.result
    conn.unbind()
    return True

def change_group_name(conn, old, new):
    if old and new:
        if get_group(conn, new):
            return False
        conn.bind()
        old_dn = 'cn=%s,%s' % (old, get_configs('ldap')['group_base'])
        conn.modify_dn(old_dn, "cn="+new)
        print conn.result
        conn.unbind()
        return True

def delete_user(conn, username):
    conn.bind()
    user = 'uid=%s,%s' % (username, get_configs('ldap')['account_base'])
    conn.delete(user)
    groups = get_groups_with_user(conn=conn, user_dn=user)
    # REMOVE user from groups.
    if groups:
        conn.bind()
        conn.modify(groups, {'uniqueMember': (MODIFY_DELETE, user)})
    conn.unbind()

def delete_group(conn, group):
    group_dn = get_group(conn, group)
    if group_dn:
        conn.bind()
        conn.delete(group_dn)
        conn.unbind()

def remove_user_from_group(conn, username, group):
    conn.bind()
    user = 'uid=%s,%s' % (username, get_configs('ldap')['account_base'])
    group = 'cn=%s,%s' % (group, get_configs('ldap')['group_base'])
    conn.modify(group, {'uniqueMember': (MODIFY_DELETE, user)})
    print conn.result
    conn.unbind()

def get_administrated_groups(conn, username):
    # return group which leader belongs or return False
    conn.bind()
    is_leader = False
    leaders_group_name = get_configs('ldap')['leaders_group_name']
    user = 'uid=%s,%s' % (username, get_configs('ldap')['account_base'])
    conn.search(search_base=leaders_group_name,
                search_filter='(objectClass=groupOfUniqueNames)',
                search_scope=SUBTREE, attributes=['uniqueMember'])
    for entry in conn.response:
        if user in entry['attributes']['uniqueMember']:
            is_leader = True
    if is_leader:
        return get_groups_with_user(conn=conn, user_dn=user,
                                    leaders_group_dn=leaders_group_name)
    conn.unbind()
    return is_leader

def get_groups_with_user(conn, user_dn=None, leaders_group_dn=None, username=None):
    # search for groups containing this user
    conn.bind()
    groups = []
    conn.search(search_base=get_configs('ldap')['group_base'],
                search_filter='(objectClass=groupOfUniqueNames)',
                search_scope=SUBTREE, attributes=['uniqueMember'])
    if not user_dn:
        if not username:
            return None
        user_dn = 'uid=%s,%s' % (username, get_configs('ldap')['account_base'])
    for group in conn.response:
        if user_dn in group['attributes']['uniqueMember'] and \
        group['dn'] != leaders_group_dn:
            groups.append(group['dn'])
    conn.unbind()
    return groups

def get_all_managable_users(conn, username, groups=None):
    conn.bind()
    if not groups:
        groups = get_administrated_groups(conn, username)
    users = []
    for group in groups:
        conn.bind()
        conn.search(search_base=group,
                    search_filter='(objectClass=*)',
                    search_scope=SUBTREE, attributes=['uniqueMember'])
        for members in conn.response:
            users += members['attributes']['uniqueMember']
    conn.unbind()
    return users

def get_group_users(conn, group_name):
    group = 'cn=%s,%s' % (group_name, get_configs('ldap')['group_base'])
    conn.bind()
    conn.search(search_base=group,
                search_filter='(objectClass=groupOfUniqueNames)',
                search_scope=SUBTREE, attributes=['uniqueMember'])
    response = conn.response
    if not response:
        return []
    users = conn.response[0]['attributes']['uniqueMember']
    conn.unbind()
    return users

def filter_admin_users(conn, users):
    conn.bind()
    conn.search(search_base=get_configs('ldap')['leaders_group_name'],
                search_filter='(objectClass=*)',
                search_scope=SUBTREE, attributes=['uniqueMember'])
    admins = conn.response[0]['attributes']['uniqueMember']
    admin_users = []
    if not users:
        return None
    for user in users:
        if user in admins:
            admin_users.append(user)
    return sorted(admin_users)

if __name__ == '__main__':
    conn = get_admin_conn()
    conn.bind()
    # conn.search('cn=SRE,ou=Groups,dc=ustack,dc=com', '(objectclass=*)', BASE, attributes=['member'])
    # conn.modify_dn('uid=yangfan,ou=Users,dc=ustack,dc=com', 'uid=yangfan', new_superior='ou=People,dc=ustack,dc=com')
    # conn.unbind()
    # delete_user(get_admin_conn(), 'zhanglihui')
    # print get_group(get_admin_conn(), 'SRE')

    # add_user(conn, 'zdt10010', 'Network')
    # print auth_login('zhangdetong', 'adsf')
    # list_users(conn, 'zdt2')
    # delete_user(conn, 'hebin')

    # conn.bind()
    # conn.search(search_base='ou=Groups,dc=ustack,dc=com',
    #               search_filter='(objectClass=groupOfUniqueNames)',
    #               search_scope = SUBTREE, attributes=['uniqueMember'])
    # for entry in conn.response:
    #     print(entry['dn'], entry['attributes']['uniqueMember'])
    #     # conn.modify(entry['dn'], {'objectClass': [(MODIFY_ADD, ['posixGroup'])]})
    #     # print conn.result
    # print add_group(conn, 'asdf', ['zdt2', 'robot'])
    conn.unbind()
    # print change_passwd('zhangdetong', 'asdf')
