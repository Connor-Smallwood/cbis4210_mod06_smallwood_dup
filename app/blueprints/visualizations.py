from flask import Blueprint, render_template, Response
from app.db_connect import get_db
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

visualizations_bp = Blueprint('visualizations', __name__)

@visualizations_bp.route('/visualizations')
def visualizations():
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    # Fetch data from the database for Pie Chart
    cursor.execute('''
        SELECT r.region_name, SUM(s.sale_amount) AS total_sales
        FROM sales_data s
        LEFT JOIN sales_region sr ON s.sales_id = sr.sales_id
        LEFT JOIN regions r ON sr.region_id = r.region_id
        GROUP BY r.region_name
    ''')
    sales_data_pie = cursor.fetchall()

    # Load data into a Pandas DataFrame for Pie Chart
    df_pie = pd.DataFrame(sales_data_pie)

    # Plotting the pie chart using Matplotlib
    plt.figure(figsize=(10, 6))
    plt.pie(df_pie['total_sales'], labels=df_pie['region_name'], autopct='%1.1f%%', startangle=140)
    plt.title('Total Sales per Region')

    # Convert plot to PNG image and encode to base64
    img_pie = io.BytesIO()
    plt.savefig(img_pie, format='png')
    img_pie.seek(0)
    plot_url_pie_chart = base64.b64encode(img_pie.getvalue()).decode()
    plt.close()

    # Fetch data from the database for Bar Chart
    cursor.execute('''
        SELECT s.product_name, SUM(s.quantity) AS total_quantity
        FROM sales_data s
        GROUP BY s.product_name
    ''')
    sales_data_bar = cursor.fetchall()

    # Load data into a Pandas DataFrame for Bar Chart
    df_bar = pd.DataFrame(sales_data_bar)

    # Plotting the bar chart using Matplotlib
    plt.figure(figsize=(10, 6))
    plt.bar(df_bar['product_name'], df_bar['total_quantity'], color='skyblue')
    plt.xlabel('Product Name')
    plt.ylabel('Total Quantity Sold')
    plt.title('Total Quantity Sold per Product')
    plt.xticks(rotation=45)

    # Convert plot to PNG image and encode to base64
    img_bar = io.BytesIO()
    plt.savefig(img_bar, format='png')
    img_bar.seek(0)
    plot_url_bar_chart = base64.b64encode(img_bar.getvalue()).decode()
    plt.close()

    # Fetch data from the database for Monthly Sales Summary Bar Chart
    cursor.execute('''
        SELECT DATE_FORMAT(s.sale_date, '%Y-%m') AS month, SUM(s.sale_amount) AS total_sales
        FROM sales_data s
        GROUP BY month
        ORDER BY month
    ''')
    sales_data_monthly = cursor.fetchall()

    # Load data into a Pandas DataFrame for Monthly Sales Summary Bar Chart
    df_monthly = pd.DataFrame(sales_data_monthly)

    # Plotting the monthly sales bar chart using Matplotlib
    plt.figure(figsize=(10, 6))
    plt.bar(df_monthly['month'], df_monthly['total_sales'], color='lightgreen')
    plt.xlabel('Month')
    plt.ylabel('Total Sales')
    plt.title('Monthly Sales Summary')
    plt.xticks(rotation=45)

    # Convert plot to PNG image and encode to base64
    img_monthly = io.BytesIO()
    plt.savefig(img_monthly, format='png')
    img_monthly.seek(0)
    plot_url_monthly_bar_chart = base64.b64encode(img_monthly.getvalue()).decode()
    plt.close()

    return render_template('visualizations.html', plot_url_pie_chart=plot_url_pie_chart, plot_url_bar_chart=plot_url_bar_chart, plot_url_monthly_bar_chart=plot_url_monthly_bar_chart)
