"""Generate Quarter Comparison Table"""

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
    st.title("Quarter Comparison Table")
    st.write("""Generate a table comparing median price, price/sf, and number of sales for 2 given
             quarters.""")

    with st.form(key='form'):
        # Data Filters
        st.subheader("Search Criteria")
        c1, c2 = st.columns(2)
        with c1:
            d11, d12 = date_input(label="Time Period 1")
            t1_str = st.text_input("Time Period 1 Label", "Q")
        with c2:
            d21, d22 = date_input(label="Time Period 2")
            t2_str = st.text_input("Time Period 2 Label", "Q")
        county = county_input()
        ptype = ptype_input()

        # Formatting Options
        include_agg_row = st.toggle("Include Aggregate Row", value=True)
        st.subheader("Include Columns:")
        cols = st.columns(3)
        with cols[0]:
            include_med_price = st.checkbox("Median Price", value=True)
        with cols[1]:
            include_ppsf = st.checkbox("Price/SF", value=True)
        with cols[2]:
            include_num = st.checkbox("No. of Sales", value=True)

        submit_button = st.form_submit_button("Generate Table")

    if submit_button:
        conn = db_conn()
        date_range1 = where_date_range('selling_date', d11, d12)
        date_range2 = where_date_range('selling_date', d21, d22)
        where1 = f"WHERE {date_range1}"
        where2 = f"WHERE {date_range2}"
        # Construct where clause
        if ptype != "Any":
            where1 += f" AND {where_ptype(ptype)}"
            where2 += f" AND {where_ptype(ptype)}"

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
        query1 = f"SELECT * FROM listings {where1}"
        query2 = f"SELECT * FROM listings {where2}"

        # Get data and compute summary stats
        df1 = pd.read_sql(query1, conn)
        df2 = pd.read_sql(query2, conn)

        if df1.empty:
            no_data(t1_str)
        if df2.empty:
            no_data(t2_str)

        df1_med = df1.groupby(group)['selling_price'].median().reset_index(name='med q1')
        df1_sppsf = df1.groupby(group)['sppsf'].mean().reset_index(name='ppsf q1')
        df1_sales = df1.groupby(group)['selling_price'].count().reset_index(name='sales q1')
        df2_med = df2.groupby(group)['selling_price'].median().reset_index(name='med q2')
        df2_sppsf = df2.groupby(group)['sppsf'].mean().reset_index(name='ppsf q2')
        df2_sales = df2.groupby(group)['selling_price'].count().reset_index(name='sales q2')

        df_stats = pd.DataFrame(df1_med[group])
        if include_agg_row:
            df_stats.loc[len(df_stats)] = {group: 'Summary'}
        if include_med_price:
            df_stats = pd.merge(df_stats, df1_med, on=group, how='left')
            df_stats = pd.merge(df_stats, df2_med, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', 'med q1'] = df1['selling_price'].median()
                df_stats.loc[df_stats[group] == 'Summary', 'med q2'] = df2['selling_price'].median()
            df_stats['Median Price Change'] = (df_stats['med q2'] - df_stats['med q1'])/df_stats['med q1']
            df_stats['Median Price Change'] = df_stats['Median Price Change'].map("{:.1%}".format)
            df_stats['med q1'] = df_stats['med q1'].map("${:,.0f}".format)
            df_stats['med q2'] = df_stats['med q2'].map("${:,.0f}".format)
        if include_ppsf:
            df_stats = pd.merge(df_stats, df1_sppsf, on=group, how='left')
            df_stats = pd.merge(df_stats, df2_sppsf, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', 'ppsf q1'] = df1['sppsf'].median()
                df_stats.loc[df_stats[group] == 'Summary', 'ppsf q2'] = df2['sppsf'].median()
            df_stats['Price/SF Change'] = (df_stats['ppsf q2'] - df_stats['ppsf q1'])/df_stats['ppsf q1']
            df_stats['Price/SF Change'] = df_stats['Price/SF Change'].map("{:.1%}".format)
            df_stats['ppsf q1'] = df_stats['ppsf q1'].map("${:,.0f}".format)
            df_stats['ppsf q2'] = df_stats['ppsf q2'].map("${:,.0f}".format)
        if include_num:
            df_stats = pd.merge(df_stats, df1_sales, on=group, how='left')
            df_stats = pd.merge(df_stats, df2_sales, on=group, how='left')
            if include_agg_row:
                df_stats.loc[df_stats[group] == 'Summary', 'sales q1'] = df1['sppsf'].count()
                df_stats.loc[df_stats[group] == 'Summary', 'sales q2'] = df2['sppsf'].count()
            df_stats['# of Sales Change'] = (df_stats['sales q2'] - df_stats['sales q1'])/df_stats['sales q1']
            df_stats['# of Sales Change'] = df_stats['# of Sales Change'].map("{:.1%}".format)

        if group == "district":
            df_stats = df_stats.sort_values(by=['district'], key=lambda x: x.map(SF_DIST_SORT))

        # Format Columns
        df_stats.rename(columns={
            'med q1': f'Median Price {t1_str}',
            'med q2': f'Median Price {t2_str}',
            'ppsf q1': f'Price/SF {t1_str}',
            'ppsf q2': f'Price/SF {t2_str}',
            'sales q1': f'Sales {t1_str}',
            'sales q2': f'Sales {t2_str}',
            'county': 'County',
            'city': 'City',
            'district': 'District',
            },
            inplace=True)

        st.dataframe(df_stats, hide_index=True)

except Exception as e:
    st.error(e)
