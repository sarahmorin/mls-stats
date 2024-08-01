"""Browse the Database"""

#pylint: disable=line-too-long
#pylint: disable=missing-docstring

import streamlit as st
import pandas as pd

# FIXME: Hardcoded path
COUNTY_FILE="county_key.csv"

try:
    county_df = pd.read_csv(COUNTY_FILE)

    # Display Data as Table
    st.title("County Key")
    st.write("""This is the county key used to lookup the county for a given city when entires are
             uploaded to the database. To add a (city, county) pair scroll to the bottom and enter
             the data in a new row. When you are done making changes, make sure to click save.""")

    county_df = st.data_editor(county_df, num_rows="dynamic")

    if st.button("Save"):
        county_df.to_csv(COUNTY_FILE, index=False)

except Exception as e:
    st.warning(e)
