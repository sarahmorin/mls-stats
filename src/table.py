"""Generate Basic Table"""

#pylint: disable=line-too-long
#pylint: disable=missing-docstring
#pylint: disable=invalid-name
#pylint: disable=consider-using-f-string
#pylint: disable=wildcard-import
#pylint: disable=unused-wildcard-import
#pylint: disable=broad-exception-caught

import streamlit as st
import pandas as pd

from utils import *

try:
    st.title("Single Date Range Table")
    st.write("Generate a table comparing sale price statistics for a given quarter.")

    with st.form(key='form'):
        # Data Filters
        d1, d2 = date_input()
        county = county_input()
        ptype = ptype_input()

        # Formatting Options
        include_agg_row = st.toggle("Include Aggregate Row", value=True)
        st.subheader("Include Columns:")
        cols = st.columns(4)
        with cols[0]:
            include_avg_price = st.checkbox("Average Price", value=True)
            include_ppsf = st.checkbox("Price/SF", value=True)
        with cols[1]:
            include_med_price = st.checkbox("Median Price", value=True)
            include_num = st.checkbox("No. of Sales", value=True)
        with cols[2]:
            include_sale_list = st.checkbox("Sale/List Price", value=True)
            include_dom = st.checkbox("DOM", value=True)
        with cols[3]:
            include_max = st.checkbox("High Sale", value=True)
            include_sale_over_ask = st.checkbox("Sales Over Asking", value=True)

        submit_button = st.form_submit_button("Generate Table")

    if submit_button:
        conn = db_conn()
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
        df = pd.read_sql(query, conn)
        if df.empty:
            no_data()

        df_avg = df.groupby(group)['selling_price'].mean().reset_index(name='Average Sale Price')
        df_med = df.groupby(group)['selling_price'].median().reset_index(name='Median Sale Price')
        df_ratio = df.groupby(group)['sale_over_list'].mean().reset_index(name='Sale/List Price')
        df_max = df.groupby(group)['selling_price'].max().reset_index(name='High Sale')
        df_sppsf = df.groupby(group)['sppsf'].mean().reset_index(name='Sale Price/SF')
        df_sales = df.groupby(group)['selling_price'].count().reset_index(name='# of Sales')
        df_dom = df.groupby(group)['dom'].mean().reset_index(name='DOM')
        df_over_ask = df.query('selling_price > listing_price').groupby(group)['selling_price'].count().reset_index(name='# Sales Over Asking')

        df_stats = pd.DataFrame(df_avg[group])
        if include_agg_row:
            df_stats.loc[len(df_stats)] = {group: 'Summary'}
        if include_avg_price:
            df_stats = pd.merge(df_stats, df_avg, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', 'Average Sale Price'] = df['selling_price'].mean()
            df_stats['Average Sale Price'] = df_stats['Average Sale Price'].map("${:,.0f}".format)
        if include_med_price:
            df_stats = pd.merge(df_stats, df_med, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', 'Median Sale Price'] = df['selling_price'].median()
            df_stats['Median Sale Price'] = df_stats['Median Sale Price'].map("${:,.0f}".format)
        if include_sale_list:
            df_stats = pd.merge(df_stats, df_ratio, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', 'Sale/List Price'] = df['sale_over_list'].mean()
            df_stats['Sale/List Price'] = df_stats['Sale/List Price'].map("{:.0%}".format)
        if include_max:
            df_stats = pd.merge(df_stats, df_max, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', 'High Sale'] = df['selling_price'].max()
            df_stats['High Sale'] = df_stats['High Sale'].map("${:,.0f}".format)
        if include_ppsf:
            df_stats = pd.merge(df_stats, df_sppsf, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', 'Sale Price/SF'] = df['sppsf'].mean()
            df_stats['Sale Price/SF'] = df_stats['Sale Price/SF'].map("${:,.0f}".format)
        if include_num:
            df_stats = pd.merge(df_stats, df_sales, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', '# of Sales'] = df_stats['# of Sales'].sum()
        if include_dom:
            df_stats = pd.merge(df_stats, df_dom, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', 'DOM'] = df['dom'].mean()
            df_stats['DOM'] = df_stats['DOM'].map("{:.0f}".format)
        if include_sale_over_ask:
            df_stats = pd.merge(df_stats, df_over_ask, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', '# Sales Over Asking'] = df_stats['# Sales Over Asking'].sum()

        if group == "district":
            df_stats = df_stats.sort_values(by=['district'], key=lambda x: x.map(SF_DIST_SORT))

        df_stats.rename(columns={'district': 'District', 'county': 'County', 'city':'City'},
                        inplace=True)

        st.dataframe(df_stats,
                     hide_index=True)

except Exception as e:
    st.error(e)
