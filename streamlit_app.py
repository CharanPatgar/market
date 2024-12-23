import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Set Page Configuration
st.set_page_config(page_title="Marketing Analysis", layout="wide")

# Apply CSS to Remove Padding/Margin
st.markdown(
    """
    <style>
    .main > div {
        padding-top: 0px !important; /* Remove top padding */
        margin-top: 0px !important; /* Remove any margin */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load Data
@st.cache_data
def load_data():
    orders = pd.read_csv("ORDERS.csv")
    order_items = pd.read_csv("ORDER_ITEMS.csv")
    customers = pd.read_csv("CUSTOMERS.csv")
    products = pd.read_csv("PRODUCTS.csv")
    sellers = pd.read_csv("SELLERS.csv")
    payments = pd.read_csv("ORDER_PAYMENTS.csv")
    reviews = pd.read_csv("ORDER_REVIEW_RATINGS.csv")
    geolocation = pd.read_csv("GEO_LOCATION.csv")
    return orders, order_items, customers, products, sellers, payments, reviews, geolocation

orders, order_items, customers, products, sellers, payments, reviews, geolocation = load_data()

# Sidebar Title
st.sidebar.markdown(
    """
    <style>
    .sidebar-title {
        text-align: center;
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
        font-size: 1.5em;
        font-weight: bold;
        color: #333;
        margin-bottom: 20px; /* Add space below the title */
    }
    </style>
    <div class="sidebar-title">
        Marketing Analysis
    </div>
    """,
    unsafe_allow_html=True
)

# Sidebar Filters
st.sidebar.header("Filters")

top_n = st.sidebar.number_input(
    "Enter the number of products to display (from 1 to 71)",
    min_value=1,
    max_value=71,
    value=10,  # Default to showing all products
    step=1,
    help="Enter a number between 1 and 71 to filter the number of products"
)

# Move the region select dropdown to the sidebar
selected_region = st.sidebar.selectbox(
    "Select Region For Revenue Analysis",
    options=sellers['seller_state'].unique(),
    index=0
)

# Merge DataFrames to include required fields 
merged_df = (
    order_items
    .merge(orders, on="order_id")
    .merge(products, on="product_id")
    .merge(customers, on="customer_id")
    .merge(sellers, on="seller_id")
)

# Add a "Region" column based on customer state
merged_df["Region"] = merged_df["customer_state"]

# Calculate revenue for each product-region combination
merged_df["Revenue"] = merged_df["price"]

# Create a sidebar for product selection
product_options = merged_df["product_category_name"].dropna().unique()
selected_product = st.sidebar.selectbox(
    "Select a Product Category Analysis:",
    options=product_options,
    index=0  # Default to the first product
)

# Sidebar Additional Information
st.sidebar.markdown("---")
st.sidebar.markdown("### Dashboard Info")
st.sidebar.text("Explore key metrics and insights")
st.sidebar.text("Use the filters above to refine data.")

# Create a container for the metrics
with st.container():
    # Add a subheading for the section
    st.markdown("<h2 style='margin-top: -70px;'>Overview</h2>", unsafe_allow_html=True)
    
    # CSS Style for Metrics
    metric_style = """
        <style>
        .metric-container {
            display: flex;
            justify-content: space-between;
            margin-top: -20px; /* Adjusted margin to ensure no overlap */
            gap: 20px;
            width: 100%; 
            padding: 0px;
        }
        .metric-box {
            background-color: #f0f0f0;
            border-radius: 8px;
            padding: 5px 15px;
            text-align: center;
            flex: 1;
            box-shadow: 0px 1px 3px rgba(0,0,0,0.1);
        }
        .metric-title {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 5px;
            color: #555;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        </style>
    """
    st.markdown(metric_style, unsafe_allow_html=True)

    # Calculate Metrics
    total_products = products['product_id'].nunique()
    total_revenue = order_items['price'].sum() #+ order_items['freight_value'].sum()
    total_sellers = sellers['seller_id'].nunique()
    total_customers = customers['customer_id'].nunique()
    total_orders = orders['order_id'].nunique() 

    # Display Metrics
    metric_html = f"""
    <div class="metric-container">
        <div class="metric-box">
            <div class="metric-title">Total Products</div>
            <div class="metric-value">{total_products}</div>
        </div>
        <div class="metric-box">
            <div class="metric-title">Total Revenue</div>
            <div class="metric-value">${total_revenue:,.2f}</div>
        </div>
        <div class="metric-box">
            <div class="metric-title">Total Sellers</div>
            <div class="metric-value">{total_sellers}</div>
        </div>
        <div class="metric-box">
            <div class="metric-title">Total Customers</div>
            <div class="metric-value">{total_customers}</div>
        </div>
        <div class="metric-box">
        <div class="metric-title">Total Orders</div>
        <div class="metric-value">{total_orders}</div>
    </div>
    </div>
    """
    st.markdown(metric_html, unsafe_allow_html=True)

# Merge order_items with products to get product names

merged_data = order_items.merge(products, on="product_id")

# Calculate revenue by product category
product_revenue = merged_data.groupby('product_category_name')['price'].sum().reset_index()
product_revenue = product_revenue.sort_values(by='price', ascending=False)


##This is Revenue per region
# Custom CSS for box styling
st.markdown(
    """
    <style>
    .box {
        background-color: #f9f9f9;  /* Light background color */
        border-radius: 10px;       /* Rounded corners */
        padding: 20px;             /* Inner spacing */
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); /* Light box shadow */
        margin-bottom: 20px;       /* Space below the box */
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# Create two columns for side-by-side display
col1, col2 = st.columns(2)


# Display the region select dropdown and the table in col1
with col1:
        # Bar Chart: Product vs Revenue
    st.subheader("Product Analysis")

    # Merge order_items with products to get product names
    merged_data = order_items.merge(products, on="product_id")

    # Calculate revenue by product
    product_revenue = merged_data.groupby('product_category_name')['price'].sum().reset_index()
    product_revenue = product_revenue.sort_values(by='price', ascending=False)

    # User selection for the number of products to display (input box)

    # Filter for top N products if selected
    filtered_product_revenue = product_revenue.head(top_n)

    # Set the title dynamically based on user input
    title = f"Top {top_n} Product Categories by Revenue" if top_n < len(product_revenue) else "All Product Categories by Revenue"

    # Plot bar chart
    fig = px.bar(
        filtered_product_revenue,
        x='product_category_name',
        y='price',
        labels={'product_category_name': 'Product Category', 'price': 'Revenue'},
        title=title,
        color='price',
        color_continuous_scale='Viridis'
    )

    # Update layout for compact display and remove text labels
    fig.update_layout(
        xaxis=dict(
            showticklabels=False  # Hide x-axis labels
        ),
        xaxis_title="Product Category",
        yaxis_title="Revenue",
        xaxis_tickangle=-45,
        height=250,  # Further reduced height
        width=500,   # Reduced width for compactness
        margin=dict(t=20, b=20, l=30, r=30),  # Tight margins
        title=dict(font=dict(size=12)),  # Reduced title font size

    )

    # Remove text labels on the bars
    fig.update_traces(texttemplate=None)

    # Display the chart
    st.plotly_chart(fig, use_container_width=False)  # Disable container width for better fit


    
# Display the chart in col2
with col2:
    # Always show the line chart
    # Display the title for the table
    # Sort region_product_revenue by product category name in alphabetical order
    # Filter orders by region (seller_state)
    
    filtered_sellers = sellers[sellers['seller_state'] == selected_region]
    filtered_orders = order_items[order_items['seller_id'].isin(filtered_sellers['seller_id'])]

    # Merge to get product categories and revenue in the selected region
    region_product_revenue = filtered_orders.merge(products, on="product_id")
    region_product_revenue = region_product_revenue.groupby('product_category_name')['price'].sum().reset_index()
    region_product_revenue = region_product_revenue.sort_values(by='product_category_name', ascending=True)
    
    # Calculate total revenue for the selected region
    total_revenue_region = filtered_orders['price'].sum()

    # Create a line chart to visualize the product categories and their revenue
    fig = px.line(
        region_product_revenue,
        x='product_category_name',
        y='price',
        title=f'Product Categories and Revenue in {selected_region}',
        labels={'product_category_name': 'Product Category', 'price': 'Revenue'},
        markers=True
    )
    # Add annotation for total revenue along the x-axis
    fig.add_annotation(
        text=f"Total Revenue in {selected_region}: ${total_revenue_region:,.2f}",
        x=0.5,  # Centered along the x-axis
        y=1.3,  # Below the x-axis
        xref="paper", yref="paper",  # Position relative to the paper space
        showarrow=False,
        font=dict(size=12, color="black"),  # Adjust font size and color
        align="center",
        bgcolor="rgba(255, 255, 255, 0.8)",  # Semi-transparent background for readability
        borderwidth=1,
        
    )
    # Update layout to hide x-axis labels by default and show them on hover
    fig.update_layout(
        xaxis=dict(
            showticklabels=False,  # Hide x-axis labels by default
        ),
        hovermode='x unified',  # Show product names when hovering over the line
        xaxis_tickangle=-45,
        height=400,
        margin=dict(t=120, b=120),  # Increase bottom margin for better label visibility
    )

    # Display the line chart
    st.plotly_chart(fig, use_container_width=True)

    
# --- New Customers Acquisition Analysis ---
# Create a container for the new customers and review scores visualization

with st.container():
    # --- Process the 'new_customers' data ---
    new_customers = orders[['customer_id', 'order_purchase_timestamp']].copy()
    new_customers = new_customers.drop_duplicates(subset=['customer_id'])

    # Extract Year and Month information
    new_customers['order_month'] = pd.to_datetime(new_customers['order_purchase_timestamp']).dt.month
    new_customers['order_year'] = pd.to_datetime(new_customers['order_purchase_timestamp']).dt.year
    new_customers['Month_Year'] = new_customers['order_year'].astype(str) + "-" + new_customers['order_month'].astype(str)

    # Order the dates for better visualization
    dates = ['2016-9', '2016-10', '2016-12', '2017-1', '2017-2', '2017-3', '2017-4',  '2017-5', 
             '2017-6', '2017-7', '2017-8','2017-9', '2017-10', '2017-11', '2017-12', '2018-1', 
             '2018-2', '2018-3', '2018-4', '2018-5', '2018-6', '2018-7', '2018-8']

    new_customers['Month_Year'] = pd.Categorical(new_customers['Month_Year'], categories=dates, ordered=True)
    new_customers = new_customers.sort_values(by='Month_Year')

    # Count the number of customers per month
    n_Cust_in_every_month = new_customers.groupby("Month_Year")["customer_id"].count().reset_index()

    # Create an interactive plot with Plotly
    fig1 = px.line(n_Cust_in_every_month, x='Month_Year', y='customer_id',
                   labels={'Month_Year': 'Month', 'customer_id': 'New Customers'},
                   markers=True)

    # Customize hover information
    fig1.update_traces(mode='lines+markers', hovertemplate='%{x}: %{y} new customers')

    # Adjust size for ultra-compact display
    fig1.update_layout(width=200, height=200, margin=dict(l=5, r=5, t=0, b=5))

    # --- Frequent Review Scores Visualization ---
    item_counts = reviews['review_score'].value_counts().sort_index()

    # Create a side-by-side layout in Streamlit
    col1, col2 = st.columns(2)

    # Place the New Customers Acquisition plot in the first column
    with col1:
        st.markdown(
            "<h6 style='text-align: center; font-weight: bold; margin-bottom: -20px;margin-top: -80px;'>New Customers</h6>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig1, use_container_width=True)

    # Place the Frequent Review Scores plot in the second column
    with col2:
        st.markdown(
            "<h6 style='text-align: center; font-weight: bold; margin-bottom: 2px; margin-top: -80px;'>Review Scores</h6>",
            unsafe_allow_html=True,
        )

        # Bar chart for frequent review scores using Plotly
        fig2 = px.bar(
            x=item_counts.index,
            y=item_counts.values,
            labels={"x": "Review", "y": "Freq"},
            text=item_counts.values,
            color=item_counts.values,
            color_continuous_scale="Blues",
        )

        # Customize layout for ultra-compact display
        fig2.update_traces(texttemplate='%{text}', textposition='outside', marker_line_width=0.5)
        fig2.update_layout(
            xaxis_title="Score",
            yaxis_title="Freq",
            coloraxis_showscale=False,
            width=200,  # Further reduced width
            height=200,  # Further reduced height
            margin=dict(l=5, r=5, t=0, b=5),
        )

        # Add the Plotly chart to Streamlit
        st.plotly_chart(fig2, use_container_width=True)


####

# Create four columns for displaying the pie charts in a single row

# Create four columns for displaying the pie charts in a single row
col1, col2, col3, col4 = st.columns(4)

# Place the first pie chart (Payment Types) in the first column
with col1:
    st.markdown('<div class="custom-box">', unsafe_allow_html=True)  # Start box
    payment_type_counts = payments['payment_type'].value_counts().reset_index()
    payment_type_counts.columns = ['Payment_Type', 'Count']
    
    fig_payment_type = px.pie(payment_type_counts, 
                              names='Payment_Type', 
                              values='Count', 
                              title='Payment Types',
                              color='Payment_Type', 
                              color_discrete_sequence=px.colors.sequential.Plasma)
    
    fig_payment_type.update_layout(height=300, width=300)
    st.plotly_chart(fig_payment_type, use_container_width=True)

# Place the second pie chart (Delivery Accuracy) in the second column
with col2:
    st.markdown('<div class="custom-box">', unsafe_allow_html=True)  # Start box
    orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'], errors='coerce')
    orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'], errors='coerce')
    
    orders['Delivery Accuracy'] = pd.cut(
        (orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']).dt.days,
        bins=[-float('inf'), -1, 0, float('inf')],
        labels=['Before', 'On Time', 'After']
    )
    
    delivery_accuracy_counts = orders['Delivery Accuracy'].value_counts().reset_index()
    delivery_accuracy_counts.columns = ['Delivery Accuracy', 'Count']
    delivery_accuracy_counts_filtered = delivery_accuracy_counts[delivery_accuracy_counts['Delivery Accuracy'].isin(['Before', 'After'])]
    
    fig_delivery_accuracy = px.pie(delivery_accuracy_counts_filtered, 
                                    names='Delivery Accuracy', 
                                    values='Count', 
                                    title='Delivery Accuracy',
                                    color='Delivery Accuracy', 
                                    color_discrete_sequence=px.colors.sequential.Plasma)
    
    fig_delivery_accuracy.update_layout(height=300, width=300)
    st.plotly_chart(fig_delivery_accuracy, use_container_width=True)

# Place the third pie chart (Seller Segmentation) in the third column
# Place the third doughnut chart (Seller Segmentation) in the third column
with col3:
    st.markdown('<div class="custom-box">', unsafe_allow_html=True)  # Start box
    order_items_payments = pd.merge(order_items, payments, on="order_id", how="inner")
    Supp_Revenue = order_items_payments.groupby(['seller_id']).agg({'payment_value': 'sum'}).reset_index()
    Supp_Revenue = Supp_Revenue[Supp_Revenue['payment_value'] >= 0]
    bins = [0, 100, 400, float('inf')]
    labels = ['Low', 'High', 'Top']
    Supp_Revenue['payment_value_GROUP'] = pd.cut(Supp_Revenue['payment_value'], bins=bins, labels=labels, right=False)
    
    payment_value_counts = Supp_Revenue['payment_value_GROUP'].value_counts().reset_index()
    payment_value_counts.columns = ['Payment Value Group', 'Count']
    
    fig_seller_segmentation = px.pie(payment_value_counts,
                                     names='Payment Value Group',
                                     values='Count',
                                     title='Seller Segmentation',
                                     color='Payment Value Group',
                                     color_discrete_sequence=px.colors.sequential.Plasma)
    
    # Add the hole parameter to convert it into a doughnut chart
    fig_seller_segmentation.update_traces(hole=0.4)
    fig_seller_segmentation.update_layout(height=300, width=300)
    st.plotly_chart(fig_seller_segmentation, use_container_width=True)


# Place the fourth pie chart (Customer Segmentation) in the fourth column
# Place the fourth doughnut chart (Customer Segmentation) in the fourth column
with col4:
    st.markdown('<div class="custom-box">', unsafe_allow_html=True)  # Start box
    Sales_by_product_payments = pd.merge(order_items, payments, on="order_id", how="inner")
    Sales_by_product_payments = pd.merge(Sales_by_product_payments, orders[['order_id', 'customer_id']], on="order_id", how="inner")
    Customer_Revenue = Sales_by_product_payments.groupby(['customer_id']).agg({'payment_value': 'sum'}).reset_index()
    Customer_Revenue = Customer_Revenue[Customer_Revenue['payment_value'] >= 0]
    Customer_Revenue['Payment_Group'] = pd.cut(Customer_Revenue['payment_value'], bins=bins, labels=labels, right=False)
    
    customer_payment_counts = Customer_Revenue['Payment_Group'].value_counts().reset_index()
    customer_payment_counts.columns = ['Payment Group', 'Count']
    
    fig_customer_segmentation = px.pie(customer_payment_counts,
                                       names='Payment Group',
                                       values='Count',
                                       title='Customer Segmentation',
                                       color='Payment Group',
                                       color_discrete_sequence=px.colors.sequential.Plasma)
    
    # Add the hole parameter to convert it into a doughnut chart
    fig_customer_segmentation.update_traces(hole=0.4)
    fig_customer_segmentation.update_layout(height=300, width=300)
    st.plotly_chart(fig_customer_segmentation, use_container_width=True)


###This is top 3 regions that are high in revenue of a particular product
# Filter data for the selected product
filtered_df = merged_df[merged_df["product_category_name"] == selected_product]

# Group by Region and calculate total revenue
region_revenue = (
    filtered_df.groupby("Region")["Revenue"].sum()
    .reset_index()
    .sort_values(by="Revenue", ascending=False)
)

# Get top 3 regions
top_regions = region_revenue.head(3)

# --- Top 3 Sellers ---
# Aggregate payment values by seller (from 'order_items_payments')
top_sellers = order_items_payments.groupby('seller_id')['payment_value'].sum().reset_index()

# Sort sellers by payment value in descending order
top_sellers_sorted = top_sellers.sort_values(by='payment_value', ascending=False).head(3)

# Merge with the sellers dataframe to get seller's city or state (instead of 'seller_name')
top_sellers_sorted = top_sellers_sorted.merge(sellers[['seller_id', 'seller_city', 'seller_state']], on='seller_id', how='left')

# --- Top 3 Customers ---
# Aggregate payment values by customer (from 'Sales_by_product_payments')
top_customers = Sales_by_product_payments.groupby('customer_id')['payment_value'].sum().reset_index()

# Sort customers by payment value in descending order
top_customers_sorted = top_customers.sort_values(by='payment_value', ascending=False).head(3)

# Merge with the customers dataframe to get customer names (optional)
top_customers_sorted = top_customers_sorted.merge(customers[['customer_id', 'customer_city', 'customer_state']], on='customer_id', how='left')


# --- Compute Metrics for Selected Product ---
average_rating = reviews.merge(order_items, on="order_id") \
                        .merge(products, on="product_id") \
                        .query("product_category_name == @selected_product")["review_score"].mean()

average_price = merged_df[merged_df["product_category_name"] == selected_product]["price"].mean()
total_revenue = merged_df[merged_df["product_category_name"] == selected_product]["Revenue"].sum()

# Display results and graphs side by side
col1, col2, col3 = st.columns([4,2,2])

# --- Column 1: Top 3 Regions by Revenue ---
with col1:
    fig = px.bar(
        top_regions,
        x="Region",
        y="Revenue",
        title=f"Top 3 Regions by Revenue for Product Category: {selected_product}",
        labels={"Revenue": "Revenue ($)", "Region": "Region"},
        color="Region",
        height=350  # Adjusted height
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
    
# --- Column 2: Metric Cards ---
with col2:
    st.markdown("#####  Product Metrics")
    st.metric(label="Average Rating", value=f"{average_rating:.2f}")
    st.metric(label="Average Price", value=f"${average_price:,.2f}")
    st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")

# --- Column 3: Top 3 Sellers and Customers ---
with col3:
    # Top 3 Sellers by Revenue
    fig_sellers = px.bar(
        top_sellers_sorted,
        x="payment_value",
        y="seller_id",
        orientation="h",
        color="seller_state",
        text="payment_value",  # Show the revenue inside the bar
        labels={"payment_value": "Revenue", "seller_state": "State"},
        title="Top 3 Sellers by Revenue",
    )
    fig_sellers.update_traces(texttemplate='%{text:.2s}', textposition='inside')
    fig_sellers.update_layout(
        yaxis=dict(title="", showticklabels=False),  # Remove y-axis title to save space
        xaxis=dict(title="Revenue"),
        height=180,  # Reduced height
        margin=dict(l=50, r=50, t=30, b=30),  # Adjusted margins
        showlegend=False,  # Hide legend if not necessary
    )
    st.plotly_chart(fig_sellers, use_container_width=True)

    # Top 3 Customers by Revenue
    fig_customers = px.bar(
        top_customers_sorted,
        x="payment_value",
        y="customer_id",
        orientation="h",
        color="customer_state",
        text="payment_value",  # Show the revenue inside the bar
        labels={"payment_value": "Revenue", "customer_state": "State"},
        title="Top 3 Customers by Revenue",
    )
    fig_customers.update_traces(texttemplate='%{text:.2s}', textposition='inside')
    fig_customers.update_layout(
        yaxis=dict(title="", showticklabels=False),  # Remove y-axis title to save space
        xaxis=dict(title="Revenue"),
        height=180,  # Reduced height
        margin=dict(l=50, r=50, t=30, b=30),  # Adjusted margins
        showlegend=False,  # Hide legend if not necessary
    )
    st.plotly_chart(fig_customers, use_container_width=True)
    
 ### This is heatnap and Top 3 customers and sellers   
# --- Data Preparation ---
# Merging Customers and Orders to get state information
customers_orders = pd.merge(customers, orders, on="customer_id", how="inner")

# Add 'Purchased_Year' column to extract the year of purchase
customers_orders["Purchased_Year"] = pd.to_datetime(customers_orders["order_purchase_timestamp"]).dt.year

# Calculate the number of unique orders per state
Ordered_State = customers_orders.groupby(['customer_state']).agg({'order_id': 'nunique'}).reset_index()

# Sort by the number of orders and select the top 10 states
Ordered_State = Ordered_State.sort_values(by='order_id', ascending=False).head(10)

# Filter data to only include the top 10 states
filtered_data = customers_orders[customers_orders['customer_state'].isin(Ordered_State['customer_state'])]

# Group data by state and year to calculate yearly orders
yearly_State_orders = filtered_data.groupby(['customer_state', 'Purchased_Year']).agg({'order_id': 'nunique'}).reset_index()

# Pivot the data to create a table where rows are states and columns are years
yearly_State_orders = yearly_State_orders.pivot(index='customer_state', columns='Purchased_Year', values='order_id').fillna(0)

# --- Data Preparation for Order Status Analysis ---

# Merge order_items with orders to get order status
#order_status_data = pd.merge(order_items, orders, on="order_id", how="inner")

# Now, merge the above with PRODUCTS to get product_category_name
#order_status_data = pd.merge(order_status_data, products[['product_id', 'product_category_name']], on='product_id', how='left')

# Calculate order status counts for each product category
#order_status_counts = order_status_data.groupby(['product_category_name', 'order_status']).size().reset_index(name='count')

# Calculate the total orders for each product category
#total_orders_per_category = order_status_data.groupby('product_category_name')['order_id'].nunique().reset_index(name='total_orders')

# Merge the total orders with the status counts to get the percentages
#order_status_counts = pd.merge(order_status_counts, total_orders_per_category, on='product_category_name')

# Calculate the percentage of each order status for each product category
#order_status_counts['percentage'] = (order_status_counts['count'] / order_status_counts['total_orders']) * 100

# Filter data to focus on specific order statuses: Delivered, Canceled, In Transit
#order_status_pie_data = order_status_counts[order_status_counts['order_status'].isin(['delivered', 'canceled', 'in_transit'])]

# --- Pie Chart Visualization ---
# Group by order status to get the total percentage for the entire dataset
#status_summary = order_status_pie_data.groupby('order_status')['percentage'].sum().reset_index()

# Plotting the pie chart
#fig, ax = plt.subplots()
#ax.pie(status_summary['percentage'], labels=status_summary['order_status'], autopct='%1.1f%%', startangle=90, colors=['#66b3ff','#99ff99','#ff6666'])
#ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.

# Layout for displaying everything in one row
col1, col2 = st.columns([3, 4])

with col1:
    # Displaying the heatmap
    st.markdown("#### Yearly Orders per Top 10 States")
    styled_table = yearly_State_orders.style.background_gradient(cmap="coolwarm")
    st.dataframe(styled_table)

#with col2:
    # Displaying the order status analysis pie chart
    #st.markdown("#### Order Status Analysis (Percentage by Product Category)")
    #st.pyplot(fig)
