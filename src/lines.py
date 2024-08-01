"""Line Graphs Comparing Previous Years"""

#pylint: disable=wildcard-import
#pylint: disable=unused-wildcard-import
#pylint: disable=broad-exception-caught
import datetime as dt
import streamlit as st
import pandas as pd
import plotly.graph_objects as pgo

from utils import *

def to_month(d):
    return d.strftime("%b")

def make_plot(df1, df2, y1, y2, title):
    df1['selling_date'] = df1['selling_date'].map(to_month)
    df2['selling_date'] = df2['selling_date'].map(to_month)
    l1 = pgo.Scatter(x=df1['selling_date'], y=df1['col'], name=y1, mode='lines')
    l2 = pgo.Scatter(x=df2['selling_date'], y=df2['col'], name=y2, mode='lines')

    fig = pgo.Figure(data=[l1, l2], layout={'title': title})
    return fig
    # st.plotly_chart(fig)

try:
    st.title("Year Comparisons")

    with st.form(key='form'):
        st.subheader("Search Criteria")
        c1, c2 = st.columns(2)
        with c1:
            year1 = year_input("Year 1")
        with c2:
            year2 = year_input("Year 2")
        ptype = ptype_input()
        county = county_input()

        st.subheader("Plots")
        cols = st.columns(4)
        with cols[0]:
            include_avg_price = st.checkbox("Average Price", value=True)
            include_ppsf = st.checkbox("Average Price/SF", value=True)
        with cols[1]:
            include_med_price = st.checkbox("Median Price", value=True)
            include_num = st.checkbox("No. of Sales", value=True)
        with cols[2]:
            include_sale_list = st.checkbox("Sale/List Price", value=True)
            include_dom = st.checkbox("Average DOM", value=True)
        with cols[3]:
            include_max = st.checkbox("High Sale", value=True)
            include_sale_over_ask = st.checkbox("No. Sales Over Asking", value=True)

        submit_button = st.form_submit_button("Generate Graphs")

    if submit_button:
        conn = st.connection("mls_db")

        # Construct Query
        date_range_year1 = where_date_range('selling_date', dt.date(year1, 1, 1),
                                            dt.date(year1, 12, 31))
        date_range_year2 = where_date_range('selling_date', dt.date(year2, 1, 1),
                                            dt.date(year2, 12, 31))
        where1 = f"WHERE {date_range_year1}"
        where2 = f"WHERE {date_range_year2}"
        if ptype != "Any":
            where1 += f" AND {where_ptype(ptype)}"
            where2 += f" AND {where_ptype(ptype)}"

        if len(county) == 1:
            where1 += f" AND county =\'{county[0]}\'"
            where2 += f" AND county =\'{county[0]}\'"

        elif len(county) > 0:
            where1 += f" AND county IN {tuple(county)}"
            where2 += f" AND county IN {tuple(county)}"

        query1 = f"SELECT * FROM listings {where1}"
        query2 = f"SELECT * FROM listings {where2}"

        # Get data
        df1 = conn.query(query1)
        df2 = conn.query(query2)

        if df1.empty:
            no_data(year1)
        if df2.empty:
            no_data(year2)

        # Handle selling date as date
        df1['selling_date'] = pd.to_datetime(df1['selling_date'])
        df2['selling_date'] = pd.to_datetime(df2['selling_date'])
        grouper = pd.Grouper(key='selling_date', freq='M')

        if include_avg_price:
            df1_avg = df1.groupby(grouper)['selling_price'].mean().reset_index(name='col')
            df2_avg = df2.groupby(grouper)['selling_price'].mean().reset_index(name='col')
            fig_avg = make_plot(df1_avg, df2_avg, year1, year2, "Average Price")
            fig_avg.update_layout(yaxis_tickprefix='$')
            st.plotly_chart(fig_avg)

        if include_med_price:
            df1_med = df1.groupby(grouper)['selling_price'].median().reset_index(name='col')
            df2_med = df2.groupby(grouper)['selling_price'].median().reset_index(name='col')
            fig_med = make_plot(df1_med, df2_med, year1, year2, "Median Price")
            fig_med.update_layout(yaxis_tickprefix='$')
            st.plotly_chart(fig_med)

        if include_sale_list:
            df1_ratio = df1.groupby(grouper)['sale_over_list'].mean().reset_index(name='col')
            df2_ratio = df2.groupby(grouper)['sale_over_list'].mean().reset_index(name='col')
            fig_ratio = make_plot(df1_ratio, df2_ratio, year1, year2, "Sale Price as % of List Price")
            fig_ratio.update_layout(yaxis_tickformat=".0%")
            st.plotly_chart(fig_ratio)

        if include_ppsf:
            df1_ppsf = df1.groupby(grouper)['sppsf'].mean().reset_index(name='col')
            df2_ppsf = df2.groupby(grouper)['sppsf'].mean().reset_index(name='col')
            fig_ppsf = make_plot(df1_ppsf, df2_ppsf, year1, year2, "Average Price/SF")
            fig_ppsf.update_layout(yaxis_tickprefix='$')
            st.plotly_chart(fig_ppsf)

        if include_num:
            df1_sales = df1.groupby(grouper)['listing_number'].count().reset_index(name='col')
            df2_sales = df2.groupby(grouper)['listing_number'].count().reset_index(name='col')
            fig_sales = make_plot(df1_sales, df2_sales, year1, year2, "Homes Sold")
            st.plotly_chart(fig_sales)

        if include_dom:
            df1_dom = df1.groupby(grouper)['dom'].mean().reset_index(name='col')
            df2_dom = df2.groupby(grouper)['dom'].mean().reset_index(name='col')
            fig_dom = make_plot(df1_dom, df2_dom, year1, year2, "Average Days on Market")
            st.plotly_chart(fig_dom)

        if include_sale_over_ask:
            df1_sol = df1.groupby(grouper)['listing_number'].count().reset_index(name='col')
            df2_sol = df2.query('selling_price > listing_price').groupby(grouper)['listing_number'].count().reset_index(name='col')
            fig_sol = make_plot(df1_sol, df2_sol, year1, year2, "No. Sales over Asking")
            st.plotly_chart(fig_sol)

except Exception as e:
    st.error(e)
