"""Distribution of Sale Price"""

#pylint: disable=wildcard-import
#pylint: disable=unused-wildcard-import
#pylint: disable=broad-exception-caught

import streamlit as st
import plotly.graph_objects as pgo

from utils import *

try:
    st.title("Distribution of Sales by Price")

    with st.form(key='form'):
        c1, c2 = st.columns(2)
        with c1:
            q = q_input()
        with c2:
            year = year_input()
        ptype = ptype_input()
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
        st.dataframe(df)

        # TODO: Formatting on plot and axes
        fig = pgo.Figure(data=[pgo.Scatter(x=df['selling_price'], y=[1 for _ in
                                                                     range(len(df['selling_price']))],
                                           mode='markers')])
        st.plotly_chart(fig)

except Exception as e:
    st.error(e)
