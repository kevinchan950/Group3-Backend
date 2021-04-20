from flask import Flask
from flask_wtf.csrf import CSRFProtect
from models.base_model import db
from models.user import User
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import config
import os

web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'grocery_api')

app = Flask('Grocery', root_path=web_dir)
app.secret_key = os.getenv('SECRET_KEY')
csrf = CSRFProtect(app)
jwt = JWTManager(app)
login_manager = LoginManager()
login_manager.init_app(app)
CORS(app)
cors = CORS(app, resources={r"/api/*": {"origins":"*"}})

if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

@login_manager.user_loader
def load_user(user_id):
    return User.get_or_none(User.id == user_id)

@app.before_request
def before_request():
    db.connect()

@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        print(db)
        print(db.close())
    return exc