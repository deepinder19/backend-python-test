"""
This module provides object relational mapper and 
implements models using flask sqlalchemy. 
"""

from flask_sqlalchemy import SQLAlchemy
from alayatodo import app

db = SQLAlchemy(app)


class User(db.Model):
    """
    This class represnts the user. Authentication is based on 
    user object.
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Todos(db.Model):
    """
    This class represents a todo, with a reference to the user table
    """
    
    __tablename__ = 'todos'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.String(255))
    is_complete = db.Column(db.Boolean, default=False)
