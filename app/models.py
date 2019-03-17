from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
import os

from app import app_config, db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(10), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    documents = db.relationship('Document', backref='user', lazy='dynamic')
    meetings = db.relationship('Meeting', backref='user', lazy='dynamic')

    @property
    def is_management(self):
        return True if self.id == getattr(config, 'MANAGEMENT_ID') else False

    @property
    def password(self):
        raise AttributeError('dostęp zabroniony')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {}>'.format(self.username)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    signature = db.Column(db.String(10), index=True, nullable=True)
    creation_date = db.Column(db.DateTime, nullable=False,
                              default=datetime.utcnow)
    filename = db.Column(db.String(100), index=True, nullable=False)
    description = db.Column(db.String(100), index=True, nullable=True)
    type_id = db.Column(db.Integer, db.ForeignKey('types.id'), nullable=False)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'),
                           nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=True)
    type = db.relationship('Type')

    def __repr__(self):
        return '<Document: {} {}>'.format(self.signature, self.type)


class Meeting(db.Model):
    __tablename__ = 'meetings'
    id = db.Column(db.Integer, primary_key=True)
    signature = db.Column(db.String(10), index=True, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    documents = db.relationship('Document', backref='meeting', lazy='dynamic')

    def __repr__(self):
        return '<Meeting: {} {}>'.format(self.signature, self.summary)


class Type(db.Model):
    __tablename__ = 'types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), index=True, nullable=False)
    signature_required = db.Column(db.Boolean, default=False)
    is_standlone = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Type: {}>'.format(self.name)


config = app_config[os.getenv('FLASK_CONFIG')]
