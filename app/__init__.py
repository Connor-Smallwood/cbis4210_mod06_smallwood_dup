from flask import Flask
from .db_connect import close_db, get_db
app = Flask(__name__)

app.secret_key = 'secret_key'

# Register blueprints
from app.blueprints.sales import sales_bp
from app.blueprints.reports import reports_bp
from app.blueprints.visualizations import visualizations_bp

app.register_blueprint(sales_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(visualizations_bp)

from app import routes