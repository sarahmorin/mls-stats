"""Main App Interface"""
import streamlit as st

# ===============================================
# Create Pages
# -----------------------------------------------
home_page = st.Page("home.py", title="Home")
# Data interface
upload_page = st.Page("upload.py", title="Upload Data")
browse_page = st.Page("browse.py", title="Browse Database")
county_page = st.Page("county.py", title="County Key")
# Graphics
table_page = st.Page("table.py", title="Sales Stats Table")
q_table_page = st.Page("qtable.py", title="Q vs. Q Table")
sale_dist_page = st.Page("dist.py", title="Scatter Line: Price Distribution")
circle_page = st.Page("circle.py", title="Pie Chart: Sales by Price")
high_end_page = st.Page("he_sale.py", title="Q vs. Q Sale Distribution")
sale_over_list_page = st.Page("sol.py", title="Bar: Q vs. Q % Sales over List")
line_page = st.Page("lines.py", title="Line Graph: X over time")
line_year_page = st.Page("lines_year_comp.py", title="Line Graphs: Change in X year over year")

# ===============================================

# ===============================================
# Navigation
# -----------------------------------------------
st.set_page_config(page_title="MLS DB")
pg = st.navigation(
    {
        "": [home_page],
        "Tables": [table_page, q_table_page],
        "Graphs": [sale_over_list_page, line_page, line_year_page],
        "Distributions": [sale_dist_page, high_end_page, circle_page],
        "Database": [upload_page, browse_page, county_page],
    }
)
# ===============================================
# Setup State and Run
# -----------------------------------------------
pg.run()
