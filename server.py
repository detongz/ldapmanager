from ldapmanager import app
from ldapmanager.manager import managerblueprint
import os

app.register_blueprint(managerblueprint)

if __name__ == '__main__':
    app.debug=True
    app.config['SECRET_KEY'] = os.urandom(20)
    app.run()
