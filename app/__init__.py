from flask import Flask,request, session
from flask_admin import Admin
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')

#initialises flask, db, loginmanager and admin
login_manager = LoginManager()
app = Flask(__name__)
app.secret_key = "Fc6Qwng4XJ"
babel = Babel(app, locale_selector=get_locale)
admin = Admin(app,template_mode='bootstrap4')
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager.init_app(app)

from app import views,models