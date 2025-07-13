import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
import json
from datetime import datetime, timedelta
import numpy as np
import requests
from PIL import Image
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Slushie CFO Assistant",
    page_icon="🍧",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #E74C3C, #3498DB);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #3498DB;
    }
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    
    /* Custom sidebar button styling */
    .stButton > button {
        background: linear-gradient(90deg, #3498DB, #2980B9);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 4px 0;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #2980B9, #3498DB);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Sidebar section headers */
    .sidebar-section {
        color: #2C3E50;
        font-weight: 600;
        margin: 16px 0 8px 0;
        padding: 8px 0;
        border-bottom: 2px solid #E8F4F8;
    }
    
    /* Override Streamlit's default colors for better natural look */
    .stMetric > div > div > div {
        color: #2C3E50 !important;
    }
    
    .stAlert {
        background-color: #F0F8FF !important;
        border-color: #3498DB !important;
    }
    
    .stSuccess {
        background-color: #F0FFF0 !important;
        border-color: #27AE60 !important;
    }
    
    .stError {
        background-color: #FDF2F2 !important;
        border-color: #E74C3C !important;
    }
    
    .stInfo {
        background-color: #F0F8FF !important;
        border-color: #3498DB !important;
    }
</style>
""", unsafe_allow_html=True)

# Show title and description
st.markdown('<div class="main-header"><h1>🍧 Slushie CFO Assistant</h1></div>', unsafe_allow_html=True)
st.write(
    "Your AI-powered CFO assistant for managing your small slushie stand. "
    "Perfect for family-run stands, food trucks, and small operations. "
    "Get insights on deals, analyze consumer data, optimize inventory, and track profits."
)

# Sidebar for navigation
st.sidebar.title("Navigation")

# Clean button-based navigation
if st.sidebar.button("Dashboard", use_container_width=True):
    st.session_state.current_page = "Dashboard"
    st.rerun()

if st.sidebar.button("Deal Finder", use_container_width=True):
    st.session_state.current_page = "Deal Finder"
    st.rerun()

if st.sidebar.button("Data Analysis", use_container_width=True):
    st.session_state.current_page = "Data Analysis"
    st.rerun()

if st.sidebar.button("Inventory", use_container_width=True):
    st.session_state.current_page = "Inventory Recommendations"
    st.rerun()

if st.sidebar.button("Profit Calculator", use_container_width=True):
    st.session_state.current_page = "Profit Calculator"
    st.rerun()

if st.sidebar.button("Live Data & Images", use_container_width=True):
    st.session_state.current_page = "Live Data & Images"
    st.rerun()

if st.sidebar.button("Live Charts", use_container_width=True):
    st.session_state.current_page = "Live Charts"
    st.rerun()

if st.sidebar.button("Chat Assistant", use_container_width=True):
    st.session_state.current_page = "Chat Assistant"
    st.rerun()

# Initialize current page if not set
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

# Get current page
page = st.session_state.current_page

# Initialize OpenAI client
openai_api_key = st.secrets.get("OPENAI_API_KEY")
if not openai_api_key:
    st.error("Please add your OpenAI API key to continue.")
    st.stop()

client = OpenAI(api_key=openai_api_key)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sales_data" not in st.session_state:
    st.session_state.sales_data = []
if "inventory_data" not in st.session_state:
    st.session_state.inventory_data = {
        "Blue Raspberry": 0,
        "Cherry": 0,
        "Lime": 0,
        "Orange": 0,
        "Strawberry": 0,
        "Grape": 0
    }
if "dashboard_metrics" not in st.session_state:
    st.session_state.dashboard_metrics = {
        "total_revenue": 0.0,
        "gross_profit": 0.0,
        "net_profit": 0.0,
        "top_flavor": "None",
        "top_flavor_percentage": 0.0
    }
if "commands_data" not in st.session_state:
    st.session_state.commands_data = {
        "net_profits": 0.0,
        "total_sales": 0,
        "best_day": "None",
        "notes": []
    }
if "venmo_data" not in st.session_state:
    st.session_state.venmo_data = {
        "connected": False,
        "access_token": "",
        "last_sync": None,
        "auto_sync": False,
        "transactions": [],
        "daily_total": 0.0,
        "sync_interval": 5  # minutes
    }
if "custom_charts" not in st.session_state:
    st.session_state.custom_charts = {
        "folders": {
            "Revenue Analysis": {
                "charts": {
                    "Daily Revenue": {
                        "type": "line",
                        "data_source": "sales_data",
                        "x_column": "Date",
                        "y_column": "Revenue",
                        "title": "Daily Revenue Trend",
                        "color": "blue"
                    },
                    "Revenue by Flavor": {
                        "type": "pie",
                        "data_source": "sales_data",
                        "x_column": "Flavor",
                        "y_column": "Revenue",
                        "title": "Revenue by Flavor",
                        "color": "Set3"
                    }
                }
            },
            "Business Metrics": {
                "charts": {
                    "Profit Trends": {
                        "type": "bar",
                        "data_source": "dashboard_metrics",
                        "x_column": "metric",
                        "y_column": "value",
                        "title": "Business Metrics Overview",
                        "color": "green"
                    }
                }
            }
        },
        "active_folder": "Revenue Analysis",
        "active_tab": "All Charts"
    }

# Dashboard Page
if page == "Dashboard":
    st.header("📊 Business Dashboard")
    
    # Editable Dashboard Metrics
    st.subheader("📝 Edit Your Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.session_state.dashboard_metrics["total_revenue"] = st.number_input(
            "Total Revenue ($)", 
            min_value=0.0, 
            value=st.session_state.dashboard_metrics["total_revenue"],
            step=0.01
        )
    with col2:
        st.session_state.dashboard_metrics["gross_profit"] = st.number_input(
            "Gross Profit ($)", 
            min_value=0.0, 
            value=st.session_state.dashboard_metrics["gross_profit"],
            step=0.01
        )
    with col3:
        st.session_state.dashboard_metrics["net_profit"] = st.number_input(
            "Net Profit ($)", 
            min_value=0.0, 
            value=st.session_state.dashboard_metrics["net_profit"],
            step=0.01
        )
    with col4:
        st.session_state.dashboard_metrics["top_flavor"] = st.text_input(
            "Top Flavor", 
            value=st.session_state.dashboard_metrics["top_flavor"]
        )
    with col5:
        st.session_state.dashboard_metrics["top_flavor_percentage"] = st.number_input(
            "Top Flavor %", 
            min_value=0.0, 
            max_value=100.0,
            value=st.session_state.dashboard_metrics["top_flavor_percentage"],
            step=0.1
        )
    
    # Display Metrics
    st.subheader("📊 Current Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", f"${st.session_state.dashboard_metrics['total_revenue']:,.2f}")
    with col2:
        st.metric("Gross Profit", f"${st.session_state.dashboard_metrics['gross_profit']:,.2f}")
    with col3:
        st.metric("Net Profit", f"${st.session_state.dashboard_metrics['net_profit']:,.2f}")
    with col4:
        st.metric("Top Flavor", st.session_state.dashboard_metrics["top_flavor"], f"{st.session_state.dashboard_metrics['top_flavor_percentage']:.1f}% sales")
    
    # Editable Sales Data for Charts
    st.subheader("📈 Edit Sales Data for Charts")
    
    # Add new sales data point
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        new_date = st.date_input("Date")
    with col2:
        new_flavor = st.selectbox("Flavor", ["Blue Raspberry", "Cherry", "Lime", "Orange", "Strawberry", "Grape", "Other"])
    with col3:
        new_quantity = st.number_input("Quantity Sold", min_value=0, value=1)
    with col4:
        new_revenue = st.number_input("Revenue ($)", min_value=0.0, value=0.0, step=0.01)
    
    if st.button("Add Sales Data Point"):
        new_data = {
            "Date": new_date,
            "Flavor": new_flavor,
            "Quantity": new_quantity,
            "Revenue": new_revenue
        }
        st.session_state.sales_data.append(new_data)
        st.success("Data point added!")
    
    # Display and edit existing sales data
    if st.session_state.sales_data:
        st.subheader("📋 Current Sales Data")
        df = pd.DataFrame(st.session_state.sales_data)
        
        # Make the dataframe editable
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Date": st.column_config.DateColumn("Date"),
                "Flavor": st.column_config.SelectboxColumn("Flavor", options=["Blue Raspberry", "Cherry", "Lime", "Orange", "Strawberry", "Grape", "Other"]),
                "Quantity": st.column_config.NumberColumn("Quantity", min_value=0),
                "Revenue": st.column_config.NumberColumn("Revenue ($)", min_value=0.0, format="$%.2f")
            }
        )
        
        # Update session state with edited data
        st.session_state.sales_data = edited_df.to_dict('records')
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Daily Revenue Trend**")
            if not df.empty:
                daily_sales = df.groupby('Date')['Revenue'].sum().reset_index()
                fig = px.line(daily_sales, x='Date', y='Revenue', title="Revenue Over Time")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Flavor Performance**")
            if not df.empty:
                flavor_sales = df.groupby('Flavor')['Revenue'].sum().reset_index()
                fig = px.pie(flavor_sales, values='Revenue', names='Flavor', title="Sales by Flavor")
                st.plotly_chart(fig, use_container_width=True)

# Deal Finder Page
elif page == "Deal Finder":
    st.header("🔍 Deal Finder")
    
    st.write("Find the best deals on supplies and ingredients for your slushie business.")
    
    # Editable Deal Categories
    st.subheader("📝 Customize Deal Categories")
    deal_categories = st.multiselect(
        "Select or add deal categories:",
        ["Syrups & Flavors", "Cups & Straws", "Ice Machines", "Blenders", "Other Supplies", "Custom"],
        default=["Syrups & Flavors", "Cups & Straws", "Ice Machines"]
    )
    
    if "Custom" in deal_categories:
        custom_category = st.text_input("Enter custom category name:")
        if custom_category:
            deal_categories = [cat for cat in deal_categories if cat != "Custom"] + [custom_category]
    
    deal_category = st.selectbox("What are you looking for?", deal_categories)
    
    # Editable Deal Data
    st.subheader("📝 Add/Edit Deals")
    
    # Add new deal
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        new_item = st.text_input("Item Name")
    with col2:
        new_price = st.text_input("Sale Price")
    with col3:
        new_original = st.text_input("Original Price")
    with col4:
        new_supplier = st.text_input("Supplier")
    with col5:
        new_rating = st.number_input("Rating", min_value=0.0, max_value=5.0, value=4.0, step=0.1)
    
    if st.button("Add Deal") and new_item and new_price:
        if "deals" not in st.session_state:
            st.session_state.deals = {}
        if deal_category not in st.session_state.deals:
            st.session_state.deals[deal_category] = []
        
        new_deal = {
            "item": new_item,
            "price": new_price,
            "original": new_original,
            "supplier": new_supplier,
            "rating": new_rating
        }
        st.session_state.deals[deal_category].append(new_deal)
        st.success("Deal added!")
    
    # Display deals
    if "deals" in st.session_state and deal_category in st.session_state.deals:
        st.subheader(f"Best Deals on {deal_category}")
        
        for i, deal in enumerate(st.session_state.deals[deal_category]):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                with col1:
                    st.write(f"**{deal['item']}**")
                    st.write(f"Supplier: {deal['supplier']}")
                with col2:
                    st.write(f"**${deal['price']}**")
                with col3:
                    st.write(f"~~${deal['original']}~~")
                with col4:
                    st.write(f"⭐ {deal['rating']}")
                with col5:
                    if st.button(f"Delete", key=f"delete_{i}"):
                        st.session_state.deals[deal_category].pop(i)
                        st.rerun()
                st.divider()
    
    # AI-powered deal analysis
    st.subheader("🤖 AI Deal Analysis")
    analysis_prompt = st.text_area(
        "Describe what you're looking for and your budget:",
        placeholder="e.g., I need blue raspberry syrup for 100 gallons of slushie, budget $200"
    )
    
    if st.button("Get AI Recommendations") and analysis_prompt:
        with st.spinner("Analyzing deals..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a procurement expert for a slushie business. Analyze deals and provide recommendations based on cost, quality, and value."},
                        {"role": "user", "content": f"Analyze this request and provide specific deal recommendations: {analysis_prompt}"}
                    ]
                )
                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Unable to get AI deal analysis at the moment. Please check your internet connection and try again. (Error: {str(e)})")

# Data Analysis Page
elif page == "Data Analysis":
    st.header("📈 Data Analysis")
    
    st.write("Upload your sales data or enter it manually to analyze consumer patterns.")
    
    # Data input methods
    data_method = st.radio("How would you like to input data?", ["Upload CSV", "Manual Entry", "Edit Existing Data"])
    
    if data_method == "Upload CSV":
        uploaded_file = st.file_uploader("Upload your sales data CSV", type=['csv'])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            # Ensure required columns exist
            if 'Quantity' not in df.columns:
                df['Quantity'] = 1  # Default quantity if not provided
            st.session_state.sales_data = df.to_dict('records')
            st.success("Data uploaded successfully!")
    
    elif data_method == "Manual Entry":
        st.subheader("Enter Sales Data")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            date = st.date_input("Date")
        with col2:
            flavor = st.selectbox("Flavor", ["Blue Raspberry", "Cherry", "Lime", "Orange", "Strawberry", "Grape", "Other"])
        with col3:
            quantity = st.number_input("Quantity Sold", min_value=0)
        with col4:
            revenue = st.number_input("Revenue", min_value=0.0)
        
        if st.button("Add Data Point"):
            new_data = {
                "Date": date,
                "Flavor": flavor,
                "Quantity": quantity,
                "Revenue": revenue
            }
            st.session_state.sales_data.append(new_data)
            st.success("Data point added!")
    
    elif data_method == "Edit Existing Data":
        st.subheader("Edit Your Sales Data")
        
        if st.session_state.sales_data:
            df = pd.DataFrame(st.session_state.sales_data)
            
            # Make the dataframe editable
            edited_df = st.data_editor(
                df,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "Date": st.column_config.DateColumn("Date"),
                    "Flavor": st.column_config.SelectboxColumn("Flavor", options=["Blue Raspberry", "Cherry", "Lime", "Orange", "Strawberry", "Grape", "Other"]),
                    "Quantity": st.column_config.NumberColumn("Quantity", min_value=0),
                    "Revenue": st.column_config.NumberColumn("Revenue ($)", min_value=0.0, format="$%.2f")
                }
            )
            
            # Update session state with edited data
            st.session_state.sales_data = edited_df.to_dict('records')
        else:
            st.info("No data to edit. Add some data first!")
    
    # Display and analyze data
    if st.session_state.sales_data:
        df = pd.DataFrame(st.session_state.sales_data)
        
        st.subheader("📊 Data Analysis Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Top Performing Flavors**")
            if not df.empty:
                flavor_performance = df.groupby('Flavor')['Revenue'].sum().sort_values(ascending=False)
                fig = px.bar(flavor_performance, title="Revenue by Flavor")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**Daily Sales Trend**")
            if not df.empty:
                daily_sales = df.groupby('Date')['Revenue'].sum()
                fig = px.line(daily_sales, title="Daily Revenue Trend")
                st.plotly_chart(fig, use_container_width=True)
        
        # AI Pattern Analysis
        st.subheader("🤖 AI Pattern Analysis")
        if st.button("Analyze Consumer Patterns"):
            with st.spinner("Analyzing patterns..."):
                # Prepare data summary for AI
                data_summary = f"""
                Data Summary:
                - Total Revenue: ${df['Revenue'].sum():.2f}
                - Total Sales: {df.get('Quantity', pd.Series([0])).sum()} units
                - Top Flavor: {flavor_performance.index[0] if not df.empty else 'None'}
                - Date Range: {df['Date'].min()} to {df['Date'].max() if not df.empty else 'None'}
                - Average Daily Revenue: ${df.groupby('Date')['Revenue'].sum().mean():.2f if not df.empty else 0}
                """
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a business analyst specializing in food service. Analyze sales data and provide insights about consumer behavior, trends, and recommendations."},
                        {"role": "user", "content": f"Analyze this slushie sales data and provide insights: {data_summary}"}
                    ]
                )
                st.write(response.choices[0].message.content)

# Inventory Recommendations Page
elif page == "Inventory Recommendations":
    st.header("📦 Inventory Recommendations")
    
    st.write("Get AI-powered recommendations for your inventory management.")
    
    # Current inventory input - fully editable
    st.subheader("Current Inventory")
    
    # Initialize inventory data if not exists
    if "inventory_data" not in st.session_state:
        st.session_state.inventory_data = {
            "Blue Raspberry": 0,
            "Cherry": 0,
            "Lime": 0,
            "Orange": 0,
            "Strawberry": 0,
            "Grape": 0
        }
    
    # Editable inventory table
    st.write("**Edit Your Current Inventory (gallons):**")
    
    inventory_df = pd.DataFrame([
        {"Flavor": flavor, "Gallons": gallons}
        for flavor, gallons in st.session_state.inventory_data.items()
    ])
    
    edited_inventory = st.data_editor(
        inventory_df,
        use_container_width=True,
        column_config={
            "Flavor": st.column_config.TextColumn("Flavor", disabled=True),
            "Gallons": st.column_config.NumberColumn("Gallons", min_value=0, step=0.1)
        }
    )
    
    # Update session state
    for _, row in edited_inventory.iterrows():
        st.session_state.inventory_data[row['Flavor']] = row['Gallons']
    
    # Add new flavor
    st.subheader("Add New Flavor")
    col1, col2 = st.columns(2)
    with col1:
        new_flavor = st.text_input("New Flavor Name")
    with col2:
        new_gallons = st.number_input("Gallons", min_value=0.0, value=0.0, step=0.1)
    
    if st.button("Add Flavor") and new_flavor:
        st.session_state.inventory_data[new_flavor] = new_gallons
        st.success(f"Added {new_flavor} to inventory!")
        st.rerun()
    
    # Sales data for recommendations
    st.subheader("Recent Sales Data")
    sales_period = st.selectbox("Sales Period", ["Last Week", "Last Month", "Last Quarter"])
    
    if st.button("Get Inventory Recommendations"):
        with st.spinner("Analyzing inventory..."):
            # AI recommendation
            prompt = f"""
            As a CFO for a slushie business, analyze this inventory and provide recommendations:
            
            Current Inventory:
            {st.session_state.inventory_data}
            
            Sales Period: {sales_period}
            
            Provide specific recommendations for:
            1. Which flavors to order more of
            2. Which flavors to reduce
            3. Optimal inventory levels
            4. Cost-saving opportunities
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a CFO specializing in inventory management for food service businesses. Provide practical, cost-effective recommendations."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            st.write(response.choices[0].message.content)
            
            # Visual inventory chart
            fig = px.bar(
                x=list(st.session_state.inventory_data.keys()),
                y=list(st.session_state.inventory_data.values()),
                title="Current Inventory Levels",
                labels={'x': 'Flavor', 'y': 'Gallons'}
            )
            st.plotly_chart(fig, use_container_width=True)

# Profit Calculator Page
elif page == "Profit Calculator":
    st.header("💰 Profit Calculator")
    
    st.write("Calculate gross and net profits for your slushie business.")
    
    # Initialize profit data if not exists
    if "profit_data" not in st.session_state:
        st.session_state.profit_data = {
            "total_sales": 0.0,
            "other_revenue": 0.0,
            "syrup_cost": 0.0,
            "cup_cost": 0.0,
            "ice_cost": 0.0,
            "other_cogs": 0.0,
            "rent": 0.0,
            "utilities": 0.0,
            "labor": 0.0,
            "marketing": 0.0,
            "other_expenses": 0.0
        }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue Input")
        st.session_state.profit_data["total_sales"] = st.number_input(
            "Total Sales ($)", 
            min_value=0.0, 
            value=st.session_state.profit_data["total_sales"],
            step=0.01
        )
        st.session_state.profit_data["other_revenue"] = st.number_input(
            "Other Revenue ($)", 
            min_value=0.0, 
            value=st.session_state.profit_data["other_revenue"],
            step=0.01
        )
        
        st.subheader("Cost of Goods Sold")
        st.session_state.profit_data["syrup_cost"] = st.number_input(
            "Syrup Cost ($)", 
            min_value=0.0, 
            value=st.session_state.profit_data["syrup_cost"],
            step=0.01
        )
        st.session_state.profit_data["cup_cost"] = st.number_input(
            "Cup & Straw Cost ($)", 
            min_value=0.0, 
            value=st.session_state.profit_data["cup_cost"],
            step=0.01
        )
        st.session_state.profit_data["ice_cost"] = st.number_input(
            "Ice Cost ($)", 
            min_value=0.0, 
            value=st.session_state.profit_data["ice_cost"],
            step=0.01
        )
        st.session_state.profit_data["other_cogs"] = st.number_input(
            "Other COGS ($)", 
            min_value=0.0, 
            value=st.session_state.profit_data["other_cogs"],
            step=0.01
        )
    
    with col2:
        st.subheader("Operating Expenses")
        st.session_state.profit_data["rent"] = st.number_input(
            "Rent ($)", 
            min_value=0.0, 
            value=st.session_state.profit_data["rent"],
            step=0.01
        )
        st.session_state.profit_data["utilities"] = st.number_input(
            "Utilities ($)", 
            min_value=0.0, 
            value=st.session_state.profit_data["utilities"],
            step=0.01
        )
        st.session_state.profit_data["labor"] = st.number_input(
            "Labor ($)", 
            min_value=0.0, 
            value=st.session_state.profit_data["labor"],
            step=0.01
        )
        st.session_state.profit_data["marketing"] = st.number_input(
            "Marketing ($)", 
            min_value=0.0, 
            value=st.session_state.profit_data["marketing"],
            step=0.01
        )
        st.session_state.profit_data["other_expenses"] = st.number_input(
            "Other Expenses ($)", 
            min_value=0.0, 
            value=st.session_state.profit_data["other_expenses"],
            step=0.01
        )
    
    # Calculate profits
    total_revenue = st.session_state.profit_data["total_sales"] + st.session_state.profit_data["other_revenue"]
    total_cogs = (st.session_state.profit_data["syrup_cost"] + 
                  st.session_state.profit_data["cup_cost"] + 
                  st.session_state.profit_data["ice_cost"] + 
                  st.session_state.profit_data["other_cogs"])
    total_expenses = (st.session_state.profit_data["rent"] + 
                      st.session_state.profit_data["utilities"] + 
                      st.session_state.profit_data["labor"] + 
                      st.session_state.profit_data["marketing"] + 
                      st.session_state.profit_data["other_expenses"])
    
    gross_profit = total_revenue - total_cogs
    net_profit = gross_profit - total_expenses
    
    gross_margin = (gross_profit / total_revenue) * 100 if total_revenue > 0 else 0
    net_margin = (net_profit / total_revenue) * 100 if total_revenue > 0 else 0
    
    # Display results
    st.subheader("📊 Profit Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    with col2:
        st.metric("Gross Profit", f"${gross_profit:,.2f}", f"{gross_margin:.1f}% margin")
    with col3:
        st.metric("Net Profit", f"${net_profit:,.2f}", f"{net_margin:.1f}% margin")
    with col4:
        profit_status = "✅ Profitable" if net_profit > 0 else "❌ Loss"
        st.metric("Status", profit_status)
    
    # Profit breakdown chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Revenue',
        x=['Total Revenue'],
        y=[total_revenue],
        marker_color='green'
    ))
    
    fig.add_trace(go.Bar(
        name='COGS',
        x=['Cost of Goods'],
        y=[total_cogs],
        marker_color='red'
    ))
    
    fig.add_trace(go.Bar(
        name='Expenses',
        x=['Operating Expenses'],
        y=[total_expenses],
        marker_color='orange'
    ))
    
    fig.update_layout(
        title="Revenue vs Costs Breakdown",
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # AI insights
    st.subheader("🤖 AI Insights")
    if st.button("Get Financial Insights"):
        with st.spinner("Analyzing finances..."):
            try:
                financial_summary = f"""
                Financial Summary:
                - Total Revenue: ${total_revenue:,.2f}
                - Gross Profit: ${gross_profit:,.2f} ({gross_margin:.1f}% margin)
                - Net Profit: ${net_profit:,.2f} ({net_margin:.1f}% margin)
                - COGS: ${total_cogs:,.2f}
                - Operating Expenses: ${total_expenses:,.2f}
                """
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a CFO specializing in small business financial analysis. Provide insights and recommendations for improving profitability."},
                        {"role": "user", "content": f"Analyze this slushie business financial data and provide recommendations: {financial_summary}"}
                    ]
                )
                
                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Unable to get AI insights at the moment. Please check your internet connection and try again. (Error: {str(e)})")

# Live Data & Images Page
elif page == "Live Data & Images":
    st.header("🌐 Live Data & Images")
    
    st.write("Access live data and generate images for your slushie business.")
    
    # Live Data Section
    st.subheader("📊 Live Data Access")
    
    data_type = st.selectbox(
        "What type of live data do you need?",
        ["Weather Data", "Currency Exchange", "Stock Prices", "News Headlines", "Custom API"]
    )
    
    if data_type == "Weather Data":
        city = st.text_input("Enter city name:", value="New York")
        if st.button("Get Weather Data"):
            try:
                # Using a free weather API (you'd need to sign up for a real API key)
                weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=YOUR_API_KEY&units=metric"
                st.info("Weather API requires a free API key from OpenWeatherMap. Sign up at openweathermap.org")
                
                # Mock weather data for demonstration
                mock_weather = {
                    "temperature": 22,
                    "humidity": 65,
                    "description": "Partly cloudy",
                    "wind_speed": 12
                }
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Temperature", f"{mock_weather['temperature']}°C")
                with col2:
                    st.metric("Humidity", f"{mock_weather['humidity']}%")
                with col3:
                    st.metric("Wind Speed", f"{mock_weather['wind_speed']} km/h")
                with col4:
                    st.metric("Conditions", mock_weather['description'])
                
                st.success("Weather data retrieved successfully!")
                
            except Exception as e:
                st.error(f"Unable to fetch weather data: {str(e)}")
    
    elif data_type == "Currency Exchange":
        from_currency = st.selectbox("From:", ["USD", "EUR", "GBP", "CAD"])
        to_currency = st.selectbox("To:", ["USD", "EUR", "GBP", "CAD"])
        amount = st.number_input("Amount:", min_value=0.01, value=1.0)
        
        if st.button("Get Exchange Rate"):
            try:
                # Mock exchange rate (you'd use a real API like exchangerate-api.com)
                exchange_rates = {
                    "USD": {"EUR": 0.85, "GBP": 0.73, "CAD": 1.25},
                    "EUR": {"USD": 1.18, "GBP": 0.86, "CAD": 1.47},
                    "GBP": {"USD": 1.37, "EUR": 1.16, "CAD": 1.71},
                    "CAD": {"USD": 0.80, "EUR": 0.68, "GBP": 0.58}
                }
                
                if from_currency != to_currency:
                    rate = exchange_rates[from_currency][to_currency]
                    converted = amount * rate
                    st.metric(f"Exchange Rate", f"1 {from_currency} = {rate:.4f} {to_currency}")
                    st.metric(f"Converted Amount", f"{converted:.2f} {to_currency}")
                else:
                    st.info("Same currency selected - no conversion needed")
                    
            except Exception as e:
                st.error(f"Unable to fetch exchange rate: {str(e)}")
    
    elif data_type == "Stock Prices":
        symbol = st.text_input("Enter stock symbol:", value="AAPL")
        if st.button("Get Stock Price"):
            try:
                # Mock stock data (you'd use a real API like Alpha Vantage or Yahoo Finance)
                mock_stock = {
                    "price": 150.25,
                    "change": 2.15,
                    "change_percent": 1.45,
                    "volume": 45000000
                }
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Price", f"${mock_stock['price']:.2f}")
                with col2:
                    st.metric("Change", f"${mock_stock['change']:.2f}")
                with col3:
                    st.metric("Change %", f"{mock_stock['change_percent']:.2f}%")
                with col4:
                    st.metric("Volume", f"{mock_stock['volume']:,}")
                
                st.info("This is mock data. For real stock data, you'd need an API key from services like Alpha Vantage.")
                
            except Exception as e:
                st.error(f"Unable to fetch stock data: {str(e)}")
    
    # Image Generation Section
    st.subheader("🎨 AI Image Generation")
    
    image_prompt = st.text_area(
        "Describe the image you want to generate:",
        placeholder="e.g., A colorful slushie stand with neon lights, modern design, summer vibes"
    )
    
    if st.button("Generate Image") and image_prompt:
        with st.spinner("Generating image..."):
            try:
                # This would use DALL-E API for real image generation
                st.info("Image generation requires DALL-E API access. For now, showing a placeholder.")
                
                # Create a simple placeholder image
                placeholder_img = Image.new('RGB', (400, 300), color='lightblue')
                
                # Add some text to the placeholder
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(placeholder_img)
                try:
                    font = ImageFont.truetype("arial.ttf", 20)
                except:
                    font = ImageFont.load_default()
                
                draw.text((50, 150), "AI Generated Image", fill='black', font=font)
                draw.text((50, 180), "Would appear here", fill='black', font=font)
                
                st.image(placeholder_img, caption="Generated Image Placeholder", use_column_width=True)
                
                st.success("Image generation completed! (This is a placeholder - real generation requires DALL-E API)")
                
            except Exception as e:
                st.error(f"Unable to generate image: {str(e)}")
    
    # Business Image Templates
    st.subheader("📋 Business Image Templates")
    
    template_type = st.selectbox(
        "Choose a business image template:",
        ["Slushie Stand Design", "Menu Layout", "Social Media Post", "Business Card", "Flyer Design"]
    )
    
    if st.button("Generate Template"):
        st.info(f"Template for '{template_type}' would be generated here.")
        st.write("This would create a professional business image template using AI.")

# Live Charts Page
elif page == "Live Charts":
    st.header("📊 Live Charts & Analytics")
    
    st.write("Create, organize, and view custom charts and graphs for your business data.")
    
    # Chart creation and management functions
    def create_chart(chart_config):
        """Create a chart based on configuration"""
        try:
            if chart_config["data_source"] == "sales_data" and st.session_state.sales_data:
                df = pd.DataFrame(st.session_state.sales_data)
            elif chart_config["data_source"] == "venmo_data" and st.session_state.venmo_data['transactions']:
                df = pd.DataFrame(st.session_state.venmo_data['transactions'])
            elif chart_config["data_source"] == "dashboard_metrics":
                # Convert dashboard metrics to dataframe
                metrics_data = [
                    {"metric": "Total Revenue", "value": st.session_state.dashboard_metrics["total_revenue"]},
                    {"metric": "Gross Profit", "value": st.session_state.dashboard_metrics["gross_profit"]},
                    {"metric": "Net Profit", "value": st.session_state.dashboard_metrics["net_profit"]}
                ]
                df = pd.DataFrame(metrics_data)
            else:
                return None, "No data available for this chart"
            
            if df.empty:
                return None, "No data available"
            
            # Create chart based on type
            if chart_config["type"] == "line":
                fig = px.line(
                    df, 
                    x=chart_config["x_column"], 
                    y=chart_config["y_column"],
                    title=chart_config["title"],
                    color_discrete_sequence=[chart_config.get("color", "blue")]
                )
            elif chart_config["type"] == "bar":
                fig = px.bar(
                    df,
                    x=chart_config["x_column"],
                    y=chart_config["y_column"],
                    title=chart_config["title"],
                    color=chart_config.get("color", "blue")
                )
            elif chart_config["type"] == "pie":
                fig = px.pie(
                    df,
                    values=chart_config["y_column"],
                    names=chart_config["x_column"],
                    title=chart_config["title"],
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
            elif chart_config["type"] == "scatter":
                fig = px.scatter(
                    df,
                    x=chart_config["x_column"],
                    y=chart_config["y_column"],
                    title=chart_config["title"],
                    color=chart_config.get("color", "blue")
                )
            elif chart_config["type"] == "histogram":
                fig = px.histogram(
                    df,
                    x=chart_config["x_column"],
                    title=chart_config["title"],
                    color_discrete_sequence=[chart_config.get("color", "blue")]
                )
            else:
                return None, f"Unknown chart type: {chart_config['type']}"
            
            return fig, None
            
        except Exception as e:
            return None, f"Error creating chart: {str(e)}"
    
    # Chart creation interface
    st.subheader("🎨 Create New Chart")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Chart configuration
        chart_name = st.text_input("Chart Name:", key="new_chart_name")
        chart_type = st.selectbox(
            "Chart Type:",
            ["line", "bar", "pie", "scatter", "histogram"],
            key="new_chart_type"
        )
        data_source = st.selectbox(
            "Data Source:",
            ["sales_data", "venmo_data", "dashboard_metrics"],
            key="new_chart_data_source"
        )
    
    with col2:
        # Column selection based on data source
        if data_source == "sales_data" and st.session_state.sales_data:
            df_sample = pd.DataFrame(st.session_state.sales_data)
            x_column = st.selectbox("X Column:", df_sample.columns.tolist(), key="new_chart_x")
            y_column = st.selectbox("Y Column:", df_sample.columns.tolist(), key="new_chart_y")
        elif data_source == "venmo_data" and st.session_state.venmo_data['transactions']:
            df_sample = pd.DataFrame(st.session_state.venmo_data['transactions'])
            x_column = st.selectbox("X Column:", df_sample.columns.tolist(), key="new_chart_x")
            y_column = st.selectbox("Y Column:", df_sample.columns.tolist(), key="new_chart_y")
        elif data_source == "dashboard_metrics":
            x_column = st.selectbox("X Column:", ["metric"], key="new_chart_x")
            y_column = st.selectbox("Y Column:", ["value"], key="new_chart_y")
        else:
            x_column = "Date"
            y_column = "Revenue"
            st.warning("No data available for selected source")
        
        chart_color = st.color_picker("Chart Color:", "#1f77b4", key="new_chart_color")
    
    # Folder selection
    folder_name = st.selectbox(
        "Save to Folder:",
        list(st.session_state.custom_charts["folders"].keys()) + ["Create New Folder"],
        key="new_chart_folder"
    )
    
    if folder_name == "Create New Folder":
        folder_name = st.text_input("New Folder Name:", key="new_folder_name")
    
    # Create chart button
    if st.button("Create Chart", key="create_chart_btn"):
        if chart_name and folder_name:
            # Create new folder if needed
            if folder_name not in st.session_state.custom_charts["folders"]:
                st.session_state.custom_charts["folders"][folder_name] = {"charts": {}}
            
            # Add chart to folder
            chart_config = {
                "type": chart_type,
                "data_source": data_source,
                "x_column": x_column,
                "y_column": y_column,
                "title": chart_name,
                "color": chart_color
            }
            
            st.session_state.custom_charts["folders"][folder_name]["charts"][chart_name] = chart_config
            st.success(f"✅ Chart '{chart_name}' created in folder '{folder_name}'!")
            st.rerun()
        else:
            st.error("Please provide chart name and folder")
    
    # Folder and chart organization
    st.subheader("📁 Chart Organization")
    
    # Folder management
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Folder selection
        selected_folder = st.selectbox(
            "Select Folder:",
            list(st.session_state.custom_charts["folders"].keys()),
            key="folder_selector"
        )
        
        if selected_folder:
            st.session_state.custom_charts["active_folder"] = selected_folder
            
            # Show charts in selected folder
            st.write(f"**Charts in '{selected_folder}':**")
            
            if st.session_state.custom_charts["folders"][selected_folder]["charts"]:
                for chart_name, chart_config in st.session_state.custom_charts["folders"][selected_folder]["charts"].items():
                    with st.expander(f"📊 {chart_name}"):
                        # Create and display chart
                        fig, error = create_chart(chart_config)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.error(error)
                        
                        # Chart management options
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            if st.button(f"🔄 Refresh", key=f"refresh_{chart_name}"):
                                st.rerun()
                        with col_b:
                            if st.button(f"✏️ Edit", key=f"edit_{chart_name}"):
                                st.session_state.editing_chart = chart_name
                        with col_c:
                            if st.button(f"🗑️ Delete", key=f"delete_{chart_name}"):
                                del st.session_state.custom_charts["folders"][selected_folder]["charts"][chart_name]
                                st.success(f"Chart '{chart_name}' deleted!")
                                st.rerun()
            else:
                st.info("No charts in this folder yet.")
    
    with col2:
        # Folder management
        st.write("**Folder Management:**")
        
        if st.button("📁 New Folder", key="new_folder_btn"):
            new_folder = st.text_input("Folder Name:", key="new_folder_input")
            if new_folder:
                st.session_state.custom_charts["folders"][new_folder] = {"charts": {}}
                st.success(f"Folder '{new_folder}' created!")
                st.rerun()
        
        if st.button("🗑️ Delete Folder", key="delete_folder_btn"):
            if selected_folder and selected_folder in st.session_state.custom_charts["folders"]:
                del st.session_state.custom_charts["folders"][selected_folder]
                st.success(f"Folder '{selected_folder}' deleted!")
                st.rerun()
    
    # Tab organization
    st.subheader("📑 Chart Tabs")
    
    # Create tabs for different chart categories
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Revenue", "🍧 Flavors", "📈 Trends", "💰 Financial"])
    
    with tab1:
        st.write("**Revenue-focused charts:**")
        # Revenue charts
        if st.session_state.sales_data:
            df = pd.DataFrame(st.session_state.sales_data)
            if not df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    daily_revenue = df.groupby('Date')['Revenue'].sum().reset_index()
                    fig = px.line(daily_revenue, x='Date', y='Revenue', title="Daily Revenue")
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    total_revenue = df['Revenue'].sum()
                    st.metric("Total Revenue", f"${total_revenue:,.2f}")
    
    with tab2:
        st.write("**Flavor performance charts:**")
        # Flavor charts
        if st.session_state.sales_data:
            df = pd.DataFrame(st.session_state.sales_data)
            if not df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    flavor_sales = df.groupby('Flavor')['Revenue'].sum().reset_index()
                    fig = px.pie(flavor_sales, values='Revenue', names='Flavor', title="Revenue by Flavor")
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    flavor_counts = df.groupby('Flavor')['Quantity'].sum().reset_index()
                    fig = px.bar(flavor_counts, x='Flavor', y='Quantity', title="Sales by Flavor")
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.write("**Trend analysis charts:**")
        # Trend charts
        if st.session_state.venmo_data['transactions']:
            col1, col2 = st.columns(2)
            with col1:
                # Transaction volume over time
                transaction_times = [t['time'] for t in st.session_state.venmo_data['transactions']]
                time_counts = {}
                for time in transaction_times:
                    hour = time.split(':')[0] + ':00'
                    time_counts[hour] = time_counts.get(hour, 0) + 1
                
                if time_counts:
                    df_time = pd.DataFrame([
                        {'Hour': hour, 'Transactions': count}
                        for hour, count in time_counts.items()
                    ])
                    fig = px.line(df_time, x='Hour', y='Transactions', title="Transaction Volume Over Time")
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.write("**Financial metrics charts:**")
        # Financial charts
        col1, col2 = st.columns(2)
        with col1:
            # Business metrics
            metrics_data = [
                {"Metric": "Total Revenue", "Value": st.session_state.dashboard_metrics["total_revenue"]},
                {"Metric": "Gross Profit", "Value": st.session_state.dashboard_metrics["gross_profit"]},
                {"Metric": "Net Profit", "Value": st.session_state.dashboard_metrics["net_profit"]}
            ]
            df_metrics = pd.DataFrame(metrics_data)
            fig = px.bar(df_metrics, x='Metric', y='Value', title="Business Metrics")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            # Venmo daily total
            st.metric("Today's Venmo Revenue", f"${st.session_state.venmo_data['daily_total']:,.2f}")
            st.metric("Transaction Count", len(st.session_state.venmo_data['transactions']))
    
    # Auto-updating charts and graphs
    st.subheader("📊 Auto-Updating Charts")

# Chat Assistant Page
elif page == "Chat Assistant":
    st.header("💬 CFO Chat Assistant")
    
    st.write("Ask me anything about your slushie business - from financial advice to operational insights.")
    
    # Context and tone selection
    st.subheader("Customize AI Response")
    col1, col2 = st.columns(2)
    
    with col1:
        context = st.selectbox(
            "Business Context:",
            [
                "General Business Advice",
                "Financial Planning & Budgeting",
                "Inventory Management",
                "Marketing & Sales Strategy",
                "Operations & Efficiency",
                "Customer Service",
                "Seasonal Planning",
                "Growth & Expansion",
                "Cost Control",
                "Pricing Strategy"
            ],
            help="Select the main area you want advice on"
        )
    
    with col2:
        tone = st.selectbox(
            "Response Tone:",
            [
                "Professional & Detailed",
                "Simple & Practical",
                "Encouraging & Motivational",
                "Analytical & Data-Driven",
                "Creative & Innovative",
                "Conservative & Cautious",
                "Aggressive & Growth-Focused",
                "Family-Friendly & Relatable"
            ],
            help="Choose how you want the AI to communicate"
        )
    
    # Additional context input
    business_context = st.text_area(
        "Additional Context (Optional):",
        placeholder="e.g., I'm a family of 4 running a small slushie stand at local events. We make about $200-300 per weekend. We're looking to expand but have limited budget...",
        help="Provide specific details about your business situation for more tailored advice"
    )
    
    # Helper function to process commands
    def process_command(command_text):
        """Process slash commands and return response"""
        command_parts = command_text.strip().split()
        
        if not command_parts:
            return "Invalid command. Type /help for available commands."
        
        command = command_parts[0].lower()
        
        if command == "/help":
            return """**Available Commands:**

📊 **Data Commands:**
- `/net profits` - Show current net profits
- `/total sales` - Show total sales count
- `/best day` - Show best performing day
- `/status` - Show all current data
- `/add [number] to net profit` - Add amount to net profits
- `/add [number] to sales` - Add to total sales
- `/set net profit [amount]` - Set net profits to specific amount
- `/set total sales [amount]` - Set total sales to specific amount
- `/set best day [day]` - Set best performing day

📝 **Note Commands:**
- `/add note [text]` - Add a note
- `/notes` - Show all notes
- `/clear notes` - Clear all notes

🧮 **Calculation Commands:**
- `/profit margin [revenue] [costs]` - Calculate profit margin
- `/break even [fixed_costs] [price] [variable_cost]` - Calculate break-even point
- `/calculate margin [revenue] [costs]` - Profit margin calculation
- `/calculate markup [cost] [markup_percent]` - Markup calculation
- `/calculate discount [original_price] [discount_percent]` - Discount calculation
- `/calculate tax [amount] [tax_rate]` - Tax calculation
- `/calculate tip [bill_amount] [tip_percent]` - Tip calculation
- `/calculate inventory [current_stock] [daily_usage]` - Inventory analysis
- `/calculate roi [investment] [returns]` - ROI calculation

🔄 **Reset Commands:**
- `/reset all` - Reset all data to default values
- `/reset profits` - Reset net profits to $0
- `/reset sales` - Reset total sales to 0

❓ **Help:**
- `/help` - Show this help message
- `/commands` - List all available commands

💡 **Examples:**
- `/add 150 to net profit` - Add $150 to profits
- `/calculate markup 10 50` - 50% markup on $10 item
- `/calculate inventory 100 5` - 100 units, 5 used daily"""
        
        elif command == "/net" and len(command_parts) > 1 and command_parts[1] == "profits":
            return f"💰 **Current Net Profits:** ${st.session_state.commands_data['net_profits']:,.2f}"
        
        elif command == "/add" and len(command_parts) >= 4:
            try:
                amount = float(command_parts[1])
                if command_parts[2] == "to" and command_parts[3] == "net" and command_parts[4] == "profit":
                    st.session_state.commands_data['net_profits'] += amount
                    return f"✅ Added ${amount:,.2f} to net profits. New total: ${st.session_state.commands_data['net_profits']:,.2f}"
            except ValueError:
                return "❌ Invalid amount. Please enter a valid number."
        
        elif command == "/total" and len(command_parts) > 1 and command_parts[1] == "sales":
            return f"📊 **Total Sales:** {st.session_state.commands_data['total_sales']:,} units"
        
        elif command == "/add" and len(command_parts) >= 4:
            try:
                amount = int(command_parts[1])
                if command_parts[2] == "to" and command_parts[3] == "sales":
                    st.session_state.commands_data['total_sales'] += amount
                    return f"✅ Added {amount:,} to total sales. New total: {st.session_state.commands_data['total_sales']:,} units"
            except ValueError:
                return "❌ Invalid amount. Please enter a valid number."
        
        elif command == "/best" and len(command_parts) > 1 and command_parts[1] == "day":
            return f"📅 **Best Performing Day:** {st.session_state.commands_data['best_day']}"
        
        elif command == "/set" and len(command_parts) >= 4:
            if command_parts[1] == "best" and command_parts[2] == "day":
                day = " ".join(command_parts[3:])
                st.session_state.commands_data['best_day'] = day
                return f"✅ Set best performing day to: {day}"
            elif command_parts[1] == "net" and command_parts[2] == "profit":
                try:
                    amount = float(command_parts[3])
                    st.session_state.commands_data['net_profits'] = amount
                    return f"✅ Set net profits to: ${amount:,.2f}"
                except ValueError:
                    return "❌ Invalid amount. Please enter a valid number."
            elif command_parts[1] == "total" and command_parts[2] == "sales":
                try:
                    amount = int(command_parts[3])
                    st.session_state.commands_data['total_sales'] = amount
                    return f"✅ Set total sales to: {amount:,} units"
                except ValueError:
                    return "❌ Invalid amount. Please enter a valid number."
        
        elif command == "/add" and len(command_parts) >= 3 and command_parts[1] == "note":
            note = " ".join(command_parts[2:])
            st.session_state.commands_data['notes'].append(note)
            return f"📝 **Note added:** {note}"
        
        elif command == "/notes":
            if not st.session_state.commands_data['notes']:
                return "📝 No notes saved yet."
            notes_text = "\n".join([f"{i+1}. {note}" for i, note in enumerate(st.session_state.commands_data['notes'])])
            return f"📝 **Saved Notes:**\n{notes_text}"
        
        elif command == "/clear" and len(command_parts) > 1 and command_parts[1] == "notes":
            st.session_state.commands_data['notes'] = []
            return "🗑️ All notes cleared."
        
        elif command == "/profit" and len(command_parts) >= 4 and command_parts[1] == "margin":
            try:
                revenue = float(command_parts[2])
                costs = float(command_parts[3])
                profit = revenue - costs
                margin = (profit / revenue) * 100 if revenue > 0 else 0
                return f"💰 **Profit Margin Calculation:**\nRevenue: ${revenue:,.2f}\nCosts: ${costs:,.2f}\nProfit: ${profit:,.2f}\nMargin: {margin:.1f}%"
            except ValueError:
                return "❌ Invalid numbers. Use: /profit margin [revenue] [costs]"
        
        elif command == "/break" and len(command_parts) >= 5 and command_parts[1] == "even":
            try:
                fixed_costs = float(command_parts[2])
                price = float(command_parts[3])
                variable_cost = float(command_parts[4])
                contribution_margin = price - variable_cost
                break_even_units = fixed_costs / contribution_margin if contribution_margin > 0 else 0
                return f"📊 **Break-Even Analysis:**\nFixed Costs: ${fixed_costs:,.2f}\nPrice per Unit: ${price:,.2f}\nVariable Cost per Unit: ${variable_cost:,.2f}\nBreak-Even Units: {break_even_units:,.0f}"
            except ValueError:
                return "❌ Invalid numbers. Use: /break even [fixed_costs] [price] [variable_cost]"
        
        elif command == "/calculate" and len(command_parts) >= 3:
            calc_type = command_parts[1].lower()
            
            if calc_type == "margin" and len(command_parts) >= 4:
                try:
                    revenue = float(command_parts[2])
                    costs = float(command_parts[3])
                    profit = revenue - costs
                    margin = (profit / revenue) * 100 if revenue > 0 else 0
                    return f"💰 **Profit Margin:**\nRevenue: ${revenue:,.2f}\nCosts: ${costs:,.2f}\nProfit: ${profit:,.2f}\nMargin: {margin:.1f}%"
                except ValueError:
                    return "❌ Invalid numbers. Use: /calculate margin [revenue] [costs]"
            
            elif calc_type == "markup" and len(command_parts) >= 4:
                try:
                    cost = float(command_parts[2])
                    markup_percent = float(command_parts[3])
                    markup_amount = cost * (markup_percent / 100)
                    selling_price = cost + markup_amount
                    return f"🏷️ **Markup Calculation:**\nCost: ${cost:,.2f}\nMarkup: {markup_percent:.1f}%\nMarkup Amount: ${markup_amount:,.2f}\nSelling Price: ${selling_price:,.2f}"
                except ValueError:
                    return "❌ Invalid numbers. Use: /calculate markup [cost] [markup_percent]"
            
            elif calc_type == "discount" and len(command_parts) >= 4:
                try:
                    original_price = float(command_parts[2])
                    discount_percent = float(command_parts[3])
                    discount_amount = original_price * (discount_percent / 100)
                    final_price = original_price - discount_amount
                    return f"🏷️ **Discount Calculation:**\nOriginal Price: ${original_price:,.2f}\nDiscount: {discount_percent:.1f}%\nDiscount Amount: ${discount_amount:,.2f}\nFinal Price: ${final_price:,.2f}"
                except ValueError:
                    return "❌ Invalid numbers. Use: /calculate discount [original_price] [discount_percent]"
            
            elif calc_type == "tax" and len(command_parts) >= 4:
                try:
                    amount = float(command_parts[2])
                    tax_rate = float(command_parts[3])
                    tax_amount = amount * (tax_rate / 100)
                    total_with_tax = amount + tax_amount
                    return f"💰 **Tax Calculation:**\nAmount: ${amount:,.2f}\nTax Rate: {tax_rate:.1f}%\nTax Amount: ${tax_amount:,.2f}\nTotal with Tax: ${total_with_tax:,.2f}"
                except ValueError:
                    return "❌ Invalid numbers. Use: /calculate tax [amount] [tax_rate]"
            
            elif calc_type == "tip" and len(command_parts) >= 4:
                try:
                    bill_amount = float(command_parts[2])
                    tip_percent = float(command_parts[3])
                    tip_amount = bill_amount * (tip_percent / 100)
                    total_with_tip = bill_amount + tip_amount
                    return f"💡 **Tip Calculation:**\nBill Amount: ${bill_amount:,.2f}\nTip: {tip_percent:.1f}%\nTip Amount: ${tip_amount:,.2f}\nTotal with Tip: ${total_with_tip:,.2f}"
                except ValueError:
                    return "❌ Invalid numbers. Use: /calculate tip [bill_amount] [tip_percent]"
            
            elif calc_type == "inventory" and len(command_parts) >= 4:
                try:
                    current_stock = float(command_parts[2])
                    daily_usage = float(command_parts[3])
                    days_remaining = current_stock / daily_usage if daily_usage > 0 else float('inf')
                    return f"📦 **Inventory Analysis:**\nCurrent Stock: {current_stock:,.1f} units\nDaily Usage: {daily_usage:,.1f} units\nDays Remaining: {days_remaining:,.1f} days"
                except ValueError:
                    return "❌ Invalid numbers. Use: /calculate inventory [current_stock] [daily_usage]"
            
            elif calc_type == "roi" and len(command_parts) >= 4:
                try:
                    investment = float(command_parts[2])
                    returns = float(command_parts[3])
                    roi_percent = ((returns - investment) / investment) * 100 if investment > 0 else 0
                    return f"📈 **ROI Calculation:**\nInvestment: ${investment:,.2f}\nReturns: ${returns:,.2f}\nROI: {roi_percent:.1f}%"
                except ValueError:
                    return "❌ Invalid numbers. Use: /calculate roi [investment] [returns]"
            
            else:
                return "❌ Unknown calculation. Available: margin, markup, discount, tax, tip, inventory, roi"
        
        elif command == "/reset":
            if len(command_parts) > 1 and command_parts[1] == "all":
                st.session_state.commands_data = {
                    "net_profits": 0.0,
                    "total_sales": 0,
                    "best_day": "None",
                    "notes": []
                }
                return "🔄 All data reset to default values."
            elif len(command_parts) > 1 and command_parts[1] == "profits":
                st.session_state.commands_data['net_profits'] = 0.0
                return "🔄 Net profits reset to $0.00"
            elif len(command_parts) > 1 and command_parts[1] == "sales":
                st.session_state.commands_data['total_sales'] = 0
                return "🔄 Total sales reset to 0 units"
        
        elif command == "/status":
            return f"""📊 **Current Status:**
💰 Net Profits: ${st.session_state.commands_data['net_profits']:,.2f}
📈 Total Sales: {st.session_state.commands_data['total_sales']:,} units
📅 Best Day: {st.session_state.commands_data['best_day']}
📝 Notes: {len(st.session_state.commands_data['notes'])} saved
💳 Venmo Connected: {'✅ Yes' if st.session_state.venmo_data['connected'] else '❌ No'}
🔄 Auto Sync: {'✅ On' if st.session_state.venmo_data['auto_sync'] else '❌ Off'}"""
        
        elif command == "/venmo" and len(command_parts) > 1:
            venmo_action = command_parts[1].lower()
            
            if venmo_action == "connect":
                return "🔗 **Venmo Connection:**\nTo connect your Venmo account:\n1. Go to the Venmo Integration section\n2. Click 'Connect Venmo Account'\n3. Follow the authorization steps\n4. Your payments will automatically sync!"
            
            elif venmo_action == "sync":
                # Simulate syncing transactions
                if st.session_state.venmo_data['connected']:
                    # Mock sync - in real implementation, this would call Venmo API
                    new_transactions = [
                        {"amount": 5.50, "note": "Blue Raspberry Slushie", "time": "2:30 PM"},
                        {"amount": 4.00, "note": "Cherry Slushie", "time": "2:45 PM"},
                        {"amount": 6.00, "note": "Large Strawberry", "time": "3:15 PM"}
                    ]
                    st.session_state.venmo_data['transactions'].extend(new_transactions)
                    st.session_state.venmo_data['daily_total'] += sum(t['amount'] for t in new_transactions)
                    st.session_state.venmo_data['last_sync'] = datetime.now().strftime("%H:%M")
                    return f"✅ **Venmo Sync Complete:**\nSynced {len(new_transactions)} new transactions\nToday's Total: ${st.session_state.venmo_data['daily_total']:,.2f}\nLast Sync: {st.session_state.venmo_data['last_sync']}"
                else:
                    return "❌ Venmo not connected. Use `/venmo connect` for instructions."
            
            elif venmo_action == "transactions":
                if st.session_state.venmo_data['transactions']:
                    transactions_text = "\n".join([
                        f"${t['amount']:.2f} - {t['note']} ({t['time']})"
                        for t in st.session_state.venmo_data['transactions'][-10:]  # Show last 10
                    ])
                    return f"💳 **Recent Venmo Transactions:**\n{transactions_text}\n\nTotal Today: ${st.session_state.venmo_data['daily_total']:,.2f}"
                else:
                    return "📭 No Venmo transactions found. Try `/venmo sync` to fetch transactions."
            
            elif venmo_action == "auto" and len(command_parts) > 2:
                if command_parts[2] == "on":
                    st.session_state.venmo_data['auto_sync'] = True
                    return "✅ Auto-sync enabled. Venmo will sync every 5 minutes."
                elif command_parts[2] == "off":
                    st.session_state.venmo_data['auto_sync'] = False
                    return "❌ Auto-sync disabled."
                else:
                    return "❌ Use: `/venmo auto on` or `/venmo auto off`"
            
            elif venmo_action == "disconnect":
                st.session_state.venmo_data['connected'] = False
                st.session_state.venmo_data['access_token'] = ""
                st.session_state.venmo_data['auto_sync'] = False
                return "🔌 Venmo disconnected successfully."
            
            else:
                return """💳 **Venmo Commands:**
- `/venmo connect` - Instructions to connect Venmo
- `/venmo sync` - Manually sync transactions
- `/venmo transactions` - Show recent transactions
- `/venmo auto on` - Enable auto-sync
- `/venmo auto off` - Disable auto-sync
- `/venmo disconnect` - Disconnect Venmo account"""
        
        elif command == "/commands":
            return """**All Available Commands:**

📊 **Data Commands:**
- `/net profits` - Show net profits
- `/total sales` - Show total sales
- `/best day` - Show best day
- `/status` - Show all current data
- `/add [number] to net profit` - Add to net profits
- `/add [number] to sales` - Add to sales
- `/set net profit [amount]` - Set net profits
- `/set total sales [amount]` - Set total sales
- `/set best day [day]` - Set best day

📝 **Note Commands:**
- `/add note [text]` - Add note
- `/notes` - Show notes
- `/clear notes` - Clear notes

🧮 **Calculation Commands:**
- `/profit margin [revenue] [costs]` - Calculate profit margin
- `/break even [fixed] [price] [variable]` - Break-even analysis
- `/calculate margin [revenue] [costs]` - Profit margin
- `/calculate markup [cost] [markup_percent]` - Markup calculation
- `/calculate discount [original] [discount_percent]` - Discount calculation
- `/calculate tax [amount] [tax_rate]` - Tax calculation
- `/calculate tip [bill] [tip_percent]` - Tip calculation
- `/calculate inventory [stock] [daily_usage]` - Inventory analysis
- `/calculate roi [investment] [returns]` - ROI calculation

🔄 **Reset Commands:**
- `/reset all` - Reset all data
- `/reset profits` - Reset net profits
- `/reset sales` - Reset total sales

❓ **Help:**
- `/help` - Show detailed help
- `/commands` - List all commands"""
        
        else:
            return f"❌ Unknown command: {command_text}\nType `/help` for available commands."
    
    # Helper function to generate AI response with context
    def generate_ai_response(prompt, context, tone, business_context=""):
        try:
            # Build the system message with context and tone
            system_message = f"""You are a CFO assistant for a family-run slushie business. 
            
CONTEXT: The user is seeking advice in the area of {context}.
TONE: Respond in a {tone.lower()} manner.

{f"BUSINESS BACKGROUND: {business_context}" if business_context else ""}

Provide practical, actionable advice on finances, operations, inventory, marketing, and business strategy. 
Be specific and helpful based on the context and tone requested.

IMPORTANT: You cannot access live internet data, create graphs, or generate images. 
Focus on providing text-based advice, calculations, and recommendations based on the information provided.
If asked for current prices or live data, explain that you work with the data provided by the user.
If asked to create graphs, suggest using the Data Analysis section of this app instead."""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                stream=True,
            )
            return response
        except Exception as e:
            return None
    
    # Simple command interface
    st.subheader("Quick Commands")
    st.write("Click any command below to execute it instantly:")
    
    # Command categories
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**📊 Data Commands:**")
        if st.button("💰 Show Net Profits", key="cmd_net_profits"):
            command_response = process_command("/net profits")
            st.session_state.messages.append({"role": "user", "content": "/net profits"})
            st.session_state.messages.append({"role": "assistant", "content": command_response})
            st.rerun()
        
        if st.button("📈 Show Total Sales", key="cmd_total_sales"):
            command_response = process_command("/total sales")
            st.session_state.messages.append({"role": "user", "content": "/total sales"})
            st.session_state.messages.append({"role": "assistant", "content": command_response})
            st.rerun()
        
        if st.button("📅 Show Best Day", key="cmd_best_day"):
            command_response = process_command("/best day")
            st.session_state.messages.append({"role": "user", "content": "/best day"})
            st.session_state.messages.append({"role": "assistant", "content": command_response})
            st.rerun()
        
        if st.button("📊 Show Status", key="cmd_status"):
            command_response = process_command("/status")
            st.session_state.messages.append({"role": "user", "content": "/status"})
            st.session_state.messages.append({"role": "assistant", "content": command_response})
            st.rerun()
        
        if st.button("📝 Show Notes", key="cmd_notes"):
            command_response = process_command("/notes")
            st.session_state.messages.append({"role": "user", "content": "/notes"})
            st.session_state.messages.append({"role": "assistant", "content": command_response})
            st.rerun()
    
    with col2:
        st.write("**📝 Add Data:**")
        if st.button("➕ Add to Net Profits", key="cmd_add_profits"):
            amount = st.number_input("Amount to add:", min_value=0.01, value=0.0, step=0.01, key="add_profits_input")
            if st.button("Confirm Add", key="confirm_add_profits"):
                command_response = process_command(f"/add {amount} to net profit")
                st.session_state.messages.append({"role": "user", "content": f"/add {amount} to net profit"})
                st.session_state.messages.append({"role": "assistant", "content": command_response})
                st.rerun()
        
        if st.button("➕ Add to Sales", key="cmd_add_sales"):
            amount = st.number_input("Amount to add:", min_value=1, value=0, step=1, key="add_sales_input")
            if st.button("Confirm Add", key="confirm_add_sales"):
                command_response = process_command(f"/add {amount} to sales")
                st.session_state.messages.append({"role": "user", "content": f"/add {amount} to sales"})
                st.session_state.messages.append({"role": "assistant", "content": command_response})
                st.rerun()
        
        if st.button("📝 Add Note", key="cmd_add_note"):
            note_text = st.text_input("Note text:", key="note_input")
            if st.button("Save Note", key="save_note"):
                command_response = process_command(f"/add note {note_text}")
                st.session_state.messages.append({"role": "user", "content": f"/add note {note_text}"})
                st.session_state.messages.append({"role": "assistant", "content": command_response})
                st.rerun()
        
        if st.button("🗑️ Clear Notes", key="cmd_clear_notes"):
            command_response = process_command("/clear notes")
            st.session_state.messages.append({"role": "user", "content": "/clear notes"})
            st.session_state.messages.append({"role": "assistant", "content": command_response})
            st.rerun()
    
    with col3:
        st.write("**🧮 Calculations:**")
        if st.button("💰 Profit Margin", key="cmd_profit_margin"):
            revenue = st.number_input("Revenue:", min_value=0.01, value=0.0, step=0.01, key="margin_revenue")
            costs = st.number_input("Costs:", min_value=0.01, value=0.0, step=0.01, key="margin_costs")
            if st.button("Calculate Margin", key="calc_margin"):
                command_response = process_command(f"/calculate margin {revenue} {costs}")
                st.session_state.messages.append({"role": "user", "content": f"/calculate margin {revenue} {costs}"})
                st.session_state.messages.append({"role": "assistant", "content": command_response})
                st.rerun()
        
        if st.button("🏷️ Markup Calculator", key="cmd_markup"):
            cost = st.number_input("Cost:", min_value=0.01, value=0.0, step=0.01, key="markup_cost")
            markup = st.number_input("Markup %:", min_value=0.0, value=0.0, step=0.1, key="markup_percent")
            if st.button("Calculate Markup", key="calc_markup"):
                command_response = process_command(f"/calculate markup {cost} {markup}")
                st.session_state.messages.append({"role": "user", "content": f"/calculate markup {cost} {markup}"})
                st.session_state.messages.append({"role": "assistant", "content": command_response})
                st.rerun()
        
        if st.button("📦 Inventory Analysis", key="cmd_inventory"):
            stock = st.number_input("Current Stock:", min_value=0.0, value=0.0, step=0.1, key="inventory_stock")
            usage = st.number_input("Daily Usage:", min_value=0.0, value=0.0, step=0.1, key="inventory_usage")
            if st.button("Analyze Inventory", key="calc_inventory"):
                command_response = process_command(f"/calculate inventory {stock} {usage}")
                st.session_state.messages.append({"role": "user", "content": f"/calculate inventory {stock} {usage}"})
                st.session_state.messages.append({"role": "assistant", "content": command_response})
                st.rerun()
        
        if st.button("❓ Help", key="cmd_help"):
            command_response = process_command("/help")
            st.session_state.messages.append({"role": "user", "content": "/help"})
            st.session_state.messages.append({"role": "assistant", "content": command_response})
            st.rerun()
    
    # Manual command input (simplified)
    st.subheader("Manual Command Input")
    st.write("Type commands directly in the chat below, or use the buttons above.")
    st.info("💡 **Tip:** Type `/help` in the chat to see all available commands!")
    
    # Venmo Integration Section
    st.subheader("💳 Venmo Integration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Connection Status:**")
        if st.session_state.venmo_data['connected']:
            st.success("✅ Connected to Venmo")
            st.write(f"Last Sync: {st.session_state.venmo_data['last_sync'] or 'Never'}")
            st.write(f"Auto Sync: {'✅ On' if st.session_state.venmo_data['auto_sync'] else '❌ Off'}")
        else:
            st.error("❌ Not connected to Venmo")
            st.write("Connect your Venmo account to automatically track payments")
        
        # Connection buttons
        if not st.session_state.venmo_data['connected']:
            if st.button("🔗 Connect Venmo Account", key="connect_venmo"):
                st.session_state.venmo_data['connected'] = True
                st.session_state.venmo_data['last_sync'] = datetime.now().strftime("%H:%M")
                st.success("✅ Venmo connected! (Demo mode)")
                st.rerun()
        else:
            if st.button("🔌 Disconnect Venmo", key="disconnect_venmo"):
                st.session_state.venmo_data['connected'] = False
                st.session_state.venmo_data['access_token'] = ""
                st.session_state.venmo_data['auto_sync'] = False
                st.success("🔌 Venmo disconnected")
                st.rerun()
    
    with col2:
        st.write("**Auto-Sync Settings:**")
        auto_sync = st.checkbox(
            "Enable Auto-Sync", 
            value=st.session_state.venmo_data['auto_sync'],
            help="Automatically sync Venmo transactions every 5 minutes"
        )
        if auto_sync != st.session_state.venmo_data['auto_sync']:
            st.session_state.venmo_data['auto_sync'] = auto_sync
            st.rerun()
        
        sync_interval = st.selectbox(
            "Sync Interval:",
            [1, 5, 10, 15, 30],
            index=1,
            help="How often to sync transactions (minutes)"
        )
        if sync_interval != st.session_state.venmo_data['sync_interval']:
            st.session_state.venmo_data['sync_interval'] = sync_interval
            st.rerun()
        
        if st.button("🔄 Manual Sync", key="manual_sync"):
            if st.session_state.venmo_data['connected']:
                # Simulate syncing
                new_transactions = [
                    {"amount": 5.50, "note": "Blue Raspberry Slushie", "time": datetime.now().strftime("%H:%M")},
                    {"amount": 4.00, "note": "Cherry Slushie", "time": datetime.now().strftime("%H:%M")}
                ]
                st.session_state.venmo_data['transactions'].extend(new_transactions)
                st.session_state.venmo_data['daily_total'] += sum(t['amount'] for t in new_transactions)
                st.session_state.venmo_data['last_sync'] = datetime.now().strftime("%H:%M")
                st.success(f"✅ Synced {len(new_transactions)} new transactions!")
                st.rerun()
            else:
                st.error("❌ Venmo not connected")
    
    # Show recent transactions
    if st.session_state.venmo_data['transactions']:
        st.write("**Recent Transactions:**")
        transactions_df = pd.DataFrame(st.session_state.venmo_data['transactions'][-10:])
        st.dataframe(
            transactions_df,
            column_config={
                "amount": st.column_config.NumberColumn("Amount ($)", format="$%.2f"),
                "note": st.column_config.TextColumn("Description"),
                "time": st.column_config.TextColumn("Time")
            },
            use_container_width=True
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Today's Total", f"${st.session_state.venmo_data['daily_total']:,.2f}")
        with col2:
            st.metric("Transaction Count", len(st.session_state.venmo_data['transactions']))
        with col3:
            avg_amount = st.session_state.venmo_data['daily_total'] / len(st.session_state.venmo_data['transactions']) if st.session_state.venmo_data['transactions'] else 0
            st.metric("Average Transaction", f"${avg_amount:,.2f}")
    
    # Auto-update business data from Venmo
    if st.session_state.venmo_data['connected'] and st.session_state.venmo_data['auto_sync']:
        st.info("🔄 **Auto-Sync Active:** Venmo transactions will automatically update your business data every 5 minutes.")
        
        # Auto-update net profits from Venmo
        if st.button("💰 Update Net Profits from Venmo", key="update_profits"):
            st.session_state.commands_data['net_profits'] += st.session_state.venmo_data['daily_total']
            st.success(f"✅ Updated net profits! Added ${st.session_state.venmo_data['daily_total']:,.2f} from Venmo")
            st.rerun()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask your CFO assistant... (use /help for commands)"):
        # Check if it's a command
        if prompt.startswith('/'):
            # Process command
            command_response = process_command(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": command_response})
            
            # Display messages
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                st.markdown(command_response)
        else:
            # Regular chat message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate AI response with context
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Build the system message with context and tone
                        system_message = f"""You are a CFO assistant for a family-run slushie business. 
                        
CONTEXT: The user is seeking advice in the area of {context}.
TONE: Respond in a {tone.lower()} manner.

{f"BUSINESS BACKGROUND: {business_context}" if business_context else ""}

Provide practical, actionable advice on finances, operations, inventory, marketing, and business strategy. 
Be specific and helpful based on the context and tone requested.

IMPORTANT: You cannot access live internet data, create graphs, or generate images. 
Focus on providing text-based advice, calculations, and recommendations based on the information provided.
If asked for current prices or live data, explain that you work with the data provided by the user.
If asked to create graphs, suggest using the Data Analysis section of this app instead."""
                        
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": system_message}
                            ] + [
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.messages
                            ],
                            stream=True,
                        )

                        response_text = st.write_stream(response)
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        
                    except Exception as e:
                        error_message = f"I'm having trouble connecting right now. Please try again in a moment. (Error: {str(e)})"
                        st.error(error_message)
                        st.session_state.messages.append({"role": "assistant", "content": error_message})
    
    # Add a clear session button
    st.sidebar.markdown("---")
    if st.sidebar.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "🍧 **Slushie CFO Assistant** - Your AI-powered business partner | "
    "Built with Streamlit & OpenAI"
)