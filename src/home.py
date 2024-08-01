"""Home Page - Info and some settings"""

import streamlit as st

st.title("MLS (Michael Likes Statistics) App")

st.write("""
         This app allows you to generate graphs and statistic for MLS data given a variety of
         criteria. The app has two main components:
         1. A database which stores MLS data.
         1. This interface which allows you to browse the database and create graphics.
         """)

st.header("Uploading New Data")
st.write("""
         1. Export data from MLS as a `.csv` file (or files) using the Focus1st format. *Note: a `.csv` file
         with an incorrect format cannot be uploaded.*
            - Make sure that each csv file only contains one type of property, either single family
              or condo, but not both.
         1. Go to the "Upload Data" page in the app.
         1. Select the files to upload. You can upload many files at the same time.
         1. Select the property type: Single Family or Condo.
            - The `.csv` files do not include the property type so this has to be manually
              specified. If you are uploading multiple files, make sure they are all the same type of
              property as the option you pick will be applied to all of them.
        1. Optionally specify the county. In most cases you do not need to specify the county and
        can leave this blank.
            - When the county is left blank, the app will automatically assign counties based on
              city as long as the city and county pair exists in the county key. Most Bay Area
              cities are in the county key, so in general you can always leave county blank.
            - If county is not specified and a property is located in a city not in the county key,
              the county field will be left empty in the database. There is no problem with this per
              se; however, it will prevent that property from being accurately represented in any
              analysis where properties are grouped by county. This is not a comon use case so it
              should not be an issue.
            - If you specify the county, it will be applied to every property in the file and the
              app will not do a lookup in the county key. This feature is useful when you want to
              do analysis on an area not usually included in the Bay Area stats.
         1. Click "Upload Data". If everything went well you will see a success message.

         **What happens if I upload the same file twice or files contain overlapping data?**
         > That's OK! The upload process ignores duplicate entries so you won't corrupt the
         database.

         **What if I upload a `.csv` file in the wrong format?**
         > The app will detect this and show an error message. Nothing will be uploaded to the
         database.
         """)

st.header("Making Graphics")
st.write("""
         Each page under the Charts section of the sidebar allows you to create a different type
         of table or graph. Since the graphs are different, each page has a short description.

         Each graphic is generated on the page for you to preview. If you are happy and want to
         save it, click the camera icon that appears when you hover over the image; this will
         allow you to download the graphic as a `.png` file.

         Sometimes the app makes things too narrow. When this happens there are two options:
         1. Click on the three dots in the upper right hand corner, go into "Settings",
         and make sure wide mode is enabled.
         1. If it's still too narrow, collapse the sidebar on the left.
         1. If it's still too narrow, hover over the graphic and enter full screen.
         """)


# TODO: Write this
# st.header("Settings and Configuration")
# st.write(""""""")
