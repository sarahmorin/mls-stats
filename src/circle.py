"""Pie Chart Closed By Sale Price"""

#pylint: disable=wildcard-import
#pylint: disable=unused-wildcard-import
#pylint: disable=broad-exception-caught

import streamlit as st
import plotly.graph_objects as pgo

from utils import *

try:
    st.title("Closed Sales by Price")

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

        df_under1m = df.query('selling_price < 1000000').shape[0]
        df_1m_3m = df.query('selling_price >= 1000000 & selling_price < 3000000').shape[0]
        df_3m_5m = df.query('selling_price >= 3000000 & selling_price < 5000000').shape[0]
        df_over5m = df.query('selling_price >= 5000000').shape[0]
        labels = ['Under $1m', "$1m - $3m", "$3m - $5m", "Over $5m"]
        values = [df_under1m, df_1m_3m, df_3m_5m, df_over5m]
        fig = pgo.Figure(data=[pgo.Pie(labels=labels, values=values, hole=.6)])
        st.plotly_chart(fig)

except Exception as e:
    st.error(e)
