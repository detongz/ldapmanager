from flask import Flask
from flask_login import LoginManager
from ldapmanager import modules


app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'admin.login'
login_manager.session_protection = "strong"
