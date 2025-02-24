"""App Utility Functions"""

#pylint: disable=missing-docstring

import datetime as dt
import streamlit as st
import pandas as pd

from sqlalchemy import create_engine

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
        'San Francisco': 10,
        'Summary': None,
        }

BLUE="#002349"
LIGHT_GREY="#adadad"
DARK_GREY="#67737a"
GOLD2="#a08525"
GOLD1="#c29b40"

# Metric Strings
AVG_PRICE = "Average Sale Price"
MED_PRICE = "Median Sale Price"
PPSF = "Average Price/Sq.Ft."
SALE_CNT = "Number of Sales"
SALE_LIST = "Sale Price as % of List Price"
AVG_DOM = "Avg. Days on Market"
SALE_ASK = "Sales over Asking"
SALE_MAX = "High Sale"

def db_conn():
    # return sqlitecloud.connect(st.secrets["DB_CONN"])
    return create_engine(st.secrets["DB_CONN"])

def get_line_styles():
    colors = [BLUE, GOLD1, LIGHT_GREY]
    dashes = ['solid', 'dash', 'dot', 'longdash', 'dashdot', 'longdashdot']
    line_styles = []
    for d in dashes:
        for c in colors:
            line_styles.append({'color': c, 'dash': d})

    return line_styles

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

def date_input(label="Date Range"):
    month = dt.date.today().month
    year = dt.date.today().year
    if month < 4:
        d1, d2 = q_to_date_range(4, year-1)
    elif month < 7:
        d1, d2 = q_to_date_range(1, year)
    elif month < 10:
        d1, d2 = q_to_date_range(2, year)
    else:
        d1, d2 = q_to_date_range(3, year)

    return st.date_input(label, (d1, d2))

def ptype_input(include_all=True):
    pytpes = ["Single Family", "Condo"]
    if include_all:
        pytpes.insert(0, "Any")
    return st.selectbox("Property Type", pytpes)

def year_input(title="Year"):
    return st.selectbox(title, list(range(dt.date.today().year, 1900, -1)))

def date_group_input(title="Group By"):
    return st.selectbox(title, ['Month', 'Quarter', 'Year'],
                        help="""How data is grouped by date along the x-axis. For
                        example: Grouping by
                        month will produce one data point per month for each line. ***Note: If
                        the date range is too small not all of these groupings make sense. For
                        example, grouping by year on a date range that spans a single quarter
                        is not useful.***""")

def county_input(title="County"):
    conn = db_conn()
    df = pd.read_sql("SELECT DISTINCT county FROM listings", conn)
    return st.multiselect(title, df, [],
                          help="""
                    * San Francisco only will produce a table/graph grouped by SF Districts
                    * Any other single county will produce a table/graph grouped by city
                    * Selecting no county or multiple counties will produce a table/graph grouped by county
                          """)

def sf_dist_input(title="Group SF by District"):
    return st.checkbox(title, help="""If you have selected **only San Francisco** as a County
                       above, this checkbox allows you to choose between a line graph for all 10
                       districts and a graph with a single line for SF. If you have not selected
                       SF above or have selected SF in a group of counties, this checkbox does
                       nothing.""")

def metric_input(title="Graph Metric"):
    return st.selectbox(title, [AVG_PRICE, MED_PRICE, PPSF, SALE_CNT, SALE_LIST, AVG_DOM,
                                SALE_ASK],
                        help=f"""
                        Select the metric represented in the graph.
                        * {AVG_PRICE}: sum of all sale prices divided by number of sales.
                        * {MED_PRICE}: middle sale price when sale prices are sorted from least
                        to greatest.
                        * {PPSF}: (sum of all sale price / sq.ft.) divided by number of sales.
                        * {SALE_CNT}: total number of sales.
                        * {SALE_LIST}: Average of Sales Price as % of List Price.
                        * {AVG_DOM}: Sum of all days on market divided by number of sales.
                        * {SALE_ASK}: Number of sales with sale price > list price.
                        """)

def no_data(opt=None, stop=True):
    if opt:
        st.warning(f"No data for the given search criteria: {opt}")
    else:
        st.warning("Database has no data for the given search criteria")

    if stop:
        st.stop()

def download(df, label="Download Data as CSV", name="mls-data.csv"):
    st.download_button(
            label=label,
            data=df.to_csv().encode("utf-8"),
            file_name=name,
            mime="text/csv")

def county_info():
    expander = st.expander("When selecting the county...", icon=":material/info:")
    expander.write("""
                    * San Francisco only will produce a table/graph grouped by SF Districts
                    * Selecting no county will produce a table/graph of all counties grouped by county
                    * Any other choices will produce a table/graph grouped by city
                   """)

def to_month(d):
    return d.strftime("%b '%y")

def to_quarter(d):
    s = d.strftime("%b")
    s = s.replace('Jan', 'Q1')
    s = s.replace('Apr', 'Q2')
    s = s.replace('Jul', 'Q3')
    s = s.replace('Oct', 'Q4')
    return s

def to_quarter_year(d):
    s = d.strftime("%b %Y")
    s = s.replace('Jan', 'Q1')
    s = s.replace('Apr', 'Q2')
    s = s.replace('Jul', 'Q3')
    s = s.replace('Oct', 'Q4')
    return s
