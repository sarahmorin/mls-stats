"""Main App Interface"""
import streamlit as st

# ===============================================
# Create Pages
# -----------------------------------------------
# Data interface
upload_page = st.Page("upload.py", title="Upload Data")
browse_page = st.Page("browse.py", title="Browse Database")
# Graphics
table_page = st.Page("table.py", title="Comparison Table")
q_table_page = st.Page("qtable.py", title="Q vs. Q Table")
sale_dist_page = st.Page("dist.py", title="Sale Distribution")
circle_page = st.Page("circle.py", title="Closed Sales by Price")
high_end_page = st.Page("he_sale.py", title="High End Sales Change")
sale_over_list_page = st.Page("sol.py", title="Sales Over List Bar")
line_page = st.Page("lines.py", title="Line Graphs over Time")
sale_vs_closed_page = st.Page("sale_v_close.py", title="Sales Price vs. Closed Sales")
med_vs_aom_page = st.Page("med_v_aom.py", title="Median Price vs. AOM")

# ===============================================

# ===============================================
# Navigation
# -----------------------------------------------
pg = st.navigation(
    {
        "Database": [upload_page, browse_page],
        "Charts": [table_page, q_table_page, sale_dist_page, circle_page, high_end_page,
                   sale_over_list_page, line_page, sale_vs_closed_page, med_vs_aom_page],
    }
)
st.set_page_config(page_title="Michael's MLS App")

# ===============================================
# Setup State and Run
# -----------------------------------------------
pg.run()
