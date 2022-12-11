import streamlit as st
import requests

st.sidebar.image("keepaneyeon-logos_black.png", use_column_width=True)

@st.cache
def grab_postcode(postcode):
    """
    Function that takes a postcode and build a polygon based on the coordinates of the area around it.
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