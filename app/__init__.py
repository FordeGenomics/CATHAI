import os, base64, sys, logging
from flask import Flask, g
from flask_assets import Environment
from flask_compress import Compress
from flask_login import LoginManager, AnonymousUserMixin
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from app.assets import app_css, app_js, vendor_css, vendor_js
from app.utils import Metadata
from config import config as Config

from celery import Celery
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery

basedir = os.path.abspath(os.path.dirname(__file__))

csrf = CSRFProtect()
compress = Compress()

from flask.sessions import SecureCookieSessionInterface

class CustomSessionInterface(SecureCookieSessionInterface):
    """Prevent creating session from API requests."""
    def save_session(self, *args, **kwargs):
        if g.get('login_via_header'):
            return
        return super(CustomSessionInterface, self).save_session(*args, **kwargs)

app = Flask(__name__, static_url_path='')

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.addHandler(logging.StreamHandler(sys.stderr))

assert os.environ.get('FLASK_CONFIG'), 'FLASK_CONFIG IS NOT SET!'
config_name = os.getenv('FLASK_CONFIG')
config = Config[config_name]()

app.config.from_object(config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# not using sqlalchemy event system, hence disabling it

# Set up extensions
csrf.init_app(app)
compress.init_app(app)

# Register Jinja template functions
from .utils import Metadata, register_template_utils
register_template_utils(app)

# Set up metadata
metadata = Metadata(app.config['DATA_DIR'])

# Set up asset pipeline
assets_env = Environment(app)
dirs = ['assets/styles', 'assets/scripts']
for path in dirs:
    assets_env.append_path(os.path.join(basedir, path))
assets_env.url_expire = True

assets_env.register('app_css', app_css)
assets_env.register('app_js', app_js)
assets_env.register('vendor_css', vendor_css)
assets_env.register('vendor_js', vendor_js)

# Configure SSL if platform supports it
# Let nginx handle this!
# if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
#     from flask_sslify import SSLify
#     SSLify(app)

if app.config['STAND_ALONE'] == True:
    # Create app blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .cathai import cathai as cathai_blueprint
    app.register_blueprint(cathai_blueprint, url_prefix='/cathai')

# Set up Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'account.login'
login_manager.init_app(app)

@app.context_processor
def inject_stand_alone():
    return dict(stand_alone=app.config['STAND_ALONE'])

if app.config['STAND_ALONE'] == False:
    # Set up extensions for multi-user mode
    mail = Mail()
    db = SQLAlchemy(session_options={'expire_on_commit': False})
    mail.init_app(app)
    db.init_app(app)
    celery = make_celery(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .cathai import cathai as cathai_blueprint
    app.register_blueprint(cathai_blueprint, url_prefix='/cathai')

    # routes for multi-user
    from .account import account as account_blueprint
    app.register_blueprint(account_blueprint, url_prefix='/account')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # Disable session cookie for APIs
    app.session_interface = CustomSessionInterface()
    from flask_login import user_loaded_from_header

    @user_loaded_from_header.connect
    def user_loaded_from_header(self, user=None):
        g.login_via_header = True

    # Handle API logins via URL argument or header auth
    from app.models import User

    @login_manager.request_loader
    def load_user_from_request(request):

        # first, try to login using the api_key url arg
        api_key = request.args.get('key')
        if api_key:
            user = User.query.filter_by(api_key=api_key).first()
            if user:
                return user

        # next, try to login using Basic Auth
        api_key = request.headers.get('Authorization')
        if api_key:
            api_key = api_key.replace('Basic ', '', 1)
            try:
                api_key = base64.b64decode(api_key)
            except TypeError:
                pass
            user = User.query.filter_by(api_key=api_key).first()
            if user:
                return user

        # finally, return None if both methods did not login the user
        return None
else:
    class AnonymousUser(AnonymousUserMixin):
        def can(self, _):
            return False

        def is_admin(self):
            return False

    from .main import clust as cluster_blueprint
    app.register_blueprint(cluster_blueprint)

    login_manager.anonymous_user = AnonymousUser
    
    @login_manager.user_loader
    def load_user(user_id):
        return None
