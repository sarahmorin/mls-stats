# mls-stats
Python App for Michael to generate quaterly stats from MLS csv files.

# Design

A simple DB and GUI to generate info-graphics for mailers. 

## Components

* SQLite DB of relevant MLS data
* Python API to interact with DB
* Streamlit interfaces

## Functionality

* Upload new MLS data to DB as a .csv file
* Browse the full DB as a DF w/ query options
* Generate Tables and Plots that can be exported as images
    * Main table of sale price, DOM, etc.
    * Sales distribution by price (for a given area and time range)
    * Sales price (med or avg.) over time (for a given area, time range, and bucketing system)
    * pie chart one
    * quarterly comparison table (compare 2+ Qs for a given area)
    * Sale price vs. closing price


# Implementation Details

## SQLite DB

- [ ] Schema
- [ ] APIs
    - [ ] Create DB (testing and setup only)
    - [ ] Delete DB (testing and setup only)
    - [ ] Lookup with a given Query
    - [ ] Edit entry (by listing number)
    - [ ] Delete entry 
    - [ ] Manually create entry
    - [ ] Connection management
- [ ] Default configuration (where is the .db file?)

## Upload new Data

1. Upload .csv to app through streamlit interface
    - also get type: single family, condo
1. Read .csv file into a pandas dataframe
1. Do some data processing and cleanup:
    - condense street dir, street name, street number, and unit into one address field
    - rename area desc to district
    - parse bathrooms to integer
    - add property type
    - parse dates as dates?
    - drop:
        - lot size, style, style desc, year built
1. Re-order columns to match DB Schema
1. Connect to DB 
1. write new entries to DB
1. Close connection

## Browse Data

1. Connect to DB
1. Read query from streamlit interface
1. Run query to DB
1. Read entries as a dataframe and display in streamlit
1. loop 
1. close connection when leaving page

## Generate graphics

1. Connect to DB
1. Parse query info from streamlit options
1. Run query and get dataframe
1. make plotly graphic from DF
1. close DB connection
