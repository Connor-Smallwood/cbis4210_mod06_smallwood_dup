from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db_connect import get_db
import pandas as pd

sales_bp = Blueprint('sales', __name__)


@sales_bp.route('/show_sales')
def show_sales():
    connection = get_db()
    query = """
    SELECT s.sales_id, s.product_name, s.quantity, s.price, s.sale_amount, s.sale_date, r.region_name
    FROM sales_data s
    LEFT JOIN sales_region sr ON s.sales_id = sr.sales_id
    LEFT JOIN regions r ON sr.region_id = r.region_id
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    df = pd.DataFrame(result)
    if not df.empty:
        # Rename columns to be more user-friendly
        df.rename(columns=lambda x: x.replace('_', ' ').title(), inplace=True)
    if not df.empty:
        # Update the Pandas DataFrame to include Edit and Delete buttons
        df['Actions'] = df['sales_id'].apply(lambda id:
            f'<a href="{url_for("sales.edit_sales_data", sales_id=id)}" class="btn btn-sm btn-info">Edit</a> '
            f'<form action="{url_for("sales.delete_sales_data", sales_id=id)}" method="post" style="display:inline;">'
            f'<button type="submit" class="btn btn-sm btn-danger">Delete</button></form>'
        )
    table_html = df.to_html(classes='dataframe table table-striped table-bordered', index=False, header=True, escape=False, justify='left', border=0)

    return render_template("sales_data.html", table=table_html)


# Route to render the add sales data form
@sales_bp.route('/add_sales_data', methods=['GET', 'POST'])
def add_sales_data():
    connection = get_db()
    if request.method == 'POST':
        product_name = request.form['product_name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        sale_date = request.form['sale_date']
        region_id = int(request.form['region_id'])

        # Insert into sales_data
        query_sales_data = "INSERT INTO sales_data (product_name, quantity, price, sale_date) VALUES (%s, %s, %s, %s)"
        with connection.cursor() as cursor:
            cursor.execute(query_sales_data, (product_name, quantity, price, sale_date))
            sales_id = cursor.lastrowid

        # Insert into sales_region
        query_sales_region = "INSERT INTO sales_region (sales_id, region_id) VALUES (%s, %s)"
        with connection.cursor() as cursor:
            cursor.execute(query_sales_region, (sales_id, region_id))
        connection.commit()
        flash("New sales data added successfully!", "success")
        return redirect(url_for('sales.show_sales'))

    # Fetch all regions for the dropdown
    query_regions = "SELECT * FROM regions"
    with connection.cursor() as cursor:
        cursor.execute(query_regions)
        regions = cursor.fetchall()

    return render_template("add_sales_data.html", regions=regions)


# Route to handle updating a row
@sales_bp.route('/edit_sales_data/<int:sales_id>', methods=['GET', 'POST'])
def edit_sales_data(sales_id):
    connection = get_db()
    if request.method == 'POST':
        product_name = request.form['product_name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        sale_date = request.form['sale_date']
        region_id = int(request.form['region_id'])

        # Update sales_data
        query_sales_data = "UPDATE sales_data SET product_name = %s, quantity = %s, price = %s, sale_date = %s WHERE sales_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query_sales_data, (product_name, quantity, price, sale_date, sales_id))

        # Update sales_region
        query_sales_region = "UPDATE sales_region SET region_id = %s WHERE sales_id = %s"
        with connection.cursor() as cursor:
            cursor.execute(query_sales_region, (region_id, sales_id))
        connection.commit()
        flash("Sales data updated successfully!", "success")
        return redirect(url_for('sales.show_sales'))

    # Fetch the current data to pre-populate the form
    query_sales = """
    SELECT s.sales_id, s.product_name, s.quantity, s.price, s.sale_date, r.region_id
    FROM sales_data s
    LEFT JOIN sales_region sr ON s.sales_id = sr.sales_id
    LEFT JOIN regions r ON sr.region_id = r.region_id
    WHERE s.sales_id = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(query_sales, (sales_id,))
        sales_data = cursor.fetchone()

    # Fetch all regions for the dropdown
    query_regions = "SELECT * FROM regions"
    with connection.cursor() as cursor:
        cursor.execute(query_regions)
        regions = cursor.fetchall()

    return render_template("edit_sales_data.html", sales_data=sales_data, regions=regions)


# Route to handle deleting a row
@sales_bp.route('/delete_sales_data/<int:sales_id>', methods=['POST'])
def delete_sales_data(sales_id):
    connection = get_db()
    query_sales_region = "DELETE FROM sales_region WHERE sales_id = %s"
    query_sales_data = "DELETE FROM sales_data WHERE sales_id = %s"
    with connection.cursor() as cursor:
        cursor.execute(query_sales_region, (sales_id,))
        cursor.execute(query_sales_data, (sales_id,))
    connection.commit()
    flash("Sales data deleted successfully!", "success")
    return redirect(url_for('sales.show_sales'))
