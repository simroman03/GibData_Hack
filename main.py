import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(
        page_title="GibData",
)
def upload():    
        st.set_page_config(
        page_title="Course Recommender",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
        )
        # st.title("Компетентностный подбор образовательных курсов")
        
                
if __name__ == "__main__":
       upload()
