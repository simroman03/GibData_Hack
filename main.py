import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(
        page_title="GibData",
)
def upload():
        x = st.slider('Select a value')
        st.write(x, 'squared is', x * x)


if __name__ == "__main__":
       upload()
