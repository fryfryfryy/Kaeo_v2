import streamlit as st
import requests
import pandas as pd
import pydeck as pdk
import plotly.express as px
import seaborn as sns

#Logo for Sidebar
st.sidebar.image("keepaneyeon-logos_black.png", use_column_width=True)

#Default Postcode in Sidebar
postcode = st.sidebar.text_input(
                'Please Input Full Postcode',
                'NN4 9YX'
            )

#Default Polygon for Map & Dates
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

response_lsoa = postcode_to_LSOA(postcode)

try:
    LSOA_Name, LSOA_Code = response_lsoa.split()
except ValueError:
    try:
        LSOA_Name, LSOA_Name_1, LSOA_Code = response_lsoa.split()
        LSOA_Name = (LSOA_Name + " " + LSOA_Name_1)
    except ValueError:
        try:
            LSOA_Name, LSOA_Name_1, LSOA_Code = response_lsoa.split()
            LSOA_Name = (LSOA_Name + " " + LSOA_Name_1)
        except ValueError:
            try:
                LSOA_Name, LSOA_Name_1, LSOA_Name_2, LSOA_Code = response_lsoa.split()
                LSOA_Name = (LSOA_Name + " " + LSOA_Name_1 + " " + LSOA_Name_2)
            except ValueError:
                st.write("Analysis Cannot be generated.")

response = requests.get(f"https://services3.arcgis.com/ivmBBrHfQfDnDf8Q/arcgis/rest/services/Indices_of_Multiple_Deprivation_(IMD)_2019/FeatureServer/0/query?where=lsoa11nm%20%3D%20%27{LSOA_Name}%20{LSOA_Code}%27&outFields=*&outSR=&f=json")

LSOA_Data = response.json()
IMD_DEC = LSOA_Data['features'][0]['attributes']['IMD_Decile']
EMP_Dec = LSOA_Data['features'][0]['attributes']['EmpDec']
ENV_Dec = LSOA_Data['features'][0]['attributes']['EnvDec']
INC_Dec = LSOA_Data['features'][0]['attributes']['IncDec']
CRI_Dec = LSOA_Data['features'][0]['attributes']['CriDec']

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Index of Multiple Deprivation", IMD_DEC)
with col2:
    st.metric("Crime Score", CRI_Dec)
with col3:
    st.metric("Income", INC_Dec)

col4, col5, col6 = st.columns(3)
with col4:
    st.metric("Environment", ENV_Dec)
with col5:
    st.metric("Employment", EMP_Dec)
with col6:
    st.text('        ')

st.write("This data is pulled straight through the Data.Police.UK API and is updated with the most recent available data")
    
st.write("-------------- ")

available = dates[dates['stop-and-search'] == force_prof['id']]['date']

date = st.selectbox(
'Choose Your Month',
list(available)
)


df = grab_data(poly, date)


crime_type = st.multiselect('Please select the crimes you would like to filter by',
                                    list(df.category.unique()), list(df.category.unique()))

st.write("[An explanation of crime types can be found here](https://www.met.police.uk/sd/stats-and-data/met/crime-type-definitions/)")

st.write("-------------- ")

st.markdown("Crimes in your location:")

pal_df = pd.DataFrame({'category':df['category'].unique(),\
        'hex_palette': sns.color_palette('pastel',len(df['category'].unique())).as_hex(),\
        'rgb_palette': sns.color_palette('pastel',len(df['category'].unique()))})
pal_df['rgb_palette'] = pal_df['rgb_palette'].apply(lambda x: [y*255 for y in x])

df = df.merge(pal_df, on='category', how='left')
df['colorR'] = [x[0] for x in df['rgb_palette']]
df['colorG'] = [x[1] for x in df['rgb_palette']]
df['colorB'] = [x[2] for x in df['rgb_palette']]
bar_data = df['category'].value_counts(normalize=True).reset_index().merge(pal_df, left_on = 'index', right_on='category')
bar_data['percentage'] = bar_data['category_x'] * 100
bar_data['index'] = bar_data['index'].str.upper()

if len(df) > 0:
        # Write bar chart
        st.markdown(f"Total no. of crimes: {len(df)}")
        st.vega_lite_chart(bar_data, {
        'title': 'Crimes Types per Percentage',
        'width':600,
        'height':400,
        'mark': {'type': 'bar', 'tooltip': False },
        'encoding': {
            'y': {'field': 'index', 'type': 'nominal', 'sort':'-x',
            "axis":{"title":'Crime Type'}
            },
            'x': {'field': 'percentage', 'type': 'quantitative',
            "axis":{"title":'Percentage of Crimes'}
            },
            "color": {
            "field": "hex_palette", "type": "nominal", "scale" : None,
            "legend":None
        }}}) 