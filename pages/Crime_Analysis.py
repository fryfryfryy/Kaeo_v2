import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
import plotly.express as px

st.sidebar.image("keepaneyeon-logos_black.png", use_column_width=True)

@st.cache
def grab_postcode(postcode):
    """
    This code defines a function called grab_postcode() that takes in a postcode as its argument. 
    The function uses the requests module to make an API request to the "http://api.postcodes.io/postcodes/" endpoint using the provided postcode.
    If the API response is successful (indicated by a status code of 200), the function extracts the latitude and longitude coordinates from the response and uses them to make additional API requests to the "https://data.police.uk/api/locate-neighbourhood" and "https://data.police.uk/api/{force}/{neigh}/boundary" endpoints. The results of these requests are then used to build a polygon that represents the area around the provided postcode.
    If the initial API request is not successful, the function raises an exception. In either case, the function returns a tuple containing the latitude and longitude coordinates and the polygon representing the area around the postcode.
    The code uses the pandas module to convert the API response data to a DataFrame object, which is then used to extract the coordinates and build the polygon. 
    """
    response = requests.get(f'http://api.postcodes.io/postcodes/{postcode}')
    if response.ok:
        df = [response.json()['result']['latitude'],response.json()['result']['longitude']]
        force = requests.get(f'https://data.police.uk/api/locate-neighbourhood?q={df[0]},{df[1]}').json().get('force')
        neigh = requests.get(f'https://data.police.uk/api/locate-neighbourhood?q={df[0]},{df[1]}').json().get('neighbourhood')
        boundary = requests.get(f'https://data.police.uk/api/{force}/{neigh}/boundary').json()
        boundary = pd.DataFrame.from_dict(boundary)
        polygon=f"{boundary['latitude'].max()},{boundary['longitude'].max()}:\
            {boundary['latitude'].max()},{boundary['longitude'].min()}:\
                {boundary['latitude'].min()},{boundary['longitude'].min()}:\
                    {boundary['latitude'].min()},{boundary['longitude'].max()}"
    else:
        raise Exception
    return df, polygon


def grab_dates(poly, date):
    """
    Function that fetches the date range of the available data. St Cache avoides any unnecessary api calls. 
    """
    response = requests.get('https://data.police.uk/api/crimes-street-dates')
    if response.ok:
        df = pd.DataFrame.from_dict(response.json())
        df = df.explode('stop-and-search')
    else:
        df = "Data Refresh failed, please refresh the page"
    return df

@st.cache
def grab_force(coordinates):
    """
    Function to match the postcodes coordinates to the police force of the area and the relevant people in it.
    """
    ids = requests.get(f'https://data.police.uk/api/locate-neighbourhood?q={coordinates[0]},{coordinates[1]}').json()['force']
    response = requests.get(f'https://data.police.uk/api/forces/{ids}')
    response2 = requests.get(f'https://data.police.uk/api/forces/{ids}/people')
    if response.ok and response2.ok:
        df = response.json()
        df2 = response2.json()
    else:
        df = f"Data pull failed with error{response.text}, please refresh the page"
        df2=''
    return df, df2
