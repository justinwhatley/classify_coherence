from myapp import db

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.Unicode, unique=True)
  password = db.Column(db.Unicode)
  email = db.Column(db.Unicode, unique=True)

# Create the database tables.
db.create_all()

