import os


class Config(object):
    """
    Common configuration
    """

    BABEL_DEFAULT_LOCALE = 'pl'
    ITEMS_PER_PAGE = 20
    MAX_FILENAME_LENGTH = 100
    MEDIA_DIR = os.path.join(os.getcwd(), 'media')
    UPLOAD_DIR = os.path.join(os.getcwd(), 'upload')


class Development(Config):
    """
    Development configuration
    """

    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class Production(Config):
    """
    Production configuration
    """

    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app_config = {
    'development': Development,
    'production': Production,
}
