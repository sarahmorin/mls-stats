"""App Utility Functions"""

#pylint: disable=missing-docstring

import datetime as dt
import streamlit as st

SF_DIST_SORT = {
        'SF District 1': 0,
        'SF District 2': 1,
        'SF District 3': 2,
        'SF District 4': 3,
        'SF District 5': 4,
        'SF District 6': 5,
        'SF District 7': 6,
        'SF District 8': 7,
        'SF District 9': 8,
        'SF District 10': 9,
        }

def q_to_date_range(q, year):
    if q == 1:
        return dt.date(year, 1, 1), dt.date(year, 3, 31)
    if q == 2:
        return dt.date(year, 4, 1), dt.date(year, 6, 30)
    if q == 3:
        return dt.date(year, 7, 1), dt.date(year, 9, 30)
    if q == 4:
        return dt.date(year, 10, 1), dt.date(year, 12, 31)
    return None

def where_date_range(date_name, d1, d2):
    return f"{date_name} BETWEEN \'{d1.isoformat()}\' AND \'{d2.isoformat()}\'"

def where_ptype(ptype):
    if ptype == "Single Family":
        return "type=\'SF\'"
    if ptype == "Condo":
        return "type=\'C\'"
    return ""

def date_input(d1=dt.date.today(), d2=dt.date.today()):
    return st.date_input("Date Range", (d1, d2))

def ptype_input(include_all=True):
    pytpes = ["Single Family", "Condo"]
    if include_all:
        pytpes.append("Any")
    return st.selectbox("Property Type", pytpes)

def group_input(title="Group By"):
    return st.selectbox(title, ["District (SF)", "City", "County"])

def q_input(title="Quarter"):
    return st.radio(title, [1, 2, 3, 4], horizontal=True)

def year_input(title="Year"):
    return st.selectbox(title, list(range(dt.date.today().year, 1900, -1)))

def county_input(title="County"):
    conn = st.connection("mls_db")
    df = conn.query("SELECT DISTINCT county FROM listings")
    return st.multiselect(title, df, [],
                          help="Select county(s)")
