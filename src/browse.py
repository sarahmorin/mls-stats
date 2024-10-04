"""Browse the Database"""

#pylint: disable=line-too-long
#pylint: disable=missing-docstring

import warnings
import streamlit as st
import pandas as pd
import sqlitecloud
from streamlit_extras.dataframe_explorer import dataframe_explorer
from sqlalchemy import create_engine


try:
    # Connect to DB and get all data
    conn = create_engine(st.secrets["DB_CONN"])
    df = pd.read_sql("SELECT * FROM listings", conn)


    # Display Data as Table
    st.title("Browse Database")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        filtered_df = dataframe_explorer(df)
        st.dataframe(filtered_df.style.format({'listing_price': '${:,}',
                                  'selling_price': '${:,}',
                                  'sale_over_list': '{:.0%}',
                                  'lppsf': '${:,.2f}',
                                  'sppsf': '${:,.2f}',
                                  'square_footage': '{:.0f}',
                                  'selling_date': lambda t: t.strftime("%m/%d/%Y") if pd.notnull(t) else "",
                                  'listing_date': lambda t: t.strftime("%m/%d/%Y") if pd.notnull(t) else "",
                                  'contingent_date': lambda t: t.strftime("%m/%d/%Y") if pd.notnull(t) else "",
                                  'pending_date': lambda t: t.strftime("%m/%d/%Y") if pd.notnull(t) else "",
                                           }),
                 hide_index=True,
                 column_order=[
                     'listing_number',
                     'type',
                     'address',
                     'city',
                     'district',
                     'county',
                     'listing_price',
                     'selling_price',
                     'sale_over_list',
                     'listing_date',
                     'selling_date',
                     'lppsf',
                     'sppsf',
                     'dom',
                     'contingent_date',
                     'pending_date',
                     'square_footage',
                     'bedrooms',
                     'bathrooms',
                     ],
                 column_config={
                     'listing_number': st.column_config.TextColumn("Listing No."),
                     'type': "Property Type",
                     'address': "Address",
                     'city': "City",
                     'district': "District",
                     'county': "County",
                     'listing_price': "Listing Price",
                     'selling_price': "Selling Price",
                     'sale_over_list': "Sale/List %",
                     'listing_date': st.column_config.DateColumn("Listing Date"),
                     'selling_date': st.column_config.DateColumn("Selling Date"),
                     'lppsf': "List Price/sq.ft.",
                     'sppsf': "Sale Price/sq.ft.",
                     'dom': "DOM",
                     'contingent_date': st.column_config.DateColumn("Contingent Date"),
                     'pending_date': st.column_config.DateColumn("Pending Date"),
                     'square_footage': st.column_config.NumberColumn("Sq.Ft."),
                     'bedrooms': "Bed",
                     'bathrooms': "Bath",

                     })

except Exception as e:
    st.warning("Resulting data is too large to display. Please refine your query to limit results.")
