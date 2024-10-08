"""Pie Chart Closed By Sale Price"""

#pylint: disable=wildcard-import
#pylint: disable=unused-wildcard-import
#pylint: disable=broad-exception-caught

import streamlit as st
import plotly.graph_objects as pgo

from utils import *

try:
    st.title("Closed Sales by Price")
    st.write("Generate a pie chart of sale prices for a given quarter.")

    with st.form(key='form'):
        d1, d2 = date_input()
        county = county_input()
        ptype = ptype_input()
        st.subheader("Ring Segments")
        cols = st.columns(3)
        bins = [
                1000000,
                3000000,
                5000000,
                ]
        with cols[0]:
            bins[0] = st.number_input("", value=bins[0])
        with cols[1]:
            bins[1] = st.number_input("", value=bins[1])
        with cols[2]:
            bins[2] = st.number_input("", value=bins[2])

        st.subheader("Appearance")
        acol = st.columns(4)
        colors = ['#00a6fb', '#0582ca', '#006494', '#003554']
        with acol[0]:
            colors[0] = st.color_picker("", value=colors[0])
        with acol[1]:
            colors[1] = st.color_picker("", value=colors[1])
        with acol[2]:
            colors[2] = st.color_picker("", value=colors[2])
        with acol[3]:
            colors[3] = st.color_picker("", value=colors[3])

        submit_button = st.form_submit_button("Generate Graph")

    if submit_button:
        conn = st.connection("mls_db")
        date_range = where_date_range('selling_date', d1, d2)
        where = f"WHERE {date_range}"
        if ptype != "Any":
            where += f" AND {where_ptype(ptype)}"

        if len(county) == 1:
            where += f" AND county =\'{county[0]}\'"
        elif len(county) > 0:
            where += f" AND county IN {tuple(county)}"

        query = f"SELECT selling_price FROM listings {where}"

        df = conn.query(query)

        if df.empty:
            no_data()

        df_bins = []
        prev = 0
        for b in bins:
            df_bins.append(df.selling_price.between(prev, b, inclusive='left').sum())
            prev = b

        df_bins.append(df.selling_price.gt(prev).sum())

        x = [
                f'<${bins[0]:,}',
                f'${bins[0]:,}-${bins[1]:,}',
                f'${bins[1]:,}-${bins[2]:,}',
                f'>${bins[2]:,}',
            ]
        fig = pgo.Figure(data=[pgo.Pie(labels=x, values=df_bins, hole=.6,
                                       marker_colors=colors,sort=False)],
                         layout={
                             'title': "Closed Sales by Price",
                             'legend': {'orientation': 'h'}
                             })
        st.plotly_chart(fig)

except Exception as e:
    st.error(e)
