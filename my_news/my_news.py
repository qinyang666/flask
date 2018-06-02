from flask import Flask
from config import DevelopConfig
from app import create_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from models import db

app = create_app(DevelopConfig)



if __name__ == '__main__':
    db.init_app(app)

    manager = Manager(app)

    migrate = Migrate(app, db)
    manager.add_command("db", MigrateCommand)

    manager.run()
