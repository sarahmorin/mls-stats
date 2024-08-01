"""Upload new data to the Database"""

#pylint: disable=missing-docstring
#pylint: disable=line-too-long
import datetime as dt
import sqlite3 as sq
import streamlit as st
import pandas as pd

# ===============================================
# Data Processing Functions
# -----------------------------------------------
# DO NOT call this function unless testing
def create_db():
    con = sq.connect("mls.db")
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS listings;")
    cur.execute("""CREATE TABLE IF NOT EXISTS listings(
        city                TEXT,
        district            TEXT,
        bathrooms           INTEGER,
        bedrooms            INTEGER,
        selling_date        TEXT,
        contingent_date     TEXT,
        dom                 INTEGER,
        listing_date        TEXT,
        listing_number      INTEGER PRIMARY KEY ON CONFLICT IGNORE,
        listing_price       INTEGER,
        pending_date        TEXT,
        selling_price       INTEGER,
        square_footage      INTEGER,
        county              TEXT,
        address             TEXT,
        type                TEXT,
        lppsf               REAL,
        sppsf               REAL,
        sale_over_list      REAL
                );""")
    con.close()

def make_address(row):
    if pd.isnull(row['unit']):
        return f"{row['street_number']} {row['street_name']} {row['street_suffix']}"

    return f"{row['street_number']} {row['street_name']} {row['street_suffix']}, {row['unit']}"

def get_baths(row):
    # Bath rows are of the form:  z (x y)
    # We simply want to extract z
    nums = row['bathrooms'].split()
    return int(nums[0])

def get_beds(row):
    try:
        return int(row['bedrooms'])
    except Exception as e:
        nums = row['bedrooms'].split('-')
        return int(nums[1])

def get_lppsf(row):
    if pd.isnull(row['square_footage']):
        return None
    return row['listing_price'] / row['square_footage']

def get_sppsf(row):
    if pd.isnull(row['square_footage']):
        return None
    return row['selling_price'] / row['square_footage']

def get_sale_over_list(row):
    return round((row['selling_price'] / row['listing_price']), 5)

# ===============================================
# Streamlit Page

try:
    st.title("Upload Data")

    upload_file = st.file_uploader("Choose a file",
                                   type='csv',
                                   accept_multiple_files=True,
                                   help="Upload a .csv with MLS data in Focus1st format to add to database")

    property_type = st.selectbox("Select Property Type",
                                 ["Single Family", "Condo"])

    county = st.text_input("County (optional)",
                            value="",
                            help="Manually set county for all entries. If you\
                           don't enter a county, counties will be automatically mapped from the\
                           county key.")

    if st.button("Upload Data"):
        if len(upload_file) == 0:
            st.warning("Please select a file to upload")
        else:
            conn = st.connection("mls_db")
            county_df = pd.read_csv('county_key.csv')   #FIXME: hardcoded
            for f in upload_file:
                df = pd.read_csv(f,
                                 usecols=[
                                     'City',
                                     'Street Name',
                                     'Street Number',
                                     'Street Suffix',
                                     'Unit',
                                     'Area Desc',
                                     'Bathrooms',
                                     'Bedrooms',
                                     'Selling Date',
                                     'Contingent Date',
                                     'DOM',
                                     'Listing Date',
                                     'Listing Number',
                                     'Listing Price',
                                     'Pending Date',
                                     'Selling Price',
                                     'Square Footage',
                                     ],
                                 dtype={
                                     'Street Name': str,
                                     'Street Number': str,
                                     'Street Suffix': str,
                                     'Unit': str,
                                     },
                                 on_bad_lines='warn',
                                 parse_dates=['Selling Date', 'Listing Date', 'Contingent Date',
                                              'Pending Date'])

                # Fix column names
                df.columns = df.columns.str.lower()
                df.columns = df.columns.str.replace(' ', '_')
                df.rename(columns={'area_desc': 'district'}, inplace=True)
                # Generate county column
                if county == "":
                    df = pd.merge(df, county_df, on='city')
                else:
                    df['county'] = county
                # Generate single col address
                df['address'] = df.apply(make_address, axis=1)
                if property_type == "Single Family":
                    df['type'] = 'SF'
                elif property_type == "Condo":
                    df['type'] = 'C'
                else:
                    df['type'] = None
                df = df.drop(columns=['street_name', 'street_number', 'street_suffix', 'unit'])
                # Parse num bathrooms as int
                df['bathrooms'] = df.apply(get_baths, axis=1)
                # Parse num beds as int (if range is given eg. 3-4 use max)
                df['bedrooms'] = df.apply(get_beds, axis=1)
                # Compute price/sf
                df['lppsf'] = df.apply(get_lppsf, axis=1)
                df['sppsf'] = df.apply(get_sppsf, axis=1)
                df['sale_over_list'] = df.apply(get_sale_over_list, axis=1)

                # Convert to SQL
                df.to_sql('listings', conn.engine, if_exists='append', index=False)

            # Print Success
            st.cache_data.clear()
            st.success("New data successfully uploaded")

    # Reset Button
    with st.expander("Reset Database"):
        st.error("WARNING: This cannot be undone")
        st.write("""If you want to reset the database - i.e. delete all the data and start fresh,
        press the button bellow. This is a permanent operation that cannot be undone. Only do this
        if you are absolutely certain.""")

        if st.button("Reset Database"):
            create_db()
            st.cache_data.clear()


except Exception as e:
    st.error("Failed to upload data. Make sure `.csv` file is the correct format")
    st.error(e)
