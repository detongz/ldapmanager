
from ldap3 import Server
from ldap3 import Connection
from ldap3 import ALL

from configs import get_configs

def authlogin(username, password):
    conf = get_configs('ldap')
    user = 'uid=%s,%s' % (username, conf['accountbase'])
    try:
        return Connection(Server(conf['ldapserver']), user, password, auto_bind=True)
    except Exception:
        return False
