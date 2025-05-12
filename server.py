from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

# Load CSV data
DATA_PATH = 'sales_data_sample.csv'
df = pd.read_csv(DATA_PATH, encoding='ISO-8859-1')

# Convert ORDERDATE to datetime for easier filtering
df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], errors='coerce')

# Create year-month field for grouping
df['YEAR_MONTH'] = df['ORDERDATE'].dt.strftime('%Y-%m')

def filter_data(start_date=None, end_date=None, country=None, status=None, customer=None):
    """Filter the dataframe based on provided parameters"""
    filtered = df.copy()
    
    if start_date:
        start_date = pd.to_datetime(start_date)
        filtered = filtered[filtered['ORDERDATE'] >= start_date]
    
    if end_date:
        end_date = pd.to_datetime(end_date)
        filtered = filtered[filtered['ORDERDATE'] <= end_date]
    
    if country and country != '':
        filtered = filtered[filtered['COUNTRY'] == country]
    
    if status and status != '':
        filtered = filtered[filtered['STATUS'] == status]
    
    if customer and customer != '':
        filtered = filtered[filtered['CUSTOMERNAME'].str.contains(customer, case=False)]
    
    return filtered

@app.route('/')
def dashboard():
    # Get unique values for filters
    countries = sorted(df['COUNTRY'].dropna().unique())
    statuses = sorted(df['STATUS'].dropna().unique())
    
    return render_template('dashboard.html', countries=countries, statuses=statuses)

@app.route('/api/sales_by_month')
def sales_by_month():
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    country = request.args.get('country')
    status = request.args.get('status')
    customer = request.args.get('customer')
    
    # Apply filters
    filtered_df = filter_data(start_date, end_date, country, status, customer)
    
    # Group by year and month
    data = filtered_df.groupby(['YEAR_ID', 'MONTH_ID'])['SALES'].sum().reset_index()
    data['label'] = data['MONTH_ID'].astype(str) + '/' + data['YEAR_ID'].astype(str)
    
    # Sort by date
    data = data.sort_values(by=['YEAR_ID', 'MONTH_ID'])
    
    return jsonify({
        'labels': data['label'].tolist(),
        'values': data['SALES'].round(2).tolist()
    })

@app.route('/api/sales_by_productline')
def sales_by_productline():
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    country = request.args.get('country')
    status = request.args.get('status')
    customer = request.args.get('customer')
    
    # Apply filters
    filtered_df = filter_data(start_date, end_date, country, status, customer)
    
    # Group by product line
    data = filtered_df.groupby('PRODUCTLINE')['SALES'].sum().reset_index()
    data = data.sort_values(by='SALES', ascending=False)
    
    return jsonify({
        'labels': data['PRODUCTLINE'].tolist(),
        'values': data['SALES'].round(2).tolist()
    })

@app.route('/api/sales_by_country')
def sales_by_country():
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    country = request.args.get('country')
    status = request.args.get('status')
    customer = request.args.get('customer')
    
    # Apply filters
    filtered_df = filter_data(start_date, end_date, country, status, customer)
    
    # Group by country
    data = filtered_df.groupby('COUNTRY')['SALES'].sum().reset_index()
    
    return jsonify({
        'labels': data['COUNTRY'].tolist(),
        'values': data['SALES'].round(2).tolist()
    })

@app.route('/api/status_distribution')
def status_distribution():
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    country = request.args.get('country')
    status = request.args.get('status')
    customer = request.args.get('customer')
    
    # Apply filters
    filtered_df = filter_data(start_date, end_date, country, status, customer)
    
    # Count by status
    data = filtered_df['STATUS'].value_counts().reset_index()
    print(130,data)
    return jsonify({
        'labels': data['STATUS'].tolist(),
        'values': data['count'].tolist()
    })

@app.route('/api/top_customers')
def top_customers():
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    country = request.args.get('country')
    status = request.args.get('status')
    customer = request.args.get('customer')
    
    # Apply filters
    filtered_df = filter_data(start_date, end_date, country, status, customer)
    
    # Group by customer and calculate total sales
    data = filtered_df.groupby('CUSTOMERNAME')['SALES'].sum().reset_index()
    
    # Sort by sales and take top 10
    data = data.sort_values(by='SALES', ascending=False).head(10)
    
    return jsonify({
        'labels': data['CUSTOMERNAME'].tolist(),
        'values': data['SALES'].round(2).tolist()
    })

@app.route('/api/deal_size_distribution')
def deal_size_distribution():
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    country = request.args.get('country')
    status = request.args.get('status')
    customer = request.args.get('customer')
    
    # Apply filters
    filtered_df = filter_data(start_date, end_date, country, status, customer)
    
    # Count by deal size
    data = filtered_df['DEALSIZE'].value_counts().reset_index()
    print(data)
    
    return jsonify({
        'labels': data['DEALSIZE'].tolist(),
        'values': data['count'].tolist()
    })

@app.route('/api/price_quantity_analysis')
def price_quantity_analysis():
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    country = request.args.get('country')
    status = request.args.get('status')
    customer = request.args.get('customer')
    
    # Apply filters
    filtered_df = filter_data(start_date, end_date, country, status, customer)
    
    # Sample data for scatter plot (limit to 100 points for performance)
    sample_size = min(100, len(filtered_df))
    if sample_size < len(filtered_df):
        sampled = filtered_df.sample(sample_size)
    else:
        sampled = filtered_df
    
    # Create data structure for scatter plot
    data = []
    for _, row in sampled.iterrows():
        data.append({
            'x': float(row['QUANTITYORDERED']),
            'y': float(row['PRICEEACH']),
            'z': float(row['SALES']),  # For bubble size
            'name': f"Order {row['ORDERNUMBER']}",
            'productLine': row['PRODUCTLINE'],
            'productCode': row['PRODUCTCODE']
        })
    
    return jsonify(data)

@app.route('/api/sales_trend')
def sales_trend():
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    country = request.args.get('country')
    status = request.args.get('status')
    customer = request.args.get('customer')
    
    # Apply filters
    filtered_df = filter_data(start_date, end_date, country, status, customer)
    
    # Group by date
    filtered_df['DATE'] = filtered_df['ORDERDATE'].dt.date
    data = filtered_df.groupby('DATE')['SALES'].sum().reset_index()
    
    # Sort by date
    data = data.sort_values(by='DATE')
    
    return jsonify({
        'dates': [d.strftime('%Y-%m-%d') for d in data['DATE']],
        'values': data['SALES'].round(2).tolist()
    })

@app.route('/api/monthly_product_sales')
def monthly_product_sales():
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    country = request.args.get('country')
    status = request.args.get('status')
    customer = request.args.get('customer')
    
    # Apply filters
    filtered_df = filter_data(start_date, end_date, country, status, customer)
    
    # Group by year-month and product line
    data = filtered_df.pivot_table(
        index=['YEAR_ID', 'MONTH_ID'],
        columns='PRODUCTLINE',
        values='SALES',
        aggfunc='sum'
    ).reset_index().fillna(0)
    
    # Create month labels
    data['label'] = data['MONTH_ID'].astype(str) + '/' + data['YEAR_ID'].astype(str)
    
    # Sort by date
    data = data.sort_values(by=['YEAR_ID', 'MONTH_ID'])
    
    # Get product lines
    product_lines = filtered_df['PRODUCTLINE'].unique().tolist()
    
    # Prepare series data
    series = []
    for product_line in product_lines:
        if product_line in data.columns:
            series.append({
                'name': product_line,
                'data': data[product_line].round(2).tolist()
            })
    
    return jsonify({
        'categories': data['label'].tolist(),
        'series': series
    })

@app.route('/api/summary_metrics')
def summary_metrics():
    # Get filter parameters from request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    country = request.args.get('country')
    status = request.args.get('status')
    customer = request.args.get('customer')
    
    # Apply filters
    filtered_df = filter_data(start_date, end_date, country, status, customer)
    
    # Calculate summary metrics
    total_sales = filtered_df['SALES'].sum()
    total_orders = filtered_df['ORDERNUMBER'].nunique()
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    product_lines_count = filtered_df['PRODUCTLINE'].nunique()
    
    # Previous period for comparison (use half the date range)
    if start_date and end_date:
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        date_range = (end - start).days
        prev_end = start - datetime.timedelta(days=1)
        prev_start = prev_end - datetime.timedelta(days=date_range)
        
        prev_filtered = filter_data(
            prev_start.strftime('%Y-%m-%d'), 
            prev_end.strftime('%Y-%m-%d'), 
            country, status, customer
        )
        
        prev_sales = prev_filtered['SALES'].sum()
        prev_orders = prev_filtered['ORDERNUMBER'].nunique()
        prev_aov = prev_sales / prev_orders if prev_orders > 0 else 0
        
        sales_trend = ((total_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0
        orders_trend = ((total_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0
        aov_trend = ((avg_order_value - prev_aov) / prev_aov * 100) if prev_aov > 0 else 0
    else:
        # Default values if no date range is specified
        sales_trend = 0
        orders_trend = 0
        aov_trend = 0
    
    return jsonify({
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'product_lines_count': product_lines_count,
        'sales_trend': sales_trend,
        'orders_trend': orders_trend,
        'aov_trend': aov_trend
    })

if __name__ == '__main__':
    app.run(debug=True, port=8080)