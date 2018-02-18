
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

# authenticating ldap user
def auth_login(username, password):
    conf = get_configs('ldap')
    user = 'uid=%s,%s' % (username, conf['account_base'])
    try:
        return Connection(Server(conf['ldap_server']), user, password, auto_bind=True)
    except Exception:
        return False

def get_admin_conn():
    conf = get_configs('ldap')
    try:
        return Connection(Server(conf['ldap_server']), conf['admin_dn'], conf['admin_password'])
    except Exception:
        return False

def list_users(conn, user=None):
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
    for (entry, counter) in zip(entry_generator, range(5)):
        print(entry['dn'])
    # return entry_generator ### unbind connectin causes generator error if any operation caused.
    conn.unbind()

def list_group(conn, group=None):
    conn.bind()
    conf = get_configs('ldap')
    if group:
        filter = '(cn=%s)' % group
    else:
        filter = '(objectClass=*)'
    entry = conn.extend.standard.paged_search(conf['group_base'],
                                              filter,
                                              search_scope=SUBTREE)
    return [item for item in entry]
    conn.unbind()

def add_user(conn, username, groupname):
    # TODO: Either modify groups from objectClass: groupOfUniqueNames to
    # objectClass: posixGroup with a gidNumber: 10000
    # or move all groups to groupOfUniqueNames and manage users
    # with uniqueMember: uid=...
    # gidNumber: 1 is a fake one.

    conn.bind()
    user = 'uid=%s,%s' % (username, get_configs('ldap')['account_base'])
    group = list_group(conn, groupname)
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
        conn.modify([item['dn'] for item in group],
                    {'uniqueMember': ('MODIFY_ADD', [user])})
        print(conn.result)
    conn.unbind()

# def modify_user(conn, username, groupname):
#     conn.bind()
#     conn.modify_dn()
#     conn.unbind()

def change_passwd(conn, username ,password):
    conn.bind()
    user = 'uid=%s,%s' % (username, get_configs('ldap')['account_base'])
    conn.modify(user,
                {'userPassword': ('MODIFY_REPLACE',
                                  [hashed(HASHED_SALTED_SHA, password)])})
    print conn.result
    conn.unbind()

def delete_user(conn, username):
    conn.bind()
    user = 'uid=%s,%s' % (username, get_configs('ldap')['account_base'])
    conn.delete(user)
    print conn.result
    # TODO: REMOVE user from group.
    conn.unbind()


if __name__ == '__main__':
    conn = get_admin_conn()
    # conn.bind()
    # conn.search('cn=SRE,ou=Groups,dc=ustack,dc=com', '(objectclass=*)', BASE, attributes=['member'])
    # conn.modify_dn('uid=yangfan,ou=Users,dc=ustack,dc=com', 'uid=yangfan', new_superior='ou=People,dc=ustack,dc=com')
    # conn.unbind()
    # add_user(get_admin_conn())
    # delete_user(get_admin_conn(), 'yangfan1')
    # print list_group(get_admin_conn(), 'SRE')

    add_user(conn, 'zdt2', 'Ops')
    change_passwd(conn, 'zdt2', 'asdfsadf')
    print auth_login('zdt2', 'asdfsadf')
    list_users(conn, 'zdt2')
    delete_user(conn, 'zdt2')
