"""Main App Interface"""
import streamlit as st

# ===============================================
# Create Pages
# -----------------------------------------------
home_page = st.Page("home.py", title="Home")
# Data interface
upload_page = st.Page("upload.py", title="Upload Data")
browse_page = st.Page("browse.py", title="Browse Database")
county_page = st.Page("county.py", title="Edit County Key")
# Graphics
table_page = st.Page("table.py", title="Sales Stats Table")
q_table_page = st.Page("q_table.py", title="Q vs. Q Stats Table")
sale_dist_page = st.Page("price_dist_line.py", title="Scatter Line: Price Distribution")
# circle_page = st.Page("circle.py", title="Pie Chart: Sales by Price")
q_price_dist_page = st.Page("q_price_dist.py", title="Q vs. Q Price Distribution")
q_sale_over_list_page = st.Page("q_sale_over_list.py", title="Q vs. Q % Sales over List Price")
line_page = st.Page("lines.py", title="Stats over time, Compare Areas")
line_year_page = st.Page("lines_year_county.py", title="Compare 2 Year in County")
line_year_sf_page = st.Page("lines_year_sf.py", title="Compare 2 Years in SF District")

# ===============================================

# ===============================================
# Navigation
# -----------------------------------------------
st.set_page_config(page_title="MLS DB")
pg = st.navigation(
    {
        "": [home_page],
        "Tables": [table_page],
        "Distributions": [sale_dist_page],
        "Line Graphs": [line_page, line_year_page, line_year_sf_page],
        "Q v. Q Comparisons": [q_table_page, q_price_dist_page, q_sale_over_list_page],
        "Database": [upload_page, browse_page, county_page],
    }
)
# ===============================================
# Setup State and Run
# -----------------------------------------------
pg.run()
