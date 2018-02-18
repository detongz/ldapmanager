from flask.ext import login

class User(login.UserMixin):
    # TODO: SAVE admin connection and user connection in this class.
    def is_authenticated(self):
        pass
    def is_active(self):
        pass
    def is_anonymous(self):
        pass
    def get_id(self):
        pass
