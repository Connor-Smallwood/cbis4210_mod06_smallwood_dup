from flask import Blueprint, render_template
from app.db_connect import get_db
import pymysql
import pandas as pd

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
def reports():
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    # Fetch data from the database
    cursor.execute('''
        SELECT s.sales_id, s.product_name, s.quantity, s.price, s.sale_amount, s.sale_date, r.region_name
        FROM sales_data s
        LEFT JOIN sales_region sr ON s.sales_id = sr.sales_id
        LEFT JOIN regions r ON sr.region_id = r.region_id
    ''')
    sales_data = cursor.fetchall()

    # Load data into a Pandas DataFrame
    df = pd.DataFrame(sales_data)

    # If there are no records, create an empty DataFrame with expected columns
    if df.empty:
        df = pd.DataFrame(columns=['sales_id', 'product_name', 'quantity', 'price', 'sale_amount', 'sale_date', 'region_name'])

    # Analysis 1: Total Sales per Region
    if 'region_name' in df.columns and 'sale_amount' in df.columns:
        total_sales_per_region = df.groupby('region_name')['sale_amount'].sum().reset_index()
        total_sales_per_region.rename(columns=lambda x: x.replace('_', ' ').title(), inplace=True)
    else:
        total_sales_per_region = pd.DataFrame(columns=['region_name', 'sale_amount'])

    # Analysis 2: Total Quantity Sold per Product
    if 'product_name' in df.columns and 'quantity' in df.columns:
        total_quantity_per_product = df.groupby('product_name')['quantity'].sum().reset_index()
        total_quantity_per_product.rename(columns=lambda x: x.replace('_', ' ').title(), inplace=True)
    else:
        total_quantity_per_product = pd.DataFrame(columns=['product_name', 'quantity'])

    # Analysis 3: Monthly Sales Summary
    if 'sale_date' in df.columns:
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df['month'] = df['sale_date'].dt.to_period('M')
        monthly_sales_summary = df.groupby('month')['sale_amount'].sum().reset_index()
        monthly_sales_summary.rename(columns=lambda x: x.replace('_', ' ').title(), inplace=True)
    else:
        monthly_sales_summary = pd.DataFrame(columns=['month', 'sale_amount'])

    # Convert DataFrames to HTML
    total_sales_per_region_html = total_sales_per_region.to_html(classes='table table-striped', index=False)
    total_quantity_per_product_html = total_quantity_per_product.to_html(classes='table table-striped', index=False)
    monthly_sales_summary_html = monthly_sales_summary.to_html(classes='table table-striped', index=False)

    # Render template with analysis results
    return render_template('reports.html',
                           total_sales_per_region=total_sales_per_region_html,
                           total_quantity_per_product=total_quantity_per_product_html,
                           monthly_sales_summary=monthly_sales_summary_html)
