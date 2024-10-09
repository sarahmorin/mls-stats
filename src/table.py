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
            include_avg_price = st.checkbox(AVG_PRICE, value=True)
            include_ppsf = st.checkbox(PPSF, value=True)
        with cols[1]:
            include_med_price = st.checkbox(MED_PRICE, value=True)
            include_num = st.checkbox(SALE_CNT, value=True)
        with cols[2]:
            include_sale_list = st.checkbox(SALE_LIST, value=True)
            include_dom = st.checkbox(AVG_DOM, value=True)
        with cols[3]:
            include_max = st.checkbox(SALE_MAX, value=True)
            include_sale_over_ask = st.checkbox(SALE_ASK, value=True)

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
            group = "county"

        # Construct query
        query = f"SELECT * FROM listings {where}"

        # Get data and compute summary stats
        df = pd.read_sql(query, conn)
        if df.empty:
            no_data()

        df_avg = df.groupby(group)['selling_price'].mean().reset_index(name=AVG_PRICE)
        df_med = df.groupby(group)['selling_price'].median().reset_index(name=MED_PRICE)
        df_ratio = df.groupby(group)['sale_over_list'].mean().reset_index(name=SALE_LIST)
        df_max = df.groupby(group)['selling_price'].max().reset_index(name=SALE_MAX)
        df_sppsf = df.groupby(group)['sppsf'].mean().reset_index(name=PPSF)
        df_sales = df.groupby(group)['selling_price'].count().reset_index(name=SALE_CNT)
        df_dom = df.groupby(group)['dom'].mean().reset_index(name=AVG_DOM)
        df_over_ask = df.query('selling_price > listing_price').groupby(group)['selling_price'].count().reset_index(name=SALE_ASK)

        df_stats = pd.DataFrame(df_avg[group])
        if include_agg_row:
            df_stats.loc[len(df_stats)] = {group: 'Summary'}
        if include_avg_price:
            df_stats = pd.merge(df_stats, df_avg, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', AVG_PRICE] = df['selling_price'].mean()
            df_stats[AVG_PRICE] = df_stats[AVG_PRICE].map("${:,.0f}".format)
        if include_med_price:
            df_stats = pd.merge(df_stats, df_med, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', MED_PRICE] = df['selling_price'].median()
            df_stats[MED_PRICE] = df_stats[MED_PRICE].map("${:,.0f}".format)
        if include_sale_list:
            df_stats = pd.merge(df_stats, df_ratio, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', SALE_LIST] = df['sale_over_list'].mean()
            df_stats[SALE_LIST] = df_stats[SALE_LIST].map("{:.0%}".format)
        if include_max:
            df_stats = pd.merge(df_stats, df_max, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', SALE_MAX] = df['selling_price'].max()
            df_stats[SALE_MAX] = df_stats[SALE_MAX].map("${:,.0f}".format)
        if include_ppsf:
            df_stats = pd.merge(df_stats, df_sppsf, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', PPSF] = df['sppsf'].mean()
            df_stats[PPSF] = df_stats[PPSF].map("${:,.0f}".format)
        if include_num:
            df_stats = pd.merge(df_stats, df_sales, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', SALE_CNT] = df_stats[SALE_CNT].sum()
        if include_dom:
            df_stats = pd.merge(df_stats, df_dom, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', AVG_DOM] = df['dom'].mean()
            df_stats[AVG_DOM] = df_stats[AVG_DOM].map("{:.0f}".format)
        if include_sale_over_ask:
            df_stats = pd.merge(df_stats, df_over_ask, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', SALE_ASK] = df_stats[SALE_ASK].sum()

        if group == "district":
            df_stats = df_stats.sort_values(by=['district'], key=lambda x: x.map(SF_DIST_SORT))

        df_stats.rename(columns={'district': 'District', 'county': 'County', 'city':'City'},
                        inplace=True)

        st.dataframe(df_stats,
                     hide_index=True)

except Exception as e:
    st.error(e)
