import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

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

def fetch_data(cursor, query):
    """
    Execute a query using the given cursor and return fetched data.
    :param cursor: Database cursor to execute the query
    :param query: SQL query to execute
    :return: Fetched data from the database
    """
    cursor.execute(query)
    return cursor.fetchall()

def create_dataframe(data, columns=None):
    """
    Create a pandas DataFrame from the provided data.
    :param data: Data to be loaded into the DataFrame
    :param columns: Optional columns for empty DataFrame
    :return: pandas DataFrame
    """
    if not data and columns:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(data)

def generate_pie_chart(df, values_column, labels_column, title):
    """
    Generate a pie chart from the given DataFrame and return it as a base64 encoded string.
    :param df: pandas DataFrame containing the data
    :param values_column: Column containing values for the pie chart
    :param labels_column: Column containing labels for the pie chart
    :param title: Title of the pie chart
    :return: Base64 encoded string of the pie chart image
    """
    plt.figure(figsize=(10, 6))
    plt.pie(df[values_column], labels=df[labels_column], autopct='%1.1f%%', startangle=140)
    plt.title(title)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

def generate_bar_chart(df, x_column, y_column, title, xlabel, ylabel, color='skyblue', rotation=45):
    """
    Generate a bar chart from the given DataFrame and return it as a base64 encoded string.
    :param df: pandas DataFrame containing the data
    :param x_column: Column containing x-axis values
    :param y_column: Column containing y-axis values
    :param title: Title of the bar chart
    :param xlabel: Label for x-axis
    :param ylabel: Label for y-axis
    :param color: Color of the bars
    :param rotation: Rotation angle for x-axis labels
    :return: Base64 encoded string of the bar chart image
    """
    plt.figure(figsize=(10, 6))
    plt.bar(df[x_column], df[y_column], color=color)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(rotation=rotation)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url
