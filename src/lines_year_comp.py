"""Line Graphs Comparing Previous Years"""

#pylint: disable=wildcard-import
#pylint: disable=unused-wildcard-import
#pylint: disable=broad-exception-caught
import datetime as dt
import streamlit as st
import pandas as pd
import plotly.graph_objects as pgo

from utils import *

def make_plot(df1, df2, freq, y1, y2, color1, color2, title):
    if freq == 'M':
        df1['selling_date'] = df1['selling_date'].map(to_month)
        df2['selling_date'] = df2['selling_date'].map(to_month)
    elif freq == 'QS':
        df1['selling_date'] = df1['selling_date'].map(to_quarter)
        df2['selling_date'] = df2['selling_date'].map(to_quarter)
    l1 = pgo.Scatter(x=df1['selling_date'], y=df1['col'], name=y1, mode='lines', line_color=color1)
    l2 = pgo.Scatter(x=df2['selling_date'], y=df2['col'], name=y2, mode='lines',
                     line_color=color2)

    fig = pgo.Figure(data=[l1, l2], layout={'title': title})
    return fig

try:
    st.title("Year over Year Comparisons")
    st.write("""Generate a collection of line graphs comparing a given statistic over 2 years.""")

    with st.form(key='form'):
        st.subheader("Search Criteria")
        c1, c2 = st.columns(2)
        with c1:
            year1 = year_input("Year 1")
        with c2:
            year2 = year_input("Year 2")
        ptype = ptype_input()
        county = county_input()
        date_group = date_group_input()
        metric = metric_input()

        # Formatting Options
        st.subheader("Appearance")
        ac1, ac2 = st.columns(2)
        with ac1:
            t1_color = st.color_picker("Color 1", value=BLUE)
        with ac2:
            t2_color = st.color_picker("Color 2", value=GOLD1)

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
            if county[0] == "San Francisco":
                where1 += " AND city =\'San Francisco\'"
                where2 += " AND city =\'San Francisco\'"
            else:
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
        GROUP_FREQ = ''
        if date_group == 'Month':
            GROUP_FREQ = 'M'
        elif date_group == 'Quarter':
            GROUP_FREQ = 'QS'
        else:
            GROUP_FREQ = 'YS'

        grouper = pd.Grouper(key='selling_date', freq=GROUP_FREQ)

        if metric == AVG_PRICE:
            df1_stat = df1.groupby(grouper)['selling_price'].mean().reset_index(name='col')
            df2_stat = df2.groupby(grouper)['selling_price'].mean().reset_index(name='col')
            fig = make_plot(df1_stat, df2_stat, GROUP_FREQ, year1, year2, t1_color, t2_color, "Average Price")
            fig.update_layout(yaxis_tickprefix='$')
        elif metric == MED_PRICE:
            df1_stat = df1.groupby(grouper)['selling_price'].median().reset_index(name='col')
            df2_stat = df2.groupby(grouper)['selling_price'].median().reset_index(name='col')
            fig = make_plot(df1_stat, df2_stat, GROUP_FREQ, year1, year2, t1_color, t2_color, "Median Price")
            fig.update_layout(yaxis_tickprefix='$')
        elif metric == SALE_LIST:
            df1_stat = df1.groupby(grouper)['sale_over_list'].mean().reset_index(name='col')
            df2_stat = df2.groupby(grouper)['sale_over_list'].mean().reset_index(name='col')
            fig = make_plot(df1_stat, df2_stat, GROUP_FREQ, year1, year2, t1_color, t2_color, "Sale Price as % of List Price")
            fig.update_layout(yaxis_tickformat=".0%")
        elif metric == PPSF:
            df1_stat = df1.groupby(grouper)['sppsf'].mean().reset_index(name='col')
            df2_stat = df2.groupby(grouper)['sppsf'].mean().reset_index(name='col')
            fig = make_plot(df1_stat, df2_stat, GROUP_FREQ, year1, year2, t1_color, t2_color, "Average Price/SF")
            fig.update_layout(yaxis_tickprefix='$')
        elif metric == SALE_CNT:
            df1_stat = df1.groupby(grouper)['listing_number'].count().reset_index(name='col')
            df2_stat = df2.groupby(grouper)['listing_number'].count().reset_index(name='col')
            fig = make_plot(df1_stat, df2_stat, GROUP_FREQ, year1, year2, t1_color, t2_color, "Homes Sold")
        elif metric == AVG_DOM:
            df1_stat = df1.groupby(grouper)['dom'].mean().reset_index(name='col')
            df2_stat = df2.groupby(grouper)['dom'].mean().reset_index(name='col')
            fig = make_plot(df1_stat, df2_stat, GROUP_FREQ, year1, year2, t1_color, t2_color, "Average Days on Market")
        elif metric == SALE_ASK:
            df1_stat = df1.query('selling_price > listing_price').groupby(grouper)['listing_number'].count().reset_index(name='col')
            df2_stat = df2.query('selling_price > listing_price').groupby(grouper)['listing_number'].count().reset_index(name='col')
            fig = make_plot(df1_stat, df2_stat, GROUP_FREQ, year1, year2, t1_color, t2_color, "No. Sales over Asking")
        else:
            raise Exception("Unsupported Metric")

        st.plotly_chart(fig)

        expander = st.expander("Underlying Data")
        expander.write("Year 1")
        expander.dataframe(df1_stat)
        expander.write("Year 2")
        expander.dataframe(df2_stat)

except Exception as e:
    st.error(e)
