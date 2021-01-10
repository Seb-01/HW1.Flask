import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # postgresql://user:pass@localhost:5432/my_db
    SQLALCHEMY_DATABASE_URI = 'postgresql://Seb:seb_user_postGR67@localhost:5432/flask_hw'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SALT = 'my_sJHLHLHKLаваыпuper_s!alt_#4$4344'

    JSON_AS_ASCII = False