import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import streamlit_shadcn_ui as ui


st.set_page_config(
        page_title="GibData",
)
def upload():    
        """
        st.set_page_config(
        page_title="Course Recommender",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
        )
        """
        st.title("Компетентностный подбор образовательных курсов")
        """
        cols = st.columns(1)
        with cols[0]:
            title = "Главный тренд года 🔥"
            content = "Специалист по внедрению Искуственного Интеллекта"
            description = "Срок обучения: 6 месяцев"
            ui.metric_card(title=title, content=content, description=description, key="card1")
            """
        
                
if __name__ == "__main__":
       upload()
