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
        c1, c2 = st.columns(2)
        with c1:
            q1 = q_input("Quater A")
            y1 = year_input("Year A")
        with c2:
            q2 = q_input("Quarter B")
            y2 = year_input("Year B")
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

    if submit_button and valid_q_v_q(q1, y1, q2, y2):
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
        query1 = f"SELECT * FROM listings {where1}"
        query2 = f"SELECT * FROM listings {where2}"

        # Get data and compute summary stats
        df1 = conn.query(query1)
        df2 = conn.query(query2)

        if df1.empty:
            no_data(q1_str)
        if df2.empty:
            no_data(q2_str)

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

        # Format Columns
        df_stats.rename(columns={
            'med q1': f'Median Price {q1_str}',
            'med q2': f'Median Price {q2_str}',
            'ppsf q1': f'Price/SF {q1_str}',
            'ppsf q2': f'Price/SF {q2_str}',
            'sales q1': f'Sales {q1_str}',
            'sales q2': f'Sales {q2_str}',
            'county': 'County',
            'city': 'City',
            'district': 'District',
            },
            inplace=True)

        cols = list(df_stats.columns)
        vals = df_stats.transpose().values.tolist()
        fig = pgo.Figure(data=[pgo.Table(
            header={'values': cols,
                    'align': 'center'},
            cells={'values': vals,
                   'align': 'center'})
                               ])

        st.plotly_chart(fig)

        st.header("Raw Data")
        st.dataframe(df_stats,
                     hide_index=True)

except Exception as e:
    st.error(e)
