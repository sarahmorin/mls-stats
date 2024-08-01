"""Generate High-End Sale Quarter Comparison Histogram"""

#pylint: disable=line-too-long
#pylint: disable=missing-docstring
#pylint: disable=invalid-name
#pylint: disable=consider-using-f-string
#pylint: disable=wildcard-import
#pylint: disable=unused-wildcard-import
#pylint: disable=broad-exception-caught

import streamlit as st
import plotly.graph_objects as pgo

from utils import *

try:
    st.title("High End Sale Comparison")
    st.write("""Generate a histogram comparing high end sales number for two given quarters.""")

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
        ptype = ptype_input()

        st.subheader("Histogram Bins")
        st.write("Alter histogram bucket divisions")
        cols = st.columns(4)
        bins = [
                750000,
                1250000,
                2500000,
                3500000,
                ]
        with cols[0]:
            bins[0] = st.number_input("", value=bins[0])
        with cols[1]:
            bins[1] = st.number_input("", value=bins[1])
        with cols[2]:
            bins[2] = st.number_input("", value=bins[2])
        with cols[3]:
            bins[3] = st.number_input("", value=bins[3])

        st.subheader("Appearance")
        ac1, ac2 = st.columns(2)
        with ac1:
            q1_color = st.color_picker("Quarter A Color", value='#22a7f0')
        with ac2:
            q2_color = st.color_picker("Quarter B Color", value='#115f9a')

        submit_button = st.form_submit_button("Generate Table")

    if submit_button and valid_q_v_q(q1, y1, q2, y2):
        bins = sorted(bins)
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

        group = "county"

        # Construct query
        query1 = f"SELECT selling_price FROM listings {where1}"
        query2 = f"SELECT selling_price FROM listings {where2}"

        # Get data and compute summary stats
        df1 = conn.query(query1)
        df2 = conn.query(query2)

        if df1.empty:
            no_data(q1_str)
        if df2.empty:
            no_data(q2_str)

        df1_bins = []
        df2_bins = []
        prev = 0
        for b in bins:
            df1_bins.append(df1.selling_price.between(prev, b, inclusive='left').sum())
            df2_bins.append(df2.selling_price.between(prev, b, inclusive='left').sum())
            prev = b

        df1_bins.append(df1.selling_price.gt(prev).sum())
        df2_bins.append(df2.selling_price.gt(prev).sum())

        x = [
                f'<${bins[0]:,}',
                f'${bins[0]:,}-${bins[1]:,}',
                f'${bins[1]:,}-${bins[2]:,}',
                f'${bins[2]:,}-${bins[3]:,}',
                f'>${bins[3]:,}',
            ]
        bar1 = pgo.Bar(x=x, y=df1_bins, text=df1_bins, name=q1_str, marker_color=q1_color)
        bar2 = pgo.Bar(x=x, y=df2_bins, text=df2_bins, name=q2_str, marker_color=q2_color)
        fig = pgo.Figure(data=[bar1, bar2])
        st.plotly_chart(fig)


except Exception as e:
    st.error(e)
