import sqlite3 as sq3
import pandas as pd

COL_NAMES = {

        }

def db_connect(db_name):
    conn = sq3.connect(db_name)
    return conn

def create_db(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS listings(
        city                TEXT,
        street_direction    TEXT,
        street_name         TEXT,
        street_number       INTEGER,
        street_suffix       TEXT,
        unit                TEXT,
        area_desc           TEXT,
        bathrooms           TEXT,
        bedrooms            TEXT,
        selling_date        TEXT,
        curr_selling_price  INTEGER,
        contingent_date     TEXT,
        dom                 INTEGER,
        listing_date        TEXT,
        listing_number      INTEGER PRIMARY KEY ON CONFLICT IGNORE,
        listing_price       INTEGER,
        lot_size            TEXT,
        pending_date        TEXT,
        selling_price       INTEGER,
        square_footage      INTEGER,
        status              TEXT,
        status_date         TEXT,
        style               TEXT,
        style_desc          TEXT,
        year_built          TEXT
                );""")

def insert_skip_dup(table, conn, keys, data_iter):
    conn.execute(f"INSERT INTO {table.name} VALUES (?)", list(data_iter))

def main():
    conn = db_connect("test.db")

    create_db(conn.cursor())

    df = pd.read_csv('~/Downloads/803214_RESI_D687.csv')
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(' ', '_')
    df.to_sql('listings', conn, if_exists='append', index=False)

    conn.close()


if __name__=='__main__':
    main()
