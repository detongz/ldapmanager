from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

from ldapmanager import modules

app = Flask(__name__)
loginmanager = LoginManager(app)
loginmanager.session_protection = "strong"
