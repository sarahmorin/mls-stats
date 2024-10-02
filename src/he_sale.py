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
            d11, d12 = date_input(label="Time Period 1")
            t1_str = st.text_input("Time Period 1 Label", "")
        with c2:
            d21, d22 = date_input(label="Time Period 2")
            t2_str = st.text_input("Time Period 2 Label", "")
        county = county_input()
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
            t1_color = st.color_picker("Color 1", value=BLUE)
        with ac2:
            t2_color = st.color_picker("Color 2", value=GOLD1)

        submit_button = st.form_submit_button("Generate Chart")

    if submit_button:
        bins = sorted(bins)
        conn = st.connection("mls_db")
        date_range1 = where_date_range('selling_date', d11, d12)
        date_range2 = where_date_range('selling_date', d21, d22)
        where1 = f"WHERE {date_range1}"
        where2 = f"WHERE {date_range2}"
        # Construct where clause
        if ptype != "Any":
            where1 += f" AND {where_ptype(ptype)}"
            where2 += f" AND {where_ptype(ptype)}"

        if len(county) == 1:
            where1 += f" AND county =\'{county[0]}\'"
            where2 += f" AND county =\'{county[0]}\'"
        elif len(county) > 0:
            where1 += f" AND county IN {tuple(county)}"
            where2 += f" AND county IN {tuple(county)}"


        group = "county"

        # Construct query
        query1 = f"SELECT selling_price FROM listings {where1}"
        query2 = f"SELECT selling_price FROM listings {where2}"

        # Get data and compute summary stats
        df1 = conn.query(query1)
        df2 = conn.query(query2)

        if df1.empty:
            no_data()
        if df2.empty:
            no_data()

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
        bar1 = pgo.Bar(x=x, y=df1_bins, text=df1_bins, name=t1_str, marker_color=t1_color)
        bar2 = pgo.Bar(x=x, y=df2_bins, text=df2_bins, name=t2_str, marker_color=t2_color)
        fig = pgo.Figure(data=[bar1, bar2])
        st.plotly_chart(fig)

        expander = st.expander("Underlying Data")
        expander.write("Computed Bin Values")
        expander.table([x, df1_bins, df2_bins])
        expander.write("Full Dataset Period 1")
        expander.dataframe(df1)
        expander.write("Full Dataset Period 2")
        expander.dataframe(df2)


except Exception as e:
    st.error(e)
