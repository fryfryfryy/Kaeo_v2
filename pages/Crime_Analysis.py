import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
import plotly.express as px

st.sidebar.image("keepaneyeon-logos_black.png", use_column_width=True)

postcode = st.sidebar.text_input(
                'Please Input Full Postcode',
                'NN4 9YX'
            )
code = [51.509865, -0.118092]
poly = '51.5201931,-0.1284721:51.5145315,-0.1272705:51.5149054,-0.1130226:51.5206203,-0.1149109:51.5201931:-0.1284721'

@st.cache(ttl=86400)
def grab_dates():
    """
    Function that fetches the date range of the available data
    """
    response = requests.get('https://data.police.uk/api/crimes-street-dates')
    if response.ok:
        df = pd.DataFrame.from_dict(response.json())
        df = df.explode('stop-and-search')
    else:
        df = "Data Refresh failed, please refresh the page"
    return df

dates = grab_dates()

def postcode_to_LSOA(postcode):
    response = requests.get(f'http://api.postcodes.io/postcodes/{postcode}')
    if response.ok:
        Parse_LSOA = response.json()
        LSOA = Parse_LSOA['result']['lsoa']
    else:
        raise Exception
    return LSOA

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

def grab_data(coordinates=None, date=None):
                """
                Function to fetch the list of individual crimes that happened in the area 
                """
                response = requests.get(f"https://data.police.uk/api/crimes-street/all-crime?date={date}&poly={coordinates}")
                if response.ok and len(response.json()) > 0:   
                    df = pd.DataFrame.from_dict(response.json())
                    df['latitude'] = df['location'].apply(lambda x: float(x.get('latitude')))
                    df['longitude'] = df['location'].apply(lambda x: float(x.get('longitude')))
                    df['last_outcome'] = df['outcome_status'].apply(lambda x: x.get('category') if type(x) is dict else None)
                else:
                    df = []
                return df

@st.cache(allow_output_mutation=True)
def period_data(dates, range, poly):
    """
    Function that fetches crimes over a set number of periods
    """
    df_t = pd.DataFrame()
    for date in dates[:range]:
        df = grab_data(poly,date)
        df_t = df_t.append(df)
    return df_t

try:
    code,poly = grab_postcode(postcode)
except:
    st.error('Postcode Could Not be Matched')
    
force_prof, force_people = grab_force(code)

st.write(force_prof, force_people)