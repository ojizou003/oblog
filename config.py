import os

class Config:
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'default_db_name')
    DB_USER = os.environ.get('DB_USER', 'default_user')
    DB_PASS = os.environ.get('DB_PASS', 'default_password')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')

    # CKEditorのグローバル設定
    CKEDITOR_HEIGHT =400
    # 警告を無効化
    CKEDITOR_ENABLE_CODESNIPPET = True
    CKEDITOR_CODE_THEME = 'monokai_sublime'
    CKEDITOR_EXTRA_PLUGINS = ['codesnippet']
    CKEDITOR_DISABLE_SECURITY_WARNING = True

    UPLOAD_FOLDER = 'static/img/'

    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')

    @staticmethod
    def get_database_url():
        return f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASS}@{Config.DB_HOST}/{Config.DB_NAME}"