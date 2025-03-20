# Import required libraries
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Set the title of the Streamlit app
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# User input for name on the order
name_on_order = st.text_input("Name on the Order")
st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Retrieve fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
pd_df = my_dataframe.to_pandas()  # Convert Snowpark dataframe to Pandas dataframe

# Fruit selection input
ingredients_list = st.multiselect("Choose up to 5 ingredients:", pd_df["FRUIT_NAME"], max_selections=5)

# Initialize ingredient string
ingredients_string = ""

# Process user selections
if ingredients_list:
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"].iloc[0]
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Fetch nutrition details from the API
        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            if response.status_code == 200:
                st.dataframe(data=response.json(), use_container_width=True)
            else:
                st.warning(f"⚠️ Unable to fetch nutrition details for {fruit_chosen}.")
        except Exception as e:
            st.error(f"❌ API request failed: {e}")

        # Construct the ingredient string
        ingredients_string += fruit_chosen + ", "

    # Remove the trailing comma and space
    ingredients_string = ingredients_string.rstrip(", ")

# Define SQL Insert Query (Using placeholders for security)
my_insert_stmt = """
INSERT INTO smoothies.public.orders (ingredients, name_on_order) 
VALUES (:1, :2)
"""

# Submit order button
if st.button("Submit Order"):
    try:
        session.sql(my_insert_stmt, [ingredients_string, name_on_order]).collect()
        st.success("✅ Your Smoothie is ordered!", icon="✅")
    except Exception as e:
        st.error(f"❌ Order submission failed: {e}")
