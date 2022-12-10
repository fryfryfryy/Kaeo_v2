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

#streamlit option menu component (https://github.com/victoryhb/streamlit-option-menu) Icons are bootstrapped. 
with st.sidebar:
                selected = option_menu(
                    menu_title = "Keep an Eye on", 
                    options = ["Location Analysis", "Police Feed", "Sentiment Analysis"],
                    menu_icon = "eye-fill",
                    icons=["geo-alt-fill", "rss-fill", "twitter"]
                    )