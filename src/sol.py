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

    st.info("""
             When selecting the county:
             * San Francisco only will produce a table grouped by SF Districts
             * Selecting no county will produce a table of all counties grouped by county
             * Any other choices will produce a table grouped by city
             """)

    with st.form(key='form'):
        # Data Filters
        st.subheader("Search Criteria")
        c1, c2 = st.columns(2)
        with c1:
            q1 = q_input("Quarter A")
            y1 = year_input("Year A")
        with c2:
            q2 = q_input("Quarter B")
            y2 = year_input("Year B")
        county = county_input()
        ptype = ptype_input()

        # Formatting Options
        st.subheader("Appearance")
        ac1, ac2 = st.columns(2)
        with ac1:
            q1_color = st.color_picker("Quarter A Color", value='#22a7f0')
        with ac2:
            q2_color = st.color_picker("Quarter B Color", value='#115f9a')

        submit_button = st.form_submit_button("Generate Table")

    if submit_button:
        q1_str = f"Q{q1} {y1}"
        q2_str = f"Q{q2} {y2}"
        conn = st.connection("mls_db")
        d11, d12 = q_to_date_range(q1, y1)
        d21, d22 = q_to_date_range(q2, y2)
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
            no_data(q1_str)
        if df2.empty:
            no_data(q2_str)

        df1['perc'] = df1['perc'].map("{:.1%}".format)
        df2['perc'] = df2['perc'].map("{:.1%}".format)
        bar1 = pgo.Bar(x=df1[group], y=df1['perc'], text=df1['perc'], name=q1_str, marker_color=q1_color)
        bar2 = pgo.Bar(x=df2[group], y=df2['perc'], text=df2['perc'], name=q2_str, marker_color=q2_color)
        fig = pgo.Figure(data=[bar1, bar2])
        st.plotly_chart(fig)

except Exception as e:
    st.error(e)
