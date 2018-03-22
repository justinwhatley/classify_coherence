from myapp import db
from myapp import app

from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                         as Serializer, BadSignature, SignatureExpired)

class Completed_Questionnaires(db.Model):
    __tablename__ = 'completed_questionnaires'
    user_id = db.Column(db.String(32), primary_key=True)
    last_answered_question = db.Column(db.Integer)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
       self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
       return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
       s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
       return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
       s = Serializer(app.config['SECRET_KEY'])
       try:
           data = s.loads(token)
       except SignatureExpired:
           return None    # valid token, but expired
       except BadSignature:
           return None    # invalid token
       user = User.query.get(data['id'])
       return user


# Create the database tables.
db.create_all()



# class User(db.Model):
#
#     """
#     https://realpython.com/blog/python/using-flask-login-for-user-management-with-flask/
#     An admin user capable of viewing reports.
#
#     :param str email: email address of user
#     :param str password: encrypted password for the user
#
#     """
#     __tablename__ = 'user'
#
#     email = db.Column(db.String, primary_key=True)
#     password = db.Column(db.String)
#     authenticated = db.Column(db.Boolean, default=False)
#
#     def is_active(self):
#         """True, as all users are active."""
#         return True
#
#     def get_id(self):
#         """Return the email address to satisfy Flask-Login's requirements."""
#         return self.email
#
#     def is_authenticated(self):
#         """Return True if the user is authenticated."""
#         return self.authenticated
#
#     def is_anonymous(self):
#         """False, as anonymous users aren't supported."""
#         return False