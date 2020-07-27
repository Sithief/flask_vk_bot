from bot_core.__init__ import *
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clicker_id = db.Column(db.Integer, db.ForeignKey('clicker.id'))
    clicker = db.relationship('Clicker')


class Clicker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hearts = db.Column(db.Integer, default=0)
    magic = db.Column(db.Integer, default=0)
    fires = db.Column(db.Integer, default=0)
    warriors = db.Column(db.Integer, default=0)


def migration():
    db.create_all()
    # migrate = Migrate(app, db)
    # manager = Manager(app)
    # manager.add_command('db', MigrateCommand)
    # manager.run()
