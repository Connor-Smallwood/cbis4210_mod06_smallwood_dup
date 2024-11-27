from flask import render_template, request, redirect, url_for, flash
import pymysql.cursors  # Ensure you import cursors for DictCursor
from app import app, db_connect, get_db
import pandas as pd


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/sales_data', methods=['GET', 'POST'])
def sales_data():
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        product_name = request.form['product_name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        sale_date = request.form['sale_date']
        region_id = int(request.form['region_id'])

        # Insert into sales_data table
        cursor.execute(
            'INSERT INTO sales_data (product_name, quantity, price, sale_date) VALUES (%s, %s, %s, %s)',
            (product_name, quantity, price, sale_date)
        )
        db.commit()

        # Get the newly inserted sales_id
        sales_id = cursor.lastrowid

        # Insert into sales_region table
        cursor.execute(
            'INSERT INTO sales_region (sales_id, region_id) VALUES (%s, %s)',
            (sales_id, region_id)
        )
        db.commit()

        flash('New sale added successfully!', 'success')
        return redirect(url_for('sales_data'))

    # Fetch all sales data with region info
    cursor.execute('''
        SELECT s.sales_id, s.product_name, s.quantity, s.price, s.sale_amount, s.sale_date, r.region_name
        FROM sales_data s
        LEFT JOIN sales_region sr ON s.sales_id = sr.sales_id
        LEFT JOIN regions r ON sr.region_id = r.region_id
    ''')
    sales = cursor.fetchall()

    # Fetch all regions
    cursor.execute('SELECT * FROM regions')
    regions = cursor.fetchall()

    return render_template('sales_data.html', sales=sales, regions=regions)

@app.route('/sales_data/edit/<int:sales_id>', methods=['GET', 'POST'])
def edit_sale(sales_id):
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        product_name = request.form['product_name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        sale_date = request.form['sale_date']
        region_id = int(request.form['region_id'])

        # Update sale record in sales_data table
        cursor.execute(
            'UPDATE sales_data SET product_name = %s, quantity = %s, price = %s, sale_date = %s WHERE sales_id = %s',
            (product_name, quantity, price, sale_date, sales_id)
        )
        db.commit()

        # Update region in sales_region table
        cursor.execute(
            'UPDATE sales_region SET region_id = %s WHERE sales_id = %s',
            (region_id, sales_id)
        )
        db.commit()

        flash('Sale updated successfully!', 'success')
        return redirect(url_for('sales_data'))

    # Fetch the sale record to edit
    cursor.execute('SELECT * FROM sales_data WHERE sales_id = %s', (sales_id,))
    sale = cursor.fetchone()

    # Fetch all regions for dropdown
    cursor.execute('SELECT * FROM regions')
    regions = cursor.fetchall()

    return render_template('sales_data.html', sales=[sale], regions=regions, edit_sale=True)



@app.route('/sales_data/delete/<int:sales_id>', methods=['POST'])
def delete_sale(sales_id):
    db = get_db()
    cursor = db.cursor()

    # Delete sale record
    cursor.execute('DELETE FROM sales_data WHERE sales_id = %s', (sales_id,))
    db.commit()

    flash('Sale deleted successfully!', 'danger')
    return redirect(url_for('sales_data'))


@app.route('/reports')
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
    else:
        total_sales_per_region = pd.DataFrame(columns=['region_name', 'sale_amount'])

    # Analysis 2: Total Quantity Sold per Product
    if 'product_name' in df.columns and 'quantity' in df.columns:
        total_quantity_per_product = df.groupby('product_name')['quantity'].sum().reset_index()
    else:
        total_quantity_per_product = pd.DataFrame(columns=['product_name', 'quantity'])

    # Analysis 3: Monthly Sales Summary
    if 'sale_date' in df.columns:
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df['month'] = df['sale_date'].dt.to_period('M')
        monthly_sales_summary = df.groupby('month')['sale_amount'].sum().reset_index()
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

@app.route('/visualizations')
def visualizations():
    # Logic to generate and pass visualizations to the template
    return render_template('visualizations.html')


@app.route('/regions', methods=['GET', 'POST'])
def regions():
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        region_name = request.form['region_name']
        description = request.form['description']

        # Insert new region into regions table
        cursor.execute('INSERT INTO regions (region_name, description) VALUES (%s, %s)', (region_name, description))
        db.commit()
        flash('New region added successfully!', 'success')
        return redirect(url_for('regions'))

    # Fetch all regions data
    cursor.execute('SELECT * FROM regions')
    regions = cursor.fetchall()

    return render_template('regions.html', regions=regions)


@app.route('/regions/edit/<int:region_id>', methods=['GET', 'POST'])
def edit_region(region_id):
    db = get_db()
    cursor = db.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        region_name = request.form['region_name']
        description = request.form['description']

        # Update region record
        cursor.execute('UPDATE regions SET region_name = %s, description = %s WHERE region_id = %s',
                       (region_name, description, region_id))
        db.commit()
        flash('Region updated successfully!', 'success')
        return redirect(url_for('regions'))

    # Fetch the region record to edit
    cursor.execute('SELECT * FROM regions WHERE region_id = %s', (region_id,))
    region = cursor.fetchone()

    return render_template('regions.html', regions=region, edit_region=True)


@app.route('/regions/delete/<int:region_id>', methods=['POST'])
def delete_region(region_id):
    db = get_db()
    cursor = db.cursor()

    # Delete region record
    cursor.execute('DELETE FROM regions WHERE region_id = %s', (region_id,))
    db.commit()

    flash('Region deleted successfully!', 'danger')
    return redirect(url_for('regions'))

