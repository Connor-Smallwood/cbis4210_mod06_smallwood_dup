from flask import Flask
from .db_connect import close_db, get_db
app = Flask(__name__)

app.secret_key = 'secret_key'

# Register blueprints
from app.blueprints.sales import sales_bp

app.register_blueprint(sales_bp)


from app import routes