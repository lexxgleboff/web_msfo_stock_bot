from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
# для миграций б.д.
from flask_migrate import Migrate
# адмминка
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from flask_babelex import Babel


app = Flask(__name__)
app.config.from_object(Configuration)
data_base = SQLAlchemy(app)
babel = Babel(app)
# создал объект класса Migrate в качестве параметров app и data_base для их корреяции
migrate = Migrate(app, data_base)

# Админка
from models import *
# создан экземпляр класса Admin
admin = Admin(app)
# таким образом можно добавить управление любыми данными
admin.add_view(ModelView(Records, data_base.session, name='Таблица МСФО'))

# локализация админки
@babel.localeselector
def get_locale():
        # Put your logic here. Application can store locale in
        # user profile, cookie, session, etc.
        return 'ru'