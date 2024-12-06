# mls-stats
Python Streamlit App to generate quartlery real-estate statistic from MLS data.

# Design

A simple SQLite DB and Streamlit Interface to generate info-graphics for real-estate marketing materials. 

## Components

* SQLite DB of relevant MLS data
* Python API to interact with DB
* Streamlit interfaces

## Functionality

* Upload new MLS data to DB as a .csv file
* Browse the full DB as a DF w/ query options
* Generate Tables and Plots that can be exported as images. Including, but not limited to:
    * Table summary statistics: avg. sale price, DOM, No. of sales, etc.
    * Sales distribution by price (for a given area and time range)
    * Sales price (med or avg.) over time (for a given area, time range, and bucketing system)
    * quarterly comparison table (compare 2+ Qs for a given area)
