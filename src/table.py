"""Generate Basic Table"""

#pylint: disable=line-too-long
#pylint: disable=missing-docstring
#pylint: disable=invalid-name
#pylint: disable=consider-using-f-string
#pylint: disable=wildcard-import
#pylint: disable=unused-wildcard-import

import datetime as dt
import streamlit as st
import pandas as pd
import plotly.graph_objects as pgo

from utils import *

try:
    st.title("Price Comparison Table")

    st.write("""
             When selecting the county:
             * San Francisco only will produce a table grouped by SF Districts
             * Selecting no county will produce a table of all counties grouped by counties
             * Any other choices will produce a table grouped by cities
             """)

    with st.form(key='form'):
        # Data Filters
        c1, c2 = st.columns(2)
        with c1:
            q = q_input()
        with c2:
            year = year_input()
        county = county_input()
        ptype = ptype_input()

        # TODO: Add more form options
        # Formatting Options
        agg_row = st.toggle("Include Aggregate Row", value=True)

        submit_button = st.form_submit_button("Generate Table")

    if submit_button:
        conn = st.connection("mls_db")
        d1, d2 = q_to_date_range(q, year)
        date_range = where_date_range('selling_date', d1, d2)
        where = f"WHERE {date_range}"
        group = ""
        # Construct where clause
        if ptype != "Any":
            where += f" AND {where_ptype(ptype)}"

        if len(county) == 0:
            group = "county"
        elif len(county) == 1:
            if county[0] == "San Francisco":
                group = "district"
                where += " AND city=\'San Francisco\'"
            else:
                group = "city"
                where += f" AND county=\'{county[0]}\'"
        else:
            where += f" AND county IN {tuple(county)}"
            group = "city"

        # Construct query
        query = f"SELECT * FROM listings {where}"

        # Get data and compute summary stats
        df = conn.query(query)
        # st.dataframe(df) # FIXME: remove

        df_avg = df.groupby(group)['selling_price'].mean().reset_index(name='Average Sale Price')
        df_med = df.groupby(group)['selling_price'].median().reset_index(name='Median Sale Price')
        df_ratio = df.groupby(group)['sale_over_list'].mean().reset_index(name='Sale/List Price')
        df_max = df.groupby(group)['selling_price'].max().reset_index(name='High Sale')
        df_sppsf = df.groupby(group)['sppsf'].mean().reset_index(name='Sale Price/SF')
        df_sales = df.groupby(group)['selling_price'].count().reset_index(name='# of Sales')
        df_dom = df.groupby(group)['dom'].mean().reset_index(name='DOM')
        df_over_ask = df.query('selling_price > listing_price').groupby(group)['selling_price'].count().reset_index(name='# Sales Over Asking')

        df_stats = pd.merge(df_avg, df_med, on=group)
        df_stats = pd.merge(df_stats, df_ratio, on=group)
        df_stats = pd.merge(df_stats, df_max, on=group)
        df_stats = pd.merge(df_stats, df_sppsf, on=group)
        df_stats = pd.merge(df_stats, df_sales, on=group)
        df_stats = pd.merge(df_stats, df_dom, on=group)
        df_stats = pd.merge(df_stats, df_over_ask, on=group)
        if group == "district":
            df_stats = df_stats.sort_values(by=['district'], key=lambda x: x.map(SF_DIST_SORT))

        # Add Aggregate row
        if agg_row:
            agg_row = {
                    'Average Sale Price': df['selling_price'].mean(),
                    'Median Sale Price': df['selling_price'].median(),
                    'Sale/List Price': df['sale_over_list'].mean(),
                    'High Sale': df['selling_price'].max(),
                    'Sale Price/SF': df['sppsf'].mean(),
                    '# of Sales': df_stats['# of Sales'].sum(),
                    'DOM': df['dom'].mean(),
                    '# Sales Over Asking': df_stats['# Sales Over Asking'].sum(),
                    }
            df_stats.loc[len(df_stats)] = agg_row

        # Format Columns
        df_stats['Average Sale Price'] = df_stats['Average Sale Price'].map("${:,.0f}".format)
        df_stats['Median Sale Price'] = df_stats['Median Sale Price'].map("${:,.0f}".format)
        df_stats['Sale/List Price'] = df_stats['Sale/List Price'].map("{:.0%}".format)
        df_stats['High Sale'] = df_stats['High Sale'].map("${:,}".format)
        df_stats['Sale Price/SF'] = df_stats['Sale Price/SF'].map("${:,.0f}".format)
        df_stats['DOM'] = df_stats['DOM'].map("{:.0f}".format)
        df_stats.columns = df_stats.columns.str.title()

        cols = list(df_stats.columns)
        vals = df_stats.transpose().values.tolist()
        fig = pgo.Figure(data=[pgo.Table(
            header={'values': cols,
                    'align': 'center'},
            cells={'values': vals,
                   'align': 'center'})
                               ])

        st.header("Graphic")
        st.plotly_chart(fig)

        st.header("Raw Data")
        st.dataframe(df_stats,
                     hide_index=True)

except Exception as e:
    st.error(e)
