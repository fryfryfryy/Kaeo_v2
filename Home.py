from textwrap import fill
import streamlit as st
from streamlit_option_menu import option_menu



#Logo
st.sidebar.image("keepaneyeon-logos_black.png", use_column_width=True)


#Hide header and footer
hide_menu_style = """
                    <style>
                    #MainMenu {visibility: hidden; }
                    footer {visibility: hidden;}
                    </style>
                    """
st.markdown(hide_menu_style, unsafe_allow_html=True)


