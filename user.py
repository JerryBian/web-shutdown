from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_name) -> None:
        self._user_name = user_name
        self._is_active = True
        self._is_anonymous = False
        self._is_authenticated = False

    @property
    def is_authenticated(self):
        return self._is_authenticated

    @is_authenticated.setter
    def is_authenticated(self, a):
        self._is_authenticated = a

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, a):
        self._is_active = a

    @property
    def is_anonymous(self):
        return self._is_anonymous

    @is_anonymous.setter
    def is_anonymous(self, a):
        self._is_anonymous = a

    @property
    def name(self):
        return self._user_name

    def get_id(self):
        return self._user_name

    def verify_pwd(self, request_pwd, pwd):
        if request_pwd and pwd:
            self.is_authenticated = request_pwd == pwd
        else:
            self.is_authenticated = False
        
        self.is_anonymous = not self.is_authenticated