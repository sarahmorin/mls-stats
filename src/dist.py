"""Distribution of Sale Price"""

#pylint: disable=line-too-long
#pylint: disable=wildcard-import
#pylint: disable=unused-wildcard-import
#pylint: disable=broad-exception-caught

import streamlit as st
import pandas as pd
import plotly.graph_objects as pgo

from utils import *

try:
    st.title("Distribution of Sales by Price")
    st.write("Generate a linear histogram of the sale distribution by price for a given quarter")

    with st.form(key='form'):
        st.subheader("Search Criteria")
        d1, d2 = date_input()
        county = county_input()
        ptype = ptype_input()

        st.subheader("Appearance")
        color = st.color_picker("Color", value=BLUE)
        opacity = st.slider("Opacity", min_value=0.1, max_value=1., value=0.5, step=0.1)
        marker_size = st.slider("Bubble Size", min_value=10, max_value=50, value=20, step=10)
        submit_button = st.form_submit_button("Generate Graph")

    if submit_button:
        conn = db_conn()
        date_range = where_date_range('selling_date', d1, d2)
        where = f"WHERE {date_range}"
        if ptype != "Any":
            where += f" AND {where_ptype(ptype)}"

        if len(county) == 1:
            where += f" AND county =\'{county[0]}\'"
        elif len(county) > 0:
            where += f" AND county IN {tuple(county)}"

        query = f"SELECT * FROM listings {where}"

        df = pd.read_sql(query, conn)
        if df.empty:
            no_data()

        fig = pgo.Figure(data=[pgo.Scatter(x=df['selling_price'],
                                           y=[1 for _ in range(len(df['selling_price']))],
                                           mode='markers',
                                           marker_color=color,
                                           marker_size=marker_size,
                                           marker_opacity=opacity)],
                         layout={
                             'title': 'Distribution of Sales',
                             'xaxis_tickprefix': '$',
                             'height': 250,
                             })
        fig.update_yaxes(showticklabels=False, nticks=1)
        min_price = min(df['selling_price'])
        max_price = max(df['selling_price'])
        fig.add_annotation(x=min_price, y=1, text=f"${min_price:,}", showarrow=False, yshift=30)
        fig.add_annotation(x=max_price, y=1, text=f"${max_price:,}", showarrow=False, yshift=30)
        st.plotly_chart(fig)

        expander = st.expander("Underlying Data")
        expander.dataframe(df)

except Exception as e:
    st.error(e)
