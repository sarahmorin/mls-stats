"""Distribution of Sale Price"""

#pylint: disable=line-too-long
#pylint: disable=wildcard-import
#pylint: disable=unused-wildcard-import
#pylint: disable=broad-exception-caught

import streamlit as st
import plotly.graph_objects as pgo

from utils import *

try:
    st.title("Distribution of Sales by Price")
    st.write("Generate a linear histogram of the sale distribution by price for a given quarter")

    with st.form(key='form'):
        st.subheader("Search Criteria")
        c1, c2 = st.columns(2)
        with c1:
            q = q_input()
        with c2:
            year = year_input()
        ptype = ptype_input()

        st.subheader("Appearance")
        color = st.color_picker("Color", value="#142bfa")
        opacity = st.slider("Opacity", min_value=0., max_value=1., value=0.5, step=0.1)
        marker_size = st.slider("Bubble Size", min_value=10, max_value=50, value=20, step=10)
        submit_button = st.form_submit_button("Generate Graph")

    if submit_button:
        conn = st.connection("mls_db")
        d1, d2 = q_to_date_range(q, year)
        date_range = where_date_range('selling_date', d1, d2)
        where = f"WHERE {date_range}"
        if ptype != "Any":
            where += f" AND {where_ptype(ptype)}"
        query = f"SELECT * FROM listings {where}"

        df = conn.query(query)
        if df.empty:
            no_data()

        fig = pgo.Figure(data=[pgo.Scatter(x=df['selling_price'],
                                           y=[1 for _ in range(len(df['selling_price']))],
                                           mode='markers',
                                           marker_color=color,
                                           marker_size=marker_size,
                                           marker_opacity=opacity)])
        fig.update_yaxes(showticklabels=False, nticks=1)
        st.plotly_chart(fig)

except Exception as e:
    st.error(e)
