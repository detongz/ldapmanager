from ldapmanager import app
from ldapmanager.admin import adminblueprint
from ldapmanager.user import commonblueprint
from ldapmanager.manager import managerblueprint
import os

app.register_blueprint(adminblueprint)
app.register_blueprint(commonblueprint)
app.register_blueprint(managerblueprint)

if __name__ == '__main__':
    app.config['SECRET_KEY'] = os.urandom(20)
    app.run()
