from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    hashPassword = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Users {self.id}: '{self.name}'>"

