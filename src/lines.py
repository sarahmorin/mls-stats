"""Line Graphs Comparing Previous Years"""

#pylint: disable=wildcard-import
#pylint: disable=unused-wildcard-import
#pylint: disable=broad-exception-caught
import datetime as dt
import streamlit as st
import pandas as pd
import plotly.graph_objects as pgo

from utils import *

try:
    st.title("Year Comparisons")

    with st.form(key='form'):
        c1, c2 = st.columns(2)
        with c1:
            year1 = year_input("Year 1")
        with c2:
            year2 = year_input("Year 2")
        ptype = ptype_input()
        # TODO: add more options for different types of graphs
        submit_button = st.form_submit_button("Generate Graphs")

    if submit_button:
        conn = st.connection("mls_db")
        date_range_year1 = where_date_range('selling_date', dt.date(year1, 1, 1),
                                            dt.date(year1, 12, 31))
        date_range_year2 = where_date_range('selling_date', dt.date(year2, 1, 1),
                                            dt.date(year2, 12, 31))
        where1 = f"WHERE {date_range_year1}"
        if ptype != "Any":
            where1 += f" AND {where_ptype(ptype)}"
        query1 = f"SELECT * FROM listings {where1}"

        where2 = f"WHERE {date_range_year2}"
        if ptype != "Any":
            where2 += f" AND {where_ptype(ptype)}"
        query2 = f"SELECT * FROM listings {where2}"

        df = pd.concat([conn.query(query1), conn.query(query2)], ignore_index=True)
        df1 = conn.query(query1)
        df2 = conn.query(query2)

        st.dataframe(df)


        st.plotly_chart(fig)

except Exception as e:
    st.error(e)
