from flask import Flask
from .db_connect import close_db, get_db
app = Flask(__name__)

app.secret_key = 'secret_key'

# Register blueprints
from app.blueprints.movies import movies
from app.blueprints.genres import genres

app.register_blueprint(movies)
app.register_blueprint(genres)

from app import routes