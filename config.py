import os, secrets

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    APP_NAME = os.environ.get('APP_NAME', 'CATHAI')
    STAND_ALONE = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'data.sqlite'))
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    assert os.environ.get('DATA_DIR'), 'DATA_DIR IS NOT SET!'
    DATA_DIR = os.environ.get('DATA_DIR', '')


class StandAloneConfig(Config):
    STAND_ALONE = True
    
    def __init__(self):
        self.SECRET_KEY = secrets.token_hex(32)
        print('Running in stand-alone mode. Generating one-time secret key.')


class MultiUserConfig(Config):
    SECRET_KEY=os.environ.get('SECRET_KEY', '')

    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', '')
    MAIL_PORT = os.environ.get('MAIL_PORT', 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True)
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', False)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', '')

    # Celery Redis config
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost')
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost')

    # Analytics
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', '')

    # Admin account
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')
    EMAIL_SUBJECT_PREFIX = '[{}]'.format(Config.APP_NAME)
    EMAIL_SENDER = '{app_name} <{email}>'.format(
        app_name=Config.APP_NAME, email=MAIL_SENDER)

    def __init__(self):
        print("Running in multi-user mode.")
        assert os.environ.get('SECRET_KEY'), 'SECRET_KEY IS NOT SET!'


config = {
    'standalone': StandAloneConfig,
    'multiuser': MultiUserConfig,
}
