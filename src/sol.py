"""Generate Sales Over List Bar Graph"""

#pylint: disable=line-too-long
#pylint: disable=missing-docstring
#pylint: disable=invalid-name
#pylint: disable=consider-using-f-string
#pylint: disable=wildcard-import
#pylint: disable=unused-wildcard-import
#pylint: disable=broad-exception-caught

import streamlit as st
import pandas as pd
import plotly.graph_objects as pgo

from utils import *

try:
    st.title("Q vs. Q Sales over List Price")
    st.write("Generate a bar graph comparing percentage of sales over list price for 2 quarters.")

    county_info()

    with st.form(key='form'):
        # Data Filters
        st.subheader("Search Criteria")
        c1, c2 = st.columns(2)
        with c1:
            d11, d12 = date_input(label="Time Period 1")
            t1_str = st.text_input("Time Period 1 Label", "")
        with c2:
            d21, d22 = date_input(label="Time Period 2")
            t2_str = st.text_input("Time Period 2 Label", "")
        county = county_input()
        ptype = ptype_input()

        # Formatting Options
        st.subheader("Appearance")
        ac1, ac2 = st.columns(2)
        with ac1:
            t1_color = st.color_picker("Color 1", value=BLUE)
        with ac2:
            t2_color = st.color_picker("Color 2", value=GOLD1)

        submit_button = st.form_submit_button("Generate Table")

    if submit_button:
        conn = st.connection("mls_db")
        date_range1 = where_date_range('selling_date', d11, d12)
        date_range2 = where_date_range('selling_date', d21, d22)
        where1 = f"WHERE {date_range1}"
        where2 = f"WHERE {date_range2}"
        # Construct where clause
        if ptype != "Any":
            where1 += f" AND {where_ptype(ptype)}"
            where2 += f" AND {where_ptype(ptype)}"

        group = ""
        if len(county) == 0:
            group = "county"
        elif len(county) == 1:
            if county[0] == "San Francisco":
                group = "district"
                where1 += " AND city=\'San Francisco\'"
                where2 += " AND city=\'San Francisco\'"
            else:
                group = "city"
                where1 += f" AND county=\'{county[0]}\'"
                where2 += f" AND county=\'{county[0]}\'"
        else:
            where1 += f" AND county IN {tuple(county)}"
            where2 += f" AND county IN {tuple(county)}"
            group = "city"

        # Construct query
        query1 = f"SELECT {group}, 1.0 * COUNT(*) / (SELECT COUNT(*) FROM listings {where1}) AS perc FROM listings {where1} AND selling_price > listing_price GROUP BY {group}"
        query2 = f"SELECT {group}, 1.0 * COUNT(*) / (SELECT COUNT(*) FROM listings {where2}) AS perc FROM listings {where2} AND selling_price > listing_price GROUP BY {group}"

        # Get data and compute summary stats
        df1 = conn.query(query1)
        df2 = conn.query(query2)

        if df1.empty:
            no_data(t1_str)
        if df2.empty:
            no_data(t2_str)

        df1['perc'] = df1['perc'].map("{:.1%}".format)
        df2['perc'] = df2['perc'].map("{:.1%}".format)
        bar1 = pgo.Bar(x=df1[group], y=df1['perc'], text=df1['perc'], name=t1_str, marker_color=t1_color)
        bar2 = pgo.Bar(x=df2[group], y=df2['perc'], text=df2['perc'], name=t2_str, marker_color=t2_color)
        fig = pgo.Figure(data=[bar1, bar2])
        st.plotly_chart(fig)

except Exception as e:
    st.error(e)
