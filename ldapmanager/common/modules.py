import redis
import dill

from ldapmanager.common import configs
from ldapmanager.common import ldap
from ldapmanager import login_manager
from datetime import timedelta


class Redis():
    @staticmethod
    def get_connection():
        conn = redis.StrictRedis(host='localhost', port=6379, db=0)
        return conn

    @staticmethod
    def set(key, data, ex=None):
        conn = Redis.get_connection()
        conn.set(key, dill.dumps(data), ex)
        conn.expire(key, timedelta(days=1))

    @staticmethod
    def get(key):
        conn = Redis.get_connection()
        data = conn.get(key)
        if data is not None:
            return dill.loads(data)
        return None

    @staticmethod
    def delete(key):
        conn = Redis.get_connection()
        conn.delete(key)

class User(object):
    def __init__(self, username, password):
        self.admin_conn = None
        self.manager_conn = None
        self.groups = None
        self.username = username
        self.password = password
        self.admin = False

        self.is_active = False
        self.is_authenticated = False
        self.is_administrator = False
        self.is_anonymous = True

        config = configs.get_configs('ldap')
        admin_conn = ldap.get_admin_conn()
        if username == "admin" and password == config['admin_password']:
            self.manager_conn = admin_conn
            self.admin_conn = admin_conn
            self.admin = True
            self.is_administrator = True
        else:
            conn = ldap.auth_login(username, password)
            groups = ldap.get_administrated_groups(admin_conn, username)
            if conn and groups:
                self.manager_conn = conn
                self.admin_conn = admin_conn
                self.groups = groups

        if self.admin_conn and self.manager_conn:
            self.is_active = True
            self.is_authenticated = True
            self.is_anonymous = False
