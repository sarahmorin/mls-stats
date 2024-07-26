import sqlite3 as sq3
import pandas as pd

def db_connect(db_name):
    conn = sq3.connect(db_name)
    return conn

def create_db(cur):
    # FIXME: Remove when done testing
    cur.execute("DROP TABLE IF EXISTS listings;")
    # TODO: Insert Type for sf vs. condo
    # TODO: Re-sort columns
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
        address             TEXT
                );""")

def make_address(row):
    if pd.isnull(row['unit']):
        return f"{row['street_number']} {row['street_name']} {row['street_suffix']}"

    return f"{row['street_number']} {row['street_name']} {row['street_suffix']}, {row['unit']}"

def get_baths(row):
    # Bath rows are of the form:  z (x y)
    # We simply want to extract z
    nums = row['bathrooms'].split()
    return int(nums[0])

def main():
    conn = db_connect("test.db")

    create_db(conn.cursor())

    df = pd.read_csv('~/Downloads/803214_RESI_D687.csv',
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
                     on_bad_lines='warn')

    # Fix column names
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(' ', '_')
    df.rename(columns={'area_desc': 'district'}, inplace=True)
    # Generate single col address
    df['address'] = df.apply(make_address, axis=1)
    df = df.drop(columns=['street_name', 'street_number', 'street_suffix', 'unit'])
    # Parse num bathrooms as int
    df['bathrooms'] = df.apply(get_baths, axis=1)

    # Convert to SQL
    df.to_sql('listings', conn, if_exists='append', index=False)

    conn.close()


if __name__=='__main__':
    main()
