"""Line Graphs Comparing Previous Years"""

#pylint: disable=wildcard-import
#pylint: disable=unused-wildcard-import
#pylint: disable=broad-exception-caught
import datetime as dt
import streamlit as st
import pandas as pd
import plotly.graph_objects as pgo
import plotly.express as px

from utils import *

line_styles = get_line_styles()

def make_plot(df, group, freq, title):
    if freq == 'M':
        df['selling_date'] = df['selling_date'].map(to_month)
    elif freq == 'QS':
        df['selling_date'] = df['selling_date'].map(to_quarter_year)
    df_dict = dict(list(df.groupby(group)))
    line_style_idx = 0
    fig = pgo.Figure(layout={'title':title})
    for k,v in df_dict.items():
        fig.add_trace(pgo.Scatter(x=v['selling_date'], y=v['col'], name=k,
                                  line=line_styles[line_style_idx], mode='lines'))
        line_style_idx += 1

    return fig

try:
    st.title("Line Graphs")
    st.write("""Generate a collection of line graphs comparing a given statistic across areas in a
             given time period.""")

    with st.form(key='form'):
        st.subheader("Search Criteria")
        d1, d2 = date_input()
        ptype = ptype_input()
        county = county_input()
        date_group = date_group_input()
        metric = metric_input()

        submit_button = st.form_submit_button("Generate Graph")

    if submit_button:
        conn = st.connection("mls_db")

        # Construct Query
        date_range = where_date_range('selling_date', d1, d2)
        where = f"WHERE {date_range}"
        group = ""
        if ptype != "Any":
            where += f" AND {where_ptype(ptype)}"

        if len(county) == 0:
            group = "county"
        elif len(county) == 1:
            if county[0] == "San Francisco":
                group = "district"
                where += " AND city=\'San Francisco\' AND district != \'SF District 10\'"
            else:
                group = "city"
                where += f" AND county=\'{county[0]}\'"
        else:
            where += f" AND county IN {tuple(county)}"
            group = "city"

        query = f"SELECT * FROM listings {where}"

        # Get data
        df = conn.query(query)

        if df.empty:
            no_data()

        # Handle selling date as date
        df['selling_date'] = pd.to_datetime(df['selling_date'])
        GROUP_FREQ = ''
        if date_group == 'Month':
            GROUP_FREQ = 'M'
        elif date_group == 'Quarter':
            GROUP_FREQ = 'QS'
        else:
            GROUP_FREQ = 'YS'

        grouper = pd.Grouper(key='selling_date', freq=GROUP_FREQ)

        if metric == AVG_PRICE:
            df_stat = df.groupby([group, grouper])['selling_price'].mean().reset_index(name='col')
            fig = make_plot(df_stat, group, GROUP_FREQ, "Average Price")
            fig.update_layout(yaxis_tickprefix='$')
        elif metric == MED_PRICE:
            df_stat = df.groupby([group, grouper])['selling_price'].median().reset_index(name='col')
            fig = make_plot(df_stat, group, GROUP_FREQ, "Median Price")
            fig.update_layout(yaxis_tickprefix='$')
        elif metric == SALE_LIST:
            df_stat = df.groupby([group, grouper])['sale_over_list'].mean().reset_index(name='col')
            fig = make_plot(df_stat, group, GROUP_FREQ, "Sale Price as % of List Price")
            fig.update_layout(yaxis_tickformat=".0%")
        elif metric == PPSF:
            df_stat = df.groupby([group, grouper])['sppsf'].mean().reset_index(name='col')
            fig = make_plot(df_stat, group, GROUP_FREQ, "Average Price/Sq.Ft.")
            fig.update_layout(yaxis_tickprefix='$')
        elif metric == SALE_CNT:
            df_stat = df.groupby([group, grouper])['listing_number'].count().reset_index(name='col')
            fig = make_plot(df_stat, group, GROUP_FREQ, "Number of Sales")
        elif metric == AVG_DOM:
            df_dom = df.groupby([group, grouper])['dom'].mean().reset_index(name='col')
            fig = make_plot(df_dom, group, GROUP_FREQ, "Average Days on Market")
        elif metric == SALE_ASK:
            df_stat = df.query('selling_price > listing_price').groupby([group, grouper])['listing_number'].count().reset_index(name='col')
            fig = make_plot(df_stat, group, GROUP_FREQ, "Sales over Asking")
        else:
            raise Exception("Unsupported metric")
        st.plotly_chart(fig)

        expander = st.expander("Underlying Data")
        expander.dataframe(df_stat)

except Exception as e:
    st.error(e)
